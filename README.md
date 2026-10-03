# Python for Bioinformatics

A beginner-friendly, hands-on course that teaches Python using DNA, RNA and protein examples. Python runs in the learner's browser through [Pyodide](https://pyodide.org), so learners don't need to install anything. Each level is one self-contained HTML file.

| Level | File | What it covers |
|---|---|---|
| 1 · Easy | `index.html` | Python from zero: 11 lessons (0–10), 60 runnable examples, 27 exercises with automatic checks, a quiz per lesson and a glossary. |
| 2 · Intermediate | `intermediate.html` | For learners who finished Level 1: 14 lessons (0–13), 82 runnable examples, 44 exercises (12 optional 🌶️ challenges), 49 quiz questions and a glossary of 57 new terms. See **Level 2** below. |
| 3 · Advanced | (not written yet) | Shown as "Coming soon" in both pages. |

### How the levels link together

Both pages have the same **Course levels** list at the top of the sidebar. The current level is highlighted with a "You are here" badge (`aria-current="page"`), and the other levels are plain relative links (`index.html`, `intermediate.html`), so they work from disk, on a local server and on GitHub Pages. Level 2's Lesson 0 links back to the matching Level 1 lessons for a refresher, and Level 2's glossary links to Level 1's glossary for the basic terms. The light/dark choice is shared between the pages (see the end of this file).

## Open it on your computer

1. Double-click `index.html` (Level 1) or `intermediate.html` (Level 2), or drag it into Chrome, Edge, Firefox or Safari.
2. Wait a few seconds until the badge at the top says **Python ready**.

You need an internet connection, because Python is downloaded from the jsDelivr CDN the first time the page opens. After that, the browser usually caches it. Extra libraries are downloaded only when the learner reaches the lesson that needs them: Biopython in Level 1 Lesson 9, and Biopython, pandas and matplotlib in Level 2 (see below).

If your browser refuses to run the page from a file, serve the folder with a small local web server instead:

```bash
npx http-server -c-1 -p 8000
# then open http://localhost:8000
```

`python -m http.server 8000` works too.

## Publish it on GitHub Pages

1. Create a new repository on GitHub, for example `python-for-bioinformatics`.
2. Upload `index.html`, `intermediate.html`, `README.md` and the `audio/` folder to the repository's main branch, either through the website (**Add file → Upload files**) or with git:
   ```bash
   git init
   git add index.html intermediate.html README.md audio
   git commit -m "Add Level 1 course"
   git branch -M main
   git remote add origin https://github.com/<your-username>/python-for-bioinformatics.git
   git push -u origin main
   ```
3. On GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, then pick `main` and `/ (root)`, and click **Save**.
4. After a minute or two, the course is live at `https://<your-username>.github.io/python-for-bioinformatics/`.

No build step is needed.

## How the files are organised

Both level pages have the same structure:

| Part of the page | What it is |
|---|---|
| `<style>` section 1, **THEME TOKENS** | All colours, fonts and sizes, for light and dark mode. Edit only this block to restyle the course. |
| `<style>` sections 2–7 | Layout, code runner, exercises, quizzes and glossary styles. |
| Sidebar `.levels` list | The "Course levels" nav. Levels that exist are links; Advanced is marked "Coming soon". |
| `<section class="lesson" id="…">` | One lesson each. The sidebar links point to these ids. |
| `<script type="text/x-python" class="py-example">` | Becomes a runnable code box with Run and Reset buttons. |
| `<div class="exercise">` | Contains `py-starter`, `div.hints` (one `<p>` per hint), `py-solution` and `py-tests`. |
| `<div class="quiz-q">` | A question. Mark the right `<li>` with `data-correct` and put an explanation in `<span class="why">` in every option. |
| `<a class="term" href="#g-…">` | A glossary word. Its tooltip is built automatically from the matching `<dt id="g-…">` in the glossary. |
| `<script type="text/plain" class="data-file" data-filename="…">` | A file written into Python's virtual folder, so `open("sample.fasta")` works. |
| `<script id="py-runtime">` | A small Python helper that runs learner code, captures output and runs the checks. |
| Final `<script>` | The reusable page logic: Pyodide loader, code runner, friendly errors, exercises, quizzes, tooltips, theme toggle, mobile menu and table of contents. Settings such as the Pyodide version are in `CONFIG` at the top. |

### Writing "Check my answer" tests

Tests are ordinary Python that runs after the learner's code, in the same namespace. The test code can also use:

- `_output`: everything the learner's code printed
- `_source`: the learner's code as a string (for example, to re-run it with other inputs)

Use `assert condition, "a friendly nudge"`. If an assert fails, the learner sees its message. If all asserts pass, they see ✅.

