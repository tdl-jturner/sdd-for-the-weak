---
name: lens-critique
description: Reviews a document against the decision log it was built from, one narrow lens per run, reporting evidence-quoted findings without rewriting anything. Use when the user wants a lens-by-lens critique or red-team of a decision-log-derived document that is not a feature spec, naming the lens definitions to use. For feature specs, use spec-critique instead. Run in a fresh conversation, never the one that wrote the document.
---

# SKILL: LENS CRITIQUE (generic binding)
Read `PROTOCOL.md` in this skill's directory NOW and follow it exactly.
This file only supplies the bindings the protocol needs.
## Bindings
- DOCUMENT: the file the user named. If they didn't name one, ask.
- SOURCE: the decision log the document was populated from. If the user
  named only the document, ask which log — never guess.
- LENSES: the lens file the user named, or lenses they describe in chat
  (treat a described lens exactly like a one-entry lens file). If
  neither, ask — never invent lenses.
- COMPLETION MESSAGE: "Critique complete. Resolve 'needs user decision'
  items in the decision log, then re-run populate-template in a fresh
  conversation and critique again."
## Notes
- One lens file, many documents: the lens file is reusable; never write
  into it.
- The spec pipeline does not use this skill directly — spec-critique
  binds the same PROTOCOL.md to `specs/` with its own five lenses.
