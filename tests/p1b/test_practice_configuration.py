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

import pathlib
import sys
import unittest

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

    def test_verification_detects_a_mislabelled_or_wrong_lattice(self):
        """Negative controls: the verifier must not simply repeat the label."""
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


if __name__ == "__main__":
    unittest.main()
