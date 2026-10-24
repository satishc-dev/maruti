# Records and honest OKF

## Store identity is not document frontmatter

The helper owns `<store>/.memory-store.json`: namespace `maruti.memory`,
`schema_version` 1, `store_id`, `role`, and `created_with`. Plugin version
`0.1.0`, metadata schema version `1`, and OKF version `0.2` are different axes.
Never put store metadata in an OKF root index or hand-edit it to enable writes.
Unknown/newer schema refuses writes; unknown keys in supported documents and
metadata must be preserved, not normalized away. Migration execution is deferred.

## Indexes, records, and links

The bundle-root `index.md` has only:

```yaml
---
okf_version: "0.2"
---
```

Nested indexes have **no frontmatter**. Their bodies are grouped/sparse standard
Markdown links, not lifecycle dashboards. `index.md` and `log.md` are reserved
names, not concept filenames.

Every concept has a non-empty `type`. Durable concepts live under
`topics/<slug>/<record>.md`; choose a descriptive type such as Decision,
Discovery, Constraint, Failed Approach, Reference, or Risk. The vocabulary is
extensible, not a claim of verification. Session state lives under
`sessions/<session-id>/checkpoint.md` or `observations.md`, with a suitable
non-empty type such as Session Checkpoint or Session Observation.

Use standard Markdown links, never wikilinks. Same-bundle links begin with `/`
and resolve from the bundle root. Links leaving the bundle do not begin with
`/`; use actual relative paths or stable absolute URLs. Check source pointer
accessibility before sharing; local provenance is not automatically shareable.

## Trust, timestamps, and actors

OKF `status` is `draft`, `stable`, or `deprecated`; it is not delivery lifecycle,
task completion, board state, or approval. Absent status is effectively stable,
not verified. Preserve valid unknown keys and any separate lifecycle field.

Use the actual writer in `generated.by`; if `generated` exists, `by` is required.
`generated.at` records the last meaningful change, not every read.
All timestamp-valued fields use ISO-8601 with an explicit UTC offset, for example
`2026-10-23T19:49:15-07:00` or `2026-10-24T02:49:15Z`. Bare dates are allowed
only as log headings.

Agent/tool actors use `<producer>/<version>` only when that producer/version is
known. Humans use `human:<id>`, teams `team:<id>`, and automation
`process:<id>`. Do not pretend the generic plugin is the writer if another agent
wrote the record. Do not invent a tool version, human identity, or historical
author. If actual actor identity is unavailable, report the blocker to capture
rather than creating false provenance. Ownership belongs in `owner`, not
`generated.by`.

Omit `verified` without an actual verifier and actual verification. Never
fabricate human review. Describe what was verified, by whom, when, and with what
scope; an agent check is not human approval.

## Evidence and citations

Each load-bearing sourced claim carries a footnote label matching
`sources[].id` exactly; that label is the join key, not positional numbering.
Each source has a real `resource`; cite only material actually read. Preserve
distinct evidence and identify speculation, unknowns, and unresolved
contradictions. Omit `sources` when there is no real source, rather than creating
empty or fictional entries. Source timestamps are actual observations, not
guessed last-modified dates. Usage metadata, if present, is not evidence quality.

Record a reproducible command and actual result for a tool observation, not a
claim that a test passed when it was never run. A failed approach needs
conditions, observed failure, cause confidence, and when revisiting might help.
A decision needs alternatives, rationale, scope, consequences, and any real
decision-maker separate from the writer. Risks need evidence, impact, and
uncertainty, not fabricated probabilities.

## Checkpoints and observations

Checkpoints record current objective, workspace/branch/commit when known,
relevant files and observed state, actions actually completed, checks actually
run, blockers, uncertainty, and next actions. They are resume hints, not
enduring architectural facts. On resume inspect actual branch/files and current
permissions. Session observations may later yield durable concepts, but promotion
requires deliberate evidence review; copying a checkpoint does not make it
knowledge. Keep checkpoint scope small and never imply automatic host compaction.

Use helper read/hash/write for both concept and session records. Preserve
existing unknown keys and evidence during updates; reread on a conflict.
