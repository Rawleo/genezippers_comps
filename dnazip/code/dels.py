import pandas as pd
import numpy as np
from decode import *
from reader import *

def encode_dels(dels_df):

    if DELTA_POS:

        # Prepare df to get relative (DELTA) positions
        dels_df = dels_df.sort_values(by='pos') 
        dels_df = dels_df.reset_index(drop=True) 

        # Set DELTA positions 
        first_pos = dels_df['pos'].iloc[0]
        dels_df['pos'] = dels_df['pos'].diff() 
        dels_df.loc[0, 'pos'] = first_pos

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

    del_data = {"var_type":None,
                "chr":None,
                "pos":del_pos,
                "del_sizes":del_sizes,
                "var_info":None
    }
    
    del_df = pd.DataFrame(del_data)
    
    del_df['chr'] = chr
    del_df['var_type'] = 1

    if DELTA_POS:

        del_df['pos'] = del_df['pos'].cumsum()

    del_df['ref_seq'] = get_del_nucs(list(del_df['pos']), del_sizes, chr)

    del_df['var_info'] = del_df.apply(lambda row: row['ref_seq'] + '/' + ('-' * row['del_sizes']),axis=1)

    return del_df[['var_type', 'chr', 'pos', 'var_info']], bit_string