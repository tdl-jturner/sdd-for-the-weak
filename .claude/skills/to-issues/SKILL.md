---
name: to-issues
description: Step 4 of the spec pipeline. Decomposes SPEC.md into an issues/ folder — one file per issue plus INDEX.md — and on re-runs appends new issues without touching existing ones. Use when the user asks to break a spec into issues, tasks, or a plan, or to update the issues after a spec change. Fresh conversation; plans only, writes no code.
---

# SKILL: ISSUES — Spec → Sequential Issue Files
You are a planner. Read SPEC.md from the feature folder `specs/S<nn>-<slug>/`
(if more than one feature folder exists and the user didn't name one, ask
which). Your only job is to decompose the spec into ordered issues, written
as ONE FILE PER ISSUE in `specs/S<nn>-<slug>/issues/`, plus an INDEX.md
listing the build order. You plan from the spec only — you do not design new
behavior, and you do not write code.
One file per issue is deliberate: the implementer reads only its own issue
file, so it never has the other issues in context tempting it to keep going.
## What makes a good issue
Every issue is a vertical slice: one thin piece of OBSERVABLE behavior
end-to-end — enough interface to trigger it, enough logic to do it, enough
storage to persist it, and a test that proves it. Never split horizontally by
layer ("all the models", then "all the endpoints", then "the UI") — a layer
on its own cannot be tested as behavior, and the sessions building the layers
die before the layers ever meet. The first issue is always the walking
skeleton: the thinnest possible end-to-end path through the feature, proving
the pieces connect.
## Issue IDs and filenames
Issues are numbered `S<nn>-I<mm>`: the feature folder's S-number plus a
sequential issue number, BOTH zero-padded to two digits — `S01-I02` is spec
1, issue 2. Padding is load-bearing: it makes a plain alphabetical sort of
file paths identical to the build order, and later steps rely on that sort
instead of reading files (unpadded, I10 sorts before I2). The next I-number
is always the highest existing I-number plus one. IDs are permanent — never
changed, never reused. Filename: `S<nn>-I<mm>-<short-slug>.md`, e.g.
`issues/S01-I02-soft-delete-invoice.md`.
## Hard rules
- Every issue must cite the spec sections and the section 11 acceptance
  criteria it implements. An issue containing work the spec does not require
  is scope creep — delete it or flag the missing criterion under Open
  questions in INDEX.md.
- Every acceptance criterion in spec section 11 must appear in at least one
  issue's "Covers" line. A criterion no issue covers is work you forgot to
  plan.
- Every issue lists its Files: which files it may create or edit, each with a
  short why. Derive them from the spec's constraints (section 10), the
  feature's flows, and earlier issues' Files lists — keep names consistent
  across issues. This is the implementer's guardrail: an implementer needing
  an unlisted file means the plan was wrong, and that should be visible.
- If an issue's spec sections contain UNRESOLVED items that affect it, set
  `status: BLOCKED: <the open question>` in its frontmatter. Never plan
  around a gap by guessing.
- Keep issues small: 1–3 tests, a handful of files, one short working
  session. The implementer is a small model with a small context; an issue
  that needs a big context will fail. When in doubt, split.
- Issues are SEQUENTIAL. Order them by dependency; an issue may only depend
  on lower-numbered issues, and they will be implemented in order.
- SAVE every issue file and INDEX.md with your file-writing tool — printing
  is not saving. Then VERIFY: list the issues/ folder and confirm every file
  you claim exists is there. Only then report. Output a short summary (issue
  IDs + names), not the full file contents.
- After saving, RUN the validator and paste its output:
  `node .claude/skills/to-issues/scripts/validate-issues.js specs/S<nn>-<slug>`
  It deterministically checks numbering, statuses, INDEX-vs-disk, and
  criterion coverage — rules in prompts are probabilistic, the script is not.
  Fix every failure and re-run until it prints PASS. Never report success
  over a failing validator.
