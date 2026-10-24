"""Windows scenarios against copied install units, without sibling packages."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
INSTALL_ROOTS = (
    "packages/memory/github-copilot",
    "packages/memory/claude-code",
    "packages/software-team/github-copilot",
)


@unittest.skipUnless(sys.platform == "win32", "First-release validation is Windows only")
class InstalledPayloadTests(unittest.TestCase):
    """Invoke the real helper from an isolated copy of each complete payload."""

    def invoke(self, helper, workspace, *arguments, expect_ok=True):
        result = subprocess.run(
            [sys.executable, "-I", "-S", str(helper), "--root", str(workspace), *arguments],
            cwd=workspace, capture_output=True, text=True, encoding="utf-8",
            timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0 if expect_ok else 2, result.stderr + result.stdout)
        response = json.loads(result.stdout)
        self.assertIs(response["ok"], expect_ok)
        return response

    def test_autocrlf_checkout_preserves_manifest_input_bytes(self):
        with tempfile.TemporaryDirectory(prefix="memory checkout ") as temporary:
            root = Path(temporary)
            repository = root / "repo"
            repository.mkdir()
            (root / "checkout").mkdir()
            shutil.copyfile(ROOT / ".gitattributes", repository / ".gitattributes")
            paths = [
                "packages/memory/runtime/check.py",
                "packages/memory/skills/memory-recall/SKILL.md",
                *[f"{install}/memory/runtime/check.py" for install in INSTALL_ROOTS],
                *[f"{install}/skills/memory-recall/SKILL.md" for install in INSTALL_ROOTS],
                *[f"{install}/.memory-package.json" for install in INSTALL_ROOTS],
            ]
            content = b"line one\nline two\n"
            for relative in paths:
                path = repository / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            for arguments in [
                ["init", "--quiet"],
                ["config", "core.autocrlf", "true"],
                ["add", "."],
                ["checkout-index", "--all", f"--prefix={root / 'checkout'}{os.sep}"],
            ]:
                result = subprocess.run(
                    ["git", "-C", str(repository), *arguments], check=False,
                    capture_output=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
            for relative in paths:
                self.assertEqual((root / "checkout" / relative).read_bytes(), content)

    def test_offline_git_and_non_git_projects(self):
        for install in INSTALL_ROOTS:
            for git_project in (False, True):
                with self.subTest(install=install, git=git_project):
                    with tempfile.TemporaryDirectory(prefix="memory install ") as temporary:
                        root = Path(temporary)
                        plugin = root / "isolated plugin"
                        shutil.copytree(
                            ROOT / install, plugin,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                        )
                        helper = plugin / "memory/runtime/memory.py"
                        self.assertTrue(helper.is_file())
                        workspace = root / "consumer project"
                        workspace.mkdir()
                        if git_project:
                            subprocess.run(
                                ["git", "init", "--quiet", str(workspace)],
                                check=True, capture_output=True, timeout=30,
                            )
                        diagnostic = self.invoke(helper, workspace, "doctor")
                        self.assertIs(diagnostic["data"]["git"], git_project)
                        self.invoke(helper, workspace, "bootstrap")
                        store = workspace / ".maruti/memory/local"
                        metadata_before = (store / ".memory-store.json").read_bytes()
                        metadata = json.loads(metadata_before)
                        self.assertEqual(metadata["namespace"], "maruti.memory")
                        self.assertEqual(metadata["schema_version"], 1)
                        self.assertEqual(metadata["role"], "local")
                        self.assertEqual(metadata["created_with"], "0.1.0")
                        if git_project:
                            self.assertIn(
                                "/.maruti/memory/local/",
                                (workspace / ".gitignore").read_text().splitlines(),
                            )
                            ignored = subprocess.run(
                                ["git", "-C", str(workspace), "check-ignore", "--quiet",
                                 ".maruti/memory/local/.memory-store.json"],
                                check=False, capture_output=True, timeout=30,
                            )
                            self.assertEqual(ignored.returncode, 0)
                        else:
                            self.assertFalse((workspace / ".gitignore").exists())
                        self.invoke(helper, workspace, "bootstrap")
                        self.assertEqual(
                            (store / ".memory-store.json").read_bytes(), metadata_before,
                        )
                        document = workspace / "input.md"
                        document.write_text(
                            "---\ntype: Memory Note\ntitle: Packaging sentinel\n---\n"
                            "# Packaging sentinel\n\nOffline package composition works.\n",
                            encoding="utf-8",
                        )
                        relative = "topics/packaging/sentinel.md"
                        self.invoke(
                            helper, workspace, "write", "--path", relative,
                            "--input", str(document), "--expected", "missing",
                        )
                        read = self.invoke(helper, workspace, "read", "--path", relative)
                        self.assertIn("Packaging sentinel", read["data"]["content"])
                        self.assertEqual(len(read["data"]["sha256"]), 64)
                        self.invoke(
                            helper, workspace, "write", "--path", relative,
                            "--input", str(document), "--expected", "0" * 64,
                            expect_ok=False,
                        )
                        recall = self.invoke(
                            helper, workspace, "discover", "--query", "Packaging sentinel",
                        )
                        self.assertIn("sentinel", json.dumps(recall))
                        scoped = self.invoke(
                            helper, workspace, "discover", "--query", "sentinel",
                            "--topic", "packaging",
                        )["data"]
                        self.assertEqual(scoped["scope"], {"group": "topics", "name": "packaging"})
                        self.assertTrue(scoped["scan_complete"])
                        self.assertGreater(len(scoped["candidates"]), 0)
                        self.assertLessEqual(len(scoped["candidates"]), 8)
                        self.assertLessEqual(
                            sum(len(item["content"]) for item in scoped["candidates"]), 16000,
                        )
                        checkpoint = workspace / "checkpoint-input.md"
                        checkpoint.write_text(
                            "---\ntype: Session Checkpoint\ntitle: Smoke checkpoint\n---\n"
                            "# Smoke checkpoint\n\nObjective: verify installed session recall.\n",
                            encoding="utf-8",
                        )
                        self.invoke(
                            helper, workspace, "write",
                            "--path", "sessions/smoke-session/checkpoint.md",
                            "--input", str(checkpoint), "--expected", "missing",
                            "--session", "smoke-session",
                        )
                        session = self.invoke(
                            helper, workspace, "discover", "--query", "checkpoint",
                            "--session", "smoke-session",
                        )["data"]
                        self.assertEqual(
                            session["scope"], {"group": "sessions", "name": "smoke-session"},
                        )
                        self.assertTrue(session["scan_complete"])
                        self.assertIn("Smoke checkpoint", session["candidates"][0]["content"])
                        self.invoke(helper, workspace, "catalog", "--topic", "packaging")
                        self.assertFalse((workspace / ".project-memory").exists())
                        self.assertFalse((workspace / ".maruti/memory/shared").exists())
                        if not git_project:
                            subprocess.run(
                                ["git", "init", "--quiet", str(workspace)],
                                check=True, capture_output=True, timeout=30,
                            )
                            pending = "topics/packaging/after-init.md"
                            refused = self.invoke(
                                helper, workspace, "write", "--path", pending,
                                "--input", str(document), "--expected", "missing",
                                expect_ok=False,
                            )
                            self.assertEqual(refused["error"]["code"], "privacy_not_ignored")
                            self.assertFalse((store / pending).exists())
                            self.invoke(helper, workspace, "bootstrap")
                            self.invoke(
                                helper, workspace, "write", "--path", pending,
                                "--input", str(document), "--expected", "missing",
                            )


if __name__ == "__main__":
    unittest.main()
