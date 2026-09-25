"""
Vyom - Biology Toolkit
Exact computational biology - DNA/RNA sequence analysis, genetic code translation.
"""

CODON_TABLE = {
    "UUU": "Phe(F)", "UUC": "Phe(F)", "UUA": "Leu(L)", "UUG": "Leu(L)",
    "CUU": "Leu(L)", "CUC": "Leu(L)", "CUA": "Leu(L)", "CUG": "Leu(L)",
    "AUU": "Ile(I)", "AUC": "Ile(I)", "AUA": "Ile(I)", "AUG": "Met(M)/START",
    "GUU": "Val(V)", "GUC": "Val(V)", "GUA": "Val(V)", "GUG": "Val(V)",
    "UCU": "Ser(S)", "UCC": "Ser(S)", "UCA": "Ser(S)", "UCG": "Ser(S)",
    "CCU": "Pro(P)", "CCC": "Pro(P)", "CCA": "Pro(P)", "CCG": "Pro(P)",
    "ACU": "Thr(T)", "ACC": "Thr(T)", "ACA": "Thr(T)", "ACG": "Thr(T)",
    "GCU": "Ala(A)", "GCC": "Ala(A)", "GCA": "Ala(A)", "GCG": "Ala(A)",
    "UAU": "Tyr(Y)", "UAC": "Tyr(Y)", "UAA": "STOP", "UAG": "STOP",
    "CAU": "His(H)", "CAC": "His(H)", "CAA": "Gln(Q)", "CAG": "Gln(Q)",
    "AAU": "Asn(N)", "AAC": "Asn(N)", "AAA": "Lys(K)", "AAG": "Lys(K)",
    "GAU": "Asp(D)", "GAC": "Asp(D)", "GAA": "Glu(E)", "GAG": "Glu(E)",
    "UGU": "Cys(C)", "UGC": "Cys(C)", "UGA": "STOP", "UGG": "Trp(W)",
    "CGU": "Arg(R)", "CGC": "Arg(R)", "CGA": "Arg(R)", "CGG": "Arg(R)",
    "AGU": "Ser(S)", "AGC": "Ser(S)", "AGA": "Arg(R)", "AGG": "Arg(R)",
    "GGU": "Gly(G)", "GGC": "Gly(G)", "GGA": "Gly(G)", "GGG": "Gly(G)",
}

DNA_COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G"}


class BiologyToolkit:
    def validate_dna(self, sequence):
        return all(base in "ATGC" for base in sequence.upper())

    def validate_rna(self, sequence):
        return all(base in "AUGC" for base in sequence.upper())

    def gc_content(self, sequence):
        seq = sequence.upper()
        if not seq:
            return {"ok": False, "error": "Empty sequence."}
        gc_count = seq.count("G") + seq.count("C")
        return {"ok": True, "gc_percent": round(gc_count / len(seq) * 100, 2), "length": len(seq)}

    def reverse_complement(self, dna_sequence):
        seq = dna_sequence.upper()
        if not self.validate_dna(seq):
            return {"ok": False, "error": "Invalid DNA sequence."}
        complement = "".join(DNA_COMPLEMENT[base] for base in seq)
        return {"ok": True, "reverse_complement": complement[::-1]}

    def transcribe(self, dna_sequence):
        seq = dna_sequence.upper()
        if not self.validate_dna(seq):
            return {"ok": False, "error": "Invalid DNA sequence."}
        mrna = seq.replace("T", "U")
        return {"ok": True, "mrna": mrna}

    def translate(self, mrna_sequence, start_at_first_atg=True):
        seq = mrna_sequence.upper()
        if not self.validate_rna(seq):
            return {"ok": False, "error": "Invalid mRNA sequence."}

        start_index = 0
        if start_at_first_atg:
            start_index = seq.find("AUG")
            if start_index == -1:
                return {"ok": False, "error": "Koi START codon nahi mila."}

        protein = []
        i = start_index
        while i + 3 <= len(seq):
            codon = seq[i:i + 3]
            amino_acid = CODON_TABLE.get(codon, "?")
            if amino_acid == "STOP":
                break
            protein.append(amino_acid)
            i += 3

        return {"ok": True, "protein": protein, "protein_length": len(protein)}

    def dna_to_protein(self, dna_sequence):
        transcribed = self.transcribe(dna_sequence)
        if not transcribed["ok"]:
            return transcribed
        return self.translate(transcribed["mrna"])

    def count_bases(self, sequence):
        seq = sequence.upper()
        return {
            "ok": True,
            "A": seq.count("A"), "T": seq.count("T"),
            "G": seq.count("G"), "C": seq.count("C"),
            "U": seq.count("U"),
            "length": len(seq),
        }

    def hamming_distance(self, seq1, seq2):
        if len(seq1) != len(seq2):
            return {"ok": False, "error": "Sequences same length ki honi chahiye."}
        distance = sum(1 for a, b in zip(seq1.upper(), seq2.upper()) if a != b)
        return {"ok": True, "hamming_distance": distance}
