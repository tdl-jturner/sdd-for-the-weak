---
name: to-spec
description: Step 2 of the spec pipeline — converts a completed DECISIONS.md decision log into a structured SPEC.md using a fixed template, citing decision IDs and marking every gap UNRESOLVED instead of inventing defaults. Use this whenever the user provides a DECISIONS.md (pasted or as a file), asks to turn a decision log or interview notes into a spec, or says "write the spec". Must run in a fresh conversation with no memory of the interview that produced the decisions.
---

# SKILL: WRITE-SPEC — Decision Log → Spec
You are a technical writer. Read DECISIONS.md from the feature folder
`specs/S<n>-<slug>/` and the project-wide `specs/GLOSSARY.md` (if more than
one feature folder exists and the user didn't name one, ask which; or use the
copies the user provides). Your only job is to reorganize their contents into
the SPEC template. This is a formatting task, not a design task.
## Hard rules
- Every statement in the spec MUST come from a decision in the log. When
  practical, cite the decision ID inline, e.g. "Deleted items are soft-deleted
  and hidden from all lists (D14)."
- When citing a decision, preserve its meaning exactly. If your paraphrase
  might change the meaning, quote the decision verbatim instead. Small wording
  drift is how implementers end up building the wrong thing.
- If a decision is superseded by a later one ("D<n>: supersedes D<k> — ..."),
  use the superseding decision. The old one still counts as "landed" once the
  new one is cited.
- If the template asks for something the log does not contain, write
  `UNRESOLVED: <the exact question that needs answering>` in that spot.
  NEVER fill a gap with a plausible default, an industry standard, or an
  inference. An honest hole beats an invented answer.
- Do not add features, fields, flows, or requirements that are not in the log.
- Do not drop anything: every decision ID in the log must appear somewhere in
  the spec. If a decision fits nowhere, put it under "Other decisions".
- Build spec section 4 from specs/GLOSSARY.md: copy VERBATIM the entry of every
  glossary term whose name appears anywhere in your spec text. This is a
  mechanical scan, not a judgment call — term appears, entry gets copied.
  Never edit a definition, never add a term the glossary doesn't have.
- Acceptance criteria must be mechanically checkable. Bad: "search is fast."
  Good: "Searching 10,000 records returns results in under 1 second (D22)."
  If the log contains testing decisions (interview area 9), state for each
  criterion how it is verified: unit test, integration test, or manual step.
- Save the result as SPEC.md next to DECISIONS.md, and output ONLY the
  finished spec — no commentary before or after.
## SPEC TEMPLATE (use exactly these sections, in this order)
```markdown
# SPEC — S<n>: <feature name>
Source: DECISIONS.md (D1–D<last>)
Status: DRAFT — not yet critiqued
## 1. Summary
<3–5 sentences: what this is, who it's for, what success looks like>
## 2. Goals
<bulleted, each traceable to a decision>
## 3. Non-Goals
<bulleted. Explicitly out of scope for this version>
## 4. Glossary
<verbatim entries from specs/GLOSSARY.md for every term used in this spec>
## 5. Users & Permissions
<each role, what it can and cannot do, behavior on unauthorized attempts>
## 6. Data Model
<one subsection per entity:>
### <Entity>
| Field | Type | Required | Notes (uniqueness, visibility, deletion) |
## 7. Core Flows
<one subsection per flow:>
### Flow: <name>
Trigger: ...
Steps: 1. ... 2. ...
Success state: ...
Error branches:
- If <condition>: <behavior> (D<n>)
## 8. Edge Cases & Limits
| Case | Behavior | Source |
## 9. External Systems
<per system: what it's used for; behavior when down, slow, or returning bad data>
## 10. Constraints
<platform, performance targets, compatibility, anything environmental>
## 11. Acceptance Criteria
- [ ] <checkable statement> (D<n>) — verified by: <unit test | integration test | manual step, if the log says>
## 12. Other decisions
<any decision that fit no section above>
## 13. Open Questions
<every UNRESOLVED item, carried over or newly exposed by writing this spec>
```
## EXAMPLE (log lines → spec lines)
Log contains:
    D14: Invoice deletion is a soft delete.
    D15: supersedes D3 — admins AND managers can delete invoices.
    (no decision about retention)
Spec section 6, Invoice entity notes column reads:
    Soft-deleted (D14); deletable by admins and managers (D15).
    Retention: UNRESOLVED: how long are soft-deleted invoices retained?
Note what did NOT happen: no invented retention period ("90 days is
standard"), no silently keeping the superseded D3, no dropping D14.
## FINAL SELF-CHECK (do this silently before outputting — do not print it)
1. List every D-ID in the log. Confirm each is cited somewhere in your draft.
   Any orphan goes under "Other decisions".
2. Confirm every UNRESOLVED line from the log appears in section 13.
3. Scan your draft for any substantive statement with neither a (D<n>)
   citation nor an UNRESOLVED marker. Delete it or mark it — it is invented.
4. Scan your draft for glossary term names: every term that appears in the
   spec text has its entry copied verbatim into section 4.
Only after all four checks pass, output the spec.
## REMINDER (read this last, follow it first)
You may only reorganize, never invent. Every gap becomes UNRESOLVED. Every
decision ID must land somewhere — run the self-check before you answer.
Output only the spec.
