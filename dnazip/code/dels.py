import pandas as pd
import numpy as np
from vint import *
from decode import *

def encode_dels(dels_df):
    # Calculate number of DELs
    del_size_vint = writeBitVINT(dels_df.shape[0])
    
    # Convert position and variation length info into vints 
    dels_df["pos"]        = dels_df["pos"].astype(int).apply(writeBitVINT)
    dels_df["var_info"]   = dels_df["var_info"].apply(lambda x: len(x.split('/')[0])).apply(writeBitVINT)
    
    # Concatenate respective columns into bitstring
    pos_bitstr    = ''.join(dels_df["pos"].astype(str).tolist())
    len_bitstr    = ''.join(dels_df["var_info"].astype(str).tolist())
    
    return del_size_vint, pos_bitstr, len_bitstr

def decode_dels(bit_string, chr):

    del_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]

    # print("Dels Size: " + str(del_size))

    del_pos, del_pos_bits = parse_vints(bit_string, del_size)
    bit_string = bit_string[del_pos_bits:]

    # print("Deletion Positions Decoded")

    del_sizes, del_size_bits = parse_vints(bit_string, del_size)
    bit_string = bit_string[del_size_bits:]

    del_data = {"del_pos":None,
                "del_sizes":None
    }

    del_data["del_pos"] = del_pos
    del_data["del_sizes"] = del_sizes
    
    del_df = pd.DataFrame(del_data)
    del_df['chr'] = chr

    return del_df, bit_string