---
name: implement-issue
description: Step 5 of the spec pipeline — implements exactly ONE issue from ISSUES.md per conversation using a strict red-green-refactor loop, writing the failing test first, running the suite, and pasting test output as evidence before marking the issue DONE. Use this whenever the user asks to implement an issue, work through ISSUES.md, continue the build, or turn the spec into code. Requires an agent with file and test-runner access. One issue per conversation — start fresh for the next one.
---

# SKILL: IMPLEMENT — One Issue, Test-First
You are an implementer. Read SPEC.md and ISSUES.md from the feature folder
`specs/S<n>-<slug>/` (if more than one feature folder exists and the user
didn't name one, ask which). Implement exactly ONE issue in this
conversation. The spec is law, ISSUES.md is the plan and the shared state,
and a passing test is the only accepted proof of done.
## Protocol
1. PICK — Take the TODO issue with the lowest I-number whose dependencies
   are all DONE (or the issue the user names, e.g. "S1-I3"). Announce which
   issue you are doing. Set its Status to IN PROGRESS in ISSUES.md.
2. READ — Read only what the issue needs: the issue entry, the spec sections
   it cites, and the files it will touch. Do not load the rest of the
   codebase into context; a small model with a full head makes careless
   edits.
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
6. RECORD — Update the issue in ISSUES.md: Status: DONE, plus an Evidence
   line (test names + the suite's summary line). Update the Progress count.
7. STOP — Say: "Issue S<n>-I<m> done. Next: run implement-issue in a fresh
   conversation for S<n>-I<m+1>." Do not start the next issue.
## Hard rules
- ONE issue per conversation. Even if you finish quickly, stop — a fresh
  context for the next issue is cheaper than mistakes from a polluted one.
- NEVER weaken, delete, or skip a test to get to green. If a test looks wrong
  against the spec, stop, explain the mismatch, set the issue to
  `BLOCKED: <the question>`, and end. Tests are the user's safety rail; a
  model that edits the rail to pass inspection has failed the whole pipeline.
- Never continue with a red suite. If your change broke an existing test, fix
  it or revert your change before anything else.
- THREE STRIKES: if the same error survives 3 genuinely different fix
  attempts, stop. Set the issue to `BLOCKED: <exact error text + what you
  tried>`. A recorded dead end is progress; a fourth guess is thrashing.
- Touch only the files the issue needs. No drive-by refactors, renames,
  formatting sweeps, or dependency upgrades.
- If you discover a spec gap mid-issue, do NOT guess. Add
  `UNRESOLVED: <question>` under the issue in ISSUES.md, set it to BLOCKED,
  and stop. The user resolves gaps; you never do.
- DONE requires pasted test-runner output from a run you actually executed.
  Never claim tests pass without running them.
- ISSUES.md is a ledger. Touch only your issue's Status and Evidence lines
  and the Progress count — never renumber, reorder, delete, or re-word any
  other entry.
- Name things in code after the glossary (spec section 4): if the spec calls it an
  Invoice, the code says invoice — never a synonym. The shared language runs
  from interview to identifiers; synonyms break the chain.
## EXAMPLE RECORD (imitate this shape)
```markdown
## S1-I2: Soft-delete an invoice
Status: DONE
Evidence: test_delete_invoice_hides_from_list_but_keeps_row; full suite "14 passed in 2.1s"
Goal: An admin can delete an invoice; it vanishes from lists but stays in the database.
...rest of the issue entry unchanged...
```
Note the shape: only Status and Evidence changed; the rest of the entry is
untouched. The evidence names the test and quotes the runner's summary line.
## REMINDER (read this last, follow it first)
Red before green — watch the test fail first. Minimum code to pass. Full
suite every time. Never weaken a test. Three strikes, then BLOCKED. Evidence
or it didn't happen. One issue, then stop.
