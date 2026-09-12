"""Stdlib-only client for the official robot interface (OFFICIAL-003 sections 5-9).

Contract points implemented here:

* the four POST paths ``/enter``, ``/measure``, ``/clear``, ``/exit`` with body
  ``{arena_id, robot_id, request_id[, position[, channel]]}``;
* ``Content-Type: application/json; charset=utf-8``, no BOM, compact UTF-8 JSON,
  no trailing slash and no query parameters;
* every **new** action uses a new ``request_id``; a retry of the identical action
  reuses the identical id **and** body;
* ``accepted`` and the HTTP status are both checked -- neither alone decides;
* ``accepted=false`` responses carry only ``accepted``/``real_timestamp_ms``/
  ``virtual_time_s``, and that ``virtual_time_s`` is 0 and is **not** the current
  virtual clock;
* a lost/missing/malformed response or a 429/500 leaves the acceptance state
  unknown: the client retries the same id a bounded number of times and then
  raises, so the caller stops instead of inventing a new id.

No third-party package is imported, and nothing here imports ``evaluator``.
"""

from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from .errors import (
    IdempotencyConflict,
    MissingJsonError,
    ServerUnknownError,
    StructuralError,
    TransportError,
    UnknownAcceptError,
)

DEFAULT_BASE_URL = "http://127.0.0.1:2026"
DEFAULT_ARENA_ID = "default"
PATHS = ("/enter", "/measure", "/clear", "/exit")
MEASURE_RESULTS = ("no_signal", "near", "direction")
CLEAR_RESULTS = ("success", "no_target_in_range")
COORD_LIMIT = 2000000.0
CHANNEL_MIN, CHANNEL_MAX = 1, 20


# --- response records --------------------------------------------------------


@dataclass
class Response:
    """One definitive simulator response."""

    path: str
    request_id: str
    http_status: int
    accepted: bool
    virtual_time_s: float
    real_timestamp_ms: float
    body: dict
    attempts: int = 1
    occupied: bool = True
    #: action specific fields
    measure_result: str = None
    svd_deg: float = None
    clear_result: str = None
    exit_reason: str = None
    max_virtual_duration_s: float = None
    max_real_duration_s: float = None
    remaining_real_duration_s: float = None


@dataclass
class ActionRecord:
    """Audit record for one logical action (possibly several attempts)."""

    seq: int
    path: str
    request_id: str
    body: dict
    attempts: int = 0
    send_monotonic: list = field(default_factory=list)
    recv_monotonic: list = field(default_factory=list)
    http_status: int = None
    accepted: object = None
    outcome: str = "pending"
    virtual_time_s: object = None
    raw_response: object = None
    detail: str = ""

    def to_dict(self):
        return {
            "seq": self.seq,
            "path": self.path,
            "request_id": self.request_id,
            "body": self.body,
            "attempts": self.attempts,
            "send_monotonic_s": [round(t, 6) for t in self.send_monotonic],
            "recv_monotonic_s": [round(t, 6) for t in self.recv_monotonic],
            "http_status": self.http_status,
            "accepted": self.accepted,
            "outcome": self.outcome,
            "virtual_time_s": self.virtual_time_s,
            "raw_response": self.raw_response,
            "detail": self.detail,
        }


class HttpTransport:
    """Real HTTP transport (``urllib``), injectable for tests."""

    def __init__(self, timeout=5.0):
        self.timeout = timeout

    def post(self, url, payload: bytes, headers):
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:  # an HTTP status is still a response
            return exc.code, exc.read()
        # URLError, socket timeouts, RemoteDisconnected ... all mean "no response"


