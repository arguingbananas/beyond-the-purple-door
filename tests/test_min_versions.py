"""The minimum Python and Node versions are stated in several places; check they all agree.

Python: pyproject.toml (ruff target-version). Node: package.json ("engines").
"""

import json
import re
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY_SCRIPTS = [
    "patches/apply_bcw_purple_door_patch.py",
    "tools/ips_apply.py",
    "tools/cp2_check.py",
]
SHELL_RUNNERS = ["tools/test.sh", "tools/verify.sh"]
NODE_SCRIPTS = ["tools/a2ts_bridge.mjs", "tools/a2ts_ctl.mjs"]
DOCS = ["README.md", "CONTRIBUTING.md", "CLAUDE.md"]


def minimum() -> tuple[int, int]:
    with open(ROOT / "pyproject.toml", "rb") as f:
        target = tomllib.load(f)["tool"]["ruff"]["target-version"]  # e.g. "py311"
    return 3, int(target.removeprefix("py3"))


class MinimumPythonTest(unittest.TestCase):
    def test_running_python_meets_minimum(self):
        self.assertGreaterEqual(sys.version_info[:2], minimum())

    def test_scripts_check_the_same_minimum(self):
        major, minor = minimum()
        for rel in ENTRY_SCRIPTS + SHELL_RUNNERS:
            text = (ROOT / rel).read_text()
            with self.subTest(rel):
                self.assertRegex(text, rf"sys\.version_info [<>]=? \({major}, {minor}\)")
                self.assertIn(f"needs Python {major}.{minor} or newer", text)

    def test_ci_tests_the_minimum(self):
        major, minor = minimum()
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        matrix = re.search(r"python: \[(.*?)\]", ci)
        self.assertIsNotNone(matrix, "CI test job has no python matrix")
        self.assertIn(f'"{major}.{minor}"', matrix.group(1))

    def test_docs_state_the_minimum(self):
        major, minor = minimum()
        for rel in DOCS:
            with self.subTest(rel):
                text = (ROOT / rel).read_text()
                self.assertRegex(text, rf"Python {major}\.{minor}(\+| or newer)")


def node_minimum() -> int:
    engines = json.loads((ROOT / "package.json").read_text())["engines"]["node"]  # e.g. ">=24"
    match = re.fullmatch(r">=(\d+)", engines)
    if match is None:
        raise AssertionError(f"package.json engines.node should be '>=N', not {engines!r}")
    return int(match.group(1))


class MinimumNodeTest(unittest.TestCase):
    def test_scripts_check_the_same_minimum(self):
        major = node_minimum()
        for rel in NODE_SCRIPTS:
            text = (ROOT / rel).read_text()
            with self.subTest(rel):
                self.assertIn(f"process.versions.node.split('.')[0]) < {major})", text)
                self.assertIn(f"needs Node {major} or newer", text)

    def test_ci_uses_the_minimum(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        versions = re.findall(r'node-version: "(\d+)"', ci)
        self.assertTrue(versions, "CI sets no node-version")
        self.assertEqual(set(versions), {str(node_minimum())})

    def test_docs_state_the_minimum(self):
        major = node_minimum()
        for rel in DOCS:
            with self.subTest(rel):
                self.assertRegex((ROOT / rel).read_text(), rf"Node {major}(\+| or newer)")


if __name__ == "__main__":
    unittest.main()
