"""Exercise real Copilot plugin and skill discovery when its CLI is installed."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
COPILOT = shutil.which("copilot")
MEMORY_SKILLS = {
    "memory-bootstrap", "memory-capture", "memory-checkpoint",
    "memory-maintain", "memory-promote", "memory-recall",
}


@unittest.skipUnless(sys.platform == "win32" and COPILOT, "Requires Windows and installed Copilot CLI")
class CopilotDiscoveryTests(unittest.TestCase):
    """Avoid false positives from repository mirrors or already installed plugins."""

    def test_copilot_recognizes_isolated_install_units_and_their_skills(self):
        for name in ("memory", "software-team"):
            with self.subTest(plugin=name), tempfile.TemporaryDirectory(
                prefix="copilot memory discovery "
            ) as temporary:
                root = Path(temporary)
                workspace = root / "empty workspace"
                workspace.mkdir()
                plugin = root / "isolated plugin"
                shutil.copytree(
                    ROOT / "packages" / name / "github-copilot", plugin,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
                manifest = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))
                environment = {
                    **os.environ,
                    "COPILOT_HOME": str(root / "isolated home"),
                    "COPILOT_AUTO_UPDATE": "false",
                }
                results = {}
                for resource in ("plugin", "skill"):
                    process = subprocess.run(
                        [COPILOT, "--no-auto-update", "-C", str(workspace),
                         "--plugin-dir", str(plugin), resource, "list", "--json"],
                        env=environment, capture_output=True, text=True, encoding="utf-8",
                        check=False, timeout=60,
                    )
                    self.assertEqual(process.returncode, 0, process.stderr + process.stdout)
                    self.assertNotIn("no plugin.json", process.stderr)
                    results[resource] = json.loads(process.stdout)
                external = [
                    item for item in results["plugin"]
                    if item["name"] == name and item["source"] == "external"
                ]
                self.assertEqual(len(external), 1)
                self.assertEqual(external[0]["version"], manifest["version"])
                self.assertTrue(external[0]["enabled"])
                skills = {
                    item["name"]: item for item in results["skill"]
                    if item["source"] == "plugin"
                    and Path(item["path"]).resolve().is_relative_to(plugin.resolve())
                }
                self.assertEqual(
                    {skill for skill in skills if skill.startswith("memory-")}, MEMORY_SKILLS,
                )
                if name == "software-team":
                    self.assertIn("st-okf-memory", skills)
                for skill in skills.values():
                    self.assertTrue(Path(skill["path"]).resolve().is_relative_to(plugin.resolve()))
                    self.assertTrue(skill["enabled"])


if __name__ == "__main__":
    unittest.main()
