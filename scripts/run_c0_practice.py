#!/usr/bin/env python3
"""C0 practice client for the official robot interface (WI-017, WI-034).

Drives the **frozen C0** policy (``src/candidate/``) through the P1-B adapter
(``src/protocol/``) using the **named practice configuration** of WI-034 / SR-004 /
D-009:

* **Q3 -> ``BASE``** -- ``P_3`` (9 points), 225-point clear rectangle;
* **Q4 -> ``SCAN49``** -- the complete ``P_4' = {700(i, j) : i, j = -3..3}`` lattice
  (49 points, all 28 exterior points kept), 225-point clear rectangle;
* **Q4 BASE fallback** -- explicit, fail-closed opt-in (``--q4-base-fallback``) that
  selects the repaired BASE 81-point scan; nothing else is reachable from this entry.

CLEAR150, COMBINED and C1 are **not** selectable here, and this script is deliberately
not a general variant selector: :data:`SELECTABLE_TAGS` is the closed set.

Safety rules enforced here:

* **practice only** -- ``--confirm-practice`` must be given explicitly, and the
  run aborts without ``/enter`` if the mode is anything else.  A formal session
  must never be entered by this script;
* serial requests only, one in flight at a time;
* stop on an unknown acceptance state (never send a new ``request_id``), on a
  protocol/ledger inconsistency, and when the real-time budget is spent;
* C1 is closed: no adaptive action is ever taken (``adaptive_actions == 0``);
* simulator internals (``JammersSimulatorData`` and friends) are never read;
* the logged configuration is the *resolved plan*, and it is reported together with
  actual action-derived counts plus a match verdict -- a label alone is not evidence.

Examples::

    # offline dry run against the bundled mock (no simulator needed)
    PYTHONPATH=src python scripts/run_c0_practice.py --mock --problem Q3

    # practice against the local service (only after the operator confirms the
    # session shown by the simulator UI is 演练/practice)
    PYTHONPATH=src python scripts/run_c0_practice.py --problem Q3 \
        --robot-id <team> --confirm-practice
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from candidate import model as candidate_model          # noqa: E402
from candidate import observe as candidate_observe      # noqa: E402
from candidate import scan as candidate_scan            # noqa: E402
from candidate import variants as candidate_variants    # noqa: E402
from protocol.client import DEFAULT_BASE_URL, RobotClient  # noqa: E402
from protocol.errors import ProtocolError, UnknownAcceptError  # noqa: E402
from protocol.session import PracticeSession, SessionConfirmation  # noqa: E402

#: the named configuration (WI-034 / SR-004 / D-009)
NAMED_TAG = {"Q3": "BASE", "Q4": "SCAN49"}
#: the only fallback this entry may offer, and only for Q4
FALLBACK_Q4_TAG = "BASE"
#: closed set: no CLEAR150, no COMBINED, no general selector
SELECTABLE_TAGS = ("BASE", "SCAN49")
#: mechanically checkable invariants: (problem, tag) -> scan/measure/switch/clear
NAMED_INVARIANTS = {
    ("Q3", "BASE"): {"scan_points": 9, "measures": 180, "switches": 179, "clear_count": 225},
    ("Q4", "SCAN49"): {"scan_points": 49, "measures": 980, "switches": 979, "clear_count": 225},
    ("Q4", "BASE"): {"scan_points": 81, "measures": 1620, "switches": 1619, "clear_count": 225},
}

#: read the mock only in --mock mode; it lives with the P1-B tests
MOCK_DIR = REPO / "tests" / "p1b"
#: the WI-020 cost accountant (itemized plan section 5.3 terms)
COSTING_DIR = REPO / "tests"
if str(COSTING_DIR) not in sys.path:
    sys.path.insert(0, str(COSTING_DIR))


def resolve_plan(problem, q4_base_fallback=False):
    """Resolve the named configuration for the practice entry (fail-closed).

    Returns ``(tag, plan)``.  Only the two named tags and the explicit Q4 BASE
    fallback can resolve; anything else raises, so CLEAR150/COMBINED are unreachable
    from this entry and the Q3 configuration cannot be deflected.
    """
    if problem not in NAMED_TAG:
        raise ValueError(f"unknown problem {problem!r}; expected one of {tuple(NAMED_TAG)}")
    if q4_base_fallback:
        if problem != "Q4":
            raise ValueError("the BASE fallback is defined for Q4 only")
        tag = FALLBACK_Q4_TAG
    else:
        tag = NAMED_TAG[problem]
    if tag not in SELECTABLE_TAGS:
        raise ValueError(f"refusing unresolved configuration {tag!r} for {problem}")
    if problem == "Q3" and tag != "BASE":
        raise ValueError("Q3 must use BASE (9-point scan, 225-point clear)")
    plan = candidate_variants.plan_for(tag)
    return tag, plan


def _file_sha256(path):
    try:
        return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _git_head():
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                             capture_output=True, timeout=10)
        return out.stdout.decode().strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def source_identity():
    """Runtime identity of the modules that define the resolved configuration."""
    import candidate.model as model_mod
    import candidate.scan as scan_mod
    import candidate.variants as variants_mod

    identity = {
        "src/candidate/variants.py_sha256": _file_sha256(variants_mod.__file__),
        "src/candidate/scan.py_sha256": _file_sha256(scan_mod.__file__),
        "src/candidate/model.py_sha256": _file_sha256(model_mod.__file__),
        "python": sys.version.split()[0],
    }
    head = _git_head()
    if head:
        identity["git_HEAD"] = head
    return identity


def check_named_invariants(problem, tag, plan):
    """Compare the resolved plan against the WI-034 invariants (mechanical).

    Returns ``{"expected": ..., "observed": ..., "matches": bool, "mismatches": [...]}``.
    """
    key = (problem, tag)
    if key not in NAMED_INVARIANTS:
        return {"expected": None, "observed": None, "matches": False,
                "mismatches": [f"no invariant registered for {problem}/{tag}"]}
    points = plan.scan_point_count(problem)
    observed = {
        "scan_points": points,
        "measures": plan.measure_count(problem),
        "switches": plan.switch_count(problem),
        "clear_count": plan.clear_count,
    }
    expected = dict(NAMED_INVARIANTS[key])
    mismatches = [f"{field}: expected {expected[field]}, observed {observed[field]}"
                  for field in expected if expected[field] != observed[field]]
    return {"expected": expected, "observed": observed,
            "matches": not mismatches, "mismatches": mismatches}


def configuration_record(problem, tag, plan, mode, q4_base_fallback):
    """The full resolved configuration written into the run report."""
    points = plan.scan_points(problem)
    exterior = sum(1 for p in points if math.hypot(p[0], p[1]) > 1800.0)
    return {
        "requested_problem": problem,
        "requested_mode": mode,
        "requested_q4_base_fallback": bool(q4_base_fallback),
        "resolved_tag": tag,
        "selectable_tags": list(SELECTABLE_TAGS),
        "identity": source_identity(),
        "planned": {
            "scan_points": len(points),
            "scan_exterior_points_outside_1800": exterior,
            "clear_count": plan.clear_count,
            "measures": plan.measure_count(problem),
            "switches": plan.switch_count(problem),
            "request_bound": plan.total_request_bound(problem),
            "budget_s": plan.budget(problem),
            "scan_route_length_m": plan.scan_route_length(problem),
            "ideal_clear_path_m": plan.describe()["ideal_clear_path_m"],
            "submitted_clear_path_m": plan.describe()["submitted_clear_path_m"],
            "channels": list(candidate_scan.Q3_Q4_CHANNELS),
        },
    }


def emitted_counts(requests):
    """Actual action-derived counts from the emitted request log.

    Derived from the wire log itself — not from a label, and not from the plan — so
    the comparison in :func:`verify_emitted_configuration` is non-trivial.
    """
    measures, clears = [], []
    for entry in requests:
        body = entry["body"]
        if entry["path"] == "/measure":
            measures.append((round(body["position"]["x"], 6), round(body["position"]["y"], 6),
                             body["channel"]))
        elif entry["path"] == "/clear":
            response = entry.get("raw_response") or {}
            clears.append((body["channel"], response.get("clear_result") == "success"))
    points = {(x, y) for x, y, _c in measures}
    switches = sum(1 for k in range(1, len(measures)) if measures[k][2] != measures[k - 1][2])
    attempts = {}
    for channel, _success in clears:
        attempts[channel] = attempts.get(channel, 0) + 1
    return {
        "measure_requests": len(measures),
        "clear_requests": len(clears),
        "distinct_scan_points": len(points),
        "distinct_channels_measured": len({c for _x, _y, c in measures}),
        "switches": switches,
        "clear_successes": sum(1 for _c, success in clears if success),
        "max_clear_attempts_per_channel": max(attempts.values()) if attempts else 0,
        "clear_attempts_per_channel": {str(k): v for k, v in sorted(attempts.items())},
    }


def verify_emitted_configuration(problem, tag, plan, emitted):
    """Aggregate-level screen of the emitted actions against the resolved plan.

    **This is a readability/count screen, not the proof.**  Counts alone cannot
    distinguish two lattices with the same cardinality (a Q4 set shifted by one metre
    has 49 distinct points, 980 measures and 979 switches).  The exact proof is
    :func:`verify_scan_sequence` / :func:`verify_clear_sequence`; the entry requires
    both and reports them separately so an aggregate-only pass can never be mistaken
    for the exact one.
    """
    expected = {
        "scan_points": plan.scan_point_count(problem),
        "measures": plan.measure_count(problem),
        "switches": plan.switch_count(problem),
        "clear_count": plan.clear_count,
    }
    observed = {
        "scan_points": emitted["distinct_scan_points"],
        "measures": emitted["measure_requests"],
        "switches": emitted["switches"],
        "clear_count": None,
    }
    mismatches = []
    for field in ("scan_points", "measures", "switches"):
        if observed[field] != expected[field]:
            mismatches.append(f"{field}: plan {expected[field]}, emitted {observed[field]}")
    if emitted["measure_requests"] == 0:
        mismatches.append("no /measure was emitted")
    if emitted["clear_requests"] and emitted["max_clear_attempts_per_channel"] > plan.clear_count:
        mismatches.append("a clear walk exceeded the plan's clear_count")
    if not emitted["clear_requests"] and emitted["clear_successes"] != 0:
        mismatches.append("successes reported without a clear request")
    return {"expected": expected, "observed": observed, "mismatches": mismatches,
            "matches": not mismatches, "proof": False,
            "note": "aggregate screen only; exact verification is verify_scan_sequence/"
                    "verify_clear_sequence"}


# ---------------------------------------------------------------------------
# Exact ordered business-action verification (WI-036)
# ---------------------------------------------------------------------------
#
# The wire log holds **one record per logical action** (``ActionRecord.attempts`` and
# ``send_monotonic_s``/``recv_monotonic_s`` carry HTTP retry metadata), so the log
# order is the business-action order and a retry never becomes a new action.


def _key(x, y, channel):
    """Normalise one action for comparison (sub-nanometre; cannot hide a 1 m shift)."""
    return (round(float(x), 9), round(float(y), 9), int(channel))


def expected_measure_sequence(plan, problem, channels=None):
    """The exact ordered (x, y, channel) sequence the resolved plan must produce."""
    channel_order = tuple(candidate_scan.Q3_Q4_CHANNELS if channels is None else channels)
    return [_key(p[0], p[1], c)
            for p, c in candidate_scan.scan_sequence(plan.scan_points(problem), channel_order)]


def emitted_measure_sequence(requests):
    """Ordered measured business actions taken from the request records."""
    return [_key(entry["body"]["position"]["x"], entry["body"]["position"]["y"],
                 entry["body"]["channel"])
            for entry in requests if entry["path"] == "/measure"]


def emitted_clear_sequence(requests):
    """Ordered clear business actions taken from the request records."""
    return [_key(entry["body"]["position"]["x"], entry["body"]["position"]["y"],
                 entry["body"]["channel"])
            for entry in requests if entry["path"] == "/clear"]


def runner_clear_sequence(runner):
    """The clear actions the runner recorded, in emission order."""
    return [_key(item["point"][0], item["point"][1], item["channel"])
            for item in runner.clear_results]


def expected_clear_sequence_by_channel(plan, runner):
    """Per-channel clear plan derived from the runner's fixed first positive.

    Uses the same inputs ``C0Runner.run_clears`` uses (the stored first positive point
    and its bearing), so the comparison is against the very sequence the runner was
    authorised to execute -- not a re-derivation of the geometry.
    """
    expected = {}
    for channel in runner.store.discovered_channels():
        st = runner.store.channels[channel]
        fp = st.first_positive
        theta = fp.get("theta_hat") or 0.0
        points = plan.clear_plan(fp["point"], theta, fp["observation"])
        expected[channel] = [_key(x[0], x[1], channel) for x in points]
    return expected


def sequence_digest(sequence):
    """Deterministic compact identity of an ordered action sequence."""
    digest = hashlib.sha256()
    for x, y, channel in sequence:
        digest.update(f"{x!r},{y!r},{channel!r};".encode())
    return digest.hexdigest()


def first_sequence_mismatch(expected, observed, context=3):
    """Bounded first-mismatch diagnostic: position, value, and a small local window."""
    limit = min(len(expected), len(observed))
    index = None
    for k in range(limit):
        if expected[k] != observed[k]:
            index = k
            break
    if index is None and len(expected) != len(observed):
        index = limit
    if index is None:
        return None
    lo = max(0, index - context)
    window = [{"index": k,
               "expected": expected[k] if k < len(expected) else "<past-end>",
               "observed": observed[k] if k < len(observed) else "<past-end>"}
              for k in range(lo, min(max(len(expected), len(observed)), index + context + 1))]
    return {
        "first_mismatch_index": index,
        "expected_length": len(expected),
        "observed_length": len(observed),
        "expected_at_index": expected[index] if index < len(expected) else "<past-end>",
        "observed_at_index": observed[index] if index < len(observed) else "<past-end>",
        "window": window,
    }


def compare_sequences(expected, observed):
    """Exact ordered comparison plus compact identities and a bounded diagnostic."""
    mismatch = first_sequence_mismatch(expected, observed)
    return {
        "matches": expected == observed,
        "expected_length": len(expected),
        "observed_length": len(observed),
        "expected_digest_sha256": sequence_digest(expected),
        "observed_digest_sha256": sequence_digest(observed),
        "first_mismatch": mismatch,
    }


def verify_scan_sequence(plan, problem, requests, runner):
    """EXACT proof for the scan stage: every (x, y, channel), in order.

    Compares three things against the sequence the resolved plan must produce: the
    request records, and independently the runner's own scan record, so a log that
    disagrees with the policy (or a policy that disagrees with the plan) is caught.
    """
    expected = expected_measure_sequence(plan, problem)
    from_log = emitted_measure_sequence(requests)
    from_runner = [_key(item["point"][0], item["point"][1], item["channel"])
                   for item in runner.scan_results]
    log_check = compare_sequences(expected, from_log)
    runner_check = compare_sequences(expected, from_runner)
    mismatches = []
    if not log_check["matches"]:
        mismatches.append("emitted wire log differs from the resolved plan's scan sequence: "
                          + json.dumps(log_check["first_mismatch"], default=str))
    if not runner_check["matches"]:
        mismatches.append("runner scan record differs from the resolved plan's scan sequence: "
                          + json.dumps(runner_check["first_mismatch"], default=str))
    return {"stage": "scan", "expected_length": len(expected),
            "emitted_log": log_check, "runner_record": runner_check,
            "expected_sample": [list(a) for a in expected[:2]] + [list(a) for a in expected[-2:]],
            "mismatches": mismatches, "matches": not mismatches, "proof": True}


def verify_clear_sequence(plan, runner, requests):
    """EXACT proof for the clear stage: same plan, same actions, legal prefixes.

    * the wire log's clear actions must equal the actions the runner recorded;
    * per discovered channel, the executed actions must be a **prefix** of that
      channel's clear plan for its fixed first positive observation (early success is
      valid, so all 225 attempts are never required);
    * a channel whose executed actions stop before success would show as an
      incomplete prefix and is reported.
    """
    log_actions = emitted_clear_sequence(requests)
    runner_actions = runner_clear_sequence(runner)
    mismatches = []
    if log_actions != runner_actions:
        mismatches.append("emitted wire log's clear actions differ from the runner's clear "
                          "record: " + json.dumps(first_sequence_mismatch(runner_actions, log_actions),
                                                  default=str))
    expected_by_channel = expected_clear_sequence_by_channel(plan, runner)
    executed_by_channel = {}
    for x, y, channel in log_actions:
        executed_by_channel.setdefault(channel, []).append((x, y, channel))
    prefix_report = {}
    for channel, executed in sorted(executed_by_channel.items()):
        full = expected_by_channel.get(channel)
        if full is None:
            mismatches.append(f"channel {channel}: clear actions emitted for an undiscovered channel")
            continue
        prefix_report[channel] = {"executed": len(executed), "plan_length": len(full),
                                  "is_prefix": executed == full[:len(executed)]}
        if executed != full[:len(executed)]:
            mismatches.append(
                f"channel {channel}: executed clear actions are not a prefix of the plan's "
                f"clear sequence: "
                + json.dumps(first_sequence_mismatch(full[:len(executed)], executed), default=str))
    for channel in expected_by_channel:
        if channel not in executed_by_channel and runner.store.channels[channel].cleared:
            mismatches.append(f"channel {channel}: recorded as cleared without emitted clear actions")
    return {"stage": "clear", "plan_channels": len(expected_by_channel),
            "expected_prefix_totals": {str(c): len(v) for c, v in sorted(expected_by_channel.items())},
            "executed_totals": {str(c): len(v) for c, v in sorted(executed_by_channel.items())},
            "prefixes": prefix_report,
            "log_matches_runner_record": log_actions == runner_actions,
            "mismatches": mismatches, "matches": not mismatches, "proof": True}


def verify_exact_action_evidence(plan, problem, requests, runner):
    """The exact proof used by the entry: scan sequence + clear sequences + aggregates."""
    scan = verify_scan_sequence(plan, problem, requests, runner)
    clear = verify_clear_sequence(plan, runner, requests)
    return {"scan": scan, "clear": clear, "matches": scan["matches"] and clear["matches"],
            "mismatches": scan["mismatches"] + clear["mismatches"], "proof": True}



def itemized_cost(question, requests):
    """Split the live request log into the plan section 5.3 cost terms.

    ``measure`` and ``clear`` requests are replayed in emission order; the
    decomposition is independent of the candidate's own ledger.
    """
    from tests.c0_baseline import costing

    class Recorded:
        __slots__ = ("action", "point", "channel", "success")

        def __init__(self, entry):
            body = entry["body"]
            self.action = "measure" if entry["path"] == "/measure" else "clear"
            self.point = (body["position"]["x"], body["position"]["y"])
            self.channel = body["channel"]
            response = entry.get("raw_response") or {}
            self.success = response.get("clear_result") == "success"

    actions = [Recorded(entry) for entry in requests if entry["path"] in ("/measure", "/clear")]
    return costing.decompose(actions, question)


class ProtocolEnv:
    """Frozen-C0 environment interface backed by the practice session."""

    def __init__(self, session):
        self.session = session
        self.measure_calls = 0
        self.clear_calls = 0

    def measure(self, position, channel):
        response = self.session.measure(position, channel)
        self.measure_calls += 1
        from protocol.mapping import measure_envelope
        return measure_envelope(response)

    def clear(self, position, channel):
        response = self.session.clear(position, channel)
        self.clear_calls += 1
        from protocol.mapping import clear_envelope
        return clear_envelope(response)


def _mock_session(problem, robot_id, bearing_error_deg):
    if str(MOCK_DIR) not in sys.path:
        sys.path.insert(0, str(MOCK_DIR))
    from mock_server import MockServer, MockSimulator  # noqa: E402

    sources = {}
    for index in range(1, 11):
        angle = math.radians(36.0 * index)
        radius = 200.0 + 40.0 * index
        sources[index] = {
            "g": (radius * math.cos(angle), radius * math.sin(angle)),
            "R": 1500.0,
            "directional": problem == "Q4" and index % 3 == 0,
            "phi_deg": 30.0 * index,
            "cleared": False,
        }
    simulator = MockSimulator(robot_id=robot_id, bearing_error_deg=bearing_error_deg, sources=sources)
    server = MockServer(simulator)
    server.__enter__()
    return simulator, server


def run(args):
    # The report is complete from the start (WI-036 defect 3): every path, including a
    # pre-enter refusal, yields the same keys, so no renderer can index a missing field.
    report = {
        "problem": args.problem,
        "mode": "mock" if args.mock else args.mode,
        "base_url": args.mock_url_label if args.mock else args.base_url,
        "robot_id": args.robot_id,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "outcome": None,
        "notes": [],
        "resolved_tag": None,
        "configuration": {},
        "scan_points": None,
        "planned_measures": None,
        "enter": None,
        "completion": None,
        "emitted": {},
        "cost": {},
        "requests": [],
        "ledger": {"candidate_total": 0.0, "max_residual_s": 0.0},
        "session": {
            "mode": "mock" if args.mock else args.mode,
            "stop_reason": "not_started",
            "accepted_actions": 0,
            "unknown_accept_count": 0,
            "adaptive_actions": 0,
            "adaptive_enabled": False,
            "virtual_time_s": 0.0,
            "max_ledger_residual_s": 0.0,
        },
        "mock_state": None,
    }

    # -- named configuration resolution and invariants (WI-034/WI-036) --------------
    # Resolved and checked BEFORE any resource is constructed, so a refusal cannot leak
    # a mock server, a session or an /enter.
    tag, plan = resolve_plan(args.problem, q4_base_fallback=args.q4_base_fallback)
    report["resolved_tag"] = tag
    report["configuration"] = configuration_record(args.problem, tag, plan,
                                                   report["mode"], args.q4_base_fallback)
    invariants = check_named_invariants(args.problem, tag, plan)
    report["configuration"]["invariants"] = invariants
    if not invariants["matches"]:
        report["outcome"] = "STOPPED_CONFIGURATION_INVARIANT"
        report["session"]["stop_reason"] = "configuration_invariant"
        report["notes"].append("resolved plan violates the named invariant: "
                               + "; ".join(invariants["mismatches"]))
        report["notes"].append("no /enter was sent and no session or mock server was created")
        return report
    points = plan.scan_points(args.problem)
    report["scan_points"] = len(points)
    report["planned_measures"] = plan.measure_count(args.problem)

    server = None
    simulator = None
    if args.mock:
        simulator, server = _mock_session(args.problem, args.robot_id, args.bearing_error_deg)
        base_url = server.base_url
        report["base_url"] = "mock:" + base_url
    else:
        base_url = args.base_url

    client = RobotClient(base_url, robot_id=args.robot_id, timeout=args.timeout,
                         max_retries=args.max_retries, id_prefix="c0")
    confirmation = None
    if not args.mock:
        confirmation = SessionConfirmation(args.confirm_session_problem, args.mode,
                                           args.robot_id, args.base_url)
        report["session_confirmation"] = confirmation.to_dict()
    session = PracticeSession(client, margin_s=args.time_margin_s, mode=args.mode,
                              require_practice_confirmation=True, confirmation=confirmation)
    env = ProtocolEnv(session)
    runner = None
    entered = False
    scan_verified = False

    try:
        enter = session.enter(problem=args.problem)
        entered = True
        report["enter"] = {
            "virtual_time_s": enter.virtual_time_s,
            "remaining_real_duration_s": enter.remaining_real_duration_s,
            "max_virtual_duration_s": enter.max_virtual_duration_s,
            "max_real_duration_s": enter.max_real_duration_s,
        }
        runner = candidate_model.C0Runner(env, channels=candidate_scan.Q3_Q4_CHANNELS, plan=plan)
        runner.run_scan(points, question=args.problem)
        report["scan_completed"] = True

        # -- exact scan verification BEFORE any clear action (WI-036 requirement 4) --
        scan_check = verify_scan_sequence(plan, args.problem, client.log(), runner)
        report["configuration"]["scan_sequence_verification"] = scan_check
        if not scan_check["matches"]:
            report["outcome"] = "STOPPED_SCAN_SEQUENCE_MISMATCH"
            report["notes"].append("emitted scan sequence differs from the resolved plan; "
                                   "no clear action was attempted")
            report["notes"].extend(scan_check["mismatches"])
        else:
            scan_verified = True
            runner.run_clears()
            report["clear_completed"] = True
            certificate = runner.completion_certificate()
            report["completion"] = {k: v for k, v in certificate.items()
                                    if k != "explicit_release_reasons"}
            report["outcome"] = ("COMPLETED" if certificate.get("status") == "COMPLETE"
                                 else certificate.get("status"))
        if args.exit:
            # The session was entered, so attempt the exit on every post-enter path.
            exit_response = session.finish()
            report["exit_reason"] = exit_response.exit_reason
            report["exit_virtual_time_s"] = exit_response.virtual_time_s
    except UnknownAcceptError as exc:
        session.note_unknown_accept()
        report["outcome"] = "STOPPED_UNKNOWN_ACCEPT"
        report["notes"].append(f"unknown acceptance state, stopped without a new request_id: {exc}")
    except ProtocolError as exc:
        report["outcome"] = "STOPPED_PROTOCOL"
        report["notes"].append(f"{type(exc).__name__}: {exc}")
    finally:
        try:
            report["session"] = session.report()
        except Exception as exc:                      # never mask the real outcome
            report["notes"].append(f"session report unavailable: {type(exc).__name__}: {exc}")
        report["ledger"] = {
            "candidate_total": session.tracker.candidate_total,
            "max_residual_s": session.tracker.max_residual,
        }
        report["requests"] = client.log()
        emitted = emitted_counts(report["requests"])
        report["emitted"] = emitted
        report["configuration"]["emitted_verification"] = verify_emitted_configuration(
            args.problem, tag, plan, emitted)
        if runner is not None:
            exact = verify_exact_action_evidence(plan, args.problem, report["requests"], runner)
            report["configuration"]["exact_action_verification"] = exact
            if not exact["matches"] and report["outcome"] == "COMPLETED":
                # a post-run mismatch must never retain COMPLETED (WI-036 requirement 5/6)
                report["outcome"] = "STOPPED_ACTION_SEQUENCE_MISMATCH"
                report["notes"].append("exact action verification failed after the run; "
                                       "COMPLETED is withdrawn")
                report["notes"].extend(exact["mismatches"])
        elif scan_verified:
            report["notes"].append("runner unavailable for exact verification")
        cost = itemized_cost(args.problem, report["requests"])
        report["cost"] = cost.to_dict()
        report["cost"]["ledger_agrees_with_decomposition"] = (
            abs(session.tracker.candidate_total - cost.total_seconds) < 1e-6)
        report["cost"]["tv_over_k"] = (None if cost.k_success == 0
                                       else cost.total_seconds / cost.k_success)
        if simulator is not None:
            report["mock_state"] = {
                "executed_actions": len(simulator.executed),
                "entered": simulator.entered,
                "exited": simulator.exited,
                "cleared_channels": sorted(c for c, s in simulator.sources.items() if s.get("cleared")),
                "virtual_time_s": simulator.virtual_time_s,
            }
        if server is not None:
            server.__exit__(None, None, None)
    return report


def build_parser():
    parser = argparse.ArgumentParser(description="C0 practice client (WI-017, named entry WI-034)")
    parser.add_argument("--problem", choices=("Q3", "Q4"), default="Q3")
    parser.add_argument("--q4-base-fallback", action="store_true",
                        help="explicit fail-closed opt-in: run Q4 with the repaired BASE "
                             "81-point scan instead of the named SCAN49 configuration "
                             "(Q4 only; CLEAR150/COMBINED are not selectable)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--robot-id", default=None, help="logged-in team identifier (参赛队号)")
    parser.add_argument("--mode", choices=("practice", "formal"), default="practice",
                        help="the session mode the operator sees; formal aborts before /enter")
    parser.add_argument("--confirm-practice", action="store_true",
                        help="operator confirmation that the open session is a practice/演练 run")
    parser.add_argument("--confirm-session-problem", choices=("Q3", "Q4"), default=None,
                        help="the problem number the operator sees for the OPEN session; "
                             "must match --problem (WI-020 requires a fresh per-session check)")
    parser.add_argument("--mock", action="store_true", help="run offline against the bundled mock")
    parser.add_argument("--mock-url-label", default="http://127.0.0.1:2026")
    parser.add_argument("--bearing-error-deg", type=float, default=0.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--time-margin-s", type=float, default=5.0)
    parser.add_argument("--exit", action="store_true", default=True)
    parser.add_argument("--no-exit", dest="exit", action="store_false")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--log-path", default=None, help="optional path for the per-request log JSON")
    return parser


def _parse_args(argv=None, parser=None):
    """Parse and validate the CLI arguments, including the fail-closed refusals.

    Split out of :func:`main` so the refusal paths are directly testable.
    """
    parser = parser or build_parser()
    args = parser.parse_args(argv)

    if not args.robot_id:
        parser.error("--robot-id is required (must byte-equal the logged-in team identifier)")
    if args.q4_base_fallback and args.problem != "Q4":
        parser.error("refusing to run: --q4-base-fallback is defined for Q4 only")
    if args.problem == "Q3" and NAMED_TAG["Q3"] != "BASE":
        parser.error("refusing to run: Q3 must use the named BASE configuration")
    if not args.mock and args.mode != "practice":
        parser.error("refusing to run: the indicated mode is formal/正式; this WI may not enter it")
    if not args.mock and not args.confirm_practice:
        parser.error("refusing to send /enter: pass --confirm-practice only after checking that the "
                     "open session in the simulator UI is a practice/演练 run")
    if not args.mock:
        if args.confirm_session_problem is None:
            parser.error("refusing to send /enter: --confirm-session-problem is required; state the "
                         "problem number the operator sees for the OPEN session")
        if args.confirm_session_problem != args.problem:
            parser.error(f"refusing to send /enter: the open session is declared "
                         f"{args.confirm_session_problem} but --problem is {args.problem}")
    return args


def main(argv=None):
    args = _parse_args(argv)
    report = run(args)
    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if args.log_path:
        pathlib.Path(args.log_path).write_text(payload, encoding="utf-8")
    if args.json:
        print(payload)
    else:
        # Defensive rendering: every field is read with a default so no path -- including
        # a pre-enter refusal -- can raise KeyError (WI-036 defect 3).
        print(f"C0 practice run: problem={report.get('problem')} mode={report.get('mode')} "
              f"url={report.get('base_url')}")
        config = report.get("configuration") or {}
        planned = config.get("planned") or {}
        invariants = config.get("invariants") or {}
        aggregates = config.get("emitted_verification") or {}
        exact = config.get("exact_action_verification") or {}
        scan_check = config.get("scan_sequence_verification") or {}
        print(f"  resolved tag            : {config.get('resolved_tag')} "
              f"(requested {config.get('requested_problem')}, "
              f"q4_base_fallback={config.get('requested_q4_base_fallback')})")
        print(f"  planned scan/clear      : {planned.get('scan_points')} points / "
              f"{planned.get('clear_count')} clear centres "
              f"(exterior pts {planned.get('scan_exterior_points_outside_1800')})")
        print(f"  planned bounds          : measures={planned.get('measures')} "
              f"switches={planned.get('switches')} requests={planned.get('request_bound')} "
              f"budget={planned.get('budget_s')}s")
        print(f"  invariant match         : {invariants.get('matches')} "
              f"{invariants.get('mismatches') or ''}")
        emitted = report.get("emitted") or {}
        print(f"  emitted (from wire log) : measures={emitted.get('measure_requests')} "
              f"distinct scan points={emitted.get('distinct_scan_points')} "
              f"switches={emitted.get('switches')} clear requests={emitted.get('clear_requests')} "
              f"successes={emitted.get('clear_successes')} "
              f"max clear attempts/channel={emitted.get('max_clear_attempts_per_channel')}")
        print(f"  aggregate screen        : {aggregates.get('matches')} "
              f"(counts only, not the proof) {aggregates.get('mismatches') or ''}")
        if scan_check:
            print(f"  exact scan sequence     : {scan_check.get('matches')} "
                  f"len={scan_check.get('expected_length')} "
                  f"expected {str((scan_check.get('emitted_log') or {}).get('expected_digest_sha256'))[:16]}... "
                  f"emitted {str((scan_check.get('emitted_log') or {}).get('observed_digest_sha256'))[:16]}...")
        if exact:
            scan_part = exact.get("scan") or {}
            clear_part = exact.get("clear") or {}
            print(f"  exact action proof      : {exact.get('matches')} "
                  f"(scan {scan_part.get('matches')}, clear {clear_part.get('matches')}) "
                  f"{exact.get('mismatches') or ''}")
            first = (scan_part.get("emitted_log") or {}).get("first_mismatch")
            if first:
                print(f"  first scan mismatch     : index {first.get('first_mismatch_index')} "
                      f"expected {first.get('expected_at_index')} "
                      f"observed {first.get('observed_at_index')}")
            prefixes = clear_part.get("prefixes") or {}
            if prefixes:
                bad = {c: v for c, v in prefixes.items() if not v.get("is_prefix")}
                print(f"  clear prefixes          : {len(prefixes)} channels, "
                      f"{'all legal prefixes' if not bad else f'ILLEGAL: {bad}'}")
        session_info = report.get("session") or {}
        print(f"  outcome                 : {report.get('outcome')}")
        print(f"  stop_reason             : {session_info.get('stop_reason')}")
        print(f"  accepted_actions        : {session_info.get('accepted_actions')}")
        print(f"  unknown_accept_count    : {session_info.get('unknown_accept_count')}")
        print(f"  adaptive_actions        : {session_info.get('adaptive_actions')} "
              f"(adaptive_enabled={session_info.get('adaptive_enabled')})")
        print(f"  virtual_time_s          : {session_info.get('virtual_time_s')}")
        print(f"  max_ledger_residual_s   : {session_info.get('max_ledger_residual_s')}")
        if report.get("enter"):
            print(f"  enter remaining real s  : {report['enter']['remaining_real_duration_s']}")
        if report.get("completion"):
            print(f"  completion              : {report['completion'].get('status')} "
                  f"success={report['completion'].get('success_count')}")
        for note in report["notes"]:
            print(f"  note                    : {note}")
    return 0 if report["outcome"] in ("COMPLETED",) else 1


if __name__ == "__main__":
    raise SystemExit(main())
