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
VARIANT_NAME = 'HG004_GRCh38'
K_MER_SIZE   = 4
DELTA_POS   = True
DBSNP_ON    = True
HUFFMAN_ON  = True

# K_MER OVERRIDE
if (not HUFFMAN_ON):
    K_MER_SIZE = 0

###
# FILEPATHS
###
DBSNP_PATH                  = "../data/dbSNP/"
CHR_FILE_PATH               = '../data/chr/'
INPUT_FILE_PATH             = f"../data/variants/{VARIANT_NAME}_sorted_variants.txt"
OUTPUT_BIN_PATH             = f"../data/output/{VARIANT_NAME}_Encoded.bin"
OUTPUT_DEC_PATH             = f"../data/output/{VARIANT_NAME}_Decoded.txt"
INS_SEQ_CONCAT              = f"../data/output/{VARIANT_NAME}_INS_SEQ.txt"
INS_DEC_CONCAT              = f"../data/output/{VARIANT_NAME}_INS_DEC.txt"
ENC_FILE_PATH               = f"../data/output/{VARIANT_NAME}_Encoded.bin"
TREE_PATH                   = f"../data/huffman_trees/{VARIANT_NAME}.txt"
FIGURE_PATH                 = f"../figures/{VARIANT_NAME}_Figure.png"
FIGURE_REMDBSNP_PATH        = f"../figures/{VARIANT_NAME}_removed_dbSNP.png"
TIME_CSV_PATH               = f"../data/output/csv/{VARIANT_NAME}_times.csv"

###
# Array of Chromosomes
###

CHROMOSOMES = [
    'chr1', 'chr2', 'chr3', 'chr4', 'chr5',
    'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
    'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 
    'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 
    'chr21', 'chr22'
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