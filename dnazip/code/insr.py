from vint import *
from huffman import *
import pandas as pd
from constants import *

def encode_ins(insr_df, k_mer_size):
    
    # Calculate size of insertions and convert to VINT
    insr_size_vint = writeBitVINT(insr_df.shape[0])
    
    # Convert positions to VINTs
    insr_df["pos"] = insr_df["pos"].astype(int).apply(writeBitVINT)
    
    # Split insertions into relevant nucleotides
    insr_df["var_info"] = insr_df["var_info"].apply(lambda x: x.split('/')[1])
    
    # Calculate length of each insertion sequence
    insr_df["var_length"] = insr_df["var_info"].apply(lambda x: len(x)).apply(writeBitVINT)

    # Concatenate all insertion sequences for Huffman coding
    ins_seq = ''.join(insr_df["var_info"].astype(str).tolist())
    
    # Concatenate all position VINTs
    pos_bitstr = ''.join(insr_df["pos"].astype(str).tolist())
    
    # Concatenate all position length VINTs
    len_bitstr = ''.join(insr_df["var_length"].astype(str).tolist())

    ### THEN RUN HUFFMAN ENCODING STUFF FOR THIS CHROMOSOME
    ins_seq_bitstr, encoding_map  = run_huffman(ins_seq, k_mer_size)
    bitstr_len_vint = writeBitVINT(len(ins_seq_bitstr))
        
    return insr_size_vint, pos_bitstr, len_bitstr, bitstr_len_vint, ins_seq_bitstr, encoding_map


def main():
    
    return
    
    
if __name__ == "__main__":
    main()