from pathlib import Path  

FULL = False
K_MER_SIZE = 4
BASE_PATH = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_PATH / 'huffman_coding' / 'output'
GENOME_DIR = BASE_PATH / 'dnazip' / 'data' /'chr'

if (FULL):
    GENOME_BIN = OUTPUT_DIR / f'ENCODED_GENOME.bin'
    GENOME_FILE = GENOME_DIR / 'genome.txt'
    DECODED_FILE = OUTPUT_DIR / 'DECODED_GENOME.txt'
    HUFFMAN_TREE = OUTPUT_DIR / 'HUFFMAN_TREE_GENOME.txt'
else:
    CHR = 'chr21'
    GENOME_BIN = OUTPUT_DIR / f'ENCODED_{CHR}.bin'
    GENOME_FILE = GENOME_DIR / f'{CHR}.fa'
    DECODED_FILE = OUTPUT_DIR / f'DECODED_{CHR}.txt'
    HUFFMAN_TREE = OUTPUT_DIR / f'HUFFMAN_TREE_{CHR}.txt'
    
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