"""Make data/hbb_trimmed.gb (embedded in the page as hbb.gb) from the full NCBI record.

usage: python tools/level2/trim_genbank.py
Keeps the header, one reference (Marotta et al. 1977, renumbered as reference 1), the
main features (source, gene, exon, CDS, regulatory, polyA_site) and the whole sequence.
The full record was saved from NCBI E-utilities efetch (db=nuccore, id=NM_000518.5,
rettype=gb) on 3 October 2026, as data/NM_000518.5_full.gb.
"""
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
KEEP = {"source", "gene", "exon", "CDS", "regulatory", "polyA_site"}

lines = (DATA / "NM_000518.5_full.gb").read_text(encoding="utf-8").splitlines()
out, i = [], 0
while not lines[i].startswith("REFERENCE"):          # header
    out.append(lines[i]); i += 1
blocks = []
while not lines[i].startswith("COMMENT"):            # references
    if lines[i].startswith("REFERENCE"):
        blocks.append([lines[i]])
    else:
        blocks[-1].append(lines[i])
    i += 1
reference = next(b for b in blocks if any("Marotta" in line for line in b))
reference[0] = "REFERENCE   1  (bases 1 to 628)"
out += reference
while not lines[i].startswith("FEATURES"):
    i += 1
out.append(lines[i]); i += 1
features = []
while not lines[i].startswith("ORIGIN"):
    if len(lines[i]) > 5 and lines[i][5] != " ":
        features.append([lines[i]])
    else:
        features[-1].append(lines[i])
    i += 1
for feature in features:
    if feature[0][5:21].strip() in KEEP:
        out += feature
out += lines[i:]
(DATA / "hbb_trimmed.gb").write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote data/hbb_trimmed.gb")
