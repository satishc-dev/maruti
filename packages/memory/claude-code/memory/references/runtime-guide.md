# Direct helper invocation (API v1)

## Locate and probe

Use the real loaded skill path, not the caller's working directory. From
`<package-or-plugin-root>/skills/<name>/SKILL.md`, choose
`<package-or-plugin-root>/memory` when `memory/runtime/memory.py` exists
(installed payload), or the package root when `runtime/memory.py` exists
(canonical checkout). Both/neither is ambiguous or incomplete: stop, do not
choose an unrelated helper from PATH. This selected directory is
`<support-root>`; references are its `references/` directory.

Probe an available Python executable with `--version` and verify **Python
3.10 or newer** before use. Candidates may include `python3`, `python`, or on
Windows an installed `py -3` command; retain the exact successful executable
and any interpreter-selector argument. Failure or a missing interpreter means
report a runtime prerequisite and do not mutate. Do not assume Python exists,
install/download it, fetch consumer dependencies, or use a PowerShell/Bash
launcher or unsafe direct-write fallback. The plugin bundles its safe YAML
parser and license; no consumer pip/uv downloads are needed.

Invoke that interpreter directly with the helper path and explicit workspace.
Examples below are argument templates, not shell scripts. Replace placeholders
with actual absolute paths and use the host's path separators and argument-list
calling mechanism. Quote paths containing spaces. `<python>` means the probed
interpreter command, including a selector argument if needed, not a literal
filename containing a space.

## Commands

```text
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" doctor
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" bootstrap
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" discover --query "<focused question>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" discover --query "<focused question>" --topic "<exact-slug>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" discover --query "<focused question>" --session "<exact-id>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" read --path "topics/<slug>/<record>.md"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" write --path "topics/<slug>/<record>.md" --input "<private UTF-8 input file>" --expected "<sha256 or missing>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" catalog --topic "<slug>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" migration-preview
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" read --path "sessions/<session-id>/checkpoint.md"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" write --path "sessions/<session-id>/checkpoint.md" --input "<private UTF-8 input file>" --expected "<sha256 or missing>" --session "<session-id>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" --role shared doctor
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" --role shared bootstrap --allow-shared
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" --role shared read --path "topics/<slug>/<record>.md"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" --role shared write --path "topics/<slug>/<record>.md" --input "<private UTF-8 input file>" --expected "<sha256 or missing>" --allow-shared
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" --role shared catalog --topic "<slug>" --allow-shared
```

The default role is `local`. `discover` returns at most 8 candidates and 16000
total content characters per call; the [recall guide](recall-guide.md) applies
the aggregate pass budget across stores and follow-up reads. `read` returns
content and its `sha256`. `write` requires `--expected` equal to that hash or
`missing` for a new path; `--input` is a complete UTF-8 document prepared outside
the store. Session writes use `--path "sessions/<session-id>/checkpoint.md"` or
`observations.md` and require per-write `--session "<session-id>"` matching the
path. Session reads do not take `--session`. Use the real session identity, not
an invented shared identifier.

Discovery searches directory/concept filenames, not all record bodies.
Its mutually exclusive per-verb selectors `--topic <exact-slug>` and
`--session <exact-id>` inspect one exact directory without enumerating unrelated
topics/sessions. These read selectors do not authorize session writes and do
not change the 8-candidate/16000-character budgets.

Successful results include `scope: {"group":"topics","name":"<slug>"}` or
`scope: {"group":"sessions","name":"<id>"}` for a selected directory;
`scope: null` means broad discovery. `scan_complete: true` means the selected
name search finished, not that all matching records fit the output:
`more_candidates` still signals candidate-output truncation.

Broad discovery has a 512-entry directory/leaf scan budget. Exceeding it returns
`discovery_limit`, an explicit incomplete-scan error, not successful empty recall.
Narrow with an exact topic/session selector instead of retrying a broad scan.
If the selected directory itself exceeds 512 entries, use `read --path` for an
already known artifact within the recall budget; otherwise report the unresolved
lookup. Never interpret incomplete discovery as absence or bypass it by loading
the full store.

`--root` and `--role` are global options **before the verb**. Use `--role shared`
only for the optional shared store. Its `bootstrap`, `write`, and `catalog`
mutations require per-verb `--allow-shared`, plus the actual authorization/
ownership checks in the [sharing guide](sharing-guide.md); a CLI flag is not
user authorization.
Read-only shared operations do not need `--allow-shared`. Never guess a new verb
or an unsupported option.

`doctor` and `migration-preview` are read-only. `bootstrap` enables compatible
local capture and creates missing structure or idempotently adopts an existing
compatible identity, schema, and root catalog without overwrite. There is no
adoption flag: an existing unidentified directory, even empty or valid OKF,
refuses mutation. Refusal is not permission to relabel an ambiguous directory.
Local `bootstrap` also creates or appends a small managed section in workspace
`AGENTS.md` by default, as part of enablement authorization. Existing UTF-8 text,
including a BOM and established line endings, is preserved; no global files or
machine-specific plugin paths are used. The section names installed skills for
bounded recall, useful-boundary local capture, and substantial-work checkpoints,
while retaining existing ownership, authorization, and evidence-only rules.
The helper never copies complete skills or stored records into instructions.
Shared bootstrap does not inspect or edit this local pointer.

Local success includes `instructions: {"path":"AGENTS.md","status":"created",
"sha256":"..."}`; status may instead be `appended` or `present`. `sha256` covers
the complete instruction file. Rerunning bootstrap repairs a missing pointer
in a compatible store and is byte-idempotent when the pointer already matches.
The reserved delimiters are `<!-- maruti-memory:begin -->` and
`<!-- maruti-memory:end -->`. Modified, malformed, or duplicate managed sections,
or an existing unmarked `## Workspace Memory` section, return
`instructions_conflict` for explicit reconciliation, never silent replacement.
Unsafe redirects, read-only targets needing an append, invalid UTF-8, and files
exceeding 256 KiB including the section also refuse.

Preflight validates the store and instruction target before ignore/store writes.
The final instruction update uses confinement and byte-hash compare-and-swap,
not an overwrite of an unseen file. Atomicity remains per file: a late
`stale_write` or `instructions_io` can leave the local store enabled while
`AGENTS.md` setup is incomplete. The error says so; `doctor` reports store
enablement, not completion of instruction setup. Inspect and reconcile before
rerunning compatible bootstrap. Do not claim total success or attempt rollback.

`catalog` refreshes only the affected topic index, not a whole-store rebuild.
There is no separate pointer command, migration execution, delete command, or promotion command: skills
compose the supported operations within their authority.

## Result and conflict handling

Expect stdout JSON `{"ok": true, "data": {...}}` with exit 0, or
`{"ok": false, "error": {"code": "...", "message": "..."}}` with exit 2.
Check both the exit code and `ok`; parse failures, contradictory results, and
permission failures are errors, not success. Do not fabricate missing `data`
or claim a write succeeded because an input file exists.

Read before updating; retain the exact hash. A conflict requires rereading and
reconciling current content, not force-overwrite or blind retry. Unknown/newer
schema, unsafe paths, incompatible stores, and missing authorization must stop
the affected mutation. Do not edit store metadata or use another tool to bypass
a denial. Read back successful writes and check affected catalogs; report any
partial multi-file outcome honestly. Remove only the specific temporary input
file created for this operation after it is no longer needed.
