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








    
        
def main():   
    
    bit_string = readBinFile(ENC_FILE_PATH)
    decode(bit_string)
  
    
       
if __name__ == "__main__":
    main()