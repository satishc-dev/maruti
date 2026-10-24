# Memory for Claude Code

```text
/plugin marketplace add satishc-dev/maruti
/plugin install memory@maruti
```

Load the Memory skills for bootstrap, capture, recall, checkpoints, consolidation,
and promotion. Resolve the actual loaded skill path, follow repository mirrors,
and find the helper at `<plugin-root>\memory\runtime\memory.py`.
Do not assume the marketplace name or an installation under a particular home
directory. Invoke Python directly; no shell wrapper or MCP service is needed.

Local bootstrap automatically creates or appends a small managed `AGENTS.md`
section in the consuming workspace, preserving existing instructions and line
endings. Modified managed content refuses rather than being overwritten. Whether
a host automatically loads `AGENTS.md` is host-specific; the helper does not
modify `CLAUDE.md` or global instructions.

This directory is the complete install unit. Its generated `memory/` payload and
`skills/` need no files from a sibling checkout or separately installed plugin.
If copying skills into a repository rather than installing the plugin, copy the
entire payload too, preserving that layout; a skill file alone is not sufficient.

Requires Python 3.10+. Windows is the first-release validation target; actual
host discovery/installation must be checked separately. Read the included
[operating policy](memory/references/operating-policy.md),
[runtime guide](memory/references/runtime-guide.md), and
[runtime contract](memory/contracts/RUNTIME.md) for storage, authorization,
limitations, and CLI details.
