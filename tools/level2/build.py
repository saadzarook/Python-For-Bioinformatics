"""Build intermediate.html (Level 2) from the parts in this folder.

    python tools/level2/build.py

Shared CSS and JavaScript are copied from index.html (Level 1) by tools/shared/shared.py,
so they stay identical. Level 2's own content lives here:
  parts/*.html        the lessons and glossary, in file-name order
  parts_tail/         the footer and the comment above the data files
  data/               files embedded as data-file blocks (see DATA below)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "shared"))
from shared import between, shared_head, shared_runtime, shared_script, shared_style  # noqa: E402

TITLE = "Python for Bioinformatics — Level 2: Intermediate"
DESCRIPTION = ("Level 2 of a hands-on bioinformatics course: cleaner code, errors, regular expressions, FASTQ quality, "
               "pandas tables, plots, GenBank files, alignment and NCBI. Runs entirely in your browser.")

# CONFIG.preload for this level: a package starts downloading when its lesson is reached.
PRELOAD = """[
      { selector: "#fastq", packages: ["biopython"] },
      { selector: "#pandas-1", packages: ["pandas"] },
      { selector: "#pandas-2", packages: ["pandas"] },
      { selector: "#plotting", packages: ["matplotlib", "pandas"] },
      { selector: "#biopython-more", packages: ["biopython"] },
      { selector: "#alignment", packages: ["biopython"] },
      { selector: "#ncbi", packages: ["biopython"] },
      { selector: "#capstone", packages: ["pandas", "matplotlib", "biopython"] }
    ]"""

# (name in the page's virtual folder, source file in data/ or None = copy from Level 1)
DATA = [
    ("sample.fasta", None), ("genes.fasta", None),
    ("reads.fastq", "reads.fastq"), ("run42.fastq", "run42.fastq"),
    ("expression.csv", "expression.csv"), ("annotation.tsv", "annotation.tsv"),
    ("hbb.gb", "hbb_trimmed.gb"),
    ("esearch_hbb.json", "esearch_hbb.json"), ("efetch_hbb.fasta", "efetch_hbb.fasta"),
    ("ncbi_helper.py", "ncbi_helper.py"), ("seqtools.py", "seqtools.py"),
]


def build():
    l1 = (REPO / "index.html").read_text(encoding="utf-8")
    head = shared_head(l1, TITLE, DESCRIPTION)
    style = shared_style(l1, "Level 2's own styles are in section 8 at the end.")
    body = "".join(p.read_text(encoding="utf-8") for p in sorted((HERE / "parts").glob("*.html")))
    blocks = []
    for name, source in DATA:
        if source is None:
            text = between(l1, f'<script type="text/plain" class="data-file" data-filename="{name}">\n', "</script>")
        else:
            text = (HERE / "data" / source).read_text(encoding="utf-8")
        assert "</script" not in text.lower(), f"{name} can't contain </script"
        blocks.append(f'<script type="text/plain" class="data-file" data-filename="{name}">\n{text.rstrip()}\n</script>\n')
    data_html = (HERE / "parts_tail" / "data_intro.html").read_text(encoding="utf-8") + "".join(blocks)
    footer = (HERE / "parts_tail" / "footer.html").read_text(encoding="utf-8")
    page = (head + style + "</head>\n<body>\n" + body + footer + data_html + "\n"
            + shared_runtime(l1) + "\n" + shared_script(l1, PRELOAD) + "</body>\n</html>\n")
    out = REPO / "intermediate.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(REPO)} ({len(page) // 1024} KB, {page.count(chr(10))} lines)")


if __name__ == "__main__":
    build()
