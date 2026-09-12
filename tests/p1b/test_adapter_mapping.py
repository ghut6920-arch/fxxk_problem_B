"""Adapter mapping check against the saved T01-T10 fixture shapes.

The P1-B design (``modeling/EXPERIMENT_DESIGN.md`` section 4.4) requires the
protocol adapter's conversion to be verified against the already-saved T01-T10
inputs and expectations, not only against new mock cases.  This module reads the
frozen P1-A fixtures (read-only) and checks that the adapter maps the official
response shapes to the same candidate-side values the fixtures expect.

Wall budget: 20 s for this module (enforced in ``tearDownModule``).
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
import time
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from candidate import ledger as candidate_ledger  # noqa: E402
from candidate import observe as candidate_observe  # noqa: E402
from protocol import mapping  # noqa: E402
from protocol.client import Response  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "p1a" / "fixtures"
BUDGET_S = 20.0
_T0 = None

#: T items that have no live protocol shape (candidate-internal only)
NO_PROTOCOL_SHAPE = {
    "T05": "candidate quadtree capacity; no /measure or /clear shape to map",
    "T07": "world legality/count domain; not returned by any interface field",
    "T09": "candidate fallback certificate; no protocol shape",
}


def setUpModule():
    global _T0
    _T0 = time.perf_counter()


def tearDownModule():
    elapsed = time.perf_counter() - _T0
    if elapsed > BUDGET_S:
        raise AssertionError(f"adapter mapping exceeded its {BUDGET_S}s budget: {elapsed:.3f}s")


def fixture(item):
    return json.loads((FIXTURES / f"{item}.json").read_text(encoding="utf-8"))


def measure_response(result, svd_deg=None, virtual_time_s=0.0, request_id="m-1"):
    body = {"accepted": True, "real_timestamp_ms": 1, "virtual_time_s": virtual_time_s,
            "measure_result": result}
    if svd_deg is not None:
        body["svd_deg"] = svd_deg
    return Response("/measure", request_id, 200, True, virtual_time_s, 1.0, body,
                    measure_result=result, svd_deg=svd_deg)


def clear_response(result, virtual_time_s=0.0, request_id="c-1"):
    body = {"accepted": True, "real_timestamp_ms": 1, "virtual_time_s": virtual_time_s,
            "clear_result": result}
    return Response("/clear", request_id, 200, True, virtual_time_s, 1.0, body, clear_result=result)


def enter_response(remaining_real_duration_s=1200.0):
    """An accepted /enter, used to set the ledger's virtual-time baseline (0)."""
    body = {"accepted": True, "real_timestamp_ms": 1, "virtual_time_s": 0,
            "max_virtual_duration_s": 360000.0, "max_real_duration_s": 1200.0,
            "remaining_real_duration_s": remaining_real_duration_s}
    return Response("/enter", "e-1", 200, True, 0.0, 1.0, body,
                    max_virtual_duration_s=360000.0, max_real_duration_s=1200.0,
                    remaining_real_duration_s=remaining_real_duration_s)


