---
name: interview-me
description: Interviews the user one question at a time against a checklist file they provide, recording answers in an append-only decision log. Use when the user supplies or names a checklist to interview against, wants a decision log for anything that is not a feature spec (a plan, a purchase, a migration, a design), or wants to resume such a log. For feature specs, use spec-design instead.
---

# SKILL: INTERVIEW ME (generic binding)
Read `PROTOCOL.md` in this skill's directory NOW and follow it exactly.
This file only supplies the bindings the protocol needs.
## Bindings
- CHECKLIST: the file the user named or provided. If they invoked this
  skill without naming one, your first question is which file to use —
  never invent a checklist. If the file doesn't match the CHECKLIST FILE
  FORMAT in the protocol, say what's wrong and stop.
- LOG: `decisions/<topic-slug>.md` at the project root, where <topic-slug>
  is a short kebab-case name for this interview's topic. If the checklist
  frontmatter has `output: <dir>`, use that directory instead. Either way,
  state the full path as a labeled suggestion in your first turn so the
  user can redirect before the file exists.
- RESUME: before starting fresh, read ONLY the frontmatter of each file in
  the LOG directory. If one has `status: IN PROGRESS` and its `checklist:`
  matches, offer to resume it (if several match, ask which).
- FRONTMATTER KEYS: `checklist: <path to CHECKLIST>` — this is the key
  RESUME matches on.
- COMPLETION MESSAGE: "Interview complete. <LOG path> is saved." If the
  checklist frontmatter has `next_step:`, append that sentence.
## Notes
- One checklist, many interviews: the checklist is a reusable template;
  each run gets its own log file. Never write into the checklist.
- The spec pipeline does not use this skill directly — spec-design binds
  the same PROTOCOL.md to `specs/` with its own frontmatter keys and
  glossary rules.
