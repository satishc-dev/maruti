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
   generated: { by: process:software-team-bootstrap, at: <ISO-8601 timestamp> }
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
   generated: { by: process:software-team-bootstrap, at: <ISO-8601 timestamp> }
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
   generated: { by: process:software-team-bootstrap, at: <ISO-8601 timestamp> }
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
   generated: { by: process:software-team-bootstrap, at: <ISO-8601 timestamp> }
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
3. Create `docs/requirements/README.md` only if missing. This is the human-facing requirements register, and it is a different document from `docs/requirements/index.md`. `st-sync`, `st-lint`, `LIFECYCLE.md` and `OKF-PROFILE.md` all expect it, so a bootstrap that omits it leaves the repository non-conformant and the next run will create it — which breaks idempotency. Frontmatter:
   ```yaml
   ---
   type: Register
   title: Requirements Register
   description: Generated register of canonical project requirements.
   generated: { by: process:software-team-bootstrap, at: <ISO-8601 timestamp> }
   status: stable
   ---
   ```
   Body: title `# Requirements Register`, then an empty table with columns ID, Title, Lifecycle, Priority, Version, Approved, Requirement issue, Project item, Doc.
4. Create `docs/requirements/_template.md` only if missing.
5. `docs/requirements/_template.md` frontmatter: `id: REQ-NNN`, `title`, `description`, `type: Requirement`, `lifecycle: draft`, `status: draft`, `priority: P2`, `version: 1`, `owner: team:project-lead`, `generated`, `approved_at`, `approved_by`, `requirement_issue`, `links: { requirement_pr:, project_item:, research: [], ux: [], specs: [], architecture: [], workstreams: [], child_issues: [], prs: [] }`.
6. Inspect team-owned bundle roots when present: `docs/research/`, `docs/ux/`, `docs/specs/`, and `docs/architecture/`.
7. Do not create or modify team-owned bundle contents during bootstrap. Report missing or non-conformant team-owned roots as owner action before first use.
8. Idempotency predicate: Project-Lead-owned roots, the register, and templates all exist; team-owned bundle status is reported without mutation.
## 6. Create `.software-team/` and materialize the contracts
1. Create `.software-team/` if missing.
2. Do not create a `REQ-NNN` subdirectory during bootstrap.
3. **Locate the shipped contracts.** Every agent reads its contracts from `.software-team/contracts/`, so bootstrap is the one step that puts them there. The contracts ship inside the installed plugin, not in the target repository. Resolve the source directory by taking the first of these that exists:
   1. `packages/software-team/github-copilot/contracts/` relative to the repository root — this is the case when working inside the `maruti` repository itself.
   2. `<plugin-root>/contracts/`, where `<plugin-root>` is the directory containing `skills/st-handoff/SKILL.md` for the installed `software-team` plugin. On a default installation this is `~/.copilot/installed-plugins/<marketplace>/software-team/`. Resolve it by locating the `st-handoff` skill file on disk and taking its grandparent's parent, rather than assuming the marketplace name.
4. If neither source resolves, stop and report `contracts source not found` as an impediment. Do not invent contract content, and do not proceed to commission any team — every downstream agent depends on these files.
5. Copy these ten files into `.software-team/contracts/`: `ROLES.md`, `GLOSSARY.md`, `LIFECYCLE.md`, `ARTIFACTS.md`, `HANDOFF-PROTOCOL.md`, `PARALLELISM.md`, `MEMORY-SCHEMA.md`, `OKF-PROFILE.md`, `GITHUB-INTEGRATION.md`, `CADENCE.md`.
6. `RUBBER-DUCK-PROTOCOL.md` is deliberately not among them. It is not shipped in the plugin and must never be copied into a repository. Ducks load the `st-rubber-duck` skill instead. If you find that file, do not read it and do not copy it.
7. Copy semantics: create the file when absent. When present and byte-identical, report `already present`. When present and different, overwrite it and report `updated`, because these are versioned contracts owned by the package rather than repository content — but never overwrite anything outside `.software-team/contracts/`.
8. Record the resolved source path and the file count in the final checklist as evidence.
9. Idempotency predicate: `.software-team/` exists, `.software-team/contracts/` holds exactly those ten files matching the shipped copies, `RUBBER-DUCK-PROTOCOL.md` is absent, and no requirement-specific ledger was invented.
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
Every new GitHub Project is created with a built-in single-select `Status` field already holding `Todo`, `In Progress` and `Done`. `Status` is therefore almost never absent, and treating a non-conformant option set as manual action would halt every first-time bootstrap. Reconcile the options instead.
1. Run:
   ```bash
   gh project field-list <N> --owner <owner> --format json
   ```