## Files to produce
### issues/INDEX.md — build order only (statuses live in the issue files)
```markdown
# ISSUES INDEX — S<nn>: <feature name>
Source: SPEC.md
Implement in this order. Current status is in each issue file's frontmatter.
1. S<nn>-I01-<slug>.md — <name>
2. S<nn>-I02-<slug>.md — <name>
## Open questions
<criteria with no issue, issues blocked on UNRESOLVED items, anything the
user must resolve before implementation>
```
### issues/S<nn>-I<mm>-<slug>.md — one per issue
```markdown
---
id: S<nn>-I<mm>
status: TODO
depends_on: none | S<nn>-I<kk>
evidence: none
---
# S<nn>-I<mm>: <name>
Goal: <one sentence of observable behavior>
Spec: sections <section numbers>
Covers: <the section 11 acceptance criteria this issue implements, quoted>
Files: <file — why it is needed; one per line>
Test first: <concrete name/description of the first failing test to write>
Done when: <mechanically checkable statement>
```
## EXAMPLE ISSUE FILE (imitate this shape)
```markdown
---
id: S01-I02
status: TODO
depends_on: S01-I01
evidence: none
---
# S01-I02: Soft-delete an invoice
Goal: An admin can delete an invoice; it vanishes from lists but stays in the database.
Spec: sections 6 (Invoice), 7 (Flow: Delete)
Covers: "Deleting an invoice hides it from all lists (D14)"
Files: app.js — delete handler and list filtering; app.test.js — the new tests
Test first: test_delete_invoice_hides_from_list_but_keeps_row
Done when: that test and the full suite pass; a deleted invoice is absent from the list endpoint and present in storage with a deletion marker.
```
Note the shape: observable behavior, cited spec sections, a bounded Files
list with reasons, a named first test, a checkable finish line. No code, no
design the spec doesn't contain.
## Re-running after a spec update (issues/ already exists)
The issues/ folder is a LEDGER. Frontmatter statuses and evidence are the
only record of work already done — losing them means losing the build state.
- Never modify, rename, renumber, or delete an existing issue file, with one
  exception: a still-TODO issue obsoleted by the new spec gets
  `status: DROPPED: <reason>` in its frontmatter — dropped, not deleted.
- Diff the new spec's section 11 criteria against the existing Covers lines.
  Write a NEW issue file (next I-number) for each criterion that is new or
  changed, and append it to INDEX.md.
- If the new spec changes behavior a DONE issue already built, write a new
  revision issue, e.g. `S01-I08: Revise soft-delete retention per D31`. Same
  move as a superseding decision: history stays, the correction is new.
Example: issues S01-I01…I06 exist, I01–I04 DONE. New spec adds one criterion and
changes retention behavior built by DONE issue S01-I02. Correct result: all six
files untouched; new files S01-I07 (new criterion) and S01-I08 (revise retention
per D31); INDEX.md gains lines 7 and 8. Nothing renumbered, no status reset.
## FINAL SELF-CHECK (do this silently before reporting — do not print it)
1. Every acceptance criterion in spec section 11 appears in some issue's
   Covers line.
2. Every issue cites at least one spec section and lists at least one file
   with a reason.
3. Every depends_on points only to a lower-numbered issue.
4. Every spec section 13 open question that affects an issue shows up as
   BLOCKED or under Open questions in INDEX.md.
5. The issues/ folder listing matches INDEX.md exactly — every listed file
   exists on disk (this catches unsaved files).
6. If this was a re-run: every pre-existing file is unchanged except a
   TODO→DROPPED status; all new content is new files with fresh I-numbers.
Only after all checks pass, report the summary.
## REMINDER (read this last, follow it first)
One file per issue, plus INDEX.md for order. Every issue is a vertical
slice — thin end-to-end behavior, never a layer; the first is the walking
skeleton. Every criterion lands in an issue; every issue bounds its Files;
every gap becomes BLOCKED, never a guess. Save with real tool calls and
verify the folder listing. On re-runs, existing files are untouchable.
