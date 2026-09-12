"""Isolation checks for the P1-B adapter and the practice client.

* ``src/protocol/`` must not import ``evaluator`` (the oracle stays out of the
  adapter) and must stay standard-library only;
* neither the adapter nor the practice client may read simulator internals
  (``JammersSimulatorData``, ``.jlog``, sqlite) as strategy input -- the official
  rules forbid that and WI-017 repeats it;
* the adapter must not read files at all: its only inputs are the official
  responses.
"""

from __future__ import annotations

import ast
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "src" / "protocol"
PRACTICE = REPO / "scripts" / "run_c0_practice.py"

FORBIDDEN_INTERNAL_MARKERS = ("JammersSimulatorData", ".jlog", "sqlite", "behavior-logs", "behavior-runs")


def _files():
    return sorted(p for p in PROTOCOL.rglob("*.py") if "__pycache__" not in p.parts)


def _imports(tree):
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


def _docstring_ids(tree):
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                ids.add(id(body[0].value))
    return ids


def _code_text(path):
    """Source with docstrings and comments removed.

    The rule being checked is "never *use* simulator internals"; a docstring or
    comment that says they are never read is prose, not a reference.  What
    remains here is executable code, its literals and its identifiers.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstrings = _docstring_ids(tree)
    parts = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            parts.append(node.value)
        if isinstance(node, ast.Name):
            parts.append(node.id)
        if isinstance(node, ast.Attribute):
            parts.append(node.attr)
        if isinstance(node, ast.arg) and node.arg:
            parts.append(node.arg)
    return "\n".join(parts)


class TestProtocolIsolation(unittest.TestCase):
    def test_package_exists(self):
        self.assertGreaterEqual(len(_files()), 4, [str(p) for p in _files()])

    def test_no_module_imports_evaluator(self):
        for path in _files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for name, _rel in _imports(tree):
                self.assertNotEqual(name.split(".")[0], "evaluator", f"{path} imports {name}")

    def test_no_import_statement_mentions_evaluator(self):
        for path in _files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    self.assertNotIn("evaluator", ast.unparse(node), f"{path}")

    def test_stdlib_only(self):
        allowed = set(sys.stdlib_module_names)
        for path in _files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for name, rel in _imports(tree):
                if rel:
                    continue
                root = name.split(".")[0]
                if root in ("candidate", "protocol"):
                    continue
                self.assertIn(root, allowed, f"{path} imports non-stdlib module {name}")

    def test_adapter_does_not_read_any_file(self):
        """The adapter's only inputs are official responses: no file I/O at all."""
        for path in _files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotEqual(node.func.id, "open", f"{path} calls open()")
                if isinstance(node, ast.Attribute):
                    self.assertNotIn(node.attr, ("read_text", "read_bytes", "open", "listdir", "walk"),
                                     f"{path} performs file I/O ({node.attr})")
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    text = ast.unparse(node)
                    for module in ("pathlib", "os", "shutil", "glob", "sqlite3", "zipfile"):
                        self.assertNotIn(module, text, f"{path} imports {module}")

    def test_no_simulator_internal_reference(self):
        """No code, literal or identifier may touch simulator internals.

        Docstrings and comments are excluded on purpose: the practice client's
        docstring states that internals are never read, which is the property,
        not a violation of it.
        """
        for path in list(_files()) + [PRACTICE]:
            code = _code_text(path)
            for marker in FORBIDDEN_INTERNAL_MARKERS:
                self.assertNotIn(marker, code, f"{path} references simulator internals ({marker})")

    def test_the_internal_reference_check_is_not_vacuous(self):
        """A planted literal must be caught and prose must be ignored."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            planted = pathlib.Path(tmp) / "planted.py"
            planted.write_text('DATA = "JammersSimulatorData/logs"\n', encoding="utf-8")
            self.assertIn("JammersSimulatorData", _code_text(planted))
            prose_only = pathlib.Path(tmp) / "prose.py"
            prose_only.write_text('"""We never read JammersSimulatorData logs."""\nVALUE = 1\n',
                                  encoding="utf-8")
            self.assertNotIn("JammersSimulatorData", _code_text(prose_only))


class TestClientContract(unittest.TestCase):
    def test_only_the_four_documented_paths_are_sent(self):
        from protocol.client import PATHS
        self.assertEqual(set(PATHS), {"/enter", "/measure", "/clear", "/exit"})

    def test_robot_id_is_required(self):
        from protocol.client import RobotClient
        with self.assertRaises(ValueError):
            RobotClient("http://127.0.0.1:2026", robot_id="")

    def test_default_base_url_matches_the_documented_service(self):
        from protocol.client import DEFAULT_BASE_URL
        self.assertEqual(DEFAULT_BASE_URL, "http://127.0.0.1:2026")


if __name__ == "__main__":
    unittest.main()
