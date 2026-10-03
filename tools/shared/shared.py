"""The code shared by every level page, and the checks that keep it identical.

Level 1 (index.html) is the source. Every later level copies its shared parts
byte-for-byte and adds the backwards-compatible extensions marked LEVEL 2:
  - runtime_ext.py : the async _pfb_run (await, plots, theme-aware plot colours)
  - errors_ext.js  : friendly messages for errors first met in Level 2
  - extra.css      : CSS section 8 (callouts, exercise labels, static code, plots)
  - PATCHES below  : small, asserted edits to Level 1's page script

Used by level2/build.py (to build pages) and check_shared.py (to verify them).
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = "SHARED WITH LEVEL 1 — keep in sync"


def between(text, start, end):
    i = text.index(start) + len(start)
    return text[i:text.index(end, i)]


def patch(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"patch {label!r}: expected 1 match, found {count}"
    return text.replace(old, new)


def shared_head(l1, title, description):
    """Level 1's <head> up to <style>, with a new title and description."""
    head = l1[:l1.index("<style>")]
    head = re.sub(r"<title>.*?</title>", lambda m: f"<title>{title}</title>", head, count=1)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  lambda m: f'<meta name="description" content="{description}">', head, count=1)
    return patch(head, "<script>\n  /* Apply the saved theme",
                 "<script>\n  /* " + SHARED + " */\n  /* Apply the saved theme", "theme marker")


def shared_style(l1, level_note):
    """<style> block: Level 1's CSS sections 1-7 unchanged, then section 8 (extra.css)."""
    css = between(l1, "<style>\n", "</style>")
    extra = (HERE / "extra.css").read_text(encoding="utf-8")
    return ("<style>\n/* " + "=" * 74 + "\n   " + SHARED + ": sections 1–7 below are copied unchanged from\n"
            "   index.html. " + level_note + "\n   " + "=" * 74 + " */\n"
            + css + "/* ---------- END OF " + SHARED + " ---------- */\n\n" + extra + "</style>\n")


def shared_runtime(l1):
    """The py-runtime block (with its comment): Level 1's imports and _pfb_describe
    unchanged, then runtime_ext.py."""
    runtime = between(l1, '<script type="text/x-python" id="py-runtime">\n', "</script>")
    cut = runtime.index("\n\ndef _pfb_run(")
    runtime = ("# " + SHARED + " (imports and _pfb_describe are unchanged).\n"
               + runtime[:cut] + (HERE / "runtime_ext.py").read_text(encoding="utf-8"))
    rule = "<!-- " + "=" * 70 + "\n     PYTHON RUNTIME HELPER"
    comment = between(l1, rule, "-->")
    return rule + comment + "-->\n" + '<script type="text/x-python" id="py-runtime">\n' + runtime + "</script>\n"


def shared_script(l1, preload):
    """The page script (with its comment): Level 1's script plus the PATCHES.
    preload is this level's CONFIG.preload entries, as JavaScript text."""
    script = between(l1, "<script>\n(function () {", "</script>\n</body>")
    script = ("<script>\n/* " + SHARED + ". Lines marked LEVEL 2 are backwards-compatible\n"
              "   extensions; Level 1 can adopt this whole script unchanged. */\n(function () {" + script)
    for label, old, new in PATCHES:
        script = patch(script, old, new.replace("__PRELOAD__", preload), label)
    rule = "<!-- " + "=" * 70 + "\n     PAGE SCRIPT"
    comment = rule + between(l1, rule, "-->") + "-->\n"
    return comment + script + "</script>\n"


def normalise_preload(script):
    """Hide the level-specific CONFIG.preload list, so scripts of different levels can be compared."""
    return re.sub(r"preload: \[.*?\n    \],", "preload: [...],", script, count=1, flags=re.S)


