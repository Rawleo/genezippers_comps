import pandas as pd
import numpy as np
import sys
from decode import *


def compares_dbsnp(snps_df, dbsnp_path, chr):
    """
    Compare a SNPs dataframe to a dbSNP file for a given chromosome.

    @params:
    * snps_df: DataFrame with columns ['chr', 'pos', 'var_info'] representing variants to map.
    * dbsnp_path: Path to the folder containing dbsnp files (files named "<chr>.txt").
    * chr: Chromosome identifier (used to select the dbsnp file).

    @return:
    * bitmap: A string of '0'/'1' characters indicating presence of each dbsnp entry in snps_df.
    * bitmap_size_vint: A VINT-encoded size of the bitmap (result of writeBitVINT).
    * unmapped_snps_df: DataFrame of snps_df rows that were not mapped to dbsnp entries (columns ['chr','pos','var_info']).
    """

    # Read the dbSNP file for the chromosome; no header so columns are 0,1,2,...
    dbsnp_df = pd.read_csv(dbsnp_path + chr + ".txt", header=None)

    dbsnp_df['bit_array'] = 0
    snps_df['mapped'] = 0

    # Build a boolean mask for dbsnp_df rows that exist in snps_df by comparing the tuple index (chr,pos,var_info)
    match_mask = dbsnp_df.set_index([0, 1, 2]).index.isin(snps_df.set_index(['chr', 'pos', 'var_info']).index)
    dbsnp_df.loc[match_mask, 'bit_array'] = 1

    # Similarly, mark which rows in snps_df were mapped by checking membership against dbsnp_df's index
    map_mask = snps_df.set_index(['chr', 'pos', 'var_info']).index.isin(dbsnp_df.set_index([0, 1, 2]).index)
    snps_df.loc[map_mask, 'mapped'] = 1
    unmapped_snps_df = snps_df.where(snps_df['mapped'] == 0).dropna()[['chr', 'pos', 'var_info']]

    # Encode the size of the bitmap using the provided writeBitVINT function (for downstream storage/serialization)
    bitmap_size_vint = writeBitVINT(dbsnp_df.shape[0])
    bitmap = ''.join(dbsnp_df['bit_array'].astype(str).tolist())
    # Return the bitmap string, its VINT-encoded size, and the unmapped SNPs dataframe
    return bitmap, bitmap_size_vint, unmapped_snps_df


def decode_dbsnp(bit_string, dbsnp_folder_path, chr):
    """
    Decode a bitmap string to recover SNPs from a dbSNP file.
    
    @params:
    * bit_string: String of '0'/'1' chars representing presence/absence of dbSNP entries
    * dbsnp_folder_path: Path to folder containing dbSNP files
    * chr: Chromosome identifier

    @return: 
    * bitmap_df[['var_type', 'chr', 'pos', 'var_info']]: DataFrame of dbsnp entries (columns ['chr','pos','var_info']).
    * bit_string: remaining bit string
    """
    # Construct full path to chromosome-specific dbSNP file
    dbsnp_file_path = dbsnp_folder_path + chr + ".txt"

    # Extract the bitmap size from VINT encoding at start of bit_string
    bitmap_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]  # Remove the size encoding from string

    # Extract the actual bitmap portion and advance the remaining bit string
    bitmap = bit_string[:bitmap_size]
    bit_string = bit_string[bitmap_size:]

    # Read the dbSNP file and mark entries that were found in the original variants
    bitmap_df = pd.read_csv(dbsnp_file_path, header=None,names=['chr', 'pos', 'var_info'])
    bitmap_df["Found_in_Vars"] = list(bitmap)
    bitmap_df = bitmap_df.where(bitmap_df['Found_in_Vars'] == '1').dropna()
    bitmap_df['var_type'] = 0  # Initialize variant type column

    # Return filtered DataFrame with required columns and remaining bit string
    return bitmap_df[['var_type', 'chr', 'pos', 'var_info']], bit_string
    