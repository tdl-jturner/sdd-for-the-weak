---
name: to-spec
description: Step 2 of the spec pipeline. Reformats a completed DECISIONS.md into SPEC.md, marking every gap UNRESOLVED, then walks the user through a review. Use when the user asks to write the spec or turn a decision log into one. Run in a fresh conversation, never the one that held the interview.
---

# SKILL: WRITE-SPEC — Decision Log → Spec (spec-pipeline binding)
The reformatting engine lives in
`.claude/skills/populate-template/PROTOCOL.md`. Read that file NOW and
follow it exactly. This file supplies only the spec-pipeline bindings and
the rules the protocol does not cover.
## Bindings
- SOURCE: DECISIONS.md in the feature folder `specs/S<nn>-<slug>/`. Find
  the right folder by reading only each DECISIONS.md frontmatter — you
  want `status: COMPLETE`; if several qualify and the user didn't name
  one, ask. Auxiliary source: the project-wide `specs/GLOSSARY.md` (used
  only as the glossary rules below say).
- TEMPLATE: `template.md` in this skill's directory. Its catch-all
  section is 12 (Other decisions); its open-questions section is 13
  (Open Questions).
- OUTPUT: SPEC.md next to DECISIONS.md.
- REVIEW MESSAGE: "SPEC.md is saved and verified. Please review it now —
  especially section 13 (Open Questions). Tell me any corrections, or say
  'done'. When you are satisfied, run spec-critique in a fresh
  conversation (recommended lens order: TRACE, HOLES, CLASH, TEST,
  VAGUE)."
## Additional hard rules (bind exactly like the protocol's)
- Build spec section 4 from specs/GLOSSARY.md: copy VERBATIM the entry of
  every glossary term whose name appears anywhere in your spec text. This
  is a mechanical scan, not a judgment call — term appears, entry gets
  copied. Never edit a definition, never add a term the glossary doesn't
  have.
- Acceptance criteria must be mechanically checkable. Bad: "search is
  fast." Good: "Searching 10,000 records returns results in under 1
  second (D22)." If the log contains testing decisions (interview area
  10), state for each criterion how it is verified: unit test,
  integration test, or manual step.
## Additional self-check (runs as protocol self-check step 4)
- Scan your draft for glossary term names: every term that appears in the
  spec text has its entry copied verbatim into section 4.
## REMINDER (read this last, follow it first)
Everything in PROTOCOL.md applies: reorganize, never invent; every gap
becomes UNRESOLVED; every decision ID lands somewhere; silent self-check,
then save with a real tool call and verify — printing is not saving. On
top of that: section 4 is a mechanical verbatim copy from
specs/GLOSSARY.md, acceptance criteria must be checkable with a stated
verification, and corrections that are decisions go into DECISIONS.md,
never silently into the spec.
