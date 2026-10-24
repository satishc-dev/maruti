# Incremental maintenance

## Choose a bounded job

Default to advisory review of one named topic. Explicit local-apply scope can
authorize a bounded set of local changes after enablement; it never authorizes
shared edits. State the scope and use the [recall budget](recall-guide.md).
Use helper `doctor` for store checks, `discover --query <text> --topic <exact-slug>`
for the named topic, or `--session <exact-id>` for a specific session review.
Inspect result `scope` and `scan_complete`; completed name search can still
omit output candidates. `discovery_limit` means an incomplete scan exceeded
the 512-entry budget, not that the topic has no evidence. Narrow a broad search
with an exact selector rather than retrying the broad scan; if the selected
directory also exceeds that limit, use `read --path` only for a known artifact
within the recall budget, or report the unresolved review. Do not load the
whole store. A report is not a promise the whole store was audited.

Prioritize outdated load-bearing constraints, contradictions, duplicate claims,
missing source targets, and misleading applicability. Cosmetic omissions and
unfamiliar types are advisory. Never invent provenance to make a check green.

## Preserve evidence, improve navigation

Consolidate only claims that are genuinely equivalent under the same conditions.
Keep each distinct source and relevant failed attempt. Preserve unresolved
contradictions with both claims, their evidence, scope differences, and what
could resolve them; freshness alone does not select the truth.

A synthesis should link its evidence and be shorter to recall than the set it
replaces. Update applicability when supported. Deprecate obsolete records and
link a real successor with an explanation of supersession; do not erase the
original evidence. **No hard-delete** of records or pruning of session files is
part of this skill. Do not silently turn an uncertain draft into verified stable
knowledge, or treat a deprecation as a delivery lifecycle change.

## Apply only within authority

Before each authorized local update, use helper `read`, retain the returned
hash, preserve unknown keys and unrelated content, and prepare a complete UTF-8
input outside the store. Use helper `write --expected` with that exact hash.
On conflict, reread, compare, and reconcile the latest content; do not reapply a
stale synthesized version blindly. No direct-write fallback.

Separate writes are not a multi-record transaction. If interrupted or rejected,
stop and report which writes actually succeeded and which did not; reread before
resuming. Elaborate crash recovery and migration execution are deferred. Never
claim rollback or atomic multi-file repair. Refresh only the affected topic with
helper `catalog --topic`; verify records and catalog after successful changes.

Shared or team-owned corrections remain owner proposals unless separately
authorized under the [sharing policy](sharing-guide.md). Inspection can suggest
migration using `migration-preview`; it must not execute one.

## Report and reuse

Distinguish findings, proposals, applied updates, remaining contradictions, and
omissions. Keep useful failure evidence. A reusable future invocation is
"Review one named topic with memory-maintain in advisory mode"; authorized
local-apply may be requested explicitly. This is not a scheduled automation or
a formal benchmark harness, and does not require specialist-team orchestration.
