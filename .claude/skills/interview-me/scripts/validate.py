#!/usr/bin/env python3
"""validate.py — deterministic check of an interview decision log.
Dual use: the interview protocol runs it after every save as a gate;
evals run it as a grader over saved logs.
Usage: python validate.py <log.md> [checklist-or-template.md] [--json <out.json>]
With the checklist/template argument it also verifies the areas_done
denominator matches the number of question-bearing areas.
Append-only discipline cannot be verified from one snapshot — that is an
eval-harness check (diff successive saves), not a gate check.
Self-contained: Python 3 standard library only."""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

results = []


def check(text, passed, evidence):
    results.append({"text": text, "passed": bool(passed), "evidence": evidence})


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


def main():
    args = sys.argv[1:]
    json_out = None
    if "--json" in args:
        i = args.index("--json")
        json_out = args[i + 1]
        del args[i:i + 2]
    if not args:
        print("usage: validate.py <log.md> [checklist.md] [--json out]", file=sys.stderr)
        sys.exit(2)
    log_path = args[0]
    checklist_path = args[1] if len(args) > 1 else None

    try:
        with open(log_path, encoding="utf-8") as fh:
            log = fh.read()
    except OSError:
        log = None
    check("decision log exists at the given path", log is not None, log_path)
    if log is None:
        finish(json_out)

    lines = re.split(r"\r?\n", log)

    # frontmatter: status and areas_done are the engine's keys
    fm = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", log)
    status_m = fm and re.search(r"^status:\s*(.+)$", fm.group(1), re.M)
    status = status_m.group(1).strip() if status_m else None
    areas_m = fm and re.search(r"^areas_done:\s*([\d,\s]+|\S+)\s+of\s+(\d+)\s*$", fm.group(1), re.M)
    check("frontmatter has status: IN PROGRESS|COMPLETE and areas_done: <done> of <total>",
          fm and status in ("IN PROGRESS", "COMPLETE") and areas_m,
          f'status: {status or "missing"}; areas_done {"ok" if areas_m else "missing or malformed"}' if fm else "no frontmatter found")

    # with a checklist/template: denominator must match its area count
    if checklist_path and areas_m:
        with open(checklist_path, encoding="utf-8") as fh:
            tpl = fh.read()
        current, areas = None, set()
        for l in re.split(r"\r?\n", tpl):
            h = re.match(r"^##\s+(.+)$", l) or re.match(r"^(\d+)\.\s+\S", l)
            if h:
                current = h.group(1)
            elif re.match(r"^\s*\?\s", l) and current:
                areas.add(current)
        check(f"areas_done total matches the checklist's {len(areas)} question-bearing areas",
              int(areas_m.group(2)) == len(areas),
              f"log says of {areas_m.group(2)}, checklist has {len(areas)}")

    # required structure, in order
    need = [r"^# DECISIONS — ", r"^## Summary$", r"^## Decision Log$", r"^## Unresolved$"]
    idxs = []
    for pat in need:
        m = re.search(pat, log, re.M)
        idxs.append(m.start() if m else -1)
    in_order = all(v > idxs[i - 1] for i, v in enumerate(idxs) if i > 0)
    check("log has '# DECISIONS — <topic>', '## Summary', '## Decision Log', '## Unresolved', in order",
          all(i >= 0 for i in idxs) and in_order,
          "a required heading is missing" if any(i < 0 for i in idxs) else ("all present" if in_order else "headings out of order"))

    # D-lines: contiguous 1..N, ascending, no duplicates, all in the Decision Log section
    d_matches = [{"id": int(m.group(1)), "text": m.group(2)}
                 for m in re.finditer(r"^D(\d+):\s*(.+)$", log, re.M)]
    ids = [d["id"] for d in d_matches]
    dupes = [v for i, v in enumerate(ids) if v in ids[:i]]
    ascending = all(v > ids[i - 1] for i, v in enumerate(ids) if i > 0)
    contiguous = not ids or (ids[0] == 1 and ids[-1] == len(ids) and not dupes)
    check("decision IDs run D1..D<n> contiguously, in ascending order, no duplicates or gaps",
          ascending and contiguous,
          f"duplicate: D{dupes[0]}" if dupes else
          "IDs out of order (log rot: lines were reordered or renumbered)" if not ascending else
          f"{len(ids)} decisions, D1–D{len(ids)}" if contiguous else f"IDs not contiguous 1..{len(ids)}")

    # supersedes lines point backward at an existing decision
    bad_sup = []
    for d in d_matches:
        s = re.match(r"^supersedes\s+D(\d+)\b", d["text"])
        if s and (int(s.group(1)) >= d["id"] or int(s.group(1)) not in ids):
            bad_sup.append(f'D{d["id"]} supersedes D{s.group(1)}')
    check("every 'supersedes D<k>' points backward at an existing decision",
          not bad_sup, "; ".join(bad_sup) if bad_sup else "supersede chain sound")

    # section content: Decision Log holds only D-lines; Unresolved only UNRESOLVED/RESOLVED lines
    def section(name):
        try:
            i = next(j for j, l in enumerate(lines) if l.strip() == f"## {name}")
        except StopIteration:
            return []
        end = next((j for j, l in enumerate(lines) if j > i and re.match(r"^## ", l)), len(lines))
        return lines[i + 1:end]

    stray_d = [l for l in section("Decision Log")
               if l.strip() and not re.match(r"^D\d+:", l) and not re.match(r"^\s", l)]
    check("the Decision Log section contains only D-lines (indented continuations allowed)",
          not stray_d, f'stray line: "{stray_d[0].strip()[:60]}"' if stray_d else "clean")
    stray_u = [l for l in section("Unresolved")
               if l.strip() and not re.match(r"^(UNRESOLVED:|RESOLVED\b|RESOLVED \()", l.strip())]
    check("the Unresolved section contains only UNRESOLVED:/RESOLVED lines",
          not stray_u, f'stray line: "{stray_u[0].strip()[:60]}"' if stray_u else "clean")

    # COMPLETE means complete
    if status == "COMPLETE" and areas_m:
        left = areas_m.group(1).strip()
        done_count = len([s for s in left.split(",") if s.strip()]) if "," in left else int(left)
        check("status COMPLETE requires areas_done to cover every area",
              done_count == int(areas_m.group(2)),
              f"areas_done says {done_count} of {areas_m.group(2)}")

    finish(json_out)


if __name__ == "__main__":
    main()
