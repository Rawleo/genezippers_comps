import pandas as pd
import numpy as np
from vint import *
from constants import *


def encode_SNPs(snps_df):

    # Convert positions to VINTs
    snps_df['pos'] = snps_df['pos'].astype(int).apply(writeBitVINT)

    # Convert nucleotides to two-bit representations
    snps_df['var_info'] = snps_df['var_info'].apply(lambda x: NUC_ENCODING[x.split('/')[-1]])

    pos_bitstring = ''.join(snps_df['pos'].astype(str).tolist())
    nuc_bitstring = ''.join(snps_df['var_info'].astype(str).tolist())
    snp_size_vint = writeBitVINT(snps_df.shape[0])

    return snp_size_vint, pos_bitstring, nuc_bitstring