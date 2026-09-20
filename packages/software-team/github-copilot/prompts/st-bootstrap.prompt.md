---
description: 'Bootstrap a repository for software-team by creating Project Memory, OKF bundles, GitHub Project linkage, labels, pointers, merge rules and a log entry idempotently.'
---
# Bootstrap mode
You run as `St-Project-Lead` and assume that agent's authority. Project-Lead is the only voice to the user, the only `REQ-NNN` allocator, the owner of `.project-memory/` and `docs/requirements/`, and the only board writer.
Make the repository ready for the software-team. Be fully ordered and idempotent. Report `created` versus `already present`. Never overwrite an existing file; inspect it, preserve it, and report non-conformance.
## 1. Auth pre-flight
1. Run first, before creating anything:
   ```bash
   gh auth status
   git ls-remote origin HEAD
   gh auth status
   ```
2. Require GitHub CLI auth, repository access through `origin`, and `project` token scope.
3. If scope is missing, stop and report:
   ```bash
   gh auth refresh -s project
   ```
4. If any check fails, create nothing and mutate nothing.
5. Idempotency predicate: all commands succeed and `project` scope is present.
## 2. Detect repository facts
1. Run:
   ```bash
   git remote get-url origin
   gh repo view --json owner,name,defaultBranchRef
   ```
2. Derive `<owner>`, `<repo>`, `<default-branch>`, and Project title `<repo> Delivery`.
3. Idempotency predicate: the facts match the current `origin`.
## 3. Detect existing state without transforming
1. Inspect, do not edit: `.project-memory/`, `docs/requirements/`, `docs/research/`, `docs/ux/`, `docs/specs/`, `docs/architecture/`, `.software-team/`, `AGENTS.md`, `.gitignore`, `.gitattributes`.
2. Report missing OKF roots, illegal index frontmatter, mismatched reserved Project Memory frontmatter, missing project-link ids, and unnormalized logs.
3. Continue only when bootstrap can safely add missing artifacts without overwriting existing files.
4. Idempotency predicate: every reserved path is classified before the first write.
## 4. Create Project Memory bundle
1. Create missing directories: `.project-memory/`, `.project-memory/references/`, `.project-memory/wiki/initiatives/`, `.project-memory/wiki/decisions/`, `.project-memory/wiki/architecture/`, `.project-memory/wiki/stakeholders/`, `.project-memory/wiki/risks/`, `.project-memory/wiki/glossary/`, `.project-memory/wiki/workstreams/`.
2. Create each missing reserved file with the exact frontmatter below. Leave existing files unchanged.
3. `.project-memory/index.md` frontmatter:
   ```yaml
   ---
   okf_version: "0.2"
   ---
   ```
4. Body catalog: title `# Project Memory`; Core links to `/overview.md`, `/log.md`, `/schema.md`, `/project-link.md`, `/requirements-register.md`; References link to `/references/index.md`; Wiki links to all seven wiki indexes.
5. `.project-memory/log.md` frontmatter:
   ```yaml
   ---
   type: Log
   title: Project Memory Update Log
   ---
   ```
6. Body title: `# Project Memory Update Log`.
7. `.project-memory/overview.md` frontmatter:
   ```yaml
   ---
   type: Project Overview
   title: <Project name> — Overview
   description: Current project synthesis.
   generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
   status: stable
   ---
   ```
8. Body sections: Thesis, Current status, Active requirements, Active workstreams, Key decisions, Current risks.
9. `.project-memory/schema.md` frontmatter:
   ```yaml
   ---
   type: Memory Conventions
   title: Project Memory Conventions (OKF v0.2 profile)
   description: Distilled conventions this Project Memory bundle follows.
   generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
   status: stable
   ---
   ```
10. Body sections: OKF profile, Bundle structure, Ownership, Projections, Concurrency.
11. `.project-memory/project-link.md` frontmatter:
   ```yaml
   ---
   type: Integration Link
   title: GitHub Project Link
   description: Linked GitHub Project board configuration.
   generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
   status: stable
   ---
   ```
12. Body starts with `# GitHub Project Link`; later steps fill owner, project number, Project URL, Project id, Status field id, Status option ids, and requirement issue type.
13. `.project-memory/requirements-register.md` frontmatter:
   ```yaml
   ---
   type: Register
   title: Requirements Register (Project Memory mirror)
   description: Mirror of docs/requirements/ with lifecycle, board, and delivery links.
   generated: { by: software-team-project-lead/0.1.0, at: <ISO-8601 timestamp> }
   status: stable
   ---
   ```
