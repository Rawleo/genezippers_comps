import pandas as pd
import numpy as np
import os
from constants import *
from huffman import *
from bitfile import *
from dbsnp import *
from dels import *
from snp import *
from insr import *
from decode import *
from plot import *


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
    
    encoding_map = create_and_export_huffman_map(variants_df)

    for chr in CHROMOSOMES:
        # Choose current chromosome
        chr_df = variants_df.where(variants_df['chr'] == chr)

        # Variation dataframes
        snps_df = chr_df.where(chr_df['var_type'] == 0).dropna()
        dels_df = chr_df.where(chr_df['var_type'] == 1).dropna()
        insr_df = chr_df.where(chr_df['var_type'] == 2).dropna()
        
        ### Start of SNPs
        # Encoding of Mapped SNPs
        bitmap, bitmap_size_vint, unmapped_df = compares_dbsnp(snps_df, dbSNP_path, chr)

        # Encoding of Unmapped SNPs
        snp_size_vint, unmapped_pos_bitstr, unmapped_nuc_bitstr = encode_SNPs(unmapped_df)
        snp_bitstring = bitmap_size_vint + bitmap + snp_size_vint + unmapped_pos_bitstr + unmapped_nuc_bitstr
        export_as_binary(OUTPUT_BIN_PATH, snp_bitstring)
                    
        ### Start of DELs
        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = encode_dels(dels_df)

        # Add above to bin 
        del_bitstring = del_size_vint + del_pos_bitstr + del_len_bitstr
        export_as_binary(OUTPUT_BIN_PATH, del_bitstring)

        ### Start of INSRs 
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = encode_ins(insr_df, encoding_map, k_mer_size)
        
        # Add above to bin        
        insertion_bitstring = ins_size_vint + ins_pos_bitstr + ins_len_bitstr + ins_bitstr_len_vint + ins_seq_bitstr
        export_as_binary(OUTPUT_BIN_PATH, insertion_bitstring)

'''
Decoding of a compressed binary file into a variant file, 
processing the data chromosome by chromosome.

@params: 
 * bit_string - the encoded bit_string of 1's and 0's.
@return:
 * None, writes the encoded outout to 'OUTPUT_DEC_PATH'.
'''
def decode_file(bit_string):
    
    encoding_map = load_map_from_file(TREE_PATH)
    huffman_root = reconstruct_huffman_tree(encoding_map)
    decode_df = pd.DataFrame()
    
    for chr in CHROMOSOMES:

        ### Find SNPs
        bit_string = add_padding(bit_string)
        bitmap_df, bit_string = decode_dbsnp(bit_string, DBSNP_PATH, chr)
        snp_df, bit_string = decode_SNPs(bit_string, chr)
        # print("Bitmap Size: " + str(bitmap_size))

        ### Find DELs
        bit_string = add_padding(bit_string)
        del_df, bit_string = decode_dels(bit_string, chr)
        # print("Deletion Sizes Decoded")

        ### Find INS
        bit_string = add_padding(bit_string)
        ins_df, bit_string = decode_ins(bit_string, huffman_root, chr)

        decode_df = pd.concat([decode_df, bitmap_df, snp_df, del_df, ins_df])
    
    # Formatting
    decode_df['pos'] = decode_df['pos'].astype(int)

    # Output Decoded File
    decode_df.sort_values(by=['var_type', 'chr', 'pos']).to_csv(OUTPUT_DEC_PATH,
                     index=False,
                     header=None)
    


def remove_file_if_exists(filepath):
    if os.path.exists(filepath):
        print("Removing:", filepath)
        os.remove(filepath)
    else:
        print("This file does not exist:", filepath)
        print("Continuing...") 


def main(): 
    # remove_file_if_exists(OUTPUT_BIN_PATH)
    # remove_file_if_exists(INS_SEQ_CONCAT)
    # remove_file_if_exists(OUTPUT_BIN_PATH)
    # encode_file(INPUT_FILE_PATH, DBSNP_PATH, K_MER_SIZE)

        
    # bit_string = readBinFile(ENC_FILE_PATH)
    # remove_file_if_exists(INS_DEC_CONCAT)
    # decode_file(bit_string)

    # Create Figures
    compression_comparison(INPUT_FILE_PATH, ENC_FILE_PATH, VARIANT_NAME, FIGURE_PATH)


if __name__ == "__main__":
    main()
    