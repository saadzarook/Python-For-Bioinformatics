"""Extra real-browser checks for Level 2: lazy package loading, table-of-contents jumps,
the NCBI live call and its saved-copy fallback, 375 px mobile layout and menu, the level
nav in both directions, theme carry-over, and screenshots (written to tools/output/shots/).

usage (from the repository folder, with a local server running in it):
    npx http-server -c-1 -p 8000
    python tools/browser_checks_level2.py http://localhost:8000
Exit status 1 if any check fails. For Level 3, copy this file and change the lesson ids.
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")   # the folder's URL
SHOTS = Path(__file__).resolve().parent / "output" / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)
results = []


def log(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" | {detail}" if detail else ""), flush=True)


def wheels(reqs):
    return sorted({u.rsplit("/", 1)[-1].split("-")[0] for u in reqs if u.endswith(".whl")})


def wait_runner(runner, timeout=180):
    btn = runner.locator(".runner-bar .btn-primary")
    t0 = time.time()
    time.sleep(0.3)
    while time.time() - t0 < timeout:
        if btn.is_enabled() and "Running" not in btn.inner_text():
            return
        time.sleep(0.2)
    raise TimeoutError


def run_box(page, section, index=0):
    runner = page.locator(f"#{section} .runner").nth(index)
    runner.scroll_into_view_if_needed()
    runner.locator(".runner-bar .btn-primary").click()
    wait_runner(runner)
    out = runner.locator(".output")
    return out.inner_text()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")

    # ---------- 1. lazy loading while scrolling ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    reqs, console = [], []
    page.on("request", lambda r: reqs.append(r.url))
    page.on("console", lambda m: console.append((m.type, m.text)))
    page.on("pageerror", lambda e: console.append(("pageerror", str(e))))
    page.goto(BASE + "/intermediate.html")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    page.wait_for_timeout(2000)
    log("no packages at start", wheels(reqs) == [], str(wheels(reqs)))
    for section, expect_new in [("regex", []), ("fastq", ["biopython"]), ("files", []),
                                ("pandas-1", ["pandas"]), ("plotting", ["matplotlib"])]:
        before = set(wheels(reqs))
        page.evaluate(f"document.getElementById('{section}').scrollIntoView({{behavior: 'instant'}})")
        page.wait_for_timeout(1600)       # longer than the 1.2 s dwell time (wait_for_timeout keeps events flowing)
        t0 = time.time()
        while time.time() - t0 < 60 and expect_new and not set(expect_new) <= set(wheels(reqs)):
            page.wait_for_timeout(500)
        page.wait_for_timeout(1000)
        new = sorted(set(wheels(reqs)) - before)
        ok = all(e in new for e in expect_new) and (expect_new or not new)
        log(f"scroll to #{section} loads {expect_new or 'nothing'}", ok, f"new wheels: {new}")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    log("status badge lists packages", "pandas" in page.locator("#py-status").inner_text(), page.locator("#py-status").inner_text())
    ctx.close()

    # ---------- 2. TOC jump past lessons doesn't download their packages ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    reqs = []
    page.on("request", lambda r: reqs.append(r.url))
    page.goto(BASE + "/intermediate.html")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    page.locator('.toc a[href="#files"]').click()       # smooth scroll passes Lesson 5 (Biopython)
    page.wait_for_timeout(5000)
    log("TOC jump to Lesson 6 skips Lesson 5's Biopython", "biopython" not in wheels(reqs), str(wheels(reqs)))
    ctx.close()

    # ---------- 3. NCBI: live, then blocked (fallback) ----------
    for blocked in [False, True]:
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        errs = []
        page.on("console", lambda m: errs.append((m.type, m.text)) if m.type == "error" else None)
        if blocked:
            page.route("**/eutils.ncbi.nlm.nih.gov/**", lambda route: route.abort())
        page.goto(BASE + "/intermediate.html#ncbi")
        page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
        texts = [run_box(page, "ncbi", i) for i in (1, 2)]
        if blocked:
            ok = all("📦" in t and "saved copy" in t and "🐞" not in t for t in texts) and "628 bases" in texts[1]
            log("NCBI blocked -> saved copy used, no error", ok, texts[0][:160].replace("\n", " / "))
        else:
            ok = all("🌐 Live answer from NCBI" in t for t in texts) and "628 bases" in texts[1]
            log("NCBI live call works", ok, texts[0][:160].replace("\n", " / "))
        # With NCBI blocked, Chrome itself logs net::ERR_FAILED for the blocked request: that's expected.
        errs = [e for e in errs if not (blocked and "ERR_FAILED" in e[1])]
        log(f"NCBI ({'blocked' if blocked else 'live'}) console errors from the page", not errs, str(errs)[:300])
        ctx.close()

    # ---------- 4. mobile 375 px: no sideways scroll, menu works ----------
    for theme in ["light", "dark"]:
        ctx = browser.new_context(viewport={"width": 375, "height": 760}, color_scheme=theme, device_scale_factor=2, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(BASE + "/intermediate.html")
        page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
        # run a plot box and a wide-table box so their output is part of the layout
        run_box(page, "plotting", 3)
        run_box(page, "pandas-2", 3)
        sw = page.evaluate("document.documentElement.scrollWidth")
        wide = page.evaluate("""() => {
            const out = [];
            for (const el of document.querySelectorAll('body *')) {
                const r = el.getBoundingClientRect();
                if (r.right > window.innerWidth + 1 && r.width > 0) {
                    let p = el.parentElement, clipped = false;
                    while (p) { const s = getComputedStyle(p); if (['auto','scroll','hidden'].includes(s.overflowX) || s.visibility === 'hidden') { clipped = true; break; } p = p.parentElement; }
                    if (!clipped) out.push(el.tagName + '.' + el.className + ' ' + Math.round(r.right));
                }
            }
            return out.slice(0, 10);
        }""")
        log(f"375px ({theme}): no sideways scrolling", sw <= 375 and not wide, f"scrollWidth={sw} overflow={wide}")
        page.locator("#plotting .runner").nth(3).screenshot(path=str(SHOTS / f"mobile_plot_{theme}.png"))
        page.evaluate("window.scrollTo(0, 0)")
        page.locator("#menu-btn").click()
        page.wait_for_timeout(400)
        visible = page.locator("#sidebar").evaluate("el => getComputedStyle(el).visibility === 'visible' && el.getBoundingClientRect().left >= 0")
        page.screenshot(path=str(SHOTS / f"mobile_menu_{theme}.png"))
        page.locator('.toc a[href="#alignment"]').click()
        page.wait_for_timeout(1500)
        closed = not page.evaluate("document.body.classList.contains('menu-open')")
        at = page.evaluate("Math.abs(document.getElementById('alignment').getBoundingClientRect().top) < 200")
        log(f"375px ({theme}): menu opens, TOC link closes it and jumps", visible and closed and at, f"visible={visible} closed={closed} at={at}")
        ctx.close()

    # ---------- 5. level nav both ways, Level 1 unchanged otherwise ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto(BASE + "/intermediate.html")
    current = page.locator('.levels a[aria-current="page"]').inner_text()
    log("Level 2 nav highlights Level 2", "Level 2" in current, current)
    page.locator('.levels a[href="index.html"]').click()
    page.wait_for_load_state()
    log("Level 2 -> Level 1 link", page.url.endswith("/index.html"), page.url)
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    l2link = page.locator('.levels a[href="intermediate.html"]')
    log("Level 1 shows Level 2 as a link", l2link.count() == 1 and "Coming soon" not in l2link.inner_text(), l2link.inner_text())
    log("Level 1 still highlights Level 1", "Level 1" in page.locator('.levels a[aria-current="page"]').inner_text())
    l2link.click()
    page.wait_for_load_state()
    log("Level 1 -> Level 2 link", page.url.endswith("/intermediate.html"), page.url)
    ctx.close()

    # ---------- 6. theme toggle carries over between levels; screenshots ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, color_scheme="light")
    page = ctx.new_page()
    page.goto(BASE + "/intermediate.html")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    page.locator("#theme-btn").click()
    log("theme toggle sets dark", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark")
    page.goto(BASE + "/index.html")
    log("dark theme carries over to Level 1", page.evaluate("document.documentElement.getAttribute('data-theme')") == "dark")
    page.goto(BASE + "/intermediate.html#plotting")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    run_box(page, "plotting", 2)
    page.locator("#plotting .runner").nth(2).screenshot(path=str(SHOTS / "desktop_plot_dark.png"))
    page.locator("#theme-btn").click()
    run_box(page, "plotting", 2)
    page.locator("#plotting .runner").nth(2).screenshot(path=str(SHOTS / "desktop_plot_light.png"))
    page.goto(BASE + "/intermediate.html#welcome-back")
    page.wait_for_timeout(1000)
    page.screenshot(path=str(SHOTS / "desktop_top_light.png"))
    page.goto(BASE + "/intermediate.html#errors")
    page.wait_for_selector("#py-status[data-state=ready]", timeout=120000)
    run_box(page, "errors", 0)
    page.locator("#errors .runner").nth(0).screenshot(path=str(SHOTS / "error_box.png"))
    ctx.close()
    browser.close()

print()
print(f"{sum(ok for _, ok, _ in results)}/{len(results)} checks passed")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
