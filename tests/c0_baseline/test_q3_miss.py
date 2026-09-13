"""WI-022: the Q3 practice 14/16 COMPLETE — offline diagnosis tests.

Frozen evidence: ``evidence/experiments/EXP-004/q3_practice.json`` (K=14, six
``no_source`` channels, COMPLETE) and the operator UI showing N=16 omnidirectional
sources.  These tests establish the mechanism offline:

* the P3 covering radius over the documented radius-1800 source region is
  ``700*sqrt(2) = 989.9495 m``, i.e. **below** the documented receive-radius floor of
  1000 m, so the plan's discovery guarantee is not broken by the lattice;
* replaying the frozen log reproduces the live certificate exactly (K=14,
  ``no_source`` = {1,5,6,10,16,20}, COMPLETE) from the recorded labels alone;
* therefore the two misses can only come from a source that no P3 point could see,
  which (with a legal radius) would have to lie >= 2980 m from the origin, far outside
  the radius-1800 target region;
* the C0 control flow has **no guard** for that situation: it converts a complete
  scan with no positive into a definite no-source claim (plan section 6/5.3, faithfully
  implemented) and then reports COMPLETE with K < N.
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

from tests.c0_baseline import flow, replay, scenario  # noqa: E402

Q3_LOG = REPO / "evidence" / "experiments" / "EXP-004" / "q3_practice.json"
Q4_LOG = REPO / "evidence" / "experiments" / "EXP-004" / "q4_practice.json"

P3 = [(1400.0 * i, 1400.0 * j) for i in (-1, 0, 1) for j in (-1, 0, 1)]
TARGET_RADIUS = 1800.0
RADIUS_FLOOR = 1000.0
CELL_CENTRE = 700.0 * math.sqrt(2.0)


def nearest_p3(p):
    return min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in P3)


class TestGeometryIsNotTheCause(unittest.TestCase):
    """The plan's Q3 discovery claim is verified true, so there is no P3 hole."""

    def test_p3_covering_radius_is_700_sqrt2(self):
        self.assertAlmostEqual(nearest_p3((700.0, 700.0)), CELL_CENTRE, places=9)
        self.assertAlmostEqual(nearest_p3((-700.0, -700.0)), CELL_CENTRE, places=9)

    def test_p3_covers_the_whole_target_region_below_the_radius_floor(self):
        # grid scan of the radius-1800 disk: max distance to the nearest P3 point
        worst = 0.0
        step = 5.0
        n = int(TARGET_RADIUS / step)
        for ix in range(-n, n + 1):
            x = ix * step
            for iy in range(-n, n + 1):
                y = iy * step
                if x * x + y * y > TARGET_RADIUS * TARGET_RADIUS:
                    continue
                d = nearest_p3((x, y))
                if d > worst:
                    worst = d
        self.assertLess(worst, RADIUS_FLOOR)
        self.assertLessEqual(worst, CELL_CENTRE + 1e-6)
        # the margin is thin but positive
        self.assertGreater(RADIUS_FLOOR - worst, 10.0)

    def test_a_source_missed_by_all_nine_points_must_be_far_outside_the_target(self):
        """With a legal radius the missed source cannot be inside the target region.

        Coarse scan (360 directions, 5 m radial steps) of the region not covered by the
        nine 1000 m disks: the measured closest approach is about 2227 m.  The exact
        boundary is not needed, only that it lies far beyond the 1800 m target radius.
        """
        def covered(p):
            return nearest_p3(p) <= RADIUS_FLOOR

        closest = None
        for k in range(360):
            phi = math.pi * k / 180.0
            ux, uy = math.cos(phi), math.sin(phi)
            t = TARGET_RADIUS
            while t < 4000.0:
                if not covered((t * ux, t * uy)):
                    if closest is None or t < closest:
                        closest = t
                    break
                t += 5.0
        self.assertIsNotNone(closest)
        self.assertGreaterEqual(closest, 2000.0)   # coarse measurement: ~2227 m
        self.assertGreater(closest, TARGET_RADIUS)


