"""WI-020 offline full-flow tests: Q3, Q4, N=16 worst path, fail-closed cases.

The flows are driven through the frozen C0 runner (``d675831`` / ``scan.py`` blob
``32dd26f7...``) with deterministic scripted environments, plus one small physical
end-to-end run through the P1-B protocol adapter and its offline mock server.
Nothing here edits ``src/candidate/``.
"""

from __future__ import annotations

import math
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from candidate import model as candidate_model  # noqa: E402
from candidate import observe as candidate_observe  # noqa: E402
from candidate import scan  # noqa: E402
from protocol.errors import ProtocolStop, UnknownAcceptError  # noqa: E402

from tests.c0_baseline import costing, flow, scenario  # noqa: E402
from tests.c0_baseline.scenario import ChannelScript  # noqa: E402


class TestQ3FullFlow(unittest.TestCase):
    def setUp(self):
        self.result = flow.run_flow("Q3", scenario.q3_full_flow_channels())

    def test_certificate_is_complete_without_conflict_or_fewer_than_sixteen(self):
        self.assertTrue(self.result.completed, self.result.certificate)
        self.assertEqual(self.result.certificate["status"], candidate_model.COMPLETE)
        self.assertEqual(self.result.certificate["status"], "COMPLETE")

    def test_every_discovered_channel_is_cleared_or_certified_no_source(self):
        cert = self.result.certificate
        self.assertEqual(len(cert["cleared"]), cert["success_count"])
        covered = set(cert["cleared"]) | set(cert["no_source_channels"])
        self.assertEqual(covered, set(scan.Q3_Q4_CHANNELS))

    def test_first_positive_is_saved_for_each_discovered_channel(self):
        store = self.result.runner.store
        for channel in store.discovered_channels():
            fp = store.channels[channel].first_positive
            self.assertIsNotNone(fp, channel)
            self.assertIn(fp["observation"], (candidate_observe.NEAR, candidate_observe.DIRECTION))
            self.assertEqual(len(fp["point"]), 2)

    def test_clear_list_is_225_centres_for_direction_and_one_point_for_near(self):
        store = self.result.runner.store
        for channel in store.discovered_channels():
            fp = store.channels[channel].first_positive
            plan = scan.clear_plan(fp["point"], fp.get("theta_hat") or 0.0, fp["observation"])
            if fp["observation"] == candidate_observe.DIRECTION:
                self.assertEqual(len(plan), 225, channel)
            else:
                self.assertEqual(plan, [tuple(fp["point"])], channel)

    def test_simulated_exit_is_recorded_and_costless(self):
        self.assertTrue(self.result.exit_seen)
        self.assertEqual(self.result.runner.ledger.n_exit, 1)
        self.assertEqual(self.result.runner.ledger.n_enter, 1)

    def test_no_fail_closed_event_and_no_false_completion(self):
        self.assertIsNone(self.result.stop_reason)
        self.assertFalse(self.result.unknown_accept)
        self.assertFalse(self.result.false_completion)


class TestQ4FullFlow(unittest.TestCase):
    def setUp(self):
        self.result = flow.run_flow("Q4", scenario.q4_full_flow_channels())

    def test_certificate_is_complete(self):
        self.assertTrue(self.result.completed, self.result.certificate)

    def test_measure_and_switch_counts_match_the_plan(self):
        self.assertEqual(self.result.cost.n_measure, candidate_model.c0_measure_count("Q4"))
        self.assertEqual(self.result.cost.n_switch, candidate_model.c0_switch_count("Q4"))

    def test_ledger_agrees_with_the_independent_decomposition(self):
        self.assertAlmostEqual(self.result.ledger_recomputed, self.result.cost.total_seconds, places=9)


