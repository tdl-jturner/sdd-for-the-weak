# LENSES — spec critique (spec pipeline)
The populate validator already guarantees, mechanically: every decision
ID lands, every log UNRESOLVED reaches section 13, glossary entries are
verbatim and only for used terms, acceptance criteria cite decision IDs,
and no hedging words survive outside UNRESOLVED lines. Never spend a
finding re-checking those — hunt what only judgment can catch.
Recommended run order: TRACE, HOLES, CLASH, TEST — traceability errors
invalidate the later lenses. VAGUE is optional polish once the others
come back PASS.
- TRACE — Compare spec against decision log, both directions. Flag: spec
  statements with no supporting decision (invention), and spec statements
  that contradict their cited decision. Remember superseding lines
  ("D<n>: supersedes D<k>") — the newest wins; a spec statement matching
  the superseded version is a contradiction. (Dropped decisions are the
  validator's job — skip that hunt.)
- HOLES — For every flow and entity, hunt missing cases: invalid input,
  duplicate submission, referenced data missing or deleted, concurrent edits,
  empty states, limits exceeded, external system down. Flag each flow that
  doesn't define the behavior.
- CLASH — Flag every pair of spec statements that contradict each other, and
  every place a flow's steps don't match the data model or permissions
  sections.
- TEST — Read only section 11. Flag every acceptance criterion that a tester
  could not mechanically verify pass/fail (vague adjectives, no numbers, no
  defined observation point), and every goal in section 2 with no criterion
  covering it. (Citation format is validator-checked — judge the substance,
  not the format.)
- VAGUE (optional) — Flag every project-specific term used but not in the
  glossary, and every place two readers could implement different behavior
  from the same sentence. (The hedging-word scan is validator-enforced —
  don't re-flag those words.)