Good practice, used throughout Level 2: re-run the learner's code with other inputs (`exec(re.sub(...), {})`) or call their functions with new values, so a hard-coded answer can't pass. If an exercise writes a file, delete that file in the test and re-run `_source` first, because files written by an earlier run (for example, by the solution) stay in the browser's virtual folder until the page is reloaded.

## Level 2 (`intermediate.html`)

Lessons: 0 Welcome back (with a warm-up quiz linking to Level 1), 1 Writing cleaner code, 2 When things go wrong, 3 Modules and imports, 4 Regular expressions, 5 FASTQ and quality scores, 6 Reading and writing files, 7–8 pandas, 9 matplotlib, 10 Biopython (SeqRecord, GenBank, translation tables, six-frame ORFs), 11 Sequence alignment, 12 Getting data from NCBI, 13 Capstone pipeline, then the glossary.

### Extra markup in Level 2

| Markup | What it is |
|---|---|
| `<span class="exercise-kind">` in an exercise's `<h4>` | The exercise type label: ✍️ Write it, 🐞 Fix the bug, 🔮 Predict, then run, 🧹 Make it cleaner. |
| `<span class="exercise-tag challenge">` | Marks an optional 🌶️ Challenge exercise. |
| `<div class="callout habit">` / `<div class="callout fact">` / `<div class="callout celebrate">` | 🧹 Good habit, 🤓 Did you know? and end-of-lesson celebration boxes. |
| `<div class="static-code">` | Code that is shown but not runnable ("💻 Run this on your own computer"), such as the `Bio.Entrez` example. |
| `<style>` section 8, **LEVEL 2 ADDITIONS** | The styles for the above. They only use theme tokens (plus four new ones defined in the same section), so they can move into a shared stylesheet unchanged. |

### Packages and download sizes

Level 2 uses the same Pyodide version as Level 1 (`v314.0.7`: Python 3.14, Biopython 1.87, pandas 3.0.2, matplotlib 3.10.8). Packages are downloaded only when needed:

| Package | First needed in | Download (including dependencies not yet loaded) |
|---|---|---|
| Biopython | Lesson 5 (and 10–13) | about 2.5 MB, plus about 2.9 MB for NumPy if it isn't loaded yet |
| pandas | Lesson 7 (and 8, 9, 13) | about 7.7 MB (pandas 4.1 MB, NumPy 2.9 MB, pytz and dateutil) |
| matplotlib | Lesson 9 (and 13) | about 9.3 MB (matplotlib 6.8 MB, Pillow, fontTools and others) |

A package starts downloading when its lesson has been on screen for 1.2 seconds (`preload` and `preloadDelayMs` in `CONFIG`), so jumping through the table of contents doesn't download everything. If the learner runs a box before that, the box waits and shows "Loading pandas (first time only, about 8 MB)…". The status badge at the top lists every package that is ready. The first matplotlib plot takes a few extra seconds while matplotlib sets up its fonts.

### Plots

matplotlib draws into memory (the `Agg` backend). After every run, the page's Python helper turns each open figure into a PNG image, shows it under the code box with an automatic `alt` text built from the figure's title and axis labels, and closes the figure. Plot colours follow the page's light or dark theme at the moment the code runs (a colour-blind-safe palette; `"C0"`, `"C1"`… pick colours from it). If the learner switches theme, re-running a box redraws its plot in the new colours.

### NCBI in the browser (Lesson 12)

Biopython's `Entrez` module uses Python's `urllib`, which can't make web requests inside Pyodide. So Lesson 12:

1. Shows the real `Bio.Entrez` code in a "💻 Run this on your own computer" box (not runnable). It uses a placeholder email (`your.name@example.org`) and reads the API key from an environment variable.
2. Runs a browser version with `pyodide.http.pyfetch`, through the small module `ncbi_helper.py` that is embedded in the page as a data file. NCBI's E-utilities send `Access-Control-Allow-Origin: *`, so the live request works from a local server, from GitHub Pages and from a file opened from disk. The helper waits at least 0.4 seconds between requests (NCBI allows 3 per second without an API key) and sends the tool name `pfb_course_level2`, but no email.
3. Falls back automatically if the request fails (offline, blocked network, rate limit or any HTTP error): it prints a friendly "📦 using the saved copy" message and reads `esearch_hbb.json` or `efetch_hbb.fasta`, real NCBI answers saved on 3 October 2026 and embedded in the page. The rest of the code runs exactly the same.

No exercise check depends on NCBI: the Lesson 12 exercises use the saved copies, so every check works offline once the packages are loaded.

### Level 2 data files

