---
name: spec-design
description: Steps 1–2 of the spec pipeline. Interviews the user one question at a time into a DECISIONS.md decision log, then writes SPEC.md from that log with every gap marked UNRESOLVED. Use when the user has a feature idea to flesh out, asks to be interviewed or grilled about requirements, wants to write or rewrite the spec from a decision log, or wants to resume either phase.
---

# SKILL: SPEC DESIGN — Interview → Decision Log → Spec
Two engines, one artifact: `template.md` in this directory is BOTH the
interview checklist (its `?` items and interview-only block) and the SPEC
template (everything else). Read it with whichever engine you are running.
## Mode routing (do this first)
Read ONLY the frontmatter of each `specs/S<nn>-*/DECISIONS.md`:
- One has `status: IN PROGRESS` → INTERVIEW mode, resuming it (if
  several, ask which).
- The user wants the spec written and a log has `status: COMPLETE` →
  POPULATE mode on that log (if several qualify and none named, ask).
- Otherwise → INTERVIEW mode for a new feature.
When the interview completes, you may continue straight into POPULATE
mode in this same conversation if the user says to.
## INTERVIEW mode
Read `.claude/skills/interview-me/PROTOCOL.md` NOW and follow it exactly,
with these bindings:
- CHECKLIST: `template.md` here — an interview template; its sections
  with `?` items are your areas.
- LOG: `specs/S<nn>-<feature-slug>/DECISIONS.md`. For a new feature,
  create `specs/S<nn>-<feature-slug>/`, where <nn> is one higher than the
  highest S-number already in `specs/`, zero-padded to two digits (S01 if
  none) — padding keeps the folders in build order under a plain
  alphabetical sort, which later steps rely on — and <feature-slug> is a
  short kebab-case name, e.g. `specs/S02-invoice-manager/`. Every later
  pipeline step reads and writes only this folder, plus the project-wide
  `specs/GLOSSARY.md`.
- FRONTMATTER KEYS: `spec: S<n>` — later pipeline steps route on this
  key. `<topic>` in the log title: `S<n>: <feature name>`.
- COMPLETION MESSAGE: "Interview complete. DECISIONS.md is saved. Say
  'write the spec' to continue here, or run spec-design in a fresh
  conversation."
- Validator command (for the protocol's per-save gate) — run EXACTLY
  this, verbatim, in your Bash tool, substituting only the folder name:
  `python .claude/skills/interview-me/scripts/validate.py specs/S<nn>-<slug>/DECISIONS.md .claude/skills/spec-design/template.md`
Also read the project-wide `specs/GLOSSARY.md` at the start (see below).
## GLOSSARY.md (project-wide shared language, at specs/GLOSSARY.md)
Terms outlive features: "Invoice" must mean the same thing in S1 and S4,
so the glossary belongs to the project, not to one spec. Format, one line
per term, annotated with the spec that defined it:
```markdown
# GLOSSARY
Invoice: a billing record the finance team sends to a client. (S1)
Batch: a group of invoices sent together in one email. (S1, updated S3)
```
- Create it when the first term is defined.
- When the user's answer uses a project-specific noun that is not in the
  glossary, your next question may be: "What exactly is a <term>?" Record
  the user's one-sentence definition VERBATIM, annotated with this spec's
  S-number. Never define a term yourself — the glossary is the user's
  language, not yours.
- If the user's usage contradicts an existing entry, point at the entry
  and ask which wins. Update the definition only after they confirm, and
  extend the annotation: (S1, updated S3).
## POPULATE mode
Read `.claude/skills/populate-template/PROTOCOL.md` NOW and follow it
exactly, with these bindings:
- SOURCE: the chosen DECISIONS.md. Auxiliary source: `specs/GLOSSARY.md`
  (the template's section 4 rule says how it is used).
- TEMPLATE: `template.md` here. Its catch-all section is 12 (Other
  decisions); its open-questions section is 13 (Open Questions).
- OUTPUT: SPEC.md next to DECISIONS.md.
- REVIEW MESSAGE: "SPEC.md is saved and verified. Please review it now —
  especially section 13 (Open Questions). Tell me any corrections, or say
  'done'. When you are satisfied, run spec-critique in a fresh
  conversation (recommended lens order: TRACE, HOLES, CLASH, TEST;
  VAGUE is optional polish)."
Same-session rule: even when the interview happened in this very
conversation, first RE-READ DECISIONS.md from disk and build the spec
ONLY from what that read-back contains. If you remember interview content
that is not in the log, that is a missing decision: stop and ask the user
to log it as a new D-line before it may appear in the spec — never write
it into the spec from memory.
Validator command (for the protocol's validator gate) — run EXACTLY
this, verbatim, in your Bash tool, substituting only the folder name:
`python .claude/skills/populate-template/scripts/validate.py specs/S<nn>-<slug>/DECISIONS.md specs/S<nn>-<slug>/SPEC.md .claude/skills/spec-design/template.md`
## REMINDER (read this last, follow it first)
Route by frontmatter first. In INTERVIEW mode everything in the interview
protocol applies: one question per turn, append-only log, save and
verify, re-print in full; undefined project nouns go to the glossary in
the user's words. In POPULATE mode everything in the populate protocol
applies: reorganize, never invent; obey every `!` rule; gaps become
UNRESOLVED; the spec derives from the re-read file, never from
conversation memory; the validator must PASS before the user is asked
to review.
