import pandas as pd
import numpy as np
from constants import *
from decode import *
from reader import *


def encode_SNPs(snps_df):

    if (DELTA_POS):

        # Prepare df to get relative (DELTA) positions
        snps_df = snps_df.sort_values(by='pos') 
        snps_df = snps_df.reset_index(drop=True) 

        # Set DELTA positions 
        first_pos = snps_df['pos'].iloc[0]
        snps_df['pos'] = snps_df['pos'].diff() 
        snps_df.loc[0, 'pos'] = first_pos

    # Convert positions to VINTs
    snps_df['pos'] = snps_df['pos'].astype(int).apply(writeBitVINT)

    # Convert nucleotides to two-bit representations
    snps_df['var_info'] = snps_df['var_info'].apply(lambda x: NUC_ENCODING[x.split('/')[-1]])

    pos_bitstring = ''.join(snps_df['pos'].astype(str).tolist())
    nuc_bitstring = ''.join(snps_df['var_info'].astype(str).tolist())
    snp_size_vint = writeBitVINT(snps_df.shape[0])

    return snp_size_vint, pos_bitstring, nuc_bitstring

def decode_SNPs(bit_string, chr):

    snp_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]

    # print("SNPs Size: " + str(snp_size))
    
    snp_pos, snp_pos_bits = parse_vints(bit_string, snp_size)
    bit_string = bit_string[snp_pos_bits:]

    # print("SNP Positions Decoded")

    alt_nucs = []

    for i in range(0, snp_size * 2, 2):

        two_bits = bit_string[i:i+2]
        nuc = TWO_BIT_ENCODING[two_bits]
        alt_nucs.append(nuc)

    # print("SNP Nucleotides Decoded")

    bit_string = bit_string[snp_size * 2:]

    snp_data = {"var_type":None,
                "chr":None,
                "pos":snp_pos,
                "alt_nucs":alt_nucs,
                "ref_nucs":None,
                "var_info":None
    }

    snp_df = pd.DataFrame(snp_data)
    snp_df['chr'] = chr

    if DELTA_POS: 
        
        snp_df['pos'] = snp_df['pos'].cumsum()
    
    snp_df['ref_nucs'] = get_snp_nuc(list(snp_df['pos']), chr, CHR_FILE_PATH)
    snp_df['var_type'] = 0
    snp_df['var_info'] = snp_df['ref_nucs'] + "/" + snp_df['alt_nucs']

    return snp_df[['var_type', 'chr', 'pos', 'var_info']], bit_string