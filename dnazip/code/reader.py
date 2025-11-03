from Bio import SeqIO
import os

CHR_FOLDER = "../data/chr/"
OUT_GENOME_FILE_PATH = 'full_genome.txt'

def sequence_cleaner(sequence):

    # Remove all 'N' characters using the replace() method
    clean_seq = str(sequence).replace("N", "")

    return clean_seq


def combine_chrs(chr_folder, output_file):
    genome = ''

    for chr_file in os.listdir(chr_folder):
        #CAN PROBABLY REMOVE I just have other stuff in my folder
        if chr_file.endswith(".fa"):
            chr_path = os.path.join(chr_folder, chr_file)

            for seq_record in SeqIO.parse(chr_path, "fasta"):
                clean_seq = sequence_cleaner(seq_record.seq).upper()
                genome += clean_seq

    with open(output_file, "w") as f:
        f.write(genome)


def get_snp_nuc(positions, chr_name):
    ref_chr_path = CHR_FOLDER + chr_name + '.fa'
    
    ref_record = SeqIO.read(ref_chr_path, "fasta")
    ref_seq = ref_record.seq

    nucs = []

    for pos in positions:

        nucs.append(ref_seq[pos-1].upper())

    return nucs

def get_del_nucs(positions, del_sizes, chr_name):
    ref_chr_path = CHR_FOLDER + chr_name + '.fa'
    
    ref_record = SeqIO.read(ref_chr_path, "fasta")
    ref_seq = ref_record.seq

    del_nucs = []

    for i in range(len(positions)):

        pos = positions[i]
        size = del_sizes[i]

        del_nucs.append(str(ref_seq[pos-1:pos+size-1]).upper())

    return del_nucs

def fa_to_txt(input_fasta_file, output_txt_file):

    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        clean_seq = sequence_cleaner(seq_record.seq).upper()


        with open(output_txt_file, "w") as f:
            f.write(clean_seq)

def main():
    input = "../../data/chr/ecoli.fna"
    output = "../../data/chr/ecoli.txt"

    fa_to_txt(input,output)

main()