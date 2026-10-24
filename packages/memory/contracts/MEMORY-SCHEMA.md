# Generic store schema 1

This schema is separate from OKF **0.2** and Memory package **0.1.0**.
The namespace is `maruti.memory`; store identities are UUIDs, not repository
names, paths, session IDs, or user identifiers.

| File | Shape | Authority |
|---|---|---|
| `.memory-store.json` | JSON identity and integer schema; see [runtime](RUNTIME.md). | Runtime initialization; preserved thereafter. |
| `index.md` | Only `okf_version: "0.2"` frontmatter; standard Markdown catalog. | Initial runtime projection, not claim evidence. |
| `topics/index.md` | No frontmatter; sparse topic entry point. | Initial runtime projection. |
| `topics/<slug>/<concept>.md` | Typed OKF concept. | Skill-approved full replacement with expected hash. |
| `topics/<slug>/index.md` | No frontmatter; derived topic-local links. | Runtime catalog primitive. |
| `sessions/index.md` | No frontmatter; sparse session entry point (local only). | Initial runtime projection. |
| `sessions/<id>/checkpoint.md` | Typed OKF checkpoint (local only). | Exact caller session. |
| `sessions/<id>/observations.md` | Typed OKF observations (local only). | Exact caller session. |

The runtime implements path safety, identity/schema guards, byte-level
concurrency and structural OKF validation. It does **not** decide truth,
trustworthiness, source currency, retention, contradictions, promotion intent,
secrets, personal information, or which evidence belongs in a store. Skills
make those decisions before passing a complete document to the writer.
Automatic capture after explicit enablement is local only. Never promote
because a document is merely present locally.

Unknown metadata is preserved, including nested extra fields. The writer
allows title/description/tags/trust status and actual generated writer/time to
change. Existing other keys and values cannot disappear or be silently
replaced; evidence lists may gain entries but must retain previous entries.
Body replacement requires an exact hash and deliberate skill judgment;
there is no semantic merge or autonomous contradiction resolution.

The generic vocabulary is open; `Observation`, `Checkpoint`, `Decision`,
`Reference`, and `Memory Conventions` are suggested types, not an enum.
`status` means OKF trust only; no workflow/team fields are required. Timestamp,
actor, citation and index rules are in the [OKF profile](OKF-PROFILE.md).
Existing project-owned bundles retain their actual owners and are outside
these writable roots; consumer-specific ownership belongs in consumer adapters.

There is no global capture log, automatic pruning, external embedding service,
recurring automation, model/runtime download, or implicit Git operation.
Total ignored store size does not gate privacy or writes. Recall has separate
scan/output budgets: exact topic/session selectors bypass unrelated history,
and incomplete scans fail explicitly instead of claiming there is no memory.
Any future schema migration must be separately reviewed; the v1 preview never
executes a migration, adopts an unknown directory, or rewrites old history.
