#!/usr/bin/env python3
"""validate.py — deterministic check of a populate-template OUTPUT against
its SOURCE decision log and TEMPLATE. Everything section-shaped is derived
from the template, so any binding (spec-design's SPEC, a generic PRD, ...)
gets the same gate. Dual use: the populate protocol runs it before handing
the document to the user; evals/ runs it as the grader (with an
expected.json of fixture-specific trap checks).
Usage: python validate.py <log.md> <output.md> <template.md>
       [expected.json] [--json <out.json>]
Glossary checks fire only when a GLOSSARY.md exists next to (or one level
above) the log, and the template has a section titled like "Glossary".
Self-contained: Python 3 standard library only."""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

results = []


def check(text, passed, evidence):
    results.append({"text": text, "passed": bool(passed), "evidence": evidence})


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def finish(json_out):
    passed = sum(1 for r in results if r["passed"])
    for r in results:
        print(f'{"PASS" if r["passed"] else "FAIL"}  {r["text"]}' + ("" if r["passed"] else "  -> " + r["evidence"]))
    print(f"SUMMARY {passed}/{len(results)}")
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump({
                "summary": {"pass_rate": passed / len(results) if results else 0,
                            "passed": passed, "failed": len(results) - passed, "total": len(results)},
                "expectations": results,
            }, fh, indent=2)
    sys.exit(0 if passed == len(results) else 1)


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def main():
    args = sys.argv[1:]
    json_out = None
    if "--json" in args:
        i = args.index("--json")
        json_out = args[i + 1]
        del args[i:i + 2]
    if len(args) < 3:
        print("usage: validate.py <log.md> <output.md> <template.md> [expected.json] [--json out]", file=sys.stderr)
        sys.exit(2)
    log_path, out_path, tpl_path = args[0], args[1], args[2]
    expected_path = args[3] if len(args) > 3 else None

    log = read(log_path)
    tpl = read(tpl_path)
    try:
        out = read(out_path)
    except OSError:
        out = None
    check("OUTPUT exists at the bound path", out is not None, out_path)
    if out is None:
        finish(json_out)

    out_lines = re.split(r"\r?\n", out)

    # --- template-derived structure
    tpl_sections = []      # numbered sections expected in output
    for l in re.split(r"\r?\n", tpl):
        m = re.match(r"^##\s+(\d+)\.\s+(.*)$", l)
        if m:
            tpl_sections.append({"num": int(m.group(1)), "title": m.group(2).strip()})
    fm_m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", tpl)
    tpl_fm_keys = re.findall(r"^(\w[\w-]*):", fm_m.group(1), re.M) if fm_m else []
    tpl_placeholders = list(dict.fromkeys(re.findall(r"<[^>\n]+>", tpl)))

    def find_section(pattern):
        return next((s for s in tpl_sections if re.search(pattern, s["title"], re.I)), None)

    gloss_section = find_section(r"glossary")
    openq_section = find_section(r"open ?questions?")

    heading_at = []
    for i, l in enumerate(out_lines):
        m = re.match(r"^##\s+(\d+)\.\s+(.*)$", l)
        if m:
            heading_at.append({"num": int(m.group(1)), "title": m.group(2).strip(), "line": i})

    def section_body(n):
        idx = next((i for i, h in enumerate(heading_at) if h["num"] == n), -1)
        if idx < 0:
            return None
        start = heading_at[idx]["line"] + 1
        end = heading_at[idx + 1]["line"] if idx + 1 < len(heading_at) else len(out_lines)
        return "\n".join(out_lines[start:end])

    # frontmatter: every template frontmatter key present, and the engine's
    # source: D1–D<last> matches the log's highest D-number
    fm = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", out)
    d_ids = [int(m) for m in re.findall(r"^D(\d+):", log, re.M)]
    max_d = max(d_ids, default=0)
    fm_missing = [k for k in tpl_fm_keys if not (fm and re.search(rf"^{k}:", fm.group(1), re.M))]
    src_ok = bool(fm and re.search(rf"source:\s*D1[–-]D{max_d}\b", fm.group(1)))
    check(f'frontmatter carries the template\'s keys ({", ".join(tpl_fm_keys)}) with source: D1–D{max_d}',
          fm and not fm_missing and src_ok,
          (f'missing keys: {", ".join(fm_missing)}' if fm_missing else
           (fm.group(1).strip() if src_ok else f"source range wrong (log max is D{max_d})")) if fm else "no frontmatter found")

    # sections: exactly the template's numbered sections, exact titles, in order
    missing = [s for s in tpl_sections
               if not any(h["num"] == s["num"] and norm(h["title"]) == norm(s["title"]) for h in heading_at)]
    extras = [h for h in heading_at if not any(s["num"] == h["num"] for s in tpl_sections)]
    ordered = all(h["num"] > heading_at[i - 1]["num"] for i, h in enumerate(heading_at) if i > 0)
    check(f"all {len(tpl_sections)} template sections present with exact titles, in order, no extras",
          not missing and not extras and ordered,
          f'missing/mistitled: {"; ".join(str(s["num"]) + ". " + s["title"] for s in missing)}' if missing else
          f'sections not in template: {", ".join(str(h["num"]) for h in extras)}' if extras else
          "matches template" if ordered else "sections out of order")

    # no sigil lines, interview-only blocks, or template placeholders
    leaks = []
    for i, l in enumerate(out_lines):
        if re.match(r"^\s*[?!]\s", l):
            leaks.append(f"line {i + 1}: {l.strip()[:60]}")
    if re.search(r"\(interview only", out, re.I):
        leaks.append("contains an '(interview only)' block")
    for p in tpl_placeholders:
        if p in out:
            leaks.append(f"placeholder leftover: {p}")
    check("no ?/! sigil lines, interview-only blocks, or template placeholders leaked into the output",
          not leaks, "; ".join(leaks) if leaks else "clean")

    # every decision lands (superseded IDs count once their superseder is cited)
    supersedes = {int(m.group(2)): int(m.group(1))
                  for m in re.finditer(r"^D(\d+):\s*supersedes\s+D(\d+)", log, re.M)}
    cited = {int(m) for m in re.findall(r"\(D(\d+)[),\s]", out)}

    def landed(i):
        cur, hops = i, 0
        while hops < 50:
            hops += 1
            if cur in cited:
                return True
            if cur not in supersedes:
                return False
            cur = supersedes[cur]
        return False

    orphans = [i for i in d_ids if not landed(i)]
    check("every decision ID in the log is cited in the output (or its superseder is)",
          not orphans,
          f'uncited: {", ".join("D" + str(i) for i in orphans)}' if orphans else f"{len(d_ids)} decisions all land")

    # every UNRESOLVED in the log reaches the open-questions section
    log_unresolved = [m.strip() for m in re.findall(r"^UNRESOLVED:\s*(.+)$", log, re.M)]
    openq_body = (section_body(openq_section["num"]) or "") if openq_section else out
    dropped = [q for q in log_unresolved
               if re.sub(r"[.?]+$", "", norm(q))[:60] not in norm(openq_body)]
    oq_label = f' ({openq_section["num"]})' if openq_section else ""
    check("every UNRESOLVED question from the log appears in the open-questions section" + oq_label,
          not dropped, f'missing: {" | ".join(dropped)}' if dropped else f"{len(log_unresolved)} carried over")

    # glossary (only when a glossary file and a glossary section exist):
    # used terms copied verbatim, unused terms absent
    if gloss_section:
        gloss = []
        for cand in (os.path.join(os.path.dirname(log_path), "..", "GLOSSARY.md"),
                     os.path.join(os.path.dirname(log_path), "GLOSSARY.md")):
            try:
                gloss = [l.strip() for l in re.split(r"\r?\n", read(cand))
                         if re.match(r"^[A-Za-z][\w -]*:\s+.+$", l)]
                break
            except OSError:
                continue
        if gloss:
            g_body = section_body(gloss_section["num"]) or ""
            g_idx = next((i for i, h in enumerate(heading_at) if h["num"] == gloss_section["num"]), -1)
            g_start = heading_at[g_idx]["line"] if g_idx >= 0 else -1
            g_end = heading_at[g_idx + 1]["line"] if 0 <= g_idx + 1 < len(heading_at) else len(out_lines)
            outside = "\n".join(l for i, l in enumerate(out_lines)
                                if not (g_start >= 0 and g_start < i < g_end))
            problems = []
            for entry in gloss:
                term = entry.split(":")[0]
                used = re.search(rf"\b{re.escape(term)}\b", outside, re.I)
                copied = any(l.strip() == entry for l in re.split(r"\r?\n", g_body))
                if used and not copied:
                    problems.append(f"'{term}' used but entry not verbatim in section {gloss_section['num']}")
                if not used and copied:
                    problems.append(f"'{term}' unused but copied into section {gloss_section['num']}")
            check("glossary rule: used terms copied verbatim, unused terms absent",
                  not problems, "; ".join(problems) if problems else f"{len(gloss)} glossary entries checked")

    # hedging gate: definitive document text must not hedge (the mechanical
    # leg of the VAGUE critique lens). Questions may hedge: UNRESOLVED lines
    # and the open-questions section are exempt. If a logged decision truly
    # contains a hedge word, the fix is a superseding decision phrased
    # definitively — not hedged output text.
    vague_re = re.compile(r"\b(should|might|usually|appropriately)\b|\betc\b\.?", re.I)
    oq_idx = next((i for i, h in enumerate(heading_at) if openq_section and h["num"] == openq_section["num"]), -1)
    oq_start = heading_at[oq_idx]["line"] if oq_idx >= 0 else -1
    oq_end = (heading_at[oq_idx + 1]["line"] if oq_idx + 1 < len(heading_at) else len(out_lines)) if oq_idx >= 0 else -1
    hedges = []
    for i, l in enumerate(out_lines):
        if oq_start >= 0 and oq_start <= i < oq_end:
            continue
        if "UNRESOLVED" in l:
            continue
        m = vague_re.search(l)
        if m:
            hedges.append(f'line {i + 1} ("{m.group(0)}"): {l.strip()[:60]}')
    check("no hedging words (should/might/usually/appropriately/etc.) outside UNRESOLVED lines and the open-questions section",
          not hedges, "; ".join(hedges[:3]) if hedges else "definitive throughout")

    # acceptance criteria (when the template has such a section): every
    # checkbox criterion cites a decision ID
    ac_section = find_section(r"acceptance criteria")
    if ac_section:
        ac_bad = [l for l in re.split(r"\r?\n", section_body(ac_section["num"]) or "")
                  if re.match(r"^\s*- \[", l) and not re.search(r"\(D\d+", l)]
        check(f'every acceptance criterion in section {ac_section["num"]} cites a decision ID',
              not ac_bad, f'uncited criterion: "{ac_bad[0].strip()[:70]}"' if ac_bad else "all criteria cited")

    # fixture-specific expectations (evals only)
    if expected_path:
        with open(expected_path, encoding="utf-8") as fh:
            exp = json.load(fh)
        for e in exp.get("checks", []):
            flags = re.I if "i" in e.get("flags", "i") else 0
            pat = re.compile(e["pattern"], flags)
            if e["type"] == "required":
                hit = pat.search(out)
                check(e["name"], hit, "found" if hit else f'pattern not found: /{e["pattern"]}/')
            elif e["type"] == "forbidden":
                m = pat.search(out)
                check(e["name"], not m, f'forbidden match: "{m.group(0)}"' if m else "absent as required")
            elif e["type"] == "section_required":
                body = section_body(e["section"]) or ""
                hit = pat.search(body)
                check(e["name"], hit, f'found in section {e["section"]}' if hit else f'not found in section {e["section"]}')
            elif e["type"] == "line_guard":
                unless = re.compile(e["unless"], re.I)
                bad = [l for l in out_lines if pat.search(l) and not unless.search(l)]
                check(e["name"], not bad, f'unguarded line: "{bad[0].strip()[:80]}"' if bad else "all matching lines guarded")

    finish(json_out)


if __name__ == "__main__":
    main()
