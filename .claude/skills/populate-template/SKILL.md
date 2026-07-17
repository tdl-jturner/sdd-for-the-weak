---
name: populate-template
description: Reformats a completed decision log into a document template the user provides, marking every gap UNRESOLVED, then walks the user through a review. Use when the user has a decision log (e.g. from interview-me) and a template to fill from it, or wants a decision log turned into any document that is not a feature spec. For feature specs, use to-spec instead.
---

# SKILL: POPULATE TEMPLATE (generic binding)
Read `PROTOCOL.md` in this skill's directory NOW and follow it exactly.
This file only supplies the bindings the protocol needs.
## Bindings
- SOURCE: the decision log the user named. If they didn't name one, look
  in `decisions/` for logs whose frontmatter says `status: COMPLETE` and
  ask which. An IN PROGRESS log is not ready — send the user back to
  interview-me to finish it.
- TEMPLATE: the file the user named or provided. Never invent one; if it
  fails the TEMPLATE REQUIREMENTS in the protocol, say what's missing and
  stop.
- OUTPUT: the SOURCE path with the template's name spliced in before
  `.md` — e.g. SOURCE `decisions/eu-vat.md` + TEMPLATE `templates/prd.md`
  → `decisions/eu-vat.prd.md`. State the path as a labeled suggestion
  before saving so the user can redirect.
- REVIEW MESSAGE: "<OUTPUT path> is saved and verified. Please review it
  now — especially the open-questions section. Tell me any corrections,
  or say 'done'."
## Notes
- One template, many logs: the template is reusable; never write into it.
- The spec pipeline does not use this skill directly — to-spec binds the
  same PROTOCOL.md to `specs/` with its own SPEC template and glossary
  rules.
