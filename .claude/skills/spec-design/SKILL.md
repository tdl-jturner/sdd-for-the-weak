---
name: spec-design
description: Step 1 of the spec pipeline. Interviews the user one question at a time and records their answers in a DECISIONS.md decision log. Use when the user has a feature idea to flesh out, asks to be interviewed or grilled about requirements, wants to start a spec, or wants to resume a partial DECISIONS.md.
---

# SKILL: SPEC DESIGN — Requirements Interview (spec-pipeline binding)
The interview engine lives in
`.claude/skills/interview-me/PROTOCOL.md`. Read that file NOW and
follow it exactly. This file supplies only the spec-pipeline bindings and
the rules the protocol does not cover.
## Bindings
- CHECKLIST: `checklist.md` in this skill's directory (the 10 areas).
- LOG: `specs/S<nn>-<feature-slug>/DECISIONS.md` — see Discovery below,
  which replaces the protocol's resume check (step 2).
- FRONTMATTER KEYS: `spec: S<n>` — later pipeline steps route on this key.
- `<topic>` in the log title: `S<n>: <feature name>`,
  e.g. `# DECISIONS — S02: Invoice manager`.
- COMPLETION MESSAGE: "Interview complete. DECISIONS.md is saved. Next
  step: run the to-spec skill in a fresh conversation."
## Discovery and folder creation (replaces protocol step 2)
1. Look in `specs/` at the project root. Read ONLY the frontmatter (the block
   between the `---` lines) of each `specs/S<nn>-*/DECISIONS.md`. If one has
   `status: IN PROGRESS`, read that whole file and RESUME: re-print it, then
   continue from the first area that is not done (if several are in progress,
   ask which). Otherwise, ask the user to describe the feature in a few
   sentences if they haven't already.
2. Create the feature folder `specs/S<nn>-<feature-slug>/`, where <nn> is one
   higher than the highest S-number already in `specs/`, zero-padded to two
   digits (S01 if none) — padding keeps the folders in build order under a
   plain alphabetical sort, which later steps rely on — and <feature-slug> is
   a short kebab-case name, e.g.
   `specs/S02-invoice-manager/`. Create DECISIONS.md inside it from the
   protocol's LOG TEMPLATE with the FRONTMATTER KEYS and `<topic>` bound
   above. Every later pipeline step reads and writes only
   this folder — except the project-wide `specs/GLOSSARY.md`, which you also
   read now (see GLOSSARY.md section below).
## GLOSSARY.md (project-wide shared language, at specs/GLOSSARY.md)
Terms outlive features: "Invoice" must mean the same thing in S1 and S4, so
the glossary belongs to the project, not to one spec. Format, one line per
term, annotated with the spec that defined it:
```markdown
# GLOSSARY
Invoice: a billing record the finance team sends to a client. (S1)
Batch: a group of invoices sent together in one email. (S1, updated S3)
```
- Read specs/GLOSSARY.md at the start of every interview (create it when the
  first term is defined).
- When the user's answer uses a project-specific noun that is not in the
  glossary, your next question may be: "What exactly is a <term>?" Record
  the user's one-sentence definition VERBATIM, annotated with this spec's
  S-number. Never define a term yourself — the glossary is the user's
  language, not yours.
- If the user's usage contradicts an existing entry, point at the entry and
  ask which wins. Update the definition only after they confirm, and extend
  the annotation: (S1, updated S3).
## REMINDER (read this last, follow it first)
Everything in PROTOCOL.md applies: one question per turn, append-only log,
save with a real tool call and verify, re-print the full DECISIONS.md
verbatim every turn. On top of that: the log's frontmatter carries
`spec: S<n>`, undefined project nouns go to the glossary in the user's
words (never into DECISIONS.md), and area 3 questions present YOUR code
findings for yes/no — never ask the user about code internals.
