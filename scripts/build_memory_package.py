#!/usr/bin/env python3
"""Compose offline Memory plugins from canonical sources without symlinks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
PAYLOAD_ROOTS = ("runtime", "vendor", "contracts", "templates", "references")
INSTALL_ROOTS = (
    "packages/memory/github-copilot",
    "packages/memory/claude-code",
    "packages/software-team/github-copilot",
)
MANIFEST = ".memory-package.json"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _safe_path(root: Path, relative: str) -> Path:
    """Reject traversal and symlink ancestors, including dangling links."""
    if root.is_symlink():
        raise ValueError(f"Output root must not be a symlink: {root}")
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(
        part in ("", ".", "..") or ":" in part or "\\" in part
        for part in path.parts
    ):
        raise ValueError(f"Unsafe generated path: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink in generated path: {current}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Generated path escapes output: {relative}")
    return current


def _source_files(root: Path) -> dict[str, bytes]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"Canonical directory missing or symlinked: {root}")
    files = {}
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Canonical source must not be a symlink: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    if not files:
        raise ValueError(f"Canonical directory is empty: {root}")
    return files


def expected_files(repo_root: Path) -> dict[str, bytes]:
    """Compute deterministic payloads and explicit identical mirror groups."""
    canonical = repo_root / "packages" / "memory"
    payload = {}
    for name in PAYLOAD_ROOTS:
        for relative, content in _source_files(canonical / name).items():
            payload[f"memory/{name}/{relative}"] = content
    skills = _source_files(canonical / "skills")
    names = sorted(
        path.split("/")[0] for path in skills if path.count("/") == 1
        and path.endswith("/SKILL.md")
    )
    if not names or any(path.split("/")[0] not in names for path in skills):
        raise ValueError("Each canonical skill needs its own <name>/SKILL.md")
    payload.update({f"skills/{path}": content for path, content in skills.items()})
    hashes = {
        path: hashlib.sha256(content).hexdigest()
        for path, content in sorted(payload.items())
    }
    manifest = _json_bytes({
        "generator": "scripts/build_memory_package.py",
        "plugin_version": VERSION,
        "schema_version": 1,
        "files": hashes,
    })
    expected = {}
    for install in INSTALL_ROOTS:
        expected.update({f"{install}/{path}": content for path, content in payload.items()})
        expected[f"{install}/{MANIFEST}"] = manifest
    groups = []
    for name in names:
        groups.append({
            "source": f"packages/memory/github-copilot/skills/{name}",
            "identical": [f"packages/software-team/github-copilot/skills/{name}"],
        })
    expected["packages/memory/composition/mirrors.json"] = _json_bytes({
        "generator": "scripts/build_memory_package.py",
        "schema_version": 1,
        "groups": groups,
    })
    return expected


def compose(repo_root: Path, output_root: Path, *, check: bool = False) -> list[str]:
    """Check or update only generated files; refuse unknown/modified collisions."""
    expected = expected_files(repo_root)
    declaration = _safe_path(output_root, "packages/memory/composition/mirrors.json")
    if declaration.exists():
        if not declaration.is_file():
            raise ValueError(f"Composed mirror declaration collision: {declaration}")
        data = json.loads(declaration.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or (
            data.get("generator") != "scripts/build_memory_package.py"
            or data.get("schema_version") != 1
        ):
            raise ValueError(f"Unknown composed mirror declaration: {declaration}")
    previous = {}
    for install in INSTALL_ROOTS:
        path = _safe_path(output_root, f"{install}/{MANIFEST}")
        if path.exists():
            manifest = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(manifest, dict) or (
                manifest.get("generator") != "scripts/build_memory_package.py"
                or manifest.get("schema_version") != 1
                or not isinstance(manifest.get("files"), dict)
            ):
                raise ValueError(f"Unknown composition manifest: {path}")
            for name, digest in manifest["files"].items():
                if not isinstance(name, str) or not (
                    name.startswith("memory/") or name.startswith("skills/")
                ):
                    raise ValueError(f"Unmanaged manifest entry: {name}")
                if not isinstance(digest, str) or len(digest) != 64 or any(
                    character not in "0123456789abcdef" for character in digest
                ):
                    raise ValueError(f"Invalid manifest digest: {name}")
                relative = f"{install}/{name}"
                _safe_path(output_root, relative)
                previous[relative] = digest
    for install in INSTALL_ROOTS:
        prefixes = {f"{install}/memory"}
        for relative in expected.keys() | previous.keys():
            prefix = f"{install}/skills/"
            if relative.startswith(prefix):
                prefixes.add(prefix + relative[len(prefix):].split("/")[0])
        for prefix in prefixes:
            directory = _safe_path(output_root, prefix)
            if directory.exists() and not directory.is_dir():
                raise ValueError(f"Generated directory collision: {directory}")
            if not directory.is_dir():
                continue
            for path in directory.rglob("*"):
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                relative = path.relative_to(output_root).as_posix()
                _safe_path(output_root, relative)
                if path.is_file() and relative not in expected and relative not in previous:
                    raise ValueError(f"Unknown file in generated payload: {path}")
    changes = []
    removals = []
    for relative, content in expected.items():
        path = _safe_path(output_root, relative)
        if path.is_file() and path.read_bytes() == content:
            continue
        if path.exists():
            managed_metadata = relative.endswith("/" + MANIFEST) or relative == (
                "packages/memory/composition/mirrors.json"
            )
            if managed_metadata and not path.is_file():
                raise ValueError(f"Refusing generated metadata directory collision: {path}")
            if not managed_metadata and (
                not path.is_file() or relative not in previous
                or hashlib.sha256(path.read_bytes()).hexdigest() != previous[relative]
            ):
                raise ValueError(f"Refusing unknown or edited generated collision: {path}")
        changes.append(relative)
    for relative, digest in previous.items():
        if relative in expected:
            continue
        path = _safe_path(output_root, relative)
        if path.exists():
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Refusing to remove edited generated file: {path}")
            removals.append(relative)
    if check:
        return sorted(changes + removals)
    for relative in changes:
        path = _safe_path(output_root, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".memory-build-tmp")
        with temporary.open("xb") as stream:
            stream.write(expected[relative])
        os.replace(temporary, path)
    for relative in removals:
        path = _safe_path(output_root, relative)
        path.unlink()
        parent = path.parent
        install_root = next(
            output_root / install for install in INSTALL_ROOTS
            if path.is_relative_to(output_root / install)
        )
        while parent != install_root and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    return sorted(changes + removals)


def main(argv: list[str] | None = None) -> int:
    """Build the current checkout, or stage payloads in an empty output tree."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    try:
        changes = compose(REPO_ROOT, args.output_root.resolve(), check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Memory composition failed: {exc}", file=sys.stderr)
        return 2
    if args.check and changes:
        print("Memory composition drift:\n" + "\n".join(changes), file=sys.stderr)
        return 1
    print(f"Memory composition {'checked' if args.check else 'built'}: {len(changes)} changed file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
