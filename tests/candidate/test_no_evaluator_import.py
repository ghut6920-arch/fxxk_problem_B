"""Structural candidate tests: no evaluator import, stdlib only, no copied source.

These checks enforce the WI-015 constraints that are structural rather than
numeric:

* no module under ``src/candidate/`` imports ``evaluator`` (AST level, so a
  static import cannot hide behind an alias);
* the candidate package imports only the Python standard library plus its own
  submodules;
* the candidate package does not copy evaluator source text verbatim.

Shared literal labels required by the SPEC (for example
``NUMERICAL_UNCERTAIN = "NUMERICAL_UNCERTAIN"``) are excluded from the overlap
check: both sides must emit the same frozen label, which is interface
compatibility rather than copied logic.
"""

import ast
import pathlib
import re
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC = REPO / "src"
CANDIDATE = SRC / "candidate"
EVALUATOR = SRC / "evaluator"

_LABEL_CONST = re.compile(r"^[A-Z][A-Z0-9_]*\s*=\s*[\"'][A-Za-z0-9_]+[\"']$")


def _candidate_files():
    return sorted(p for p in CANDIDATE.rglob("*.py") if "__pycache__" not in p.parts)


def _imports(tree):
    """Yield ``(module_name, is_relative)`` for every import statement."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, False
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    yield node.module, False
            else:
                yield (node.module or ""), True


class TestNoEvaluatorDependency(unittest.TestCase):
    def test_candidate_package_exists_and_is_non_empty(self):
        files = _candidate_files()
        self.assertGreaterEqual(len(files), 5, [str(p) for p in files])

    def test_no_module_imports_evaluator(self):
        for path in _candidate_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for name, _rel in _imports(tree):
                root = name.split(".")[0]
                self.assertNotEqual(root, "evaluator", f"{path} imports {name}")
                self.assertNotEqual(root, "src", f"{path} imports {name}")

    def test_no_import_statement_mentions_evaluator(self):
        for path in _candidate_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    text = ast.unparse(node)
                    self.assertNotIn("evaluator", text, f"{path}: {text}")

    def test_no_dynamic_import_of_evaluator(self):
        for path in _candidate_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, ("eval", "exec", "__import__"),
                                     f"{path}: {ast.unparse(node)}")
                if isinstance(node, ast.Name) and node.id == "importlib":
                    self.fail(f"{path} references importlib")
                if isinstance(node, ast.Attribute) and node.attr in ("import_module", "load_module"):
                    self.fail(f"{path} performs a dynamic import: {ast.unparse(node)}")

    def test_no_evaluator_file_is_opened(self):
        for path in _candidate_files():
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                if ("open(" in line or "read_text" in line or "Path(" in line):
                    self.assertNotIn("evaluator", line, f"{path}: {line.strip()}")

    def test_stdlib_only(self):
        allowed = set(sys.stdlib_module_names)
        for path in _candidate_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for name, rel in _imports(tree):
                if rel:
                    # relative import inside the candidate package is fine
                    self.assertNotIn("..", name, f"{path} escapes the package with {name}")
                    continue
                root = name.split(".")[0]
                if root == "candidate":
                    continue
                self.assertIn(root, allowed, f"{path} imports non-stdlib module {name}")


class TestNoCopiedEvaluatorSource(unittest.TestCase):
    def test_no_long_verbatim_line_shared_with_the_evaluator(self):
        if not EVALUATOR.exists():
            self.skipTest("evaluator tree absent at this base")
        cand_lines = set()
        for path in _candidate_files():
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if len(stripped) >= 40 and not stripped.startswith("#"):
                    cand_lines.add(stripped)
        shared = []
        for path in sorted(EVALUATOR.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if len(stripped) < 40 or stripped not in cand_lines:
                    continue
                if stripped.startswith(("import ", "from ", '"""', "def ", "class ")):
                    continue
                if _LABEL_CONST.match(stripped):
                    continue
                shared.append((str(path), stripped))
        self.assertEqual(shared, [], f"suspicious verbatim overlap: {shared}")


if __name__ == "__main__":
    unittest.main()