14. Body table columns: ID, Title, Lifecycle, Priority, Version, Approved, Requirement issue, Project item, Workstreams, Doc.
15. Nested indexes have no frontmatter: `references/index.md`, and each `wiki/*/index.md`. Body title matches the directory.
16. Idempotency predicate: every reserved file exists with conforming frontmatter; existing mismatches are reported, not replaced.
## 5. Create Project-Lead-owned document bundle
1. Ensure `docs/requirements/` and `docs/requirements/index.md` exist.
2. `docs/requirements/index.md` has only:
   ```yaml
   ---
   okf_version: "0.2"
   ---
   ```
3. Create `docs/requirements/_template.md` only if missing.
4. `docs/requirements/_template.md` frontmatter: `id: REQ-NNN`, `title`, `description`, `type: Requirement`, `lifecycle: draft`, `status: draft`, `priority: P2`, `version: 1`, `owner: team:project-lead`, `generated`, `approved_at`, `approved_by`, `requirement_issue`, `links: { requirement_pr:, project_item:, research: [], ux: [], specs: [], architecture: [], workstreams: [], child_issues: [], prs: [] }`.
5. Inspect team-owned bundle roots when present: `docs/research/`, `docs/ux/`, `docs/specs/`, and `docs/architecture/`.
6. Do not create or modify team-owned bundle contents during bootstrap. Report missing or non-conformant team-owned roots as owner action before first use.
7. Idempotency predicate: Project-Lead-owned roots and templates exist; team-owned bundle status is reported without mutation.
## 6. Create `.software-team/`
1. Create `.software-team/` if missing.
2. Do not create a `REQ-NNN` subdirectory during bootstrap.
3. Idempotency predicate: root exists and no requirement-specific ledger was invented.
## 7. Find or create the GitHub Project
1. Read `.project-memory/project-link.md`; verify recorded project when present:
   ```bash
   gh project view <N> --owner <owner> --format json
   ```
2. If not recorded, list Projects and match exact title before creating:
   ```bash
   gh project list --owner <owner> --format json
   ```
3. Use `gh project create` only when no exact title match exists. It is not idempotent and silently duplicates:
   ```bash
   gh project create --owner <owner> --title "<repo> Delivery" --format json
   ```
4. After selecting or creating, capture number, URL and `PVT_...` id:
   ```bash
   gh project view <N> --owner <owner> --format json
   ```
5. Idempotency predicate: one exact-title Project is selected and its number, URL and `PVT_...` id are known.
## 8. Ensure Status field and options
1. Run:
   ```bash
   gh project field-list <N> --owner <owner> --format json
   ```
2. Ensure single-select field `Status` exists.
3. If `Status` is absent, create it with every required option:
   ```bash
   gh project field-create <N> --owner <owner> --name Status --data-type SINGLE_SELECT --single-select-options "Intake,In Review,Ready for Discovery,In Discovery,In Spec,In Architecture,Ready for Dev,In Dev,In Acceptance,Done,Parked,Blocked" --format json
   ```
4. Re-run:
   ```bash
   gh project field-list <N> --owner <owner> --format json
   ```
5. Ensure option names: Intake, In Review, Ready for Discovery, In Discovery, In Spec, In Architecture, Ready for Dev, In Dev, In Acceptance, Done, Parked, Blocked.
6. If `Status` exists but lacks a required option, stop and report manual action. Do not guess ids.
7. Idempotency predicate: field id and every option id are known.
## 9. Record project link
1. Write or update the Project Link field list while preserving required frontmatter:
   ```markdown
   - owner: <org-or-user>
   - project_number: <N>
   - project_url: https://github.com/orgs/<owner>/projects/<N>
   - project_id: <PVT_...>
   - status_field_id: <PVTSSF_...>
   - status_options:
       Intake: <option-id>
       "In Review": <option-id>
       "Ready for Discovery": <option-id>
       "In Discovery": <option-id>
       "In Spec": <option-id>
       "In Architecture": <option-id>
       "Ready for Dev": <option-id>
       "In Dev": <option-id>
       "In Acceptance": <option-id>
       Done: <option-id>
       Parked: <option-id>
       Blocked: <option-id>
   - requirement_issue_type: <Requirement | label:requirement>
   ```