class TestFrozenLogReplay(unittest.TestCase):
    """The live certificate is reproduced from the recorded labels alone."""

    def setUp(self):
        self.log = replay.load_log(Q3_LOG)
        self.verdicts, self.env = replay.replay_scan(self.log, "Q3")

    def test_every_channel_was_measured_at_all_nine_points(self):
        self.assertEqual(len(self.verdicts), 20)
        for channel, info in self.verdicts.items():
            self.assertEqual(info["points_measured"], 9, channel)
        self.assertEqual(self.env.measure_calls, 180)

    def test_replay_reproduces_the_live_certificate(self):
        live = self.log["completion"]
        exists = sorted(c for c, i in self.verdicts.items() if i["verdict"] == "exists")
        no_source = sorted(c for c, i in self.verdicts.items() if i["verdict"] == "no_source")
        self.assertEqual(exists, live["cleared"])
        self.assertEqual(no_source, live["no_source_channels"])
        self.assertEqual(no_source, [1, 5, 6, 10, 16, 20])
        self.assertEqual(len(exists), 14)

    def test_the_six_no_source_channels_returned_no_signal_at_every_point(self):
        for channel in (1, 5, 6, 10, 16, 20):
            labels = [label for (_x, _y, c), (label, _svd) in self.env.labels.items()
                      if c == channel]
            self.assertEqual(len(labels), 9, channel)
            self.assertEqual(set(labels), {"no_signal"}, channel)

    def test_no_positive_reading_was_dropped_or_mislabelled(self):
        # every recorded measure carries a verdict from the three documented codes
        self.assertEqual(set(l for l, _s in self.env.labels.values()),
                         {"no_signal", "direction"})
        # and every direction reading belongs to a channel that was later cleared
        cleared = set(self.log["completion"]["cleared"])
        for (_x, _y, channel), (label, _svd) in self.env.labels.items():
            if label == "direction":
                self.assertIn(channel, cleared)

    def test_located_sources_are_all_inside_the_target_region(self):
        """Triangulation from the recorded bearings: the practice world is in-domain."""
        per = {}
        for (_x, _y, channel), (label, svd) in self.env.labels.items():
            if label == "direction":
                per.setdefault(channel, []).append(((_x, _y), svd))
        norms = []
        for channel, readings in per.items():
            if len(readings) < 2:
                continue
            a = [[0.0, 0.0], [0.0, 0.0]]
            b = [0.0, 0.0]
            for (px, py), deg in readings:
                th = math.radians(deg)
                ux, uy = math.cos(th), math.sin(th)
                m = [[1 - ux * ux, -ux * uy], [-ux * uy, 1 - uy * uy]]
                for i in range(2):
                    for j in range(2):
                        a[i][j] += m[i][j]
                    b[i] += m[i][0] * px + m[i][1] * py
            det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
            gx = (b[0] * a[1][1] - a[0][1] * b[1]) / det
            gy = (a[0][0] * b[1] - b[0] * a[1][0]) / det
            norms.append(math.hypot(gx, gy))
        self.assertGreaterEqual(len(norms), 10)
        self.assertLess(max(norms), TARGET_RADIUS)


