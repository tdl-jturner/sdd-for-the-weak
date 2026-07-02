# Spec Pipeline (Weak-Model Edition)
A repeatable process for turning a vague feature idea into working code,
designed to be driven by inexpensive/weak LLMs: interview → spec → critique →
sequential issues → test-first implementation, one small step per conversation.
## The pipeline
```
Idea ──▶ 1-GRILL ──▶ DECISIONS.md ──▶ 2-WRITE-SPEC ──▶ SPEC.md ──▶ 3-CRITIQUE ──▶ fixes ──▶ final SPEC.md
          (interview)  (state file)     (synthesis)                (fresh context)
final SPEC.md ──▶ 4-ISSUES ──▶ ISSUES.md ──▶ 5-IMPLEMENT ──▶ working code
                   (planning)   (tracker)     (one issue per conversation, test-first)
```
| Step | Skill | What it does | Context rule |
|------|-------|--------------|--------------|
| 1 | `interview-me/SKILL.md` | Checklist-driven interview. One question per turn. Every answer is logged immediately into DECISIONS.md. | One conversation |
| 2 | `to-spec/SKILL.md` | Converts DECISIONS.md into SPEC.md using a fixed template. Pure formatting — no memory of the interview needed. | Fresh conversation |
| 3 | `spec-critique/SKILL.md` | Adversarial review of SPEC.md against DECISIONS.md, one narrow lens at a time. | Fresh conversation, run once per lens |
| 4 | `to-issues/SKILL.md` | Decomposes SPEC.md into ISSUES.md: small, sequential, independently testable issues (each a vertical slice). | Fresh conversation |
| 5 | `implement-issue/SKILL.md` | Implements one issue, test-first (red-green-refactor), and records evidence in ISSUES.md. | Fresh conversation **per issue** |
## How to run it
Install once: copy the five skill folders into your agent's skills directory
(e.g. `~/.claude/skills/`). Each feature gets a numbered folder at your
project root — `specs/S1-<feature-slug>/` — holding its DECISIONS.md,
SPEC.md, and ISSUES.md, plus one project-wide `specs/GLOSSARY.md` shared by
all features. Those files are the state that travels between steps; the
conversations are not.
1. In your project, invoke `/interview-me` with your feature idea. Answer one
   question per turn. It saves DECISIONS.md to disk after every answer and
   re-prints it so you can review each entry as it lands. It also grows
   `specs/GLOSSARY.md`: when you use a project term it doesn't know, it asks
   you to define it and records your words verbatim.
2. Start a **fresh** session. Invoke `/to-spec`. It reads DECISIONS.md and
   writes SPEC.md.
3. Start a **fresh** session. Invoke `/spec-critique`, naming ONE lens
   (recommended order: TRACE, HOLES, CLASH, TEST, VAGUE). It reads SPEC.md
   and DECISIONS.md. Repeat per lens, fresh session each time. Resolve the
   findings in DECISIONS.md, then re-run step 2.
4. Start a **fresh** session. Invoke `/to-issues`. It reads the final
   SPEC.md and writes ISSUES.md.
5. For EACH issue, start a **fresh** session and invoke `/implement-issue`.
   It picks the next TODO issue, implements it test-first, and records
   evidence in ISSUES.md. Repeat until every issue is DONE.
Fallback: each SKILL.md body (everything below the frontmatter) also works as
a plain pasted prompt in any chat UI — steps 1–4 need no tools at all; you
just save the produced files yourself.
## Multiple features and re-spec cycles
Each interview creates the next numbered feature folder — `specs/S1-<slug>/`,
`specs/S2-<slug>/`, … — and issue IDs carry that number (`S1-I2` = spec 1,
issue 2), so every issue is unique across the whole project. The three
artifacts have deliberately different lifecycles:
- **DECISIONS.md is append-only, forever.** New requirements mid-build?
  Resume `/interview-me` on the same feature — new decisions get new
  D-numbers, corrections supersede old lines.
- **SPEC.md is disposable.** It is derived entirely from DECISIONS.md, so
  re-running `/to-spec` and overwriting it never loses anything.
- **ISSUES.md is an append-only ledger.** Statuses and Evidence lines are the
  only record of work already done. Re-running `/to-issues` after a spec
  change appends new issues (and marks obsoleted TODO ones DROPPED); it never
  renumbers, deletes, or resets existing entries.
- **GLOSSARY.md is project-wide.** One shared language, grown by every
  interview, defined only in your words. Specs copy the entries they use;
  implementation names code after them. Definitions change only when you
  confirm the change.
## Rules that make this work on weak models (don't break these)
- **Fresh context between steps.** The spec writer must never see the interview
  conversation, and the critic must never see the conversation that wrote the
  spec. Weak models are bad critics of work sitting in their own context.
- **State lives in the files, not the conversation.** DECISIONS.md, SPEC.md,
  and ISSUES.md in the feature folder (`specs/S<n>-<slug>/`) are the only
  state that matters. If a session dies mid-interview, start a fresh one and
  invoke `/interview-me` again — it resumes from the DECISIONS.md on disk.
- **UNRESOLVED is sacred.** Models are forbidden from inventing answers. Any
  gap must be marked `UNRESOLVED: <question>`. You resolve them; the model
  never does. A spec with visible UNRESOLVED markers is honest; a spec with
  silent invented defaults is a trap.
- **You are the judgment layer.** The model administers checklists and formats
  text. Deciding what the product does is your job. Read every DECISIONS.md
  entry the model writes — it drafts, you correct.
- **One issue per conversation.** During implementation, each issue gets a
  fresh session. Weak models degrade fast as context grows; ISSUES.md carries
  the state between sessions so no single session needs to remember anything.
- **Tests are the rail, evidence is the proof.** An issue is DONE only when
  the model pastes real test-runner output. A model may never weaken or
  delete a test to get to green — that failure mode defeats the entire
  pipeline.
## When the model misbehaves
- Asks multiple questions at once → reply: "One question at a time. Re-read your instructions."
- Stops re-printing DECISIONS.md → reply: "Print the full DECISIONS.md now."
- Invents an answer you never gave → delete that line from your saved copy,
  tell it: "I never decided that. Mark it UNRESOLVED."
- Writes a glossary definition you never gave → replace it with your own
  wording, tell it: "Only I define terms. Ask me."
- Re-words or renumbers old decision lines → restore them from your saved
  copy, tell it: "The log is append-only. Corrections are new superseding
  lines, never edits."
- Goes in circles → start a fresh conversation with the skill file + your saved
  state. Fresh context beats long repair.
- Weakens or deletes a test to get to green → revert it, tell it: "Restore the
  test. If you think it's wrong, mark the issue BLOCKED and explain."
- Claims an issue is done without showing test output → reply: "Show the full
  test run." No output, no DONE.
- Keeps retrying the same failing fix → invoke the three-strikes rule: "Mark
  the issue BLOCKED with the exact error and stop." Then start a fresh session.
- Rewrites or renumbers existing issues on a to-issues re-run → restore them
  (from git or your copy), tell it: "ISSUES.md is a ledger. Existing issues
  are immutable — append new ones."
