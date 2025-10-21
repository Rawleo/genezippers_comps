import pandas as pd
import numpy as np
import os
from constants import *
from bitfile import *

CURR_DIR = os.path.dirname(__file__)
ENC_FILE_PATH = os.path.join(CURR_DIR, '../data/output/HG002_GRCh38_Encoded.bin')

def decode(file_to_bin_file):
    
    with open(file_to_bin_file, 'rb') as f:
        binary_data = f.read()

        bit_string = BytesToBitString(binary_data)

        bitmap_size, bit_string = readBitVINT(bit_string)
        print(bitmap_size)
        
def main(): 
    decode(ENC_FILE_PATH)
    
if __name__ == "__main__":
    main()