All are embedded in the page as `data-file` blocks and written into Python's virtual folder before each run (so even if a learner overwrites one, the next run gets the original back).

| File | Contents |
|---|---|
| `sample.fasta`, `genes.fasta` | Copied unchanged from Level 1 (real NCBI sequences). |
| `hbb.gb` | The real GenBank record NM_000518.5 (human HBB mRNA), trimmed to one reference and the main features (gene, exons, CDS, polyA signal) to keep the page small. |
| `efetch_hbb.fasta`, `esearch_hbb.json` | Saved NCBI E-utilities answers, used by Lessons 4 and 12 and as the Lesson 12 fallback. |
| `reads.fastq` (6 reads × 40 bases), `run42.fastq` (40 reads × 75 bases) | **Made-up teaching data**: real fragments of HBB, INS, GAPDH and TP53 with simulated Illumina-like Phred+33 qualities that fall towards the 3′ end, about 20% poor reads, and a few `N`s and errors at low-quality positions. Generated with a fixed random seed. |
| `expression.csv`, `annotation.tsv` | **Made-up teaching data**: TPM values for 15 real genes in a "DNA-damage" experiment (p53 targets up, cell-cycle genes down, housekeeping genes steady), with one missing value (FAS) and one gene missing from the annotation (TP53I3) on purpose. |
| `seqtools.py`, `ncbi_helper.py` | Small Python modules that lessons import: the Level 1 toolkit plus FASTA/FASTQ readers, and the NCBI fetch helper with its fallback. |

Other real sequences are typed into the lessons with their accession numbers: mouse beta-globin (NM_001201391.1) in Lesson 11, and the HBB, INS, TP53 and GAPDH sequences from Level 1.

### Code shared with Level 1

The CSS sections 1–7, the Python helper (`py-runtime`) and the page script were copied from `index.html` and are marked `SHARED WITH LEVEL 1 — keep in sync`. Level 2 needed a few additions, each marked `LEVEL 2` in the code. They are backwards compatible, so Level 1 can adopt Level 2's versions unchanged when the code is moved into shared `course.css` / `course.js` files:

- `_pfb_run` is `async`, so learner code can use `await` (needed for `pyfetch`); it also returns plot images, and resets matplotlib's style before each run.
- Python modules in the page's folder are re-imported fresh on every run.
- Code boxes run one at a time, in order (an awaiting box can't mix its output with another box's).
- `CONFIG` gained `packageInfo` (names and sizes for loading messages), `preloadDelayMs` and more `preload` entries; the status badge lists every loaded package.
- Friendly error messages for regex mistakes (`PatternError`), `StatisticsError`, `OSError` and `UnicodeDecodeError`, and extra hints for `KeyError` (pandas columns), `ValueError` (your own `raise`) and `AssertionError`.

Neither level has voice-over slots yet (see **Voice-overs** below).

### Building and testing

`intermediate.html` is generated from the sources in `tools/level2/` (`python tools/level2/build.py`), and the `tools/` folder has scripts to check that the shared code is identical in every page, run every example and exercise check in normal Python, and run the browser tests. See `tools/README.md`.

## Voice-overs

Voice-overs are planned; the empty `audio/` folder is reserved for them.

## Add Level 3 (Advanced)

1. Copy `intermediate.html` to `advanced.html` in the same folder. Keep the parts marked `SHARED WITH LEVEL 1 — keep in sync` exactly as they are.
2. In the new file, change the `<title>`, the `brand-level` text and the hero heading; replace the lesson `<section>`s, the sidebar table of contents, the glossary entries and the `data-file` blocks; and in the **Course levels** list, move `aria-current="page"` and the "You are here" badge to Level 3.
3. In **every** level file, turn the "Coming soon" entry into a link: `<li><a href="advanced.html">Level 3 · Advanced</a></li>`.
4. Use the scripts in `tools/` to check that the shared code is still identical and to test every example and exercise (see `tools/README.md`). If copying the shared code becomes tedious, move it into shared `course.css` and `course.js` files and link them from each page; GitHub Pages serves them without any changes.

The theme is saved in `localStorage` under `pfb-theme`, so a learner's light or dark choice carries over between level pages on the same site.

## Content notes

- All sequences are real human RefSeq sequences from NCBI: HBB (NM_000518.5), INS (NM_000207.3), TP53 (NM_000546.6) and GAPDH (NM_002046.7). They are written 5′→3′.
- The codon table used in the lessons follows the standard genetic code (NCBI translation table 1).
- The page uses Pyodide v314.0.7 (Python 3.14, Biopython 1.87). To upgrade, change `pyodideVersion` in `CONFIG`, then re-test the Biopython lesson.
