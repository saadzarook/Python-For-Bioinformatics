# Python for Bioinformatics — notes for Claude Code

A browser-based course that teaches Python with DNA, RNA and protein examples. Python runs in the page through Pyodide; learners install nothing. Level 1 (`index.html`) and Level 2 (`intermediate.html`) exist; Level 3 is planned.

## Audience and tone
- Learners are beginners in biology/bioinformatics. Level 2 learners finished Level 1 and still see themselves as beginners: never assume anything not taught earlier; explain every new term the first time.
- Tone: casual, warm, encouraging, a little playful. Talk to "you", short paragraphs, plain words, British spelling (as in Level 1).
- Always say **why** something matters in real bioinformatics before showing **how**.
- Normalise mistakes ("errors are clues"); celebrate progress at the end of each lesson. Never call something "easy".

## Files
- `index.html` — Level 1. Edited directly. It is the **source of the shared code**.
- `intermediate.html` — Level 2. **Generated; never edit it directly.** Edit `tools/level2/` (lessons in `parts/`, data in `data/`), then run `python tools/level2/build.py`.
- `tools/shared/` — code shared by Level 2+ (runtime, error hints, extra CSS, marked patches to Level 1's script).
- `tools/` — build, checks and tests; see `tools/README.md`. Test output goes to `tools/output/` (git-ignored).
- `audio/` — reserved for planned voice-overs (empty apart from `.gitkeep`).

## Shared-code rule
- Blocks marked `SHARED WITH LEVEL 1 — keep in sync` (theme script, favicon, CSS sections 1–7, Python runtime, page script) must be identical in every level page. Level 2 additions are marked `LEVEL 2` and must stay backwards compatible.
- To change shared code: edit `index.html` (or `tools/shared/` for Level 2+ extensions), rebuild later levels, then run `python tools/check_shared.py`.

## Before finishing any change, run
```bash
python tools/level2/build.py
python tools/check_shared.py
python tools/run_python_tests.py index.html
python tools/run_python_tests.py intermediate.html
python tools/browser_test.py index.html
python tools/browser_test.py intermediate.html
# with a server: npx http-server -c-1 -p 8000
python tools/browser_test.py http://localhost:8000/intermediate.html --theme dark
python tools/browser_checks_level2.py http://localhost:8000
```
All must report no problems / exit status 0. Setup is in `tools/README.md`.

## Lesson pattern
Why it matters → explanation → runnable examples → 1–3 exercises (+ optional 🌶️ challenge) → quiz (2–4 questions, an explanation on every option) → key takeaways → short celebration.

## Exercises and checks
- Markup: `div.exercise` with `py-starter`, `div.hints` (one `<p>` per hint, progressive), `py-solution`, `py-tests`. Label the kind in the `<h4>`: ✍️ Write it, 🐞 Fix the bug, 🔮 Predict, then run, 🧹 Make it cleaner.
- Checks are `assert cond, "friendly nudge"`. They must re-run the learner's code with other inputs (`_source`, or call their functions with new values) so hard-coded answers fail.
- The untouched starter must fail; the solution must pass. If an exercise writes files, the check deletes them and re-runs `_source` first.
- No check may depend on the network (NCBI checks use the saved copies).
- Example boxes that error on purpose: say so in the text and add them to `tools/expected_errors.json`.

## Data
- Real sequences show their NCBI accession with version (e.g. NM_000518.5).
- Made-up teaching data must be biologically plausible and labelled "made-up teaching data" wherever it appears. Embed every file as a `data-file` block; keep files small.
- Double-check biology claims by computing them, not from memory.

## Planned work
- Voice-overs: `audio/` is reserved; no player code exists yet in either level.
- Level 3 (Advanced, "Coming soon"): NGS data at scale, variant calls (VCF), statistics for differential expression, reproducible workflows. Build it with `tools/level3/` following "Reuse for Level 3" in `tools/README.md`.

## Hosting
- GitHub Pages from the `main` branch root (`.nojekyll` present). No build step on the server: commit the built `intermediate.html`.
- Relative links only (`index.html`, `intermediate.html#lesson`), so pages work from disk, a local server and a Pages subfolder.
- No secrets in the repo: no API keys or real email addresses (use placeholders such as `your.name@example.org`).
- Commit only when asked; never push without being asked.
