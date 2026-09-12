"""Offline mock of the official robot interface (OFFICIAL-003) for T11/T12.

The mock is an independent implementation of the documented protocol, used to
exercise the adapter without a live simulator.  It implements: the four POST
paths, exact-path and content-type checks, duplicate-key and required-field
checks, ``arena_id``/``robot_id`` mismatch, unknown-field rejection, request_id
idempotency (same content replays the first response; different content is 409),
the virtual-time formulas, and deadline behaviour (a request at or after the
deadline is not executed and the connection is closed without a response).

Faults are injectable per path so T11/T12 can be scored deterministically.
"""

from __future__ import annotations

import json
import math
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

COORD_LIMIT = 2000000.0
BODY_LIMIT = 65536
ALLOWED_PATHS = ("/enter", "/measure", "/clear", "/exit")
DECLARED_FIELDS = {
    "/enter": {"arena_id", "robot_id", "request_id"},
    "/measure": {"arena_id", "robot_id", "request_id", "position", "channel"},
    "/clear": {"arena_id", "robot_id", "request_id", "position", "channel"},
    "/exit": {"arena_id", "robot_id", "request_id"},
}

#: sentinel body meaning "the HTTP response carried no usable JSON business body"
NON_JSON = object()


class _DuplicateKey(ValueError):
    pass


def _no_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise _DuplicateKey(key)
        seen[key] = value
    return seen


def _content_type_ok(value):
    if not value:
        return False
    parts = [p.strip() for p in value.split(";")]
    if parts[0].lower() != "application/json":
        return False
    for extra in parts[1:]:
        if extra.lower() != "charset=utf-8":
            return False
    return True


