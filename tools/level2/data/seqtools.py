"""seqtools: small, tested helpers for DNA sequences (from Level 1 of the course)."""

CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L", "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M", "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S", "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T", "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*", "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K", "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W", "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R", "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}
PAIRS = {"A": "T", "T": "A", "G": "C", "C": "G", "N": "N"}


def gc_content(seq):
    """Return the GC content of a DNA sequence as a percentage (0 to 100)."""
    seq = seq.upper()
    return (seq.count("G") + seq.count("C")) / len(seq) * 100


def reverse_complement(seq):
    """Return the reverse complement of a DNA sequence, written 5'->3'."""
    result = ""
    for base in seq.upper():
        result = PAIRS[base] + result
    return result


def translate(seq):
    """Translate DNA into protein, stopping at the first stop codon."""
    protein = ""
    for i in range(0, len(seq) - 2, 3):
        amino_acid = CODON_TABLE[seq[i:i + 3]]
        if amino_acid == "*":
            break
        protein += amino_acid
    return protein


def read_fasta(filename):
    """Read a FASTA file and return a dictionary {id: sequence}."""
    sequences = {}
    current_id = None
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                sequences[current_id] = ""
            elif line:
                sequences[current_id] += line
    return sequences


def phred_scores(qual):
    """Return the list of Phred scores for a Phred+33 quality string."""
    return [ord(character) - 33 for character in qual]


def read_fastq(filename):
    """Read a FASTQ file and return a list of reads (dictionaries with id, seq and qual)."""
    with open(filename) as f:
        lines = [line.strip() for line in f if line.strip()]
    reads = []
    for i in range(0, len(lines), 4):
        header, seq, plus, qual = lines[i:i + 4]
        if not header.startswith("@") or not plus.startswith("+") or len(seq) != len(qual):
            raise ValueError(f"Record starting on line {i + 1} isn't valid FASTQ")
        reads.append({"id": header[1:].split()[0], "seq": seq, "qual": qual})
    return reads
