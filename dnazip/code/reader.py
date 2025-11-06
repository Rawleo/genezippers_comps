from Bio import SeqIO
import os


def sequence_cleaner(sequence):
    '''
    Removes all N or n nucleotides from sequences

    @params:
    * sequence: nucleotide sequences

    @return:
    * clean_seq: nucleotide sequnce with only A's, C's, T's, and G's
    '''
    # Remove all 'N' and 'n' characters using the replace() method
    clean_seq = sequence.replace("N", "")
    clean_seq = clean_seq.replace("n", "")

    return clean_seq


def combine_chrs(chr_folder, output_file, file_type):
    '''
    Given a folder filled with chromosome sequecnes, combines 
    them, and outputs them into a .txt file

    @params:
    * chr_folder: folder which hold a list of chromosome files
    * output_file: output file path where genome should be written to
    * file_type: file type of sequences (.fna, .fasta, etc.)
    '''
    genome = ''

    for chr_file in os.listdir(chr_folder):
        # Identify each sequence file within folder
        if chr_file.endswith(f"{chr}.fa") or chr_file.endswith(f"{chr}.{file_type}"):
            chr_path = os.path.join(chr_folder, chr_file)

            for seq_record in SeqIO.parse(chr_path, file_type):
                # Clean each chromosome sequence and append to genome
                seq = str(seq_record.seq).upper()
                clean_seq = sequence_cleaner(seq)
                genome += clean_seq

    with open(output_file, "w") as f:
        f.write(genome)
        
        
def clean_chr(chr_folder, output_file, chr, file_type):
    '''
    Cleans a single chromosome file and outputs it to a text file

    @params:
    * chr_folder: folder containing chromosome files
    * output_file: path where to write cleaned sequence
    * chr: chromosome identifier
    * file_type: file type of sequences (.fna, .fasta, etc.)
    '''
    genome = ''

    # Iterate through files in chromosome folder
    for chr_file in os.listdir(chr_folder):
        # Find file matching chromosome identifier
        if chr_file.endswith(f"{chr}.{file_type}"):
            chr_path = os.path.join(chr_folder, chr_file)

            # Parse and clean sequence
            for seq_record in SeqIO.parse(chr_path, "fasta"):
                seq = str(seq_record.seq).upper()
                clean_seq = sequence_cleaner(seq)
                genome += clean_seq

    # Write cleaned sequence to output file
    with open(output_file, "w") as f:
        f.write(genome)


def get_snp_nuc(positions, chr_name, chr_folder):
    '''
    Gets the nucleotide at specified positions in a chromosome sequence

    @params:
    * positions: list of positions to look up
    * chr_name: chromosome identifier
    * chr_folder: path to folder containing chromosomes
    
    @return:
    * nucs: list of nucleotides found at the specified positions
    '''
    # Construct path to reference chromosome file
    ref_chr_path = chr_folder + chr_name + '.fa'
    
    # Read the reference sequence
    ref_record = SeqIO.read(ref_chr_path, "fasta")
    ref_seq = ref_record.seq

    nucs = []

    # Extract nucleotide at each position
    for pos in positions:
        # Convert to 0-based indexing and get uppercase nucleotide
        nucs.append(ref_seq[pos-1].upper())

    return nucs


def get_del_nucs(positions, del_sizes, chr_name, chr_folder):
    '''
    Gets the nucleotide sequences for deletions at specified positions

    @params:
    * positions: list of deletion start positions 
    * del_sizes: list of deletion sizes
    * chr_name: chromosome identifier
    * chr_folder: path to folder containing chromosomes

    @return:
    * del_nucs: list of deleted nucleotide sequences
    '''
    # Construct path to reference chromosome file
    ref_chr_path = chr_folder + chr_name + '.fa'
    
    # Read the reference sequence
    ref_record = SeqIO.read(ref_chr_path, "fasta")
    ref_seq = ref_record.seq

    del_nucs = []

    # Extract deleted sequence for each position and size
    for i in range(len(positions)):
        pos = positions[i]
        size = del_sizes[i]

        # Get sequence from pos to pos+size and convert to uppercase
        del_nucs.append(str(ref_seq[pos-1:pos+size-1]).upper())

    return del_nucs


def fa_to_txt(input_fasta_file, output_txt_file):
    '''
    Converts sequence file into .txt file

    @params:
    * input_fasta_file: file path to sequence file (.fna, .fasta, etc.)
    * output_txt_file: file path where to output cleaned sequence
    '''
    # Parse the input FASTA file and process each sequence record
    for seq_record in SeqIO.parse(input_fasta_file, "fasta"):
        # Clean the sequence by removing unwanted nucleotides and convert to uppercase
        clean_seq = sequence_cleaner(seq_record.seq).upper()

        # Open the output text file in write mode and write the cleaned sequence
        with open(output_txt_file, "w") as f:
            f.write(clean_seq)