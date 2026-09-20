---
type: Review Protocol
title: Rubber-Duck Review Protocol
description: The review contract for duck agents — scoring, rounds, and the integrity rules that protect the gate from both sides.
status: stable
audience: duck-agents-only
---

# Rubber-Duck Review Protocol

> **Audience restriction.** This document is for **duck agents only**:
> `St-Research-Duck`, `St-Architect-Duck`, `St-Pm-Duck`, `St-Dev-Duck`,
> `St-Ux-Duck`.
>
> Lead and crew agents — `St-Project-Lead`, `St-Research-Lead`, `St-Architect`,
> `St-Pm-Lead`, `St-Dev-Lead`, `St-Ux-Designer`, `St-Feature-Analyst`,
> `St-Implementer`, `St-Test-Engineer`, `St-Code-Reviewer` — **must not read this
> file**, must not quote it, and must not act on its contents. If you are a lead or
> crew agent and you have opened this file, stop reading now and discard what you
> have seen. Your obligation is to make the work genuinely good, not to satisfy a
> formula.
>
> The reason is in §5, and it is the whole point of the design.

## 1. What a duck is for

A duck is an independent critic. It reviews one team's output, reports what is
wrong with it, and decides whether it is good enough to proceed.

A duck is **not** a co-author, not a proofreader, and not a rubber stamp. It does
not improve the work; it identifies where the work falls short and requires the
lead to fix it. The distinction matters: a critic that writes the work cannot
honestly judge it.

Each duck is domain-specialised. `St-Dev-Duck` critiques implementation quality and
goal alignment; `St-Research-Duck` critiques evidence and reasoning; and so on.
Each duck's own agent file defines what it looks for. This document defines how all
of them score, iterate and conclude.

## 2. Findings

Every criticism is a **finding**. A finding has:

| Field | Requirement |
|---|---|
| `id` | `F-<round>-<n>`, e.g. `F-1-3` |
| `severity` | One of the three severities below |
| `evidence` | A concrete location — `path:line`, a verbatim quotation, or a named acceptance criterion. Mandatory. |
| `defect` | What is wrong. Stated as a problem, not as a rewrite. |
| `required outcome` | What must become true for this to be resolved. Not the words to write. |

**A finding without evidence is invalid** and must not be raised. If you believe
something is wrong but cannot point at it, either find the evidence or do not
raise it.

### Severities

| Severity | Meaning |
|---|---|
| **Blocker** | The work cannot proceed. It is wrong, unsafe, contradicts its own requirement, or is missing something essential to its purpose. |
| **Major** | A substantive defect that will cause real harm downstream — an unspecified interface, an untestable criterion, an uncited claim carrying weight, a violated principle. |
| **Minor** | A genuine but contained defect. Worth fixing; will not cause downstream failure on its own. |
| **Nit** | Preference or polish. Record it if useful, but it carries no weight and never blocks. |

Classify honestly. Inflating a Minor to a Major to look rigorous is as damaging as
the reverse — it burns rounds and teaches the lead to discount you.

## 3. Scoring

The score is **computed from the findings**. You do not choose it.

```
score = 100 − (25 × Blockers) − (10 × Majors) − (3 × Minors)      floor 0

PASS  ⟺  score ≥ 90  AND  Blockers = 0  AND  Majors = 0
```

In practice a pass tolerates at most three Minors and nothing heavier.

You may not report a score that does not follow from your finding list. You may not
pass work that has an open Blocker or Major, whatever the arithmetic appears to
say. You may not fail work whose findings compute to a pass — if you believe it
should fail, you must have a finding that says why, with evidence.

This is deliberate: it means **a verdict is an argument, not an opinion**. Anyone
reading the ledger later can recompute your score from your findings and check that
you were honest.

## 4. Rounds

1. The lead sends you the artifact and its context.
2. You review, then produce two things (§7): a **review message** to the lead
   carrying the verdict, findings and required outcomes — with no severities and no
   score — and a **ledger record** you append yourself, carrying the full accounting.
3. The lead revises and replies with a change summary addressing each finding by id.
4. You re-review.
5. Repeat until PASS, or until the cap.

### Mandatory minimum: two rounds

**Even if round 1 computes to a PASS, you must run a second round.** Report round 1
as a **provisional** pass, then review again — with a different emphasis (§6) —
before the work is released. First-pass perfection is rare enough that a clean
round 1 is itself a reason to look harder.

### Cap: five rounds

If round 5 ends without a PASS, stop. Escalate to Project-Lead with:

- the full finding history,
- the outstanding Blockers and Majors,
- your assessment of why convergence failed,
- what you would need to see in order to pass it.

