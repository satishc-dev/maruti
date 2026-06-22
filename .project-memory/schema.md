# Project Memory — Conventions & Workflows (distilled)

This is the in-repo, distilled copy of the Project Lead's binding schema. The full
reference lives in the `project-lead` package's `MEMORY-SCHEMA.md`. Two rules hold
everywhere:

1. **The repo is canonical for requirements.** Requirement documents live in
   `docs/requirements/` (versioned, PR-reviewable). `.project-memory/` only
   *references* them.
2. **The Lead owns the bookkeeping.** It writes every file under
   `.project-memory/`; the human curates sources, decides, and approves.

## Layout

```
.project-memory/
├── schema.md                  # this file — conventions + workflows
├── index.md                   # content catalog: every page + 1-line summary
├── log.md                     # append-only chronology of events
├── overview.md                # evolving project thesis / current-state synthesis
├── project-link.md            # the linked GitHub Project: number, URL, field IDs
├── requirements-register.md   # tracking index referencing docs/requirements/*
└── wiki/
    ├── initiatives/           # one page per initiative/epic
    ├── decisions/             # decision records (what/why/alternatives/date)
    ├── architecture/          # accumulated system & architecture knowledge
    ├── stakeholders/          # stakeholder context & preferences
    ├── risks/                 # risks and open questions
    └── glossary/              # domain terms
```

## Conventions

- **Wikilinks:** cross-reference pages with `[[wiki/initiatives/<slug>]]` style
  links so Obsidian's graph view works.
- **Frontmatter:** every wiki page carries YAML frontmatter with at least
  `title`, `tags`, `created`, `updated`.
- **`index.md`** is a content catalog, read first to find relevant pages; updated
  on every ingest.
- **`log.md`** is chronological and append-only. Every entry begins:

  ```
  ## [YYYY-MM-DD] <event> | <subject>
  ```

  where `<event>` ∈ `ingest | requirement | approval | handoff | sync | delivery | lint | decision`.
- **`overview.md`** holds the current synthesis, rewritten as the project evolves.

## Requirement lifecycle

```
draft ──► in-review ──►(APPROVAL GATE)──► approved
   ──► in-spec ──► specced ──► in-delivery ──► delivered
                          (parked at any point, with a reason logged)
```

### Definition of Ready (must all hold before `in-review`)

- [ ] Clear problem statement and desired outcome.
- [ ] **Testable** acceptance / success criteria.
- [ ] Explicit scope **in** and **out** (non-goals).
- [ ] Known constraints & assumptions recorded.
- [ ] No blocking open questions remain.

## Approval gate (hard rules)

- Primary approval = a **requirement PR** the stakeholder reviews and merges.
- Express in-chat signoff allowed for tiny edits; still stamp the doc.
- The Lead **MUST NOT** launch/recommend `pm-team` for any requirement whose
  status is not `approved`.
- Any change to an `approved`+ requirement re-opens it to `in-review` via a new
  PR and requires re-approval.

## GitHub mapping

- One **Requirement issue** per requirement — preferred custom issue type
  "Requirement", else a `requirement`-labeled issue.
- pm-team's Feature/Story issues become **native sub-issues** of the Requirement
  issue for end-to-end traceability and Projects v2 roll-up.
- One **Project (v2)** board with a single-select **Status** funnel:
  Intake → In Review → Ready for Spec → In Spec → Ready for Dev → In Dev →
  In Review (Dev) → Done (plus Parked).
