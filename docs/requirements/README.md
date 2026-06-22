# Requirements Register

The official register of stakeholder requirements for **maruti**. Each row points
to a versioned requirement document in this folder. A requirement may only be
handed to `pm-team` once its status is `approved`.

| ID | Title | Status | Priority | Approved | Requirement issue | Doc |
|----|-------|--------|----------|----------|-------------------|-----|
| REQ-001 | Top-level CONTRIBUTING.md for new contributors | approved | P2 | 2026-06-21 | [#7](https://github.com/satishc-dev/maruti/issues/7) | [REQ-001-contributing-guide.md](REQ-001-contributing-guide.md) |

## Lifecycle

`draft → in-review → (APPROVAL GATE) → approved → in-spec → specced → in-delivery → delivered` (or `parked`).

## Authoring a new requirement

1. Copy [`_template.md`](_template.md) to `REQ-NNN-<slug>.md` (next zero-padded number).
2. Fill every section; keep it focused on **what & why**, never **how**.
3. Satisfy the Definition of Ready before requesting approval.
