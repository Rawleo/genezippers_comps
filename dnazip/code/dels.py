import pandas as pd
import numpy as np
from vint import *

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
