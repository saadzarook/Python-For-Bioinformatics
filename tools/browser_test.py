"""Drive a level page in real Chrome: run every example, check every exercise.

usage (from the repository folder):
    python tools/browser_test.py intermediate.html                 # opened from disk (file://)
    python tools/browser_test.py http://localhost:8000/index.html  # from a local server
    options: --theme dark   --offline-ncbi (block NCBI to test the saved-copy fallback)
For every exercise, the untouched starter must fail its check and the solution must pass.
Writes a JSON report to tools/output/ and prints a summary. Exit status 1 on any failure.
Needs: pip install playwright, and Google Chrome installed (or change channel="chrome").
"""
import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
TARGET = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "intermediate.html"
if TARGET.startswith(("http://", "https://", "file://")):
    URL = TARGET
else:
    URL = (Path(TARGET) if Path(TARGET).exists() else REPO / TARGET).resolve().as_uri()
PAGE_NAME = URL.rsplit("/", 1)[-1].split("#")[0].split("?")[0]
EXPECTED = json.loads((TOOLS / "expected_errors.json").read_text(encoding="utf-8")).get(PAGE_NAME, [])
THEME = "dark" if "--theme" in sys.argv and sys.argv[sys.argv.index("--theme") + 1] == "dark" else "light"
BLOCK_NCBI = "--offline-ncbi" in sys.argv
(TOOLS / "output").mkdir(exist_ok=True)
OUT = TOOLS / "output" / f"browser_{Path(PAGE_NAME).stem}_{THEME}{'_offline' if BLOCK_NCBI else ''}.json"

console, page_errors, requests = [], [], []


def wait_idle(page, runner, timeout=180):
    """Wait until the runner's Run button is enabled again."""
    btn = runner.locator(".runner-bar .btn-primary")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if btn.is_enabled() and "Running" not in btn.inner_text():
            return
        time.sleep(0.15)
    raise TimeoutError("runner did not finish")


def read_output(runner):
    out = runner.locator(".output")
    return {
        "text": out.locator("pre").first.inner_text() if out.locator("pre").count() else "",
        "error": out.locator(".error-box").first.inner_text() if out.locator(".error-box").count() else None,
        "check": (out.locator(".check-box").first.get_attribute("class"), out.locator(".check-box").first.inner_text())
                 if out.locator(".check-box").count() else None,
        "images": [img.get_attribute("alt") for img in out.locator("img.plot").all()],
        "note": out.locator(".note").first.inner_text() if out.locator(".note").count() else "",
    }


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(color_scheme=THEME, viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("request", lambda r: requests.append(r.url))
    if BLOCK_NCBI:
        page.route("**/eutils.ncbi.nlm.nih.gov/**", lambda route: route.abort())
    page.goto(URL)
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    status_at_start = page.locator("#py-status").inner_text()
    report = {"url": URL, "theme": THEME, "examples": [], "exercises": []}

    # 1. every example box
    examples = page.locator("section.lesson > .runner, section.lesson .callout .runner, section.lesson div:not(.exercise):not(.solution-wrap) > .runner")
    seen = set()
    all_runners = page.locator(".runner")
    for i in range(all_runners.count()):
        r = all_runners.nth(i)
        if r.evaluate("n => !!n.closest('.exercise')"):
            continue
        r.scroll_into_view_if_needed()
        section = r.evaluate("n => n.closest('section') ? n.closest('section').id : ''")
        code = r.locator("textarea").input_value()
        r.locator(".runner-bar .btn-primary").click()
        time.sleep(0.2)
        wait_idle(page, r)
        res = read_output(r)
        res.update({"index": i, "section": section, "code_head": code.splitlines()[0][:70] if code else ""})
        report["examples"].append(res)

    # 2. every exercise: untouched starter must fail, solution must pass
    exs = page.locator(".exercise")
    for i in range(exs.count()):
        ex = exs.nth(i)
        ex.scroll_into_view_if_needed()
        title = ex.locator("h4").first.inner_text()
        item = {"title": title}
        check_btn = ex.locator(".exercise-actions .btn-check")
        starter = ex.locator(".runner").first
        if check_btn.count():
            check_btn.click(); time.sleep(0.2); wait_idle(page, starter)
            item["starter"] = read_output(starter)
        ex.locator(".exercise-actions button", has_text="Show solution").click()
        sol = ex.locator(".solution-wrap .runner")
        sol_check = ex.locator(".solution-wrap .btn-check")
        if sol_check.count():
            sol_check.click()
        else:
            sol.locator(".runner-bar .btn-primary").click()
        time.sleep(0.2); wait_idle(page, sol)
        item["solution"] = read_output(sol)
        report["exercises"].append(item)

    report["status_end"] = page.locator("#py-status").inner_text()
    report["status_start"] = status_at_start
    report["console"] = console
    report["page_errors"] = page_errors
    report["ncbi_requests"] = [u for u in requests if "ncbi" in u]
    report["package_requests"] = [u.rsplit("/", 1)[-1] for u in requests if u.endswith(".whl")]
    OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    browser.close()

# summary
failures = 0
expected_left = [(e["section"], e["error"]) for e in EXPECTED]
bad_examples = [e for e in report["examples"] if e["error"]]
print(f"{PAGE_NAME} ({THEME}): examples: {len(report['examples'])}, with error box: {len(bad_examples)}")
for e in bad_examples:
    found = re.search(r"\b(\w+(?:Error|Exception))\b", e["error"])
    key = (e["section"], found.group(1) if found else "?")
    if key in expected_left:
        expected_left.remove(key)
        print("  expected error (deliberate demo):", e["section"], key[1])
    else:
        failures += 1
        print("  ERR", e["section"], e["index"], e["code_head"], "|", (e["error"] or "").splitlines()[:3])
for x in report["exercises"]:
    s = x.get("starter", {}).get("check")
    sol = x["solution"].get("check")
    ok_sol = sol and "pass" in sol[0]
    ok_start = (s is None) or ("pass" not in s[0])
    flag = "OK " if ok_sol and ok_start else "BAD"
    failures += flag == "BAD"
    print(f"  {flag} {x['title'][:60]} | starter: {s[0] if s else '-'} | solution: {sol[0] if sol else x['solution'].get('error')}")
# The browser's own favicon 404 and blocked NCBI requests (with --offline-ncbi) aren't page errors.
page_console = [c for c in console if c["type"] == "error" and not ("404" in c["text"] and "favicon" in c["text"])
                and not (BLOCK_NCBI and "ERR_FAILED" in c["text"])]
failures += len(page_console) + len(page_errors)
print("console errors:", page_console)
print("console warnings:", [c["text"][:120] for c in console if c["type"] == "warning"])
print("page errors:", page_errors)
print("ncbi requests:", report["ncbi_requests"])
print("packages:", report["package_requests"])
print("status:", report["status_start"], "->", report["status_end"])
print("RESULT:", "all passed" if failures == 0 else f"{failures} failure(s)")
sys.exit(1 if failures else 0)
