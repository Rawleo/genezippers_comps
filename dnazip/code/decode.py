import pandas as pd
import numpy as np
from constants import *
from bitfile import *
from huffman import *

VARIANT_NAME    = 'HG002_GRCh38'
ENC_FILE_PATH   = f"../data/output/{VARIANT_NAME}_Encoded.bin"
CHR_FILE_PATH   = '../data/chr/'
TREE_PATH       = f"../data/huffman_trees/{VARIANT_NAME}.txt"

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

            bitmap_size, bits_shifted = readBitVINT(bit_string)
            bit_string = bit_string[bits_shifted:]

            bitmap = bit_string[:bitmap_size]
            bit_string = bit_string[bitmap_size:]

            # print("Bitmap Size: " + str(bitmap_size))

            snp_size, bits_shifted = readBitVINT(bit_string)
            bit_string = bit_string[bits_shifted:]

            # print("SNPs Size: " + str(snp_size))
            
            snp_pos, snp_pos_bits = parse_vints(bit_string, snp_size)
            bit_string = bit_string[snp_pos_bits:]

            # print("SNP Positions Decoded")

            snp_nucs = []

            for i in range(0, snp_size * 2, 2):

                two_bits = bit_string[i:i+2]
                nuc = TWO_BIT_ENCODING[two_bits]
                snp_nucs.append(nuc)

            # print("SNP Nucleotides Decoded")

            bit_string = bit_string[snp_size * 2:]

            bit_string = add_padding(bit_string)
        
            del_size, bits_shifted = readBitVINT(bit_string)
            bit_string = bit_string[bits_shifted:]

            # print("Dels Size: " + str(del_size))

            del_pos, del_pos_bits = parse_vints(bit_string, del_size)
            bit_string = bit_string[del_pos_bits:]

            # print("Deletion Positions Decoded")

            del_size, del_size_bits = parse_vints(bit_string, del_size)
            bit_string = bit_string[del_size_bits:]

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

            
            #Making df example:

            snp_data = {
                 "snp_pos":None,
                 "snp_nucs":None
            }

            # snp_data["snp_pos"] = snp_pos
            # snp_data["snp_nucs"] = snp_nucs
            
            # snp_df = pd.DataFrame(snp_data)
            # display(snp_df)





    
        
def main():   
    
    bit_string = readBinFile(ENC_FILE_PATH)
    decode(bit_string)
  
    
       
if __name__ == "__main__":
    main()