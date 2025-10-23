from vint import *
from huffman import *
from constants import *
import pandas as pd
import os


def ins_seq_to_bitstr(ins_seq, encoding_map, k_mer_size):
    ins_seq_kmer = insertions_to_kmers(ins_seq, k_mer_size)
    ins_seq_bitstr  = encode_insertions(encoding_map, ins_seq_kmer)
    
    return ins_seq_bitstr


def create_insertion_seq_file(chr, ins_seq, out_path):
    
    result = f"{chr} Insertion Sequence: " + ins_seq + '\n'
    
    append_as_txt(INS_SEQ_CONCAT, result)
    

def encode_ins(insr_df, encoding_map, k_mer_size):
    
    # Current chromosome
    chr = insr_df["chr"].values[0]
    
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

    # Huffman encoding of the current chromosome's insertion sequences
    ins_seq_bitstr  = ins_seq_to_bitstr(ins_seq, encoding_map, k_mer_size)

    create_insertion_seq_file(chr, ins_seq, INS_SEQ_CONCAT)

    # VINT for bitstring length
    bitstr_len_vint = writeBitVINT(len(ins_seq_bitstr))
        
    return insr_size_vint, pos_bitstr, len_bitstr, bitstr_len_vint, ins_seq_bitstr


def main():
    
    return
    
    
if __name__ == "__main__":
    main()