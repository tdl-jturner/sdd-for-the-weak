#!/usr/bin/env python3
"""run.py — run the spec-design evals end to end with the `claude` CLI.

Two slices, one per half of the skill:

  populate   a complete decision log in, a SPEC.md out (single shot). Runs
             with_skill and a no-skill baseline so the delta is visible.
  interview  a feature brief in, a DECISIONS.md out, built over a multi-turn
             conversation driven by a simulated user that says "yes" to every
             suggestion. with_skill only — the log format is skill-defined, so
             a no-skill baseline is uninformative.

Both build throwaway sandboxes OUTSIDE the repo (so a baseline can't see the
session's skills), run the model under test in them, and grade the result with
the validator the skill already ships as its runtime gate. See evals/run.md
for the harness-independent contract this implements.

Examples:
  python evals/run.py                         # both modes, haiku
  python evals/run.py --mode populate         # just the populate slice
  python evals/run.py --mode interview --max-turns 40
  python evals/run.py --model claude-haiku-4-5-20251001 --trials 3
  python evals/run.py --fixtures S02-file-uploads invoice-manager
  python evals/run.py --list

Requirements: python 3.8+, and an authenticated `claude` CLI on PATH
(`claude` then `/login`, or set ANTHROPIC_API_KEY).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = ("spec-design", "populate-template", "interview-me")
TEMPLATE = os.path.join(REPO, ".claude/skills/spec-design/template.md")
POPULATE_VALIDATOR = os.path.join(REPO, ".claude/skills/populate-template/scripts/validate.py")
INTERVIEW_VALIDATOR = os.path.join(REPO, ".claude/skills/interview-me/scripts/validate.py")
POPULATE_FIXTURES = os.path.join(REPO, "evals/fixtures/populate-template")
INTERVIEW_FIXTURES = os.path.join(REPO, "evals/fixtures/interview-me")
INTERVIEW_ANSWER = "Yes, go with your suggestion. Continue to the next question."

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# --- claude CLI -------------------------------------------------------------

def claude_json(prompt, cwd, model, resume=None):
    """Run one headless `claude` turn and return its parsed JSON result.
    Prompt goes on stdin (no arg-quoting headaches); shell=True so a Windows
    `claude.cmd` shim resolves the same way it does in a terminal."""
    cmd = f"claude -p --model {model} --permission-mode bypassPermissions --output-format json"
    if resume:
        cmd += f" --resume {resume}"
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, input=prompt,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return {"is_error": True, "result": f"failed to launch claude: {e}"}
    try:
        return json.loads(p.stdout)
    except Exception:  # noqa: BLE001
        return {"is_error": True,
                "result": (p.stdout or p.stderr or "no output from claude").strip()[:500]}


def preflight(model):
    if not shutil.which("claude"):
        sys.exit("error: 'claude' CLI not on PATH")
    print("checking claude auth ...")
    d = claude_json("Reply with the single word READY.", REPO, model)
    if d.get("is_error"):
        print("error: the 'claude' CLI could not run a headless prompt.", file=sys.stderr)
        if d.get("result"):
            print(f"  CLI says: {d['result']}", file=sys.stderr)
        print("  Fix: run 'claude' once and '/login' (or set ANTHROPIC_API_KEY), then retry.", file=sys.stderr)
        print(f"  Also check the model alias '{model}' is valid for your account.", file=sys.stderr)
        sys.exit(1)
    print("auth OK\n")


# --- shared helpers ---------------------------------------------------------

def copy_skills(sandbox):
    dst = os.path.join(sandbox, ".claude", "skills")
    os.makedirs(dst, exist_ok=True)
    for sk in SKILLS:
        shutil.copytree(os.path.join(REPO, ".claude/skills", sk), os.path.join(dst, sk))


def write_timing(rundir, result):
    ms = result.get("duration_ms", 0) or 0
    usage = result.get("usage", {}) or {}
    tokens = sum(v for k, v in usage.items() if isinstance(v, int) and "token" in k.lower())
    with open(os.path.join(rundir, "timing.json"), "w", encoding="utf-8") as fh:
        json.dump({"total_tokens": tokens, "duration_ms": ms,
                   "total_duration_seconds": round(ms / 1000, 1)}, fh, indent=2)


def grade(validator_args, rundir):
    """Run a validator with --json into the run dir; return its summary dict."""
    out = os.path.join(rundir, "grading.json")
    txt = subprocess.run([sys.executable, *validator_args, "--json", out],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    with open(os.path.join(rundir, "grading.txt"), "w", encoding="utf-8") as fh:
        fh.write(txt.stdout + txt.stderr)
    try:
        return json.load(open(out, encoding="utf-8")).get("summary", {})
    except Exception:  # noqa: BLE001
        with open(out, "w", encoding="utf-8") as fh:
            json.dump({"summary": {"pass_rate": 0, "passed": 0, "failed": 0, "total": 0},
                       "expectations": [], "error": "grader produced no json"}, fh)
        return {"pass_rate": 0, "passed": 0, "failed": 0, "total": 0}


def log_status(sandbox):
    """status: value of the sole specs/*/DECISIONS.md under a sandbox, or ''.
    Reads the LAST status line in the frontmatter, not the first: a weak model
    that appends `status: COMPLETE` instead of editing the existing line would
    otherwise never be detected as done, wasting the rest of the turn budget.
    (The validator flags that duplicate as malformed at grade time.)"""
    hits = glob.glob(os.path.join(sandbox, "specs", "*", "DECISIONS.md"))
    if not hits:
        return ""
    txt = open(hits[0], encoding="utf-8").read()
    fm = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", txt)
    block = fm.group(1) if fm else txt
    matches = re.findall(r"^status:\s*(.+)$", block, re.M)
    return matches[-1].strip() if matches else ""


def find_log(sandbox):
    hits = glob.glob(os.path.join(sandbox, "specs", "*", "DECISIONS.md"))
    return hits[0] if hits else None


# --- populate slice ---------------------------------------------------------

def populate_prompt(config, spec_folder):
    if config == "with_skill":
        return (
            "Read .claude/skills/spec-design/SKILL.md and follow it EXACTLY. It routes by the "
            "DECISIONS.md frontmatter state; the decision log is COMPLETE, so you are in POPULATE "
            "mode. Follow every instruction it and the PROTOCOL.md files it references give you, "
            "including running the validator gate command and pasting the result.\n\n"
            f"Task: The decision log under specs/ is complete — write the spec. The output is "
            f"specs/{spec_folder}/SPEC.md. Write it with your file tools and verify by reading it back.\n\n"
            "There is NO human user available. When the protocol reaches a review step that waits "
            "for the user, print the review message and STOP — do not wait for input, do not invent "
            "user answers. Complete the task autonomously from the files on disk.")
    return (
        f"Read specs/{spec_folder}/DECISIONS.md and specs/GLOSSARY.md. Write a specification "
        f"document for implementers as specs/{spec_folder}/SPEC.md, derived from that decision log. "
        "Write it with your file tools and verify by reading it back. There is NO human user "
        "available — complete the task autonomously from the files on disk.")


def run_populate(fx, idx, config, trial, args, ws, sandbox_root):
    ename = f"eval-{idx}-{fx}"
    sandbox = os.path.join(sandbox_root, ename, config)
    rundir = os.path.join(ws, ename, config, f"run-{trial}")
    os.makedirs(os.path.join(sandbox, "specs"), exist_ok=True)
    os.makedirs(rundir, exist_ok=True)
    shutil.copytree(os.path.join(POPULATE_FIXTURES, fx, "specs"),
                    os.path.join(sandbox, "specs"), dirs_exist_ok=True)
    if config == "with_skill":
        copy_skills(sandbox)

    print(f">>> {ename} / {config} / trial {trial} ...")
    result = claude_json(populate_prompt(config, fx), sandbox, args.model)
    with open(os.path.join(rundir, "agent.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    write_timing(rundir, result)

    spec = os.path.join(sandbox, "specs", fx, "SPEC.md")
    log = os.path.join(sandbox, "specs", fx, "DECISIONS.md")
    if os.path.isfile(spec):
        shutil.copy(spec, os.path.join(rundir, "SPEC.md"))
        s = grade([POPULATE_VALIDATOR, log, spec, TEMPLATE,
                   os.path.join(POPULATE_FIXTURES, fx, "expected.json")], rundir)
        print(f"    {s.get('passed', 0)}/{s.get('total', 0)}")
    else:
        why = f"ERROR: {result.get('result', '')}" if result.get("is_error") else "no SPEC.md written"
        print(f"    {why}")
        with open(os.path.join(rundir, "grading.json"), "w", encoding="utf-8") as fh:
            json.dump({"summary": {"pass_rate": 0, "passed": 0, "failed": 0, "total": 0},
                       "expectations": [], "error": why}, fh)


# --- interview slice --------------------------------------------------------

def run_interview(fx, idx, args, ws, sandbox_root):
    ename = f"eval-{idx}-interview-{fx}"
    sandbox = os.path.join(sandbox_root, ename, "with_skill")
    rundir = os.path.join(ws, ename, "with_skill", "run-1")
    os.makedirs(os.path.join(sandbox, "specs"), exist_ok=True)
    os.makedirs(os.path.join(rundir, "turns"), exist_ok=True)
    copy_skills(sandbox)

    brief = open(os.path.join(INTERVIEW_FIXTURES, fx, "brief.md"), encoding="utf-8").read()
    open_prompt = (brief + "\n\nUse the spec-design skill to interview me. Follow it exactly: ONE "
                   "question per turn, each with a concrete labeled suggestion, saving DECISIONS.md "
                   "after every answer. Do not write the spec yet — just run the interview.")

    print(f">>> {ename} : opening the interview ...")
    turn = 1
    result = claude_json(open_prompt, sandbox, args.model)
    json.dump(result, open(os.path.join(rundir, "turns", "turn-1.json"), "w", encoding="utf-8"), indent=2)
    sid = result.get("session_id", "")
    if not sid:
        why = f"ERROR: {result.get('result', 'no session started')}"
        print(f"    {why}")
        with open(os.path.join(rundir, "grading.json"), "w", encoding="utf-8") as fh:
            json.dump({"summary": {"pass_rate": 0, "passed": 0, "failed": 0, "total": 0},
                       "expectations": [], "error": why}, fh)
        return

    status = log_status(sandbox)
    while status != "COMPLETE" and turn < args.max_turns:
        turn += 1
        r = claude_json(INTERVIEW_ANSWER, sandbox, args.model, resume=sid)
        json.dump(r, open(os.path.join(rundir, "turns", f"turn-{turn}.json"), "w", encoding="utf-8"), indent=2)
        status = log_status(sandbox)
        print(f"\r    turn {turn}  (log status: {status or 'none'})      ", end="", flush=True)
    print()

    with open(os.path.join(rundir, "interview.meta"), "w", encoding="utf-8") as fh:
        fh.write(f"turns_used={turn}\nfinal_status={status or 'none'}\nsession_id={sid}\n")

    log = find_log(sandbox)
    if log:
        shutil.copy(log, os.path.join(rundir, "DECISIONS.md"))
        s = grade([INTERVIEW_VALIDATOR, log, TEMPLATE,
                   os.path.join(INTERVIEW_FIXTURES, fx, "expected.json")], rundir)
        print(f"    {s.get('passed', 0)}/{s.get('total', 0)} after {turn} turns (status: {status or 'none'})")
    else:
        print(f"    NO DECISIONS.md produced after {turn} turns")
        with open(os.path.join(rundir, "grading.json"), "w", encoding="utf-8") as fh:
            json.dump({"summary": {"pass_rate": 0, "passed": 0, "failed": 0, "total": 0},
                       "expectations": [], "error": "no DECISIONS.md"}, fh)


# --- summary ----------------------------------------------------------------

def summarize(ws):
    def rate(pattern):
        rows = {}
        for g in glob.glob(os.path.join(ws, pattern, "*", "run-*", "grading.json")):
            parts = g.replace("\\", "/").split("/")
            ename, cfg = parts[-4], parts[-3]
            try:
                s = json.load(open(g, encoding="utf-8")).get("summary", {})
            except Exception:  # noqa: BLE001
                continue
            rows.setdefault((ename, cfg), []).append(s.get("pass_rate", 0))
        return rows

    pop = rate("eval-[0-9]*")
    pop = {k: v for k, v in pop.items() if "-interview-" not in k[0]}
    if pop:
        print("\n=== POPULATE (mean pass rate across trials) ===")
        print(f"{'eval':<44}{'with_skill':>12}{'without_skill':>16}")
        enames = sorted({e for e, _ in pop})
        allw, alln = [], []
        for e in enames:
            w = pop.get((e, "with_skill"), [])
            n = pop.get((e, "without_skill"), [])
            allw += w
            alln += n
            wm = f"{sum(w)/len(w)*100:5.1f}%" if w else "  n/a"
            nm = f"{sum(n)/len(n)*100:5.1f}%" if n else "  n/a"
            print(f"{e:<44}{wm:>12}{nm:>16}")
        if allw and alln:
            d = (sum(allw)/len(allw) - sum(alln)/len(alln)) * 100
            print("-" * 72)
            print(f"{'OVERALL':<44}{sum(allw)/len(allw)*100:11.1f}%{sum(alln)/len(alln)*100:15.1f}%")
            print(f"delta (with - without): {d:+.1f} points")

    iv = {k: v for k, v in rate("eval-*-interview-*").items()}
    if iv:
        print("\n=== INTERVIEW ===")
        for (e, _), rates in sorted(iv.items()):
            for g in glob.glob(os.path.join(ws, e, "with_skill", "run-*", "grading.json")):
                s = json.load(open(g, encoding="utf-8")).get("summary", {})
                print(f"{e:<48}{s.get('passed', 0)}/{s.get('total', 0)} checks   {s.get('pass_rate', 0)*100:5.1f}%")


# --- main -------------------------------------------------------------------

def discover(path):
    if not os.path.isdir(path):
        return []
    return sorted(d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)))


def next_iteration():
    base = os.path.join(REPO, "spec-design-workspace")
    n = 1
    while os.path.exists(os.path.join(base, f"iteration-{n}")):
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Run the spec-design evals with the claude CLI.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--mode", choices=["populate", "interview", "all"], default="all",
                    help="which slice(s) to run (default: all)")
    ap.add_argument("--model", default="haiku", help="model alias/id for --model (default: haiku)")
    ap.add_argument("--trials", type=int, default=1, help="populate trials per case (default: 1)")
    ap.add_argument("--max-turns", type=int, default=50, help="interview turn cap (default: 50)")
    ap.add_argument("--fixtures", nargs="+", metavar="NAME",
                    help="fixture names to run (default: all for the chosen mode)")
    ap.add_argument("--iteration", type=int, help="workspace iteration number (default: next unused)")
    ap.add_argument("--sandbox-root", help="where sandboxes go (default: a fresh temp dir, outside repo)")
    ap.add_argument("--keep-sandbox", action="store_true", help="keep sandboxes after the run")
    ap.add_argument("--list", action="store_true", help="list available fixtures and exit")
    args = ap.parse_args()

    pop_fx = discover(POPULATE_FIXTURES)
    iv_fx = discover(INTERVIEW_FIXTURES)
    if args.list:
        print("populate fixtures (evals/fixtures/populate-template/):")
        for f in pop_fx:
            print(f"  {f}")
        print("interview fixtures (evals/fixtures/interview-me/):")
        for f in iv_fx:
            print(f"  {f}")
        return

    do_pop = args.mode in ("populate", "all")
    do_iv = args.mode in ("interview", "all")
    if args.fixtures:
        pop_fx = [f for f in pop_fx if f in args.fixtures]
        iv_fx = [f for f in iv_fx if f in args.fixtures]

    iteration = args.iteration or next_iteration()
    ws = os.path.join(REPO, "spec-design-workspace", f"iteration-{iteration}")
    sandbox_root = args.sandbox_root or tempfile.mkdtemp(prefix="sdd-evals-")

    preflight(args.model)
    print(f"repo:      {REPO}")
    print(f"mode:      {args.mode}   model: {args.model}   trials: {args.trials}   max-turns: {args.max_turns}")
    print(f"fixtures:  populate={pop_fx if do_pop else '-'}  interview={iv_fx if do_iv else '-'}")
    print(f"workspace: {ws}")
    print(f"sandboxes: {sandbox_root}\n")

    started = time.time()
    try:
        if do_pop:
            for idx, fx in enumerate(pop_fx):
                for trial in range(1, args.trials + 1):
                    run_populate(fx, idx, "with_skill", trial, args, ws, sandbox_root)
                    run_populate(fx, idx, "without_skill", trial, args, ws, sandbox_root)
        if do_iv:
            for idx, fx in enumerate(iv_fx):
                run_interview(fx, idx, args, ws, sandbox_root)
    finally:
        if not args.keep_sandbox:
            shutil.rmtree(sandbox_root, ignore_errors=True)

    summarize(ws)
    print(f"\nGrades, specs, and transcripts under {ws}/")
    print(f"({time.time() - started:.0f}s total)")


if __name__ == "__main__":
    main()
