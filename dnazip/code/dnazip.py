import huffman, bitfile, dbsnp, dels, dbSNP_bit_array, snp, vint, dnazip, insr, os
import argparse
import pandas as pd
import numpy as np
from constants import *

VARIANT_NAME    = 'HG003_GRCh38'
INPUT_FILE_PATH = f"../data/variants/{VARIANT_NAME}_sorted_variants.txt"
DBSNP_PATH      = "../data/dbSNP/"
OUTPUT_PATH     = f"../data/output/{VARIANT_NAME}_Encoded"

def encode_file(input_file_path, dbSNP_path, k_mer_size):
    
    variants_df       = pd.read_csv(input_file_path, 
                                    names=['var_type', 'chr', 'pos', 'var_info'],
                                    header=None)

    # # Create list of chromosomes to encode
    # chr_list = variants_df['chr'].unique()

    chr_list = CHROMOSOMES
    not_used = ''
    
    ### Export Huffman Encoding Map
    insr_df = variants_df.where(variants_df['var_type'] == 2).dropna()
    # Split insertions into relevant nucleotides
    insr_df["var_info"] = insr_df["var_info"].apply(lambda x: x.split('/')[1])
    # Concatenate all position length VINTs
    ins_seq = ''.join(insr_df["var_info"].astype(str).tolist())

    # Produce encoding_map
    not_used, encoding_map = huffman.run_huffman(ins_seq, k_mer_size)
    
    # print(encoding_map)
    
    huffman.export_as_txt(f"../data/huffman_trees/{VARIANT_NAME}", encoding_map)

    for chr in chr_list:

        # Choose current chromosome
        chr_df = variants_df.where(variants_df['chr'] == chr)

        # Variation dataframes
        snps_df = chr_df.where(chr_df['var_type'] == 0).dropna()
        dels_df = chr_df.where(chr_df['var_type'] == 1).dropna()
        insr_df = chr_df.where(chr_df['var_type'] == 2).dropna()
        

        # Encoding of Mapped SNPs
        bitmap, bitmap_size_vint, unmapped_df = dbsnp.compares_dbsnp(snps_df, dbSNP_path, chr)

        # Encoding of Unmapped SNPs
        snp_size_vint, unmapped_pos_bitstr, unmapped_nuc_bitstr = snp.encode_SNPs(unmapped_df)
        snp_bitstring = bitmap_size_vint + bitmap + snp_size_vint + unmapped_pos_bitstr + unmapped_nuc_bitstr
        bitfile.export_as_binary(OUTPUT_PATH, snp_bitstring)
                    
        # Start of DELs

        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = dels.encode_dels(dels_df)

        
        ### Add above to bin 
        del_bitstring = del_size_vint + del_pos_bitstr + del_len_bitstr
        bitfile.export_as_binary(OUTPUT_PATH, del_bitstring)

        # Start of INSRs 
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = insr.encode_ins(insr_df, encoding_map, k_mer_size)
        
        ### Add above to bin        
        insertion_bitstring = ins_size_vint + ins_pos_bitstr + ins_len_bitstr + ins_bitstr_len_vint + ins_seq_bitstr
        bitfile.export_as_binary(OUTPUT_PATH, insertion_bitstring)


def main(): 
    
    k_mer_size = 4
    
    if os.path.exists(OUTPUT_PATH + ".bin"):
        os.remove(OUTPUT_PATH + ".bin")
    else:
        print("The bin file does not exist") 
    
    encode_file(INPUT_FILE_PATH, DBSNP_PATH, k_mer_size)    


if __name__ == "__main__":
    main()
    