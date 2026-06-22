# Requirements Register (Project Memory)

Tracking index that **references** `docs/requirements/*` plus their Requirement
issues and GitHub Project items. The canonical register is
`docs/requirements/README.md`; this page mirrors it for the memory wiki and adds
Project-item / initiative cross-links.

| ID | Title | Status | Priority | Requirement issue | Project item | Doc |
|----|-------|--------|----------|-------------------|--------------|-----|
| REQ-001 | Top-level CONTRIBUTING.md for new contributors | delivered | P2 | [#7](https://github.com/satishc-dev/maruti/issues/7) | [Done](https://github.com/users/satishc-dev/projects/5) | [docs/requirements/REQ-001-contributing-guide.md](../docs/requirements/REQ-001-contributing-guide.md) |

## Spec & work items (REQ-001)

- Spec PR: [#8](https://github.com/satishc-dev/maruti/pull/8) (base `pl-e2e-test`) — spec `docs/specs/contributing-guide/contributing-guide.md`.
- Code PR: [#12](https://github.com/satishc-dev/maruti/pull/12) (base `pl-e2e-test`, **MERGED**) — top-level `CONTRIBUTING.md`, closing Stories #11 & #10.
- Sub-issues of Requirement [#7](https://github.com/satishc-dev/maruti/issues/7) (all **closed**):
  Feature [#9](https://github.com/satishc-dev/maruti/issues/9),
  Story A [#11](https://github.com/satishc-dev/maruti/issues/11),
  Story B [#10](https://github.com/satishc-dev/maruti/issues/10).
- **Delivered** 2026-06-22: all 9 acceptance criteria verified PASS; Requirement #7 closed; board item moved to Done.

## Notes

- New requirements are authored under `docs/requirements/REQ-NNN-<slug>.md`.
- A requirement may only be handed to `pm-team` once its status is `approved`.
