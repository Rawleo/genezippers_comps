import pandas as pd
import numpy as np
from constants import *
from bitfile import *
from huffman import *
from dbsnp import *
from snp import *
from dels import *


def add_padding(bit_string):

    # Find first VINT
    padding = 0
    while bit_string[padding] != '1':

        padding += 1

    return bit_string[padding:]


def readBinFile(file_to_bin_file):

    with open(file_to_bin_file, 'rb') as f:

        binary_data = f.read()

        bit_string = BytesToBitString(binary_data)

    return bit_string


def parse_vints(bit_string, size):
    items = []
    shifted_bits = 0

    for _ in range(size):
        pos, bits_shifted = readBitVINT_from(bit_string, shifted_bits)
        shifted_bits += bits_shifted
        items.append(pos)

    return items, shifted_bits


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


def decode(bit_string):
    
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





    
        
def main():   
    
    bit_string = readBinFile(ENC_FILE_PATH)
    decode(bit_string)
  
    
       
if __name__ == "__main__":
    main()