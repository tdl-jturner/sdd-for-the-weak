---
name: spec-critique
description: Step 3 of the spec pipeline. Reviews SPEC.md against DECISIONS.md through one lens per run (TRACE, HOLES, TEST, VAGUE, or CLASH), reporting findings without rewriting anything. Use when the user asks to critique, review, red-team, or find holes in a spec. Run in a fresh conversation, never the one that wrote the spec.
---

# SKILL: CRITIQUE — Adversarial Spec Review (spec-pipeline binding)
The review engine lives in
`.claude/skills/lens-critique/PROTOCOL.md`. Read that file NOW and follow
it exactly. This file supplies only the spec-pipeline bindings.
## Bindings
- DOCUMENT: SPEC.md in the feature folder `specs/S<nn>-<slug>/` —
  critique the folder the user named; otherwise take the highest-numbered
  spec folder (sort the `specs/S*` folder names and take the LAST —
  zero-padded names make that the newest) and announce your pick so the
  user can redirect you. Or use the copies the user provides.
- SOURCE: DECISIONS.md next to that SPEC.md. Auxiliary source:
  the project-wide `specs/GLOSSARY.md` (the VAGUE lens checks terms
  against it).
- LENSES: `lenses.md` in this skill's directory (TRACE, HOLES, TEST,
  VAGUE, CLASH).
- COMPLETION MESSAGE: "To apply fixes: resolve 'needs user decision'
  items yourself, add them to DECISIONS.md, then re-run the to-spec skill
  in a fresh conversation. When your chosen lenses come back PASS,
  proceed to the to-issues skill."
## REMINDER (read this last, follow it first)
Everything in PROTOCOL.md applies: one lens only, findings only, every
finding quotes its evidence or is discarded, never answer an open
question, max 10 findings severity-ordered. Announce which spec folder
you picked before reviewing.
