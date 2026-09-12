"""Candidate tests for the fallback queue, ``L = 2`` gate and certificate protection (T08/T09).

Predicates come from ``modeling/COMPLETE_MODEL_PLAN.md`` sections 7.1-7.3.
No evaluator module is imported.
"""

import unittest

from candidate import queue


class TestT08OneClearListPerSource(unittest.TestCase):
    def test_duplicate_discovery_creates_only_one_list(self):
        fm = queue.FallbackManager([])
        fm.register_discovery(1, (0.0, 0.0), 0.0, "direction")
        fm.register_discovery(1, (0.0, 0.0), 0.0, "direction")
        self.assertEqual(len(fm.clear_lists), 1)
        self.assertEqual(len(fm.clear_lists[1].tasks), 225)
        self.assertTrue(any(entry[0] == "discovery_ignored_duplicate" for entry in fm.trace))

    def test_near_discovery_creates_a_single_task(self):
        fm = queue.FallbackManager([])
        cl = fm.register_discovery(3, (10.0, 5.0), 0.0, "near")
        self.assertEqual(len(cl.tasks), 1)
        self.assertEqual(cl.tasks[0].point, (10.0, 5.0))

    def test_global_detection_is_advanced_before_local_clear(self):
        fm = queue.FallbackManager([((0.0, 0.0), 1), ((0.0, 0.0), 2)])
        fm.register_discovery(1, (0.0, 0.0), 0.0, "near")
        self.assertEqual(fm.next_task().kind, "measure")
        self.assertEqual(fm.next_task().kind, "measure")
        self.assertEqual(fm.next_task().kind, "clear")

    def test_success_permanently_discharges_the_channel(self):
        fm = queue.FallbackManager([((0.0, 0.0), 1), ((0.0, 0.0), 2)])
        fm.register_discovery(1, (0.0, 0.0), 0.0, "near")
        self.assertTrue(fm.on_clear_success(1))
        self.assertFalse(fm.on_clear_success(1))
        # the remaining global detection task for channel 2 still runs ...
        task = fm.next_task()
        self.assertEqual(task.kind, "measure")
        self.assertEqual(task.channel, 2)
        # ... and no clear task for the cleared channel 1 is ever issued again
        self.assertIsNone(fm.next_task())

    def test_clear_list_exhaustion_is_recorded_as_a_discharge(self):
        fm = queue.FallbackManager([])
        fm.register_discovery(1, (0.0, 0.0), 0.0, "near")
        task = fm.next_task()
        fm.execute(task)
        self.assertIsNone(fm.next_task())
        self.assertTrue(any(entry[0] == "discharged" for entry in fm.trace))

    def test_cancellation_always_carries_a_reason(self):
        fm = queue.FallbackManager([((0.0, 0.0), 1), ((0.0, 0.0), 2), ((0.0, 0.0), 1)])
        removed = fm.cancel_measure_tasks(1, "registered_clear_queue")
        self.assertEqual(len(removed), 2)
        self.assertTrue(any(entry[0] == "cancel" and entry[2] == "registered_clear_queue" for entry in fm.trace))

    def test_creation_and_action_bounds(self):
        fm = queue.FallbackManager([])
        self.assertEqual(fm.total_created_bound(180), 180 + 16 * 225)
        self.assertEqual(fm.action_bound(180), 3 * (180 + 3600) + 2)


class TestT08L2NotResetByOrdinaryProgress(unittest.TestCase):
    def test_ordinary_progress_does_not_reset(self):
        gate = queue.AdaptiveGate()
        gate.on_adaptive_action()
        self.assertEqual(gate.count, 1)
        gate.on_ordinary_feedback()
        gate.on_channel_switch()
        gate.on_region_shrunk()
        self.assertEqual(gate.count, 1)

    def test_two_adaptive_actions_force_a_fallback(self):
        gate = queue.AdaptiveGate()
        gate.on_adaptive_action()
        self.assertFalse(gate.must_fallback)
        gate.on_adaptive_action()
        self.assertTrue(gate.must_fallback)

    def test_fallback_task_execution_resets(self):
        gate = queue.AdaptiveGate()
        gate.on_adaptive_action()
        gate.on_adaptive_action()
        self.assertTrue(gate.must_fallback)
        gate.on_fallback_task_executed()
        self.assertEqual(gate.count, 0)

    def test_head_task_discharge_resets(self):
        gate = queue.AdaptiveGate()
        gate.on_adaptive_action()
        gate.on_head_task_discharged()
        self.assertEqual(gate.count, 0)


class TestT09NonMonotoneCrudeBound(unittest.TestCase):
    def test_old_certificate_is_charged_and_kept(self):
        cm = queue.CertificateManager()
        cm.install(100.0)
        cm.charge(30.0)
        self.assertEqual(cm.remaining, 70.0)
        accepted, reason = cm.offer_crude_remaining(120.0)
        self.assertFalse(accepted)
        self.assertEqual(reason, "kept_held_certificate")
        self.assertEqual(cm.bound, 100.0)
        self.assertEqual(cm.remaining, 70.0)
        self.assertEqual(cm.rejected_crudes, [(120.0, 70.0, 0)])

    def test_a_tighter_crude_bound_is_accepted(self):
        cm = queue.CertificateManager()
        cm.install(100.0)
        cm.charge(30.0)
        accepted, reason = cm.offer_crude_remaining(40.0)
        self.assertTrue(accepted)
        self.assertEqual(reason, "tightened")
        self.assertEqual(cm.remaining, 40.0)

    def test_certificate_coverage(self):
        cm = queue.CertificateManager()
        cm.install(50.0)
        self.assertTrue(cm.covers(50.0))
        cm.charge(1.0)
        self.assertFalse(cm.covers(50.0))


class TestRemainingCostBounds(unittest.TestCase):
    def test_v_back_formula(self):
        self.assertEqual(queue.v_back(1000.0, 10, 0), 200.0 + 60.0 + 3700.0 * 16)
        self.assertEqual(queue.v_back(0.0, 0, 16), 0.0)

    def test_per_source_bound_is_below_3700(self):
        bound = queue.v_source_bound()
        self.assertAlmostEqual(bound, 3662.6, places=6)
        self.assertLess(bound, 3700.0)


if __name__ == "__main__":
    unittest.main()
