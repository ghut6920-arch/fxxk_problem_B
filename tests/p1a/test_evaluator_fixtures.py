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


if __name__ == "__main__":
    unittest.main(verbosity=2)
