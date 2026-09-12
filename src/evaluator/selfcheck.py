"""Fixture loading and ``evaluator_now`` self-check for EXP-002 (P1-A).

The frozen fixtures under ``tests/p1a/fixtures/`` carry, for every ID, the analytic/plan expectation
in ``expected_evaluator``. This module evaluates the *evaluator side only* (``phase_checks`` ==
``evaluator_now``) and compares against those frozen expectations. It never touches a candidate and
never runs the 4 min 20 s G/T candidate property suite.

``candidate_later_checks`` are listed for the report and are intentionally **not** executed.
"""

from __future__ import annotations

import hashlib
import json
import math
import os

from . import halfplane, predicates
from .predicates import (
    BOUNDED,
    O03_OPEN,
    canonical_point_key,
    c_in_member,
    clear_centre_formula_point,
    clear_centres,
    direction_contract_ok,
    dist,
    in_disk,
    observation,
    p3_points,
    p4_points,
    validate_world,
    visible_scan_points,
    visibility,
)

FIXTURE_IDS = ["G%02d" % i for i in range(1, 17)] + ["T%02d" % i for i in range(1, 11)]
MANIFEST_NAME = "manifest.json"


def repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir, os.pardir))


def default_fixtures_dir() -> str:
    return os.path.join(repo_root(), "tests", "p1a", "fixtures")


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_fixture(fixtures_dir: str, fixture_id: str) -> dict:
    with open(os.path.join(fixtures_dir, fixture_id + ".json"), "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_all(fixtures_dir: str | None = None) -> dict:
    fixtures_dir = fixtures_dir or default_fixtures_dir()
    return {fid: load_fixture(fixtures_dir, fid) for fid in FIXTURE_IDS}


def load_manifest(fixtures_dir: str | None = None) -> dict:
    fixtures_dir = fixtures_dir or default_fixtures_dir()
    with open(os.path.join(fixtures_dir, MANIFEST_NAME), "r", encoding="utf-8") as handle:
        return json.load(handle)


def _pool_c_in(S, theta_hat_deg, points):
    return [c_in_member(S, theta_hat_deg, p) for p in points]


def _clear_label(ok: bool) -> str:
    return "success" if ok else "fail"


def run_evaluator_now(fixture: dict) -> dict:
    """Recompute every ``evaluator_now`` observable for one fixture."""
    fid = fixture["id"]
    inputs = fixture["inputs"]

    if fid == "G01":
        hps = halfplane.parse_halfplanes(inputs["half_planes"])
        return {"halfplane_state": halfplane.halfplane_state(hps)}

    if fid == "G02":
        hps = halfplane.parse_halfplanes(inputs["half_planes"])
        state = halfplane.halfplane_state(hps)
        return {"halfplane_state": state, "finite_diameter_reported": state == BOUNDED}

    if fid == "G03":
        hps = halfplane.parse_halfplanes(inputs["half_planes"])
        return {
            "halfplane_state": halfplane.halfplane_state(hps),
            "vertices": [[float(v[0]), float(v[1])] for v in halfplane.halfplane_vertices(hps)],
            "diameter": halfplane.halfplane_diameter(hps),
            "covering_circle": {
                "center": halfplane.halfplane_covering_circle(hps)["center"],
                "radius": halfplane.halfplane_covering_circle(hps)["radius"],
            },
        }

    if fid == "G04":
        hps = halfplane.parse_halfplanes(inputs["half_planes"])
        return {
            "halfplane_state": halfplane.halfplane_state(hps),
            "vertices": [[float(v[0]), float(v[1])] for v in halfplane.halfplane_vertices(hps)],
            "diameter": halfplane.halfplane_diameter(hps),
            "covering_circle": {
                "center": halfplane.halfplane_covering_circle(hps)["center"],
                "radius": halfplane.halfplane_covering_circle(hps)["radius"],
            },
        }

    if fid == "G05":
        hps = halfplane.parse_halfplanes(inputs["half_planes"])
        circle = halfplane.halfplane_covering_circle(hps)
        return {
            "halfplane_state": halfplane.halfplane_state(hps),
            "vertices": [[float(v[0]), float(v[1])] for v in halfplane.halfplane_vertices(hps)],
            "diameter": halfplane.halfplane_diameter(hps),
            "farthest_pair_midpoint": circle["center"],
            "max_vertex_distance_to_midpoint": circle["max_vertex_distance_to_midpoint"],
            "min_enclosing_radius": halfplane.halfplane_min_enclosing_radius(hps),
        }

    if fid == "G06":
        vertices = inputs["vertices"]
        pairs = [
            dist(vertices[0], vertices[1]),
            dist(vertices[0], vertices[2]),
            dist(vertices[1], vertices[2]),
        ]
        center, radius = predicates.circumcircle(vertices[0], vertices[1], vertices[2])
        return {
            "diameter": max(pairs),
            "circumradius": radius,
            "circumcenter": [center[0], center[1]],
            "half_radius_covers_vertices": all(
                dist(center, v) <= 0.5 + 1e-12 for v in vertices
            ),
        }

    if fid == "G07":
        strip = halfplane.parse_halfplanes(inputs["g07a_parallel_strip"]["half_planes"])
        return {
            "g07a_state": halfplane.halfplane_state(strip),
            "g07b_state": halfplane.near_collinear_wedges_state(inputs["g07b_near_collinear"]),
        }

    if fid == "G08":
        a = predicates.wrap_deg(inputs["A_deg"])
        b = predicates.wrap_deg(inputs["B_deg"])
        c = predicates.wrap_deg(inputs["C_deg"])
        return {
            "A_normalized_deg": a,
            "B_normalized_deg": b,
            "ab_internally_equivalent": a == b,
            "C_normalized_deg": c,
        }

    if fid == "G09":
        S = inputs["S"]
        theta = inputs["theta_hat_deg"]
        worlds = [
            {"g": w["g"], "R_c": inputs["R_c"], "kind": predicates.OMNI}
            for w in inputs["worlds"]
        ]
        return {
            "worlds_in_D": [in_disk(w["g"]) for w in inputs["worlds"]],
            "first_observation": [observation(w, S) for w in worlds],
            "c_in_membership_pool": _pool_c_in(S, theta, inputs["submitted_pool"]),
            "c_in_membership_lateral": c_in_member(S, theta, inputs["extra_points"]["lateral"]),
            "c_in_membership_forward": c_in_member(S, theta, inputs["extra_points"]["forward"]),
        }

    if fid == "G10":
        S = inputs["S"]
        g = inputs["g"]
        return {
            "g_in_D": in_disk(g),
            "observation": [
                observation({"g": g, "R_c": w["R_c"]}, S) for w in inputs["worlds"]
            ],
            "direction_contract_ok": [
                direction_contract_ok(w["theta_hat_deg"], S, g) for w in inputs["worlds"]
            ],
        }

    if fid == "G11":
        S = inputs["first_observation"]["S"]
        theta = inputs["first_observation"]["theta_hat_deg"]
        comparators = inputs["comparators"]
        return {
            "c_in_membership_pool": _pool_c_in(S, theta, comparators["pool_6"]),
            "c_in_membership_lateral": c_in_member(S, theta, comparators["lateral"]),
            "c_in_membership_forward": c_in_member(S, theta, comparators["forward"]),
        }

    if fid == "G12":
        S = inputs["S"]
        theta = inputs["theta_hat_deg"]
        deserialized = json.loads(inputs["serialization"]["raw"])
        return {
            "c_in_original": c_in_member(S, theta, inputs["p"]),
            "c_in_deserialized": c_in_member(S, theta, deserialized),
            "deserialized_point": [float(deserialized[0]), float(deserialized[1])],
        }

    if fid == "G13":
        S = inputs["S"]
        return {
            "observation": [
                observation({"g": w["g"], "R_c": inputs["R_c"]}, S)
                for w in inputs["worlds"]
            ]
        }

    if fid == "G14":
        source = {
            "g": inputs["g"],
            "R_c": inputs["R_c"],
            "kind": predicates.DIRECTIONAL,
            "phi_deg": inputs["phi_deg"],
        }
        return {
            "visible": visibility(
                predicates.DIRECTIONAL, inputs["phi_deg"], inputs["S"], inputs["g"]
            ),
            "observation": observation(source, inputs["S"]),
            "world_label": "component_world",
        }

    if fid == "G15":
        p3 = p3_points()
        p4 = p4_points()
        p3_nonempty = {}
        p4_nonempty = {}
        for world in inputs["worlds"]:
            if world.get("kind", predicates.DIRECTIONAL) != predicates.OMNI:
                continue
            source = {"g": world["g"], "R_c": world["R_c"], "kind": predicates.OMNI}
            p3_nonempty[world["name"]] = len(visible_scan_points(p3, source)) > 0
            p4_nonempty[world["name"]] = len(visible_scan_points(p4, source)) > 0

        def heading_observation(name):
            world = [w for w in inputs["worlds"] if w["name"] == name][0]
            source = {
                "g": world["g"],
                "R_c": world["R_c"],
                "kind": predicates.DIRECTIONAL,
                "phi_deg": world["phi_deg"],
            }
            return observation(source, world["chosen_p"])

        coincidence = [w for w in inputs["worlds"] if w["name"] == "coincidence_o03"][0]
        coincidence_source = {
            "g": coincidence["g"],
            "R_c": coincidence["R_c"],
            "kind": predicates.DIRECTIONAL,
            "phi_deg": coincidence["phi_deg"],
        }
        return {
            "P_3_count": len(p3),
            "P_4_count": len(p4),
            "p3_visible_nonempty": p3_nonempty,
            "p4_visible_nonempty": p4_nonempty,
            "heading_boundary_observation": heading_observation("heading_boundary"),
            "heading_boundary_eps_far_observation": heading_observation(
                "heading_boundary_eps_far"
            ),
            "heading_boundary_eps_near_observation": heading_observation(
                "heading_boundary_eps_near"
            ),
            "coincidence_label": observation(coincidence_source, coincidence["g"]),
            "coincidence_used_as_coverage_evidence": False,
        }

    if fid == "G16":
        S = inputs["S"]
        theta = inputs["theta_deg"]
        centres = clear_centres(S, theta)
        match = True
        index = 0
        for i in range(75):
            for j in range(3):
                expected_point = clear_centre_formula_point(S, theta, i, j)
                if dist(expected_point, centres[index]) > 1e-9:
                    match = False
                index += 1
        unique = len({(round(c[0], 9), round(c[1], 9)) for c in centres})
        corner = inputs["source_placements"]["corner"]
        nearest = min(centres, key=lambda q: dist(q, corner))
        clear_results = []
        for key in ("distance_20_minus_eps", "distance_20", "distance_20_plus_eps"):
            submitted, source_g = inputs["source_placements"][key]
            clear_results.append(
                _clear_label(predicates.clear_succeeds({"g": source_g, "R_c": 1500.0}, submitted))
            )
        adjacent = inputs["adjacent_centres"]
        nominal = dist(adjacent[0], adjacent[1])
        return {
            "centre_count": len(centres),
            "centres_unique": unique,
            "centres_match_formula": match,
            "corner_nearest_centre": [nearest[0], nearest[1]],
            "corner_centre_distance": dist(nearest, corner),
            "submitted_offset_norm": math.hypot(
                inputs["submitted_centre_with_1m_error"]["offset"][0],
                inputs["submitted_centre_with_1m_error"]["offset"][1],
            ),
            "clear_results": clear_results,
            "adjacent_nominal": nominal,
            "adjacent_bound_with_1m_errors": nominal + 1.0 + 1.0,
        }

    if fid == "T01":
        world = inputs["world"]
        source = {"g": world["g"], "R_c": world["R_c"], "kind": world["kind"]}
        p = inputs["p"]
        return {
            "observation": [observation(source, p) for _ in inputs["theta_hat_deg"]],
            "direction_contract_ok": [
                direction_contract_ok(theta, p, world["g"])
                for theta in inputs["theta_hat_deg"]
            ],
        }

    if fid == "T02":
        near = inputs["omni_near"]
        coinc = inputs["directional_coincidence"]
        return {
            "omni_near_observation": observation(
                {"g": near["g"], "R_c": near["R_c"], "kind": near["kind"]}, near["p"]
            ),
            "o03_label": observation(
                {
                    "g": coinc["g"],
                    "R_c": coinc["R_c"],
                    "kind": coinc["kind"],
                    "phi_deg": coinc["phi_deg"],
                },
                coinc["p"],
            ),
            "o03_allowed_labels": [predicates.NEAR, predicates.NO_SIGNAL],
        }

    if fid == "T03":
        empty = inputs["empty_channel"]
        outside = inputs["outside_radius"]
        back = inputs["directional_back"]
        return {
            "observations": [
                observation({"g": [0.0, 0.0], "R_c": 1500.0, "exists": False}, empty["p"]),
                observation(
                    {"g": outside["g"], "R_c": outside["R_c"], "kind": outside["kind"]},
                    outside["p"],
                ),
                observation(
                    {
                        "g": back["g"],
                        "R_c": back["R_c"],
                        "kind": back["kind"],
                        "phi_deg": back["phi_deg"],
                    },
                    back["p"],
                ),
            ]
        }

    if fid == "T04":
        results = [
            _clear_label(predicates.clear_succeeds({"g": inputs["g"], "R_c": 1500.0}, p))
            for p in inputs["clear_points"]
        ]
        ledger = predicates.ledger_totals(
            inputs["two_success_script"], p0=(0.0, 0.0), b0=1
        )
        return {
            "clear_results": results,
            "K_after_two_successes": ledger["K"],
            "N_clear_after_two_successes": ledger["N_clear"],
            # TR-012 F7: the injected duplicate-success script is not consistent with plan §2, so
            # its totals identity must not be presented as a valid ledger.
            "ledger_consistent": ledger["consistent"],
            "ledger_inconsistency_count": len(ledger["inconsistencies"]),
            "sum_delta_t": ledger["sum_delta_t"],
            "totals_formula_T": ledger["T"],
        }

    if fid == "T05":
        return {
            "candidate_g": inputs["g"],
            "leaf_cap": inputs["leaf_cap"],
            "depth_cap": inputs["depth_cap"],
        }

    if fid == "T06":
        repeat = inputs["repeat"]
        source = {"g": repeat["g"], "R_c": repeat["R_c"], "kind": repeat["kind"]}
        first = observation(source, repeat["p"])
        second = observation(source, repeat["p"])
        json_a = inputs["json_equivalent"]["a"]
        json_b = json.loads(inputs["json_equivalent"]["b_raw"])
        nearby = inputs["nearby_distinct"]
        nearby_source = {
            "g": nearby["g"],
            "R_c": nearby["R_c"],
            "kind": nearby["kind"],
        }
        return {
            "repeat_observations_equal": first == second,
            "json_point_keys_equal": canonical_point_key(json_a)
            == canonical_point_key(json_b),
            "nearby_point_keys_distinct": canonical_point_key(nearby["p_a"])
            != canonical_point_key(nearby["p_b"]),
            "nearby_observations": [
                observation(nearby_source, nearby["p_a"]),
                observation(nearby_source, nearby["p_b"]),
            ],
        }

    if fid == "T07":
        results = {}
        for name, world in inputs["worlds"].items():
            ok, _reason = validate_world(world["problem"], world["N"], world["N_dir"])
            results[name] = ok
        return {
            "validate_world_ok": results,
            "initial_N_counts_cleared_source": results["q3_n10_one_already_cleared"],
        }

    if fid == "T08":
        ledger = predicates.ledger_totals(
            inputs["script"],
            p0=inputs["initial_state"]["p"],
            b0=inputs["initial_state"]["b"],
        )
        fully_specified = sum(
            1 for e in inputs["script"] if e.get("action") in ("move", "measure", "clear")
        )
        return {
            "ledger_total": ledger["T"],
            "K": ledger["K"],
            "fully_specified_actions": fully_specified,
            "N_measure": ledger["N_measure"],
            "N_switch": ledger["N_switch"],
            "N_clear": ledger["N_clear"],
            "L_move_m": ledger["L_move_m"],
            # TR-012 F7: a well-formed injected script must satisfy the plan §2 totals identity.
            "ledger_consistent": ledger["consistent"],
            "sum_delta_t": ledger["sum_delta_t"],
        }

    if fid == "T09":
        return {
            "old_fallback_certificate_bound": inputs["old_fallback_certificate_bound"],
            "new_crude_bound_after_one_step": inputs["new_crude_bound_after_one_step"],
            "keep_old_certificate": True,
        }

    if fid == "T10":
        initial = inputs["initial_state"]
        measure = inputs["measure"]
        dt = predicates.delta_t(
            initial["p"],
            initial["b"],
            {"action": "measure", "x": measure["x"], "c": measure["c"]},
        )
        remainders = inputs["remainders"]
        return {
            "measure_delta_t": dt,
            "remainder_5_sufficient": remainders[0] >= dt,
            "remainder_5_minus_eps_sufficient": remainders[1] >= dt,
        }

    raise KeyError("no evaluator_now recipe for fixture %s" % fid)


def _compare_numbers(expected, actual, tol: float, path: str):
    """Numeric comparison that never silently accepts a non-finite actual value (TR-012 F2).

    ``abs(1.0 - nan) > tol`` is ``False``, so a plain tolerance comparison returned no problem for
    ``compare(1.0, float('nan'))``. Non-finite values are now compared by kind and sign: NaN only
    matches NaN, an infinity only matches the same infinity, and a finite expectation never matches
    a non-finite actual value.
    """
    exp = float(expected)
    act = float(actual)
    if math.isnan(exp) or math.isnan(act):
        if math.isnan(exp) and math.isnan(act):
            return []
        return ["%s: expected %r, got %r (NaN vs non-NaN)" % (path, expected, actual)]
    if math.isinf(exp) or math.isinf(act):
        if exp == act:
            return []
        return ["%s: expected %r, got %r (non-finite mismatch)" % (path, expected, actual)]
    if abs(exp - act) > tol:
        return ["%s: expected %r, got %r" % (path, expected, actual)]
    return []


def compare(expected, actual, tol: float = 1e-9, path: str = "root"):
    """Recursive comparison returning a list of human-readable mismatch strings."""
    problems = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return ["%s: expected mapping, got %r" % (path, actual)]
        for key, value in expected.items():
            if key not in actual:
                problems.append("%s.%s: missing in actual" % (path, key))
            else:
                problems.extend(compare(value, actual[key], tol, "%s.%s" % (path, key)))
        return problems
    if isinstance(expected, (list, tuple)):
        if not isinstance(actual, (list, tuple)) or len(expected) != len(actual):
            return [
                "%s: expected %d elements, got %r" % (path, len(expected), actual)
            ]
        for i, (exp, act) in enumerate(zip(expected, actual)):
            problems.extend(compare(exp, act, tol, "%s[%d]" % (path, i)))
        return problems
    if isinstance(expected, bool) or isinstance(actual, bool):
        if expected != actual:
            problems.append("%s: expected %r, got %r" % (path, expected, actual))
        return problems
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return _compare_numbers(expected, actual, tol, path)
    if isinstance(expected, (int, float)) != isinstance(actual, (int, float)):
        # a non-numeric actual (e.g. a string) may hide a non-finite or out-of-contract value
        problems.append("%s: expected %r, got %r (type mismatch)" % (path, expected, actual))
        return problems
    if expected != actual:
        problems.append("%s: expected %r, got %r" % (path, expected, actual))
    return problems


def check_fixture(fixture: dict, tol: float = 1e-9) -> dict:
    """Run one fixture's ``evaluator_now`` checks and compare with the expectation."""
    actual = run_evaluator_now(fixture)
    expected = fixture["expected_evaluator"]
    mismatches = compare(expected, actual, tol)
    return {
        "id": fixture["id"],
        "phase_checks": list(fixture.get("phase_checks", [])),
        "candidate_later_checks": list(fixture.get("candidate_later_checks", [])),
        "expected": expected,
        "actual": actual,
        "mismatches": mismatches,
        "ok": not mismatches,
    }


def check_all(fixtures_dir: str | None = None, tol: float = 1e-9):
    fixtures = load_all(fixtures_dir)
    return [check_fixture(fixtures[fid], tol) for fid in FIXTURE_IDS]


def check_manifest(fixtures_dir: str | None = None):
    """Verify every ``manifest.json`` SHA-256 against the fixture file bytes."""
    fixtures_dir = fixtures_dir or default_fixtures_dir()
    manifest = load_manifest(fixtures_dir)
    report = {}
    for name, recorded in manifest["files"].items():
        path = os.path.join(fixtures_dir, name)
        report[name] = {
            "recorded": recorded,
            "measured": sha256_file(path),
            "ok": sha256_file(path) == recorded,
        }
    return report
