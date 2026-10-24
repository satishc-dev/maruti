"""Offline memory runtime behavior tests; run with Python's unittest runner."""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


PACKAGE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("memory_runtime", PACKAGE / "runtime" / "memory.py")
memory = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = memory
SPEC.loader.exec_module(memory)


def concept(title="A memory", extra=""):
    """Return an honestly unverified concept with a custom metadata key."""
    return (
        "---\ntype: Observation\ntitle: " + title + "\nstatus: draft\n"
        + extra + "---\n\n# " + title + "\n\nEvidence is unknown.\n"
    )


class RuntimeTests(unittest.TestCase):
    """Exercise filesystem invariants without package installs."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = self.root / ".maruti" / "memory" / "local"

    def tearDown(self):
        self.temporary.cleanup()

    def call(self, *args, ok=True):
        """Invoke the public CLI and assert its machine-readable envelope."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = memory.main(["--root", str(self.root), *args])
        response = json.loads(output.getvalue())
        self.assertEqual(response["ok"], ok, response)
        self.assertEqual(result, 0 if ok else 2, response)
        return response["data"] if ok else response["error"]

    def bootstrap(self):
        self.call("bootstrap")

    def write(self, path, content=None, expected="missing", *flags, ok=True):
        source = self.root / "input.md"
        source.write_text(content or concept(), encoding="utf-8", newline="\n")
        return self.call(
            "write", "--path", path, "--input", str(source),
            "--expected", expected, *flags, ok=ok,
        )

    def test_doctor_never_bootstraps(self):
        data = self.call("doctor")
        self.assertFalse(data["enabled"])
        self.assertFalse((self.root / ".maruti").exists())

    def test_bootstrap_is_idempotent_and_versions_are_independent(self):
        self.bootstrap()
        initial = (self.store / ".memory-store.json").read_bytes()
        self.call("bootstrap")
        self.assertEqual(initial, (self.store / ".memory-store.json").read_bytes())
        metadata = json.loads(initial)
        self.assertEqual(metadata["namespace"], "maruti.memory")
        self.assertEqual(metadata["schema_version"], 1)
        self.assertEqual(metadata["created_with"], memory.VERSION)
        self.assertEqual(memory.parse_document((self.store / "index.md").read_text())["okf_version"], "0.2")

    def test_unknown_directory_is_not_adopted_even_if_empty(self):
        self.store.mkdir(parents=True)
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unrecognized_store")
        self.assertEqual(list(self.store.iterdir()), [])

    def test_existing_okf_without_store_identity_is_read_only(self):
        self.store.mkdir(parents=True)
        (self.store / "index.md").write_text('---\nokf_version: "0.2"\n---\n')
        self.assertEqual(self.call("doctor")["recognition"], "okf-unmanaged")
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "unrecognized_store")

    def test_newer_and_noninteger_schemas_refuse_mutations_without_changes(self):
        self.bootstrap()
        meta = self.store / ".memory-store.json"
        original = json.loads(meta.read_text())
        for version in (2, True, "1", 0):
            metadata = dict(original, schema_version=version)
            meta.write_text(json.dumps(metadata))
            before = meta.read_bytes()
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "unsupported_schema")
            self.assertEqual(before, meta.read_bytes())
            self.assertEqual(self.call("migration-preview")["supported"], False)

    def test_wrong_role_namespace_or_identity_refuses_write(self):
        self.bootstrap()
        path = self.store / ".memory-store.json"
        initial = json.loads(path.read_text())
        for field, value in (("role", "shared"), ("namespace", "other"), ("store_id", "bad")):
            path.write_text(json.dumps(dict(initial, **{field: value})))
            self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "invalid_metadata")

    def test_compare_and_swap_and_unknown_keys_are_preserved(self):
        self.bootstrap()
        content = concept(extra="extension:\n  nested: [one, two]\n")
        first = self.write("topics/test/page.md", content)
        self.assertEqual(first["sha256"], hashlib.sha256(content.encode()).hexdigest())
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "stale_write")
        self.assertEqual(self.write("topics/test/page.md", expected=first["sha256"], ok=False)["code"], "metadata_loss")
        second = self.write("topics/test/page.md", content + "\nMore evidence.\n", first["sha256"])
        self.assertNotEqual(first["sha256"], second["sha256"])
        read = self.call("read", "--path", "topics/test/page.md")
        self.assertIn("nested: [one, two]", read["content"])
        self.assertEqual(read["sha256"], second["sha256"])

    def test_known_evidence_metadata_cannot_be_silently_removed(self):
        self.bootstrap()
        content = concept(extra="sources:\n  - {id: repo, resource: README.md}\n")
        first = self.write("topics/test/page.md", content)
        error = self.write("topics/test/page.md", concept(), first["sha256"], ok=False)
        self.assertEqual(error["code"], "metadata_loss")

    def test_shared_bootstrap_and_write_need_explicit_permission(self):
        self.assertEqual(self.call("--role", "shared", "bootstrap", ok=False)["code"], "shared_permission")
        self.call("--role", "shared", "bootstrap", "--allow-shared")
        source = self.root / "input.md"
        source.write_text(concept(), encoding="utf-8", newline="\n")
        args = ("--role", "shared", "write", "--path", "topics/test/page.md",
                "--input", str(source), "--expected", "missing")
        self.assertEqual(self.call(*args, ok=False)["code"], "shared_permission")
        self.call(*args, "--allow-shared")
        self.assertFalse(self.store.exists())

    def test_session_writes_require_exact_session_owner(self):
        self.bootstrap()
        for flags in ((), ("--session", "other")):
            error = self.write("sessions/session-a/checkpoint.md", None, "missing", *flags, ok=False)
            self.assertEqual(error["code"], "session_permission")
        self.write("sessions/session-a/checkpoint.md", None, "missing", "--session", "session-a")
        self.write("sessions/session-b/observations.md", None, "missing", "--session", "session-b")
        self.assertEqual(self.write("sessions/session-a/other.md", ok=False)["code"], "invalid_path")

    def test_path_traversal_and_reserved_file_writes_are_rejected(self):
        self.bootstrap()
        for path in ("../outside.md", "/absolute.md", "C:\\outside.md", "topics/../escape.md",
                     "topics/test/index.md", "index.md", ".memory-store.json", "topics/a/CON.md",
                     "topics/a/page.md ", "topics/a/page.md:stream"):
            self.assertEqual(self.write(path, ok=False)["code"], "invalid_path", path)

    def test_symlink_escape_is_rejected_without_reading_or_writing_target(self):
        self.bootstrap()
        outside = self.root / "outside"
        outside.mkdir()
        link = self.store / "topics" / "test"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Windows symlink creation requires Developer Mode or privilege")
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "unsafe_path")
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_lock_is_never_stolen(self):
        self.bootstrap()
        lock = self.store.parent / ".local.lock"
        lock.write_text("another-writer")
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "locked")
        self.assertEqual(lock.read_text(), "another-writer")

    def test_catalog_updates_only_one_topic_and_preserves_root(self):
        self.bootstrap()
        root_catalog = (self.store / "index.md").read_bytes()
        self.write("topics/test/z.md", concept("Zebra"))
        self.write("topics/test/a.md", concept("Alpha"))
        self.call("catalog", "--topic", "test")
        index = (self.store / "topics" / "test" / "index.md").read_text()
        self.assertFalse(index.startswith("---"))
        self.assertLess(index.index("Alpha"), index.index("Zebra"))
        self.assertIn("](/topics/test/a.md)", index)
        self.assertEqual(root_catalog, (self.store / "index.md").read_bytes())
        self.assertFalse((self.store / "log.md").exists())

    def test_discovery_is_targeted_bounded_and_deterministic(self):
        self.bootstrap()
        for i in range(12):
            self.write(f"topics/widgets/page-{i:02}.md", concept(f"Widget {i}") + "x" * 2500)
        self.write("topics/unrelated/page.md", concept("Unrelated"))
        first = self.call("discover", "--query", "widgets")
        second = self.call("discover", "--query", "widgets")
        self.assertEqual(first, second)
        self.assertEqual(len(first["candidates"]), 8)
        self.assertLessEqual(sum(len(item["content"]) for item in first["candidates"]), 16000)
        self.assertTrue(all("widgets" in item["path"] for item in first["candidates"]))
        self.assertEqual(self.call("discover", "--query", "notpresent")["candidates"], [])

    def test_discovery_does_not_load_unrelated_corrupt_concepts(self):
        self.bootstrap()
        self.write("topics/widgets/good.md")
        other = self.store / "topics" / "unrelated"
        other.mkdir()
        (other / "bad.md").write_text("not a concept")
        self.assertEqual(len(self.call("discover", "--query", "widgets")["candidates"]), 1)

    def test_invalid_yaml_and_invalid_okf_are_rejected_before_write(self):
        self.bootstrap()
        invalid = (
            "---\ntype: !!python/object/apply:os.system ['echo unsafe']\n---\n",
            "---\ntype: Observation\ntype: Decision\n---\n",
            "---\ntype: [Observation]\n---\n",
            concept(extra="generated: {at: '2026-10-23T10:00:00Z'}\n"),
            concept(extra="verified: {by: 'human:a', at: '2026-10-23'}\n"),
            concept(extra="generated: {by: maruti-memory/0.1.0, at: '2026-10-23T10:00:00'}\n"),
            concept(extra="sources: [{id: missing-resource}]\n"),
            concept() + "\nClaim.[^missing]\n",
            concept() + "\n[[wikilink]]\n",
        )
        for content in invalid:
            self.assertEqual(self.write("topics/test/page.md", content, ok=False)["code"], "invalid_document")
            self.assertFalse((self.store / "topics" / "test" / "page.md").exists())

    def test_external_editor_failure_is_reported_without_temp_leak(self):
        self.bootstrap()
        with patch.object(memory.os, "replace", side_effect=PermissionError("busy")):
            self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "io_error")
        self.assertFalse(list(self.store.rglob("*.tmp")))
        self.assertFalse((self.store.parent / ".local.lock").exists())

    def test_external_edit_before_final_hash_check_is_not_overwritten(self):
        self.bootstrap()
        target = self.store / "topics" / "test" / "page.md"

        def external_edit(_descriptor):
            target.write_bytes(b"external editor content")

        with patch.object(memory.os, "fsync", side_effect=external_edit):
            self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "stale_write")
        self.assertEqual(target.read_bytes(), b"external editor content")
        self.assertFalse(list(self.store.rglob("*.tmp")))

    def test_store_metadata_extensions_are_never_rewritten(self):
        self.bootstrap()
        path = self.store / ".memory-store.json"
        initial = json.loads(path.read_text())
        initial["future"] = {"opaque": ["retain", {"value": 17}]}
        path.write_text(json.dumps(initial, indent=3))
        original = path.read_bytes()
        self.call("bootstrap")
        self.write("topics/test/page.md")
        self.assertEqual(path.read_bytes(), original)

    def test_extension_fixture_and_generated_extensions_survive_updates(self):
        self.bootstrap()
        initial = (PACKAGE / "tests" / "fixtures" / "extension-concept.md").read_text(encoding="utf-8")
        first = self.write("topics/test/page.md", initial)
        replacement = initial.replace("19:47:17-07:00", "20:47:17-07:00") + "\nAdditional current evidence.\n"
        second = self.write("topics/test/page.md", replacement, first["sha256"])
        without_unknown = replacement.replace("  extension: preserve-me\n", "")
        self.assertEqual(self.write("topics/test/page.md", without_unknown, second["sha256"], ok=False)["code"],
                         "metadata_loss")

    def test_templates_are_typed_unverified_and_valid(self):
        for template in sorted((PACKAGE / "templates").glob("*.md")):
            content = template.read_text(encoding="utf-8")
            frontmatter = memory.validate_document(content, f"topics/templates/{template.name}")
            self.assertNotIn("verified", frontmatter)
            self.assertNotIn("sources", frontmatter)

    def test_parser_resource_limits_and_metadata_shapes(self):
        self.bootstrap()
        invalid = (
            "---\n- not-a-mapping\n---\n",
            "---\ntype: &alias Observation\nextension: *alias\n---\n",
            concept(extra="extension: " + "[" * 40 + "one" + "]" * 40 + "\n"),
            concept(extra="generated: null\n"),
            concept(extra="tags: text\n"),
            concept(extra="verified: []\n"),
            concept(extra="sources: wrong\n"),
            concept(extra="sources: [{resource: README.md, usage_window: {from: '2026-10-23T10:00:00Z'}}]\n"),
            concept(extra="usage_window: wrong\n"),
            concept(extra="last_modified: 2026-10-23\n"),
            concept(extra="custom: [2026-10-23]\n"),
        )
        for content in invalid:
            self.assertEqual(self.write("topics/test/page.md", content, ok=False)["code"], "invalid_document")

    def test_oversized_input_and_missing_target_are_explicit_failures(self):
        self.bootstrap()
        self.assertEqual(self.write("topics/test/page.md", concept() + "x" * memory.MAX_FILE_BYTES, ok=False)["code"],
                         "too_large")
        self.assertEqual(self.call("read", "--path", "topics/test/missing.md", ok=False)["code"], "not_found")
        self.assertEqual(self.call("catalog", "--topic", "missing", ok=False)["code"], "not_found")
        self.assertEqual(self.call("catalog", "--topic", "../outside", ok=False)["code"], "arguments")
        self.assertEqual(self.call("discover", "--query", "", ok=False)["code"], "arguments")

    def test_directory_budgets_fail_explicitly_instead_of_returning_false_success(self):
        self.bootstrap()
        self.write("topics/test/page.md")
        directory = self.store / "topics" / "test"
        for i in range(memory.MAX_ENTRIES):
            (directory / f"unread-{i:03}.txt").touch()
        self.assertEqual(self.call("discover", "--query", "test", ok=False)["code"], "discovery_limit")

    def test_conflicting_root_catalog_and_corrupt_identity_never_mutate(self):
        self.bootstrap()
        index = self.store / "index.md"
        index.write_text('---\nokf_version: "0.2"\ntype: Foreign\n---\n')
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "invalid_document")
        identity = self.store / ".memory-store.json"
        identity.write_text("{bad")
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "invalid_metadata")
        self.assertEqual(index.read_text(), '---\nokf_version: "0.2"\ntype: Foreign\n---\n')

    def test_invalid_root_and_missing_enablement_are_explicit(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = memory.main(["--root", str(self.root / "missing"), "doctor"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["error"]["code"], "invalid_root")
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "not_enabled")

    def test_metadata_duplicate_keys_and_nonfinite_json_are_rejected(self):
        self.bootstrap()
        identity = self.store / ".memory-store.json"
        for content in ('{"namespace":"foreign","namespace":"maruti.memory"}',
                        '{"future":NaN}', '{"future":1e9999}', '[]'):
            identity.write_text(content)
            self.assertEqual(self.call("doctor", ok=False)["code"], "invalid_metadata")

    def test_metadata_history_order_duplicates_and_scalar_types_are_preserved(self):
        self.bootstrap()
        content = concept(extra="extension: {flag: true, history: [first, first, second]}\n")
        first = self.write("topics/test/page.md", content)
        for changed in (
            content.replace("flag: true", "flag: 1"),
            content.replace("[first, first, second]", "[first, second]"),
            content.replace("[first, first, second]", "[second, first, first]"),
        ):
            self.assertEqual(self.write("topics/test/page.md", changed, first["sha256"], ok=False)["code"],
                             "metadata_loss")

    def test_read_only_doctor_reports_incomplete_and_future_stores(self):
        self.bootstrap()
        identity = self.store / ".memory-store.json"
        initial = json.loads(identity.read_text())
        identity.write_text(json.dumps(dict(initial, schema_version=2)))
        before = identity.read_bytes()
        data = self.call("doctor")
        self.assertFalse(data["enabled"])
        self.assertEqual(data["issues"][0]["code"], "unsupported_schema")
        self.assertEqual(identity.read_bytes(), before)
        identity.write_text(json.dumps(initial))
        (self.store / "index.md").unlink()
        data = self.call("doctor")
        self.assertFalse(data["enabled"])
        self.assertEqual(data["issues"][0]["code"], "invalid_document")

    def test_invalid_utf8_and_unclosed_frontmatter_are_explicit(self):
        self.bootstrap()
        source = self.root / "input.md"
        source.write_bytes(b"\xff")
        error = self.call("write", "--path", "topics/test/page.md", "--input", str(source),
                          "--expected", "missing", ok=False)
        self.assertEqual(error["code"], "invalid_document")
        for content in ("not frontmatter", "---\ntype: Observation\n", concept() + "\x00"):
            self.assertEqual(self.write("topics/test/page.md", content, ok=False)["code"], "invalid_document")
        self.assertEqual(self.write("topics/test/page.md", expected="bad-hash", ok=False)["code"], "arguments")
        self.assertEqual(self.call("read", "--path", ".memory-store.json", ok=False)["code"], "invalid_path")

    def test_valid_source_authors_verification_lists_and_usage_windows(self):
        self.bootstrap()
        content = concept(extra=(
            "generated: {by: maruti-memory/0.1.0, at: '2026-10-23T10:00:00Z'}\n"
            "verified:\n  - {by: 'process:fixture-check', at: '2026-10-23T11:00:00+00:00'}\n"
            "sources:\n  - {id: fixture, resource: README.md, author: 'team:fixture'}\n"
            "usage_window: {from: '2026-10-22T00:00:00Z', to: '2026-10-23T00:00:00Z'}\n"
        )) + "\nFixture claim.[^fixture]\n\n[^fixture]: Fixture example only.\n"
        self.write("topics/test/page.md", content)
        for changed in (
            content.replace("maruti-memory/0.1.0", "bad actor"),
            content.replace("team:fixture", "bad actor"),
            content.replace("10:00:00Z", "bad-time"),
            content.replace("id: fixture", "id: ''"),
            content.replace("status: draft", "status: done"),
        ):
            self.assertEqual(self.write("topics/test/invalid.md", changed, ok=False)["code"], "invalid_document")

    def test_catalog_encodes_links_and_refuses_frontmatter_in_nested_index(self):
        self.bootstrap()
        self.write("topics/test/a (detail).md", concept("Detailed [title]"))
        self.call("catalog", "--topic", "test")
        index = self.store / "topics" / "test" / "index.md"
        self.assertIn("](/topics/test/a%20%28detail%29.md)", index.read_text())
        index.write_text(" ---\ntype: Foreign\n---\n")
        original = index.read_bytes()
        self.assertEqual(self.call("catalog", "--topic", "test", ok=False)["code"], "invalid_document")
        self.assertEqual(index.read_bytes(), original)

    def test_directory_input_is_rejected_before_reading(self):
        self.bootstrap()
        error = self.call("write", "--path", "topics/test/page.md", "--input", str(self.root),
                          "--expected", "missing", ok=False)
        self.assertEqual(error["code"], "unsafe_path")

    def test_failed_git_inspection_and_missing_git_never_create_private_content(self):
        (self.root / ".git").mkdir(exist_ok=True)
        with patch.object(memory.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "prerequisite")
        with patch.object(memory.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 15)):
            self.assertEqual(self.call("bootstrap", ok=False)["code"], "git_error")
        self.assertFalse(self.store.exists())

    def test_cli_argument_errors_use_json_not_argparse_exit(self):
        self.assertEqual(self.call("write", ok=False)["code"], "arguments")


