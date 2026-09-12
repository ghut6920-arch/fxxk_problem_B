#!/usr/bin/env python3
"""C0 practice client for the official robot interface (WI-017).

Drives the **frozen C0** policy (``src/candidate/``) through the P1-B adapter
(``src/protocol/``).  Q3 scans ``P_3`` (9 points), Q4 scans ``P_4`` (81 points);
channels 1..20 are measured at every point in snake order, then each discovered
channel is cleared with its 225-point rectangle (``near`` clears at the saved
point).

Safety rules enforced here:

* **practice only** -- ``--confirm-practice`` must be given explicitly, and the
  run aborts without ``/enter`` if the mode is anything else.  A formal session
  must never be entered by this script;
* serial requests only, one in flight at a time;
* stop on an unknown acceptance state (never send a new ``request_id``), on a
  protocol/ledger inconsistency, and when the real-time budget is spent;
* C1 is closed: no adaptive action is ever taken (``adaptive_actions == 0``);
* simulator internals (``JammersSimulatorData`` and friends) are never read.

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
import json
import math
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from candidate import model as candidate_model          # noqa: E402
from candidate import observe as candidate_observe      # noqa: E402
from candidate import scan as candidate_scan            # noqa: E402
from protocol.client import DEFAULT_BASE_URL, RobotClient  # noqa: E402
from protocol.errors import ProtocolError, UnknownAcceptError  # noqa: E402
from protocol.session import PracticeSession            # noqa: E402

#: read the mock only in --mock mode; it lives with the P1-B tests
MOCK_DIR = REPO / "tests" / "p1b"


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
    report = {
        "problem": args.problem,
        "mode": "mock" if args.mock else args.mode,
        "base_url": args.mock_url_label if args.mock else args.base_url,
        "robot_id": args.robot_id,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "outcome": None,
        "notes": [],
    }
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
    session = PracticeSession(client, margin_s=args.time_margin_s, mode=args.mode,
                              require_practice_confirmation=True)
    env = ProtocolEnv(session)
    points = candidate_scan.P3() if args.problem == "Q3" else candidate_scan.P4()
    report["scan_points"] = len(points)
    report["planned_measures"] = len(points) * len(candidate_scan.Q3_Q4_CHANNELS)

    try:
        enter = session.enter()
        report["enter"] = {
            "virtual_time_s": enter.virtual_time_s,
            "remaining_real_duration_s": enter.remaining_real_duration_s,
            "max_virtual_duration_s": enter.max_virtual_duration_s,
            "max_real_duration_s": enter.max_real_duration_s,
        }
        runner = candidate_model.C0Runner(env, channels=candidate_scan.Q3_Q4_CHANNELS)
        runner.run_scan(points, question=args.problem)
        report["scan_completed"] = True
        runner.run_clears()
        report["clear_completed"] = True
        certificate = runner.completion_certificate()
        report["completion"] = {k: v for k, v in certificate.items() if k != "explicit_release_reasons"}
        report["outcome"] = "COMPLETED" if certificate.get("status") == "COMPLETE" else certificate.get("status")
        if args.exit:
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
        report["session"] = session.report()
        report["ledger"] = {
            "candidate_total": session.tracker.candidate_total,
            "max_residual_s": session.tracker.max_residual,
        }
        report["requests"] = client.log()
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


def main(argv=None):
    parser = argparse.ArgumentParser(description="C0 practice client (WI-017)")
    parser.add_argument("--problem", choices=("Q3", "Q4"), default="Q3")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--robot-id", default=None, help="logged-in team identifier (参赛队号)")
    parser.add_argument("--mode", choices=("practice", "formal"), default="practice",
                        help="the session mode the operator sees; formal aborts before /enter")
    parser.add_argument("--confirm-practice", action="store_true",
                        help="operator confirmation that the open session is a practice/演练 run")
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
    args = parser.parse_args(argv)

    if not args.robot_id:
        parser.error("--robot-id is required (must byte-equal the logged-in team identifier)")
    if not args.mock and args.mode != "practice":
        parser.error("refusing to run: the indicated mode is formal/正式; this WI may not enter it")
    if not args.mock and not args.confirm_practice:
        parser.error("refusing to send /enter: pass --confirm-practice only after checking that the "
                     "open session in the simulator UI is a practice/演练 run")

    report = run(args)
    payload = json.dumps(report, indent=2, ensure_ascii=False, default=str)
    if args.log_path:
        pathlib.Path(args.log_path).write_text(payload, encoding="utf-8")
    if args.json:
        print(payload)
    else:
        print(f"C0 practice run: problem={report['problem']} mode={report['mode']} url={report['base_url']}")
        session_info = report["session"]
        print(f"  outcome                 : {report['outcome']}")
        print(f"  stop_reason             : {session_info['stop_reason']}")
        print(f"  accepted_actions        : {session_info['accepted_actions']}")
        print(f"  unknown_accept_count    : {session_info['unknown_accept_count']}")
        print(f"  adaptive_actions        : {session_info['adaptive_actions']} "
              f"(adaptive_enabled={session_info['adaptive_enabled']})")
        print(f"  virtual_time_s          : {session_info['virtual_time_s']}")
        print(f"  max_ledger_residual_s   : {session_info['max_ledger_residual_s']}")
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
