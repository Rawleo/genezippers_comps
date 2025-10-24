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
    encoding_map = run_insr_huffman(ins_seq, k_mer_size)
    
    # print(encoding_map)
    
    export_as_txt(f"../data/huffman_trees/{VARIANT_NAME}.txt", encoding_map)

    for chr in chr_list:

        # Choose current chromosome
        chr_df = variants_df.where(variants_df['chr'] == chr)

        # Variation dataframes
        snps_df = chr_df.where(chr_df['var_type'] == 0).dropna()
        dels_df = chr_df.where(chr_df['var_type'] == 1).dropna()
        insr_df = chr_df.where(chr_df['var_type'] == 2).dropna()
        

        # Encoding of Mapped SNPs
        bitmap, bitmap_size_vint, unmapped_df = compares_dbsnp(snps_df, dbSNP_path, chr)

        # Encoding of Unmapped SNPs
        snp_size_vint, unmapped_pos_bitstr, unmapped_nuc_bitstr = encode_SNPs(unmapped_df)
        snp_bitstring = bitmap_size_vint + bitmap + snp_size_vint + unmapped_pos_bitstr + unmapped_nuc_bitstr
        export_as_binary(OUTPUT_BIN_PATH, snp_bitstring)
                    
        # Start of DELs

        # Encoding of DELs
        del_size_vint, del_pos_bitstr, del_len_bitstr = encode_dels(dels_df)

        
        ### Add above to bin 
        del_bitstring = del_size_vint + del_pos_bitstr + del_len_bitstr
        export_as_binary(OUTPUT_BIN_PATH, del_bitstring)

        # Start of INSRs 
        # Encoding of INSRs
        ins_size_vint, ins_pos_bitstr, ins_len_bitstr, ins_bitstr_len_vint, ins_seq_bitstr = encode_ins(insr_df, encoding_map, k_mer_size)
        
        ### Add above to bin        
        insertion_bitstring = ins_size_vint + ins_pos_bitstr + ins_len_bitstr + ins_bitstr_len_vint + ins_seq_bitstr
        export_as_binary(OUTPUT_BIN_PATH, insertion_bitstring)

def decode_file(bit_string):
    
        encoding_map = load_map_from_file(TREE_PATH)
        huffman_root = reconstruct_huffman_tree(encoding_map)
        
        for chr in CHROMOSOMES:

            bit_string = add_padding(bit_string)
            bitmap_df, bit_string = decode_dbsnp(bit_string, DBSNP_PATH, chr)
            snp_df, bit_string = decode_SNPs(bit_string, chr)
            # print("Bitmap Size: " + str(bitmap_size))
            

            bit_string = add_padding(bit_string)
            del_df, bit_string = decode_dels(bit_string, chr)
            # print("Deletion Sizes Decoded")

            bit_string = add_padding(bit_string)
            ins_size, bits_shifted = readBitVINT(bit_string)
            bit_string = bit_string[bits_shifted:]

            # print("Ins Size: " + str(ins_size))

            ins_pos, ins_pos_bits = parse_vints(bit_string, ins_size)
            bit_string = bit_string[ins_pos_bits:]

            # print("Insertion Positions Decoded")

            ins_lens, ins_len_bits = parse_vints(bit_string, ins_size)
            bit_string = bit_string[ins_len_bits:]

            bitstr_len, bits_shifted = readBitVINT(bit_string)
            bit_string = bit_string[bits_shifted:]

            # print("Bitstr Len: " + str(bitstr_len))

            ins_bitstring = bit_string[:bitstr_len]
            bit_string = bit_string[bitstr_len:]
            
            # Nucleotides after mod 16
            extra_nuc_bit_len = len(ins_bitstring) % 16
            extra_nuc_bitmap = ins_bitstring[:extra_nuc_bit_len]
            extra_nuc = []
            
            huffman_bitmap = ins_bitstring[:len(ins_bitstring) - extra_nuc_bit_len] 
            
            for i in range(len(extra_nuc_bitmap) // 2):
                extra_nuc.append(TWO_BIT_ENCODING[extra_nuc_bitmap[i:i+2]])

            # Final insertion sequence
            ins_seq  = decode_huffman(huffman_bitmap, huffman_root)
            
            print(chr, "Insertion Sequence:", ins_seq)


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

    bit_string = readBinFile(ENC_FILE_PATH)
    decode(bit_string)


if __name__ == "__main__":
    main()
    