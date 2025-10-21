import huffman, bitfile, dbsnp, dels, dbSNP_bit_array, snp, vint, dnazip, insr, os
import argparse
import pandas as pd
import numpy as np
from constants import *

    
INPUT_FILE_PATH = "../data/variants/HG004_GRCh38_sorted_variants.txt"
DBSNP_PATH = "../data/dbSNP/"
OUTPUT_PATH = "../data/output/HG004_GRCh38_Encoded"


def encode_file(input_file_path, dbSNP_path, k_mer_size):
    
    variants_df       = pd.read_csv(input_file_path, 
                                    names=['var_type', 'chr', 'pos', 'var_info'],
                                    header=None)

    # Create list of chromosomes to encode
    chr_list = variants_df['chr'].unique()

    for chr in chr_list:

        # Choose current chromosome
        chr_df = variants_df.where(variants_df['chr'] == chr)

        # Variation dataframes
        snps_df = chr_df.where(chr_df['var_type'] == 0).dropna()
        dels_df = chr_df.where(chr_df['var_type'] == 1).dropna()
        insr_df = chr_df.where(chr_df['var_type'] == 2).dropna()
        
        # Bitstring encoding of: chr#
        ascii_chr_bitstring = bitfile.encodeStringToBytes(chr)
        bitfile.export_as_binary(OUTPUT_PATH, ascii_chr_bitstring)

        # Encoding of Mapped SNPs
        bitmap, bitmap_size_vint, unmapped_df = dbsnp.compares_dbsnp(snps_df, dbSNP_path, chr)
        
        bitfile.export_as_binary(OUTPUT_PATH, bitmap_size_vint)
        bitfile.export_as_binary(OUTPUT_PATH, bitmap)

        # Encoding of Unmapped SNPs
        snp_size_vint, unmapped_pos_bitstr, unmapped_nuc_bitstr = snp.encode_SNPs(unmapped_df)
        
        ### Add above to bin 
        bitfile.export_as_binary(OUTPUT_PATH, snp_size_vint)
        bitfile.export_as_binary(OUTPUT_PATH, unmapped_pos_bitstr)
        bitfile.export_as_binary(OUTPUT_PATH, unmapped_nuc_bitstr)

        # Start of DELs
        bitfile.export_as_binary(OUTPUT_PATH, ascii_chr_bitstring)

        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = dels.encode_dels(dels_df)
        
        ### Add above to bin 
        bitfile.export_as_binary(OUTPUT_PATH, del_size_vint)
        bitfile.export_as_binary(OUTPUT_PATH, del_pos_bitstr)
        bitfile.export_as_binary(OUTPUT_PATH, del_len_bitstr)
        
        # Start of INSRs 
        bitfile.export_as_binary(OUTPUT_PATH, ascii_chr_bitstring)
        
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = insr.encode_ins(insr_df, k_mer_size)
        
        ### Add above to bin        
        bitfile.export_as_binary(OUTPUT_PATH, ins_size_vint)
        bitfile.export_as_binary(OUTPUT_PATH, ins_pos_bitstr)
        bitfile.export_as_binary(OUTPUT_PATH, ins_len_bitstr)
        bitfile.export_as_binary(OUTPUT_PATH, ins_bitstr_len_vint)
        bitfile.export_as_binary(OUTPUT_PATH, ins_seq_bitstr)        


def main(): 
    
    k_mer_size = 4
    
    if os.path.exists(OUTPUT_PATH + ".bin"):
        os.remove(OUTPUT_PATH + ".bin")
    else:
        print("The bin file does not exist") 
    
    encode_file(INPUT_FILE_PATH, DBSNP_PATH, k_mer_size)    


if __name__ == "__main__":
    main()
    