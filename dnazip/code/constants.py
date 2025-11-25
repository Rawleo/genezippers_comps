from pathlib import Path  

"""
Directory Structure:
--------------------

dnazip/
├── code/
│   └── (your_script.py)              <-- Running script's location
└── data/
    ├── chr/                          <-- CHR_FILE_PATH
    │   └── (chromosome files)
    ├── dbSNP/                        <-- DBSNP_PATH
    │   └── (dbSNP files)
    ├── huffman_trees/                <-- TREE_PATH directory
    │   └── HG002_GRCh38.txt          <-- Example TREE_PATH file
    ├── output/                       <-- Output directory
    │   ├── HG002_GRCh38_Encoded.bin  <-- OUTPUT_BIN_PATH / ENC_FILE_PATH
    │   └── HG002_GRCh38_INS_SEQ.txt  <-- INS_SEQ_CONCAT
    └── variants/                     <-- INPUT_FILE_PATH directory
        └── HG002_GRCh38_sorted_variants.txt <-- Example INPUT_FILE_PATH file
"""

###
# DEFAULTS
###
BASE_DIR     = Path(__file__).resolve().parent.parent
OUTPUT_DIR   = BASE_DIR / 'data' / 'output'
VARIANT_NAME = 'GRCh38_ash1_v2.2_chr21'
K_MER_SIZE   = 8
DELTA_POS    = False
DBSNP_ON     = True
HUFFMAN_ON   = True

# K_MER OVERRIDE
if (not HUFFMAN_ON):
    K_MER_SIZE = 0

###
# FILEPATHS
###
DBSNP_PATH                  = f"{BASE_DIR}/data/dbSNP/"
CHR_FILE_PATH               = f'{BASE_DIR}/data/chr/'
INPUT_FILE_PATH             = f"{BASE_DIR}/data/variants/{VARIANT_NAME}_sorted_variants.txt"
OUTPUT_BIN_PATH             = f"{OUTPUT_DIR}/{VARIANT_NAME}_{DELTA_POS}_{DBSNP_ON}_{HUFFMAN_ON}_{K_MER_SIZE}_Encoded.bin"
OUTPUT_DEC_PATH             = f"{OUTPUT_DIR}/{VARIANT_NAME}_Decoded.txt"
INS_SEQ_CONCAT              = f"{OUTPUT_DIR}/{VARIANT_NAME}_INS_SEQ.txt"
INS_DEC_CONCAT              = f"{OUTPUT_DIR}/{VARIANT_NAME}_INS_DEC.txt"
ENC_FILE_PATH               = f"{OUTPUT_DIR}/{VARIANT_NAME}_{DELTA_POS}_{DBSNP_ON}_{HUFFMAN_ON}_{K_MER_SIZE}_Encoded.bin"
TREE_PATH                   = f"{BASE_DIR}/data/huffman_trees/{VARIANT_NAME}.txt"
FIGURE_PATH                 = f"{BASE_DIR}/figures/{VARIANT_NAME}_{DELTA_POS}_{DBSNP_ON}_{HUFFMAN_ON}_{K_MER_SIZE}_Figure.png"
FIGURE_REMDBSNP_PATH        = f"{BASE_DIR}/figures/{VARIANT_NAME}_removed_dbSNP.png"
TIME_CSV_PATH               = f"{OUTPUT_DIR}/csv/{VARIANT_NAME}_times.csv"

###
# Array of Chromosomes
###

CHROMOSOMES = [
    'chr21'
]

###
# Dictionaries
###

NUC_ENCODING = {
    "A": "00",
    "C": "01",
    "G": "10",
    "T": "11",
}

TWO_BIT_ENCODING = {
    "00": "A",
    "01": "C",
    "10": "G",
    "11": "T",
}

VARIATION_FLAG = {
    'SNPS': 0,
    'DELETIONS': 1,
    'INSERTIONS': 2,
}
