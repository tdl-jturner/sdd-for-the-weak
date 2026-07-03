---
name: unblock
description: Finds everything waiting on the user in a feature folder — BLOCKED issues and UNRESOLVED questions — and resolves them one at a time, routing each answer into the right file. Use when the user asks what is blocked or open, wants to unblock work or resolve questions, or when implement-issue reports nothing eligible to pick.
---

# SKILL: UNBLOCK — Find and Clear Everything Waiting on the User
You are a dispatcher. Blockers accumulate in the pipeline's files — issues
marked BLOCKED, questions marked UNRESOLVED — and the user has no reason to
remember them. Your job: surface every blocker in one list, then resolve
them one at a time, writing each resolution into the right file. The user
supplies every answer; you only record and route.
## Protocol
1. SCAN — In the feature folder `specs/S<n>-<slug>/` (ask which, if several),
   collect blockers from:
   - every issue file whose frontmatter status starts with BLOCKED
     (read only frontmatter to find them),
   - the Unresolved section of DECISIONS.md,
   - SPEC.md section 13 (Open Questions).
   The same question often appears in several places — that is ONE blocker.
   DECISIONS.md is the source; SPEC is derived from it and gets
   regenerated later. Print a numbered list: `B1 <where> — <question or
   error>`. If the list is empty, say so and point at the next pipeline step
   (implement-issue if TODO issues remain, verify-feature if all DONE).
2. RESOLVE — Take ONE blocker per turn, starting at B1. Ask the user for
   their answer. You may add one labeled suggestion:
   `Suggestion: <one concrete answer> — yes/no, or your own answer?`
   Never record anything they have not confirmed.
3. ROUTE the confirmed answer:
   - It answers an open question → append `D<n>: <answer, their words>` to
     the DECISIONS.md Decision Log (next number, append-only), and change
     that `UNRESOLVED: <q>` line to `RESOLVED (D<n>): <q>` — visible
     history, no deletions.
   - It clears a BLOCKED issue → set that issue's frontmatter back to
     `status: TODO` and append one body line: `Unblocked: <resolution> (D<n>
     if one was recorded)`. If the user instead abandons the issue, set
     `status: DROPPED: <their reason>`.
   - A three-strikes technical block (error text, not a question) → record
     the user's guidance ("try X instead") as the Unblocked line; back to
     TODO. The next implement-issue session reads it fresh.
   Save each change with a real tool call and verify by reading it back.
4. REPEAT until the list is done, then run the validator and paste output:
   `node .claude/skills/to-issues/scripts/validate-issues.js specs/S<n>-<slug>`
5. HAND OFF — If any resolution added or superseded a decision that the spec
   text cares about, say: "Decisions changed — re-run to-spec, then
   spec-critique/to-issues as needed, in fresh conversations." Otherwise
   say: "All clear — next: implement-issue in a fresh conversation."
## Hard rules
- You resolve NOTHING yourself. Every answer comes from the user; an
  unanswered blocker simply stays on the list. Skipping is allowed —
  record `(skipped by user <date>)` next to it and move on.
- ONE blocker per turn. A wall of questions gets a wall of half-answers.
- Append-only discipline holds: new decisions get new D-numbers;
  UNRESOLVED lines become RESOLVED lines, never deleted; issue files keep
  their IDs; only frontmatter status and an appended Unblocked line change.
- Touch nothing that isn't a blocker: no code, no tests, no DONE issues, no
  spec edits (the spec regenerates via to-spec).
## EXAMPLE (one blocker, end to end)
Scan finds: `B1 issue S01-I04 — BLOCKED: how long are soft-deleted invoices
retained? (also UNRESOLVED in DECISIONS.md and SPEC section 13)`.
You ask: "How long should soft-deleted invoices be retained?
Suggestion: 90 days — yes/no, or your own answer?" User: "Forever, actually."
You: append `D23: Soft-deleted invoices are retained forever.` to the
Decision Log; change the UNRESOLVED line to
`RESOLVED (D23): How long are soft-deleted invoices retained?`; set S01-I04 to
`status: TODO` with body line `Unblocked: retention is forever (D23)`; save,
verify, validator PASS. Because D23 changes spec content, the hand-off is:
"re-run to-spec in a fresh conversation."
## REMINDER (read this last, follow it first)
One list, then one blocker per turn. The user answers; you record and route.
New decisions are appended, UNRESOLVED becomes RESOLVED, BLOCKED becomes
TODO or DROPPED — nothing is deleted. Validator PASS, then hand off.
