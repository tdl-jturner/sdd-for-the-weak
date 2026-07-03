# FEEDBACK LEDGER — append-only record of pipeline skill edits
F1 2026-07-02 to-issues: with a second spec on disk, implement-issue scanned every issue; unpadded IDs also sort I10 before I2 -> issue IDs and filenames zero-padded to S<nn>-I<mm> so alphabetical path sort equals build order
F2 2026-07-02 interview-me: folder names S1/S2 sort wrong past S9 and break cross-spec path sort -> feature folders zero-padded to S<nn>-<slug>
F3 2026-07-02 implement-issue: read every issue across all specs to pick the next one -> PICK is a sorted grep for the first ^status: TODO, then reads only the candidate and its deps
F4 2026-07-02 to-spec: SPEC.md status stayed DRAFT forever, nothing ever advanced it -> dropped the status field from the SPEC template (spec state lives only in issue frontmatter)
F5 2026-07-02 spec-critique: found its spec by status DRAFT, which never flips - every spec qualified forever -> discovery is the highest-numbered folder in sort order, announced so the user can redirect
F6 2026-07-02 validator: nothing enforced zero-padding, one unpadded id would silently corrupt sort order -> validator rejects unpadded ids and folder names
F7 2026-07-02 unblock/diagnose-bug/README: example IDs still unpadded after scheme change; diagnose-bug mints IDs by imitating them -> padded every example ID
F8 2026-07-02 migration: user explicitly overrode the never-rename ledger invariant for a one-time scheme change -> renamed 2 spec folders + 14 issue files to S<nn>-I<mm>, padded all id/depends_on/INDEX refs, stripped SPEC status lines; validator PASS on both specs after
F9 2026-07-02 implement-issue: model translated the PICK grep into PowerShell and burned a run on a shell error -> command is now 'run EXACTLY this, verbatim, in your Bash tool', not an e.g.
