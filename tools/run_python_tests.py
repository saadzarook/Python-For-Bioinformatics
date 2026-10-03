"""Run every example and exercise of intermediate.html in normal CPython.

Uses the page's own runtime (_pfb_run) and data files, so results match the
browser as closely as possible. Code that needs Pyodide (await / pyfetch) is
skipped here and tested in the browser instead.

usage (from the repository folder):
    python tools/run_python_tests.py                       # intermediate.html, all lessons
    python tools/run_python_tests.py index.html            # Level 1
    python tools/run_python_tests.py intermediate.html regex fastq   # only some lessons
Needs: pip install pandas matplotlib biopython (the same versions as the page's Pyodide, see tools/README.md).
The report (all outputs) is written to tools/output/. Exit status 1 if anything fails.
"""
import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
ARGS = sys.argv[1:]
PAGE_NAME = ARGS.pop(0) if ARGS and ARGS[0].endswith(".html") else "intermediate.html"
PAGE_PATH = Path(PAGE_NAME) if Path(PAGE_NAME).exists() else REPO / PAGE_NAME
PAGE = PAGE_PATH.read_text(encoding="utf-8")
ONLY = set(ARGS)
EXPECTED = json.loads((TOOLS / "expected_errors.json").read_text(encoding="utf-8")).get(PAGE_PATH.name, [])
expected_left = [(e["section"], e["error"]) for e in EXPECTED]
(TOOLS / "output").mkdir(exist_ok=True)
OUT = TOOLS / "output" / f"python_report_{PAGE_PATH.stem}.txt"


def clean(code):
    return re.sub(r"^\s*\n", "", code, count=1).rstrip()


data = {m.group(1): m.group(2).lstrip("\n") if False else re.sub(r"^\n", "", m.group(2))
        for m in re.finditer(r'<script type="text/plain" class="data-file" data-filename="([^"]+)">(.*?)</script>', PAGE, re.S)}
runtime = re.search(r'<script type="text/x-python" id="py-runtime">\n(.*?)</script>', PAGE, re.S).group(1)

workdir = Path(tempfile.mkdtemp(prefix="pfb_"))
os.chdir(workdir)


def write_files():
    for name, text in data.items():
        (workdir / name).write_text(text, encoding="utf-8")


ns = {}
exec(runtime, ns)


def run(code, tests=None):
    write_files()
    result = ns["_pfb_run"](code, tests)       # Level 2+ runtime is async; Level 1's is not
    if asyncio.iscoroutine(result):
        result = asyncio.run(result)
    return json.loads(result)


sections = re.split(r'(?=<section class="lesson[^"]*" id=")', PAGE)
lines, problems = [], []
n_examples = n_ex = 0
for sec in sections:
    m = re.match(r'<section class="lesson[^"]*" id="([^"]+)"', sec)
    if not m:
        continue
    sid = m.group(1)
    if ONLY and sid not in ONLY:
        continue
    # examples (outside exercises)
    no_ex = re.sub(r'<div class="exercise".*?<script type="text/x-python" class="py-tests">.*?</script>', "", sec, flags=re.S)
    for code in re.findall(r'<script type="text/x-python" class="py-example">(.*?)</script>', no_ex, re.S):
        code = clean(code)
        n_examples += 1
        head = code.splitlines()[0][:70]
        if "await " in code or "pyodide" in code:
            lines.append(f"## [{sid}] SKIPPED (browser only): {head}")
            continue
        r = run(code)
        lines.append(f"## [{sid}] {head}\n{r['output']}" + (f"\n!! ERROR: {r['error']['message']} (line {r['error']['line']})" if r["error"] else "")
                     + (f"\n[images: {[i['alt'] for i in r['images']]}]" if r.get("images") else ""))
        if r["error"]:
            if (sid, r["error"]["type"]) in expected_left:
                expected_left.remove((sid, r["error"]["type"]))     # a deliberate error demo
            else:
                problems.append(f"example error in {sid}: {head} -> {r['error']['message']}")
    # exercises
    for ex in re.findall(r'<div class="exercise"(.*?<script type="text/x-python" class="py-tests">.*?</script>)', sec, re.S):
        n_ex += 1
        title = re.sub(r"<[^>]+>", " ", re.search(r"<h4>(.*?)</h4>", ex, re.S).group(1))
        title = re.sub(r"\s+", " ", title).strip()
        starter = clean(re.search(r'class="py-starter">(.*?)</script>', ex, re.S).group(1))
        solution = clean(re.search(r'class="py-solution">(.*?)</script>', ex, re.S).group(1))
        tests = clean(re.search(r'class="py-tests">(.*?)</script>', ex, re.S).group(1))
        if "await " in solution:
            lines.append(f"## EXERCISE [{sid}] {title}: SKIPPED (browser only)")
            continue
        rs = run(starter, tests)
        rsol = run(solution, tests)
        s_ok = not (rs["check"] and rs["check"]["passed"])
        sol_ok = bool(rsol["check"] and rsol["check"]["passed"])
        lines.append(f"## EXERCISE [{sid}] {title}\n-- starter: {'error ' + rs['error']['message'] if rs['error'] else rs['check']}\n-- solution output:\n{rsol['output']}\n-- solution check: {rsol['check']} {rsol['error']}")
        rs2 = run(starter, tests)   # again, AFTER the solution ran (files it wrote still exist)
        if rs2["check"] and rs2["check"]["passed"]:
            problems.append(f"STARTER PASSES AFTER SOLUTION RAN: {sid} {title}")
        if not s_ok:
            problems.append(f"STARTER PASSES: {sid} {title}")
        if not sol_ok:
            problems.append(f"SOLUTION FAILS: {sid} {title}: {rsol['check']} {rsol['error']}")

OUT.write_text("\n\n".join(lines), encoding="utf-8")
print(f"{PAGE_PATH.name}: examples: {n_examples}, exercises: {n_ex}, report: {OUT.relative_to(REPO)}")
print("problems:" if problems else "no problems")
for p in problems:
    print("  ", p)
sys.exit(1 if problems else 0)
