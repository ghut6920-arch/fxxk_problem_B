"""Per-item checks for the EXP-002 C0 P1-A property run (WI-016).

This package is a **run harness**: it may import the frozen ``evaluator`` (oracle
side) and the frozen ``candidate`` (under test).  It never edits either.

Every G01-G16 and T01-T10 item gets one check function.  A check returns
``(checks, notes, flags)``:

* ``checks`` -- list of ``(name, ok, detail)``; the item passes only when every
  entry is true;
* ``notes`` -- factual remarks recorded in the report (resolution used, measured
  quantities, residuals);
* ``flags`` -- counters for the SPEC safety metrics
  (``truth_exclusion``, ``false_completion``, ``unsafe_cancel``) and the
  ``ledger_residual`` (candidate-reported total minus evaluator recomputation).

Wording: this is a **same-model internal consistency check** on preregistered
fixtures (D-004 / SR-002).  Nothing here is an independent evaluation.
"""

from __future__ import annotations

import ast
import json
import math
import pathlib

from candidate import cells, geo, ledger, model, observe, q2, queue, scan
from candidate import state as cand_state

from evaluator import halfplane, predicates as ev

REPO = pathlib.Path(__file__).resolve().parents[2]
CANDIDATE_DIR = REPO / "src" / "candidate"

#: plan section 4.3 frozen feedback partition, used for the G09/G11 comparators
FROZEN_INTERVALS = 360
#: plan section 6 per-channel cell cap, used for the G09/G11 comparators
FROZEN_LEAVES = 4096
FROZEN_DEPTH = 8


def approx(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))


def _flags():
    return {"truth_exclusion": 0, "false_completion": 0, "unsafe_cancel": 0, "ledger_residual": None}


def _ev_source(world):
    """Evaluator-side source dict from a fixture world."""
    src = {"g": list(world["g"]), "R_c": world["R_c"], "kind": world.get("kind", "omni")}
    if src["kind"] == "directional":
        src["phi_deg"] = world["phi_deg"]
    return src


def _cand_source(world):
    """Candidate-side source dict from the same fixture world."""
    return {
        "g": tuple(float(v) for v in world["g"]),
        "R": float(world["R_c"]),
        "directional": world.get("kind", "omni") == "directional",
        "phi": math.radians(float(world.get("phi_deg", 0.0))),
        "present": True,
        "cleared": False,
    }


def _halfplanes(rows):
    return [geo.HalfPlane(hp["a"], hp["b"], hp["c"]) for hp in rows]


# ---------------------------------------------------------------- G01-G08


def g01(fx, _ev):
    rows = fx["inputs"]["half_planes"]
    cand = geo.classify_region(_halfplanes(rows))
    oracle = halfplane.halfplane_state(halfplane.parse_halfplanes(rows))
    frozen = fx["expected_evaluator"]["halfplane_state"]
    checks = [
        ("candidate state is CONFLICT", cand.status == geo.CONFLICT, f"candidate={cand.status}"),
        ("candidate agrees with the frozen evaluator label", cand.status == frozen, f"{cand.status} vs {frozen}"),
        ("candidate agrees with the evaluator oracle", cand.status == oracle, f"{cand.status} vs {oracle}"),
        ("empty set is not reported as a completed task",
         observe.completion_label(0, True, True, conflict=True) != observe.COMPLETE,
         "completion_label(conflict=True)"),
        ("no diameter is claimed for the empty intersection", cand.diameter is None, f"{cand.diameter}"),
    ]
    flags = _flags()
    if observe.completion_label(0, True, True, conflict=True) == observe.COMPLETE:
        flags["false_completion"] = 1
    return checks, [], flags


def g02(fx, _ev):
    rows = fx["inputs"]["half_planes"]
    cand = geo.classify_region(_halfplanes(rows))
    oracle = halfplane.halfplane_state(halfplane.parse_halfplanes(rows))
    checks = [
        ("candidate state is UNBOUNDED", cand.status == geo.UNBOUNDED, f"candidate={cand.status}"),
        ("candidate agrees with the frozen label", cand.status == fx["expected_evaluator"]["halfplane_state"],
         fx["expected_evaluator"]["halfplane_state"]),
        ("candidate agrees with the evaluator oracle", cand.status == oracle, f"{cand.status} vs {oracle}"),
        ("no finite diameter is reported", cand.diameter is None, f"diameter={cand.diameter}"),
        ("a nonzero recession direction is recorded",
         cand.recession_direction is not None and math.hypot(*cand.recession_direction) > 0.5,
         f"{cand.recession_direction}"),
    ]
    return checks, [], _flags()


def _bounded_item(fx, expect_vertices, expect_diameter, expect_centre=None):
    rows = fx["inputs"]["half_planes"]
    cand = geo.classify_region(_halfplanes(rows))
    oracle_state = halfplane.halfplane_state(halfplane.parse_halfplanes(rows))
    exp = fx["expected_evaluator"]
    vertices = sorted((float(v[0]), float(v[1])) for v in cand.vertices)
    checks = [
        ("candidate state is BOUNDED", cand.status == geo.BOUNDED, f"candidate={cand.status}"),
        ("candidate agrees with the evaluator oracle", cand.status == oracle_state, f"{cand.status} vs {oracle_state}"),
        ("vertex set matches the frozen expectation",
         len(vertices) == len(expect_vertices)
         and all(approx(a, c) and approx(b, d)
                 for (a, b), (c, d) in zip(vertices, expect_vertices)),
         f"{vertices} vs {expect_vertices}"),
        ("diameter matches", approx(cand.diameter, expect_diameter), f"{cand.diameter} vs {expect_diameter}"),
        ("evaluator diameter agrees",
         approx(halfplane.halfplane_diameter(halfplane.parse_halfplanes(rows)), expect_diameter),
         "evaluator halfplane_diameter"),
        ("diameter circle covers every vertex", bool(cand.diameter_circle_covers), "diameter_circle_covers"),
    ]
    expected_diameter = exp.get("diameter", expect_diameter)
    checks.append(("diameter matches the fixture field", approx(cand.diameter, expected_diameter),
                   f"{cand.diameter} vs {expected_diameter}"))
    if expect_centre is not None:
        cx, cy = cand.diameter_circle_centre
        checks.append(("covering-circle centre matches", approx(cx, expect_centre[0]) and approx(cy, expect_centre[1]),
                       f"{(float(cx), float(cy))} vs {expect_centre}"))
        checks.append(("covering-circle radius matches", approx(cand.diameter_circle_radius, exp.get("radius",
                       expect_diameter / 2.0)), f"{cand.diameter_circle_radius}"))
    if "min_enclosing_radius" in exp:
        checks.append(("min enclosing radius matches the fixture",
                       approx(cand.min_enclosing_radius, exp["min_enclosing_radius"]),
                       f"{cand.min_enclosing_radius} vs {exp['min_enclosing_radius']}"))
        checks.append(("min enclosing radius agrees with the evaluator oracle",
                       approx(cand.min_enclosing_radius,
                              halfplane.halfplane_min_enclosing_radius(halfplane.parse_halfplanes(rows))),
                       "evaluator halfplane_min_enclosing_radius"))
    return checks, _flags()


def g03(fx, _ev):
    checks, flags = _bounded_item(fx, [(0.0, 0.0)], 0.0, expect_centre=(0.0, 0.0))
    checks.append(("zero-radius circle has radius 0", approx(fx["expected_evaluator"]["covering_circle"]["radius"], 0.0), "0"))
    return checks, ["degenerate single point: vertices, zero diameter and the point circle all exercised"], flags


def g04(fx, _ev):
    checks, flags = _bounded_item(fx, [(0.0, 0.0), (1.0, 0.0)], 1.0, expect_centre=(0.5, 0.0))
    checks.append(("endpoint-circle radius is half the segment", approx(fx["expected_evaluator"]["covering_circle"]["radius"], 0.5), "0.5"))
    return checks, ["degenerate segment: endpoints retained as vertices"], flags


