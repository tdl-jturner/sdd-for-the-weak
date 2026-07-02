---
name: pipeline-feedback
description: Maintenance for the spec-pipeline skills. Turns the user's report of a misbehaving (or well-behaved) pipeline run into one minimal, user-approved skill edit, logged in FEEDBACK.md. Use when the user reports a pipeline skill misbehaved, gives feedback on a run, or asks to tune or improve the pipeline skills.
---

# SKILL: PIPELINE-FEEDBACK — Turn Run Feedback into Skill Fixes
You maintain the spec-pipeline skills in `.claude/skills/`. The user will
tell you what went wrong (or right) in a real run. Your job is to convert
each piece of feedback into the SMALLEST skill edit that would have prevented
the problem — with the user approving every change. You are editing
instructions that a weaker model must follow, so concrete beats abstract:
prefer an example, an exact format, or a verify-step over a broad rule.
## Protocol (one complaint at a time)
1. Ask the user for one problem: which skill, what happened, what they
   expected instead. If they gave a list, work it top to bottom, one per
   turn.
2. DIAGNOSE — Read the named SKILL.md. Find the rule that should have
   prevented the behavior and QUOTE it. If no such rule exists, say so — the
   fix is an addition, not a strengthening. If the behavior contradicts a
   rule that is already clear, suspect the rule is buried: consider moving
   its substance into the REMINDER block or adding a worked example, rather
   than adding words elsewhere.
3. PROPOSE — Exactly ONE minimal edit: a strengthened wording, a small
   example, or a new rule with its why. Show old text and new text. Explain
   in one sentence why this edit generalizes beyond this one run — a fix that
   only patches today's symptom is overfitting.
4. APPLY — Only after the user says yes. Make the edit with your file tools,
   then verify by reading the changed lines back.
5. LOG — Append one line to `.claude/skills/FEEDBACK.md` (create it if
   missing; it is append-only):
   `F<n> <date> <skill>: <symptom> -> <edit applied | rejected | conflicts with invariant>`
   The ledger is how future maintainers see what was tried and why.
6. Ask for the next complaint, or stop when the user is done.
## Hard rules
- ONE edit per approval. Never batch changes, never rewrite whole sections,
  never "tidy up while you're in there".
- Prefer strengthening an existing rule over adding a new one, and prefer a
  worked example over an abstract rule. Every added line costs the weak
  model's attention on every future run — skills that grow without pruning
  stop being followed.
- If a skill file exceeds about 150 lines, find something to REMOVE before
  adding: a duplicate, or a rule the model demonstrably follows without
  being told.
- NEVER remove or weaken these pipeline invariants — they are the design,
  not preferences:
  fresh conversation per step; state lives in files with status in
  frontmatter; DECISIONS log and issues folder are append-only (corrections
  supersede, never edit); UNRESOLVED instead of invented answers; saves are
  verified tool calls, never printouts; evidence required for DONE; one
  question per turn; one issue per conversation; issues bounded by their
  Files list; glossary only in the user's words.
- If a complaint conflicts with an invariant, say so plainly, explain what
  the invariant protects, and let the user decide explicitly. Record the
  outcome in the ledger either way — including "user chose to override".
- Praise is signal too: if the user says something worked well, log it and
  leave the skill alone. Do not fix what works.
## EXAMPLE (one full cycle)
User: "interview-me said it saved DECISIONS.md but never wrote the file."
You: Quote the save rule from interview-me. Diagnose: the rule says to save
but never demands proof, so a weak model narrates the save instead of doing
it. Propose: add to the save rule — "After EVERY save, verify: read the file
back and confirm your newest line is there. Never claim a save you have not
verified." Show old/new. User approves. Apply, verify the edit landed, log:
`F3 2026-07-02 interview-me: claimed save without writing -> added
read-back verification to the save rule`.
## REMINDER (read this last, follow it first)
One complaint, one quoted rule, one proposed edit, one approval, one ledger
line. Concrete beats abstract. Never touch the invariants without an
explicit user override. Small skills stay followed — prune before you add.
