import pandas as pd
import numpy as np
import sys
from decode import *

def compares_dbsnp(snps_df, dbsnp_path, chr):

    dbsnp_df = pd.read_csv(dbsnp_path + chr + ".txt", header=None)
    dbsnp_df['bit_array'] = 0
    snps_df['mapped'] = 0

    # Set bit_array to 1 where dbsnp_df row matches snps_df row (columns 'chr', 'pos', 'var_info')
    match_mask = dbsnp_df.set_index([0, 1, 2]).index.isin(snps_df.set_index(['chr', 'pos', 'var_info']).index)
    dbsnp_df.loc[match_mask, 'bit_array'] = 1

    map_mask = snps_df.set_index(['chr', 'pos', 'var_info']).index.isin(dbsnp_df.set_index([0, 1, 2]).index)
    snps_df.loc[map_mask, 'mapped'] = 1
    unmapped_snps_df = snps_df.where(snps_df['mapped'] == 0).dropna()[['chr', 'pos', 'var_info']]

    bitmap_size_vint = writeBitVINT(dbsnp_df.shape[0])
    bitmap = ''.join(dbsnp_df['bit_array'].astype(str).tolist())

    # Return bit_array column as a single string
    return bitmap, bitmap_size_vint, unmapped_snps_df

def decode_dbsnp(bit_string, dbsnp_folder_path, chr):

    dbsnp_file_path = dbsnp_folder_path + chr + ".txt"

    bitmap_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]

    bitmap = bit_string[:bitmap_size]
    bit_string = bit_string[bitmap_size:]

    bitmap_df = pd.read_csv(dbsnp_file_path, header=None,names=['chr', 'pos', 'var_info'])
    bitmap_df["Found_in_Vars"] = list(bitmap)
    bitmap_df = bitmap_df.where(bitmap_df['Found_in_Vars'] == '1').dropna()
    bitmap_df['var_type'] = 0

    return bitmap_df[['var_type', 'chr', 'pos', 'var_info']], bit_string

    