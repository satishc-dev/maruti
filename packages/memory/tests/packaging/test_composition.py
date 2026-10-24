"""Offline composition and repository mirror collision regression tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]


def load_script(name):
    """Load a repository script without installing any package."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build = load_script("build_memory_package")
links = load_script("link_packages")


class CompositionTests(unittest.TestCase):
    """Exercise generation using temporary roots, not premature real payloads."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "source"
        self.output = Path(self.temporary.name) / "output"
        for directory in build.PAYLOAD_ROOTS:
            self.write(f"packages/memory/{directory}/example.txt", directory)
        self.write("packages/memory/skills/memory-recall/SKILL.md", "canonical narrative\n")

    def write(self, name, text, *, output=False):
        root = self.output if output else self.root
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def discover(self):
        with patch.multiple(
            links, REPO_ROOT=self.output, PACKAGES_DIR=self.output / "packages",
            CLAUDE_ROOT=self.output / ".claude", GITHUB_ROOT=self.output / ".github",
        ):
            return links.discover_mirrors()

    def test_staged_payload_is_identical_self_contained_and_idempotent(self):
        self.assertTrue(build.compose(self.root, self.output))
        self.assertEqual(build.compose(self.root, self.output), [])
        self.assertEqual(build.compose(self.root, self.output, check=True), [])
        for install in build.INSTALL_ROOTS:
            root = self.output / install
            for directory in build.PAYLOAD_ROOTS:
                self.assertEqual(
                    (root / "memory" / directory / "example.txt").read_bytes(),
                    directory.encode(),
                )
            self.assertFalse(any(path.is_symlink() for path in root.rglob("*")))
            self.assertEqual(
                (root / "skills/memory-recall/SKILL.md").read_bytes(),
                b"canonical narrative\n",
            )

    def test_unknown_collision_is_never_overwritten(self):
        path = self.write(
            "packages/software-team/github-copilot/skills/memory-recall/SKILL.md",
            "unrelated author",
            output=True,
        )
        with self.assertRaisesRegex(ValueError, "collision"):
            build.compose(self.root, self.output)
        self.assertEqual(path.read_text(), "unrelated author")
        self.assertFalse((self.output / build.INSTALL_ROOTS[0]).exists())

    def test_modified_generated_file_is_not_replaced(self):
        build.compose(self.root, self.output)
        self.write("packages/memory/github-copilot/memory/runtime/example.txt", "local edit",
                   output=True)
        with self.assertRaisesRegex(ValueError, "collision"):
            build.compose(self.root, self.output)

    def test_unknown_payload_addition_is_reported_and_preserved(self):
        build.compose(self.root, self.output)
        path = self.write(
            "packages/memory/github-copilot/memory/runtime/unknown.py",
            "do not delete",
            output=True,
        )
        with self.assertRaisesRegex(ValueError, "Unknown file"):
            build.compose(self.root, self.output, check=True)
        self.assertEqual(path.read_text(), "do not delete")

    def test_unknown_mirror_declaration_is_not_overwritten(self):
        path = self.write(
            "packages/memory/composition/mirrors.json",
            '{"schema_version": 1, "groups": []}',
            output=True,
        )
        with self.assertRaisesRegex(ValueError, "Unknown composed mirror"):
            build.compose(self.root, self.output)
        self.assertEqual(json.loads(path.read_text())["groups"], [])
        self.assertFalse((self.output / build.INSTALL_ROOTS[0]).exists())

    def test_canonical_change_regenerates_and_check_is_read_only(self):
        build.compose(self.root, self.output)
        self.write("packages/memory/runtime/example.txt", "new")
        self.assertTrue(build.compose(self.root, self.output, check=True))
        destination = self.output / build.INSTALL_ROOTS[0] / "memory/runtime/example.txt"
        self.assertEqual(destination.read_text(), "runtime")
        build.compose(self.root, self.output)
        self.assertEqual(destination.read_text(), "new")

    def test_existing_software_team_contracts_and_ownership_are_untouched(self):
        contract = self.write(
            "packages/software-team/github-copilot/contracts/MEMORY-SCHEMA.md",
            "Project-Lead owns .project-memory; workers propose via memory_proposals",
            output=True,
        )
        skill = self.write(
            "packages/software-team/github-copilot/skills/st-okf-memory/SKILL.md",
            "team ownership adapter",
            output=True,
        )
        build.compose(self.root, self.output)
        self.assertIn("Project-Lead owns", contract.read_text())
        self.assertEqual(skill.read_text(), "team ownership adapter")

    def test_only_explicit_identical_mirrors_are_coalesced(self):
        build.compose(self.root, self.output)
        mirrors = self.discover()
        self.assertEqual(len(mirrors), 2)
        self.assertTrue(all("software-team" not in str(item.source) for item in mirrors))
        self.write("packages/unknown/github-copilot/skills/memory-recall/SKILL.md",
                   "canonical narrative\n", output=True)
        with self.assertRaises(SystemExit):
            self.discover()

    def test_declared_but_divergent_mirror_is_rejected(self):
        build.compose(self.root, self.output)
        self.write("packages/software-team/github-copilot/skills/memory-recall/SKILL.md",
                   "different", output=True)
        with self.assertRaises(SystemExit):
            self.discover()

    def test_manifest_traversal_is_rejected(self):
        build.compose(self.root, self.output)
        path = self.output / build.INSTALL_ROOTS[0] / build.MANIFEST
        manifest = json.loads(path.read_text())
        manifest["files"]["memory/../../unmanaged.txt"] = "0" * 64
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            build.compose(self.root, self.output)

    def test_malformed_manifest_is_reported(self):
        build.compose(self.root, self.output)
        path = self.output / build.INSTALL_ROOTS[0] / build.MANIFEST
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unknown composition manifest"):
            build.compose(self.root, self.output)

    def test_modified_obsolete_file_is_preserved(self):
        source = self.write("packages/memory/runtime/obsolete.txt", "old")
        build.compose(self.root, self.output)
        source.unlink()
        path = self.write(
            "packages/memory/github-copilot/memory/runtime/obsolete.txt",
            "important local change",
            output=True,
        )
        with self.assertRaisesRegex(ValueError, "remove edited"):
            build.compose(self.root, self.output)
        self.assertEqual(path.read_text(), "important local change")

    def test_stale_generated_file_is_removed_only_if_unmodified(self):
        source = self.write("packages/memory/runtime/obsolete.txt", "old")
        build.compose(self.root, self.output)
        source.unlink()
        self.assertTrue(build.compose(self.root, self.output, check=True))
        build.compose(self.root, self.output)
        self.assertFalse(
            (self.output / build.INSTALL_ROOTS[0] / "memory/runtime/obsolete.txt").exists()
        )

    def test_removed_skill_does_not_leave_a_discoverable_empty_directory(self):
        source = self.write("packages/memory/skills/memory-old/SKILL.md", "old")
        build.compose(self.root, self.output)
        source.unlink()
        source.parent.rmdir()
        build.compose(self.root, self.output)
        self.assertEqual(len(self.discover()), 2)
        self.assertFalse(
            (self.output / build.INSTALL_ROOTS[0] / "skills/memory-old").exists()
        )


class SoftwareTeamWiringTests(unittest.TestCase):
    """Keep both bootstrap entry points and the ownership adapter connected."""

    def test_bootstrap_entry_points_invoke_bundled_helper(self):
        team = ROOT / "packages/software-team/github-copilot"
        for relative in [
            "agents/st-project-lead.agent.md", "prompts/st-bootstrap.prompt.md",
        ]:
            content = (team / relative).read_text(encoding="utf-8")
            self.assertIn("memory/runtime/memory.py", content)
            self.assertIn("/.maruti/memory/local/", content)
            self.assertIn("memory_proposals[]", content)
            self.assertIn(".project-memory/", content)
            self.assertIn("AGENTS.md", content)
            self.assertIn("managed Memory section", content)

    def test_adapter_preserves_ownership_and_separates_generic_capability(self):
        content = (
            ROOT / "packages/software-team/github-copilot/skills/st-okf-memory/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Write only documents your team owns", content)
        self.assertIn("| `.project-memory/` | Project-Lead |", content)
        self.assertIn("memory_proposals[]", content)
        self.assertIn("memory/runtime/memory.py", content)
        self.assertIn("It needs no GitHub authentication", content)
        self.assertIn("not approval to stage, commit, or push", content)
        self.assertIn("When board and documents disagree, documents win", content)
        self.assertIn("managed `AGENTS.md` section by default", content)

    def test_marketplaces_publish_complete_independent_memory_roots(self):
        copilot = json.loads((ROOT / ".github/plugin/marketplace.json").read_text())
        entries = [entry for entry in copilot["plugins"] if entry["name"] == "memory"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], "./packages/memory/github-copilot")
        self.assertEqual(entries[0]["version"], build.VERSION)
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        entries += [entry for entry in claude["plugins"] if entry["name"] == "memory"]
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]["source"]["path"], "packages/memory/claude-code")
        for entry in entries:
            self.assertNotIn("dependencies", entry)
        manifest = json.loads((
            ROOT / "packages/memory/claude-code/.claude-plugin/plugin.json"
        ).read_text())
        self.assertEqual(manifest["name"], "memory")
        self.assertEqual(manifest["version"], build.VERSION)

    def test_copilot_install_units_have_loader_manifests_matching_marketplace(self):
        build.validate_copilot_manifests(ROOT)
        marketplace = json.loads((ROOT / ".github/plugin/marketplace.json").read_text())
        for name in ("memory", "software-team"):
            entry = next(item for item in marketplace["plugins"] if item["name"] == name)
            root = ROOT / entry["source"]
            manifest = json.loads((root / "plugin.json").read_text())
            self.assertEqual(manifest["name"], name)
            self.assertEqual(manifest["version"], entry["version"])
            self.assertNotIn("$schema", manifest)
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertTrue((root / manifest["skills"]).is_dir())
            self.assertNotIn("dependencies", manifest)
            if name == "software-team":
                self.assertEqual(manifest["agents"], "./agents/")
                self.assertTrue((root / manifest["agents"]).is_dir())
            else:
                self.assertEqual(manifest["version"], build.VERSION)

    def test_composition_rejects_missing_or_mismatched_loader_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / ".github/plugin/marketplace.json"
            catalog.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / ".github/plugin/marketplace.json", catalog)
            for install in build.INSTALL_ROOTS:
                if install.endswith("/github-copilot"):
                    plugin = root / install
                    (plugin / "skills").mkdir(parents=True)
                    shutil.copyfile(ROOT / install / "plugin.json", plugin / "plugin.json")
            build.validate_copilot_manifests(root)
            manifest = root / "packages/memory/github-copilot/plugin.json"
            original = manifest.read_bytes()
            manifest.unlink()
            with self.assertRaises(FileNotFoundError):
                build.validate_copilot_manifests(root)
            manifest.write_bytes(original.replace(b'"0.1.0"', b'"0.9.0"'))
            with self.assertRaisesRegex(ValueError, "catalog mismatch"):
                build.validate_copilot_manifests(root)

    def test_installed_readme_links_do_not_depend_on_sibling_checkout_files(self):
        for install in build.INSTALL_ROOTS:
            root = (ROOT / install).resolve()
            content = (root / "README.md").read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(install=install, target=target):
                    destination = (root / target.split("#")[0]).resolve()
                    self.assertTrue(destination.is_relative_to(root))
                    self.assertTrue(destination.exists())


if __name__ == "__main__":
    unittest.main()
