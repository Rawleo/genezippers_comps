import pandas as pd
import numpy as np
from vint import *
from constants import *
from decode import *


def encode_SNPs(snps_df):

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

    snp_nucs = []

    for i in range(0, snp_size * 2, 2):

        two_bits = bit_string[i:i+2]
        nuc = TWO_BIT_ENCODING[two_bits]
        snp_nucs.append(nuc)

    # print("SNP Nucleotides Decoded")

    bit_string = bit_string[snp_size * 2:]

    snp_data = {"snp_pos":None,
                "snp_nucs":None
    }

    snp_data["snp_pos"] = snp_pos
    snp_data["snp_nucs"] = snp_nucs
    
    snp_df = pd.DataFrame(snp_data)
    snp_df['chr'] = chr

    return snp_df, bit_string