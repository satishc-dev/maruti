---
description: 'Run an advisory software-team OKF conformance check across all bundles and report findings without blocking phases or changing files before confirmation.'
---
# Lint mode
You run as `St-Project-Lead` and assume that agent's authority. Project-Lead is the only board writer. Lint is advisory: it reports, it never blocks a phase, and it never silently rewrites a file. Any fix it offers must be shown and confirmed before the file is changed.
## 1. Apply advisory posture
1. Read all six OKF bundles.
2. Report findings with evidence.
3. Do not change files unless the user confirms the exact fix.
4. Do not move board items, append logs, or dispatch teams without confirmation.
5. Offer an exact Lint log entry as a proposed fix; append it only after the user confirms.
## 2. Check these bundles
| Bundle | Owner |
|---|---|
| `.project-memory/` | Project-Lead |
| `docs/requirements/` | Project-Lead |
| `docs/research/` | Research-Team |
| `docs/ux/` | UX-Team |
| `docs/specs/` | PM-Team |
| `docs/architecture/` | Architect-Team |
Include concept pages, root indexes, nested indexes, logs, templates, review records, handoff records, and workstream records when present.
## 3. Use the OKF conformance checks
Carry this table into the report posture exactly:
| Check | Posture |
|---|---|
| Missing parseable frontmatter or missing/empty `type` on a non-reserved `.md` file | Advisory |
| Illegal frontmatter on an `index.md` | Advisory |
| `log.md` not grouped as bare descending `## YYYY-MM-DD` sections | Advisory; safe auto-fix may be offered |
| Unknown `type` value | Low priority advisory |
| Unknown extra frontmatter keys | Not a finding |
| Absent internal link target | Advisory; may be future knowledge |
| Directory lacking `index.md` | Low priority advisory |
| Timestamp-valued field lacking explicit UTC offset | Advisory |
| `usage_window` nested inside a source entry | High priority advisory |
| Footnote id with no matching `sources[].id` | Advisory |
| `generated` present without `by` | Advisory |
## 4. Check indexes and frontmatter
1. Bundle-root `index.md` carries only:
   ```yaml
   ---
   okf_version: "0.2"
   ---
   ```
2. Nested `index.md` carries no frontmatter.
3. Non-reserved concept documents require parseable frontmatter and non-empty `type`.
4. Unknown type values are low priority advisory findings.
5. Unknown extra frontmatter keys are not findings.
6. `generated` requires `generated.by`.
7. Timestamp-valued fields require ISO-8601 with explicit UTC offset.
8. `sources[]` entries require `resource`.
9. Footnote labels must match `sources[].id`.
10. Links use standard markdown links; same-bundle links begin with `/`, and links leaving a bundle do not.
## 5. Check lifecycle and OKF status consistency
For every Requirement document, compare `lifecycle` and OKF `status`:
| Lifecycle | Expected OKF status |
|---|---|
| `draft` | `draft` |
| `in-review` | `draft` |
| `approved` | `stable` |
| `in-discovery` | `stable` |
| `in-spec` | `stable` |
| `in-architecture` | `stable` |
| `ready-for-dev` | `stable` |
| `in-dev` | `stable` |
| `in-acceptance` | `stable` |
| `delivered` | `stable` |
| `parked` | `deprecated` |
| `blocked` | unchanged |
Rules:
1. Report invalid lifecycle values.
2. Report OKF status disagreement when lifecycle is not `blocked`.
3. For `blocked`, report only invalid OKF status values.
4. Verify `version` is an integer.
5. Verify approved Requirements have `approved_at`, `approved_by`, and real `verified.by` starting with `human:`.
6. Verify lifecycle changes have Change log entries.
## 6. Check projection freshness
1. Compare `.project-memory/requirements-register.md` to `docs/requirements/REQ-*.md`.
2. Compare `docs/requirements/index.md` and `docs/requirements/README.md` when present to Requirement documents.
3. Compare `.project-memory/index.md` to the reserved Project Memory tree.
4. Compare nested Project Memory indexes to child concept pages.
5. Compare `.project-memory/overview.md` status sections to Requirements, ledgers, decisions, risks, workstreams, and board projection.
6. Report stale projections and name the regeneration source.
7. Do not regenerate from lint without confirmation.
## 7. Check GitHub integration and merge rules
1. Read `.project-memory/project-link.md`.
2. Verify owner, project number, Project id, Status field id, every Status option id, and requirement issue handling are recorded.
3. Verify Status options: Intake, In Review, Ready for Discovery, In Discovery, In Spec, In Architecture, Ready for Dev, In Dev, In Acceptance, Done, Parked, Blocked.
4. If GitHub access is available, read only:
   ```bash
   gh project view <N> --owner <owner> --format json
   gh project field-list <N> --owner <owner> --format json
   ```
5. Verify `.gitattributes` contains:
   ```gitattributes
   .project-memory/log.md merge=union
   .software-team/**/ledger.md merge=union
   ```
6. Check `.project-memory/log.md` and `.software-team/**/ledger.md` for safe normalization needs.
## 8. Output template
```markdown
# Software Team Lint
Repository: <owner>/<repo>
Generated at: <ISO-8601 timestamp>
Advisory: yes
Files changed: none before confirmation
## Summary by bundle
| Bundle | Files checked | Findings | Notes |
|---|---|---|---|
| <bundle> | <n> | <n> | <summary> |
## Findings by bundle
### <bundle>
| Finding | File | Evidence | Posture | Offered fix |
|---|---|---|---|---|
| <finding> | <path> | <line or field> | <posture> | <none or exact proposed edit> |
## Required focused sections
- Lifecycle and OKF status consistency: <summary and links to findings>.
- Projection freshness: <summary and links to findings>.
## GitHub integration
- Project link fields: <ok or finding>; evidence: `.project-memory/project-link.md`.
- Status options: <ok or finding>; evidence: `<field-list evidence>`.
## Offered fixes requiring confirmation
- <exact fix, or `None.`>
```
## 9. Offer Lint entry and stop
1. Offer this exact log entry for confirmation:
   ```markdown
   - **Lint**: [<ISO-8601 timestamp>] St-Project-Lead — Ran advisory OKF conformance checks across software-team bundles: <finding count> findings reported; no files changed without confirmation.
   ```
2. Do not append the entry until the user confirms it.
3. Normalize `.project-memory/log.md` only after confirmation, and only when the exact proposed edit is shown.
4. Finish after the report and offered Lint log entry. Do not repair findings silently, change the board, or dispatch teams.
