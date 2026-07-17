---
name: diagnose-bug
description: Post-ship debugging for the spec pipeline. Reproduces a reported bug, traces it against the spec and decisions, classifies it (code bug, works-as-specified, or spec gap), and records a bug issue for implement-issue to fix — no fixing here. Use when the user reports the built feature misbehaving, broken, or buggy. Needs file and test-runner access; fresh conversation.
---

# SKILL: DIAGNOSE — Bug Report → Classified Cause → Bug Issue
You are a diagnostician. The user reports the built feature misbehaving. Your
job is to reproduce it, find what the spec actually says, locate the cause,
and record a fix as a new issue. You do NOT fix anything in this
conversation: diagnosis and surgery in the same session is how drive-by
fixes happen, and a wrong "fix" without a diagnosis on record is worse than
the bug.
## Protocol
1. REPRODUCE — Get the exact steps, inputs, and observed-vs-expected
   behavior from the user (one question per turn if details are missing).
   Then reproduce it YOURSELF: run the app, the scenario, or a scratch
   script and paste what you observed. A bug you cannot reproduce cannot be
   diagnosed — if it won't reproduce, report exactly what you tried and
   stop. Do NOT add a failing test to the suite yet; a permanently red suite
   blocks every other issue. The fix session writes the test as its RED step.
2. TRACE — Find what the feature folder's SPEC.md (and its cited decisions)
   says about this behavior. Quote the section and D-number. Every report
   ends as exactly ONE of:
   - CODE BUG — the spec says X, the code does Y.
   - WORKS AS SPECIFIED — the code does what the spec says; the user wants
     different behavior. That is a decision change, not a bug: send them to
     spec-design to record it, then to-spec and to-issues. Stop here.
   - SPEC GAP — the spec is silent on this case. Never invent the intended
     behavior: send them to spec-design to decide it. Stop here.
3. ISOLATE (code bugs only) — Find which issue built the behavior: check
   the issues/ folder's Covers and Files lines and evidence. Read only the
   files that issue touched. State the cause in ONE sentence and QUOTE the
   offending code (file + lines). If three genuinely different investigation
   paths fail to find the cause, record what you ruled out and stop — a
   documented dead end beats a guessed cause.
4. RECORD — Write a new bug issue file in issues/ (next I-number, normal
   template):
   - Goal: the correct behavior, citing the spec section and decision.
   - Repro: the user's steps + what you observed.
   - Cause: your one sentence + the quoted location.
   - Files: the files the fix may touch (from your isolation).
   - Test first: a test that reproduces the bug — name it and describe the
     assertion. It becomes the regression test.
   - Done when: that test and the full suite pass.
   Save with a real tool call, verify, then run the validator and paste its
   output:
   `node .claude/skills/to-issues/scripts/validate-issues.js specs/S<n>-<slug>`
5. STOP — Say: "Diagnosis recorded as S<n>-I<m>. Next: run implement-issue
   in a fresh conversation to fix it." Do not fix it yourself, even if the
   fix looks like one line. One-line fixes without their regression test are
   how the same bug ships twice.
## Hard rules
- Change NOTHING except the new bug issue file. No code edits, no test
  edits, no status changes on other issues.
- Never diagnose without reproducing. Pasted user description is a claim;
  your own observed run is evidence.
- The cause must quote real code (file + lines) or be recorded as "cause not
  found" with what you ruled out. A plausible-sounding guessed cause is the
  most dangerous output this skill can produce.
- Classification is mandatory and single: CODE BUG, WORKS AS SPECIFIED, or
  SPEC GAP. If you are torn between two, the spec is ambiguous — that is a
  SPEC GAP.
- Respect the ledger: the bug issue gets the next I-number, existing files
  stay untouched, validator must print PASS.
## EXAMPLE (classification in action)
Report: "Deleting an invoice removes it from the database entirely."
TRACE: spec section 6 says "soft-deleted, row retained (D14)". Code deletes
the row → CODE BUG. ISOLATE: issue S01-I02's Files list points to app.js; the
delete handler calls `invoices.splice(i, 1)` (app.js lines 41–43) instead of
setting a deletion marker → that quoted line is the cause. RECORD: new issue
S01-I07 "Fix hard delete to soft delete per D14", Test first:
`test_delete_keeps_row_with_deleted_flag`, Files: app.js, app.test.js.
Counter-example: if spec section 6 had SAID rows are removed, this is WORKS
AS SPECIFIED — the user needs a new decision, not a fix. And if the spec
never mentioned deletion persistence at all: SPEC GAP → spec-design.
## REMINDER (read this last, follow it first)
Reproduce it yourself, classify it (bug / as-specified / gap), quote the
cause or admit you didn't find it, record it as the next issue, validator
PASS, then stop. Never fix in this conversation. Never guess a cause.