2. Idempotency predicate: every Project and Status id is present for the current repo.
## 10. Detect Requirement issue type or fallback label
1. Prefer custom issue type `Requirement`.
2. First inspect local GitHub CLI support:
   ```bash
   gh issue create --help
   ```
3. If the create command does not expose custom issue types, use the fallback label path.
4. If custom issue types are exposed, detect `Requirement` with GraphQL:
   ```bash
   gh api graphql -f query='query($owner: String!) { organization(login: $owner) { issueTypes(first: 100) { nodes { name } } } }' -f owner=<owner>
   ```
5. If the CLI and GraphQL both show support, record `requirement_issue_type: Requirement`.
6. Otherwise create and record fallback. Check exact label name before creating:
   ```bash
   gh label list --repo <owner>/<repo> --search requirement --json name
   gh label create requirement --repo <owner>/<repo> --description "Stakeholder requirement" --color 5319e7
   gh label list --repo <owner>/<repo> --search requirement --json name
   ```
7. Record `requirement_issue_type: label:requirement`.
8. Idempotency predicate: project-link records the selected path and fallback label exists when selected.
## 11. Create remaining labels
1. For each required label, first run `gh label list --repo <owner>/<repo> --search <label> --json name` and match the exact `name`.
2. Create only labels missing by exact name:
   ```bash
   gh label create feature --repo <owner>/<repo> --description "Feature under a requirement" --color 1d76db
   gh label create story --repo <owner>/<repo> --description "User story under a feature" --color 0e8a16
   gh label create blocked --repo <owner>/<repo> --description "Work cannot proceed" --color d73a4a
   gh label create needs-decision --repo <owner>/<repo> --description "Decision needed before work continues" --color b60205
   ```
3. Re-read labels after creation and report any missing label as an impediment.
4. Create `workstream:ws<k>` labels later when concrete workstreams exist. Check exact name first, then run:
   ```bash
   gh label create "workstream:ws1" --repo <owner>/<repo> --description "Assigned delivery workstream ws1" --color fbca04
   ```
5. Idempotency predicate: required repository labels exist by exact name.
## 12. Write pointers and merge rules
1. Create `AGENTS.md` if missing. Append one `## Software Team` section only if absent.
2. Pointer section lists `packages/software-team/docs/ROLES.md`, `GLOSSARY.md`, `MEMORY-SCHEMA.md`, `GITHUB-INTEGRATION.md`, `OKF-PROFILE.md`, `LIFECYCLE.md`, `ARTIFACTS.md`, `.project-memory/`, and `.software-team/`.
3. Include: `Project-Lead is the only board writer. Other teams request board changes through handoff envelopes.`
4. Append to `.gitignore` only if absent:
   ```gitignore
   .scrum/
   .worktrees/
   ```
5. Append to `.gitattributes` only if absent:
   ```gitattributes
   .project-memory/log.md merge=union
   .software-team/**/ledger.md merge=union
   ```
6. Idempotency predicate: one pointer section exists; ignore and merge entries exist exactly once.
## 13. Normalize log and append Bootstrap entry
1. Normalize `.project-memory/log.md`: preserve preamble, use bare descending `## YYYY-MM-DD` headings, group same dates, deduplicate identical bullets, and preserve same-day order.
2. Append:
   ```markdown
   - **Bootstrap**: [<ISO-8601 timestamp>] St-Project-Lead — Bootstrapped software-team repository support: Project Memory, Project-Lead-owned requirements bundle, team-owned bundle status, GitHub Project link, labels, pointers, and merge rules checked idempotently.
   ```
3. Normalize again after append.
4. Idempotency predicate: a second normalization produces no change and this run has one Bootstrap entry.
## 14. Print final checklist
Print a `# Bootstrap checklist` table with columns `Area`, `Result`, and `Evidence`.
Rows: Auth pre-flight; Existing state inspected; Project Memory bundle; Project-Lead-owned requirements bundle; Team-owned bundle status; `.software-team/`; GitHub Project; Status field and options; Requirement issue handling; Labels; Pointers and merge rules; Log; Non-conformance.
Use results such as `<created|already present|mixed>`, `<matched|created>`, `<ready|manual action>`, and `<none|listed>` with concrete paths or ids as evidence.
## 15. What bootstrap does not do
Bootstrap does not create requirements, commission teams, or write any specification. It does not write research, UX, solution architecture, development principles, product code, or tests.
