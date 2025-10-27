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
    
    # Will contain the Huffman encoding maps for each chromosome
    # and the number of k_mers that were encoded    
    encoding_dict = {}

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
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr, encoding_tuple = encode_ins(insr_df, k_mer_size)
        
        # Push encoding tuple into encoding_dict: 
        # key: chr
        # value: (chr_encoding_map_dict, number of k_mers)
        encoding_dict[chr] = encoding_tuple
        
        # Add above to bin        
        insertion_bitstring = ins_size_vint + ins_pos_bitstr + ins_len_bitstr + ins_bitstr_len_vint + ins_seq_bitstr
        export_as_binary(OUTPUT_BIN_PATH, insertion_bitstring)
    
    # Export the final encoding dictionary    
    export_as_txt(TREE_PATH, encoding_dict)


'''
Decoding of a compressed binary file into a variant file, 
processing the data chromosome by chromosome.
@params: 
 * bit_string - the encoded bit_string of 1's and 0's.
@return:
 * None, writes the encoded outout to 'OUTPUT_DEC_PATH'.
'''
def decode_file(bit_string):
    
    # Read in encoding_dict file
    encoding_dict = load_dict_from_file(TREE_PATH)
    
    # Construct decode data frame
    decode_df = pd.DataFrame()
    
    for chr in CHROMOSOMES:
        ### Reconstructing Huffman tree for the select chr
        huffman_root = reconstruct_huffman_tree(encoding_dict[chr][0])
        number_of_kmers = encoding_dict[chr][1]

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
        ins_df, bit_string = decode_ins(bit_string, huffman_root, number_of_kmers, chr)

        ### Adding everything into the decode_df
        decode_df = pd.concat([decode_df, bitmap_df, snp_df, del_df, ins_df])
    
    # Formatting
    decode_df['pos'] = decode_df['pos'].astype(int)

    # Output Decoded File
    decode_df.sort_values(by=['var_type', 'chr', 'pos']).to_csv(OUTPUT_DEC_PATH,
                     index=False,
                     header=None) # type: ignore
    

'''
Deletes a file if it exists. Useful for files that are
appended to.
@params: 
 * filepath - file path (str) to the file to delete. 
@return:
 * None, deletes the file if it exists.
'''
def remove_file_if_exists(filepath):
    if os.path.exists(filepath):
        print("Removing:", filepath)
        os.remove(filepath)
    else:
        print("This file does not exist:", filepath)
        print("This file does exist. Continuing...") 


def main(): 
    
    start_cpu_time_encode, start_wall_time_encode = record_current_times()
    
    remove_file_if_exists(OUTPUT_BIN_PATH)
    remove_file_if_exists(INS_SEQ_CONCAT)
    remove_file_if_exists(OUTPUT_BIN_PATH)
    encode_file(INPUT_FILE_PATH, DBSNP_PATH, K_MER_SIZE)
    
    end_cpu_time_encode, end_wall_time_encode = record_current_times()
    
    print("CPU Time Encode:", time_difference(end_cpu_time_encode, start_cpu_time_encode), "seconds")
    print("Wall Time Encode:", time_difference(end_wall_time_encode, start_wall_time_encode), "seconds")
    
    start_cpu_time_decode, start_wall_time_decode = record_current_times()
        
    bit_string = readBinFile(ENC_FILE_PATH)
    remove_file_if_exists(INS_DEC_CONCAT)
    decode_file(bit_string)
    
    end_cpu_time_decode, end_wall_time_decode = record_current_times()

    print("CPU Time Decode:", time_difference(end_cpu_time_decode, start_cpu_time_decode), "seconds")
    print("Wall Time Decode:", time_difference(end_wall_time_decode, start_wall_time_decode), "seconds")

    # Create Figures
    compression_comparison(INPUT_FILE_PATH, ENC_FILE_PATH, VARIANT_NAME, FIGURE_PATH)


if __name__ == "__main__":
    main()
    