class BundledDependencyTests(unittest.TestCase):
    """Verify installed parser bytes and explicit offline prerequisite failures."""

    def test_manifest_matches_every_bundled_source_and_license(self):
        vendor = PACKAGE / "vendor"
        manifest = json.loads((vendor / "manifest.json").read_text())
        self.assertEqual(manifest["commit"], "49790e73684bebad1df05ef8d828fa12f685bffb")
        self.assertEqual(manifest["version"], "6.0.3")
        self.assertEqual(manifest["license_sha256"], memory.digest((vendor / "LICENSE-PyYAML").read_bytes()))
        self.assertEqual(len(manifest["files"]), 16)
        for record in manifest["files"]:
            content = (vendor / record["path"]).read_bytes()
            self.assertEqual(memory.digest(content), record["sha256"])
            blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            self.assertEqual(blob, record["git_blob_sha1"])
        self.assertEqual(memory.yaml_module().__version__, "6.0.3")
        self.assertFalse(memory.yaml_module().__with_libyaml__)

    def test_missing_bundle_refuses_ambient_yaml_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(memory, "_YAML", None), patch.object(memory, "PACKAGE", Path(temporary)):
                with self.assertRaises(memory.MemoryError) as caught:
                    memory.yaml_module()
            self.assertEqual(caught.exception.code, "prerequisite")

    def test_missing_python_and_broken_parser_have_prerequisite_errors(self):
        with patch.object(memory.sys, "version_info", (3, 9)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = memory.main([])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["error"]["code"], "prerequisite")
        with patch.object(memory, "_YAML", None):
            with patch("importlib.machinery.SourceFileLoader.exec_module", side_effect=ImportError("missing")):
                with self.assertRaises(memory.MemoryError) as caught:
                    memory.yaml_module()
            self.assertEqual(caught.exception.code, "prerequisite")

    def test_parser_import_never_creates_bytecode_during_preflight(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            shutil.copytree(PACKAGE / "vendor" / "yaml", target / "vendor" / "yaml",
                            ignore=shutil.ignore_patterns("__pycache__"))
            with patch.object(memory, "_YAML", None), patch.object(memory, "PACKAGE", target):
                memory.yaml_module()
            self.assertFalse(list(target.rglob("*.pyc")))

    def test_cli_runs_without_any_network_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = (
                "import importlib.util, socket, sys\n"
                "def blocked(*args, **kwargs): raise AssertionError('network forbidden')\n"
                "socket.socket = blocked\n"
                "spec = importlib.util.spec_from_file_location('memory_runtime', sys.argv[1])\n"
                "module = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(module)\n"
                "sys.exit(module.main(['--root', sys.argv[2], 'bootstrap']))\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script, str(PACKAGE / "runtime" / "memory.py"), temporary],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_relocated_installed_layout_is_self_contained(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            support = root / "plugin" / "memory"
            shutil.copytree(PACKAGE / "runtime", support / "runtime",
                            ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(PACKAGE / "vendor", support / "vendor",
                            ignore=shutil.ignore_patterns("__pycache__"))
            workspace = root / "workspace"
            workspace.mkdir()
            helper = support / "runtime" / "memory.py"
            for flags in (("doctor",), ("bootstrap",),
                          ("--role", "shared", "bootstrap", "--allow-shared")):
                result = subprocess.run(
                    [sys.executable, "-I", "-B", str(helper), "--root", str(workspace), *flags],
                    capture_output=True, text=True, encoding="utf-8", check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(json.loads(result.stdout)["ok"])
            self.assertFalse(list(support.rglob("*.pyc")))


@unittest.skipUnless(shutil.which("git"), "Git is required for transition tests")
class GitTransitionTests(unittest.TestCase):
    """Preserve non-Git knowledge while explicitly enabling Git privacy."""

    setUp = RuntimeTests.setUp
    tearDown = RuntimeTests.tearDown
    call = RuntimeTests.call
    bootstrap = RuntimeTests.bootstrap
    write = RuntimeTests.write

    def initialize_git(self):
        result = subprocess.run(
            ["git", "-C", str(self.root), "init", "--quiet"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def snapshot(self):
        return {path.relative_to(self.store): path.read_bytes()
                for path in self.store.rglob("*") if path.is_file()}

    def test_explicit_bootstrap_repairs_privacy_after_git_init_without_rewriting_store(self):
        self.bootstrap()
        first = self.write("topics/test/existing.md")
        original = self.snapshot()
        self.assertFalse((self.root / ".gitignore").exists())
        self.initialize_git()
        self.assertEqual(self.write("topics/test/new.md", ok=False)["code"], "privacy_not_ignored")
        ignore = self.root / ".gitignore"
        ignore.write_bytes(b"# Preserve existing rules\r\n*.scratch")
        data = self.call("bootstrap")
        self.assertFalse(data["created"])
        self.assertEqual(ignore.read_bytes(), b"# Preserve existing rules\r\n*.scratch\n/.maruti/memory/local/\n")
        self.assertEqual(self.snapshot(), original)
        self.assertEqual(self.call("read", "--path", "topics/test/existing.md")["sha256"], first["sha256"])
        self.write("topics/test/new.md")
        self.assertTrue(self.call("doctor")["enabled"])

    def test_transition_rejects_tracked_contents_before_modifying_ignore_or_store(self):
        self.bootstrap()
        self.write("topics/test/existing.md")
        original = self.snapshot()
        self.initialize_git()
        result = subprocess.run(
            ["git", "-C", str(self.root), "add", ".maruti/memory/local/topics/test/existing.md"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "tracked_local")
        self.assertFalse((self.root / ".gitignore").exists())
        self.assertEqual(self.snapshot(), original)

    def test_transition_preserves_conflicting_ignore_rules_and_refuses_bootstrap(self):
        self.bootstrap()
        self.write("topics/test/existing.md")
        original = self.snapshot()
        self.initialize_git()
        ignore = self.root / ".gitignore"
        rules = b"/.maruti/memory/local/\n!/.maruti/memory/local/\n"
        ignore.write_bytes(rules)
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "privacy_not_ignored")
        self.assertEqual(ignore.read_bytes(), rules)
        self.assertEqual(self.snapshot(), original)


class GrowingStoreTests(unittest.TestCase):
    """Keep privacy and exact recall usable as unrelated history accumulates."""

    setUp = RuntimeTests.setUp
    tearDown = RuntimeTests.tearDown
    call = RuntimeTests.call
    bootstrap = RuntimeTests.bootstrap
    write = RuntimeTests.write

    def populate_history(self):
        self.bootstrap()
        for topic in range(12):
            directory = self.store / "topics" / f"history-{topic:02}"
            directory.mkdir()
            for page in range(48):
                (directory / f"page-{page:02}.md").write_bytes(concept().encode())
        self.write("topics/relevant/target.md", concept("Relevant current evidence"))

    def test_exact_topic_scope_bypasses_unrelated_records_and_reports_scope(self):
        self.populate_history()
        traversed = []
        original_entries = memory.entries

        def record_entries(path):
            traversed.append(path.relative_to(self.store).as_posix())
            return original_entries(path)

        with patch.object(memory, "entries", side_effect=record_entries):
            data = self.call("discover", "--query", "target", "--topic", "relevant")
        self.assertEqual(traversed, ["topics/relevant"])
        self.assertEqual(data["scope"], {"group": "topics", "name": "relevant"})
        self.assertEqual([item["path"] for item in data["candidates"]], ["topics/relevant/target.md"])
        self.assertLessEqual(sum(len(item["content"]) for item in data["candidates"]), 16000)
        self.assertLessEqual(len(data["candidates"]), 8)

    def test_broad_search_over_budget_is_explicitly_incomplete_and_can_be_narrowed(self):
        self.populate_history()
        error = self.call("discover", "--query", "page", ok=False)
        self.assertEqual(error["code"], "discovery_limit")
        self.assertIn("--topic", error["message"])
        narrowed = self.call("discover", "--query", "page", "--topic", "history-11")
        self.assertEqual(len(narrowed["candidates"]), 8)
        self.assertTrue(narrowed["more_candidates"])

    def test_exact_scope_does_not_enumerate_an_oversized_namespace(self):
        self.bootstrap()
        topics = self.store / "topics"
        for i in range(memory.MAX_ENTRIES + 1):
            (topics / f"topic-{i:03}").mkdir()
        self.write("topics/relevant/target.md")
        self.assertEqual(self.call("discover", "--query", "target", ok=False)["code"], "discovery_limit")
        result = self.call("discover", "--query", "target", "--topic", "relevant")
        self.assertEqual(len(result["candidates"]), 1)

    def test_exact_session_scope_is_bounded_and_needs_no_write_permission(self):
        self.populate_history()
        self.write("sessions/task-a/checkpoint.md", None, "missing", "--session", "task-a")
        result = self.call("discover", "--query", "checkpoint", "--session", "task-a")
        self.assertEqual(result["scope"], {"group": "sessions", "name": "task-a"})
        self.assertEqual([item["path"] for item in result["candidates"]], ["sessions/task-a/checkpoint.md"])
        self.assertEqual(self.call("discover", "--query", "checkpoint", "--session", "../escape", ok=False)["code"],
                         "arguments")
        self.assertEqual(self.call("discover", "--query", "target", "--topic", "missing", ok=False)["code"],
                         "not_found")
        self.assertEqual(self.call("discover", "--query", "target", "--topic", "relevant",
                                   "--session", "task-a", ok=False)["code"], "arguments")

    def test_oversized_single_topic_remains_readable_with_known_path(self):
        self.bootstrap()
        directory = self.store / "topics" / "large"
        directory.mkdir()
        for i in range(memory.MAX_ENTRIES + 1):
            (directory / f"page-{i:03}.md").write_bytes(concept().encode())
        self.write("topics/large/new.md")
        error = self.call("discover", "--query", "new", "--topic", "large", ok=False)
        self.assertEqual(error["code"], "discovery_limit")
        self.assertIn("read --path", error["message"])
        read = self.call("read", "--path", "topics/large/new.md")
        self.assertEqual(read["content"], concept())

    @unittest.skipUnless(shutil.which("git"), "Git is required for privacy growth tests")
    def test_git_privacy_and_new_writes_stay_usable_above_512_ignored_records(self):
        initialized = subprocess.run(
            ["git", "-C", str(self.root), "init", "--quiet"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.populate_history()
        with patch.object(memory, "entries", side_effect=AssertionError("privacy must not enumerate ignored knowledge")):
            self.assertTrue(self.call("doctor")["enabled"])
            self.call("bootstrap")
            self.write("topics/relevant/next.md")
        self.call("catalog", "--topic", "relevant")
        result = self.call("discover", "--query", "relevant", "--topic", "relevant")
        self.assertEqual(len(result["candidates"]), 2)
        status = subprocess.run(
            ["git", "-C", str(self.root), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertNotIn(".maruti/memory/local", status.stdout)

    @unittest.skipUnless(shutil.which("git"), "Git is required for privacy growth tests")
    def test_effective_unignored_inspection_failure_refuses_new_capture(self):
        initialized = subprocess.run(
            ["git", "-C", str(self.root), "init", "--quiet"],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.bootstrap()
        original_git = memory.git

        def failed_unignored(root, *args, **kwargs):
            if "--others" in args:
                return subprocess.CompletedProcess(args, 1, stdout="", stderr="inspection failed")
            return original_git(root, *args, **kwargs)

        with patch.object(memory, "git", side_effect=failed_unignored):
            self.assertEqual(self.write("topics/relevant/new.md", ok=False)["code"], "git_error")
        self.assertFalse((self.store / "topics" / "relevant" / "new.md").exists())


@unittest.skipUnless(shutil.which("git"), "Git is required for privacy integration tests")
class GitPrivacyTests(RuntimeTests):
    """Repeat runtime coverage inside a real Git repository, plus ignore checks."""

    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.root), *args], capture_output=True, text=True,
            encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_git_bootstrap_appends_anchor_and_proves_ignored(self):
        ignore = self.root / ".gitignore"
        ignore.write_text("# Keep this rule\n*.scratch")
        self.bootstrap()
        self.assertEqual(ignore.read_text(), "# Keep this rule\n*.scratch\n/.maruti/memory/local/\n")
        self.assertEqual(self.git("check-ignore", ".maruti/memory/local/topics/a/page.md").strip(),
                         ".maruti/memory/local/topics/a/page.md")
        self.assertNotIn(".maruti/memory/local", self.git("status", "--porcelain", "--untracked-files=all"))

    def test_later_ignore_negation_refuses_private_store_before_creation(self):
        (self.root / ".gitignore").write_text("/.maruti/memory/local/\n!/.maruti/memory/local/\n")
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "privacy_not_ignored")
        self.assertFalse(self.store.exists())

    def test_tracked_local_content_refuses_bootstrap(self):
        self.store.mkdir(parents=True)
        (self.store / "existing.md").write_text("private")
        self.git("add", ".maruti/memory/local/existing.md")
        self.assertEqual(self.call("bootstrap", ok=False)["code"], "tracked_local")
        self.assertFalse((self.store / ".memory-store.json").exists())

    def test_removing_ignore_after_enablement_blocks_writes(self):
        self.bootstrap()
        (self.root / ".gitignore").write_text("")
        self.assertEqual(self.write("topics/test/page.md", ok=False)["code"], "privacy_not_ignored")
        self.assertFalse((self.store / "topics" / "test" / "page.md").exists())

    def test_specific_existing_file_negation_is_reported_before_other_capture(self):
        self.bootstrap()
        self.write("topics/test/existing.md")
        (self.root / ".gitignore").write_text(
            "/.maruti/memory/local/\n"
            "!/.maruti/memory/local/\n"
            "/.maruti/memory/local/*\n"
            "!/.maruti/memory/local/topics/\n"
            "/.maruti/memory/local/topics/*\n"
            "!/.maruti/memory/local/topics/test/\n"
            "/.maruti/memory/local/topics/test/*\n"
            "!/.maruti/memory/local/topics/test/existing.md\n"
        )
        data = self.call("doctor")
        self.assertFalse(data["enabled"])
        self.assertEqual(data["issues"][0]["code"], "privacy_not_ignored")
        self.assertEqual(self.write("topics/test/new.md", ok=False)["code"], "privacy_not_ignored")
        self.assertFalse((self.store / "topics" / "test" / "new.md").exists())

    def test_worktree_git_file_and_subdirectory_root_discovery(self):
        self.git("-c", "user.name=Memory Test", "-c", "user.email=test@example.invalid",
                 "commit", "--quiet", "--allow-empty", "-m", "initial")
        worktree = self.root / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "test-worktree", str(worktree))
        nested = worktree / "nested"
        nested.mkdir()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = memory.main(["--root", str(nested), "bootstrap"])
        self.assertEqual(code, 0, output.getvalue())
        self.assertTrue((worktree / ".git").is_file())
        self.assertTrue((worktree / ".maruti" / "memory" / "local" / ".memory-store.json").exists())
        self.assertFalse((nested / ".maruti").exists())
        self.git("worktree", "remove", "--force", str(worktree))


if __name__ == "__main__":
    unittest.main()
