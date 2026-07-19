---
spec: S<nn>
source: D1–D<last>
---
# SPEC — S<nn>: <feature name>
## 1. Summary
! 3–5 sentences: what this is, who it's for, what success looks like
? who uses this and what problem it solves
? how we know it worked — the observable success signal
## 2. Goals
! bulleted, each traceable to a decision
? the goals of this version
## 3. Non-Goals
! bulleted; explicitly out of scope for this version
? at least 3 non-goals — vague scope is the #1 spec killer
## Existing Code (interview only — nothing here renders into the spec)
! Greenfield project? Record `D<n>: EXISTING CODE — greenfield, N/A` and
  move on.
! Gather facts yourself BEFORE asking: entry points, the modules this
  feature would touch, the test setup, the naming conventions. NEVER ask
  the user which files or functions to change — the user may never have
  read the code; research it yourself. Every question presents YOUR
  finding for a yes/no: "This looks like it lives in the move logic in
  game.js; the UI must not change — correct?" The user confirms behavior
  and constraints, never code internals. A finding becomes a decision
  only when the user confirms it; record confirmed findings as decisions
  WITH file paths — a spec that ignores the real codebase contradicts
  reality.
? where this feature lives in the existing code — file paths, confirmed
  by the user
? constraints the existing code imposes: what must not change
## 4. Glossary
! copy VERBATIM the entry of every specs/GLOSSARY.md term whose name
  appears anywhere in this spec — a mechanical scan, not a judgment
  call. Never edit a definition, never add a term the glossary lacks.
## 5. Users & Permissions
! each role: what it can and cannot do, behavior on unauthorized attempts
? who can do what; what happens on an unauthorized attempt
? admin or override paths
## 6. Data Model
! one subsection per entity
### <Entity>
| Field | Type | Required | Notes (uniqueness, visibility, deletion) |
? entities and their fields: types, required/optional, uniqueness
? visibility: who can see each entity
? deletion: ever deleted? hard or soft?
## 7. Core Flows
! one subsection per flow
### Flow: <name>
Trigger: ...
Steps: 1. ... 2. ...
Success state: ...
Error branches:
- If <condition>: <behavior> (D<n>)
? each main user action: trigger, steps, end state, what the user sees
  on success
## 8. Edge Cases & Limits
| Case | Behavior | Source |
? per flow: invalid input, duplicate action, missing or deleted
  referenced data, concurrent edits, empty states
? limits: max size, max count, rate
## 9. External Systems
! per system: what it's used for; behavior when down, slow, or returning
  bad data
? APIs, services, files, or systems this touches — and what happens when
  each is down, slow, or returns garbage
## 10. Constraints
! platform, performance targets, compatibility, anything environmental
? platform, language, or framework requirements; performance targets
? compatibility or migration needs; deadlines that affect scope
## 11. Acceptance Criteria
- [ ] <checkable statement> (D<n>) — verified by: <unit test | integration test | manual step>
! every criterion mechanically checkable — numbers and observable
  outcomes, never vague adjectives. Bad: "search is fast." Good:
  "Searching 10,000 records returns results in under 1 second (D22)."
  Cite each criterion's D-number and, when the log says how, its
  verification: unit test, integration test, or manual step
? per core flow: how we verify it works and the observable signal that
  proves success — push for numbers; these become acceptance criteria
? the riskiest flow, deserving the most test coverage
## 12. Other decisions
! every decision that fit no section above lands here — none may drop
## 13. Open Questions
! every UNRESOLVED item, carried over from the log or newly exposed by
  writing this spec
