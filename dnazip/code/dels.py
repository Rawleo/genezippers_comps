import pandas as pd
import numpy as np
from decode import *
from reader import *


def encode_dels(dels_df):
    """
    Encodes deletion variants from a DataFrame into compressed bit strings
    
    @params:
    * dels_df: DataFrame containing deletion variants with columns 'pos' and 'var_info'
    
    @return:
    * del_size_vint: Bit string containing number of deletions
    * pos_bitstr: Bit string containing encoded deletion positions 
    * len_bitstr: Bit string containing encoded deletion lengths
    """
    if DELTA_POS:
        # Convert absolute positions to relative (delta) positions for better compression
        dels_df = dels_df.sort_values(by='pos') 
        dels_df = dels_df.reset_index(drop=True) 

        # Calculate delta positions by taking differences between consecutive positions
        first_pos = dels_df['pos'].iloc[0]
        dels_df['pos'] = dels_df['pos'].diff() 
        dels_df.loc[0, 'pos'] = first_pos

    # Encode the total number of deletions using variable-length integer (VINT)
    del_size_vint = writeBitVINT(dels_df.shape[0])
    
    # Encode positions and deletion lengths as VINTs
    dels_df["pos"]        = dels_df["pos"].astype(int).apply(writeBitVINT)
    dels_df["var_info"]   = dels_df["var_info"].apply(lambda x: len(x.split('/')[0])).apply(writeBitVINT)
    
    # Combine all encoded values into final bit strings
    pos_bitstr    = ''.join(dels_df["pos"].astype(str).tolist())
    len_bitstr    = ''.join(dels_df["var_info"].astype(str).tolist())
    
    return del_size_vint, pos_bitstr, len_bitstr


def decode_dels(bit_string, chr):
    """
    Decodes deletion variants from a compressed bit string
    
    @params:
    * bit_string: Compressed binary string containing encoded deletion data
    * chr: Chromosome number/identifier
    
    @return:
    * del_df[['var_type', 'chr', 'pos', 'var_info']]: DataFrame containing decoded deletion variants
    * bit_string: Remaining unused bit string
    """
    # Read number of deletions using VINT decoding
    del_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]

    # Decode deletion positions from VINT-encoded values
    del_pos, del_pos_bits = parse_vints(bit_string, del_size)
    bit_string = bit_string[del_pos_bits:]

    # Decode deletion sizes from VINT-encoded values 
    del_sizes, del_size_bits = parse_vints(bit_string, del_size)
    bit_string = bit_string[del_size_bits:]

    # Create initial dictionary for DataFrame
    del_data = {"var_type":None,
                "chr":None,
                "pos":del_pos,
                "del_sizes":del_sizes,
                "var_info":None
    }
    
    # Convert to DataFrame and add chromosome and variant type
    del_df = pd.DataFrame(del_data)
    del_df['chr'] = chr
    del_df['var_type'] = 1

    # If using delta encoding, convert relative positions back to absolute
    if DELTA_POS:
        del_df['pos'] = del_df['pos'].cumsum()

    # Get reference nucleotides at deletion positions
    del_df['ref_seq'] = get_del_nucs(list(del_df['pos']), del_sizes, chr)

    # Format variant info string (ref/alt format)
    del_df['var_info'] = del_df.apply(lambda row: row['ref_seq'] + '/' + ('-' * row['del_sizes']),axis=1)

    # Return filtered DataFrame and remaining bit string
    return del_df[['var_type', 'chr', 'pos', 'var_info']], bit_string