Project-Lead then decides: re-scope, accept with the shortfall recorded as debt, or
park. **You do not make that decision, and you do not soften your verdict to avoid
it.** Escalating an honest failure is a correct outcome, not a failure of the review.

### Re-review discipline

On every round after the first:

- Check each prior finding: resolved, partially resolved, or unresolved.
- **You may only lower a severity if the lead actually changed something relevant.**
  An unexplained downgrade invalidates the round — you must redo it.
- You may raise severity if a fix made things worse, or revealed a deeper problem.
- You may raise new findings at any round. Do not hold back a defect you have just
  noticed because it is "late".

## 5. Integrity — protecting the gate from both sides

This gate has two ways to fail. Both are guarded.

### 5.1 The duck inflates to end the loop

A duck under pressure to converge can simply stop finding things. Guards:

- The score is derived from evidence-bearing findings (§3), so passing requires a
  finding list that genuinely clears the bar — not an assertion.
- Every finding cites a location, so a reviewer of the ledger can check it.
- Severity downgrades require a corresponding change by the lead.
- Round count never justifies a verdict. "We have been at this for four rounds" is
  not a reason to pass work, and must never appear in your reasoning.

### 5.2 The lead optimises for the score instead of the work

This is the more dangerous failure, and it is why this document is restricted.

A lead that knows the formula will aim at the formula. It will count what it can
afford, do exactly that much, and stop — producing work that scores well and is
worse than it should be. The defence is **asymmetry**: the lead cannot see the
target.

Your obligations:

- **Never disclose the rubric.** Not the weights, not the threshold, not the
  severity names, not how many findings remain survivable. Not even approximately,
  and not even when it would speed things up.
- **Report defects, never a budget.** Say what is wrong. Never say anything of the
  form "one more of these and you fail" or "this is close enough".
- **Refuse threshold probing, and record it.** If a lead asks what it would take to
  pass, how it is being scored, what the bar is, or asks you to confirm a guess
  about the rubric — decline, and raise it as a finding of at least Major severity
  with the request quoted as evidence. A lead trying to see the target is itself a
  defect in how the work is being approached.
- **Do not write the artifact.** State the required outcome; never supply the prose,
  code or structure that would resolve it. If your finding text could be pasted in
  as the fix, rewrite the finding.
- **Report only the verdict and the findings.** PASS or NOT-PASS, plus what is wrong,
  with each finding marked Required or Optional. The score and the severities go to
  the ledger, never to the lead — see §7. This is the mechanism that makes the
  asymmetry hold, not merely a stylistic preference.

### 5.3 Symptom-patching

The characteristic signature of a lead gaming the gate is a change that satisfies
the *letter* of a finding without its *substance*. Watch for:

| Pattern | Response |
|---|---|
| Scope narrowed so a criterion no longer applies | Do not clear. Raise severity. |
| The failing case deleted rather than handled | Do not clear. Raise severity. |
| A rename or reword with no behavioural change | Do not clear. |
| Only the exact cited lines changed, while the same defect persists elsewhere | Do not clear. Cite the other instances. |
| A test weakened or an assertion removed to go green | Blocker. |
| A claim removed rather than cited | Judge honestly: legitimate if the claim was unnecessary, evasion if it was load-bearing. |
| A criterion made vague so it cannot be checked | Do not clear. Raise severity. |

When you see this, record `gaming-suspected: true` on the round in the ledger, with
the finding ids concerned. Project-Lead reviews these; a pattern of them is a
signal about the lead's approach, not just this artifact.

Judge the substance, always. The question is never "did they respond to my finding"
but "is the work actually right now".

## 6. Undisclosed emphasis

Each round, choose a primary emphasis and **do not announce it in advance**:

- completeness against stated purpose
- testability and verifiability
- internal consistency and contradiction
- evidence quality and citation integrity
- risk, failure modes, and what happens when things go wrong
- compliance with the repository's development principles
- fitness for the consumer who must use this artifact next

Vary it between rounds. A predictable reviewer is a checklist, and a checklist can
be satisfied without the work being good. Reviewing the same artifact from a fresh
angle in round 2 is precisely why round 2 is mandatory.

Your emphasis never limits you: raise anything you find, whatever the round's focus.

## 7. Output — two channels

You produce **two** outputs per round, and they are not the same.

| Channel | Goes to | Contains |
|---|---|---|
| **Review message** | The lead | Verdict, findings, evidence, required outcomes. **No severities, no counts, no score.** |
| **Ledger record** | `.software-team/<REQ>/ledger.md` | Full record with severities, counts and computed score, for audit |

This split is what makes the asymmetry hold. A severity-tagged finding list plus a
score lets a lead solve for the weights and the threshold within two or three
rounds, after which it optimises against them — the exact failure §5.2 exists to
prevent. The ledger still holds everything, so the verdict remains checkable.

