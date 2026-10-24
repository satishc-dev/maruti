# Memory for GitHub Copilot

```text
copilot plugin marketplace add satishc-dev/maruti
copilot plugin install memory@maruti
```

For an unpublished local checkout, run from its repository root:

```text
copilot --plugin-dir ".\packages\memory\github-copilot" plugin list --json
copilot --plugin-dir ".\packages\memory\github-copilot" skill list --json
copilot --plugin-dir ".\packages\memory\github-copilot"
```

These mounts are per-process, not persistent installs. Start a new interactive
session with the last command; a previously running session will not acquire the
mount. Marketplace installs use published remote content, not unpushed changes.
The root `plugin.json` is required by Copilot's loader; a marketplace entry alone
is not a plugin manifest.

Load the Memory skills for bootstrap, capture, recall, checkpoints, consolidation,
and promotion. Resolve the actual loaded skill path, follow repository mirrors,
and find the helper at `<plugin-root>\memory\runtime\memory.py`.
Do not assume the marketplace name or an installation under a particular home
directory. Invoke Python directly; no shell wrapper or MCP service is needed.

Local bootstrap automatically creates or appends a small managed `AGENTS.md`
section in the consuming workspace. No hand-written pointer is needed. Existing
instructions and line endings are preserved; a modified managed section refuses
with an explicit reconciliation error rather than being overwritten.

This directory is the complete install unit. Its generated `memory/` payload and
`skills/` need no files from a sibling checkout or separately installed plugin.
If copying skills into a repository rather than installing the plugin, copy the
entire payload too, preserving that layout; a skill file alone is not sufficient.

Requires Python 3.10+. Local plugin and skill discovery was verified with Windows
Copilot CLI 1.0.103; persistent installation and interactive execution remain
separate checks. Read the included
[operating policy](memory/references/operating-policy.md),
[runtime guide](memory/references/runtime-guide.md), and
[runtime contract](memory/contracts/RUNTIME.md) for storage, authorization,
limitations, and CLI details.
