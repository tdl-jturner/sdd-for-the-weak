#!/usr/bin/env python3
"""Deterministic checks for a spec-pipeline feature folder.
Usage: python validate.py <feature-folder>   e.g. specs/S01-my-feature
Exit codes: 0 = PASS, 1 = failures found, 2 = usage error.
Self-contained: Python 3 standard library only."""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def frontmatter(text):
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", text)
    if not m:
        return None
    out = {}
    for line in re.split(r"\r?\n", m.group(1)):
        i = line.find(":")
        if i > 0:
            out[line[:i].strip()] = line[i + 1:].strip()
    return out


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def main():
    if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
        print("Usage: python validate.py <feature-folder>  e.g. specs/S01-my-feature", file=sys.stderr)
        sys.exit(2)
    dir_ = sys.argv[1]
    issues_dir = os.path.join(dir_, "issues")
    errors = []

    # Zero-padding is load-bearing: alphabetical path sort must equal build order.
    dir_base = os.path.basename(os.path.abspath(dir_))
    if not re.match(r"^S\d{2}-", dir_base):
        errors.append(f'feature folder "{dir_base}" is not zero-padded (expected S<nn>-<slug>, e.g. S01-invoices)')

    if not os.path.isdir(issues_dir):
        print("FAIL\n- no issues/ folder in " + dir_)
        sys.exit(1)

    issues = []
    for f in sorted(os.listdir(issues_dir)):
        if not re.match(r"^S\d+-I\d+-.*\.md$", f):
            continue
        with open(os.path.join(issues_dir, f), encoding="utf-8") as fh:
            text = fh.read()
        meta = frontmatter(text)
        if meta is None:
            errors.append(f"{f}: missing frontmatter")
            continue
        name_id = (re.match(r"^(S\d+-I\d+)", f) or [None, None])[1]
        if meta.get("id") != name_id:
            errors.append(f'{f}: frontmatter id "{meta.get("id")}" does not match filename id "{name_id}"')
        issues.append({
            "f": f, "id": meta.get("id") or name_id,
            "n": int(name_id.split("-I")[1]), "meta": meta, "text": text,
        })
    issues.sort(key=lambda it: it["n"])

    # 1. IDs sequential from I01 and zero-padded — append-only numbering, never reused
    for i, it in enumerate(issues):
        if not re.match(r"^S\d{2}-I\d{2}$", it["id"] or ""):
            errors.append(f'{it["id"]}: id not zero-padded to two digits (expected S<nn>-I<mm>, e.g. S01-I02) — sort order depends on it')
        if it["n"] != i + 1:
            errors.append(f'numbering broken at {it["id"]} (expected I{i + 1:02d}): IDs must be sequential, never reused')

    # 2. Legal statuses; DONE needs evidence; deps exist and point backward; max one IN PROGRESS
    legal = re.compile(r"^(TODO|IN PROGRESS|DONE|BLOCKED: .+|DROPPED: .+)$")
    in_progress = 0
    for it in issues:
        s = it["meta"].get("status", "")
        if not legal.match(s):
            errors.append(f'{it["id"]}: illegal status "{s}"')
        if s == "IN PROGRESS":
            in_progress += 1
        if s == "DONE" and it["meta"].get("evidence", "none") in ("", "none"):
            errors.append(f'{it["id"]}: DONE without evidence')
        dep = it["meta"].get("depends_on", "none").strip()
        if dep != "none":
            for d in [x.strip() for x in dep.split(",")]:
                target = next((o for o in issues if o["id"] == d), None)
                if target is None:
                    errors.append(f'{it["id"]}: depends_on {d} does not exist')
                elif target["n"] >= it["n"]:
                    errors.append(f'{it["id"]}: depends_on {d} is not a lower-numbered issue')
    if in_progress > 1:
        errors.append(f"{in_progress} issues are IN PROGRESS — the maximum is 1")

    # 3. No INDEX.md — the concept was removed; sorted padded filenames ARE the build order
    if os.path.exists(os.path.join(issues_dir, "INDEX.md")):
        errors.append("issues/INDEX.md exists — the index concept was removed (sorted filenames are the build order); delete it")

    # 4. Every SPEC section 11 criterion appears in some issue's Covers line
    spec_path = os.path.join(dir_, "SPEC.md")
    if not os.path.exists(spec_path):
        errors.append("SPEC.md is missing")
    else:
        with open(spec_path, encoding="utf-8") as fh:
            spec = fh.read()
        parts = re.split(r"^## 11\..*$", spec, maxsplit=1, flags=re.M)
        s11 = re.split(r"^## ", parts[1], maxsplit=1, flags=re.M)[0] if len(parts) > 1 else ""
        criteria = [m.group(1).split("— verified by")[0].strip()
                    for m in re.finditer(r"^- \[[ x]\] (.+)$", s11, re.M)]
        if not criteria:
            errors.append('SPEC.md section 11 has no "- [ ]" acceptance criteria')
        covers = [(re.search(r"^Covers: (.+)$", it["text"], re.M) or [None, ""])[1] for it in issues]
        all_covers = norm(" | ".join(covers))
        for c in criteria:
            needle = norm(c)[:60]
            if needle and needle not in all_covers:
                errors.append(f'criterion not covered by any issue: "{c[:70]}"')

    # Status summary and blocker report (printed on PASS and FAIL alike —
    # blocked work is invisible unless something surfaces it)
    counts = {}
    for it in issues:
        k = it["meta"].get("status", "MISSING").split(":")[0].strip()
        counts[k] = counts.get(k, 0) + 1
    summary = ", ".join(f"{v} {k}" for k, v in counts.items())
    blocked = [it for it in issues if it["meta"].get("status", "").startswith("BLOCKED")]

    if errors:
        print("FAIL")
        for e in errors:
            print("- " + e)
        for it in blocked:
            reason = re.sub(r"^BLOCKED:\s*", "", it["meta"]["status"])
            print(f'BLOCKED {it["id"]}: {reason}')
        sys.exit(1)
    print(f"PASS - {len(issues)} issues ({summary}): numbering sequential, statuses legal, all section 11 criteria covered")
    for it in blocked:
        reason = re.sub(r"^BLOCKED:\s*", "", it["meta"]["status"])
        print(f'BLOCKED {it["id"]}: {reason} -> run the unblock skill')


if __name__ == "__main__":
    main()