class MockSimulator:
    """Stateful, deterministic implementation of the documented interface."""

    def __init__(self, robot_id="TEAM-TEST", arena_id="default", remaining_real_duration_s=1200,
                 max_virtual_duration_s=360000.0, max_real_duration_s=1200.0,
                 bearing_error_deg=0.0, sources=None, clock=time.monotonic):
        self.robot_id = robot_id
        self.arena_id = arena_id
        self.remaining_real_duration_s = remaining_real_duration_s
        self.max_virtual_duration_s = max_virtual_duration_s
        self.max_real_duration_s = max_real_duration_s
        self.bearing_error_deg = bearing_error_deg
        self.clock = clock
        self.sources = sources if sources is not None else {
            1: {"g": (100.0, 0.0), "R": 1500.0, "directional": False, "phi_deg": 0.0, "cleared": False},
            2: {"g": (-400.0, 300.0), "R": 1000.0, "directional": True, "phi_deg": 90.0, "cleared": False},
        }
        self.position = (0.0, 0.0)
        self.channel = 1
        self.virtual_time_s = 0.0
        self.entered = False
        self.exited = False
        self.deadline_virtual_s = None
        self.deadline_real_monotonic = None
        self.idempotency = {}
        self.executed = []
        self.faults = {}
        self.request_log = []
        self._lock = threading.Lock()

    # -- fault injection ----------------------------------------------------
    def set_fault(self, path, mode, repeat=True, **kwargs):
        """Queue a fault for ``path``.  ``repeat`` keeps it active for every call."""
        entry = dict(kwargs)
        entry.update({"mode": mode, "repeat": repeat, "used": 0})
        self.faults.setdefault(path, []).append(entry)

    def _next_fault(self, path):
        for entry in self.faults.get(path) or []:
            if entry["repeat"] or entry["used"] == 0:
                entry["used"] += 1
                return entry
        return None

    # -- physics ------------------------------------------------------------
    def _observation(self, position, channel):
        source = self.sources.get(channel)
        if source is None or source.get("cleared"):
            return "no_signal", None
        gx, gy = source["g"]
        dx, dy = position[0] - gx, position[1] - gy
        r = math.hypot(dx, dy)
        if r == 0.0:
            return ("near", None) if not source["directional"] else ("no_signal", None)
        if source["directional"]:
            phi = math.radians(source["phi_deg"])
            dot = math.cos(phi) * dx + math.sin(phi) * dy
            if dot < -1e-12 * max(1.0, r):
                return "no_signal", None
        if r <= 5.0:
            return "near", None
        if r <= source["R"]:
            bearing = math.degrees(math.atan2(gy - position[1], gx - position[0])) % 360.0
            return "direction", round((bearing + self.bearing_error_deg) % 360.0, 2)
        return "no_signal", None

    def _deadline_passed(self):
        if self.deadline_virtual_s is not None and self.virtual_time_s >= self.deadline_virtual_s - 1e-9:
            return True
        if self.deadline_real_monotonic is not None and self.clock() >= self.deadline_real_monotonic:
            return True
        return False

    # -- protocol -----------------------------------------------------------
    def handle(self, path, raw_body, content_type):
        """Return ``(status|None, json_body|NON_JSON|None, close_connection)``.

        ``status is None`` means "no response at all": the connection is closed.
        """
        fault = self._next_fault(path)
        if fault is not None and fault["mode"] == "delay":
            time.sleep(float(fault.get("seconds", 0.0)))
            fault = None

        if fault is not None and fault["mode"] == "http_415":
            return 415, self._common(False), False
        if not _content_type_ok(content_type):
            return 415, self._common(False), False
        if path not in ALLOWED_PATHS:
            return 404, self._common(False), False
        if raw_body is None:
            return 400, self._common(False), False
        if len(raw_body) > BODY_LIMIT:
            return 413, self._common(False), False
        try:
            body = json.loads(raw_body.decode("utf-8"), object_pairs_hook=_no_duplicates)
        except (_DuplicateKey, ValueError, UnicodeDecodeError):
            return 400, self._common(False), False
        if not isinstance(body, dict):
            return 400, self._common(False), False

        if fault is not None and fault["mode"] == "http_400":
            return 400, self._common(False), False
        if fault is not None and fault["mode"] == "http_500":
            return 500, self._common(False), False
        if fault is not None and fault["mode"] == "http_429":
            return 429, self._common(False), False
        if fault is not None and fault["mode"] == "missing_json":
            return 200, NON_JSON, False

        for field in ("arena_id", "robot_id", "request_id"):
            if field not in body or not isinstance(body[field], str) or not body[field]:
                return 400, self._common(False), False
        if path in ("/measure", "/clear"):
            if "position" not in body or "channel" not in body or not isinstance(body["position"], dict):
                return 400, self._common(False), False
            position = body["position"]
            if "x" not in position or "y" not in position:
                return 400, self._common(False), False
            for value in (position["x"], position["y"]):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return 400, self._common(False), False
                if not math.isfinite(value) or abs(value) > COORD_LIMIT:
                    return 400, self._common(False), False
            channel = body["channel"]
            if isinstance(channel, bool) or not isinstance(channel, (int, float)):
                return 400, self._common(False), False
            if float(channel) != int(channel) or not (1 <= int(channel) <= 20):
                return 400, self._common(False), False

        unknown = set(body) - DECLARED_FIELDS[path]
        if path in ("/measure", "/clear"):
            unknown |= set(body["position"]) - {"x", "y"}
        if unknown:
            return 200, self._common(False), False
        if body["arena_id"] != self.arena_id or body["robot_id"] != self.robot_id:
            return 200, self._common(False), False

        request_id = body["request_id"]
        fingerprint = json.dumps({"path": path, "body": body}, sort_keys=True)
        with self._lock:
            if request_id in self.idempotency:
                stored_fp, stored_response = self.idempotency[request_id]
                if stored_fp != fingerprint:
                    return 409, self._common(False), False
                if fault is not None and fault["mode"] == "lost_response":
                    return None, None, True      # the replayed response is lost again
                return 200, stored_response, False
            if self._deadline_passed():
                return None, None, True
            if fault is not None and fault["mode"] == "reject":
                return 200, self._common(False), False
            status, response = self._execute(path, body)
            if fault is not None and fault["mode"] == "lost_response":
                if status == 200 and response.get("accepted"):
                    self.idempotency[request_id] = (fingerprint, response)
                return None, None, True
            if status == 200 and response.get("accepted"):
                self.idempotency[request_id] = (fingerprint, response)
            return status, response, False

    def _execute(self, path, body):
        if self.exited:
            return 200, self._common(False)
        if path in ("/measure", "/clear") and not self.entered:
            return 200, self._common(False)
        if path == "/enter":
            if self.entered:
                return 200, self._common(False)
            self.entered = True
            response = self._common(True)
            response.update({
                "max_virtual_duration_s": self.max_virtual_duration_s,
                "max_real_duration_s": self.max_real_duration_s,
                "remaining_real_duration_s": int(self.remaining_real_duration_s),
            })
            self.executed.append({"path": path, "request_id": body["request_id"]})
            return 200, response

        if path in ("/measure", "/clear"):
            position = (float(body["position"]["x"]), float(body["position"]["y"]))
            move = math.hypot(position[0] - self.position[0], position[1] - self.position[1]) / 5.0
        if path == "/measure":
            channel = int(body["channel"])
            switch = 0.0 if channel == self.channel else 1.0
            self.virtual_time_s += move + switch + 5.0
            self.position = position
            self.channel = channel
            label, svd = self._observation(position, channel)
            response = self._common(True)
            response["measure_result"] = label
            if label == "direction":
                response["svd_deg"] = svd
        elif path == "/clear":
            channel = int(body["channel"])
            source = self.sources.get(channel)
            success = False
            if source is not None and not source.get("cleared"):
                gx, gy = source["g"]
                if math.hypot(position[0] - gx, position[1] - gy) <= 20.0:
                    success = True
                    source["cleared"] = True
            self.virtual_time_s += move + (5.0 if success else 3.0)
            self.position = position
            response = self._common(True)
            response["clear_result"] = "success" if success else "no_target_in_range"
        else:  # /exit
            self.exited = True
            response = self._common(True)
            response["exit_reason"] = "user_exit"
        self.executed.append({"path": path, "request_id": body["request_id"],
                              "virtual_time_s": self.virtual_time_s})
        self.request_log.append({"path": path, "request_id": body["request_id"]})
        return 200, response

    def _common(self, accepted):
        # OFFICIAL-003 section 4.1: an accepted=false response reports virtual_time_s = 0,
        # a sentinel that is not the current virtual clock.
        return {
            "accepted": bool(accepted),
            "real_timestamp_ms": int(self.clock() * 1000),
            "virtual_time_s": round(self.virtual_time_s, 6) if accepted else 0,
        }

    def accepted_actions(self):
        return [e["path"] for e in self.executed]


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    # one buffered write per response avoids a Nagle/delayed-ACK stall (test speed only)
    wbufsize = -1
    simulator = None

    def log_message(self, *args):
        return

    def _write(self, status, payload):
        head = (
            f"HTTP/1.1 {status} {self.responses.get(status, ('',))[0]}\r\n"
            f"Content-Type: application/json; charset=utf-8\r\n"
            f"Content-Length: {len(payload)}\r\n"
            f"Connection: keep-alive\r\n\r\n"
        ).encode("ascii")
        self.wfile.write(head + payload)

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        status, body, close = self.simulator.handle(self.path, raw, self.headers.get("Content-Type"))
        if status is None:
            self.close_connection = True
            return
        if body is NON_JSON:
            self._write(status, b"<html>not json</html>")
            return
        self._write(status, json.dumps(body).encode("utf-8"))

    def do_GET(self):  # noqa: N802
        # a known path with a non-POST method is 405; anything else is 404
        status = 405 if self.path in ALLOWED_PATHS else 404
        self._write(status, json.dumps(self.simulator._common(False)).encode("utf-8"))

    def do_PUT(self):  # noqa: N802
        self.do_GET()


class _Server(ThreadingHTTPServer):
    """Threaded server that does not join request threads on close (test speed)."""

    daemon_threads = True
    allow_reuse_address = True
    block_on_close = False


class MockServer:
    """Context manager running the mock on an ephemeral localhost port."""

    def __init__(self, simulator):
        self.simulator = simulator
        self.httpd = None
        self.thread = None
        self.base_url = None

    def __enter__(self):
        handler = type("BoundHandler", (_Handler,), {"simulator": self.simulator})
        self.httpd = _Server(("127.0.0.1", 0), handler)
        # a short poll interval keeps shutdown() from costing its default 0.5 s
        self.thread = threading.Thread(
            target=lambda: self.httpd.serve_forever(poll_interval=0.02), daemon=True
        )
        self.thread.start()
        host, port = self.httpd.server_address
        self.base_url = f"http://{host}:{port}"
        return self

    def __exit__(self, *exc):
        if self.httpd is not None:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread is not None:
            self.thread.join(timeout=5)
        return False
