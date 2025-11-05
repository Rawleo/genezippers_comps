from pathlib import Path  

FULL          = True
K_MER_SIZE    = 16
BASE_PATH     = Path(__file__).resolve().parent.parent
OUTPUT_DIR    = BASE_PATH / 'huffman_coding' / 'output'
GENOME_DIR    = BASE_PATH / 'dnazip' / 'data' /'chr'
TIME_CSV_PATH = OUTPUT_DIR / 'csv' / 'huffman_times.csv'
GENOME_CHOICE = "Ash1_v2_Genome.txt"
K_MER_TAG     = f"K_MER_{K_MER_SIZE}"


if (FULL):
    GENOME_BIN    = OUTPUT_DIR / f'ENCODED_{GENOME_CHOICE}{K_MER_TAG}'
    GENOME_FILE   = GENOME_DIR / GENOME_CHOICE
    DECODED_FILE  = OUTPUT_DIR / f'DECODED_GENOME_{GENOME_CHOICE}{K_MER_TAG}'
    HUFFMAN_TREE  = OUTPUT_DIR / f'HUFFMAN_TREE_GENOME_{GENOME_CHOICE}{K_MER_TAG}'
else:
    CHR           = 'chr21'
    GENOME_BIN    = OUTPUT_DIR / f'ENCODED_{CHR}'
    GENOME_FILE   = GENOME_DIR / f'{CHR}.txt'
    DECODED_FILE  = OUTPUT_DIR / f'DECODED_{CHR}'
    HUFFMAN_TREE  = OUTPUT_DIR / f'HUFFMAN_TREE_{CHR}'
    
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