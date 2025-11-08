from pathlib import Path  

"""
Directory Structure: 

huffman_coding/
├── code
│   ├── config.py
│   ├── huffman.py
│   ├── k_mer_huffman.py
│   ├── metrics.py
│   ├── plot_huffman.py
│   └── regular_huffman.py
└── output
    ├── csv
    ├── data
    └── plots
"""

K_MER         = True
K_MER_SIZE    = 4
BASE_PATH     = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR    = BASE_PATH / 'huffman_coding' / 'output'
OUT_GENOME    = OUTPUT_DIR / 'data'
GENOME_DIR    = BASE_PATH / 'dnazip' / 'data' /'chr'
PLOT_OUT_PATH = OUTPUT_DIR / 'plots' / 'space_savings_vs_kmer.png'
TIME_CSV_PATH = OUTPUT_DIR / 'csv' / 'huffman_times.csv'
GENOME_CHOICE = "Ash1_v2_CHR21"
K_MER_TAG     = f"K_MER_{K_MER_SIZE}"

# print("K-mer?", K_MER)
# print("K-mer Size:", K_MER_SIZE)
# print("Genome:", GENOME_CHOICE)

if (K_MER):
    GENOME_BIN    = OUT_GENOME / f'ENCODED_{GENOME_CHOICE}_{K_MER_TAG}'
    GENOME_FILE   = GENOME_DIR / f"{GENOME_CHOICE}.txt"
    DECODED_FILE  = OUT_GENOME / f'DECODED_GENOME_{GENOME_CHOICE}_{K_MER_TAG}'
    HUFFMAN_TREE  = OUT_GENOME / f'HUFFMAN_TREE_GENOME_{GENOME_CHOICE}_{K_MER_TAG}'
else:
    GENOME_BIN    = OUT_GENOME / f'ENCODED_{GENOME_CHOICE}_{K_MER_TAG}_Regular'
    GENOME_FILE   = GENOME_DIR / f"{GENOME_CHOICE}.txt"
    DECODED_FILE  = OUT_GENOME / f'DECODED_GENOME_{GENOME_CHOICE}_{K_MER_TAG}_Regular'
    HUFFMAN_TREE  = OUT_GENOME / f'HUFFMAN_TREE_GENOME_{GENOME_CHOICE}_{K_MER_TAG}_Regular'
    
###
# Array of Chromosomes
###

CHROMOSOMES = [
    'chr1', 'chr2', 'chr3', 'chr4', 'chr5',
    'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
    'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 
    'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 
    'chr21', 'chr22', 'chrX', 'chrY'
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