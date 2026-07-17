# LENSES — spec critique (spec pipeline)
Recommended run order: TRACE, HOLES, CLASH, TEST, VAGUE — traceability
errors invalidate the later lenses.
- TRACE — Compare spec against decision log, both directions. Flag: spec
  statements with no supporting decision (invention), decisions missing from
  the spec (dropped), spec statements that contradict their cited decision.
  Remember superseding lines ("D<n>: supersedes D<k>") — the newest wins;
  a spec citing the superseded version is a contradiction.
- HOLES — For every flow and entity, hunt missing cases: invalid input,
  duplicate submission, referenced data missing or deleted, concurrent edits,
  empty states, limits exceeded, external system down. Flag each flow that
  doesn't define the behavior.
- TEST — Read only section 11. Flag every acceptance criterion that a tester
  could not mechanically verify pass/fail (vague adjectives, no numbers, no
  defined observation point), and every goal in section 2 with no criterion
  covering it.
- VAGUE — Flag every "should", "might", "usually", "appropriately", "etc.",
  every term used but not in the glossary, and every place two readers could
  implement different behavior from the same sentence.
- CLASH — Flag every pair of spec statements that contradict each other, and
  every place a flow's steps don't match the data model or permissions
  sections.