def g05(fx, _ev):
    exp = fx["expected_evaluator"]
    vertices, flags = _bounded_item(fx, [(0.0, 0.0), (0.0, 2.0), (1.0, 0.0), (1.0, 2.0)], math.sqrt(5.0))
    rows = fx["inputs"]["half_planes"]
    cand = geo.classify_region(_halfplanes(rows))
    cx, cy = cand.diameter_circle_centre
    max_offset = max(math.hypot(float(v[0]) - float(cx), float(v[1]) - float(cy)) for v in cand.vertices)
    checks = vertices + [
        ("farthest-pair midpoint matches", approx(cx, 0.5) and approx(cy, 1.0), f"{(float(cx), float(cy))}"),
        ("max vertex distance to the midpoint matches", approx(max_offset, exp["max_vertex_distance_to_midpoint"]),
         f"{max_offset} vs {exp['max_vertex_distance_to_midpoint']}"),
        ("evaluator covering circle agrees",
         approx(halfplane.halfplane_covering_circle(halfplane.parse_halfplanes(rows))["radius"],
                exp["max_vertex_distance_to_midpoint"]), "evaluator halfplane_covering_circle"),
    ]
    return checks, [], flags


def g06(fx, _ev):
    exp = fx["expected_evaluator"]
    cov = geo.equilateral_cover(fx["inputs"]["side_length"])
    checks = [
        ("diameter is 1", approx(cov["diameter"], exp["diameter"]), f"{cov['diameter']}"),
        ("circumradius is 1/sqrt(3)", approx(cov["circumradius"], exp["circumradius"]), f"{cov['circumradius']}"),
        ("circumcentre matches", approx(cov["circumcentre"][0], exp["circumcenter"][0])
         and approx(cov["circumcentre"][1], exp["circumcenter"][1]), f"{cov['circumcentre']}"),
        ("radius-1/2 circle does NOT cover the vertices",
         cov["half_radius_covers"] == exp["half_radius_covers_vertices"] == False, f"{cov['half_radius_covers']}"),
        ("circumradius circle does cover", bool(cov["circumradius_covers"]), "circumradius_covers"),
        ("covering-circle submodule rejects the half-diameter circle",
         cov["circumradius"] > cov["half_radius"], f"{cov['circumradius']} > {cov['half_radius']}"),
    ]
    return checks, [], _flags()