class RobotClient:
    """Sequential, idempotent client for the four official commands."""

    def __init__(self, base_url=DEFAULT_BASE_URL, robot_id=None, arena_id=DEFAULT_ARENA_ID,
                 timeout=5.0, max_retries=2, transport=None, clock=time.monotonic,
                 id_prefix="c0"):
        if not robot_id:
            raise ValueError("robot_id (logged-in team identifier) is required")
        self.base_url = base_url.rstrip("/")
        self.robot_id = robot_id
        self.arena_id = arena_id
        self.max_retries = int(max_retries)
        self.transport = transport or HttpTransport(timeout=timeout)
        self.clock = clock
        self.id_prefix = id_prefix
        self.records = []
        self._seq = 0

    # -- request plumbing ---------------------------------------------------
    def _new_record(self, path, body):
        self._seq += 1
        record = ActionRecord(self._seq, path, body["request_id"], body)
        self.records.append(record)
        return record

    def _post(self, path, body, record):
        payload = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}
        url = self.base_url + path
        last_error = None
        for attempt in range(1, self.max_retries + 2):
            record.attempts = attempt
            record.send_monotonic.append(self.clock())
            try:
                status, raw = self.transport.post(url, payload, headers)
            except Exception as exc:  # transport failure: no response at all
                last_error = TransportError(f"{type(exc).__name__}: {exc}")
                record.detail = str(last_error)
                continue
            record.recv_monotonic.append(self.clock())
            record.http_status = status
            parsed = self._parse_body(raw)
            if parsed is None:
                last_error = MissingJsonError(f"HTTP {status} without a JSON business body")
                record.detail = str(last_error)
                continue
            record.raw_response = parsed
            result = self._classify(record, path, status, parsed)
            if result is not None:
                return result
            # 429/500 -> the action may or may not have executed; retry the SAME id and body
            last_error = ServerUnknownError(status, "server did not confirm execution", parsed)
            record.detail = str(last_error)
        record.outcome = "unknown_accept"
        raise UnknownAcceptError(
            f"{path} {body['request_id']}: acceptance unknown after {record.attempts} attempt(s); "
            f"last error: {last_error}"
        )

    @staticmethod
    def _parse_body(raw):
        if not raw:
            return None
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        if not isinstance(parsed, dict):
            return None
        for key in ("accepted", "real_timestamp_ms", "virtual_time_s"):
            if key not in parsed:
                return None
        return parsed

    def _classify(self, record, path, status, parsed):
        """Return a :class:`Response` when the outcome is definitive, else ``None``."""
        if status in (400, 413, 415, 404, 405):
            record.outcome = "structural_error"
            record.detail = f"HTTP {status}"
            raise StructuralError(status, "invalid request (request_id not occupied)", parsed)
        if status == 409:
            record.outcome = "id_conflict"
            record.detail = "HTTP 409"
            raise IdempotencyConflict(message=str(parsed))
        if status == 429:
            record.detail = "HTTP 429"
            return None
        if status >= 500:
            record.detail = f"HTTP {status}"
            return None
        if status != 200:
            record.detail = f"unexpected HTTP {status}"
            raise StructuralError(status, "unexpected status", parsed)

        accepted = bool(parsed["accepted"])
        record.accepted = accepted
        record.virtual_time_s = parsed["virtual_time_s"]
        if not accepted:
            # only the three common fields are present; the id is not occupied when
            # the rejection came from an unknown field / arena / robot mismatch
            record.outcome = "rejected"
            return Response(path, record.request_id, status, False, float(parsed["virtual_time_s"]),
                            float(parsed["real_timestamp_ms"]), parsed,
                            attempts=record.attempts, occupied=False)
        record.outcome = "accepted"
        response = Response(path, record.request_id, status, True, float(parsed["virtual_time_s"]),
                            float(parsed["real_timestamp_ms"]), parsed, attempts=record.attempts,
                            occupied=True)
        if path == "/measure":
            response.measure_result = parsed.get("measure_result")
            if "svd_deg" in parsed:
                response.svd_deg = float(parsed["svd_deg"])
        elif path == "/clear":
            response.clear_result = parsed.get("clear_result")
        elif path == "/exit":
            response.exit_reason = parsed.get("exit_reason")
        elif path == "/enter":
            response.max_virtual_duration_s = float(parsed["max_virtual_duration_s"])
            response.max_real_duration_s = float(parsed["max_real_duration_s"])
            response.remaining_real_duration_s = float(parsed["remaining_real_duration_s"])
        return response

    # -- the four commands --------------------------------------------------
    def enter(self):
        body = {"arena_id": self.arena_id, "robot_id": self.robot_id,
                "request_id": f"{self.id_prefix}-enter-1"}
        return self._post("/enter", body, self._new_record("/enter", body))

    def measure(self, position, channel, request_id=None):
        body = self._action_body("/measure", position, channel, request_id)
        return self._post("/measure", body, self._new_record("/measure", body))

    def clear(self, position, channel, request_id=None):
        body = self._action_body("/clear", position, channel, request_id)
        return self._post("/clear", body, self._new_record("/clear", body))

    def exit(self, request_id=None):
        rid = request_id or f"{self.id_prefix}-exit-{self._seq + 1}"
        body = {"arena_id": self.arena_id, "robot_id": self.robot_id, "request_id": rid}
        return self._post("/exit", body, self._new_record("/exit", body))

    def _action_body(self, path, position, channel, request_id):
        self._validate_position(position)
        channel = self._validate_channel(channel)
        rid = request_id or f"{self.id_prefix}-{path.strip('/')}-{self._seq + 1}"
        return {"arena_id": self.arena_id, "robot_id": self.robot_id, "request_id": rid,
                "position": {"x": float(position[0]), "y": float(position[1])}, "channel": channel}

    @staticmethod
    def _validate_position(position):
        x, y = float(position[0]), float(position[1])
        for value in (x, y):
            if not math.isfinite(value) or abs(value) > COORD_LIMIT:
                raise ValueError(f"coordinate {value} is not finite or exceeds {COORD_LIMIT}")
        return x, y

    @staticmethod
    def _validate_channel(channel):
        value = int(channel)
        if not (CHANNEL_MIN <= value <= CHANNEL_MAX):
            raise ValueError(f"channel {channel} outside {CHANNEL_MIN}..{CHANNEL_MAX}")
        return value

    # -- idempotent retry of a recorded action ------------------------------
    def retry(self, record):
        """Retry one recorded action with the identical id and body."""
        return self._post(record.path, record.body, record)

    def log(self):
        return [record.to_dict() for record in self.records]