class TestN16WorstPath(unittest.TestCase):
    """N=16 discovered channels, each needing all 225 clear attempts."""

    def test_q3_worst_path_hits_the_plan_request_bound(self):
        result = flow.run_flow("Q3", scenario.worst_path_channels(16))
        self.assertTrue(result.completed, result.certificate)
        self.assertEqual(result.certificate["success_count"], 16)
        self.assertEqual(result.actions_at_stop, candidate_model.c0_total_request_bound("Q3"))
        self.assertEqual(result.actions_at_stop, 3780)

    def test_q4_worst_path_hits_the_plan_request_bound(self):
        result = flow.run_flow("Q4", scenario.worst_path_channels(16))
        self.assertTrue(result.completed, result.certificate)
        self.assertEqual(result.certificate["success_count"], 16)
        self.assertEqual(result.actions_at_stop, candidate_model.c0_total_request_bound("Q4"))
        self.assertEqual(result.actions_at_stop, 5220)

    def test_every_channel_is_attempted_exactly_225_times(self):
        for question in ("Q3", "Q4"):
            result = flow.run_flow(question, scenario.worst_path_channels(16))
            attempts = result.cost.attempts_per_channel
            self.assertEqual(len(attempts), 16, question)
            self.assertEqual(set(attempts.values()), {225}, question)

    def test_worst_path_virtual_cost_stays_inside_the_closed_form_budget(self):
        for question in ("Q3", "Q4"):
            result = flow.run_flow(question, scenario.worst_path_channels(16))
            budget = candidate_model.c0_budget_certificate(question)
            self.assertLess(result.ledger_recomputed, budget, question)
            self.assertLess(result.cost.total_seconds, budget, question)

    def test_each_clear_stage_stays_inside_the_per_source_bound(self):
        bound = candidate_model.per_source_clear_bound()
        result = flow.run_flow("Q3", scenario.worst_path_channels(16))
        actions = result.env.actions
        stages = {}
        for action in actions:
            if action.action == "clear":
                stages.setdefault(action.channel, []).append(action)
        self.assertEqual(len(stages), 16)
        for channel, stage in stages.items():
            self.assertEqual(len(stage), 225, channel)
            local = scan.clear_rectangle_centres((0.0, 0.0), 0.0)
            intra = sum(math.dist(local[k - 1], local[k]) for k in range(1, len(local)))
            stage_seconds = intra / 5.0 + 224 * 3.0 + 5.0
            self.assertLess(stage_seconds, bound, channel)

    def test_worst_path_is_not_only_light_successes(self):
        result = flow.run_flow("Q3", scenario.worst_path_channels(16))
        self.assertEqual(result.cost.n_clear_fail, 16 * 224)
        self.assertEqual(result.cost.k_success, 16)


class TestFailClosed(unittest.TestCase):
    """Unknown acceptance state or a spent deadline must stop, never complete."""

    def test_unknown_accept_stops_without_a_completion_certificate(self):
        result = flow.run_flow("Q3", scenario.q3_full_flow_channels(), inject_unknown_accept_at=200)
        self.assertTrue(result.unknown_accept)
        self.assertEqual(result.stop_reason, "unknown_accept")
        self.assertEqual(result.certificate, {})
        self.assertFalse(result.completed)
        self.assertFalse(result.false_completion)

    def test_unknown_accept_emits_no_action_after_the_fault(self):
        result = flow.run_flow("Q3", scenario.q3_full_flow_channels(), inject_unknown_accept_at=200)
        self.assertEqual(result.actions_at_stop, 199)
        self.assertEqual(result.env.accepted_action_count(), 199)
        self.assertEqual([a.index for a in result.env.actions], list(range(1, 200)))
        self.assertEqual(result.env.actions_after(199), [])

    def test_unknown_accept_during_the_first_measure_is_fail_closed(self):
        result = flow.run_flow("Q3", scenario.q3_full_flow_channels(), inject_unknown_accept_at=1)
        self.assertEqual(result.actions_at_stop, 0)
        self.assertEqual(result.certificate, {})
        self.assertEqual(result.env.measure_calls, 0)

    def test_deadline_stop_is_fail_closed(self):
        result = flow.run_flow("Q3", scenario.q3_full_flow_channels(), inject_deadline_at=250)
        self.assertTrue(result.deadline_stop)
        self.assertEqual(result.stop_reason, "real_deadline")
        self.assertEqual(result.actions_at_stop, 249)
        self.assertEqual(result.certificate, {})
        self.assertFalse(result.false_completion)

    def test_a_never_clearing_channel_raises_instead_of_claiming_absent(self):
        # channel 3 is discovered but never clears: C0 must not report the source absent
        specs = [ChannelScript(3, candidate_observe.DIRECTION, 0.0, success_at_attempt=None)]
        result = flow.run_flow("Q3", specs)
        self.assertIsNotNone(result.stop_reason)
        self.assertEqual(result.certificate, {})
        self.assertIn("225-point clear coverage failed", result.error)


class TestScriptedScenarioSanity(unittest.TestCase):
    def test_first_positive_is_not_replaced_by_a_later_observation(self):
        # the channel is seen at the first scan point and again much later: the saved
        # first positive must stay at the first point (plan section 5.2)
        points = scan.snake_order(scan.P3())
        first, later = points[0], points[5]
        spec = ChannelScript(7, candidate_observe.DIRECTION, 0.25, first_point=first,
                             also_visible_at=(later,), success_at_attempt=1)
        result = flow.run_flow("Q3", [spec])
        fp = result.runner.store.channels[7].first_positive
        self.assertEqual(tuple(fp["point"]), tuple(first))
        self.assertNotEqual(tuple(fp["point"]), tuple(later))

    def test_scripted_env_only_answers_the_two_c0_actions(self):
        env = scenario.ScriptedEnv(scenario.q3_full_flow_channels(), total_stages=9)
        self.assertEqual(sorted(m for m in dir(env) if m in ("measure", "clear")), ["clear", "measure"])


