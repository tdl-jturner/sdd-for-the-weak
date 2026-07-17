---
spec: S<nn>
source: D1–D<last>
---
# SPEC — S<nn>: <feature name>
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
