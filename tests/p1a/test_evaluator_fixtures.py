"""EXP-002 P1-A ``evaluator_now`` self-check (WI-014).

This suite exercises the *evaluator side only*: for every frozen fixture ID it recomputes the
plan-derived predicate outputs and compares them with the fixture's frozen ``expected_evaluator``.
It deliberately does **not** run the G/T candidate property suite, does not import
``src/candidate/``, does not need a candidate, and does not conclude ``P1A_PROPERTIES_*``.

Run (WI-014 Required Review Command 11)::

    PYTHONPATH=src python -m unittest discover -s tests/p1a -v
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
SRC = os.path.join(REPO_ROOT, "src")
if SRC not in sys.path:  # convenience fallback; the WI command sets PYTHONPATH=src explicitly
    sys.path.insert(0, SRC)

from evaluator import halfplane, predicates, selfcheck  # noqa: E402

FIXTURES_DIR = os.path.join(HERE, "fixtures")


class FixtureInventoryTest(unittest.TestCase):
    def test_exactly_the_26_fixture_files_plus_manifest_exist(self):
        present = sorted(os.listdir(FIXTURES_DIR))
        expected = sorted(
            [fid + ".json" for fid in selfcheck.FIXTURE_IDS] + [selfcheck.MANIFEST_NAME]
        )
        self.assertEqual(present, expected)

    def test_manifest_lists_every_fixture_once(self):
        manifest = selfcheck.load_manifest(FIXTURES_DIR)
        self.assertEqual(
            sorted(manifest["files"].keys()),
            sorted(fid + ".json" for fid in selfcheck.FIXTURE_IDS),
        )

    def test_manifest_sha256_matches_file_bytes(self):
        report = selfcheck.check_manifest(FIXTURES_DIR)
        self.assertEqual(len(report), 26)
        bad = {name: info for name, info in report.items() if not info["ok"]}
        self.assertEqual(bad, {}, "manifest hash mismatches: %r" % (bad,))


class FixtureSchemaTest(unittest.TestCase):
    def test_schema_and_id(self):
        for fid in selfcheck.FIXTURE_IDS:
            with self.subTest(fixture=fid):
                fixture = selfcheck.load_fixture(FIXTURES_DIR, fid)
                self.assertEqual(fixture["id"], fid)
                for key in (
                    "phase_checks",
                    "candidate_later_checks",
                    "inputs",
                    "truth",
                    "expected_evaluator",
                ):
                    self.assertIn(key, fixture)
                self.assertIn("evaluator_now", fixture["phase_checks"])
                self.assertTrue(fixture["candidate_later_checks"])
                self.assertTrue(fixture["expected_evaluator"])
                self.assertTrue(fixture["truth"])

    def test_catalog_numbers_are_exactly_g01_g16_and_t01_t10(self):
        ids = [fid for fid in selfcheck.FIXTURE_IDS]
        self.assertEqual(ids, ["G%02d" % i for i in range(1, 17)] + ["T%02d" % i for i in range(1, 11)])


class EvaluatorNowTest(unittest.TestCase):
    def test_every_fixture_evaluator_now_matches_expected(self):
        for result in selfcheck.check_all(FIXTURES_DIR):
            with self.subTest(fixture=result["id"]):
                self.assertEqual(
                    result["mismatches"], [], "%s mismatch: %r" % (result["id"], result["mismatches"])
                )
                self.assertTrue(result["ok"])

    def test_halfplane_state_labels_are_in_the_closed_set(self):
        allowed = {
            predicates.CONFLICT,
            predicates.UNBOUNDED,
            predicates.BOUNDED,
            predicates.NUMERICAL_UNCERTAIN,
        }
        for fid in ("G01", "G02", "G03", "G04", "G05", "G07"):
            with self.subTest(fixture=fid):
                fixture = selfcheck.load_fixture(FIXTURES_DIR, fid)
                actual = selfcheck.run_evaluator_now(fixture)
                for key, value in actual.items():
                    if key.endswith("_state"):
                        self.assertIn(value, allowed)

    def test_o03_branch_never_commits_to_an_official_answer(self):
        fixture = selfcheck.load_fixture(FIXTURES_DIR, "T02")
        actual = selfcheck.run_evaluator_now(fixture)
        self.assertEqual(actual["o03_label"], predicates.O03_OPEN)
        self.assertIn(predicates.NEAR, actual["o03_allowed_labels"])
        self.assertIn(predicates.NO_SIGNAL, actual["o03_allowed_labels"])

    def test_observation_labels_are_in_the_closed_set(self):
        allowed = {predicates.NEAR, predicates.DIRECTION, predicates.NO_SIGNAL, predicates.O03_OPEN}
        for fid in ("G09", "G10", "G13", "G14", "T01", "T02", "T03"):
            with self.subTest(fixture=fid):
                actual = selfcheck.run_evaluator_now(selfcheck.load_fixture(FIXTURES_DIR, fid))
                for key, value in actual.items():
                    if "observation" not in key:
                        continue
                    values = value if isinstance(value, list) else [value]
                    for item in values:
                        self.assertIn(item, allowed)


class IndependenceTest(unittest.TestCase):
    def test_evaluator_does_not_import_candidate_code(self):
        import ast

        package_dir = os.path.dirname(os.path.abspath(predicates.__file__))
        sources = sorted(
            os.path.join(package_dir, name)
            for name in os.listdir(package_dir)
            if name.endswith(".py")
        )
        self.assertTrue(sources)
        for path in sources:
            with self.subTest(module=os.path.basename(path)):
                with open(path, "r", encoding="utf-8") as handle:
                    tree = ast.parse(handle.read(), filename=path)
                imported = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.append(node.module)
                for name in imported:
                    self.assertNotIn("candidate", name, "candidate import in %s" % path)

    def test_no_candidate_directory_is_required_or_created(self):
        candidate_dir = os.path.join(REPO_ROOT, "src", "candidate")
        self.assertFalse(
            os.path.isdir(candidate_dir),
            "src/candidate/ must not exist during WI-014 (evaluator author independence bind)",
        )


class Tr012RegressionTest(unittest.TestCase):
    """Focused regressions for the five bounded TR-012 repairs (F1, F2, F5, F6, F7).

    These exercise the evaluator only; they are not the G/T candidate property suite and they do not
    establish P1-A property passage.
    """

    # --- F1: the closed directional half-plane boundary must be visible ------------------------

    def test_closed_cardinal_boundary_is_visible(self):
        # TR-012 F1 reproduction: exact normal (0,1) and sensor on the line y = 700 (dot product 0).
        for p in ([0, 700], [100, 700], [1400, 700], [2000, 700]):
            with self.subTest(sensor=p):
                self.assertEqual(
                    predicates.observation(
                        {"g": [700, 700], "R_c": 1500, "kind": "directional", "phi_deg": 90},
                        p,
                    ),
                    "direction",
                )

    def test_cardinal_normals_are_exact(self):
        for phi, expected in ((0, (1, 0)), (90, (0, 1)), (180, (-1, 0)), (270, (0, -1)), (-90, (0, -1))):
            with self.subTest(phi=phi):
                nx, ny, exact = predicates.normal_vector(phi)
                self.assertTrue(exact)
                self.assertEqual((int(nx), int(ny)), expected)

    def test_just_outside_the_closed_boundary_is_not_visible(self):
        # phi=90 -> normal (0,1): visible iff p_y >= 700. One metre is ~0.08 deg at 700 m, far
        # above float noise, so these are genuine sign decisions and not boundary ties.
        self.assertFalse(predicates.visibility("directional", 90, [0, 699], [700, 700]))
        self.assertTrue(predicates.visibility("directional", 90, [0, 700], [700, 700]))
        self.assertTrue(predicates.visibility("directional", 90, [0, 701], [700, 700]))
        # phi=270 -> normal (0,-1): the opposite closed half-plane.
        self.assertTrue(predicates.visibility("directional", 270, [0, 699], [700, 700]))
        self.assertTrue(predicates.visibility("directional", 270, [0, 700], [700, 700]))
        self.assertFalse(predicates.visibility("directional", 270, [0, 701], [700, 700]))

    def test_generic_angle_uses_the_equivalent_closed_predicate(self):
        # p=(0,0), g=(1,1) has arg(g-p)=45 deg, so n(phi).(p-g) >= 0 iff |wrap(phi-45)| >= 90.
        for phi, visible in (
            (0, False), (45, False), (134, False), (135, True), (136, True),
            (-45, True), (-46, True), (225, True), (270, True),
        ):
            with self.subTest(phi=phi):
                self.assertEqual(predicates.visibility("directional", phi, [0, 0], [1, 1]), visible)

    def test_generic_path_agrees_with_cos_sin_dot_reference(self):
        # Independent reference: the classical dot product with math.cos/math.sin. Away from the
        # closed boundary (>= 0.5 deg) the two must agree; the tolerance band is only reported here.
        import math as _math

        for phi in (0.0, 10.0, 40.0, 80.0, 120.0, 170.0, 200.0, 260.0, 300.0, 350.0):
            for g in ([1, 1], [3, -2], [-5, 4], [0, 7]):
                p = [0, 0]
                dot = _math.cos(_math.radians(phi)) * (p[0] - g[0]) + _math.sin(
                    _math.radians(phi)
                ) * (p[1] - g[1])
                scale = _math.hypot(g[0], g[1])
                if abs(dot) / max(scale, 1e-12) < _math.sin(_math.radians(0.5)):
                    continue  # too close to the boundary for a float dot reference
                with self.subTest(phi=phi, g=g):
                    self.assertEqual(
                        predicates.visibility("directional", phi, p, g), dot > 0.0
                    )

    def test_g14_back_side_remains_no_signal(self):
        self.assertEqual(
            predicates.observation(
                {"g": [1000, 0], "R_c": 1500, "kind": "directional", "phi_deg": 0}, [0, 0]
            ),
            "no_signal",
        )

    # --- F2: non-finite values must never pass a finite comparison -----------------------------

    def test_nan_never_matches_a_finite_expectation(self):
        self.assertTrue(selfcheck.compare(1.0, float("nan")))
        self.assertTrue(selfcheck.compare(0.0, float("nan")))
        self.assertTrue(selfcheck.compare([1.0, 2.0], [1.0, float("nan")]))
        self.assertTrue(selfcheck.compare({"r": 1.0}, {"r": float("nan")}))

    def test_infinity_never_matches_a_finite_expectation(self):
        self.assertTrue(selfcheck.compare(1.0, float("inf")))
        self.assertTrue(selfcheck.compare(1.0, float("-inf")))

    def test_non_finite_matches_only_the_same_kind(self):
        self.assertEqual(selfcheck.compare(float("nan"), float("nan")), [])
        self.assertEqual(selfcheck.compare(float("inf"), float("inf")), [])
        self.assertEqual(selfcheck.compare(float("-inf"), float("-inf")), [])
        self.assertTrue(selfcheck.compare(float("inf"), float("-inf")))

    # --- F5: fixture JSON bytes must be protected from checkout conversion ---------------------

    def test_scoped_gitattributes_protects_fixture_json_bytes(self):
        attributes = os.path.join(HERE, ".gitattributes")
        self.assertTrue(os.path.isfile(attributes), "tests/p1a/.gitattributes must exist")
        with open(attributes, "r", encoding="utf-8") as handle:
            text = handle.read()
        rules = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        self.assertIn("fixtures/*.json -text", rules)

    def test_no_fixture_file_contains_crlf_on_disk(self):
        for name in sorted(os.listdir(FIXTURES_DIR)):
            with self.subTest(fixture=name):
                with open(os.path.join(FIXTURES_DIR, name), "rb") as handle:
                    self.assertNotIn(b"\r\n", handle.read())

    # --- F6: the misleading partial A_1 helper must not be exposed -----------------------------

    def test_partial_a1_helper_is_not_exposed(self):
        self.assertFalse(
            hasattr(predicates, "in_a1"),
            "the partial A_1 helper was removed by TR-012 F6; it must not return as a full A1 oracle",
        )

    # --- F7: an inconsistent duplicate-success ledger must be flagged, not silently accepted ---

    def test_duplicate_success_ledger_is_flagged(self):
        fixture = selfcheck.load_fixture(FIXTURES_DIR, "T04")
        script = fixture["inputs"]["two_success_script"]
        ledger = predicates.ledger_totals(script, p0=(0.0, 0.0), b0=1)
        self.assertFalse(ledger["consistent"])
        self.assertTrue(ledger["inconsistencies"])
        self.assertEqual(ledger["K"], 1)                 # single-count check retained
        self.assertEqual(ledger["N_clear"], 2)
        self.assertAlmostEqual(ledger["sum_delta_t"], 10.0)
        self.assertAlmostEqual(ledger["T"], 8.0)
        with self.assertRaises(predicates.InconsistentLedgerError):
            predicates.ledger_totals(script, p0=(0.0, 0.0), b0=1, strict=True)

    def test_consistent_ledger_satisfies_the_totals_identity(self):
        script = [
            {"seq": 1, "action": "clear", "x": [0, 0], "c": 1, "s": 1},
            {"seq": 2, "action": "clear", "x": [0, 0], "c": 2, "s": 1},
        ]
        ledger = predicates.ledger_totals(script, p0=(0.0, 0.0), b0=1, strict=True)
        self.assertTrue(ledger["consistent"])
        self.assertEqual(ledger["K"], 2)
        self.assertAlmostEqual(ledger["sum_delta_t"], ledger["T"])

    def test_frozen_t08_script_is_consistent(self):
        fixture = selfcheck.load_fixture(FIXTURES_DIR, "T08")
        ledger = predicates.ledger_totals(
            fixture["inputs"]["script"],
            p0=fixture["inputs"]["initial_state"]["p"],
            b0=fixture["inputs"]["initial_state"]["b"],
            strict=True,
        )
        self.assertTrue(ledger["consistent"])
        self.assertAlmostEqual(ledger["sum_delta_t"], ledger["T"])


class Rt003F2ResidualTest(unittest.TestCase):
    """RT-003 RT3-F2 residual: an *unexpected* key must not hide a NaN or an infinity.

    The first TR-012/RT-003 F2 repair rejected a non-finite actual value only when the expectation
    named the key; extra actual keys stayed ignored, so ``compare({'a':1.0}, {'a':1.0,'b':nan})``
    still returned ``[]``. These regressions cover the residual, nested dicts and lists included, and
    pin the two semantics that must *not* change: extra finite keys stay ignored, and explicitly
    expected non-finite values still match by kind and sign. Evaluator-side only; not a candidate run.
    """

    NAN = float("nan")
    INF = float("inf")
    NINF = float("-inf")

    def test_extra_nan_key_is_reported(self):
        problems = selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": self.NAN})
        self.assertTrue(problems, "an unexpected NaN value must not pass silently")
        self.assertIn("b", problems[0])

    def test_extra_positive_and_negative_infinity_keys_are_reported(self):
        for value in (self.INF, self.NINF):
            with self.subTest(value=value):
                self.assertTrue(selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": value}))

    def test_extra_key_holding_a_container_with_nan_is_reported(self):
        self.assertTrue(
            selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": {"x": [1.0, self.NAN]}})
        )
        self.assertTrue(
            selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": [{"y": self.NINF}]})
        )

    def test_nested_extra_non_finite_key_is_reported(self):
        self.assertTrue(
            selfcheck.compare({"a": {"r": 1.0}}, {"a": {"r": 1.0, "n": self.INF}})
        )
        self.assertTrue(
            selfcheck.compare(
                {"a": {"b": {"c": 1.0}}}, {"a": {"b": {"c": 1.0, "d": self.NAN}}}
            )
        )

    def test_list_element_mapping_with_extra_nan_is_reported(self):
        self.assertTrue(
            selfcheck.compare([{"a": 1.0}], [{"a": 1.0, "b": self.NAN}])
        )

    def test_extra_finite_keys_keep_their_ignored_semantics(self):
        # G16's real `actual` mapping carries the extra finite summary key `centres_unique`, so
        # finite extras must stay ignored or every frozen fixture check would break.
        self.assertEqual(selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": 2.0}), [])
        self.assertEqual(selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": [1.0, 2.0]}), [])
        self.assertEqual(selfcheck.compare({"a": 1.0}, {"a": 1.0, "b": True}), [])
        self.assertEqual(
            selfcheck.compare({"a": {"r": 1.0}}, {"a": {"r": 1.0, "t": 3.0}}), []
        )
        self.assertEqual(
            selfcheck.compare({"c": 225}, {"c": 225, "centres_unique": 225}), []
        )

    def test_explicitly_expected_non_finite_values_still_match(self):
        self.assertEqual(selfcheck.compare({"a": self.NAN}, {"a": self.NAN}), [])
        self.assertEqual(selfcheck.compare({"a": self.INF}, {"a": self.INF}), [])
        self.assertEqual(selfcheck.compare({"a": self.NINF}, {"a": self.NINF}), [])
        self.assertTrue(selfcheck.compare({"a": self.INF}, {"a": self.NINF}))
        self.assertTrue(selfcheck.compare({"a": 1.0}, {"a": self.NAN}))

    def test_fixture_level_check_flags_an_injected_non_finite_extra_key(self):
        # Simulate a future fixture whose actual mapping gains an unexpected non-finite value: the
        # fixture-level gate must fail, not pass.
        fixture = selfcheck.load_fixture(FIXTURES_DIR, "G03")
        actual = dict(selfcheck.run_evaluator_now(fixture))
        self.assertEqual(selfcheck.compare(fixture["expected_evaluator"], actual), [])
        tainted = dict(actual)
        tainted["unexpected_diameter_estimate"] = self.NAN
        self.assertTrue(
            selfcheck.compare(fixture["expected_evaluator"], tainted),
            "an injected unexpected NaN must fail the fixture-level comparison",
        )

    def test_frozen_fixtures_are_unaffected(self):
        # No frozen fixture may gain a spurious problem from the new extra-key rule.
        for result in selfcheck.check_all(FIXTURES_DIR):
            with self.subTest(fixture=result["id"]):
                self.assertEqual(result["mismatches"], [])
                self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
