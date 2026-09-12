"""Candidate tests for the virtual ledger and the T10 budget accept/reject.

Predicates come from ``modeling/COMPLETE_MODEL_PLAN.md`` sections 2 and 7.2-7.3
and from ``experiments/EXP-002/FIXTURE_CATALOG.md`` T10.  No evaluator module is
imported.
"""

import unittest

from candidate import ledger

EPS_D = 1e-6


class TestDeltaT(unittest.TestCase):
    def test_measure_on_the_same_channel_costs_five(self):
        self.assertEqual(ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_measure=True, c_k=1, b_prev=1), 5.0)

    def test_measure_with_a_channel_switch_costs_six(self):
        self.assertEqual(ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_measure=True, c_k=2, b_prev=1), 6.0)

    def test_clear_success_and_failure(self):
        self.assertEqual(ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_clear=True, s_k=1), 5.0)
        self.assertEqual(ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_clear=True, s_k=0), 3.0)

    def test_move_component_is_length_over_five(self):
        self.assertEqual(ledger.delta_t((0.0, 0.0), (50.0, 0.0)), 10.0)

    def test_enter_and_exit_add_no_virtual_time(self):
        lg = ledger.Ledger()
        lg.enter()
        lg.exit()
        self.assertEqual(lg.total, 0.0)
        self.assertEqual(lg.n_enter, 1)
        self.assertEqual(lg.n_exit, 1)


class TestLedgerTotals(unittest.TestCase):
    def test_closed_form_total_matches_an_independent_sum(self):
        lg = ledger.Ledger()
        lg.measure((0.0, 0.0), (0.0, 0.0), 1, 1)
        lg.measure((0.0, 0.0), (50.0, 0.0), 2, 1)
        lg.clear((50.0, 0.0), (100.0, 0.0), 2, 2, success=True)
        expected = (50.0 / 5.0 + 0.0)  # move in the second measure
        # measure 1: 5 ; measure 2: 50/5 + 5 + 1 = 16 ; clear: 50/5 + 3 + 2 = 15
        expected = 5.0 + 16.0 + 15.0
        self.assertAlmostEqual(lg.total, expected, places=12)
        self.assertEqual(lg.n_measure, 2)
        self.assertEqual(lg.n_switch, 1)
        self.assertEqual(lg.n_clear, 1)
        self.assertEqual(lg.k_success, 1)
        self.assertAlmostEqual(lg.move_length, 100.0, places=12)

    def test_success_is_counted_once_per_channel(self):
        lg = ledger.Ledger()
        lg.clear((0.0, 0.0), (0.0, 0.0), 1, 1, success=True)
        lg.clear((0.0, 0.0), (0.0, 0.0), 1, 1, success=True)
        self.assertEqual(lg.k_success, 1)
        self.assertEqual(lg.n_clear, 2)

    def test_rejected_action_is_not_counted_as_an_action(self):
        lg = ledger.Ledger()
        lg.measure((0.0, 0.0), (10.0, 0.0), 1, 1, accepted=False)
        self.assertEqual(lg.n_measure, 0)
        self.assertEqual(lg.n_reject, 1)
        self.assertEqual(lg.total, 0.0)

    def test_retry_is_not_a_new_action(self):
        lg = ledger.Ledger()
        lg.retry("req-1")
        self.assertEqual(lg.n_retry, 1)
        self.assertEqual(lg.total, 0.0)

    def test_recompute_from_records_agrees(self):
        lg = ledger.Ledger()
        lg.measure((0.0, 0.0), (0.0, 0.0), 1, 1)
        lg.clear((0.0, 0.0), (20.0, 0.0), 1, 1, success=True)
        self.assertEqual(lg.total, lg.recompute_from_records())


class TestT10BudgetAcceptReject(unittest.TestCase):
    def test_one_measure_remainder_five_is_enough(self):
        cost = ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_measure=True, c_k=1, b_prev=1)
        self.assertEqual(cost, 5.0)
        self.assertTrue(ledger.budget_accepts(5.0, cost))

    def test_remainder_slightly_short_is_rejected(self):
        cost = ledger.delta_t((0.0, 0.0), (0.0, 0.0), is_measure=True, c_k=1, b_prev=1)
        self.assertFalse(ledger.budget_accepts(5.0 - EPS_D, cost))

    def test_accept_reject_uses_all_feedback_not_the_favourable_realisation(self):
        # worst-case feedback would need 12 while the favourable one needs 5
        costs = [5.0, 12.0]
        self.assertEqual(ledger.worst_case_feedback(costs), 12.0)
        self.assertFalse(ledger.all_feedback_accepts(10.0, costs))
        self.assertTrue(ledger.all_feedback_accepts(12.0, costs))

    def test_worst_case_of_an_empty_feedback_set_is_zero(self):
        self.assertEqual(ledger.worst_case_feedback([]), 0.0)

    def test_adaptive_action_safety_inequality(self):
        self.assertTrue(ledger.adaptive_action_safe(100.0, 5.0, 50.0, 155.0))
        self.assertFalse(ledger.adaptive_action_safe(100.0, 5.0, 51.0, 155.0))


class TestRemainingBoundAndRealtimeGate(unittest.TestCase):
    def test_v_back_uses_initial_source_count(self):
        # K counts cleared channels; the (16 - K) term uses the initial upper bound
        self.assertEqual(ledger.v_back(0.0, 0, 0), 3700.0 * 16)

    def test_realtime_gate_is_unknown_without_duration_evidence(self):
        status, reasons = ledger.realtime_check(1200.0, 100)
        self.assertEqual(status, ledger.REALTIME_UNCERTIFIED)
        self.assertTrue(reasons)

    def test_realtime_gate_rejects_when_the_window_is_too_small(self):
        status, _reasons = ledger.realtime_check(
            1.0, 10, l_max=1.0, c_back_max=1.0, c_dec_max=1.0
        )
        self.assertEqual(status, ledger.REALTIME_UNCERTIFIED)

    def test_realtime_gate_passes_only_with_all_bounds(self):
        status, reasons = ledger.realtime_check(
            1000.0, 10, l_max=0.1, c_back_max=1.0, c_dec_max=1.0
        )
        self.assertEqual(status, "OK")
        self.assertEqual(reasons, [])


if __name__ == "__main__":
    unittest.main()