class TestPhysicalAdapterFlow(unittest.TestCase):
    """One small real-HTTP end-to-end through the P1-B adapter and its mock server."""

    @classmethod
    def setUpClass(cls):
        p1b = REPO / "tests" / "p1b"
        if str(p1b) not in sys.path:
            sys.path.insert(0, str(p1b))

    def test_q3_physical_mock_full_flow_matches_the_simulated_clock(self):
        from mock_server import MockServer, MockSimulator
        from protocol.client import RobotClient
        from protocol.session import PracticeSession

        # A *legal* world: the plan requires N in [10,16], so a sub-minimum world
        # would (correctly) be reported as a quantity CONFLICT instead of COMPLETE.
        # Ten omni sources sit on the P3 lattice corners with R_c = 1000 (the lattice
        # spacing is 1400, so each is seen as `near` only at its own point).
        corners = scan.snake_order(scan.P3())
        sources = {}
        for index, channel in enumerate(range(1, 11)):
            g = corners[index % len(corners)]
            if index == 9:                      # second source sharing the first corner
                g = (corners[0][0] + 2.0, corners[0][1])
            sources[channel] = {"g": (float(g[0]), float(g[1])), "R": 1000.0,
                                "directional": False, "phi_deg": 0.0, "cleared": False}
        self.assertEqual(len(sources), 10)

        simulator = MockSimulator(robot_id="TEAM-BASELINE", sources=sources)
        with MockServer(simulator) as server:
            client = RobotClient(server.base_url, robot_id="TEAM-BASELINE", max_retries=2)
            session = PracticeSession(client, margin_s=0.05)
            session.enter()
            runner = candidate_model.C0Runner(session, channels=scan.Q3_Q4_CHANNELS)
            # PracticeSession exposes measure/clear; the C0 envelope is the adapter's mapping
            runner.env = _SessionEnv(session)
            runner.run_scan(scan.P3(), question="Q3")
            runner.run_clears()
            certificate = runner.completion_certificate()
            exit_response = session.finish()

        self.assertEqual(certificate["status"], "COMPLETE")
        self.assertEqual(certificate["success_count"], 10)
        self.assertEqual(exit_response.exit_reason, "user_exit")
        self.assertEqual(session.unknown_accept_count, 0)
        self.assertEqual(session.adaptive_actions, 0)
        self.assertLess(session.tracker.max_residual, 1e-3)
        self.assertEqual(simulator.entered, True)
        self.assertEqual(simulator.exited, True)

    def test_a_sub_minimum_world_is_a_quantity_conflict_not_a_completion(self):
        """N < 10 violates the official domain, so C0 must not report COMPLETE."""
        from mock_server import MockServer, MockSimulator
        from protocol.client import RobotClient
        from protocol.session import PracticeSession

        sources = {2: {"g": (1400.0, 0.0), "R": 1500.0, "directional": False,
                       "phi_deg": 0.0, "cleared": False}}
        simulator = MockSimulator(robot_id="TEAM-BASELINE", sources=sources)
        with MockServer(simulator) as server:
            client = RobotClient(server.base_url, robot_id="TEAM-BASELINE", max_retries=2)
            session = PracticeSession(client, margin_s=0.05)
            session.enter()
            runner = candidate_model.C0Runner(session, channels=scan.Q3_Q4_CHANNELS)
            runner.env = _SessionEnv(session)
            runner.run_scan(scan.P3(), question="Q3")
            certificate = runner.completion_certificate()
            session.finish()

        self.assertEqual(certificate["status"], "CONFLICT")
        self.assertTrue(any("proven + possible channels" in r for r in certificate["reasons"]),
                        certificate["reasons"])


class _SessionEnv:
    """Adapter shim: the practice session's accepted actions with the C0 envelope."""

    def __init__(self, session):
        self.session = session

    def measure(self, point, channel):
        from protocol.mapping import measure_envelope
        return measure_envelope(self.session.measure(point, channel))

    def clear(self, point, channel):
        from protocol.mapping import clear_envelope
        return clear_envelope(self.session.clear(point, channel))


if __name__ == "__main__":
    unittest.main()