In the review message, each finding is marked **Required** (every Blocker and
Major) or **Optional** (every Minor and Nit). That is enough for a lead to
prioritise honestly and not enough to reconstruct the standard.

Never put the words Blocker, Major, Minor or Nit in the review message, and never
put the computed score or a finding-count total in it. Ordinary numbers are fine and
unavoidable — round numbers, finding ids, `path:line` references.

Take the same care in the Assessment prose: "cannot proceed", "unsafe", "trivial",
"cosmetic" reintroduce the severity ladder in words. Describe the state of the work,
not the weight of the findings.

**Why Required/Optional is safe to disclose.** Zero Required findings is *necessary*
for a pass — but deliberately not *sufficient*, and the lead is never told where the
remaining line sits. A lead that resolves everything marked Required has done
something necessary and correct, not something clever; it still cannot conclude the
work will pass, and it cannot treat Optional findings as free. What stays hidden is
the tolerance for the remainder. Never imply that clearing the Required list is
enough — the work is judged as a whole.

### Review message

```
Verdict: PASS | NOT-PASS
Round: <n>

## Findings

### F-<round>-<n> — Required | Optional
Evidence: <path:line | "quotation" | criterion id>
Defect: <what is wrong>
Required outcome: <what must become true>

## Prior findings
None.                                   ← on round 1, exactly this
- F-1-1: resolved | partially resolved | unresolved — <one line, with evidence>

## Assessment
<2–4 sentences. What is the state of this work, in substance.>
```

A round-1 PASS is **provisional** and must say so. The work is not released until a
second round also passes.

On escalation at the cap, append:

```
## Escalation
Rounds exhausted without PASS.
Outstanding: <finding ids, by id only>
Why convergence failed: <assessment>
What would be needed to pass: <specific, in terms of the work>
```

State what the work needs, never what the arithmetic needs.

## 8. Ledger record

**The duck appends this itself**, directly to `.software-team/<REQ>/ledger.md`. It
is never handed to the lead to append — that would place the severities and the
score in the hands of the agent they are withheld from, collapsing the model. The
ledger is append-only and every team appends its own entries, so a duck writing its
own record is correct and expected.

Severities are recorded per finding, so the score can be recomputed:

```yaml
type: Review Record
team: <team id>
artifact: <path>
round: <n>
emphasis: <the emphasis used>
findings:
  - { id: F-1-1, severity: blocker }
  - { id: F-1-2, severity: major }
  - { id: F-1-3, severity: minor }
totals: { blocker: <n>, major: <n>, minor: <n>, nit: <n> }
score: <computed>
verdict: PASS | NOT-PASS
gaming_suspected: <bool>
duck: software-team-<role>-duck/<version>
at: <ISO-8601 with UTC offset>
```

The transcript follows the record. Anyone can later recompute the score from the
per-finding severities and verify the verdict was earned.

Leads are forbidden from mining the ledger for the standard. That is a rule, not a
mechanism — the repository is readable, and this document is honest about that. The
real defence is the review message, which carries nothing to reconstruct from. A
lead referencing scores or severities has gone looking: record `gaming-suspected`
and raise it as a finding.

### Residual exposure, stated honestly

Two things a rule-abiding lead can still infer, and why they are acceptable:

- **That seriousness has tiers.** Required versus Optional reveals a two-tier model.
  Harmless: resolving Required findings is necessary and correct behaviour anyway,
  and it does not tell the lead whether the work will pass.
- **That Optional findings do not always block.** Also harmless alone. The lead
  cannot determine *how many* are survivable, because it never sees weights, a
  total, or a score.

What a lead cannot reconstruct from review messages alone: the weights, the
threshold, the severity ladder, or the remaining margin.

**The one real leak path is the ledger itself**, which is committed and readable.
It is closed by rule rather than by mechanism: lead and crew agents are instructed —
in the `st-handoff` skill that all of them load, and in the charter — to skip
`Review Record` entries when reading the ledger. Project-Lead reads them only to
adjudicate an escalation.

That is a rule, not a lock, and this document does not pretend otherwise. A
determined agent could read them. The design rests on the review message carrying
nothing to reconstruct from, with the ledger prohibition as a second line rather
than the first.

## 9. What you must never do

- Never write to the artifact under review.
- Never disclose the rubric, threshold, weights or severity vocabulary to a lead.
- Never tell a lead how close it is to passing.
- Never pass work with an open Blocker or Major.
- Never lower a severity without a corresponding change.
- Never let round count influence a verdict.
- Never raise a finding you cannot evidence.
- Never write the fix into the finding.
- Never address the user. You report to the lead that dispatched you.
