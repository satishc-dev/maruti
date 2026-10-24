"""Safe, persistent workspace instructions established by local bootstrap."""

from pathlib import Path
from itertools import product
import re
import shutil
import stat
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_memory as helpers

memory = helpers.memory
PREVIOUS_BLOCKS = tuple(
    (helpers.PACKAGE / "tests/fixtures" / name).read_bytes().replace(b"\r\n", b"\n").rstrip(b"\n")
    for name in ("previous-agents-block.md", "previous-generic-agents-block.md")
)
PREVIOUS_BLOCK = PREVIOUS_BLOCKS[0]


class BootstrapInstructionTests(unittest.TestCase):
    """Exercise only the workspace AGENTS.md managed-section contract."""

    setUp = helpers.RuntimeTests.setUp
    tearDown = helpers.RuntimeTests.tearDown
    call = helpers.RuntimeTests.call

    def test_previous_section_fingerprint_is_exact_and_current_section_is_generic(self):
        self.assertEqual(
            {memory.digest(block) for block in PREVIOUS_BLOCKS}, memory.AGENTS_PREVIOUS_HASHES,
        )
        self.assertNotIn(memory.digest(memory.AGENTS_BLOCK), memory.AGENTS_PREVIOUS_HASHES)
        for token in (b"Software Team", b"Project-Lead", b".project-memory/"):
            self.assertNotIn(token, memory.AGENTS_BLOCK)

    def test_generated_guidance_covers_actual_canonical_skill_names_and_conditional_triggers(self):
        names = []
        for path in (helpers.PACKAGE / "skills").glob("*/SKILL.md"):
            match = re.search(r"^name: (\S+)$", path.read_text(encoding="utf-8"), re.M)
            self.assertIsNotNone(match, path)
            names.append(match.group(1))
        references = re.findall(r"`(memory-[a-z-]+)`", memory.AGENTS_BLOCK.decode("ascii"))
        self.assertCountEqual(references, names)
        self.assertIn(b"when a topic needs bounded review or consolidation", memory.AGENTS_BLOCK)
        self.assertIn(b"never as a scheduled service", memory.AGENTS_BLOCK)
        self.assertIn(b"when selected knowledge is worth sharing: propose first", memory.AGENTS_BLOCK)
        self.assertIn(b"write shared content only with explicit authorization", memory.AGENTS_BLOCK)

    def test_exact_previous_section_upgrades_without_touching_surrounding_bytes_or_store(self):
        self.call("bootstrap")
        metadata = (self.store / ".memory-store.json").read_bytes()
        path = self.root / "AGENTS.md"
        for previous, newline in product(PREVIOUS_BLOCKS, (b"\n", b"\r\n", b"\r")):
            with self.subTest(previous=memory.digest(previous), newline=newline):
                prefix = b"\xef\xbb\xbf# Owner policy\r\n\r\n"
                suffix = b"\n\n## Existing project rules\rKeep these exact bytes.\r"
                path.write_bytes(prefix + previous.replace(b"\n", newline) + suffix)
                result = self.call("bootstrap")
                expected = prefix + memory.AGENTS_BLOCK.replace(b"\n", newline) + suffix
                self.assertFalse(result["created"])
                self.assertEqual(result["instructions"]["status"], "upgraded")
                self.assertEqual(result["instructions"]["sha256"], memory.digest(expected))
                self.assertEqual(path.read_bytes(), expected)
                self.assertEqual((self.store / ".memory-store.json").read_bytes(), metadata)
                self.assertEqual(self.call("bootstrap")["instructions"]["status"], "present")
                self.assertEqual(path.read_bytes(), expected)

    def test_previous_section_upgrades_during_new_local_enablement(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(PREVIOUS_BLOCK + b"\n")
        result = self.call("bootstrap")
        self.assertTrue(result["created"])
        self.assertEqual(result["instructions"]["status"], "upgraded")
        self.assertEqual(path.read_bytes(), memory.AGENTS_BLOCK + b"\n")

    def test_edited_or_conflicting_previous_sections_are_never_upgraded(self):
        path = self.root / "AGENTS.md"
        for content in (
            variant for previous in PREVIOUS_BLOCKS for variant in (
                previous.replace(b"bounded", b"unbounded"),
                previous.replace(b"authorization;", b"authorization ;"),
                previous.replace(memory.AGENTS_BEGIN, b"<!-- maruti-memory:start -->"),
                previous + b"\n" + memory.AGENTS_BLOCK,
                b"Quote: " + previous,
            )
        ):
            with self.subTest(content=content[:70]):
                path.write_bytes(content)
                self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_conflict")
                self.assertEqual(path.read_bytes(), content)
                self.assertFalse(self.store.exists())

    def test_read_only_previous_section_requires_permission_instead_of_upgrade(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(PREVIOUS_BLOCK + b"\n")
        mode = path.stat().st_mode
        try:
            path.chmod(stat.S_IREAD)
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_read_only")
            self.assertEqual(path.read_bytes(), PREVIOUS_BLOCK + b"\n")
            self.assertFalse(self.store.exists())
        finally:
            path.chmod(mode)

    def test_previous_section_upgrade_keeps_hash_cas_and_explicit_partial_errors(self):
        self.call("bootstrap")
        path = self.root / "AGENTS.md"
        path.write_bytes(PREVIOUS_BLOCK + b"\n")
        external = PREVIOUS_BLOCK + b"\n\n## Concurrent owner policy\nKeep this.\n"
        original = memory.atomic

        def concurrent(target, content, expected):
            if target == path:
                path.write_bytes(external)
            return original(target, content, expected)

        with patch.object(memory, "atomic", side_effect=concurrent):
            error = self.call("bootstrap", ok=False)
        self.assertEqual(error["code"], "stale_write")
        self.assertIn("Bootstrap is incomplete", error["message"])
        self.assertEqual(path.read_bytes(), external)
        self.assertTrue(self.call("doctor")["enabled"])

    def test_shared_bootstrap_never_upgrades_previous_local_section(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(PREVIOUS_BLOCK + b"\n")
        result = self.call("--role", "shared", "bootstrap", "--allow-shared")
        self.assertNotIn("instructions", result)
        self.assertEqual(path.read_bytes(), PREVIOUS_BLOCK + b"\n")
        self.assertFalse(self.store.exists())

    def test_new_local_bootstrap_creates_instructions_and_is_byte_idempotent(self):
        first = self.call("bootstrap")
        path = self.root / "AGENTS.md"
        before = path.read_bytes()
        self.assertEqual(before, memory.AGENTS_BLOCK + b"\n")
        self.assertEqual(first["instructions"], {
            "path": "AGENTS.md", "status": "created", "sha256": memory.digest(before),
        })
        metadata = (self.store / ".memory-store.json").read_bytes()
        second = self.call("bootstrap")
        self.assertEqual(second["instructions"]["status"], "present")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual((self.store / ".memory-store.json").read_bytes(), metadata)
        self.assertFalse((self.root / ".gitignore").exists())
        self.assertTrue(self.call("doctor")["enabled"])

    def test_existing_utf8_bytes_bom_and_line_endings_are_preserved(self):
        path = self.root / "AGENTS.md"
        for old in (
            b"# Owner\n\nKeep this.\n", b"# Owner\r\n\r\nKeep this.\r\n",
            b"# Owner\rKeep this.\r", b"No trailing newline", b"",
            b"\xef\xbb\xbf# Caf\xc3\xa9\r\n",
        ):
            with self.subTest(original=old):
                path.write_bytes(old)
                self.assertEqual(self.call("bootstrap")["instructions"]["status"], "appended")
                content = path.read_bytes()
                self.assertTrue(content.startswith(old))
                self.assertEqual(content.count(memory.AGENTS_BEGIN), 1)
                if b"\r\n" in old:
                    self.assertNotIn(b"\n", content[len(old):].replace(b"\r\n", b""))
                self.call("bootstrap")
                self.assertEqual(path.read_bytes(), content)

    def test_recognized_store_missing_pointer_is_repaired_without_store_changes(self):
        self.call("bootstrap")
        before = {
            path.relative_to(self.store): path.read_bytes()
            for path in self.store.rglob("*") if path.is_file()
        }
        agents = self.root / "AGENTS.md"
        for old in (None, b"# Existing project guidance\n"):
            with self.subTest(previous=old):
                agents.unlink()
                if old is not None:
                    agents.write_bytes(old)
                result = self.call("bootstrap")
                self.assertFalse(result["created"])
                self.assertEqual(result["instructions"]["status"], "created" if old is None else "appended")
                self.assertEqual(before, {
                    path.relative_to(self.store): path.read_bytes()
                    for path in self.store.rglob("*") if path.is_file()
                })

    def test_modified_malformed_duplicate_or_embedded_markers_refuse_without_clobber(self):
        variants = (
            memory.AGENTS_BLOCK.replace(b"bounded", b"unbounded"),
            memory.AGENTS_BEGIN,
            memory.AGENTS_END,
            memory.AGENTS_END + b"\n" + memory.AGENTS_BEGIN,
            memory.AGENTS_BLOCK + b"\n" + memory.AGENTS_BLOCK,
            memory.AGENTS_BLOCK.replace(b"maruti-memory:begin", b"MARUTI-MEMORY:BEGIN"),
            memory.AGENTS_BLOCK.replace(b"<!-- maruti-memory:", b"<!--maruti-memory:"),
            memory.AGENTS_BLOCK.replace(b"maruti-memory:begin", b"maruti-memory begin"),
            b"User quotation: " + memory.AGENTS_BLOCK,
            memory.AGENTS_BLOCK + b" user suffix",
            memory.AGENTS_BLOCK.replace(memory.AGENTS_BEGIN, b"").replace(memory.AGENTS_END, b""),
            b"## Workspace Memory\nOwner-authored policy.\n",
        )
        path = self.root / "AGENTS.md"
        for content in variants:
            with self.subTest(content=content[:70]):
                path.write_bytes(content)
                self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_conflict")
                self.assertEqual(path.read_bytes(), content)
                self.assertFalse(self.store.exists())

    def test_modified_section_in_enabled_store_requires_explicit_reconciliation(self):
        self.call("bootstrap")
        path = self.root / "AGENTS.md"
        modified = path.read_bytes().replace(b"bounded", b"unbounded")
        path.write_bytes(modified)
        metadata = (self.store / ".memory-store.json").read_bytes()
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_conflict")
        self.assertEqual(path.read_bytes(), modified)
        self.assertEqual((self.store / ".memory-store.json").read_bytes(), metadata)

    @unittest.skipUnless(shutil.which("git"), "Requires installed Git")
    def test_git_bootstrap_adds_pointer_and_ignore_without_staging(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        path = self.root / "AGENTS.md"
        before = b"# Owner\r\n"
        path.write_bytes(before)
        self.call("bootstrap")
        content = path.read_bytes()
        self.assertTrue(content.startswith(before))
        self.assertIn(memory.ANCHOR, (self.root / ".gitignore").read_bytes().splitlines())
        self.call("bootstrap")
        self.assertEqual(path.read_bytes(), content)
        tracked = subprocess.run(
            ["git", "-C", str(self.root), "ls-files", "--cached"],
            check=True, capture_output=True,
        )
        self.assertEqual(tracked.stdout, b"")

    @unittest.skipUnless(shutil.which("git"), "Requires installed Git")
    def test_conflicting_instructions_fail_before_gitignore_or_store_changes(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        (self.root / "AGENTS.md").write_bytes(memory.AGENTS_BEGIN)
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_conflict")
        self.assertFalse((self.root / ".gitignore").exists())
        self.assertFalse(self.store.exists())

    def test_user_text_after_valid_section_is_preserved_without_rewrite(self):
        path = self.root / "AGENTS.md"
        content = memory.AGENTS_BLOCK + b"\n\n## Owner policy\r\nKeep ownership.\r\n"
        path.write_bytes(content)
        with patch.object(memory, "atomic", wraps=memory.atomic) as atomic:
            self.call("bootstrap")
        self.assertEqual(path.read_bytes(), content)
        self.assertFalse(any(call.args[0] == path for call in atomic.call_args_list))

    def test_unknown_or_incompatible_store_never_creates_instructions(self):
        self.store.mkdir(parents=True)
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unrecognized_store")
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.store.rmdir()
        self.call("bootstrap")
        (self.root / "AGENTS.md").unlink()
        metadata = self.store / ".memory-store.json"
        metadata.write_bytes(metadata.read_bytes().replace(b'"schema_version": 1', b'"schema_version": 2'))
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unsupported_schema")
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_shared_bootstrap_neither_creates_nor_validates_local_pointer(self):
        self.call("--role", "shared", "bootstrap", "--allow-shared")
        path = self.root / "AGENTS.md"
        self.assertFalse(path.exists())
        path.write_bytes(memory.AGENTS_BEGIN)
        self.call("--role", "shared", "bootstrap", "--allow-shared")
        self.assertEqual(path.read_bytes(), memory.AGENTS_BEGIN)
        self.assertFalse(self.store.exists())

    def test_read_only_existing_instructions_refuse_before_store_creation(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(b"# Owner\n")
        original_mode = path.stat().st_mode
        try:
            path.chmod(stat.S_IREAD)
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "instructions_read_only")
            self.assertFalse(self.store.exists())
            self.assertEqual(path.read_bytes(), b"# Owner\n")
        finally:
            path.chmod(original_mode)

    def test_instruction_directory_is_rejected_before_store_creation(self):
        (self.root / "AGENTS.md").mkdir()
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unsafe_path")
        self.assertFalse(self.store.exists())

    def test_instruction_symlink_is_not_read_or_replaced(self):
        target = self.root / "owner.md"
        target.write_bytes(b"Owner bytes")
        path = self.root / "AGENTS.md"
        try:
            path.symlink_to(target)
        except OSError:
            self.skipTest("Windows symlink creation requires Developer Mode or privilege")
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unsafe_path")
        self.assertEqual(target.read_bytes(), b"Owner bytes")
        self.assertTrue(path.is_symlink())
        self.assertFalse(self.store.exists())

    def test_reparse_redirect_is_rejected_before_instruction_read(self):
        original = Path.lstat

        def redirected(path, *args, **kwargs):
            if path == self.root / "AGENTS.md":
                return SimpleNamespace(st_mode=stat.S_IFREG, st_file_attributes=0x400)
            return original(path, *args, **kwargs)

        with patch.object(Path, "lstat", redirected):
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "unsafe_path")
        self.assertFalse(self.store.exists())

    def test_concurrent_instruction_edit_is_preserved_and_partial_outcome_is_explicit(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(b"# Owner\n")
        external = b"# Owner\n\n## Owner policy\nConcurrent owner addition.\n"
        original = memory.atomic

        def concurrent(target, content, expected):
            if target == path:
                path.write_bytes(external)
            return original(target, content, expected)

        with patch.object(memory, "atomic", side_effect=concurrent):
            error = self.call("bootstrap", ok=False)
        self.assertEqual(error["code"], "stale_write")
        self.assertIn("Local Memory is enabled", error["message"])
        self.assertIn("Bootstrap is incomplete", error["message"])
        self.assertEqual(path.read_bytes(), external)
        self.assertTrue(self.call("doctor")["enabled"])
        self.call("bootstrap")
        self.assertTrue(path.read_bytes().startswith(external))

    def test_instruction_replace_permission_failure_reports_enabled_store_without_rollback(self):
        path = self.root / "AGENTS.md"
        path.write_bytes(b"# Owner\n")
        original = memory.os.replace

        def denied(source, target):
            if target == path:
                raise PermissionError("fixture denial")
            return original(source, target)

        with patch.object(memory.os, "replace", side_effect=denied):
            error = self.call("bootstrap", ok=False)
        self.assertEqual(error["code"], "instructions_io")
        self.assertIn("Local Memory is enabled", error["message"])
        self.assertIn("No multi-file rollback", error["message"])
        self.assertEqual(path.read_bytes(), b"# Owner\n")
        self.assertTrue(self.call("doctor")["enabled"])
        self.assertEqual(list(self.root.glob(".memory-*.tmp")), [])

    def test_already_present_section_still_checks_for_concurrent_owner_edits(self):
        self.call("bootstrap")
        path = self.root / "AGENTS.md"
        external = path.read_bytes() + b"\n## Owner addition\n"
        original = memory.privacy

        def concurrent(*args, **kwargs):
            path.write_bytes(external)
            return original(*args, **kwargs)

        with patch.object(memory, "privacy", side_effect=concurrent):
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "stale_write")
        self.assertEqual(path.read_bytes(), external)

    def test_invalid_utf8_and_oversize_instruction_targets_refuse_without_truncation(self):
        path = self.root / "AGENTS.md"
        for content, code in (
            (b"\xff", "invalid_document"),
            (b"x" * (memory.MAX_FILE_BYTES + 1), "too_large"),
            (b"x" * (memory.MAX_FILE_BYTES - 1), "too_large"),
        ):
            with self.subTest(code=code, size=len(content)):
                path.write_bytes(content)
                self.assertEqual(self.call("bootstrap", ok=False)["code"], code)
                self.assertEqual(path.read_bytes(), content)
                self.assertFalse(self.store.exists())


if __name__ == "__main__":
    unittest.main()