2. Locate the single-select field named `Status` and capture its `PVTSSF_...` id and its current options, each with `id` and `name`.
3. Required option names, in order: Intake, In Review, Ready for Discovery, In Discovery, In Spec, In Architecture, Ready for Dev, In Dev, In Acceptance, Done, Parked, Blocked.
4. If `Status` is genuinely absent, create it with every required option:
   ```bash
   gh project field-create <N> --owner <owner> --name Status --data-type SINGLE_SELECT --single-select-options "Intake,In Review,Ready for Discovery,In Discovery,In Spec,In Architecture,Ready for Dev,In Dev,In Acceptance,Done,Parked,Blocked" --format json
   ```
5. If `Status` exists and its option names already match the required set, change nothing.
6. Otherwise reconcile with `updateProjectV2Field`. That mutation **replaces the whole option list**, so build the replacement carefully: for every required name that already exists, reuse its existing `id` so items keep their status; for every required name that does not exist, omit `id` so a new option is created.
7. Count the items on the board before deciding what to do with options that are not in the required set:
   ```bash
   gh project item-list <N> --owner <owner> --format json
   ```
   - **No items** — drop the extra options. A fresh board's `Todo` and `In Progress` carry no information.
   - **Any items** — keep every extra option, appended after the required ones, and report them as non-conformant but preserved. Never silently delete an option that items may be using.
8. Apply the reconciliation. Inline the option list; `singleSelectOptions` is a list of input objects and cannot be passed through `-f`:
   ```bash
   gh api graphql -f query='
   mutation {
     updateProjectV2Field(input: {
       fieldId: "<PVTSSF_...>",
       singleSelectOptions: [
         {name: "Intake", color: GRAY, description: "Requirement recorded, not yet reviewed"},
         {name: "In Review", color: YELLOW, description: "Awaiting stakeholder review"},
         {name: "Ready for Discovery", color: BLUE, description: "Approved, UX discovery pending"},
         {name: "In Discovery", color: BLUE, description: "UX discovery running"},
         {name: "In Spec", color: PURPLE, description: "PM-Team is specifying"},
         {name: "In Architecture", color: PURPLE, description: "Architect-Team is designing"},
         {name: "Ready for Dev", color: BLUE, description: "Build-ready, no workstream active"},
         {name: "In Dev", color: ORANGE, description: "Dev-Team is implementing"},
         {name: "In Acceptance", color: YELLOW, description: "Project-Lead is verifying the PR"},
         {name: "Done", color: GREEN, description: "Accepted, merged and closed"},
         {name: "Parked", color: GRAY, description: "Deliberately deferred"},
         {name: "Blocked", color: RED, description: "Cannot proceed"}
       ]
     }) {
       projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name } } }
     }
   }'
   ```
   Add `id: "<existing-option-id>"` to any option that already exists. Valid colors are GRAY, BLUE, GREEN, YELLOW, ORANGE, RED, PINK and PURPLE; anything else is rejected.
9. Re-run:
   ```bash
   gh project field-list <N> --owner <owner> --format json
   ```
