# Spec Pipeline (Weak-Model Edition)
A repeatable process for turning a vague feature idea into working, verified
code, designed to be driven by inexpensive/weak LLMs: interview → spec →
critique → sequential issues → test-first implementation → conformance
review, one small step per conversation.

Inspired by [mattpocock/skills](https://github.com/mattpocock/skills), whose
alignment interviews, feedback-first development, and shared-glossary ideas
this pipeline borrows and adapts for much weaker models.
## The pipeline
```
Idea ──▶ 1 interview-me ──▶ DECISIONS.md ──▶ 2 to-spec ──▶ SPEC.md ──▶ 3 spec-critique ──▶ fixes
final SPEC.md ──▶ 4 to-issues ──▶ issues/*.md ──▶ 5 implement-issue (one per session) ──▶ 6 verify-feature
                                                                                            (conformance)
Anything misbehaves? ──▶ pipeline-feedback turns your complaint into a one-line skill fix.
```
| Step | Skill | What it does | Context rule |
|------|-------|--------------|--------------|
| 1 | `interview-me` | Checklist-driven interview (10 areas, incl. EXISTING CODE and TESTING). One question per turn, logged into DECISIONS.md, saved and verified every answer. | One conversation, resumable |
| 2 | `to-spec` | Converts DECISIONS.md into SPEC.md via a fixed template, then walks you through a review before handing off to critique. | Fresh conversation |
| 3 | `spec-critique` | Adversarial review of SPEC.md against DECISIONS.md, one narrow lens at a time. | Fresh conversation, one lens per run |
| 4 | `to-issues` | Decomposes SPEC.md into `issues/` — one file per issue (vertical slices with a bounding Files list) plus INDEX.md, checked by a validator script. | Fresh conversation |
| 5 | `implement-issue` | Implements ONE issue test-first (red-green-refactor), records evidence in the issue's frontmatter, validator must pass. | Fresh conversation **per issue** |
| 6 | `verify-feature` | Fresh-eyes conformance review: re-runs the suite, reads test bodies, traces code against every acceptance criterion. Changes nothing. | Fresh conversation |
| — | `unblock` | Lists every BLOCKED issue and UNRESOLVED question, then resolves them one at a time with you, routing each answer into the right file. | Any time |
| — | `diagnose-bug` | Post-ship debugging: reproduces the bug, classifies it (code bug / works-as-specified / spec gap), records a bug issue for implement-issue. Never fixes. | Fresh conversation |
| — | `pipeline-feedback` | Maintenance loop: one complaint → one quoted rule → one approved minimal edit → append-only FEEDBACK.md ledger. | Any time |
## The state files
Each feature gets a numbered folder; one glossary is shared project-wide.
```
your-project/
└── specs/
    ├── GLOSSARY.md                  (project-wide shared language)
    └── S1-<feature-slug>/
        ├── DECISIONS.md             (append-only decision log)
        ├── SPEC.md                  (derived, disposable)
        └── issues/
            ├── INDEX.md             (build order only)
            ├── S01-I01-<slug>.md      (one file per issue)
            └── S01-I02-<slug>.md
```
Every file carries YAML frontmatter with its status (`status: IN PROGRESS`,
`status: DONE`, …) so a skill can find the right file by reading only the
first few lines. Issue IDs (`S01-I02` = spec 1, issue 2) are permanent and
globally unique. One file per issue is deliberate: the implementer reads only
its own issue, so the rest of the plan never tempts it to keep going.
## How to run it
Install once: copy the skill folders into your agent's skills directory
(`.claude/skills/` in the project, or `~/.claude/skills/` globally). The
files above are the state that travels between steps; conversations are not.
1. Invoke `/interview-me` with your feature idea. One question per turn; it
   saves DECISIONS.md after every answer and verifies the save (printing is
   not saving). It inspects existing code for the EXISTING CODE area, and
   grows `specs/GLOSSARY.md` from terms you define.
2. Fresh session: `/to-spec`. Reads DECISIONS.md, writes SPEC.md, then asks
   you to review before pointing you at critique. Corrections that are
   decisions get logged, never silently absorbed.
3. Fresh session: `/spec-critique` with ONE lens (recommended order: TRACE,
   HOLES, CLASH, TEST, VAGUE). Repeat per lens. Resolve findings, re-run
   step 2.
4. Fresh session: `/to-issues`. Writes `issues/` and INDEX.md, then must show
   you a passing validator run:
   `node .claude/skills/to-issues/scripts/validate-issues.js specs/S01-<slug>`
5. For EACH issue, fresh session: `/implement-issue`. Picks the next TODO by
   frontmatter, implements it test-first inside its Files list, records
   evidence, validator must pass. When none remain it points you at step 6;
   when work is stuck it lists what's BLOCKED and points you at `/unblock`,
   which walks you through resolving every blocker and open question one at
   a time (the validator also flags blocked issues in every run).
6. Fresh session: `/verify-feature`. Re-runs everything itself and traces
   code against every acceptance criterion. Fixes become new decisions and
   new issues — never edits made during review.
When the built feature misbehaves later, run `/diagnose-bug`: it reproduces
the problem, traces it against the spec, and classifies it — a code bug
becomes a new bug issue (fixed via `/implement-issue`, whose failing test
becomes the regression test); works-as-specified or a spec gap routes back
to `/interview-me` for a decision. It never fixes anything itself.
When any pipeline step misbehaves, run `/pipeline-feedback` with what
happened — it finds the rule that failed, proposes one minimal edit, and
applies it only with your approval, logging to `.claude/skills/FEEDBACK.md`.
## Multiple features and re-spec cycles
- **DECISIONS.md is append-only, forever.** New requirements mid-build?
  Resume `/interview-me` — new decisions get new D-numbers, corrections
  supersede old lines.
- **SPEC.md is disposable.** Derived entirely from DECISIONS.md; re-running
  `/to-spec` loses nothing.
- **The issues/ folder is an append-only ledger.** Frontmatter statuses and
  evidence are the record of work done. Re-running `/to-issues` after a spec
  change adds new issue files (and marks obsoleted TODO ones DROPPED); it
  never renumbers, deletes, or resets existing files.
- **GLOSSARY.md is project-wide.** One shared language, defined only in your
  words; specs copy the entries they use, implementation names code after
  them.
## Rules that make this work on weak models (don't break these)
- **Fresh context between steps.** The spec writer never sees the interview;
  the critic never sees the session that wrote the spec; the verifier never
  sees the sessions that wrote the code. Weak models are bad critics of work
  sitting in their own context.
- **State lives in the files, not the conversation.** If a session dies,
  start fresh — the frontmatter tells the next session where things stand.
- **Saving is a verified tool call.** Every skill must write with a real
  file tool and read the result back before claiming success. Weak models
  will otherwise narrate saves that never happened.
- **UNRESOLVED is sacred.** Gaps are marked, never filled with invented
  defaults. You resolve them; the model never does.
- **You are the judgment layer.** The model administers checklists; deciding
  what the product does is your job. Read every entry it logs.
- **One issue per conversation.** A second issue in the same session is
  defined as a failure, even if its tests pass.
- **Tests are the rail, evidence is the proof.** DONE requires pasted
  test-runner output; tests are never weakened to get to green; the
  validator script checks the ledger deterministically.
## When the model misbehaves
- Asks multiple questions at once → "One question at a time. Re-read your instructions."
- Claims it saved a file it never wrote → "You did not write the file. Save
  it with your file tool and verify by reading it back."
- Stops re-printing DECISIONS.md → "Print the full DECISIONS.md now."
- Invents an answer you never gave → delete the line, "I never decided that. Mark it UNRESOLVED."
- Writes a glossary definition you never gave → replace it, "Only I define terms. Ask me."
- Re-words or renumbers old decision lines → restore them, "The log is
  append-only. Corrections are new superseding lines, never edits."
- Goes in circles → fresh conversation with the skill + saved state. Fresh
  context beats long repair.
- Weakens or deletes a test to get to green → revert it, "Restore the test.
  If you think it's wrong, mark the issue BLOCKED and explain."
- Claims DONE without test output → "Show the full test run." No output, no DONE.
- Keeps retrying the same failing fix → "Three strikes: mark the issue
  BLOCKED with the exact error and stop." Then fresh session.
- Starts the next issue in the same session → "Stop. One issue per
  conversation. Mark where you are and end."
- Touches issue files it doesn't own, or rewrites them on a re-run → restore
  from git, "The issues folder is a ledger. Existing files are immutable."
- Any of the above keeps happening → run `/pipeline-feedback` and turn the
  complaint into a permanent skill fix.
