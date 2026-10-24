# Selective promotion

## Permission and ownership first

Sharing requires **explicit authorization** for selected content, destination,
and audience. Enabling local capture or requesting a memory review is not that
authorization. A Git-ignored local record is not safe to publish by default.
Do not stage, commit, push, open a PR, or change repository visibility implicitly.
An authorized shared-store write still does not authorize those Git actions.

Discover the destination's existing owner and contract before drafting.
If direct edits exceed the writer's authority, propose changes through the
owner's established process instead. The standalone helper only writes recognized stores under
`.maruti/memory/`; it is not a backdoor into other bundles. If destination
authority is unknown or conflicting, withhold the write.

## Review a minimal candidate

Select claims, not whole files or stores. Read their actual sources and inspect
current destination content within the recall budget. Check for credentials,
secrets, unnecessary personal information, private repository names, workstation
paths, conversation details, raw logs, and inaccessible sources. Do not assume
shared readers can access the local store, private URLs, or a machine path.

Where a source is private or inaccessible to the audience, find an independently
shareable authoritative source actually read, narrow the claim to what that
source supports, or withhold it. Do not simply strip citations while retaining
an unsupported claim. Preserve provenance without revealing private source text,
identifiers, or links. If safe provenance cannot be represented, stop at a
private proposal and explain the limitation without leaking it.

## Propose, then write only if authorized

A minimal proposal names target, action, owner, reason, shareable evidence,
proposed text, applicability, and uncertainty. Keep it local/private until
authorization covers delivery to the proposed audience; even an issue comment
or committed handoff can expose the finding. Never claim owner acceptance merely
because a proposal was sent.

For an explicitly authorized standalone shared write, inspect compatibility
with helper `doctor`; obtain approval for creating/enabling a shared store if
one is missing. Use the shared role and `--allow-shared` only as documented in
the [runtime guide](runtime-guide.md). Read current content/hash, preserve its
unknown keys and distinct evidence, write with compare-and-swap, then refresh
the affected topic catalog and verify the result. Local identities and timestamps
must not be relabeled as historical shared verification.

If the helper refuses the destination or schema, report it; do not manually copy
Markdown as a fallback. Existing ownership does not change after promotion.
Report whether content was proposed, withheld, or actually written, and any
remaining inaccessible evidence. Do not imply the local store was Git-published.
