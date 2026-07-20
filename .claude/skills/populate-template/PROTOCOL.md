# POPULATE TEMPLATE PROTOCOL (shared engine)
This is the reusable reformatting engine: it reorganizes a completed
decision log (the kind interview-me and spec-design produce) into a target
template, inventing nothing. It always runs through a binding — the
populate-template skill (generic) or a wrapper like spec-design (spec
pipeline) — which supplies four things:
- SOURCE: the decision log to draw from, plus any auxiliary sources the
  binding names.
- TEMPLATE: the file whose shape the output copies (requirements below).
- OUTPUT: the path where the populated document is saved.
- REVIEW MESSAGE: what to print after saving, inviting the user's review.
This file defines no defaults for these. If a required binding is missing,
stop and say which one — never improvise it. A binding may also add hard
rules and self-checks of its own; they bind exactly like the ones here.
## Role
You are a technical writer. Your only job is to reorganize the SOURCE's
contents into the TEMPLATE. This is a formatting task, not a design task.
## Protocol
1. Read SOURCE and TEMPLATE in full. Build OUTPUT as a copy of TEMPLATE,
   handling each line by its sigil (an indented line continues the sigil
   line above it):
   - `! <rule>` — a binding instruction for filling that section. Obey
     it; never render it into OUTPUT.
   - `? <coverage item>` — an interview anchor; never render it. Content
     answering it lands here under the hard rules; if the log never
     answered it, write `UNRESOLVED: <the exact question that needs
     answering>` in its place.
   - `<...>` — a substitution slot: replace it with the value it names.
   - A section heading marked "(interview only)" — skip that whole
     block; nothing in it renders (its decisions still land wherever
     they fit).
   - Anything else is literal structure: copy it as-is.
2. Run the FINAL SELF-CHECK silently.
3. SAVE the result to OUTPUT — saving means invoking your file-writing
   tool, not printing text. Then VERIFY: read the file back and confirm it
   starts with the template's frontmatter. Never claim it is saved without
   verifying. (No file tools? Say so plainly and tell the user to copy the
   printed document themselves.)
   Then run the validator that ships with this skill — in your Bash tool,
   substituting only the three paths — and paste its output:
   `python .claude/skills/populate-template/scripts/validate.py <SOURCE> <OUTPUT> <TEMPLATE>`
   Every check must PASS before step 4. A FAIL means a hard rule was
   broken: fix OUTPUT, re-save, re-run the validator. (A binding may spell
   out the exact substituted command; use it verbatim.)
4. Print the full document, then print the REVIEW MESSAGE and wait.
5. Handle the user's review feedback, one item at a time:
   - Mechanical fix (typo, wrong section, formatting): fix it, re-save,
     verify, show the changed lines.
   - A new or changed decision: append it to SOURCE as the next D-number,
     in the user's words (superseding an old D-line if it contradicts
     one), then update the affected OUTPUT sections, re-save both, verify,
     show the changed lines. Never absorb a decision into the output
     without logging it — an unlogged decision is invisible to everything
     else that reads the log.
   When they say done, repeat the REVIEW MESSAGE.
## Hard rules
- Every statement in OUTPUT MUST come from a decision in the log. When
  practical, cite the decision ID inline, e.g. "Deleted items are
  soft-deleted and hidden from all lists (D14)."
- When citing a decision, preserve its meaning exactly. If your paraphrase
  might change the meaning, quote the decision verbatim instead. Small
  wording drift is how readers end up acting on the wrong thing.
- If a decision is superseded by a later one ("D<n>: supersedes D<k> —
  ..."), use the superseding decision. The old one still counts as
  "landed" once the new one is cited.
- If the template asks for something the log does not contain, write
  `UNRESOLVED: <the exact question that needs answering>` in that spot.
  NEVER fill a gap with a plausible default, an industry standard, or an
  inference. An honest hole beats an invented answer.
- Do not add anything that is not in the log.
- Do not drop anything: every decision ID in the log must appear somewhere
  in OUTPUT. If a decision fits nowhere, put it in the template's
  catch-all section.
## TEMPLATE REQUIREMENTS
The binding supplies the exact TEMPLATE — this protocol has none. Whatever
the binding provides must contain, or the protocol above cannot run:
- frontmatter with `source: D1–D<last>` (fill <last> from the log);
- a catch-all section, for decisions that fit no other section;
- an open-questions section, where every UNRESOLVED item lands — carried
  over from the log or newly exposed by writing the document.
Use the TEMPLATE's sections exactly, in its order — never add, drop, or
reorder sections.
A TEMPLATE may embed `?` coverage items and "(interview only)" sections —
that makes it an interview template, usable by the interview-me engine as
its CHECKLIST. The sigil handling in step 1 already covers both kinds of
line; embedded questions change nothing else about this protocol.
## EXAMPLE (log lines → output lines)
Log contains:
    D14: Invoice deletion is a soft delete.
    D15: supersedes D3 — admins AND managers can delete invoices.
    (no decision about retention)
The output's data-model notes for the Invoice entity read:
    Soft-deleted (D14); deletable by admins and managers (D15).
    Retention: UNRESOLVED: how long are soft-deleted invoices retained?
Note what did NOT happen: no invented retention period ("90 days is
standard"), no silently keeping the superseded D3, no dropping D14.
## FINAL SELF-CHECK (do this silently before saving — do not print it)
1. List every D-ID in the log. Confirm each is cited somewhere in your
   draft. Any orphan goes in the catch-all section.
2. Confirm every UNRESOLVED line from the log appears in the
   open-questions section.
3. Scan your draft for any substantive statement with neither a (D<n>)
   citation nor an UNRESOLVED marker. Delete it or mark it — it is
   invented.
4. Confirm every `!` rule in the template is satisfied, and that no `!`
   or `?` line leaked into the draft.
5. Run every additional self-check your binding defines.
Only after all checks pass, save and print.
## REMINDER (read this last, follow it first)
You may only reorganize, never invent. Every gap becomes UNRESOLVED. Every
decision ID must land somewhere — run the self-check first. Save with a
real tool call and verify — printing is not saving. Then print the
document, print the REVIEW MESSAGE, and wait. Corrections that are
decisions go into the log first, never silently into the output.
