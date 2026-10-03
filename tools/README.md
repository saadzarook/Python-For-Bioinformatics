# Tools: build and test the course pages

Run every command from the repository folder (the one with `index.html`). All paths in these scripts are relative to the repository, so they work wherever it's cloned.

## Setup (once)

```bash
pip install pandas==3.0.2 matplotlib==3.10.8 biopython==1.87 "numpy<2.5" playwright
```

These match the versions the pages load through Pyodide v314.0.7, so results in normal Python match the browser. The browser tests use your installed Google Chrome (`channel="chrome"` in the scripts); to use Playwright's own Chromium instead, run `playwright install chromium` and remove `channel="chrome"`.

## What's here

| Path | What it is |
|---|---|
| `check_shared.py` | Checks that the shared code is identical in every level page. |
| `run_python_tests.py` | Runs every example and every exercise check of a page in normal Python. |
| `browser_test.py` | Does the same in real Chrome, from disk or from a server, in light or dark mode. |
| `browser_checks_level2.py` | Level 2's extra browser checks: lazy loading, NCBI live and fallback, 375 px mobile layout and menu, level nav, theme carry-over, screenshots. |
| `expected_errors.json` | The example boxes that show an error on purpose (the test runners don't count them as failures). |
| `shared/` | The code shared by all levels: `shared.py` (copies Level 1's CSS and scripts and applies the marked Level 2 extensions), `runtime_ext.py`, `errors_ext.js`, `extra.css`. |
| `level2/` | Level 2's source: `build.py`, the lessons in `parts/`, the data files in `data/`, and helper scripts (`make_data.py`, `trim_genbank.py`, `dump_plots.py`). |
| `output/` | Reports and screenshots written by the scripts. Ignored by git. |

`intermediate.html` is **generated**: edit the files in `tools/level2/` (and `tools/shared/` for shared code), then rebuild with `python tools/level2/build.py`. If you edit `intermediate.html` directly, copy the change back into `tools/level2/parts/` too, or the next build will overwrite it. `index.html` (Level 1) is still edited directly, and it's the source of the shared code.

## Check that the shared code is identical in both pages

```bash
python tools/check_shared.py
```

Level 1 is the source. The script rebuilds the shared parts from `index.html` plus `tools/shared/` and checks that `intermediate.html` (and `advanced.html`, once it exists) contains them unchanged: the theme script and favicon in `<head>`, the CSS, the Python runtime and the page script. (Each page's `CONFIG.preload` list is level-specific, so it isn't compared.) It prints `OK` or a diff, and exits with status 1 if anything differs.

If you change shared code in `index.html`, rebuild the later levels so they pick it up, then run the check. If you change a Level 2 extension, edit `tools/shared/`, not the page.

## Run all examples and exercise checks in normal Python

```bash
python tools/run_python_tests.py index.html          # Level 1
python tools/run_python_tests.py intermediate.html   # Level 2
python tools/run_python_tests.py intermediate.html regex fastq   # just some lessons (section ids)
```

This uses the page's own Python runtime and data files. For every exercise it checks that the untouched starter fails, that the solution passes, and that the starter still fails after the solution has run (exercises that write files must not pass on a file left over from an earlier run). Example boxes that use `await` (the live NCBI calls) need a browser and are skipped here. Every output is written to `tools/output/python_report_<page>.txt`; the summary ends with `no problems`, or lists them and exits with status 1.

## Run the browser tests

```bash
# from disk, light theme
python tools/browser_test.py intermediate.html
python tools/browser_test.py index.html

# from a local server, dark theme (start the server in another terminal)
npx http-server -c-1 -p 8000
python tools/browser_test.py http://localhost:8000/intermediate.html --theme dark

# block NCBI, to test the saved-copy fallback
python tools/browser_test.py intermediate.html --offline-ncbi

# Level 2's extra checks (needs the local server)
python tools/browser_checks_level2.py http://localhost:8000
```

`browser_test.py` waits for Python to start, runs every example, then for every exercise presses **Check my answer** on the untouched starter (it must not pass) and **Check this solution** (it must pass). It also collects console errors (ignoring the browser's own `favicon.ico` 404, and blocked requests when using `--offline-ncbi`) and lists which package files were downloaded. A full Level 2 run takes about five minutes. Reports go to `tools/output/`.

To look at every plot in both themes without a browser: `python tools/level2/dump_plots.py` (PNG files in `tools/output/plots/`).

## Reuse for Level 3

1. Copy `tools/level2/` to `tools/level3/`. In `level3/build.py`, change `TITLE`, `DESCRIPTION`, `PRELOAD` (which lesson ids start which package downloads), `DATA` and the output file name (`advanced.html`). Replace the lessons in `parts/` and the files in `data/`; the sidebar and level nav are in `parts/00_header.html`.
2. Build with `python tools/level3/build.py`. The shared code comes from `index.html` and `tools/shared/` automatically, so it's identical by construction.
3. `python tools/check_shared.py` already checks `advanced.html` once it exists.
4. `run_python_tests.py` and `browser_test.py` work on any page: pass `advanced.html`. Add any deliberate error demos to `expected_errors.json`.
5. For extra browser checks, copy `browser_checks_level2.py` and change the lesson ids it scrolls to and the boxes it runs.
6. If Level 3 needs a new shared feature, add it to `tools/shared/` (as a new marked patch in `shared.py`, or in `runtime_ext.py`, `errors_ext.js` or `extra.css`), keep it backwards compatible, and rebuild Level 2 too.

## Where the Level 2 data comes from

| File in `level2/data/` | Source |
|---|---|
| `reads.fastq`, `run42.fastq` | Made-up teaching data: `python tools/level2/make_data.py` (fixed random seed, so it reproduces the same files). |
| `expression.csv`, `annotation.tsv` | Made-up teaching data, written by hand (real genes and chromosomes, invented TPM values). |
| `NM_000518.5_full.gb`, `NM_001201391.1_mouse_full.gb` | Full GenBank records saved from NCBI on 3 October 2026 (human HBB; mouse Hbb-bs, used to check the Lesson 11 sequences). |
| `hbb_trimmed.gb` | Made from the full HBB record by `python tools/level2/trim_genbank.py`. |
| `esearch_hbb.json`, `efetch_hbb.fasta` | NCBI E-utilities answers saved on 3 October 2026; the page's offline fallback for Lesson 12. If you refresh them, update `SAVED_ON` in `ncbi_helper.py` and the dates mentioned in Lesson 12. |
| `seqtools.py`, `ncbi_helper.py` | Python modules the lessons import. |