def g07(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    rows_a = inputs["g07a_parallel_strip"]["half_planes"]
    cand_a = geo.classify_region(_halfplanes(rows_a))
    oracle_a = halfplane.halfplane_state(halfplane.parse_halfplanes(rows_a))
    spec = inputs["g07b_near_collinear"]
    ev_rows = halfplane.wedge_pair_halfplanes(spec)
    cand_rows = list(geo.wedge_halfplanes(spec["S1"], math.radians(spec["theta_hat_1_deg"]),
                                          math.radians(spec["delta_deg"]))) + \
        list(geo.wedge_halfplanes(spec["S2"], math.radians(spec["theta_hat_2_deg"]), math.radians(spec["delta_deg"])))
    row_match = all(
        approx(float(hp.a), float(a), 0) and approx(float(hp.b), float(b), 0) and approx(float(hp.c), float(c), 0)
        for hp, (a, b, c) in zip(cand_rows, ev_rows)
    )
    cand_b = geo.classify_region(cand_rows)
    oracle_b = halfplane.halfplane_state(ev_rows)
    q = tuple(inputs["g07b_ray_certificate"]["q"])
    d = tuple(inputs["g07b_ray_certificate"]["d"])
    cand_ok, cand_margin = geo.certify_ray(cand_rows, q, d)
    cand_bad, _m = geo.certify_ray(cand_rows, q, (0.0, 1.0))
    ev_ok, ev_wit = halfplane.ray_certificate(ev_rows, q, d)
    checks = [
        ("G07a is UNBOUNDED", cand_a.status == geo.UNBOUNDED == exp["g07a_state"], f"{cand_a.status}"),
        ("G07a agrees with the evaluator oracle", cand_a.status == oracle_a, f"{cand_a.status} vs {oracle_a}"),
        ("G07a reports no finite diameter", cand_a.diameter is None, f"{cand_a.diameter}"),
        ("candidate wedge rows equal the evaluator wedge rows", row_match, f"{len(cand_rows)} rows"),
        ("G07b is UNBOUNDED", cand_b.status == geo.UNBOUNDED == exp["g07b_state"], f"{cand_b.status}"),
        ("G07b is not CONFLICT / BOUNDED / NUMERICAL_UNCERTAIN",
         cand_b.status not in (geo.CONFLICT, geo.BOUNDED, geo.NUMERICAL_UNCERTAIN), f"{cand_b.status}"),
        ("G07b feasible", geo.is_feasible(cand_rows) == exp["g07b_feasible"] is True, "is_feasible"),
        ("G07b has a nonzero recession direction", cand_b.recession_direction is not None, f"{cand_b.recession_direction}"),
        ("G07b does not report a finite diameter", cand_b.diameter is None, f"{cand_b.diameter}"),
        ("candidate certifies the frozen ray q=(2000,0), d=(1,0)", cand_ok is True, f"margin={cand_margin}"),
        ("candidate rejects a wrong ray direction", cand_bad is False, "d=(0,1)"),
        ("evaluator certifies the same frozen ray exactly", ev_ok is True, f"{len(ev_wit)} rows"),
        ("evaluator oracle also says UNBOUNDED", oracle_b == exp["g07b_state"], f"{oracle_b}"),
        ("no disk cap is applied (certificate point is outside D)",
         math.hypot(*q) > ev.DISK_RADIUS, f"|q|={math.hypot(*q)} > {ev.DISK_RADIUS}"),
    ]
    return checks, [f"G07b candidate ray margin {cand_margin:.6f}; frozen q,d verified without any start/sample test"], _flags()


def g08(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    a = geo.deg2rad(inputs["A_deg"])
    b = geo.deg2rad(inputs["B_deg"])
    c = geo.deg2rad(inputs["C_deg"])
    checks = [
        ("candidate wraps A and B to the same internal direction",
         approx(math.degrees(geo.wrap_pi(a)), math.degrees(geo.wrap_pi(b)), 1e-9),
         f"{math.degrees(geo.wrap_pi(a)):.12f} vs {math.degrees(geo.wrap_pi(b)):.12f}"),
        ("candidate wrap agrees with the evaluator wrap_deg",
         approx(math.degrees(geo.wrap_pi(a)), ev.wrap_deg(inputs["A_deg"]), 1e-9),
         f"{math.degrees(geo.wrap_pi(a))} vs {ev.wrap_deg(inputs['A_deg'])}"),
        ("C is the +90 degree rotated equivalent",
         approx(math.degrees(geo.wrap_pi(a + math.pi / 2.0)), inputs["C_deg"], 1e-9),
         f"{math.degrees(geo.wrap_pi(a + math.pi / 2.0))}"),
        ("A/B equivalence is not decided by two-decimal display",
         round(inputs["A_deg"], 2) != round(inputs["B_deg"], 2) and
         approx(math.degrees(geo.wrap_pi(a)), math.degrees(geo.wrap_pi(b)), 1e-9), "359.50 vs -0.50 display"),
    ]
    # rotated-equivalent geometry: classification is invariant under an exact +90 degree rotation
    from fractions import Fraction
    wedge = geo.wedge_from_rational_direction((0, 0), (1, 0), Fraction(1, 10))
    rotated = [geo.HalfPlane(-hp.b, hp.a, hp.c) for hp in wedge]
    r0, r1 = geo.classify_region(wedge), geo.classify_region(rotated)
    checks.append(("candidate geometry is invariant under an exact +90 degree rotation",
                   r0.status == r1.status, f"{r0.status} vs {r1.status}"))
    return checks, ["rotation is re-checked on the representation itself, not on a fixed lattice"], _flags()


# ---------------------------------------------------------------- G09-G16


def g09(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    s = tuple(inputs["S"])
    theta_deg = inputs["theta_hat_deg"]
    theta = math.radians(theta_deg)
    pool = [tuple(p) for p in inputs["submitted_pool"]]
    lateral = tuple(inputs["extra_points"]["lateral"])
    forward = tuple(inputs["extra_points"]["forward"])
    checks = []
    for i, g in enumerate(inputs["worlds"]):
        world = {"g": g["g"], "R_c": inputs["R_c"], "kind": "omni"}
        ev_label = ev.observation(_ev_source(world), s)
        cand_label = observe.observation(_cand_source(world), s)
        checks.append((f"world {i} in D", ev.in_disk(g["g"]) == exp["worlds_in_D"][i], f"{g['g']}"))
        checks.append((f"world {i} first observation is direction (evaluator)", ev_label == exp["first_observation"][i],
                       f"{ev_label}"))
        checks.append((f"world {i} first observation agrees (candidate)", cand_label == ev_label,
                       f"candidate={cand_label} evaluator={ev_label}"))
    for i, p in enumerate(pool):
        cand_in = q2.c_in_membership(p, s, theta)["inside"]
        ev_in = ev.c_in_member(s, theta_deg, p)
        checks.append((f"pool point {i} certified in C_in by candidate and evaluator",
                       cand_in == ev_in == exp["c_in_membership_pool"][i], f"{p} cand={cand_in} ev={ev_in}"))
    checks.append(("lateral (500,500) certified in C_in",
                   q2.c_in_membership(lateral, s, theta)["inside"] == ev.c_in_member(s, theta_deg, lateral)
                   == exp["c_in_membership_lateral"], f"{lateral}"))
    checks.append(("forward (500,0) certified in C_in",
                   q2.c_in_membership(forward, s, theta)["inside"] == ev.c_in_member(s, theta_deg, forward)
                   == exp["c_in_membership_forward"], f"{forward}"))
    checks.append(("forward point is not a member of the six-point pool",
                   forward not in pool, f"{forward} in pool? {forward in pool}"))
    # inner-domain guarantee must not be a hidden-truth read: A_1 must retain each world
    a1 = q2.build_a1_outer(s, theta, max_leaves=FROZEN_LEAVES, max_depth=FROZEN_DEPTH)
    retained = [a1.contains_any(w["g"]) for w in inputs["worlds"]]
    checks.append(("candidate A_1 outer approximation retains all three worlds", all(retained), f"{retained}"))
    # the named comparator family must run at the frozen resolution
    res = q2.certifiable_candidates(s, theta, intervals=FROZEN_INTERVALS, max_leaves=FROZEN_LEAVES,
                                    max_depth=FROZEN_DEPTH)
    checked_tags = sorted({r["tag"] for r in res["candidates"]})
    checks.append(("comparator ran at the frozen 360-interval / 4096-leaf resolution", res["status"] == "OK",
                   f"status={res['status']} intervals={FROZEN_INTERVALS} leaves={FROZEN_LEAVES}"))
    checks.append(("all three comparator families are present", checked_tags == ["forward", "lateral", "pool"],
                   f"{checked_tags}"))
    checks.append(("every certified comparator point reports a bound and a move cost",
                   all(r.get("worst_radius") is not None and r.get("move_cost") is not None
                       for r in res["candidates"] if r.get("status") == "OK"), f"{len(res['ranking'])} ranked"))
    notes = [f"G09 comparator: {FROZEN_INTERVALS} intervals x 4096-leaf cap, {len(res['ranking'])} certified points",
             "truth (g, R_c) was used only on the evaluator side; C_in membership uses the public S, theta_hat only"]
    return checks, notes, _flags()


def g10(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    g = inputs["g"]
    s = tuple(inputs["S"])
    checks = [("true source is in D", ev.in_disk(g) == exp["g_in_D"], f"{g}") ]
    for i, world in enumerate(inputs["worlds"]):
        w = {"g": g, "R_c": world["R_c"], "kind": "omni", "phi_deg": 0.0}
        theta_deg = world["theta_hat_deg"]
        ev_label = ev.observation(_ev_source(w), s)
        cand_label = observe.observation(_cand_source(w), s)
        checks.append((f"world {i} observation is direction (evaluator)", ev_label == exp["observation"][i], ev_label))
        checks.append((f"world {i} observation agrees (candidate)", cand_label == ev_label, f"{cand_label}"))
        checks.append((f"world {i} endpoints satisfy the direction contract (evaluator)",
                       ev.direction_contract_ok(theta_deg, s, g) == exp["direction_contract_ok"][i], "delta=1 deg"))
        checks.append((f"world {i} endpoints satisfy the direction contract (candidate)",
                       observe.bearing_consistent(_cand_source(w), s, math.radians(theta_deg)) is True, "delta=1 deg"))
        a1 = q2.build_a1_outer(s, math.radians(theta_deg), max_leaves=FROZEN_LEAVES, max_depth=FROZEN_DEPTH)
        checks.append((f"world {i} true position retained in the candidate outer approximation",
                       a1.contains_any(g), f"leaves={a1.leaf_count}"))
    flags = _flags()
    if not all(ok for name, ok, _d in checks if "retained" in name):
        flags["truth_exclusion"] = 1
    return checks, [f"g on the disk boundary at r={math.hypot(g[0]-s[0], g[1]-s[1])} m"], flags


def g11(fx, _ev):
    inputs = fx["inputs"]
    first = inputs["first_observation"]
    exp = fx["expected_evaluator"]
    s = tuple(first["S"])
    theta = math.radians(first["theta_hat_deg"])
    comp = inputs["comparators"]
    checks = []
    for i, p in enumerate(comp["pool_6"]):
        checks.append((f"pool {i} certified in C_in by both sides",
                       q2.c_in_membership(tuple(p), s, theta)["inside"]
                       == ev.c_in_member(s, first["theta_hat_deg"], p) == exp["c_in_membership_pool"][i], f"{p}"))
    checks.append(("lateral certified in C_in", q2.c_in_membership(tuple(comp["lateral"]), s, theta)["inside"]
                   == exp["c_in_membership_lateral"] == True, f"{comp['lateral']}"))
    checks.append(("forward certified in C_in", q2.c_in_membership(tuple(comp["forward"]), s, theta)["inside"]
                   == exp["c_in_membership_forward"] == True, f"{comp['forward']}"))
    res = q2.certifiable_candidates(s, theta, intervals=FROZEN_INTERVALS, max_leaves=FROZEN_LEAVES,
                                    max_depth=FROZEN_DEPTH)
    checks.append(("comparator ran at the frozen 360-interval / 4096-leaf resolution", res["status"] == "OK",
                   f"status={res['status']}"))
    checks.append(("all three comparator families produced a worst-case bound",
                   sorted({r["tag"] for r in res["candidates"]}) == ["forward", "lateral", "pool"],
                   f"{sorted({r['tag'] for r in res['candidates']})}"))
    bounds = {r["tag"]: r.get("worst_radius") for r in res["candidates"] if r.get("status") == "OK"}
    checks.append(("a worst-case cover-radius upper bound is reported per family", all(v is not None for v in bounds.values()),
                   f"{ {k: round(v, 3) for k, v in bounds.items()} }"))
    checks.append(("a move cost is reported per candidate",
                   all(r.get("move_cost") is not None for r in res["candidates"]), "move_cost"))
    checks.append(("the forward (near-collinear) comparator is worst here, so 90 degrees is not claimed optimal",
                   bounds.get("forward", 0.0) > min(bounds.values()), f"forward={bounds.get('forward'):.3f}"))
    checks.append(("lateral is not hard-coded as the winner",
                   res["selected_record"]["tag"] in ("pool", "lateral", "forward"),
                   f"selected tag={res['selected_record']['tag']}"))
    checks.append(("no '90 degrees is always optimal' claim is exposed",
                   "optimal" not in model.MODULE_MAP and not any("optimal" in k for k in res.keys()),
                   "MODULE_MAP / result keys"))
    notes = [f"G11 bounds (360 intervals, 4096-leaf cap): { {k: round(v, 3) for k, v in bounds.items()} }",
             "near-collinear forward has the largest worst-case bound; the report makes no optimality claim"]
    return checks, notes, _flags()


def g12(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    s = tuple(inputs["S"])
    theta_deg = inputs["theta_hat_deg"]
    theta = math.radians(theta_deg)
    p = tuple(inputs["p"])
    des = tuple(json.loads(inputs["serialization"]["raw"]))
    checks = [
        ("raw point is certified in C_in by candidate and evaluator",
         q2.c_in_membership(p, s, theta)["inside"] == ev.c_in_member(s, theta_deg, p) == exp["c_in_original"], f"{p}"),
        ("deserialized point is certified on both sides",
         q2.c_in_membership(des, s, theta)["inside"] == ev.c_in_member(s, theta_deg, des) == exp["c_in_deserialized"],
         f"{des}"),
        ("deserialized coordinates are the submitted coordinates",
         tuple(exp["deserialized_point"]) == des, f"{des}"),
        ("the point is on the closed ||q|| = 1000 piece",
         approx(math.hypot(des[0] - s[0], des[1] - s[1]), 1000.0), "boundary piece"),
    ]
    # the rejection branch must exist: a point beyond the certificate is refused
    outside = (1200.0, 0.0)
    checks.append(("a point outside C_in is rejected (rejection branch exercised)",
                   q2.c_in_membership(outside, s, theta)["inside"] is False
                   and ev.c_in_member(s, theta_deg, outside) is False, f"{outside}"))
    return checks, ["the candidate re-checks the serialized coordinate, not an unsubmitted ideal point"], _flags()


def g13(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    s = tuple(inputs["S"])
    theta = math.radians(inputs["theta_hat_deg"])
    checks = []
    for i, world in enumerate(inputs["worlds"]):
        w = {"g": world["g"], "R_c": inputs["R_c"], "kind": "omni"}
        ev_label = ev.observation(_ev_source(w), s)
        cand_label = observe.observation(_cand_source(w), s)
        checks.append((f"world {i} ({world['note']}) label matches the frozen expectation",
                       ev_label == exp["observation"][i], f"evaluator={ev_label}"))
        checks.append((f"world {i} candidate agrees with the evaluator", cand_label == ev_label,
                       f"candidate={cand_label}"))
    # successor containment: A_2^near and A_2^dir must retain the true source
    g_dir = (1000.0, 0.0)
    a1 = q2.build_a1_outer(s, theta, max_leaves=FROZEN_LEAVES, max_depth=FROZEN_DEPTH)
    near_state = q2.successor_near(a1, (1000.0, 0.0))
    checks.append(("A_2^near retains the true source", near_state.contains_any(g_dir), f"leaves={near_state.leaf_count}"))
    p2 = (500.0, 0.0)
    back = math.atan2(g_dir[1] - p2[1], g_dir[0] - p2[0])
    dir_state = q2.successor_dir(a1, p2, back)
    checks.append(("A_2^dir retains the true source", dir_state.contains_any(g_dir), f"leaves={dir_state.leaf_count}"))
    x0, y0, x1, y1 = near_state.bounding_box()
    checks.append(("near score 0 is not zero position variance (successor still has area)",
                   (x1 - x0) * (y1 - y0) > 0.0, f"area={(x1 - x0) * (y1 - y0):.3f}"))
    checks.append(("no_signal successor is nonempty inside C_in (conflict must be logged, not ignored)",
                   q2.successor_no(a1, q2.forward_point(s, theta)).leaf_count > 0, "A_2^no"))
    flags = _flags()
    if not near_state.contains_any(g_dir) or not dir_state.contains_any(g_dir):
        flags["truth_exclusion"] = 1
    return checks, [], flags


def g14(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    world = {"g": inputs["g"], "R_c": inputs["R_c"], "kind": "directional", "phi_deg": inputs["phi_deg"]}
    s = tuple(inputs["S"])
    ev_label = ev.observation(_ev_source(world), s)
    cand_label = observe.observation(_cand_source(world), s)
    checks = [
        ("evaluator visibility is false", ev.visibility("directional", inputs["phi_deg"], s, inputs["g"])
         == exp["visible"] == False, f"n.phi . (S-g) = {sum(a * b for a, b in zip(inputs['n_phi'], [s[0]-inputs['g'][0], s[1]-inputs['g'][1]]))}"),
        ("evaluator label is no_signal", ev_label == exp["observation"], ev_label),
        ("candidate label agrees: no_signal", cand_label == ev_label == observe.NO_SIGNAL, f"{cand_label}"),
        ("candidate does not treat this world as a guaranteed-receive Q2 case",
         cand_label not in (observe.NEAR, observe.DIRECTION), "no C_in applicability"),
        ("directional back-side no_signal keeps the position (orientation only)",
         observe.no_signal_removes("directional", 500.0) == "orientation_only", "no_signal_removes"),
        ("omnidirectional no_signal would remove the position (rule differs by type)",
         observe.no_signal_removes("omni", 500.0) == "position", "no_signal_removes"),
        ("back-side no_signal never deletes a true position",
         observe.back_side_no_signal_deletes_position(world) is False, "helper"),
    ]
    return checks, [f"world label from the fixture: {exp['world_label']} (a component world, not a performance sample)"], _flags()


def g15(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    cand_p3 = {(float(p[0]), float(p[1])) for p in scan.P3()}
    cand_p4 = {(float(p[0]), float(p[1])) for p in scan.P4()}
    ev_p3 = {(float(p[0]), float(p[1])) for p in ev.p3_points()}
    ev_p4 = {(float(p[0]), float(p[1])) for p in ev.p4_points()}
    checks = [
        ("candidate P_3 is the frozen 9-point lattice", cand_p3 == ev_p3 and len(cand_p3) == exp["P_3_count"],
         f"{len(cand_p3)} points"),
        ("candidate P_4 is the frozen 81-point lattice", cand_p4 == ev_p4 and len(cand_p4) == exp["P_4_count"],
         f"{len(cand_p4)} points"),
    ]
    for world in inputs["omni_worlds"]:
        ev_vis = ev.visible_scan_points(ev.p3_points(), _ev_source(world))
        cand_vis = scan.visible_lattice_points(scan.P3(), _cand_source(world))
        ev_vis4 = ev.visible_scan_points(ev.p4_points(), _ev_source(world))
        cand_vis4 = scan.visible_lattice_points(scan.P4(), _cand_source(world))
        checks.append((f"{world['name']}: P_3 visible set nonempty on both sides",
                       len(ev_vis) > 0 and len(cand_vis) > 0 and exp["p3_visible_nonempty"][world["name"]],
                       f"evaluator={len(ev_vis)} candidate={len(cand_vis)}"))
        checks.append((f"{world['name']}: P_4 visible set nonempty on both sides",
                       len(ev_vis4) > 0 and len(cand_vis4) > 0 and exp["p4_visible_nonempty"][world["name"]],
                       f"evaluator={len(ev_vis4)} candidate={len(cand_vis4)}"))
    ht = inputs["heading_triple"]
    for name, p, expected in (("p_R", ht["p_R"], exp["heading_triple_at_p_R"]),
                              ("p_L", ht["p_L"], exp["heading_triple_at_p_L"]),
                              ("p_offaxis", ht["p_offaxis"], exp["heading_triple_at_p_offaxis"])):
        for i, phi in enumerate(ht["phi_deg"]):
            world = {"g": ht["g"], "R_c": ht["R_c"], "kind": "directional", "phi_deg": phi}
            ev_label = ev.observation(_ev_source(world), p)
            cand_label = observe.observation(_cand_source(world), p)
            checks.append((f"heading triple {name}[{i}] matches the frozen label",
                           ev_label == expected[i] and cand_label == ev_label,
                           f"evaluator={ev_label} candidate={cand_label} expected={expected[i]}"))
    mirror = {"g": ht["g"], "R_c": ht["R_c"], "kind": "directional", "phi_deg": 90.0}
    checks.append(("mirror closed boundary at p_L(phi=90) is direction",
                   observe.observation(_cand_source(mirror), ht["p_L"]) == exp["heading_triple_mirror_closed_boundary_at_p_L_90"]
                   == ev.observation(_ev_source(mirror), ht["p_L"]), "closed half-plane boundary"))
    checks.append(("epsilon_phi is an angle, distinct from the metre epsilon_d",
                   approx(inputs["epsilon_phi_deg"], math.degrees(math.atan(inputs["epsilon_d"] / 700.0)), 1e-9)
                   and inputs["epsilon_phi_rad"] == math.atan(inputs["epsilon_d"] / 700.0),
                   f"eps_phi_deg={inputs['epsilon_phi_deg']}"))
    roundtripped = [json.loads(json.dumps(phi)) for phi in ht["phi_deg"]]
    checks.append(("JSON round-trip preserves the perturbations distinct from 90",
                   roundtripped[0] != 90.0 and roundtripped[2] != 90.0
                   and roundtripped[0] != roundtripped[2] == exp["heading_json_perturbations_pairwise_distinct"] is False
                   or (roundtripped[0] != roundtripped[2]), f"{roundtripped}"))
    checks.append(("two-decimal rounding would destroy the heading distinction",
                   round(ht["phi_deg"][0], 2) == round(ht["phi_deg"][2], 2) == 90.0,
                   "rounding is not used as internal arithmetic"))
    co = inputs["coincidence_o03"]
    co_world = {"g": co["g"], "R_c": co["R_c"], "kind": "directional", "phi_deg": co["phi_deg"]}
    checks.append(("directional coincidence keeps the open O-03 branch",
                   observe.observation(_cand_source(co_world), tuple(co["g"])) == exp["coincidence_label"]
                   == observe.O03_OPEN, "O03_OPEN"))
    vis = scan.visible_lattice_points(scan.P4(), _cand_source(co_world))
    checks.append(("the coincidence point is not used as coverage evidence",
                   all(p != tuple(co["g"]) for p, _lab in vis) and not exp["coincidence_used_as_coverage_evidence"],
                   f"{len(vis)} visible points, coincidence excluded"))
    p4_dir_nonempty = [bool(scan.visible_lattice_points(scan.P4(), _cand_source(
        {"g": ht["g"], "R_c": ht["R_c"], "kind": "directional", "phi_deg": phi}))) for phi in ht["phi_deg"]]
    checks.append(("directional P_4 visible set nonempty for all three frozen headings",
                   p4_dir_nonempty == exp["heading_triple_p4_visible_nonempty"], f"{p4_dir_nonempty}"))
    notes = ["P_3/P_4 generated from the formula on both sides; the visible-set claim is recomputed by the candidate"]
    return checks, notes, _flags()


def g16(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    s = tuple(inputs["S"])
    theta = inputs["theta_deg"]
    cand = scan.clear_rectangle_centres(s, math.radians(theta))
    evc = [tuple(p) for p in ev.clear_centres(s, theta)]
    cand_set = {(round(p[0], 9), round(p[1], 9)) for p in cand}
    ev_set = {(round(p[0], 9), round(p[1], 9)) for p in evc}
    checks = [
        ("225 distinct clear centres generated", len(cand) == exp["centre_count"] == len(cand_set), f"{len(cand)}"),
        ("candidate centres match the formula and the evaluator list",
         cand_set == ev_set and exp["centres_match_formula"] is True,
         f"set equality on {len(cand_set)} points"),
    ]
    worst = 0.0
    for cx, cy in cand:
        for dx in (-10.0, 10.0):
            for dy in (-10.0, 10.0):
                worst = max(worst, math.hypot(dx, dy))
    checks.append(("cell-to-centre distance is 10*sqrt(2) < 20", approx(worst, 10.0 * math.sqrt(2.0))
                   and scan.CELL_TO_CENTRE_MAX < 20.0, f"{worst:.6f}"))
    checks.append(("1 m submission error still leaves 10*sqrt(2)+1 < 20",
                   approx(scan.combined_cover_radius_upper_bound(), 10.0 * math.sqrt(2.0) + 1.0)
                   and scan.combined_cover_radius_upper_bound() < 20.0, f"{scan.combined_cover_radius_upper_bound():.6f}"))
    exact = tuple(inputs["submitted_centre_with_1m_error"]["exact"])
    submitted = tuple(inputs["submitted_centre_with_1m_error"]["submitted"])
    checks.append(("submitted centre offset norm is exactly 1 m",
                   approx(exp["submitted_offset_norm"], math.hypot(submitted[0] - exact[0], submitted[1] - exact[1]))
                   and scan.submitted_within_bound(exact, submitted), f"{submitted} vs {exact}"))
    checks.append(("a 1.1 m offset is rejected (certification bound is not widened)",
                   scan.submitted_within_bound(exact, (exact[0] + 1.1, exact[1])) is False, "1.1 m"))
    for i, (pair, expected) in enumerate(zip(
            (inputs["source_placements"]["distance_20_minus_eps"], inputs["source_placements"]["distance_20"],
             inputs["source_placements"]["distance_20_plus_eps"]), exp["clear_results"])):
        centre, source = tuple(pair[0]), tuple(pair[1])
        cand_ok = observe.clear_succeeds(source, centre, 1)
        ev_ok = ev.clear_succeeds({"g": list(source), "R_c": 1500}, centre)
        checks.append((f"clear at 20 m placement {i} is {expected}",
                       (cand_ok and expected == "success") or (not cand_ok and expected == "fail"),
                       f"candidate={cand_ok} evaluator={ev_ok}"))
        checks.append((f"evaluator agrees on placement {i}", cand_ok == ev_ok, f"{cand_ok} vs {ev_ok}"))
    corner = tuple(inputs["source_placements"]["corner"])
    nearest = min(cand, key=lambda c: math.hypot(c[0] - corner[0], c[1] - corner[1]))
    checks.append(("rectangle corner is covered by its nearest centre within 20 m",
                   approx(nearest[0], exp["corner_nearest_centre"][0]) and approx(nearest[1], exp["corner_nearest_centre"][1])
                   and approx(math.hypot(nearest[0] - corner[0], nearest[1] - corner[1]), exp["corner_centre_distance"]),
                   f"nearest={tuple(round(v, 3) for v in nearest)} distance="
                   f"{math.hypot(nearest[0] - corner[0], nearest[1] - corner[1]):.6f}"))
    a, b = inputs["adjacent_centres"]
    checks.append(("adjacent nominal 20 m and the 22 m bound with two 1 m errors",
                   approx(ev.dist(a, b), exp["adjacent_nominal"]) and scan.adjacent_submitted_bound()
                   == exp["adjacent_bound_with_1m_errors"] == 22.0, f"{scan.adjacent_submitted_bound()}"))
    # WI-018: the *emitted* order must satisfy the bound, not just the nominal pair above.
    # G16's fixture heading is 0 deg, where the pre-repair global-y snake coincided with the
    # local core snake, so this fixture alone could not see the long-step defect: at 45 deg
    # 150 of 224 steps reached sqrt(40^2+60^2) ~ 72.11 m.  Rotated rectangles are generated
    # here from the same S (the fixture is not edited).
    bound = scan.adjacent_submitted_bound()
    for theta_deg in (45.0, 90.0, 123.456):
        rotated = scan.clear_rectangle_centres(s, math.radians(theta_deg))
        step_lengths = [math.hypot(rotated[k][0] - rotated[k - 1][0], rotated[k][1] - rotated[k - 1][1])
                        for k in range(1, len(rotated))]
        worst_step = max(step_lengths) if step_lengths else 0.0
        total = sum(step_lengths)
        checks.append((f"all {len(step_lengths)} consecutive clear centres at theta={theta_deg:g} deg "
                       f"are within the {bound:g} m submitted bound",
                       len(rotated) == 225 and len(step_lengths) == 224 and worst_step <= bound + 1e-9,
                       f"max step {worst_step:.6f} m"))
        checks.append((f"theta={theta_deg:g} deg clear connect path stays within (225-1)*22 m",
                       total <= (len(rotated) - 1) * bound,
                       f"{total:.3f} m <= {(len(rotated) - 1) * bound:.1f} m"))
        over = sum(1 for step in step_lengths if step > bound + 1e-9)
        checks.append((f"no over-long step survives at theta={theta_deg:g} deg",
                       over == 0, f"{over} of {len(step_lengths)} steps over {bound:g} m"))
    return checks, ["clear results are evaluated with the submitted centre against the true (evaluator-side) source",
                    "the emitted 225-centre order is snaked in local core indices before rotation "
                    "(WI-018 repair); rotated headings are generated from the same S without editing the fixture"], _flags()


# ---------------------------------------------------------------- T01-T10


def t01(fx, _ev):
    inputs = fx["inputs"]
    world = inputs["world"]
    p = tuple(inputs["p"])
    exp = fx["expected_evaluator"]
    checks = []
    for i, theta_deg in enumerate(inputs["theta_hat_deg"]):
        ev_label = ev.observation(_ev_source(world), p)
        checks.append((f"endpoint {theta_deg} observation is direction", ev_label == exp["observation"][i], ev_label))
        checks.append((f"endpoint {theta_deg} satisfies the contract (evaluator)",
                       ev.direction_contract_ok(theta_deg, p, world["g"]) == exp["direction_contract_ok"][i],
                       "delta=1 deg"))
        checks.append((f"endpoint {theta_deg} satisfies the contract (candidate)",
                       observe.bearing_consistent(_cand_source(world), p, math.radians(theta_deg)) is True, "delta=1 deg"))
        a1 = q2.build_a1_outer(p, math.radians(theta_deg), max_leaves=FROZEN_LEAVES, max_depth=FROZEN_DEPTH)
        checks.append((f"endpoint {theta_deg}: true position retained in the outer approximation",
                       a1.contains_any(world["g"]), f"leaves={a1.leaf_count}"))
        cell_ok = any(c.contains(world["g"]) and cells.OMNI in c.tags for c in a1.leaves)
        checks.append((f"endpoint {theta_deg}: true type tag (omni) retained on the cell holding the source",
                       cell_ok, "type tag"))
    flags = _flags()
    if not all(ok for name, ok, _d in checks if "retained" in name):
        flags["truth_exclusion"] = 1
    return checks, [], flags


def t02(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    omni = inputs["omni_near"]
    co = inputs["directional_coincidence"]
    omni_world = {"g": omni["g"], "R_c": omni["R_c"], "kind": "omni"}
    co_world = {"g": co["g"], "R_c": co["R_c"], "kind": "directional", "phi_deg": co["phi_deg"]}
    checks = [
        ("omni near observation agrees with the evaluator",
         observe.observation(_cand_source(omni_world), tuple(omni["p"]))
         == ev.observation(_ev_source(omni_world), tuple(omni["p"])) == exp["omni_near_observation"], "near"),
        ("directional coincidence keeps the open O-03 label",
         observe.observation(_cand_source(co_world), tuple(co["p"])) == exp["o03_label"] == observe.O03_OPEN, "O03_OPEN"),
        ("no official answer is invented for the coincidence point",
         observe.O03_OPEN not in exp["o03_allowed_labels"], f"allowed={exp['o03_allowed_labels']}"),
        ("the coincidence point is excluded from coverage evidence",
         all(p != tuple(co["g"]) for p, _lab in scan.visible_lattice_points(scan.P4(), _cand_source(co_world))),
         "P_4 visible set"),
        ("existence is known correctly for the omni near case (positive feedback recorded)",
         observe.observation(_cand_source(omni_world), tuple(omni["p"])) == observe.NEAR, "existence known"),
    ]
    return checks, [f"O-03 stays open: candidate returns {observe.O03_OPEN}, neither allowed label is asserted"], _flags()


def t03(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    cases = [
        ("empty channel", None, tuple(inputs["empty_channel"]["p"])),
        ("outside radius", {"g": inputs["outside_radius"]["g"], "R_c": inputs["outside_radius"]["R_c"], "kind": "omni"},
         tuple(inputs["outside_radius"]["p"])),
        ("directional back", {"g": inputs["directional_back"]["g"], "R_c": inputs["directional_back"]["R_c"],
                              "kind": "directional", "phi_deg": inputs["directional_back"]["phi_deg"]},
         tuple(inputs["directional_back"]["p"])),
    ]
    checks = []
    for i, (name, world, p) in enumerate(cases):
        if world is None:
            checks.append((f"{name}: no source on the channel is no_signal",
                           exp["observations"][i] == observe.NO_SIGNAL, "empty channel"))
            continue
        ev_label = ev.observation(_ev_source(world), p)
        cand_label = observe.observation(_cand_source(world), p)
        checks.append((f"{name}: both sides report no_signal",
                       ev_label == cand_label == exp["observations"][i] == observe.NO_SIGNAL,
                       f"evaluator={ev_label} candidate={cand_label}"))
    checks.append(("Q3 and Q4 no_signal updates differ",
                   observe.no_signal_removes("omni", 500.0) == "position"
                   and observe.no_signal_removes("directional", 500.0) == "orientation_only", "update table"))
    # Legal history: a positive reading at a point where the directional source is
    # front-facing, then a back-side no_signal at a *different* point.  Repeating the
    # no_signal at the already-read point would be a genuine contradiction and the
    # candidate correctly raises a conflict there (covered by T06).
    back_world = {"g": inputs["directional_back"]["g"], "R_c": inputs["directional_back"]["R_c"],
                  "kind": "directional", "phi_deg": inputs["directional_back"]["phi_deg"]}
    store = cand_state.StateStore((1,), {1: cells.DIRECTIONAL})
    front_point = (1500.0, 0.0)
    front_label = observe.observation(_cand_source(back_world), front_point)
    store.record_reading(1, front_point, front_label)
    exists_before = store.channels[1].exists
    store.record_reading(1, (0.0, 0.0), observe.observation(_cand_source(back_world), (0.0, 0.0)))
    checks.append(("front-facing reading is direction and records existence",
                   front_label == observe.DIRECTION and exists_before is True, f"front={front_label}"))
    checks.append(("back-side no_signal does not delete the true position or existence",
                   store.channels[1].exists is exists_before and store.channels[1].exists is True
                   and store.channels[1].cleared is False
                   and observe.back_side_no_signal_deletes_position(back_world) is False,
                   f"exists={store.channels[1].exists}"))
    flags = _flags()
    if store.channels[1].exists is not True:
        flags["truth_exclusion"] = 1
    return checks, [], flags


def t04(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    g = tuple(inputs["g"])
    checks = []
    for i, p in enumerate(inputs["clear_points"]):
        p = tuple(p)
        cand_ok = observe.clear_succeeds(g, p, inputs["u_c"])
        ev_ok = ev.clear_succeeds({"g": list(g), "R_c": 1500}, p)
        expected = exp["clear_results"][i]
        checks.append((f"clear at {p[0]} is {expected}",
                       (cand_ok and expected == "success") or (not cand_ok and expected == "fail"),
                       f"candidate={cand_ok}"))
        checks.append((f"evaluator agrees at {p[0]}", cand_ok == ev_ok, f"{ev_ok}"))
    store = cand_state.StateStore((1,), {1: cells.OMNI})
    first = store.record_clear(1, (0.0, 0.0), True)
    second = store.record_clear(1, (0.0, 0.0), True)
    checks.append(("a second success is recorded but not counted twice",
                   first is True and second is False and store.success_count() == exp["K_after_two_successes"] == 1,
                   f"success_count={store.success_count()}"))
    lg = ledger.Ledger()
    lg.clear((0.0, 0.0), (0.0, 0.0), 1, 1, True)
    lg.clear((0.0, 0.0), (0.0, 0.0), 1, 1, True)
    ev_tot = ev.ledger_totals([{"action": "clear", "x": [0.0, 0.0], "c": 1, "s": 1},
                               {"action": "clear", "x": [0.0, 0.0], "c": 1, "s": 1}])
    checks.append(("candidate ledger counts N_clear once per action and K once per channel",
                   lg.n_clear == exp["N_clear_after_two_successes"] == 2 and lg.k_success == exp["K_after_two_successes"] == 1,
                   f"N_clear={lg.n_clear} K={lg.k_success}"))
    checks.append(("candidate total matches the evaluator totals identity",
                   approx(lg.total, exp["totals_formula_T"]) and approx(lg.total, ev_tot["T"]),
                   f"candidate={lg.total} evaluator={ev_tot['T']} fixture={exp['totals_formula_T']}"))
    flags = _flags()
    flags["ledger_residual"] = abs(lg.total - ev_tot["T"])
    checks.append(("duplicate-success script is flagged inconsistent by the evaluator, not silently accepted",
                   ev_tot["consistent"] == exp["ledger_consistent"] == False,
                   f"inconsistencies={len(ev_tot['inconsistencies'])}"))
    return checks, [f"ledger residual |candidate - evaluator| = {flags['ledger_residual']:.3g}"], flags


def t05(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    g = tuple(inputs["g"])
    checks = [
        ("reference caps match the frozen fixture",
         inputs["leaf_cap"] == exp["leaf_cap"] == 4096 and inputs["depth_cap"] == exp["depth_cap"] == 8,
         f"{inputs['leaf_cap']}/{inputs['depth_cap']}"),
        ("candidate g matches the fixture truth", tuple(exp["candidate_g"]) == g, f"{g}"),
    ]
    # RT4-F2: use OuterState.apply, never the dead build_outer helper
    st = cells.OuterState(max_leaves=inputs["leaf_cap"], max_depth=inputs["depth_cap"])
    st.apply({"kind": "no_signal", "p": (1.0e9, 1.0e9)})
    report = st.report()
    checks.append(("true cell retained at the 4096-leaf cap", st.contains_any(g),
                   f"leaves={st.leaf_count} contains_g={st.contains_any(g)}"))
    checks.append(("leaf cap respected", st.leaf_count <= inputs["leaf_cap"], f"{st.leaf_count}"))
    checks.append(("depth cap respected", report["peak_depth"] <= inputs["depth_cap"], f"{report['peak_depth']}"))
    checks.append(("a coarse cell is kept rather than deleting truth (cap reached)",
                   report["cap_reached"] is True, f"cap_reached={report['cap_reached']}"))
    checks.append(("peak leaf count and peak depth are recorded",
                   report["peak_leaves"] >= st.leaf_count and report["peak_depth"] >= 1,
                   f"peak_leaves={report['peak_leaves']} peak_depth={report['peak_depth']}"))
    for cap in (16, 1):
        small = cells.OuterState(max_leaves=cap, max_depth=inputs["depth_cap"])
        small.apply({"kind": "no_signal", "p": (1.0e9, 1.0e9)})
        checks.append((f"control cap {cap}: true cell still retained", small.contains_any(g),
                       f"leaves={small.leaf_count}"))
    flags = _flags()
    if not st.contains_any(g):
        flags["truth_exclusion"] = 1
    notes = [f"T05 via OuterState.apply: peak_leaves={report['peak_leaves']}, peak_depth={report['peak_depth']}, "
             f"cap_reached={report['cap_reached']}, memory proxy={report['memory_estimate_bytes']} bytes",
             "RT4-F2 honoured: the dead build_outer helper was not called; peak memory is a deterministic proxy, not measured RSS"]
    return checks, notes, flags


def t06(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    rep = inputs["repeat"]
    world = {"g": rep["g"], "R_c": rep["R_c"], "kind": rep["kind"]}
    p = tuple(rep["p"])
    first = observe.observation(_cand_source(world), p)
    second = observe.observation(_cand_source(world), p)
    checks = [
        ("repeated reading on the same uncleared point is identical",
         first == second and exp["repeat_observations_equal"] is True, f"{first}"),
        ("evaluator observation matches the candidate",
         first == ev.observation(_ev_source(world), p), "repeat"),
        ("JSON-equivalent spellings map to one canonical point key",
         observe.canonical_point(tuple(json.loads("[1.00e2, 100.0]")))
         == observe.canonical_point(tuple(inputs["json_equivalent"]["a"]))
         and exp["json_point_keys_equal"] is True,
         "1.00e2 vs 100.0"),
        ("the 0.001 m distinct pair is NOT merged by a tolerance",
         observe.canonical_point(tuple(inputs["nearby_distinct"]["p_a"]))
         != observe.canonical_point(tuple(inputs["nearby_distinct"]["p_b"]))
         and exp["nearby_point_keys_distinct"] is True, "0.001 m"),
    ]
    nd = inputs["nearby_distinct"]
    nworld = {"g": nd["g"], "R_c": nd["R_c"], "kind": nd["kind"]}
    labels = [observe.observation(_cand_source(nworld), tuple(nd["p_a"])),
              observe.observation(_cand_source(nworld), tuple(nd["p_b"]))]
    checks.append(("the two nearby points get the distinct observations the catalog states",
                   labels == exp["nearby_observations"], f"{labels}"))
    checks.append(("evaluator agrees on the distinct observations",
                   labels == [ev.observation(_ev_source(nworld), tuple(nd["p_a"])),
                              ev.observation(_ev_source(nworld), tuple(nd["p_b"]))], "cross-check"))
    store = cand_state.StateStore((1,), {1: cells.OMNI})
    store.record_reading(1, p, first)
    store.record_reading(1, p, second)
    checks.append(("history keeps both identical readings without a conflict", len(store.channels[1].raw_readings) == 2,
                   f"{len(store.channels[1].raw_readings)} records"))
    flags = _flags()
    try:
        store.record_reading(1, p, observe.NO_SIGNAL)
        inconsistent_raised = False
    except cand_state.ConflictError:
        inconsistent_raised = True
    except Exception:
        inconsistent_raised = False
    checks.append(("an inconsistent repeat on the same uncleared point raises a conflict",
                   inconsistent_raised is True, "ConflictError"))
    return checks, [], flags


def t07(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    checks = []
    for name, world in inputs["worlds"].items():
        problem = world["problem"]
        n, nd = world["N"], world["N_dir"]
        ev_ok, _reason = ev.validate_world(problem, n, nd)
        channels = {}
        for i in range(n):
            channels[i + 1] = {"present": True, "directional": i < nd}
            if name == "q3_n10_one_already_cleared" and i == 0:
                channels[i + 1]["cleared"] = True
        cand_ok, _why = observe.validate_world({"question": problem, "channels": channels})
        checks.append((f"{name}: candidate legality matches the frozen and evaluator verdict",
                       cand_ok == ev_ok == exp["validate_world_ok"][name], f"candidate={cand_ok} evaluator={ev_ok}"))
        if exp["validate_world_ok"][name]:
            store = cand_state.StateStore(range(1, n + 1), {c: ("directional" if i < nd else "omni")
                                                            for i, c in enumerate(range(1, n + 1))})
            conflict, reasons = store.check_conflicts()
            checks.append((f"{name}: no false CONFLICT on a legal world", conflict is False, f"{reasons}"))
            if conflict:
                flags_local = True
    checks.append(("initial N still counts an already-cleared source",
                   observe.count_initial_sources({"channels": {1: {"present": True, "cleared": True}}}) == 1
                   and exp["initial_N_counts_cleared_source"] is True, "count_initial_sources"))
    checks.append(("the illegal all-directional world is reject-only and not a performance sample",
                   inputs["illegal_world_is_reject_only"] is True
                   and exp["validate_world_ok"]["q4_n10_dir10_all_directional"] is False, "reject-only"))
    flags = _flags()
    if not all(ok for name, ok, _d in checks if "no false CONFLICT" in name):
        flags["false_completion"] = 1
    return checks, [], flags


def t08(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    checks = []
    # candidate-side ledger for the fully specified script (evaluator cross-check below)
    lg = ledger.Ledger()
    lg.measure((0.0, 0.0), (0.0, 0.0), 1, 1)
    lg.measure((0.0, 0.0), (0.0, 0.0), 2, 1)
    lg.clear((0.0, 0.0), (0.0, 0.0), 1, 2, True)
    ev_tot = ev.ledger_totals(
        [{"action": "measure", "x": [0.0, 0.0], "c": 1},
         {"action": "progress", "kind": "small_progress"},
         {"action": "progress", "kind": "small_progress"},
         {"action": "measure", "x": [0.0, 0.0], "c": 2},
         {"action": "progress", "kind": "repeat_positive_feedback"},
         {"action": "clear", "x": [0.0, 0.0], "c": 1, "s": 1},
         {"action": "cancel_remaining", "c": 1}],
        p0=tuple(inputs["initial_state"]["p"]), b0=inputs["initial_state"]["b"])
    checks.append(("candidate ledger matches the evaluator totals for the injected script",
                   approx(lg.total, exp["ledger_total"]) and approx(lg.total, ev_tot["T"]),
                   f"candidate={lg.total} evaluator={ev_tot['T']} fixture={exp['ledger_total']}"))
    checks.append(("evaluator ledger is consistent; ordinary progress is not charged",
                   ev_tot["consistent"] is True and len(ev_tot["skipped"]) == 4
                   and exp["fully_specified_actions"] == 3,
                   f"skipped={len(ev_tot['skipped'])} non-ledger events (2 small_progress, "
                   f"repeat_positive_feedback, cancel_remaining)"))
    checks.append(("counts match the fixture (N_measure/N_switch/N_clear/K)",
                   lg.n_measure == exp["N_measure"] and lg.n_switch == exp["N_switch"]
                   and lg.n_clear == exp["N_clear"] and lg.k_success == exp["K"],
                   f"{lg.n_measure}/{lg.n_switch}/{lg.n_clear}/{lg.k_success}"))
    # AdaptiveGate: L=2 is not reset by ordinary progress
    gate = queue.AdaptiveGate(limit=inputs["L"])
    gate.on_adaptive_action()
    gate.on_ordinary_feedback()
    gate.on_channel_switch()
    gate.on_region_shrunk()
    checks.append(("L=2 is not reset by ordinary progress / switch / region shrink",
                   gate.count == 1 and gate.must_fallback is False, f"count={gate.count}"))
    gate.on_adaptive_action()
    checks.append(("two consecutive adaptive actions force a fallback", gate.must_fallback is True, "count=2"))
    gate.on_fallback_task_executed()
    checks.append(("executing a fallback task clears the counter", gate.count == 0, f"count={gate.count}"))
    gate.on_adaptive_action()
    gate.on_adaptive_action()
    gate.on_head_task_discharged()
    checks.append(("permanently discharging the head task clears the counter", gate.count == 0, f"count={gate.count}"))
    # one clear list per discovered source, and full trace coverage
    fm = queue.FallbackManager([((0.0, 0.0), 1), ((0.0, 0.0), 2)], max_clear=8)
    fm.register_discovery(1, (0.0, 0.0), 0.0, "direction")
    fm.register_discovery(1, (0.0, 0.0), 0.0, "direction")
    checks.append(("one clear list per discovered source (duplicate discovery ignored)",
                   len(fm.clear_lists) == 1
                   and any(e[0] == "discovery_ignored_duplicate" for e in fm.trace), f"lists={len(fm.clear_lists)}"))
    executed = 0
    while True:
        task = fm.next_task()
        if task is None:
            break
        fm.execute(task)
        executed += 1
    executed += 0
    fm.on_clear_success(1)
    discharged = [e for e in fm.trace if e[0] == "discharged"]
    checks.append(("every fallback task is executed or discharged with a trace",
                   executed >= 1 and len(discharged) >= 1 and fm.created_total <= 2 + 16 * 8,
                   f"executed={executed} discharged={len(discharged)} created={fm.created_total}"))
    checks.append(("a successful clear permanently discharges that channel's tasks",
                   fm.on_clear_success(1) is False and all(t.channel != 1 for t in [fm.next_task()] if t), "success once"))
    cancelled = queue.FallbackManager([((0.0, 0.0), 1), ((0.0, 0.0), 2)], max_clear=8)
    removed = cancelled.cancel_measure_tasks(1, "registered_clear_queue")
    checks.append(("every cancellation carries an explicit logical reason",
                   len(removed) == 1 and any(e[0] == "cancel" and len(e) == 4 for e in cancelled.trace),
                   f"removed={len(removed)}"))
    # RT4-F3: C0 takes no adaptive actions; record it instead of failing the analytic cover
    model_src = (CANDIDATE_DIR / "model.py").read_text(encoding="utf-8")
    tree = ast.parse(model_src)
    gate_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute)
                  and n.attr in ("on_adaptive_action", "must_fallback", "on_ordinary_feedback",
                                 "on_region_shrunk", "on_channel_switch")]
    checks.append(("RT4-F3 recorded: no adaptive-action hook exists in the C0 runner",
                   gate_calls == [], f"{len(gate_calls)} gate calls in model.py"))
    checks.append(("C0 runner never increments the adaptive counter (no adaptive actions taken)",
                   _c0_gate_count() == 0, "gate.count after a full C0 scan+clear"))
    flags = _flags()
    flags["ledger_residual"] = abs(lg.total - ev_tot["T"])
    notes = [f"T08 scored on AdaptiveGate and the clear-list/queue semantics: ledger residual "
             f"|candidate - evaluator| = {flags['ledger_residual']:.3g}",
             "RT4-F3: C0Runner stores a gate but takes no adaptive action; the unused wiring is recorded, "
             "not treated as a C0 analytic-cover failure (SR-002 T08 grade)"]
    return checks, notes, flags


def _c0_gate_count():
    """Run a small C0 scan+clear and return the adaptive counter (must stay 0)."""

    class _Env:
        def __init__(self):
            self.g = (100.0, 0.0)

        def measure(self, p, c):
            if c != 1:
                return {"accepted": True, "observation": observe.NO_SIGNAL}
            src = {"g": self.g, "R": 1500.0, "directional": False, "present": True, "cleared": False}
            lab = observe.observation(src, p)
            out = {"accepted": True, "observation": lab}
            if lab == observe.DIRECTION:
                out["theta_hat"] = math.atan2(self.g[1] - p[1], self.g[0] - p[0])
            return out

        def clear(self, p, c):
            return {"accepted": True, "success": math.hypot(p[0] - self.g[0], p[1] - self.g[1]) <= 20.0}

    runner = model.C0Runner(_Env(), channels=(1, 2))
    runner.run_scan([(0.0, 0.0)], question="Q3")
    runner.run_clears()
    return runner.gate.count


def t09(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    cm = queue.CertificateManager()
    cm.install(float(inputs["old_fallback_certificate_bound"]))
    accepted, reason = cm.offer_crude_remaining(float(inputs["new_crude_bound_after_one_step"]))
    checks = [
        ("a larger newly computed crude bound does not displace the held certificate",
         accepted is False and exp["keep_old_certificate"] is True and reason == "kept_held_certificate",
         f"accepted={accepted} reason={reason}"),
        ("the old certificate bound is retained", approx(cm.bound, exp["old_fallback_certificate_bound"]),
         f"bound={cm.bound}"),
        ("the rejected crude bound is recorded for the trace", len(cm.rejected_crudes) == 1, f"{cm.rejected_crudes}"),
        ("the actual executed cost is charged against the held certificate",
         (cm.charge(30.0), approx(cm.remaining, 70.0))[1], f"remaining={cm.remaining}"),
        ("a newly computed bound larger than the remaining budget is still refused",
         cm.offer_crude_remaining(120.0)[0] is False and approx(cm.remaining, 70.0), f"remaining={cm.remaining}"),
        ("a tighter crude bound is accepted", cm.offer_crude_remaining(40.0)[0] is True and approx(cm.remaining, 40.0),
         f"remaining={cm.remaining}"),
    ]
    return checks, [f"old bound {exp['old_fallback_certificate_bound']}, newer crude bound "
                    f"{exp['new_crude_bound_after_one_step']}: non-monotone case handled"], _flags()


def t10(fx, _ev):
    inputs = fx["inputs"]
    exp = fx["expected_evaluator"]
    measure = {"action": "measure", "x": list(inputs["measure"]["x"]), "c": inputs["measure"]["c"]}
    p0 = tuple(inputs["initial_state"]["p"])
    b0 = inputs["initial_state"]["b"]
    cand_dt = ledger.delta_t(p0, tuple(measure["x"]), is_measure=True, c_k=measure["c"], b_prev=b0)
    ev_dt = ev.delta_t(p0, b0, measure)
    checks = [
        ("candidate cost of one same-channel measure is 5", approx(cand_dt, exp["measure_delta_t"]) == True,
         f"{cand_dt}"),
        ("evaluator recomputation agrees", approx(ev_dt, cand_dt), f"evaluator={ev_dt}"),
    ]
    r_exact, r_short = inputs["remainders"]
    checks.append(("remainder exactly 5 accepts the measure",
                   ledger.budget_accepts(r_exact, cand_dt) == exp["remainder_5_sufficient"] == True,
                   f"remainder={r_exact}"))
    checks.append(("remainder 5 - eps_d rejects the measure",
                   ledger.budget_accepts(r_short, cand_dt) == exp["remainder_5_minus_eps_sufficient"] == False,
                   f"remainder={r_short}"))
    checks.append(("the decision uses the all-feedback worst case, not a favourable realisation",
                   ledger.all_feedback_accepts(5.0, [5.0, 6.0]) is False
                   and ledger.worst_case_feedback([5.0, 6.0]) == 6.0, "worst case 6 > 5"))
    checks.append(("accepting the worst case still succeeds when the certificate allows it",
                   ledger.all_feedback_accepts(6.0, [5.0, 6.0]) is True, "worst case 6 <= 6"))
    checks.append(("the real-time gate stays UNKNOWN without evidenced duration bounds",
                   ledger.realtime_check(1200.0, 100)[0] == ledger.REALTIME_UNCERTIFIED, "REALTIME_UNCERTIFIED"))
    flags = _flags()
    flags["ledger_residual"] = abs(cand_dt - ev_dt)
    return checks, [f"ledger residual |candidate - evaluator| = {flags['ledger_residual']:.3g}"], flags


CHECKS = {
    "G01": g01, "G02": g02, "G03": g03, "G04": g04, "G05": g05, "G06": g06, "G07": g07, "G08": g08,
    "G09": g09, "G10": g10, "G11": g11, "G12": g12, "G13": g13, "G14": g14, "G15": g15, "G16": g16,
    "T01": t01, "T02": t02, "T03": t03, "T04": t04, "T05": t05, "T06": t06, "T07": t07, "T08": t08,
    "T09": t09, "T10": t10,
}

ITEM_ORDER = ["G%02d" % i for i in range(1, 17)] + ["T%02d" % i for i in range(1, 11)]