PATCHES = [
    ("config", '''    packagesByImport: { Bio: "biopython" },
    // Start downloading a package when the learner scrolls to this section.
    preload: [{ selector: "#biopython", packages: ["biopython"] }],
    themeKey: "pfb-theme"''',
     '''    packagesByImport: { Bio: "biopython", pandas: "pandas", matplotlib: "matplotlib" },
    // Start downloading a package when the learner scrolls to this section.
    preload: __PRELOAD__,
    // LEVEL 2: a section must stay on screen this long before its packages load,
    // so jumping through the table of contents doesn't download everything.
    preloadDelayMs: 1200,
    // LEVEL 2: friendly names and rough download sizes for the loading messages.
    packageInfo: {
      biopython: { label: "Biopython", size: "about 5 MB" },
      pandas: { label: "pandas", size: "about 8 MB" },
      matplotlib: { label: "matplotlib", size: "about 9 MB" }
    },
    themeKey: "pfb-theme"'''),

    ("helpers", '''  function cleanCode(text) { return text.replace(/^\\s*\\n/, "").replace(/\\s+$/, ""); }''',
     '''  function cleanCode(text) { return text.replace(/^\\s*\\n/, "").replace(/\\s+$/, ""); }
  // LEVEL 2: helpers for package names and the current colour theme.
  function packageLabel(name) { return (CONFIG.packageInfo && CONFIG.packageInfo[name] || {}).label || (name === "biopython" ? "Biopython" : name); }
  function packageSize(name) { return (CONFIG.packageInfo && CONFIG.packageInfo[name] || {}).size || ""; }
  function joinWords(words) { return words.length < 2 ? words.join("") : words.slice(0, -1).join(", ") + " and " + words[words.length - 1]; }
  function currentTheme() {
    var set = document.documentElement.getAttribute("data-theme");
    if (set) return set;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }'''),

    ("statusText", '''    statusText: function () {
      var names = Object.keys(this.loadedPackages);
      return names.indexOf("biopython") !== -1 ? "ready + Biopython" : "ready";
    },''',
     '''    statusText: function () {
      // LEVEL 2: list every extra package that is loaded.
      var names = Object.keys(this.loadedPackages).map(packageLabel);
      return names.length ? "ready + " + names.join(", ") : "ready";
    },'''),

    ("loadPackage label", '''setStatus("loading", "loading " + (name === "biopython" ? "Biopython" : name) + "…");''',
     '''setStatus("loading", "loading " + packageLabel(name) + "…");   // LEVEL 2: packageLabel'''),

    ("run", '''    run: function (code, tests, onWait) {
      var self = this;
      var needed = this.packagesFor(code + "\\n" + (tests || ""));
      if (!this.pyodide || needed.some(function (n) { return !self.loadedPackages[n]; })) {
        if (onWait) onWait(needed.length && this.pyodide ? "Loading Biopython (first time only)…" : "Starting Python… your code will run as soon as it's ready.");
      }
      return this.start().then(function () {
        return Promise.all(needed.map(function (n) { return self.loadPackage(n); }));
      }).then(function () {
        self.writeFiles();
        var fn = self.pyodide.globals.get("_pfb_run");
        // Call without a second argument when there are no tests (Pyodide turns JS null into JsNull, not None).
        try { return JSON.parse(tests == null ? fn(code) : fn(code, tests)); }
        finally { fn.destroy(); }
      });
    }''',
     '''    queue: Promise.resolve(),   // LEVEL 2: code boxes run one at a time, in order
    run: function (code, tests, onWait) {
      var self = this;
      var needed = this.packagesFor(code + "\\n" + (tests || ""));
      var missing = needed.filter(function (n) { return !self.loadedPackages[n]; });   // LEVEL 2
      if (!this.pyodide || missing.length) {
        if (onWait) onWait(missing.length && this.pyodide
          ? "Loading " + joinWords(missing.map(packageLabel)) + " (first time only, " + joinWords(missing.map(packageSize)) + "). This can take a few seconds…"
          : "Starting Python… your code will run as soon as it's ready.");
      }
      var job = this.queue.then(function () { return self.start(); }).then(function () {
        return Promise.all(needed.map(function (n) { return self.loadPackage(n); }));
      }).then(function () {
        self.writeFiles();
        self.pyodide.globals.set("_pfb_theme", currentTheme());   // LEVEL 2: plot colours follow the theme
        var fn = self.pyodide.globals.get("_pfb_run");
        // Call without a second argument when there are no tests (Pyodide turns JS null into JsNull, not None).
        // LEVEL 2: _pfb_run is async (so code can use `await`), so the call gives back a promise.
        var pending;
        try { pending = tests == null ? fn(code) : fn(code, tests); }
        finally { fn.destroy(); }
        return Promise.resolve(pending);
      }).then(function (json) { return JSON.parse(json); });
      this.queue = job.catch(function () {});
      return job;
    }'''),

    ("show images", '''      if (result.output) {
        output.appendChild(el("pre", { text: result.output.replace(/\\n$/, "") }));
      } else if (!result.error) {
        output.appendChild(el("p", { class: "note", text: "(Your code ran without errors but didn't print anything. Use print() to show a result.)" }));
      }''',
     '''      var images = result.images || [];   // LEVEL 2: plots made with matplotlib
      if (result.output) {
        output.appendChild(el("pre", { text: result.output.replace(/\\n$/, "") }));
      } else if (!result.error && !images.length) {
        output.appendChild(el("p", { class: "note", text: "(Your code ran without errors but didn't print anything. Use print() to show a result.)" }));
      }
      images.forEach(function (img) { output.appendChild(el("img", { class: "plot", src: img.src, alt: img.alt })); });'''),

    ("file list", '''.join(" and ") + "."]]''', '''.join(", ") + "."]]   // LEVEL 2: comma list (more files)'''),

    ("module hint", '''      hints: [[/./, "Check the spelling and capitals: it's <code>from Bio.Seq import Seq</code> and <code>from Bio import SeqIO</code>."]]''',
     '''      hints: [
        [/'(pandas|matplotlib)/, "Check the spelling: it's <code>import pandas as pd</code> and <code>import matplotlib.pyplot as plt</code>, all lowercase."],   // LEVEL 2
        [/./, "Check the spelling and capitals: it's <code>from Bio.Seq import Seq</code> and <code>from Bio import SeqIO</code>."]
      ]'''),

    ("preload", '''      var obs = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) {
          obs.disconnect();
          p.packages.forEach(function (name) { Py.loadPackage(name); });
        }
      }, { rootMargin: "200px 0px" });''',
     '''      var timer = null;   // LEVEL 2: wait until the section has been on screen for a moment
      var obs = new IntersectionObserver(function (entries) {
        clearTimeout(timer);
        if (entries.some(function (e) { return e.isIntersecting; })) {
          timer = setTimeout(function () {
            obs.disconnect();
            p.packages.forEach(function (name) { Py.loadPackage(name); });
          }, CONFIG.preloadDelayMs || 0);
        }
      }, { rootMargin: CONFIG.preloadDelayMs ? "-35% 0px -35% 0px" : "200px 0px" });   // LEVEL 2: "reached" = crosses the middle of the screen'''),

    ("extra errors", '''  function escapeHtml(s) {''',
     (HERE / "errors_ext.js").read_text(encoding="utf-8") + '''
  function escapeHtml(s) {'''),
]
