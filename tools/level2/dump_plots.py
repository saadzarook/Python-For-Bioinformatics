"""Render every matplotlib example and solution of a page to PNG files, in light and dark
theme, so you can look at them all at once (normal Python, no browser needed).

usage (from the repository folder):  python tools/level2/dump_plots.py [page.html]
Writes tools/output/plots/plotNN_light.png and plotNN_dark.png.
"""
import asyncio, base64, json, os, re, sys, tempfile
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PAGE = (REPO / (sys.argv[1] if len(sys.argv) > 1 else "intermediate.html")).read_text(encoding="utf-8")
OUTDIR = REPO / "tools" / "output" / "plots"; OUTDIR.mkdir(parents=True, exist_ok=True)
data = {m.group(1): re.sub(r"^\n", "", m.group(2)) for m in re.finditer(r'<script type="text/plain" class="data-file" data-filename="([^"]+)">(.*?)</script>', PAGE, re.S)}
runtime = re.search(r'<script type="text/x-python" id="py-runtime">\n(.*?)</script>', PAGE, re.S).group(1)
os.chdir(tempfile.mkdtemp())
for n, t in data.items(): Path(n).write_text(t, encoding="utf-8")
ns = {}; exec(runtime, ns)
codes = re.findall(r'<script type="text/x-python" class="py-(?:example|solution)">(.*?)</script>', PAGE, re.S)
k = 0
for code in codes:
    if "matplotlib" not in code: continue
    for theme in ["light", "dark"]:
        ns["_pfb_theme"] = theme
        r = json.loads(asyncio.run(ns["_pfb_run"](code.strip())))
        for img in r["images"]:
            (OUTDIR / f"plot{k:02d}_{theme}.png").write_bytes(base64.b64decode(img["src"].split(",")[1]))
    k += 1
print(k, "plots")
