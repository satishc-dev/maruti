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
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" read --path "topics/<slug>/<record>.md"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" write --path "topics/<slug>/<record>.md" --input "<private UTF-8 input file>" --expected "<sha256 or missing>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" catalog --topic "<slug>"
"<python>" "<support-root>/runtime/memory.py" --root "<workspace>" migration-preview
```

The default role is `local`. `discover` returns at most 8 candidates and 16000
total content characters per call; the [recall guide](recall-guide.md) applies
the aggregate pass budget across stores and follow-up reads. `read` returns
content and its `sha256`. `write` requires `--expected` equal to that hash or
`missing` for a new path; `--input` is a complete UTF-8 document prepared outside
the store. Session writes use `--path "sessions/<session-id>/checkpoint.md"` or
`observations.md`, with `--session "<session-id>"` where required by the helper.
Use the real session identity, not an invented shared identifier.

Use `--role shared` only for the optional shared store. Shared mutations also
require `--allow-shared`, plus the actual authorization/ownership checks in the
[sharing guide](sharing-guide.md); a CLI flag is not user authorization.
Inspect the installed helper's `--help` for option placement before adding
role/authorization flags; never guess a new verb or an unsupported option.

`doctor` and `migration-preview` are read-only. `bootstrap` enables compatible
local capture and creates/adopts compatible structure without overwrite;
refusal is not permission to relabel an ambiguous directory. `catalog` refreshes
only the affected topic index, not a whole-store rebuild. There is no pointer
command, migration execution, delete command, or promotion command: skills
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
