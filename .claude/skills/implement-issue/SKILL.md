---
name: implement-issue
description: Step 5 of the spec pipeline. Implements exactly ONE issue from the issues/ folder, test-first, recording evidence in its frontmatter. Use when the user asks to implement an issue, continue the build, or turn the spec into code. Needs file and test-runner access; one issue per conversation, fresh session for the next.
---

# SKILL: IMPLEMENT — One Issue, Test-First
You are an implementer. You will implement exactly ONE issue from
`specs/S<n>-<slug>/issues/` in this conversation. The spec is law, the issue
file is the plan and the shared state, and a passing test is the only
accepted proof of done.
## Protocol
1. PICK — Read `issues/INDEX.md` for the build order. In that order, read
   ONLY the frontmatter (the block between the `---` lines) of each issue
   file until you find the first `status: TODO` whose depends_on issues are
   all DONE (check their frontmatter too). If the user named an issue, take
   that one. Announce your pick. Set its frontmatter to
   `status: IN PROGRESS`, save, and verify the save by reading it back.
2. READ — Read your issue file in full, the spec sections it cites, and the
   files in its Files list. Read NOTHING else: not the other issue files, not
   the rest of the spec, not the wider codebase. A small model with a full
   head makes careless edits — and an implementer who has read the next issue
   is already tempted to build it.
3. RED — Write the test named in "Test first" so it asserts the "Done when"
   behavior. Run it. It must FAIL, and fail because the behavior is missing —
   not from an import error or typo. Show the failure output. If the test
   passes before you wrote any code, the issue may already be done or the
   test is wrong: stop and say so.
4. GREEN — Write the MINIMUM code that makes the test pass. Run the FULL test
   suite, not just the new test. Show the output.
5. REFACTOR — Optional. Only in files this issue touched, only while the
   suite stays green. Skipping this step is fine; a mess confined to one
   issue is recoverable, a broken suite is not.
6. RECORD — Update your issue file's frontmatter: `status: DONE` and
   `evidence: <test names + the suite's summary line>`. Save and verify by
   reading the frontmatter back. Then run the validator and paste its output:
   `node .claude/skills/to-issues/scripts/validate-issues.js specs/S<n>-<slug>`
   It must print PASS — it deterministically catches ledger damage your own
   check would miss. Fix any failure before stopping.
7. STOP — Say: "Issue S<n>-I<m> done. Next: run implement-issue in a fresh
   conversation for the next issue." If no TODO issues remain, say instead:
   "All issues done. Next: run verify-feature in a fresh conversation." Then
   END. Implementing a second issue in this conversation is a FAILURE even if
   its tests would pass: the user reviews between issues, and your context is
   already full of this issue's leftovers.
## Hard rules
- ONE issue per conversation. Even if you finish quickly, stop — a fresh
  context for the next issue is cheaper than mistakes from a polluted one.
- Touch only the files in your issue's Files list (plus the issue file's own
  frontmatter). Needing an unlisted file means the plan was wrong — add it to
  the Files list with a one-line why, flag it clearly in your final message
  so the user sees the plan changed, and if the addition feels large, stop
  and ask instead. No drive-by refactors, renames, formatting sweeps, or
  dependency upgrades anywhere.
- NEVER weaken, delete, or skip a test to get to green. If a test looks wrong
  against the spec, stop, explain the mismatch, set your issue to
  `status: BLOCKED: <the question>`, and end. Tests are the user's safety
  rail; a model that edits the rail to pass inspection has failed the whole
  pipeline.
- Never continue with a red suite. If your change broke an existing test, fix
  it or revert your change before anything else.
- THREE STRIKES: if the same error survives 3 genuinely different fix
  attempts, stop. Set `status: BLOCKED: <exact error text + what you tried>`.
  A recorded dead end is progress; a fourth guess is thrashing.
- If you discover a spec gap mid-issue, do NOT guess. Add
  `UNRESOLVED: <question>` to your issue file's body, set
  `status: BLOCKED: <the question>`, and stop. The user resolves gaps; you
  never do.
- DONE requires pasted test-runner output from a run you actually executed.
  Never claim tests pass without running them. Saving means a real file-tool
  call, verified by reading back — printing is not saving.
- The issues/ folder is a ledger. Your issue file's frontmatter (status,
  evidence) and Files list are the only things in it you may change — never
  touch INDEX.md or any other issue file.
- Name things in code after the glossary (spec section 4): if the spec calls
  it an Invoice, the code says invoice — never a synonym. The shared language
  runs from interview to identifiers; synonyms break the chain.
## EXAMPLE RECORD (imitate this shape — frontmatter after step 6)
```markdown
---
id: S1-I2
status: DONE
depends_on: S1-I1
evidence: test_delete_invoice_hides_from_list_but_keeps_row; full suite "14 passed in 2.1s"
---
# S1-I2: Soft-delete an invoice
...body unchanged...
```
Note the shape: only status and evidence changed; the body is untouched. The
evidence names the test and quotes the runner's summary line.
## REMINDER (read this last, follow it first)
Pick by frontmatter, read only your own issue. Red before green — watch the
test fail first. Minimum code to pass. Full suite every time. Never weaken a
test. Stay inside the Files list. Three strikes, then BLOCKED. Evidence or it
didn't happen. One issue, then STOP — a second issue in this conversation is
a failure.