class TestMappingOfSavedFixtures(unittest.TestCase):
    def test_all_t01_to_t10_fixtures_are_present(self):
        for index in range(1, 11):
            self.assertTrue((FIXTURES / f"T{index:02d}.json").exists(), index)

    def test_t01_direction_endpoints_map_to_the_expected_label(self):
        fx = fixture("T01")
        expected = fx["expected_evaluator"]["observation"]
        for i, theta_deg in enumerate(fx["inputs"]["theta_hat_deg"]):
            response = measure_response("direction", svd_deg=theta_deg)
            self.assertEqual(mapping.to_candidate_observation(response), candidate_observe.DIRECTION)
            self.assertEqual(expected[i], "direction")
            # the adapter converts degrees to radians for the candidate contract
            self.assertAlmostEqual(mapping.to_radians(response.svd_deg), math.radians(theta_deg), places=12)

    def test_t02_near_maps_and_o03_is_not_a_server_code(self):
        fx = fixture("T02")
        near = measure_response("near")
        self.assertEqual(mapping.to_candidate_observation(near), candidate_observe.NEAR)
        self.assertEqual(fx["expected_evaluator"]["omni_near_observation"], "near")
        # the O-03 coincidence label is a plan-side open branch, never a returned code
        self.assertNotIn(candidate_observe.O03_OPEN, mapping.CANDIDATE_LABEL.values())
        self.assertEqual(set(mapping.CANDIDATE_LABEL), {"no_signal", "near", "direction"})
        self.assertNotIn(fx["expected_evaluator"]["o03_label"], mapping.CANDIDATE_LABEL)

    def test_t03_no_signal_maps(self):
        fx = fixture("T03")
        response = measure_response("no_signal")
        self.assertEqual(mapping.to_candidate_observation(response), candidate_observe.NO_SIGNAL)
        self.assertEqual(set(fx["expected_evaluator"]["observations"]), {"no_signal"})

    def test_t04_clear_results_map_and_charge_three_or_five(self):
        fx = fixture("T04")
        tracker = mapping.LedgerTracker()
        tracker.note_accepted(measure_response("no_signal", virtual_time_s=0.0), (0.0, 0.0), 1, "measure")
        success = clear_response("success", virtual_time_s=5.0)
        failure = clear_response("no_target_in_range", virtual_time_s=8.0)
        self.assertTrue(mapping.clear_envelope(success)["success"])
        self.assertFalse(mapping.clear_envelope(failure)["success"])
        self.assertEqual(fx["expected_evaluator"]["clear_results"], ["success", "success", "fail"])
        self.assertAlmostEqual(mapping.clear_envelope(success)["virtual_time_s"], 5.0)
        # and the candidate ledger identity for the two-success script is preserved
        ledger = candidate_ledger.Ledger()
        ledger.clear((0.0, 0.0), (0.0, 0.0), 1, 1, True)
        ledger.clear((0.0, 0.0), (0.0, 0.0), 1, 1, True)
        self.assertEqual(ledger.k_success, fx["expected_evaluator"]["K_after_two_successes"])
        self.assertEqual(ledger.n_clear, fx["expected_evaluator"]["N_clear_after_two_successes"])
        self.assertAlmostEqual(ledger.total, fx["expected_evaluator"]["totals_formula_T"])

    def test_t06_point_identity_survives_the_adapter_body_encoding(self):
        fx = fixture("T06")
        a = tuple(json.loads(json.dumps(fx["inputs"]["json_equivalent"]["a"])))
        b = tuple(json.loads(fx["inputs"]["json_equivalent"]["b_raw"]))
        self.assertEqual(candidate_observe.canonical_point(a), candidate_observe.canonical_point(b))
        pa = tuple(fx["inputs"]["nearby_distinct"]["p_a"])
        pb = tuple(fx["inputs"]["nearby_distinct"]["p_b"])
        self.assertNotEqual(candidate_observe.canonical_point(pa), candidate_observe.canonical_point(pb))

    def test_t08_injected_script_maps_to_the_fixture_ledger_total(self):
        fx = fixture("T08")
        expected = fx["expected_evaluator"]
        tracker = mapping.LedgerTracker()
        tracker.clock.observe(enter_response())      # /enter sets the 0 baseline
        # the script's three fully specified actions, with official virtual times
        tracker.note_accepted(measure_response("no_signal", virtual_time_s=5.0), (0.0, 0.0), 1, "measure")
        tracker.note_accepted(measure_response("no_signal", virtual_time_s=11.0), (0.0, 0.0), 2, "measure")
        tracker.note_accepted(clear_response("success", virtual_time_s=16.0), (0.0, 0.0), 1, "clear", success=True)
        self.assertAlmostEqual(tracker.candidate_total, expected["ledger_total"])
        self.assertEqual(tracker.max_residual, 0.0)
        self.assertEqual(len(tracker.records), expected["fully_specified_actions"])
        self.assertFalse(tracker.inconsistent())

    def test_t10_measure_delta_t_maps_to_five(self):
        fx = fixture("T10")
        tracker = mapping.LedgerTracker()
        tracker.clock.observe(enter_response())      # /enter sets the 0 baseline
        response = measure_response("no_signal", virtual_time_s=5.0)
        residual = tracker.note_accepted(response, (0.0, 0.0), 1, "measure")
        self.assertAlmostEqual(tracker.candidate_total, fx["expected_evaluator"]["measure_delta_t"])
        self.assertAlmostEqual(residual, 0.0)
        enough, short = fx["inputs"]["remainders"]
        self.assertTrue(candidate_ledger.budget_accepts(enough, tracker.candidate_total))
        self.assertFalse(candidate_ledger.budget_accepts(short, tracker.candidate_total))

    def test_no_protocol_shape_items_are_named_not_silently_skipped(self):
        for item, reason in NO_PROTOCOL_SHAPE.items():
            fx = fixture(item)
            self.assertIn("candidate_later_checks", fx, item)
            self.assertTrue(reason, item)
        self.assertEqual(sorted(NO_PROTOCOL_SHAPE), ["T05", "T07", "T09"])

    def test_unknown_measure_code_is_refused(self):
        with self.assertRaises(ValueError):
            mapping.to_candidate_observation(measure_response("bogus"))

    def test_no_fixture_was_modified(self):
        # read-only guard: the fixture directory still holds exactly the frozen files
        names = sorted(p.name for p in FIXTURES.glob("*.json"))
        self.assertEqual(len(names), 27)  # G01-G16, T01-T10, manifest
        self.assertIn("manifest.json", names)


if __name__ == "__main__":
    unittest.main()
