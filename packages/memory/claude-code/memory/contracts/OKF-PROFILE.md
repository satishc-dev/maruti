# Generic Memory OKF profile

Memory uses Open Knowledge Format **0.2** independently of any consuming
workflow, organizational roles, or project-specific document tree. Consumers
may add their own ownership adapters without changing this generic format.

The root `index.md` has exactly `okf_version: "0.2"` in YAML frontmatter.
Nested `index.md` files have no frontmatter. `index.md` and `log.md` are
reserved, not concept names. Concepts have a nonempty string `type`; type
vocabulary is open. Templates use `Observation`, `Checkpoint`, `Decision`,
`Reference`, and `Memory Conventions`. `status` is document trust only:
`draft`, `stable`, or `deprecated`; absence means stable, never delivery state.

Recommended metadata: `title`, `description`, `tags`, `generated`, `status`.
Unknown keys are preserved. `generated` is a mapping with mandatory `by`;
`at`, when supplied, records the last meaningful content change. `owner`
names accountability, independently from `generated.by` authorship.

Actors use `<producer>/<version>`, `human:<id>`, `team:<id>`, or `process:<id>`.
The helper does not invent authors, verifiers, or sources. Templates omit
verification and sources until real evidence exists. `maruti-memory/0.1.0`
is a valid helper actor only for text actually authored by that helper;
caller-supplied content must name its actual writer.

`verified` is a mapping or list of mappings with `by`. No empty verification.
`sources` is a list of mappings each requiring `resource`; optional `id`
joins the exact footnote label. Omit sources if none were used. Load-bearing
sourced claims carry a matching footnote. Source authors use actor grammar.
`usage_window` belongs beside `sources`, never inside a source.

All timestamp fields, including `generated.at`, `verified.at`, `stale_after`,
`sources[].last_modified`, `usage_window.from/to`, and extension timestamps,
use ISO-8601 with explicit UTC offset. Bare dates are only log headings.

Standard Markdown links only; no wikilinks. Same-bundle links start with `/`
and resolve from the bundle root. Links leaving a bundle do not start `/`;
absolute stable URLs are allowed. Footnote labels match `sources[].id`
exactly; never use unstable positional labels.

Readers preserve unknown metadata and tolerate unfamiliar types. The runtime
validates its own writes strictly; it does not rewrite foreign bundles or
pretend its advisory conformance findings are delivery gates. Existing invalid
documents are reported, not normalized silently.
