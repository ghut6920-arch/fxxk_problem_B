"""WI-034: the named C0 practice entry resolves Q3 BASE / Q4 SCAN49 (and Q4 BASE).

These tests bind the *real* practice entry (``scripts/run_c0_practice.py``) to the
approved configuration:

* named Q3 resolves to ``BASE`` with 9 scan / 180 measure / 179 switch / 225 clear;
* named Q4 resolves to ``SCAN49`` with 49 / 980 / 979 / 225 and the complete
  ``P_4'`` lattice including all 28 exterior points;
* the explicit Q4 BASE fallback resolves to 81 / 1620 / 1619 / 225;
* CLEAR150, COMBINED and unknown values cannot be selected;
* the *same* plan drives the scan points, the clear generator and the budget passed
  to ``C0Runner``;
* the logged configuration is verified against **action-derived** counts taken from
  the emitted request log, so a label alone cannot pass.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
for extra in (str(REPO), str(REPO / "src"), str(REPO / "scripts")):
    if extra not in sys.path:
        sys.path.insert(0, extra)

import run_c0_practice as entry  # noqa: E402

from candidate import model as candidate_model  # noqa: E402
from candidate import variants  # noqa: E402

SELECTABLE = ("BASE", "SCAN49")
FORBIDDEN = ("CLEAR150", "COMBINED", "C0", "ADAPTIVE", "SCAN25", "SCAN81")


class TestNamedResolution(unittest.TestCase):
    def test_q3_named_is_base_with_9_scan_and_225_clear(self):
        tag, plan = entry.resolve_plan("Q3")
        self.assertEqual(tag, "BASE")
        self.assertEqual(plan.scan_point_count("Q3"), 9)
        self.assertEqual(plan.measure_count("Q3"), 180)
        self.assertEqual(plan.switch_count("Q3"), 179)
        self.assertEqual(plan.clear_count, 225)
        self.assertEqual(len(plan.scan_points("Q3")), 9)

    def test_q4_named_is_scan49_with_49_scan_and_225_clear(self):
        tag, plan = entry.resolve_plan("Q4")
        self.assertEqual(tag, "SCAN49")
        self.assertEqual(plan.scan_point_count("Q4"), 49)
        self.assertEqual(plan.measure_count("Q4"), 980)
        self.assertEqual(plan.switch_count("Q4"), 979)
        self.assertEqual(plan.clear_count, 225)

    def test_named_q4_scan_is_the_complete_prescribed_lattice(self):
        _tag, plan = entry.resolve_plan("Q4")
        points = plan.scan_points("Q4")
        self.assertEqual(set(points), {(700.0 * i, 700.0 * j)
                                       for i in range(-3, 4) for j in range(-3, 4)})
        exterior = [p for p in points if (p[0] ** 2 + p[1] ** 2) ** 0.5 > 1800.0]
        self.assertEqual(len(exterior), 28)

    def test_q4_base_fallback_is_81_scan_and_225_clear(self):
        tag, plan = entry.resolve_plan("Q4", q4_base_fallback=True)
        self.assertEqual(tag, "BASE")
        self.assertEqual(plan.scan_point_count("Q4"), 81)
        self.assertEqual(plan.measure_count("Q4"), 1620)
        self.assertEqual(plan.switch_count("Q4"), 1619)
        self.assertEqual(plan.clear_count, 225)

    def test_named_tag_table_is_exactly_the_approved_mapping(self):
        self.assertEqual(entry.NAMED_TAG, {"Q3": "BASE", "Q4": "SCAN49"})
        self.assertEqual(entry.FALLBACK_Q4_TAG, "BASE")

    def test_invariants_match_for_all_three_configurations(self):
        for problem, fallback in (("Q3", False), ("Q4", False), ("Q4", True)):
            tag, plan = entry.resolve_plan(problem, q4_base_fallback=fallback)
            result = entry.check_named_invariants(problem, tag, plan)
            self.assertTrue(result["matches"], (problem, fallback, result["mismatches"]))
            self.assertEqual(result["observed"], result["expected"])

    def test_registered_invariants_are_the_wire_numbers(self):
        self.assertEqual(entry.NAMED_INVARIANTS[("Q3", "BASE")],
                         {"scan_points": 9, "measures": 180, "switches": 179, "clear_count": 225})
        self.assertEqual(entry.NAMED_INVARIANTS[("Q4", "SCAN49")],
                         {"scan_points": 49, "measures": 980, "switches": 979, "clear_count": 225})
        self.assertEqual(entry.NAMED_INVARIANTS[("Q4", "BASE")],
                         {"scan_points": 81, "measures": 1620, "switches": 1619, "clear_count": 225})


class TestForbiddenConfigurationsCannotBeSelected(unittest.TestCase):
    def test_selectable_set_excludes_clear150_and_combined(self):
        self.assertEqual(tuple(entry.SELECTABLE_TAGS), SELECTABLE)
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, entry.SELECTABLE_TAGS, forbidden)

    def test_resolver_never_returns_a_forbidden_tag(self):
        for problem, fallback in (("Q3", False), ("Q4", False), ("Q4", True)):
            tag, _plan = entry.resolve_plan(problem, q4_base_fallback=fallback)
            self.assertIn(tag, SELECTABLE)
            self.assertNotIn(tag, FORBIDDEN)

    def test_q3_cannot_be_deflected_to_another_tag(self):
        original = entry.NAMED_TAG["Q3"]
        try:
            entry.NAMED_TAG["Q3"] = "SCAN49"
            with self.assertRaises(ValueError):
                entry.resolve_plan("Q3")
        finally:
            entry.NAMED_TAG["Q3"] = original

    def test_q4_fallback_cannot_be_redirected_to_a_forbidden_tag(self):
        original = entry.FALLBACK_Q4_TAG
        try:
            entry.FALLBACK_Q4_TAG = "COMBINED"      # simulated mis-binding
            with self.assertRaises(ValueError):
                entry.resolve_plan("Q4", q4_base_fallback=True)
        finally:
            entry.FALLBACK_Q4_TAG = original

    def test_unknown_problem_and_q3_fallback_are_refused(self):
        with self.assertRaises(ValueError):
            entry.resolve_plan("Q5")
        with self.assertRaises(ValueError):
            entry.resolve_plan("Q3", q4_base_fallback=True)

    def test_cli_refuses_q3_with_the_fallback_flag(self):
        with self.assertRaises(SystemExit):
            entry.main(["--mock", "--problem", "Q3", "--q4-base-fallback",
                        "--robot-id", "TESTTEAM"])


class TestSamePlanDrivesScanClearAndBudget(unittest.TestCase):
    def test_the_plan_passed_to_the_runner_is_the_resolved_plan(self):
        for problem, fallback, expected in (("Q3", False, "BASE"),
                                            ("Q4", False, "SCAN49"),
                                            ("Q4", True, "BASE")):
            tag, plan = entry.resolve_plan(problem, q4_base_fallback=fallback)
            runner = candidate_model.C0Runner(env=None, plan=plan)
            self.assertIs(runner.plan, plan, (problem, fallback))
            self.assertEqual(runner._budget(problem), plan.budget(problem))
            self.assertEqual(runner._clear_plan((0.0, 0.0), 0.0, "direction"),
                             plan.clear_plan((0.0, 0.0), 0.0, "direction"))

    def test_named_q4_budget_is_the_scan49_envelope_not_the_base_one(self):
        _tag, scan49 = entry.resolve_plan("Q4")
        _tag2, base = entry.resolve_plan("Q4", q4_base_fallback=True)
        self.assertLess(scan49.budget("Q4"), base.budget("Q4"))
        self.assertEqual(scan49.budget("Q4"), 71794.5696961967)
        self.assertEqual(base.budget("Q4"), 81000.0)

    def test_clear_generator_comes_from_the_same_plan(self):
        for problem, fallback in (("Q3", False), ("Q4", False), ("Q4", True)):
            _tag, plan = entry.resolve_plan(problem, q4_base_fallback=fallback)
            centres = plan.clear_plan((0.0, 0.0), 0.0, "direction")
            self.assertEqual(len(centres), plan.clear_count)
            self.assertEqual(len(set(centres)), plan.clear_count)

    def test_scan_points_come_from_the_plan_not_from_a_global_lattice(self):
        _tag, plan = entry.resolve_plan("Q4")
        self.assertEqual(plan.scan_points("Q4"), variants.plan_for("SCAN49").scan_points("Q4"))
        _tag2, base = entry.resolve_plan("Q4", q4_base_fallback=True)
        self.assertEqual(base.scan_points("Q4"), variants.plan_for("BASE").scan_points("Q4"))
        self.assertNotEqual(plan.scan_points("Q4"), base.scan_points("Q4"))

    def test_configuration_record_reports_plan_derived_numbers(self):
        tag, plan = entry.resolve_plan("Q4")
        record = entry.configuration_record("Q4", "SCAN49", plan, "mock", False)
        self.assertEqual(record["resolved_tag"], "SCAN49")
        self.assertEqual(record["requested_q4_base_fallback"], False)
        self.assertEqual(record["planned"]["scan_points"], 49)
        self.assertEqual(record["planned"]["scan_exterior_points_outside_1800"], 28)
        self.assertEqual(record["planned"]["measures"], 980)
        self.assertEqual(record["planned"]["switches"], 979)
        self.assertEqual(record["planned"]["clear_count"], 225)
        self.assertEqual(record["planned"]["request_bound"], 4580)
        self.assertEqual(record["planned"]["channels"], list(range(1, 21)))
        for key in ("src/candidate/variants.py_sha256", "src/candidate/scan.py_sha256",
                    "src/candidate/model.py_sha256", "python"):
            self.assertTrue(record["identity"].get(key), key)


class TestLoggedConfigurationIsVerifiedAgainstEmittedActions(unittest.TestCase):
    """The log must agree with the wire log, not merely echo a label."""

    @staticmethod
    def _measure_requests(points, channels):
        return [{"path": "/measure", "body": {"position": {"x": p[0], "y": p[1]}, "channel": c},
                 "raw_response": {"measure_result": "no_signal"}}
                for p in points for c in channels]

    def test_emitted_counts_are_derived_from_the_request_log(self):
        _tag, plan = entry.resolve_plan("Q3")
        points = plan.scan_points("Q3")
        requests = self._measure_requests(points, plan.describe() and range(1, 21))
        emitted = entry.emitted_counts(requests)
        self.assertEqual(emitted["measure_requests"], 180)
        self.assertEqual(emitted["distinct_scan_points"], 9)
        self.assertEqual(emitted["switches"], 179)
        self.assertEqual(emitted["clear_requests"], 0)

    def test_verification_passes_when_actions_match_the_resolved_plan(self):
        for problem, fallback in (("Q3", False), ("Q4", False), ("Q4", True)):
            tag, plan = entry.resolve_plan(problem, q4_base_fallback=fallback)
            requests = self._measure_requests(plan.scan_points(problem), range(1, 21))
            emitted = entry.emitted_counts(requests)
            verdict = entry.verify_emitted_configuration(problem, tag, plan, emitted)
            self.assertTrue(verdict["matches"], (problem, fallback, verdict["mismatches"]))

    def test_aggregate_screen_alone_is_insufficient_shifted_lattice(self):
        """Records WHY the aggregate screen cannot be the proof (TR-038 defect 1).

        Shifting every planned x coordinate by one metre leaves 49 distinct points,
        980 measures and 979 switches, so the count screen still says 'matches'.  The
        exact ordered comparison in :class:`TestExactOrderedSequences` rejects it.  This
        test pins the insufficiency so the aggregate screen can never be mistaken for
        the proof again.
        """
        _tag, plan = entry.resolve_plan("Q4")
        shifted = [(x + 1.0, y) for x, y in plan.scan_points("Q4")]
        requests = self._measure_requests(shifted, range(1, 21))
        emitted = entry.emitted_counts(requests)
        self.assertEqual(emitted["measure_requests"], 980)
        self.assertEqual(emitted["distinct_scan_points"], 49)
        self.assertEqual(emitted["switches"], 979)
        verdict = entry.verify_emitted_configuration("Q4", "SCAN49", plan, emitted)
        self.assertTrue(verdict["matches"], "counts alone cannot see a 1 m shift")
        self.assertFalse(verdict["proof"])
        # ... and the exact comparison rejects the very same lattice
        expected = entry.expected_measure_sequence(plan, "Q4")
        self.assertFalse(entry.compare_sequences(expected, entry.emitted_measure_sequence(requests))["matches"])

    def test_verification_detects_a_mislabelled_or_wrong_lattice(self):
        """Negative controls: the aggregate screen must not simply repeat the label."""
        _tag, plan = entry.resolve_plan("Q4")          # SCAN49, 49 points
        # (a) a 5x5 substitute lattice: 25 points / 500 measures
        inner = [(700.0 * i, 700.0 * j) for i in range(-2, 3) for j in range(-2, 3)]
        emitted = entry.emitted_counts(self._measure_requests(inner, range(1, 21)))
        verdict = entry.verify_emitted_configuration("Q4", "SCAN49", plan, emitted)
        self.assertFalse(verdict["matches"])
        self.assertTrue(any("scan_points" in m for m in verdict["mismatches"]))
        # (b) the BASE 81-point lattice emitted while claiming the named SCAN49 plan
        base_points = variants.plan_for("BASE").scan_points("Q4")
        emitted = entry.emitted_counts(self._measure_requests(base_points, range(1, 21)))
        verdict = entry.verify_emitted_configuration("Q4", "SCAN49", plan, emitted)
        self.assertFalse(verdict["matches"])
        # (c) an empty log cannot be signed off
        verdict = entry.verify_emitted_configuration("Q4", "SCAN49", plan,
                                                     entry.emitted_counts([]))
        self.assertFalse(verdict["matches"])

    def test_clear_walk_beyond_the_plan_clear_count_is_detected(self):
        _tag, plan = entry.resolve_plan("Q4")
        requests = self._measure_requests(plan.scan_points("Q4"), range(1, 21))
        requests += [{"path": "/clear", "body": {"position": {"x": 0.0, "y": 0.0}, "channel": 1},
                      "raw_response": {"clear_result": "no_success"}} for _ in range(226)]
        emitted = entry.emitted_counts(requests)
        self.assertEqual(emitted["max_clear_attempts_per_channel"], 226)
        verdict = entry.verify_emitted_configuration("Q4", "SCAN49", plan, emitted)
        self.assertFalse(verdict["matches"])
        self.assertTrue(any("clear" in m for m in verdict["mismatches"]))

    def test_switch_count_follows_the_emitted_channel_order(self):
        _tag, plan = entry.resolve_plan("Q4")
        requests = self._measure_requests(plan.scan_points("Q4"), range(1, 21))
        emitted = entry.emitted_counts(requests)
        # 49 snake points x 20 channels: 19 switches per point + 1 between points
        self.assertEqual(emitted["switches"], 19 + 48 * 20)
        self.assertEqual(emitted["switches"], plan.switch_count("Q4"))

    def test_base_default_outside_this_entry_is_preserved(self):
        runner = candidate_model.C0Runner(env=None)
        self.assertIsNone(runner.plan)
        from candidate import model as model_mod
        self.assertEqual(runner._budget("Q3"), model_mod.c0_budget_certificate("Q3"))
        self.assertEqual(runner._budget("Q4"), model_mod.c0_budget_certificate("Q4"))


class TestExactOrderedSequences(unittest.TestCase):
    """WI-036: the proof is the full ordered (x, y, channel) sequence.

    Positive cases drive a real ``C0Runner`` bound to the resolved plan over the
    in-process scripted scenario, then build the request records from what that run
    actually emitted; negatives doctor those records while keeping aggregate counts
    identical.
    """

    PROBLEMS = (("Q3", False, "BASE"), ("Q4", False, "SCAN49"), ("Q4", True, "BASE"))

    @staticmethod
    def _requests(scan_results, clear_results):
        requests = []
        for item in scan_results:
            requests.append({"path": "/measure",
                             "body": {"position": {"x": item["point"][0], "y": item["point"][1]},
                                      "channel": item["channel"]},
                             "raw_response": {"measure_result": "no_signal"}})
        for item in clear_results:
            requests.append({"path": "/clear",
                             "body": {"position": {"x": item["point"][0], "y": item["point"][1]},
                                      "channel": item["channel"]},
                             "raw_response": {"clear_result": "no_success"}})
        return requests

    @staticmethod
    def _run(problem, fallback, success_at_attempt=1):
        from tests.c0_baseline import flow, scenario
        from candidate import observe as candidate_observe
        specs = [scenario.ChannelScript(c, candidate_observe.DIRECTION, 0.0,
                                        success_at_attempt=success_at_attempt)
                 for c in range(2, 12)]
        tag = "BASE" if (problem == "Q3" or fallback) else "SCAN49"
        return tag, flow.run_flow(problem, specs, tag=tag)

    def test_exact_measure_sequence_passes_for_all_three_configurations(self):
        for problem, fallback, expected_tag in self.PROBLEMS:
            tag, result = self._run(problem, fallback)
            plan = variants.plan_for(expected_tag)
            self.assertEqual(tag, expected_tag)
            requests = self._requests(result.runner.scan_results, result.runner.clear_results)
            check = entry.verify_scan_sequence(plan, problem, requests, result.runner)
            self.assertTrue(check["matches"], (problem, fallback, check["mismatches"]))
            self.assertTrue(check["proof"])
            self.assertEqual(check["expected_length"], plan.measure_count(problem))
            self.assertEqual(check["emitted_log"]["expected_digest_sha256"],
                             check["emitted_log"]["observed_digest_sha256"])

    def test_retry_attempts_remain_metadata_on_one_business_action(self):
        """A retried action keeps one record; attempts must not inflate the sequence."""
        _tag, result = self._run("Q3", False)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        for record in requests[:5]:
            record["attempts"] = 3
            record["send_monotonic_s"] = [1.0, 1.1, 1.2]
        check = entry.verify_scan_sequence(plan, "Q3", requests, result.runner)
        self.assertTrue(check["matches"])
        self.assertEqual(check["emitted_log"]["observed_length"], 180)

    def test_shifted_49_point_set_fails_despite_identical_aggregates(self):
        """TR-038 counterexample: every x shifted by 1 m must be rejected exactly."""
        _tag, result = self._run("Q4", False)
        plan = variants.plan_for("SCAN49")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        shifted = []
        for record in requests:
            record = json.loads(json.dumps(record))
            if record["path"] == "/measure":
                record["body"]["position"]["x"] += 1.0
            shifted.append(record)
        emitted = entry.emitted_counts(shifted)
        self.assertEqual((emitted["measure_requests"], emitted["distinct_scan_points"],
                          emitted["switches"]), (980, 49, 979))
        check = entry.verify_scan_sequence(plan, "Q4", shifted, result.runner)
        self.assertFalse(check["matches"])
        self.assertEqual(check["emitted_log"]["first_mismatch"]["first_mismatch_index"], 0)
        self.assertNotEqual(check["emitted_log"]["expected_digest_sha256"],
                            check["emitted_log"]["observed_digest_sha256"])

    def test_reordered_points_fail(self):
        _tag, result = self._run("Q4", False)
        plan = variants.plan_for("SCAN49")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        measures = [r for r in requests if r["path"] == "/measure"]
        clears = [r for r in requests if r["path"] == "/clear"]
        swapped = [measures[40]] + measures[1:40] + [measures[0]] + measures[41:]
        check = entry.verify_scan_sequence(plan, "Q4", swapped + clears, result.runner)
        self.assertFalse(check["matches"])

    def test_reordered_channels_fail(self):
        _tag, result = self._run("Q3", False)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        measures = [r for r in requests if r["path"] == "/measure"]
        swapped = [json.loads(json.dumps(r)) for r in measures]
        swapped[0]["body"]["channel"], swapped[1]["body"]["channel"] = (
            swapped[1]["body"]["channel"], swapped[0]["body"]["channel"])
        check = entry.verify_scan_sequence(plan, "Q3", swapped, result.runner)
        self.assertFalse(check["matches"])
        self.assertEqual(check["emitted_log"]["first_mismatch"]["first_mismatch_index"], 0)

    def test_missing_and_extra_and_duplicated_actions_fail(self):
        _tag, result = self._run("Q3", False)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        measures = [r for r in requests if r["path"] == "/measure"]
        for label, doctored in (
            ("missing", measures[:-1]),
            ("extra", measures + [measures[0]]),
            ("duplicate substitution", measures[:-1] + [measures[0]]),
        ):
            check = entry.verify_scan_sequence(plan, "Q3", doctored, result.runner)
            self.assertFalse(check["matches"], label)

    def test_digest_is_deterministic_and_distinguishes_sequences(self):
        plan = variants.plan_for("SCAN49")
        expected = entry.expected_measure_sequence(plan, "Q4")
        self.assertEqual(entry.sequence_digest(expected), entry.sequence_digest(list(expected)))
        shifted = [(x + 1.0, y, c) for x, y, c in expected]
        self.assertNotEqual(entry.sequence_digest(expected), entry.sequence_digest(shifted))
        self.assertEqual(len(entry.sequence_digest(expected)), 64)

    def test_first_mismatch_diagnostic_is_bounded_and_names_the_index(self):
        plan = variants.plan_for("BASE")
        expected = entry.expected_measure_sequence(plan, "Q3")
        observed = list(expected)
        observed[7] = (observed[7][0] + 1.0, observed[7][1], observed[7][2])
        diagnostic = entry.first_sequence_mismatch(expected, observed, context=3)
        self.assertEqual(diagnostic["first_mismatch_index"], 7)
        self.assertEqual(diagnostic["expected_at_index"], expected[7])
        self.assertEqual(diagnostic["observed_at_index"], observed[7])
        self.assertLessEqual(len(diagnostic["window"]), 7)
        self.assertIsNone(entry.first_sequence_mismatch(expected, list(expected)))

    def test_clear_actions_are_a_legal_prefix_of_the_same_plan(self):
        for problem, fallback, expected_tag in self.PROBLEMS:
            _tag, result = self._run(problem, fallback)
            plan = variants.plan_for(expected_tag)
            requests = self._requests(result.runner.scan_results, result.runner.clear_results)
            check = entry.verify_clear_sequence(plan, result.runner, requests)
            self.assertTrue(check["matches"], (problem, fallback, check["mismatches"]))
            self.assertTrue(check["log_matches_runner_record"])
            # early success: the executed walk is a prefix, never all 225 attempts
            for channel, info in check["prefixes"].items():
                self.assertTrue(info["is_prefix"], channel)
                self.assertEqual(info["plan_length"], 225)
                self.assertLessEqual(info["executed"], 225)

    def test_wrong_clear_coordinate_fails(self):
        _tag, result = self._run("Q3", False)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        self.assertTrue([r for r in requests if r["path"] == "/clear"])
        doctored = [json.loads(json.dumps(r)) for r in requests]
        for record in doctored:
            if record["path"] == "/clear":
                record["body"]["position"]["x"] += 5.0
                break
        check = entry.verify_clear_sequence(plan, result.runner, doctored)
        self.assertFalse(check["matches"])

    def test_reordered_clear_actions_fail(self):
        # the scripted channel needs 3 attempts, so two clear actions exist to swap
        _tag, result = self._run("Q3", False, success_at_attempt=3)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        first_channel = next(r["body"]["channel"] for r in requests if r["path"] == "/clear")
        positions = [i for i, r in enumerate(requests) if r["path"] == "/clear"
                     and r["body"]["channel"] == first_channel]
        self.assertGreaterEqual(len(positions), 2, "need two clear actions on one channel")
        reordered = [json.loads(json.dumps(r)) for r in requests]
        a, b = positions[0], positions[1]
        reordered[a]["body"]["position"], reordered[b]["body"]["position"] = (
            reordered[b]["body"]["position"], reordered[a]["body"]["position"])
        check = entry.verify_clear_sequence(plan, result.runner, reordered)
        self.assertFalse(check["matches"])

    def test_clear_actions_from_another_lattice_fail(self):
        _tag, result = self._run("Q3", False)
        plan = variants.plan_for("BASE")
        requests = self._requests(result.runner.scan_results, result.runner.clear_results)
        other = variants.plan_for("CLEAR150").clear_plan((0.0, 0.0), 0.0, "direction")
        doctored = [r for r in requests if r["path"] == "/measure"]
        doctored += [{"path": "/clear",
                      "body": {"position": {"x": x, "y": y}, "channel": 2},
                      "raw_response": {"clear_result": "no_success"}} for x, y in other]
        check = entry.verify_clear_sequence(plan, result.runner, doctored)
        self.assertFalse(check["matches"])


class TestFailClosedPaths(unittest.TestCase):
    """WI-036 requirements 5-7: a mismatch or a refusal must be non-success, status 1."""

    ARGS = ["--mock", "--problem", "Q3", "--robot-id", "TESTTEAM"]

    @staticmethod
    def _render(argv):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            status = entry.main(argv)
        return status, buffer.getvalue()

    def test_post_scan_mismatch_stops_before_any_clear_and_exits_1(self):
        shifted = [(-1400.0 + 1.0, -1400.0, c) for c in range(1, 21)]
        with mock.patch.object(entry, "expected_measure_sequence", return_value=shifted):
            report = entry.run(entry._parse_args(self.ARGS))
        self.assertEqual(report["outcome"], "STOPPED_SCAN_SEQUENCE_MISMATCH")
        self.assertNotIn("clear_completed", report)
        self.assertFalse([r for r in report["requests"] if r["path"] == "/clear"],
                         "no clear action may be attempted after a scan mismatch")
        self.assertEqual(report["emitted"]["measure_requests"], 180)

    def test_main_reports_post_scan_mismatch_status_1_with_full_scan_and_no_clears(self):
        """TR-040 finding 1: assert the command-exit path directly through main().

        The sibling test above exercises ``run()``; this one drives the real CLI entry
        point with the same injected exact-scan mismatch and checks the ordinary
        (non-JSON) rendering, so the operator-visible status and the emitted action
        counts are asserted where they are actually produced.
        """
        shifted = [(-1400.0 + 1.0, -1400.0, c) for c in range(1, 21)]
        with mock.patch.object(entry, "expected_measure_sequence", return_value=shifted):
            status, text = self._render(self.ARGS)          # ordinary mode, no --json
        self.assertEqual(status, 1)
        self.assertIn("STOPPED_SCAN_SEQUENCE_MISMATCH", text)
        # the full 9 x 20 scan was emitted (180 measures) ...
        self.assertIn("measures=180", text)
        # ... and not one clear action was attempted
        self.assertIn("clear requests=0", text)
        self.assertNotIn("clear requests=1", text)

    def test_post_run_mismatch_cannot_retain_completed_and_exits_1(self):
        fake = {"matches": False, "mismatches": ["injected clear mismatch"], "proof": True,
                "scan": {"matches": True}, "clear": {"matches": False}}
        with mock.patch.object(entry, "verify_exact_action_evidence", return_value=fake):
            report = entry.run(entry._parse_args(self.ARGS))
        # the run itself produced a COMPLETE certificate ...
        self.assertIsNotNone(report["completion"])
        self.assertEqual(report["completion"]["status"], "COMPLETE")
        # ... but the entry withdraws it
        self.assertEqual(report["outcome"], "STOPPED_ACTION_SEQUENCE_MISMATCH")
        self.assertNotEqual(report["outcome"], "COMPLETED")
        with mock.patch.object(entry, "verify_exact_action_evidence", return_value=fake):
            status, text = self._render(self.ARGS)
        self.assertEqual(status, 1)
        self.assertIn("STOPPED_ACTION_SEQUENCE_MISMATCH", text)

    def test_pre_enter_invariant_mismatch_sends_no_enter_and_exits_1(self):
        broken = {"expected": {"scan_points": 49}, "observed": {"scan_points": 25},
                  "matches": False, "mismatches": ["scan_points: expected 49, observed 25"]}
        with mock.patch.object(entry, "check_named_invariants", return_value=broken):
            report = entry.run(entry._parse_args(self.ARGS))
        self.assertEqual(report["outcome"], "STOPPED_CONFIGURATION_INVARIANT")
        self.assertFalse(report["configuration"]["invariants"]["matches"])
        # no /enter, no session, no mock server -- and the report is still complete
        self.assertEqual(report["requests"], [])
        self.assertIsNone(report["enter"])
        self.assertIsNone(report["mock_state"])
        self.assertIn("session", report)
        with mock.patch.object(entry, "check_named_invariants", return_value=broken):
            status, text = self._render(self.ARGS)
        self.assertEqual(status, 1)
        self.assertIn("STOPPED_CONFIGURATION_INVARIANT", text)
        with mock.patch.object(entry, "check_named_invariants", return_value=broken):
            status_json, text_json = self._render(self.ARGS + ["--json"])
        self.assertEqual(status_json, 1)
        self.assertEqual(json.loads(text_json)["outcome"], "STOPPED_CONFIGURATION_INVARIANT")

    def test_healthy_mock_run_still_exits_0_with_the_exact_proof(self):
        status, text = self._render(self.ARGS)
        self.assertEqual(status, 0)
        self.assertIn("exact action proof      : True", text)
        self.assertIn("all legal prefixes", text)

    def test_json_output_carries_both_verifications_for_a_healthy_run(self):
        status, text = self._render(self.ARGS + ["--json"])
        self.assertEqual(status, 0)
        report = json.loads(text)
        exact = report["configuration"]["exact_action_verification"]
        self.assertTrue(exact["matches"])
        self.assertTrue(exact["proof"])
        self.assertFalse(report["configuration"]["emitted_verification"]["proof"])
        self.assertTrue(report["configuration"]["scan_sequence_verification"]["matches"])


if __name__ == "__main__":
    unittest.main()