import bitfile, dbsnp, dels, snp, insr, os
import pandas as pd
import numpy as np
from constants import *


'''
Encoding of a variant file into a compressed binary file, 
processing the data chromosome by chromosome.

@params: 
 * input_file_path - file path (str) to the input variant file. 
 * dbSNP_path - directory path (str) containing dbSNP reference files.
 * k_mer_size - integer size of the k-mers.
@return:
 * None, writes the encoded outout to 'OUTPUT_BIN_PATH'.
'''
def encode_file(input_file_path, dbSNP_path, k_mer_size):
    
    variants_df = pd.read_csv(input_file_path, 
                              names = ['var_type', 'chr', 'pos', 'var_info'],
                              header = None)
    
    encoding_map = insr.create_and_export_huffman_map(variants_df)

    for chr in CHROMOSOMES:
        # Choose current chromosome
        chr_df = variants_df.where(variants_df['chr'] == chr)

        # Variation dataframes
        snps_df = chr_df.where(chr_df['var_type'] == 0).dropna()
        dels_df = chr_df.where(chr_df['var_type'] == 1).dropna()
        insr_df = chr_df.where(chr_df['var_type'] == 2).dropna()
        
        ### Start of SNPs
        # Encoding of Mapped SNPs
        bitmap, bitmap_size_vint, unmapped_df = dbsnp.compares_dbsnp(snps_df, dbSNP_path, chr)

        # Encoding of Unmapped SNPs
        snp_size_vint, unmapped_pos_bitstr, unmapped_nuc_bitstr = snp.encode_SNPs(unmapped_df)
        snp_bitstring = bitmap_size_vint + bitmap + snp_size_vint + unmapped_pos_bitstr + unmapped_nuc_bitstr
        
        # Add SNP encodings to bin
        bitfile.export_as_binary(OUTPUT_BIN_PATH, snp_bitstring)
                    
        ### Start of DELs
        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = dels.encode_dels(dels_df)

        # Add above to bin 
        del_bitstring = del_size_vint + del_pos_bitstr + del_len_bitstr
        bitfile.export_as_binary(OUTPUT_BIN_PATH, del_bitstring)

        ### Start of INSRs 
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = insr.encode_ins(insr_df, encoding_map, k_mer_size)
        
        # Add above to bin        
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
    