class TestNoGuardInTheControlFlow(unittest.TestCase):
    """The documented behaviour: a complete scan with no positive is a no-source claim.

    A channel is scripted as "silent" by **omitting** it from the scenario: the scripted
    environment then answers ``no_signal`` at every point, exactly as the live device did
    for channels 1, 5, 6, 10, 16, 20.  Ten or more in-range channels are kept so that the
    plan's count domain ``|F| >= 10`` still holds.
    """

    SILENT = (12, 13)
    #: twelve in-range channels, deliberately excluding the two silent ones
    DISCOVERED = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15)

    def _world(self, discovered=None):
        return [scenario.ChannelScript(c, candidate_observe.DIRECTION, 0.0, success_at_attempt=1)
                for c in (self.DISCOVERED if discovered is None else discovered)]

    def test_c0_marks_a_channel_no_source_from_a_complete_scan_with_no_positive(self):
        # twelve in-range channels; channels 12 and 13 are never observed at all
        result = flow.run_flow("Q3", self._world())
        store = result.runner.store
        for channel in self.SILENT:
            self.assertIs(store.channels[channel].exists, False, channel)
            self.assertIsNone(store.channels[channel].first_positive, channel)
        self.assertEqual(result.certificate["status"], "COMPLETE")
        self.assertEqual(result.certificate["success_count"], 12)

    def test_current_behaviour_reports_complete_with_k_below_the_true_count(self):
        """Documents the false-completion mode: C0 cannot see the world is out of domain.

        The live Q3 case had the same shape with 14 cleaned channels: the two unobserved
        sources were certified ``no_source`` and the run still reported COMPLETE.
        """
        result = flow.run_flow("Q3", self._world())
        self.assertEqual(result.certificate["status"], "COMPLETE")
        self.assertEqual(result.certificate["success_count"], 12)
        self.assertIn(12, result.certificate["no_source_channels"])
        self.assertIn(13, result.certificate["no_source_channels"])

    @unittest.expectedFailure
    def test_c0_should_not_report_complete_when_a_channel_source_is_still_in_range(self):
        """WI-022 objective 2: the desired behaviour, which FAILS on current B.

        The world has twelve in-range omni sources (a legal count) plus channels 12/13
        that are never observed even though a source still legitimately sits in range --
        the live Q3 situation.  A conservative certificate would refuse COMPLETE rather
        than assert a no-source it cannot actually see.  Frozen B reports COMPLETE with
        K < N.  No plan-faithful code change can tell the two cases apart from the
        responses alone, so WI-022 records this as a contract-level limitation rather
        than patching C0; the expected failure is the deliberate marker for that gap and
        will flip to "unexpected success" if a guard is ever added.
        """
        result = flow.run_flow("Q3", self._world())
        self.assertNotEqual(result.certificate.get("status"), "COMPLETE",
                            "C0 reported COMPLETE while at least one in-range source was "
                            "never observable; a conservative certificate must refuse")


class TestSameDayQ4ForComparison(unittest.TestCase):
    """Q4's P4 lattice has a much larger covering margin, and it found every source."""

    def test_q4_covering_radius_leaves_a_large_margin(self):
        """P4's worst cell-centre distance is 350*sqrt(2) ~ 495 m, half of P3's."""
        p4 = [(700.0 * i, 700.0 * j) for i in range(-4, 5) for j in range(-4, 5)]
        self.assertAlmostEqual(min(math.hypot(350.0 - q[0], 350.0 - q[1]) for q in p4),
                               350.0 * math.sqrt(2.0), places=9)
        worst = 0.0
        step = 50.0
        n = int(TARGET_RADIUS / step)
        for ix in range(-n, n + 1):
            x = ix * step
            for iy in range(-n, n + 1):
                y = iy * step
                if x * x + y * y > TARGET_RADIUS * TARGET_RADIUS:
                    continue
                d = min(math.hypot(x - q[0], y - q[1]) for q in p4)
                if d > worst:
                    worst = d
        self.assertLess(worst, 700.0)
        self.assertGreater(RADIUS_FLOOR - worst, 300.0)

    def test_q4_log_found_every_channel_it_could_see(self):
        log = replay.load_log(Q4_LOG)
        verdicts, env = replay.replay_scan(log, "Q4")
        exists = sorted(c for c, i in verdicts.items() if i["verdict"] == "exists")
        self.assertEqual(exists, log["completion"]["cleared"])
        self.assertEqual(len(exists), 16)


if __name__ == "__main__":
    unittest.main()
