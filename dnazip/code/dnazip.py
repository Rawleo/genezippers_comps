import huffman, bitfile, dbsnp, dels, snp, insr, os
import pandas as pd
import numpy as np
from constants import *

def encode_file(input_file_path, dbSNP_path, k_mer_size):
    
    variants_df       = pd.read_csv(input_file_path, 
                                    names=['var_type', 'chr', 'pos', 'var_info'],
                                    header=None)

    chr_list = CHROMOSOMES
    
    ### Export Huffman Encoding Map
    insr_df = variants_df.where(variants_df['var_type'] == 2).dropna()
    # Split insertions into relevant nucleotides
    insr_df["var_info"] = insr_df["var_info"].apply(lambda x: x.split('/')[1])
    # Concatenate all position length VINTs
    ins_seq = ''.join(insr_df["var_info"].astype(str).tolist())

    # Produce encoding_map
    encoding_map = huffman.run_insr_huffman(ins_seq, k_mer_size)
    
    # print(encoding_map)
    
    huffman.export_as_txt(f"../data/huffman_trees/{VARIANT_NAME}.txt", encoding_map)

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
        bitfile.export_as_binary(OUTPUT_BIN_PATH, snp_bitstring)
                    
        # Start of DELs

        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = dels.encode_dels(dels_df)

        
        ### Add above to bin 
        del_bitstring = del_size_vint + del_pos_bitstr + del_len_bitstr
        bitfile.export_as_binary(OUTPUT_BIN_PATH, del_bitstring)

        # Start of INSRs 
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = insr.encode_ins(insr_df, encoding_map, k_mer_size)
        
        ### Add above to bin        
        insertion_bitstring = ins_size_vint + ins_pos_bitstr + ins_len_bitstr + ins_bitstr_len_vint + ins_seq_bitstr
        bitfile.export_as_binary(OUTPUT_BIN_PATH, insertion_bitstring)


def remove_file_if_exists(filepath):
    if os.path.exists(filepath):
        print("Removing:", filepath)
        os.remove(filepath)
    else:
        print("This file does not exist:", filepath)
        print("Continuing...") 


def main(): 
    
    remove_file_if_exists(OUTPUT_BIN_PATH)
    remove_file_if_exists(INS_SEQ_CONCAT)
    
    encode_file(INPUT_FILE_PATH, DBSNP_PATH, K_MER_SIZE)    


if __name__ == "__main__":
    main()
    