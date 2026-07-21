# Eval runner contract

The evals are harness-independent. Fixtures and graders are the durable
assets; a "runner" is anything that satisfies the contract below. The
Claude Code subagent setup used for iteration 1 is one implementation,
not a dependency.

Two slices exist, one per half of `spec-design`, both driven by
`evals/run.py` (`--mode populate` / `--mode interview` / `--mode all`):

- **Populate** (this file's main contract): a complete decision log in, a
  SPEC.md out, single-shot.
- **Interview** (see the section at the end): a feature brief in, a
  DECISIONS.md out, built over a multi-turn conversation with a simulated
  user that says "yes" to every suggestion.

`run.py` needs only Python 3.8+ and an authenticated `claude` CLI; run
`python evals/run.py --help` for all flags. The steps below are what it does
for each slice — reimplement them verbatim in any other harness.

## The populate contract

For each fixture `evals/fixtures/populate-template/<F>/` and each configuration:

1. **Build a sandbox** (a throwaway directory, ideally outside this repo
   to avoid skill contamination):
   ```
   <sandbox>/
     specs/                  copied from evals/fixtures/populate-template/<F>/specs/
     .claude/skills/         with_skill config only: copy spec-design/,
                             populate-template/, interview-me/
   ```
2. **Run the model under test** with the sandbox as its project root and
   file read/write ability:
   - with_skill: "Read .claude/skills/spec-design/SKILL.md and follow it
     exactly. The decision log under specs/ is complete — write the
     spec." (If the harness has no skill auto-triggering, injecting that
     file — and the two PROTOCOL.md files plus template.md it references
     — into context is equivalent.)
   - without_skill (baseline): "Read specs/<S>/DECISIONS.md and
     specs/GLOSSARY.md. Write a specification document for implementers
     as specs/<S>/SPEC.md, derived from that decision log."
   The model may be anything that can read and write files. Target the
   weakest model you intend to drive the pipeline with — a strong model
   passing proves nothing about the skill text.
3. **Grade** (requires only Python 3.8+, stdlib). The grader ships inside the
   populate-template skill — the populate protocol also runs it at
   runtime as a gate, the same dual role to-issues' validate.py
   plays. Sections, frontmatter keys, and placeholders are derived from
   the template argument, so it works for any binding's template:
   ```
   python .claude/skills/populate-template/scripts/validate.py \
        <sandbox>/specs/<S>/DECISIONS.md <sandbox>/specs/<S>/SPEC.md \
        .claude/skills/spec-design/template.md \
        evals/fixtures/populate-template/<F>/expected.json [--json grading.json]
   ```
   Exit 0 = all checks pass. Stdout is PASS/FAIL per check plus
   `SUMMARY p/t`. `--json` emits `{summary: {pass_rate, passed, failed,
   total}, expectations: [{text, passed, evidence}]}`.
4. **Aggregate** however you like. Per-check pass rates across trials
   are the useful unit — a single overall number hides which rule
   regressed. Run multiple trials per case; weak models are
   high-variance, and a rule that holds 6/10 times is a finding.

## Fixture format

Each `evals/fixtures/populate-template/<F>/` holds `specs/` (a GLOSSARY.md and one
`S<nn>-<slug>/DECISIONS.md` with `status: COMPLETE`) and an
`expected.json` of trap checks. Check types: `required` /
`forbidden` (regex over the whole spec), `section_required` (regex
within section N), `line_guard` (every line matching `pattern` must
also match `unless` — e.g. any hard/soft-delete claim must be an
UNRESOLVED marker). The generic invariants (sections, citations,
UNRESOLVED carry-over, glossary verbatim/unused, sigil leaks) are built
into the grader and need no per-fixture configuration.

## Known implementations

- **Claude Code** (iteration 1): parallel Haiku subagents, one sandbox
  per run under `spec-design-workspace/iteration-<N>/eval-<id>-<name>/
  <config>/`, grading.json in `run-<n>/`, aggregated with the
  skill-creator plugin's benchmark/viewer tooling. That workspace layout
  and viewer are conveniences of that plugin only.
- **Anything else** (promptfoo `exec:` provider, an Inspect AI solver, a
  bash loop over a CLI): implement steps 1–3 verbatim; the grader and
  fixtures are used unchanged.

## The interview contract

The interview slice tests the OTHER half of `spec-design`: given only a
feature brief and no decision log, does the skill drive a complete,
structurally valid DECISIONS.md? Run it with `python evals/run.py --mode interview`.

Fixtures live under `evals/fixtures/interview-me/<F>/`:
- `brief.md` — the opening message the simulated user sends (a plain-English
  feature idea, asking to be interviewed with a suggestion per question).
- `expected.json` — interview trap checks. Types: `required` / `forbidden`
  (regex over the whole log) and `min_decisions` (`count` integer).

The loop, per fixture (with_skill only — the DECISIONS.md format is
skill-defined, so a no-skill baseline is uninformative):

1. Build an out-of-repo sandbox with the three skills copied in and an empty
   `specs/`. `spec-design` sees no COMPLETE log and routes to INTERVIEW mode
   for a new feature.
2. Open the session with `brief.md` (capture the `session_id`). Then, until
   the sole `specs/*/DECISIONS.md` reads `status: COMPLETE` or a turn cap is
   hit, resume that session with a fixed "yes, go with your suggestion"
   reply. That fixed reply IS the simulated user — the weakest possible one,
   which makes a completed, valid log a strong signal that the skill's
   scaffolding (one question per turn, append-only log, per-save validator
   gate) carries the model on its own.
3. Grade the built log with the interview validator plus the fixture's
   expected.json:
   ```
   python .claude/skills/interview-me/scripts/validate.py \
        <sandbox>/specs/<S>/DECISIONS.md \
        .claude/skills/spec-design/template.md \
        evals/fixtures/interview-me/<F>/expected.json [--json grading.json]
   ```

`MAX_TURNS` caps the conversation (default 50); a log still `IN PROGRESS` at
the cap fails the "reached COMPLETE" check, which is the finding you want.

## Caveats learned across iterations

- Baselines run inside this repo can see the pipeline skills (session
  skill discovery) — put sandboxes outside the repo for a clean
  baseline. Both runners use `mktemp -d`.
- The model must be told there is no interactive user: populate mode ends
  by printing a review message and waiting, so instruct it to print and
  stop; the interview runner instead supplies the "user" itself, one canned
  reply per turn.
- Grade with the repo's canonical validator, template, and expected.json —
  never the copies inside a with_skill sandbox — so grading is identical
  across configs and can't be tampered with by the run under test.
- The `claude` CLI must be authenticated (`/login` or `ANTHROPIC_API_KEY`);
  both scripts preflight one headless prompt and fail fast with the CLI's
  own message if not.
