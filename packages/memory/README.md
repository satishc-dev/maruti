# Memory

Standalone, offline OKF 0.2 memory for agents. Capture durable facts, recall a
bounded set of relevant documents, checkpoint a session, consolidate one topic,
and explicitly promote curated knowledge. No MCP server, embedding service,
consumer package install, or network access is required.

## Install

| Host | Commands in the host |
|---|---|
| GitHub Copilot CLI | `copilot plugin marketplace add satishc-dev/maruti`, then `copilot plugin install memory@maruti` |
| Claude Code | `/plugin marketplace add satishc-dev/maruti`, then `/plugin install memory@maruti` |

The install roots are [github-copilot](github-copilot/) and
[claude-code](claude-code/). Software Team includes the **same** canonical
capability in its own Copilot plugin; it does not rely on installing another
plugin transitively.

Requires Python 3.10 or later. The helper includes a licensed pure-Python YAML
parser. Python 3.14 remains Maruti's development standard; the standalone helper's
lower minimum is intentional. Windows is the first-release validation target.
Portability is intended but Linux/macOS support is unverified.

## Storage and safety

Bootstrap creates `.maruti/memory/local/` only after a narrow
`/.maruti/memory/local/` ignore rule is present and verified. In a non-Git project,
the rule is recorded for a future Git initialization; no claim of active Git
protection is made. Curated `.maruti/memory/shared/` is optional and requires
separate authorization for shared mutations.

The helper preserves existing roots rather than migrating or overwriting them.
Store identity in `.memory-store.json` separates namespace `maruti.memory`,
schema version `1`, a store UUID, role, and creator package version `0.1.0`.
OKF bundle-root indexes contain only `okf_version: "0.2"`; plugin and store
metadata do not belong there.

Capture session observations under `sessions/<session-id>/`, knowledge under
`topics/<topic>/`, and use checkpoints for continuity. Reads report SHA-256;
writes require the expected SHA-256 or `missing`. Discovery is bounded to eight
candidates and 16,000 content characters. The installed contracts and skills
define validation, conflict handling, and topic consolidation.

Permission to promote content is **not** permission to stage, commit, or push it.
Never capture secrets or unsupported personal inferences. Shared promotion does
not change Software Team ownership: `.project-memory/` stays committed and
Project-Lead-owned; workers use local memory or `memory_proposals[]`.

## Direct helper

Resolve the real loaded skill file on disk, then take its parent (`<skill>`),
parent (`skills`), and parent (plugin root). Do not guess a host installation
directory, marketplace namespace, or current working directory. Repository
mirrors must be resolved before taking parents.

Invoke Python directly, quoting the resolved path:

```text
python "<plugin-root>\memory\runtime\memory.py" --root "<workspace>" doctor
python "<plugin-root>\memory\runtime\memory.py" --root "<workspace>" bootstrap
python "<plugin-root>\memory\runtime\memory.py" --root "<workspace>" discover --query "topic"
```

Commands are `doctor`, `bootstrap`, `discover`, `read`, `write`, `catalog`, and
read-only `migration-preview`. `--role local` is the default; shared mutation
requires `--role shared --allow-shared`. Successful JSON is
`{"ok": true, "data": {...}}` (exit 0), and failures are
`{"ok": false, "error": {"code": "...", "message": "..."}}` (exit 2).
Capture, checkpoints, consolidation, and promotion are skill-guided workflows
over these primitives, not extra CLI verbs.

## Authoring and composition

Canonical roots: `runtime/`, `vendor/`, `contracts/`, `templates/`, `skills/`,
and `references/`. Generated install payloads are self-contained copies, not
cross-package links. Shared skill narrative is byte-identical across hosts and
Software Team. See [composition](composition/) for build/check and safe mirror
alias rules.

```text
python scripts\build_memory_package.py
python scripts\build_memory_package.py --check
python -m unittest discover -s packages\memory\tests\packaging -v
```

No generalized migration execution, multi-file recovery framework, automatic
deletion, recurring automation, or token benchmark harness ships in this lean
release. Automated Windows validation and host installation/discovery are
different checks: do not infer a tested host installation from a passing helper
test or from the presence of a package manifest.