10. Confirm every required option name is present and capture its option id. Option ids are short hex strings, not `PVTSSFO_` values.
11. Stop and report manual action only if the mutation itself fails, or if `Status` is not a single-select field and so cannot hold these options. Do not guess ids.
12. Idempotency predicate: field id and every required option id are known, and a second run finds the options already conformant and changes nothing.
## 9. Record project link
1. Write or update the Project Link field list while preserving required frontmatter:
   ```markdown
   - owner: <org-or-user>
   - project_number: <N>
   - project_url: <the url field returned by `gh project view`, verbatim>
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
1. Prefer the custom issue type `Requirement`. Do not probe the CLI for support — `gh` has no issue-type flag on `gh issue create`, so a CLI probe would always fail and wrongly force the fallback. Detection is a GraphQL question.
2. Detect with GraphQL, capturing the type id:
   ```bash
   gh api graphql -f query='query($owner: String!) { organization(login: $owner) { issueTypes(first: 100) { nodes { id name } } } }' -f owner=<owner>
   ```
3. If a node named `Requirement` is returned, record both:
   ```markdown
   - requirement_issue_type: Requirement
   - requirement_issue_type_id: <IT_...>
   ```
4. **Expected non-failure:** custom issue types are an organization feature. For a user-owned repository the query returns `NOT_FOUND` and `gh` exits non-zero with `Could not resolve to an Organization with the login of '<owner>'`. This is a normal outcome, not a pre-flight failure. Do not stop bootstrap. Take the fallback path. The same applies to an organization with no `Requirement` type, which returns an empty node list.
5. Fallback: create and record the label. Check the exact label name before creating:
   ```bash
   gh label list --repo <owner>/<repo> --search requirement --json name
   gh label create requirement --repo <owner>/<repo> --description "Stakeholder requirement" --color 5319e7
   gh label list --repo <owner>/<repo> --search requirement --json name
   ```
6. Record `requirement_issue_type: label:requirement`.
7. Idempotency predicate: project-link records the selected path, and when the fallback was selected the `requirement` label exists.
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
2. Pointer section lists `.software-team/contracts/ROLES.md`, `.software-team/contracts/GLOSSARY.md`, `.software-team/contracts/MEMORY-SCHEMA.md`, `.software-team/contracts/GITHUB-INTEGRATION.md`, `.software-team/contracts/OKF-PROFILE.md`, `.software-team/contracts/LIFECYCLE.md`, `.software-team/contracts/ARTIFACTS.md`, `.project-memory/`, and `.software-team/`.
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
2. Append, using the OKF automation actor exactly as written. Do not substitute the agent display name — `OKF-PROFILE.md` §5 requires `<producer>/<version>` or a `process:` actor, and writing `St-Project-Lead` here makes a later run rewrite the line, which breaks idempotency:
   ```markdown
   - **Bootstrap**: [<ISO-8601 timestamp>] process:software-team-bootstrap — Bootstrapped software-team repository support: Project Memory, Project-Lead-owned requirements bundle, team-owned bundle status, GitHub Project link, labels, pointers, and merge rules checked idempotently.
   ```
3. Normalize again after append.
4. Idempotency predicate: a second normalization produces no change, this run has one Bootstrap entry, and a later run neither rewrites the actor nor adds a second entry.
## 14. Print final checklist
Print a `# Bootstrap checklist` table with columns `Area`, `Result`, and `Evidence`.
Rows: Auth pre-flight; Existing state inspected; Project Memory bundle; Project-Lead-owned requirements bundle; Team-owned bundle status; `.software-team/`; Contracts materialized; GitHub Project; Status field and options; Requirement issue handling; Labels; Pointers and merge rules; Log; Commit; Non-conformance.
Use results such as `<created|already present|mixed>`, `<matched|created>`, `<ready|manual action>`, and `<none|listed>` with concrete paths or ids as evidence.
## 15. Commit policy
1. Commit the artifacts you created in a single commit. Bootstrap output is scaffolding the project is meant to keep, and leaving it uncommitted makes the next run's idempotency impossible to judge.
2. Commit message: `chore: bootstrap software-team`, with the standard `Co-authored-by` trailer.
3. Stage only paths bootstrap owns: `.project-memory/`, `.software-team/`, `docs/requirements/`, `AGENTS.md`, `.gitignore`, `.gitattributes`. Never stage unrelated working-tree changes you did not make.
4. If there is nothing to commit, say so and commit nothing. A second run must produce no commit.
5. **Never push.** Never create a branch, never open a pull request, and never modify any remote ref. Publishing is the stakeholder's decision, and bootstrap has not been asked to make it.
6. Idempotency predicate: the first run produces exactly one commit, a second run produces none, and `origin` is untouched by both.
## 16. What bootstrap does not do
Bootstrap does not create requirements, commission teams, or write any specification. It does not write research, UX, solution architecture, development principles, product code, or tests.
