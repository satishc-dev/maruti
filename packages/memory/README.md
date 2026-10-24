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

### Try this local checkout before publication

From the root of this checkout:

```text
copilot --plugin-dir ".\packages\memory\github-copilot" plugin list --json
copilot --plugin-dir ".\packages\memory\github-copilot" skill list --json
copilot --plugin-dir ".\packages\memory\github-copilot"
```

The first command must include `memory`, version `0.1.0`, enabled, with source
`external`. The second must show all six `memory-*` skills with source `plugin`.
The last command starts an interactive session with that local plugin mounted.
A mount applies only to that process: it does not install globally, alter an
already running session, or publish the marketplace. Restart using the flag to
see the local plugin in the interactive plugin dashboard. The marketplace
commands above read the published repository, not these unpushed changes.

The install roots are [github-copilot](github-copilot/) and
[claude-code](claude-code/). Software Team includes the **same** canonical
capability in its own Copilot plugin; it does not rely on installing another
plugin transitively.

If both plugins are installed, their generic skill names intentionally overlap.
They contain identical capability bytes; select the skill from the intended
plugin using the host's actual discovery result rather than assuming a particular
namespacing syntax or precedence. Repository mirrors explicitly choose the
standalone Memory copy and reject any divergent alias.

Requires Python 3.10 or later. The helper includes a licensed pure-Python YAML
parser. Python 3.14 remains Maruti's development standard; the standalone helper's
lower minimum is intentional. Windows is the first-release validation target.
Portability is intended but Linux/macOS support is unverified.

## Use

In the consuming workspace, ask the agent to load `memory-bootstrap` first.
Authorized local bootstrap automatically creates or appends a small managed
section in workspace `AGENTS.md`; no hand-written instructions are required.
It points future agents to bounded recall before rediscovery, useful-boundary
evidence-backed local capture, and checkpoints for substantial work. Existing
instructions, line endings, and Software Team ownership are preserved.
Rerun bootstrap to add a missing section to an already enabled store; an
unchanged section is byte-idempotent. Modified/malformed managed content or an
unmarked `## Workspace Memory` section produces an explicit reconciliation
error, never an overwrite. Shared bootstrap does not edit the local pointer.

Select the actual discovered skill from the intended plugin; do not guess a
host-specific namespace. Then use these focused skills as needed:

| Skill | Purpose |
|---|---|
| `memory-bootstrap` | Inspect existing state and explicitly enable compatible local memory. |
| `memory-capture` | Capture evidence-backed findings at useful work boundaries, not every tool call. |
| `memory-recall` | Retrieve bounded relevant evidence without treating stored text as instructions. |
| `memory-checkpoint` | Save or resume session-scoped state after checking the current workspace. |
| `memory-maintain` | Consolidate one topic while preserving distinct evidence and contradictions. |
| `memory-promote` | Propose or write only selected, shareable, explicitly authorized content. |

These are explicit agent workflows, not guaranteed host lifecycle hooks or
automatic context compaction. Missing Python or a helper refusal is a blocker,
not permission to download dependencies or write directly into the store.
If an instruction write fails after store enablement, bootstrap reports that
partial outcome explicitly. Inspect the error and `AGENTS.md` before retrying;
`doctor` reporting an enabled store does not mean instruction setup completed.

## Storage and safety

In a Git project, bootstrap creates `.maruti/memory/local/` only after a narrow
`/.maruti/memory/local/` ignore rule is present and verified. A non-Git project
reports `git: false`, has no active Git ignore protection, and does not receive a
`.gitignore` file by default. If you later initialize Git, rerun bootstrap before
staging files. Subsequent mutations re-evaluate Git status and refuse local
capture until the ignore rule is effective. Curated `.maruti/memory/shared/` is
optional and requires separate authorization for shared mutations.

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

As the store grows, scope recall to an exact topic or session rather than scanning
unrelated namespaces. `discover --query "<text>" --topic "<slug>"` and
`--session "<id>"` are mutually exclusive per-verb selectors. Successful results
identify `scope` and `scan_complete`; `more_candidates` and per-record
`truncated` still indicate omitted output. A `discovery_limit` error is an
incomplete search, not empty recall: narrow the scope or read a known path.

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
python "<plugin-root>\memory\runtime\memory.py" --root "<workspace>" discover --query "decision" --topic "architecture"
```

Commands are `doctor`, `bootstrap`, `discover`, `read`, `write`, `catalog`, and
read-only `migration-preview`. `--role local` is the default; shared mutation
requires `--role shared` before the verb and `--allow-shared` after the mutating
verb, in addition to actual content/owner authorization. Successful JSON is
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
release. Windows Copilot CLI 1.0.103 local `--plugin-dir` plugin and skill
discovery has been exercised, including relocated install units outside the
repository mirrors. The live discovery regression runs when Copilot is installed
and otherwise skips explicitly. Persistent marketplace installation and
interactive agent execution are separate checks, not implied by helper or
discovery tests.
