---
spec: S3
status: COMPLETE
areas_done: 11 of 11
---
# DECISIONS — S3: Project status badge
## Summary
Show a colored status badge on each project card in the portal so members see project health at a glance.
## Decision Log
D1: Users are portal members; the badge shows project health at a glance.
D2: Out of scope: badge history, notifications, custom colors.
D3: EXISTING CODE — greenfield, N/A.
D4: Badge states: green (on track), yellow (at risk), red (blocked).
D5: The badge state is set manually by the project owner from the card menu.
D6: Only the project owner changes the badge; everyone can see it.
D7: EXTERNAL SYSTEMS — N/A per user.
D8: Badge change is verified by a unit test: setting a state updates the card.
## Unresolved
UNRESOLVED: What does a project with no badge set display?
UNRESOLVED: Is there a limit on how often the badge can change?
