# Memory runtime v1

The independently installed Memory package is version **0.1.0**. Its offline
helper is `runtime/memory.py`, requiring an existing Python **3.10 or later**
and Git only when the workspace is a Git repository. No consumer operation
downloads or installs anything. A missing interpreter must be reported by the
calling skill as an explicit prerequisite, not repaired automatically.

## CLI

```text
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] doctor
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] bootstrap [--allow-shared]
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] discover --query <text>
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] read --path <relative.md>
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] write --path <relative.md> --input <utf8-file> --expected <sha256|missing> [--session <id>] [--allow-shared]
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] catalog --topic <slug> [--allow-shared]
python <install-root>/runtime/memory.py --root <workspace> [--role local|shared] migration-preview
```

Global flags precede the command. `local` is the default role. Commands return
one JSON object to stdout: `{"ok":true,"data":{...}}`, exit 0, or
`{"ok":false,"error":{"code":"...","message":"..."}}`, exit 2. Errors do not
print concept content. There is no deletion, migration execution, Git staging,
commit, push, embedding, background service, scheduler, or dependency installer.
`doctor` and `migration-preview` are read-only, including for unknown schemas.

`--root` is an existing workspace directory. In Git, discovery uses
`git rev-parse --show-toplevel`; a worktree `.git` file is supported. Outside
Git, the supplied directory is the workspace root. Helpers never write
`.project-memory/` or arbitrary user-provided store roots.

## Stores and ownership

```text
.maruti/memory/
  .local.lock                     # transient exclusive helper lock
  local/                          # anchored Git ignore required before content
    .memory-store.json
    index.md                      # OKF 0.2 root catalog
    topics/<slug>/<concept>.md
    topics/<slug>/index.md         # topic-local derived catalog
    sessions/<session-id>/checkpoint.md
    sessions/<session-id>/observations.md
  shared/                         # optional, explicitly curated
    .memory-store.json
    index.md
    topics/<slug>/<concept>.md
```

Bootstrap is explicit enablement of automatic local capture by skills.
No separate config file exists in v1. Shared bootstrap, writes, and catalog
updates require `--allow-shared` on that invocation. Passing the flag is a
mechanical permission, not proof of stakeholder consent: skills must obtain
explicit shared-promotion intent. Session writes require a matching `--session`
and only the two named files; session IDs are non-secret caller-selected slugs,
not an authentication boundary. Shared stores do not accept session captures.

`.memory-store.json` is a JSON object outside OKF frontmatter:

```json
{
  "namespace": "maruti.memory",
  "schema_version": 1,
  "store_id": "<unique UUID>",
  "role": "local",
  "created_with": "0.1.0"
}
```

Plugin version, integer store schema, and OKF version are independent.
Unknown metadata is retained unchanged. Missing identity, foreign identity,
wrong role, invalid UUID, and unknown/newer schema refuse mutation. Existing
OKF bundles without this identity are recognized as unmanaged, never adopted
or overwritten. Empty pre-existing directories are not adopted either.
Migration preview explains this state; execution is deliberately unsupported.

## Safety and bounded recall

Bootstrap appends `/.maruti/memory/local/` to the workspace `.gitignore`,
preserving all existing bytes and rules. It rejects tracked local content
and proves effective exclusion with `git check-ignore` **before** creating
private content. An existing anchor with a later negation is an explicit
failure. Every local mutation rechecks effective exclusion and tracked content;
rerunning compatible local bootstrap may establish the anchored ignore rule
after a non-Git workspace becomes a Git repository, without rewriting the
store identity or knowledge. Non-Git bootstrap never creates `.gitignore`.
existing local paths are also checked, with an explicit 512-entry/16-level
privacy-inspection limit rather than silently skipping an oversized tree.
Git-ignored means ignored in that Git worktree, not encrypted or private from
other processes, filesystem users, backups, or consumer tools.

All store paths are confined, reject traversal, Windows device names and
alternate streams, and reject symbolic links/junctions/reparse redirects.
Concept files have a 256 KiB UTF-8 limit; metadata and catalog work are bounded.
Discovery searches only named topic/session directories matching query tokens,
not the whole repository or all concept bodies. At most 8 candidates and
16,000 total content characters are returned, with explicit truncation flags.
No match means no candidates; it does not fall back to broad loading.

Writes need the SHA-256 returned by `read`, or literal `missing` for creation.
The helper locks the selected store, rechecks the expected bytes, validates the
complete replacement, and atomically replaces a single file. Unknown metadata
and existing source/verification/history metadata cannot be silently removed
or changed. An intentional semantic revision of existing evidence is a skill
decision, not automatic conflict resolution; v1 fails closed when its
preservation guard cannot express that revision.

There is no global capture log. `catalog --topic` derives only one topic's
catalog, including root-relative links; it does not rewrite the root catalog
or another topic. The initial root catalog links to the topic/session areas.
Root catalogs are not claim evidence.

The exclusive lock coordinates **cooperating helper processes only**. Locks
are never automatically stolen; a crashed writer requires an operator to
inspect and remove the exact stale lock. External editors do not honor locks.
The last hash recheck narrows but cannot eliminate the external-editor race
between that check and replace. Symlink/path checks similarly assume no
hostile concurrent filesystem actor. Atomicity is per file, not across
bootstrap identity/catalog or concepts/catalogs. Interrupted bootstrap is
reported as an incompatible partial directory, not silently recovered. Failed
catalog updates leave canonical concepts intact and can be explicitly retried.
