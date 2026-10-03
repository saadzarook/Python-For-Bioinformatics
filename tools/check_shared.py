"""Check that the shared code is identical in every level page.

    python tools/check_shared.py                      # checks intermediate.html (and advanced.html if it exists)
    python tools/check_shared.py intermediate.html advanced.html

Level 1 (index.html) is the source. For every later page, this script rebuilds the
shared parts from index.html plus tools/shared/ (exactly as the build does) and checks
that the page contains them unchanged:
  1. the <head> shared block: the theme script and the inline favicon
  2. CSS sections 1-7 (Level 1's whole stylesheet) and section 8 (tools/shared/extra.css)
  3. the Python runtime (py-runtime)
  4. the page script (its CONFIG.preload list is level-specific, so it isn't compared)
It also checks that index.html itself still has the favicon and the shared theme script.
Exits with status 1 if anything differs.
"""
import difflib
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS / "shared"))
from shared import SHARED, normalise_preload, shared_head, shared_runtime, shared_script, shared_style  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def head_block(head):
    """From the color-scheme meta tag to the end of the theme script (title and description excluded)."""
    start = head.index('<meta name="color-scheme"')
    return head[start:head.index("</script>", start) + len("</script>")]


def style_block(page):
    return page[page.index("<style>"):page.index("</style>") + len("</style>\n")]


def runtime_block(page):
    start = page.index("<!-- " + "=" * 70 + "\n     PYTHON RUNTIME HELPER")
    return page[start:page.index("</script>", start) + len("</script>\n")]


def script_block(page):
    start = page.index("<!-- " + "=" * 70 + "\n     PAGE SCRIPT")
    return page[start:page.rindex("</script>") + len("</script>\n")]


def compare(name, expected, actual):
    if expected == actual:
        print(f"  OK    {name}")
        return True
    print(f"  DIFF  {name}:")
    diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(), "expected (from index.html + tools/shared)", "page", lineterm="", n=1)
    for line in list(diff)[:40]:
        print("        " + line)
    return False


def main(pages):
    l1 = (REPO / "index.html").read_text(encoding="utf-8")
    ok = True
    print("index.html (Level 1, the source)")
    l1_head = l1[:l1.index("<style>")]
    ok &= compare("favicon present", True, 'rel="icon" href="data:image/svg+xml' in l1_head)
    expected_head = head_block(shared_head(l1, "x", "x"))
    expected_style = shared_style(l1, "")
    expected_runtime = shared_runtime(l1)
    expected_script = normalise_preload(shared_script(l1, "[\n    ]"))
    for name in pages:
        path = REPO / name
        if not path.exists():
            continue
        page = path.read_text(encoding="utf-8")
        print(name)
        ok &= compare("head: theme script + favicon", expected_head, head_block(page[:page.index("<style>")]))
        # The note in the CSS header comment names the level, so compare everything after it.
        css_start = lambda s: s[s.index(SHARED + ": sections 1–7"):]
        exp_css, act_css = css_start(expected_style), css_start(style_block(page))
        exp_css, act_css = exp_css[exp_css.index("*/"):], act_css[act_css.index("*/"):]
        ok &= compare("CSS sections 1-8", exp_css, act_css)
        ok &= compare("Python runtime", expected_runtime, runtime_block(page))
        ok &= compare("page script (CONFIG.preload ignored)", expected_script, normalise_preload(script_block(page)))
    print("\nAll shared code is identical." if ok else "\nShared code differs (see DIFF above).")
    return ok


if __name__ == "__main__":
    pages = sys.argv[1:] or ["intermediate.html", "advanced.html"]
    sys.exit(0 if main(pages) else 1)
