"""Generate the made-up FASTQ teaching data for Level 2 (seeded, so it's reproducible).

usage: python tools/level2/make_data.py   -> rewrites data/reads.fastq and data/run42.fastq
(expression.csv and annotation.tsv were written by hand; the NCBI files were saved from
NCBI's E-utilities on 3 October 2026, see tools/README.md.)
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)

# Real sequences (NCBI RefSeq coding sequences, same as Level 1's genes.fasta / sample.fasta)
HBB = ("ATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAAC"
       "GTGGATGAAGTTGGTGGTGAGGCCCTGGGCAGGCTGCTGGTGGTCTACCCTTGGACCCAG"
       "AGGTTCTTTGAGTCCTTTGGGGATCTGTCCACTCCTGATGCTGTTATGGGCAACCCTAAG"
       "GTGAAGGCTCATGGCAAGAAAGTGCTCGGTGCCTTTAGTGATGGCCTGGCTCACCTGGAC"
       "AACCTCAAGGGCACCTTTGCCACACTGAGTGAGCTGCACTGTGACAAGCTGCACGTGGAT"
       "CCTGAGAACTTCAGGCTCCTGGGCAACGTGCTGGTCTGTGTGCTGGCCCATCACTTTGGC"
       "AAAGAATTCACCCCACCAGTGCAGGCTGCCTATCAGAAAGTGGTGGCTGGTGTGGCTAAT"
       "GCCCTGGCCCACAAGTATCACTAA")
INS = ("ATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGAC"
       "CCAGCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTAC"
       "CTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGAC"
       "CTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTG"
       "GCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGC"
       "TCCCTCTACCAGCTGGAGAACTACTGCAACTAG")
GAPDH = ("ATGGGGAAGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGG"
         "GCTGCTTTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTC")
TP53 = ("ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCA"
        "GACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATG")
assert len(HBB) == 444 and len(INS) == 333 and len(GAPDH) == 120 and len(TP53) == 120

SOURCES = [HBB, INS, GAPDH, TP53]


def quality_profile(rng, length, good=True):
    """Phred scores that start high and fall towards the 3' end (Illumina-like)."""
    base = rng.uniform(35, 39) if good else rng.uniform(21, 27)
    drop = rng.uniform(8, 16) if good else rng.uniform(10, 18)
    quals = []
    for i in range(length):
        q = base - drop * (i / length) ** 2 + rng.gauss(0, 1.8)
        if i < 3:
            q -= 2          # the first couple of cycles are slightly lower
        quals.append(int(round(min(40, max(2, q)))))
    return quals


def make_read(rng, length, good=True):
    src = rng.choice(SOURCES)
    start = rng.randrange(0, len(src) - length + 1)
    seq = list(src[start:start + length])
    quals = quality_profile(rng, length, good)
    for i, q in enumerate(quals):
        if q <= 8 and rng.random() < 0.35:     # very low quality -> base called N
            seq[i] = "N"
            quals[i] = 2
        elif q < 20 and rng.random() < 0.08:   # low quality -> occasional wrong base
            seq[i] = rng.choice([b for b in "ACGT" if b != seq[i]])
    return "".join(seq), quals


def to_fastq(records):
    lines = []
    for rid, seq, quals in records:
        lines += ["@" + rid, seq, "+", "".join(chr(q + 33) for q in quals)]
    return "\n".join(lines) + "\n"


# Lesson 5: a tiny file with 6 reads of 40 bases, chosen to show each situation.
rng = random.Random(7)
small = []
kinds = [True, True, False, True, True, False]
for n, good in enumerate(kinds, start=1):
    seq, q = make_read(rng, 40, good)
    if n == 3:                       # give one read an unknown base, as real data has
        worst = q.index(min(q))
        seq = seq[:worst] + "N" + seq[worst + 1:]
        q[worst] = 2
    small.append((f"read{n} sample=S01", seq, q))
(OUT / "reads.fastq").write_text(to_fastq(small))

# Capstone: 40 reads of 75 bases.
rng = random.Random(42)
big = []
for n in range(1, 41):
    good = rng.random() > 0.2
    seq, q = make_read(rng, 75, good)
    big.append((f"run42_read{n:03d}", seq, q))
(OUT / "run42.fastq").write_text(to_fastq(big))
print("written")
