import pandas as pd
import numpy as np
from constants import *
from bitfile import *
from huffman import *

VARIANT_NAME    = 'HG004_GRCh38'
ENC_FILE_PATH   = f"../data/output/{VARIANT_NAME}_Encoded.bin"
CHR_FILE_PATH   = '../data/chr/'
TREE_PATH       = f"../data/huffman_trees/{VARIANT_NAME}.txt"

def decode(file_to_bin_file):

    with open(file_to_bin_file, 'rb') as f:
        # Read the entire file content as a bytes object
        binary_data = f.read()

        bit_string = BytesToBitString(binary_data)
        
        # Find first VINT
        padding = 0
        while bit_string[padding] != '1':

            padding += 1

        bit_string = bit_string[padding:]

        bitmap_size, bits_shifted = readBitVINT(bit_string)

        bitmap = bit_string[bits_shifted:bitmap_size]
        bit_string = bit_string[bitmap_size + bits_shifted:]

        snp_size, bits_shifted = readBitVINT(bit_string)
        bit_string = bit_string[bits_shifted:]
        
        snp_pos = []
        snp_pos_bits = 0

        for i in range(snp_size):

            pos, bits_shifted = readBitVINT(bit_string[snp_pos_bits:])
            snp_pos_bits += bits_shifted
            snp_pos.append(pos)

        print("SNP Positions Decoded")

        bit_string = bit_string[snp_pos_bits:]

        snp_nucs = []

        for i in range(0, snp_size * 2, 2):

            two_bits = bit_string[i:i+2]
            nuc = TWO_BIT_ENCODING[two_bits]
            snp_nucs.append(nuc)

        print("SNP Nucleotides Decoded")

        bit_string = bit_string[snp_size * 2:]
    
        del_size, bits_shifted = readBitVINT(bit_string)
        bit_string = bit_string[bits_shifted:]

        del_pos = []
        del_pos_bits = 0

        for i in range(del_size):

            pos, bits_shifted = readBitVINT(bit_string[del_pos_bits:])
            del_pos_bits += bits_shifted
            del_pos.append(pos)

        print("Deletion Positions Decoded")

        bit_string = bit_string[del_pos_bits:]

        del_sizes = []
        del_size_bits = 0

        for i in range(del_size):

            pos, bits_shifted = readBitVINT(bit_string[del_size_bits:])
            del_size_bits += bits_shifted
            del_sizes.append(pos)

        print("Deletion Sizes Decoded")

        bit_string = bit_string[del_size_bits:]

        ins_size, bits_shifted = readBitVINT(bit_string)
        bit_string = bit_string[bits_shifted:]

        ins_pos = []
        ins_pos_bits = 0

        for i in range(ins_size):

            pos, bits_shifted = readBitVINT(bit_string[ins_pos_bits:])
            ins_pos_bits += bits_shifted
            ins_pos.append(pos)

        print("Insertion Positions Decoded")

        bit_string = bit_string[ins_pos_bits:]

        ins_len = []
        ins_len_bits = 0

        for i in range(snp_size):

            pos, bits_shifted = readBitVINT(bit_string[ins_len_bits:])
            ins_len_bits += bits_shifted
            ins_len.append(pos)

        print("Insertion Lengths Decoded")

        bit_string = bit_string[del_pos_bits:]
        
        ins_seq = []
        ins_seq_bits = 0
        
        # At the beginning of the insertion sequence bitstring...
        # Do tree traversal and the extra bits at the end should not be able to be converted
        # This then should be caught, and then their actual two bit encodings can be given
        # Actually string length should be cleanly divisible by 16, so ins_seq_size % 16 = # of nuc left.
        
        ins_seq_bitstring_placeholder = []
        
        encoding_map = load_map_from_file(TREE_PATH)
        huffman_root = reconstruct_huffman_tree(encoding_map)
        ins_decoded  = decode_huffman(ins_seq_bitstring_placeholder, huffman_root)
            


def createRefGen(chr): 
    
    refGen = []
    
    with open(CHR_FILE_PATH + chr + ".fa", 'r', encoding='utf-8') as f:
        f.readline()
        
        while True: 
            char=f.read(1)
            
            if not char:
                break
            if char != '\n':
                refGen.append(char)
        
    return refGen






        
        
def main():   
    
    encoding_map = load_map_from_file(TREE_PATH)
    root = reconstruct_huffman_tree(encoding_map)
    
    map_encodings(root, encoding_map, "")
    
    # print(encoding_map)
  
    
       
if __name__ == "__main__":
    main()