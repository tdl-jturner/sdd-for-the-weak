# FEEDBACK LEDGER — append-only record of pipeline skill edits
F1 2026-07-02 to-issues: with a second spec on disk, implement-issue scanned every issue; unpadded IDs also sort I10 before I2 -> issue IDs and filenames zero-padded to S<nn>-I<mm> so alphabetical path sort equals build order
F2 2026-07-02 interview-me: folder names S1/S2 sort wrong past S9 and break cross-spec path sort -> feature folders zero-padded to S<nn>-<slug>
F3 2026-07-02 implement-issue: read every issue across all specs to pick the next one -> PICK is a sorted grep for the first ^status: TODO, then reads only the candidate and its deps
F4 2026-07-02 to-spec: SPEC.md status stayed DRAFT forever, nothing ever advanced it -> dropped the status field from the SPEC template (spec state lives only in issue frontmatter)
F5 2026-07-02 spec-critique: found its spec by status DRAFT, which never flips - every spec qualified forever -> discovery is the highest-numbered folder in sort order, announced so the user can redirect
