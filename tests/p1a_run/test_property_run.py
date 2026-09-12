"""Unittest wrapper for the EXP-002 C0 P1-A property run (WI-016).

``PYTHONPATH=src python -m unittest discover -s tests/p1a_run -v``

The full 26-item suite is executed once per session (cached in ``setUpClass``).
The last test is a **harness negative control**: a doctored fixture must make an
item FAIL, proving the per-item assertions are live rather than vacuous.  This is
a control on this harness, not candidate mutation testing -- SR-002 /
``modeling/EXPERIMENT_DESIGN.md`` section 4.5 reserve mutation checks for a
separately authorized WI, and none was performed here.
"""

from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tests.p1a_run import checks as checks_mod  # noqa: E402
from tests.p1a_run import runner  # noqa: E402

_CACHE = {}


def _results():
    if "results" not in _CACHE:
        _CACHE["results"] = runner.run_suite()
    return _CACHE["results"]


class TestFixtureCoverage(unittest.TestCase):
    def test_all_twenty_six_items_are_registered_and_reached(self):
        self.assertEqual(checks_mod.ITEM_ORDER,
                         ["G%02d" % i for i in range(1, 17)] + ["T%02d" % i for i in range(1, 11)])
        self.assertEqual(len(checks_mod.ITEM_ORDER), 26)
        self.assertEqual(sorted(checks_mod.CHECKS), sorted(checks_mod.ITEM_ORDER))

    def test_every_frozen_fixture_loads_and_carries_its_id(self):
        fixtures = runner.load_fixtures()
        self.assertEqual(len(fixtures), 26)
        for item, fx in fixtures.items():
            self.assertEqual(fx["id"], item)
            self.assertIn("candidate_later_checks", fx)
            self.assertTrue(fx["candidate_later_checks"], item)

    def test_budget_declarations_match_the_spec(self):
        self.assertEqual(runner.PER_ITEM_CAP, 10.0)
        self.assertEqual(runner.STAGE_CAP, 260.0)


class TestPropertyRun(unittest.TestCase):
    def test_every_item_was_attempted_with_at_least_one_check(self):
        results = _results()
        self.assertEqual([r.id for r in results], checks_mod.ITEM_ORDER)
        for r in results:
            self.assertGreaterEqual(len(r.checks), 1, r.id)
            self.assertFalse(r.error, f"{r.id}: {r.error}")

    def test_no_item_was_skipped(self):
        results = _results()
        skipped = [r.id for r in results if not r.checks]
        self.assertEqual(skipped, [])

    def test_every_item_passed(self):
        results = _results()
        failed = {r.id: r.failed for r in results if r.result != runner.PASS}
        self.assertEqual(failed, {})

    def test_conclusion_is_the_closed_set_value(self):
        conclusion = runner.conclude(_results())
        self.assertIn(conclusion, (runner.CONCLUSION_PASS, runner.CONCLUSION_FAIL, runner.CONCLUSION_UNRESOLVED))
        self.assertEqual(conclusion, runner.CONCLUSION_PASS)

    def test_caps_are_respected(self):
        results = _results()
        metrics = runner.summary_metrics(results)
        self.assertLessEqual(metrics["wall_clock_max_item_s"], runner.PER_ITEM_CAP)
        self.assertLessEqual(metrics["wall_clock_total_s"], runner.STAGE_CAP)

    def test_safety_metrics_are_zero(self):
        metrics = runner.summary_metrics(_results())
        self.assertEqual(metrics["truth_exclusions"], 0)
        self.assertEqual(metrics["false_completions"], 0)
        self.assertEqual(metrics["unsafe_cancels"], 0)
        self.assertEqual(metrics["ledger_residual_max"], 0.0)

    def test_run_reproduces_on_one_repeat_execution(self):
        """An identical repeat run is for reproduction only and adds no new sample."""
        first = runner.summary_metrics(_results())
        repeated = runner.run_suite()
        second = runner.summary_metrics(repeated)
        self.assertEqual(first["items_pass"], second["items_pass"])
        self.assertEqual(first["checks_failed"], second["checks_failed"])
        self.assertEqual(runner.conclude(repeated), runner.CONCLUSION_PASS)


class TestHarnessNegativeControl(unittest.TestCase):
    """A doctored expectation must fail: the checks are live, not vacuous."""

    def test_doctored_g01_expectation_fails_the_item(self):
        fixtures = runner.load_fixtures()
        doctored = copy.deepcopy(fixtures["G01"])
        doctored["expected_evaluator"]["halfplane_state"] = "UNBOUNDED"
        res = runner.run_item("G01", doctored)
        self.assertEqual(res.result, runner.FAIL)
        self.assertTrue(any("frozen evaluator label" in name for name in res.failed), res.failed)

    def test_doctored_g16_count_fails_the_item(self):
        fixtures = runner.load_fixtures()
        doctored = copy.deepcopy(fixtures["G16"])
        doctored["expected_evaluator"]["centre_count"] = 224
        res = runner.run_item("G16", doctored)
        self.assertEqual(res.result, runner.FAIL)

    def test_a_doctored_run_cannot_conclude_pass(self):
        fixtures = runner.load_fixtures()
        doctored = copy.deepcopy(fixtures["G01"])
        doctored["expected_evaluator"]["halfplane_state"] = "UNBOUNDED"
        res = runner.run_item("G01", doctored)
        self.assertEqual(runner.conclude([res]), runner.CONCLUSION_FAIL)


class TestReportInputs(unittest.TestCase):
    def test_json_export_round_trips(self):
        payload = json.loads(runner.as_json(_results()))
        self.assertEqual(payload["conclusion"], runner.CONCLUSION_PASS)
        self.assertEqual(len(payload["items"]), 26)
        self.assertEqual(payload["metrics"]["items_pass"], 26)


if __name__ == "__main__":
    unittest.main()
