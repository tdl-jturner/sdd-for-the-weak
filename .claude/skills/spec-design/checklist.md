# AREA CHECKLIST — feature requirements interview (spec pipeline)
1. PURPOSE — Who uses this? What problem does it solve? How do we know it worked?
2. SCOPE & NON-GOALS — What is explicitly OUT of scope for this version? (Push
   for at least 3 non-goals. Vague scope is the #1 spec killer.)
3. EXISTING CODE — If the project already has code, this is the one area
   where you gather facts yourself before asking: look at the entry points,
   the modules this feature would touch, the test setup, and the naming
   conventions. NEVER ask the user which files or functions to change — the
   user may never have read the code; research it yourself. Every question
   in this area presents YOUR finding for a yes/no: "This looks like it
   lives in the move logic in game.js; the UI must not change — correct?"
   The user confirms behavior and constraints, never code internals. Record
   confirmed findings as decisions WITH file paths — a spec that ignores the
   real codebase contradicts reality. A finding becomes a decision only when
   the user confirms it. Greenfield project? Record
   `D<n>: EXISTING CODE — greenfield, N/A`.
4. DATA — What entities exist? For each: fields, types, required/optional,
   uniqueness, who can see it, is it ever deleted (hard/soft)?
5. CORE FLOWS — For each main user action: trigger, steps, end state, what the
   user sees on success.
6. ERRORS & EDGE CASES — For each flow: invalid input, duplicate action,
   missing/deleted referenced data, concurrent edits, empty states, limits
   (max size, max count, rate).
7. PERMISSIONS — Who can do what? What happens on unauthorized attempt?
   Any admin/override paths?
8. EXTERNAL SYSTEMS — APIs, services, files, or systems this touches. For
   each: what if it's down, slow, or returns garbage?
9. CONSTRAINTS — Platform/language/framework requirements, performance targets,
   compatibility or migration needs, deadlines that affect scope.
10. TESTING — For each core flow: how do we verify it works (automated test,
    manual check?) and what observable signal proves success? Which flow is
    riskiest and deserves the most test coverage? These answers become the
    spec's acceptance criteria, so push for numbers and observable outcomes.
