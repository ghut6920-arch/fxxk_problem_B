"""WI-023 flow tests: N=16 action counts, ledger and fail-closed per tag.

Each tag is driven through the frozen C0 runner on a scripted world whose
discovered channels are all cleared on the **last** legal attempt, so the emitted
action count hits that tag's request bound exactly.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from candidate import observe as candidate_observe  # noqa: E402
from candidate import scan  # noqa: E402
from candidate import variants  # noqa: E402

from tests.c0_baseline import flow, scenario  # noqa: E402

#: 16 discovered channels, each cleared only on its last attempt -> worst path
WORST_CHANNELS = tuple(range(1, 17))


def worst_specs(tag):
    count = variants.plan_for(tag).clear_count
    return [scenario.ChannelScript(c, candidate_observe.DIRECTION, 0.01 * c,
                                   success_at_attempt=count)
            for c in WORST_CHANNELS]


class TestN16ActionCountsPerTag(unittest.TestCase):
    def _run(self, question, tag):
        return flow.run_flow(question, worst_specs(tag), tag=tag)

    def test_q3_base_and_clear150(self):
        base = self._run("Q3", "BASE")
        self.assertTrue(base.completed, base.certificate)
        self.assertEqual(base.certificate["success_count"], 16)
        self.assertEqual(base.actions_at_stop, 3780)

        clear150 = self._run("Q3", "CLEAR150")
        self.assertTrue(clear150.completed, clear150.certificate)
        self.assertEqual(clear150.actions_at_stop, 2580)

    def test_q4_all_four_arms(self):
        expected = {"BASE": 5220, "CLEAR150": 4020, "SCAN49": 4580, "COMBINED": 3380}
        for tag in variants.TAGS:
            result = self._run("Q4", tag)
            self.assertTrue(result.completed, (tag, result.certificate))
            self.assertEqual(result.certificate["success_count"], 16, tag)
            self.assertEqual(result.actions_at_stop, expected[tag], tag)
            self.assertEqual(result.actions_at_stop,
                             variants.plan_for(tag).total_request_bound("Q4"), tag)

    def test_every_tag_matches_its_own_request_bound(self):
        for tag in variants.TAGS:
            for question in ("Q3", "Q4"):
                if question == "Q3" and tag in ("SCAN49", "COMBINED"):
                    continue      # P_4' is a Q4 construction; Q3 compares BASE/CLEAR150
                result = self._run(question, tag)
                self.assertEqual(result.actions_at_stop,
                                 variants.plan_for(tag).total_request_bound(question),
                                 (question, tag))

    def test_clear150_channel_attempts_are_150_each(self):
        result = self._run("Q3", "CLEAR150")
        self.assertEqual(len(result.cost.attempts_per_channel), 16)
        self.assertEqual(set(result.cost.attempts_per_channel.values()), {150})

    def test_scan49_measure_count_is_980_and_switches_979(self):
        result = self._run("Q4", "SCAN49")
        self.assertEqual(result.cost.n_measure, 980)
        self.assertEqual(result.cost.n_switch, 979)
        self.assertEqual(result.cost.n_clear, 16 * 225)

    def test_combined_uses_49_point_scan_and_150_clears(self):
        result = self._run("Q4", "COMBINED")
        self.assertEqual(result.cost.n_measure, 980)
        self.assertEqual(result.cost.n_clear, 16 * 150)
        self.assertEqual(result.actions_at_stop, 980 + 2400)

    def test_clear150_intra_steps_are_20_or_30_metres(self):
        result = self._run("Q4", "CLEAR150")
        self.assertAlmostEqual(result.cost.max_intra_clear_step_m, 30.0, places=6)

    def test_base_intra_steps_stay_at_20_metres(self):
        result = self._run("Q4", "BASE")
        self.assertAlmostEqual(result.cost.max_intra_clear_step_m, 20.0, places=6)

    def test_no_tag_exceeds_its_envelope(self):
        for tag in variants.TAGS:
            result = self._run("Q4", tag)
            envelope = variants.plan_for(tag).budget("Q4")
            self.assertLess(result.ledger_recomputed, envelope, tag)


class TestLedgerAndFailClosedPerTag(unittest.TestCase):
    def test_unique_accepted_actions_and_ledger_agreement(self):
        for tag in variants.TAGS:
            result = flow.run_flow("Q4", worst_specs(tag), tag=tag)
            indices = [a.index for a in result.env.actions]
            self.assertEqual(indices, sorted(indices), tag)
            self.assertEqual(len(indices), len(set(indices)), tag)
            self.assertAlmostEqual(result.ledger_recomputed, result.cost.total_seconds, places=9)

    def test_unknown_accept_is_fail_closed_for_every_tag(self):
        for tag in variants.TAGS:
            result = flow.run_flow("Q4", worst_specs(tag), tag=tag, inject_unknown_accept_at=500)
            self.assertTrue(result.unknown_accept, tag)
            self.assertEqual(result.certificate, {}, tag)
            self.assertFalse(result.completed, tag)
            self.assertFalse(result.false_completion, tag)
            self.assertEqual(result.actions_at_stop, 499, tag)

    def test_deadline_stop_is_fail_closed_for_every_tag(self):
        for tag in variants.TAGS:
            result = flow.run_flow("Q4", worst_specs(tag), tag=tag, inject_deadline_at=600)
            self.assertTrue(result.deadline_stop, tag)
            self.assertEqual(result.certificate, {}, tag)
            self.assertEqual(result.actions_at_stop, 599, tag)

    def test_adaptive_actions_stay_zero_for_every_tag(self):
        for tag in variants.TAGS:
            result = flow.run_flow("Q4", worst_specs(tag), tag=tag)
            self.assertEqual(result.runner.gate.count, 0, tag)


class TestQ3Q4Matrix(unittest.TestCase):
    def test_q3_arm_set_is_base_and_clear150_only(self):
        self.assertEqual(variants.tags_for("Q3"), ("BASE", "CLEAR150"))

    def test_scan49_does_not_change_the_q3_lattice(self):
        self.assertEqual(variants.plan_for("SCAN49").scan_points("Q3"), scan.P3())

    def test_clear150_keeps_the_20_channel_policy(self):
        for tag in variants.TAGS:
            self.assertEqual(variants.plan_for(tag).measure_count("Q3") % 20, 0, tag)
            self.assertEqual(variants.plan_for(tag).measure_count("Q4") % 20, 0, tag)


if __name__ == "__main__":
    unittest.main()
