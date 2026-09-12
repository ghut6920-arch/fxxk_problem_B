"""Offline environment stub used only by candidate tests.

This stands in for the injected official response source.  It is deliberately
kept in ``tests/candidate/`` (not in ``src/candidate/``) so the candidate package
contains no hidden-truth helper at all; hidden truth belongs to the environment
and, in a real run, to the evaluator process.
"""

import math

from candidate import observe


class WorldEnv:
    """Deterministic environment over an explicit world description."""

    def __init__(self, sources, bearing_error=None):
        #: channel -> {"present", "directional", "g", "R", "phi", "cleared"}
        self.sources = sources
        self.bearing_error = bearing_error or (lambda p, c: 0.0)
        self.log = []

    def measure(self, p, c):
        src = self.sources.get(c)
        if src is None or not src.get("present"):
            self.log.append(("measure", p, c, observe.NO_SIGNAL))
            return {"accepted": True, "observation": observe.NO_SIGNAL}
        obs = observe.observation(src, p)
        resp = {"accepted": True, "observation": obs}
        if obs == observe.DIRECTION:
            g = src["g"]
            true_bearing = math.atan2(g[1] - p[1], g[0] - p[0])
            resp["theta_hat"] = true_bearing + self.bearing_error(p, c)
        self.log.append(("measure", p, c, obs))
        return resp

    def clear(self, p, c):
        src = self.sources.get(c)
        if src is None:
            return {"accepted": True, "success": False}
        u_c = 1 if (src.get("present") and not src.get("cleared")) else 0
        ok = observe.clear_succeeds(src["g"], p, u_c)
        if ok:
            src["cleared"] = True
        self.log.append(("clear", p, c, ok))
        return {"accepted": True, "success": ok}


def omni(g, r=1500.0, present=True):
    return {"present": present, "directional": False, "g": tuple(g), "R": r, "phi": 0.0, "cleared": False}


def directional(g, phi=0.0, r=1500.0, present=True):
    return {"present": present, "directional": True, "g": tuple(g), "R": r, "phi": phi, "cleared": False}
