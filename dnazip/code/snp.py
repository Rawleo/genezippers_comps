import pandas as pd
import numpy as np
from constants import *
from decode import *
from reader import *


def encode_SNPs(snps_df):
    """
    Encodes SNP data into a compressed binary format

    @params:
    * snps_df: DataFrame containing SNP information

    @return:
    * tuple containing (size_vint, positions_bitstring, nucleotides_bitstring)
    """

    if (DELTA_POS):
        # If using delta encoding for positions:
        # Sort positions in ascending order and reset index
        snps_df = snps_df.sort_values(by='pos') 
        snps_df = snps_df.reset_index(drop=True) 

        # Calculate delta/relative positions by taking differences
        # Store first position separately since it has no previous value
        first_pos = snps_df['pos'].iloc[0]
        snps_df['pos'] = snps_df['pos'].diff() 
        snps_df.loc[0, 'pos'] = first_pos

    # Convert each position to variable-length integer (VINT) binary representation
    snps_df['pos'] = snps_df['pos'].astype(int).apply(writeBitVINT)

    # Convert alternate nucleotides to 2-bit encoding
    snps_df['var_info'] = snps_df['var_info'].apply(lambda x: NUC_ENCODING[x.split('/')[-1]])

    # Concatenate all encoded data into bitstrings
    pos_bitstring = ''.join(snps_df['pos'].astype(str).tolist())  # Position bitstring
    nuc_bitstring = ''.join(snps_df['var_info'].astype(str).tolist())  # Nucleotide bitstring
    snp_size_vint = writeBitVINT(snps_df.shape[0])  # Number of SNPs as VINT

    return snp_size_vint, pos_bitstring, nuc_bitstring

def decode_SNPs(bit_string, chr):
    """
    Decodes SNP data from compressed binary format back to DataFrame

    @params:
    * bit_string: Binary string containing encoded SNP data
    * chr: Chromosome number
    
    @return:
    * tuple containing (decoded SNP DataFrame, remaining bit string)
    """

    # Read number of SNPs from VINT encoding
    snp_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]
    
    # Extract and decode position values
    snp_pos, snp_pos_bits = parse_vints(bit_string, snp_size)
    bit_string = bit_string[snp_pos_bits:]

    # Decode alternate nucleotides from 2-bit encoding
    alt_nucs = []
    for i in range(0, snp_size * 2, 2):
        two_bits = bit_string[i:i+2]
        nuc = TWO_BIT_ENCODING[two_bits]
        alt_nucs.append(nuc)

    # Remove processed nucleotide bits
    bit_string = bit_string[snp_size * 2:]

    # Create dictionary with SNP data
    snp_data = {"var_type":None,
                "chr":None,
                "pos":snp_pos,
                "alt_nucs":alt_nucs,
                "ref_nucs":None,
                "var_info":None
    }

    # Convert to DataFrame and add chromosome info
    snp_df = pd.DataFrame(snp_data)
    snp_df['chr'] = chr

    # If using delta encoding, convert relative positions to absolute
    if DELTA_POS: 
        snp_df['pos'] = snp_df['pos'].cumsum()
    
    # Get reference nucleotides and create variant info
    snp_df['ref_nucs'] = get_snp_nuc(list(snp_df['pos']), chr, CHR_FILE_PATH)
    snp_df['var_type'] = 0
    snp_df['var_info'] = snp_df['ref_nucs'] + "/" + snp_df['alt_nucs']

    return snp_df[['var_type', 'chr', 'pos', 'var_info']], bit_string