# Python for Bioinformatics: Level 1 (Easy)

A beginner-friendly, hands-on course that teaches Python from zero using DNA, RNA and protein examples. It has 11 lessons (0–10), 60 runnable examples, 27 exercises with automatic checks, a quiz for each lesson and a glossary.

Everything is in one file, `index.html`. Python runs in the learner's browser through [Pyodide](https://pyodide.org), so learners don't need to install anything.

## Open it on your computer

1. Double-click `index.html`, or drag it into Chrome, Edge, Firefox or Safari.
2. Wait a few seconds until the badge at the top says **Python ready**.

You need an internet connection, because Python is downloaded from the jsDelivr CDN the first time the page opens. After that, the browser usually caches it. Biopython (a few MB) is downloaded only when the learner scrolls to Lesson 9.

If your browser refuses to run the page from a file, serve the folder with a small local web server instead:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Publish it on GitHub Pages

1. Create a new repository on GitHub, for example `python-for-bioinformatics`.
2. Upload `index.html` and `README.md` to the repository's main branch, either through the website (**Add file → Upload files**) or with git:
   ```bash
   git init
   git add index.html README.md
   git commit -m "Add Level 1 course"
   git branch -M main
   git remote add origin https://github.com/<your-username>/python-for-bioinformatics.git
   git push -u origin main
   ```
3. On GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, then pick `main` and `/ (root)`, and click **Save**.
4. After a minute or two, the course is live at `https://<your-username>.github.io/python-for-bioinformatics/`.

No build step is needed.

## How the file is organised

| Part of `index.html` | What it is |
|---|---|
| `<style>` section 1, **THEME TOKENS** | All colours, fonts and sizes, for light and dark mode. Edit only this block to restyle the course. |
| `<style>` sections 2–7 | Layout, code runner, exercises, quizzes and glossary styles. |
| Sidebar `.levels` list | The "Course levels" nav (Intermediate and Advanced are marked "Coming soon"). |
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

## Add the Intermediate and Advanced levels

1. Copy `index.html` to `intermediate.html` (and later `advanced.html`) in the same folder.
2. In the new file:
   - Change the `<title>`, the `brand-level` text in the header and the hero heading.
   - Replace the lesson `<section>`s, the sidebar table of contents, the glossary entries and the `data-file` blocks with the new content.
   - In the **Course levels** list, move `aria-current="page"` and the "You are here" badge to the new level.
3. In **every** level file, turn the "Coming soon" entry into a link once that level exists:
   ```html
   <li><a href="intermediate.html">Level 2 · Intermediate</a></li>
   ```
4. Keep the THEME TOKENS block and the final `<script>` the same in every file so all levels look and behave alike. If copying them becomes tedious, move them into shared `course.css` and `course.js` files and link them from each page. GitHub Pages serves them without any changes.

The theme is saved in `localStorage` under `pfb-theme`, so a learner's light or dark choice carries over between level pages on the same site.

## Content notes

- All sequences are real human RefSeq sequences from NCBI: HBB (NM_000518.5), INS (NM_000207.3), TP53 (NM_000546.6) and GAPDH (NM_002046.7). They are written 5′→3′.
- The codon table used in the lessons follows the standard genetic code (NCBI translation table 1).
- The page uses Pyodide v314.0.7 (Python 3.14, Biopython 1.87). To upgrade, change `pyodideVersion` in `CONFIG`, then re-test the Biopython lesson.
