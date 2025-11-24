#!/bin/bash

# Script to run compression benchmarks on Ash1_v2.2_chr21
# Runs: biocompress_1, k_mer_huffman, and dnazip

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GENOME_NAME="Ash1_v2_CHR21"
CHR_FILE="$SCRIPT_DIR/dnazip/data/chr/Ash1_v2.2_chr21.txt"

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}COMPRESSION BENCHMARKS FOR ASH1 v2.2 CHR21${NC}"
echo -e "${BLUE}============================================================${NC}"

# Check if chr21.txt exists
if [ ! -f "$CHR_FILE" ]; then
    echo -e "${RED}Error: chr21.txt not found at $CHR_FILE${NC}"
    echo -e "${YELLOW}Please run extract_chromosomes.sh first to extract chr21${NC}"
    exit 1
fi

echo -e "${YELLOW}Using genome file: $CHR_FILE${NC}"
echo -e ""

# ============================================
# 1. Run biocompress_1
# ============================================
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}[1/3] Running biocompress_1...${NC}"
echo -e "${BLUE}============================================================${NC}"

cd "$SCRIPT_DIR/biocompress_1"

# Update config.py to use Ash1_v2_CHR21
cat > config.py << 'EOF'
DNA_FILE = "Ash1_v2_CHR21"
DNA_FILE_PATH = "../dnazip/data/chr/"
DNA_FILE_TXT = DNA_FILE + ".txt"
DNA_FILE_FA = DNA_FILE + ".fa"
COMPLEMENT_TABLE = str.maketrans("ACTG", "TGAC")
HEIGHT = 11
COMPARE_LENGTH = 50

with open(DNA_FILE_PATH+DNA_FILE_TXT, "r") as file:
       CONTENT = file.read()
EOF

# Copy chr21.txt to Ash1_v2_CHR21.txt for biocompress
if [ ! -f "../dnazip/data/chr/Ash1_v2_CHR21.txt" ]; then
    echo -e "${GREEN}Creating Ash1_v2_CHR21.txt from chr21.txt...${NC}"
    cp "$CHR_FILE" "../dnazip/data/chr/Ash1_v2_CHR21.txt"
fi

echo -e "${GREEN}Running biocompress.py...${NC}"
python3 biocompress.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ biocompress_1 completed successfully${NC}"
else
    echo -e "${RED}✗ biocompress_1 failed${NC}"
fi

cd "$SCRIPT_DIR"

# ============================================
# 2. Run k_mer_huffman.py
# ============================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}[2/3] Running k_mer_huffman.py...${NC}"
echo -e "${BLUE}============================================================${NC}"

cd "$SCRIPT_DIR/huffman_coding/code"

# Update config.py to use Ash1_v2_CHR21
python3 << 'PYEOF'
from pathlib import Path

K_MER_SIZE = 8
BASE_PATH = Path.cwd().parent.parent
GENOME_CHOICE = "Ash1_v2_CHR21"

config_content = f'''from pathlib import Path  

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
K_MER_SIZE    = {K_MER_SIZE}
BASE_PATH     = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR    = BASE_PATH / 'huffman_coding' / 'output'
OUT_GENOME    = OUTPUT_DIR / 'data'
GENOME_DIR    = BASE_PATH / 'dnazip' / 'data' /'chr'
PLOT_OUT_PATH = OUTPUT_DIR / 'plots' / 'space_savings_vs_kmer.png'
TIME_CSV_PATH = OUTPUT_DIR / 'csv' / 'huffman_times.csv'
GENOME_CHOICE = "{GENOME_CHOICE}"
K_MER_TAG     = f"K_MER_{{K_MER_SIZE}}"

if (K_MER):
    GENOME_BIN    = OUT_GENOME / f'ENCODED_{{GENOME_CHOICE}}_{{K_MER_TAG}}'
    GENOME_FILE   = GENOME_DIR / f"{{GENOME_CHOICE}}.txt"
    DECODED_FILE  = OUT_GENOME / f'DECODED_GENOME_{{GENOME_CHOICE}}_{{K_MER_TAG}}'
    HUFFMAN_TREE  = OUT_GENOME / f'HUFFMAN_TREE_GENOME_{{GENOME_CHOICE}}_{{K_MER_TAG}}'
else:
    GENOME_BIN    = OUT_GENOME / f'ENCODED_{{GENOME_CHOICE}}_{{K_MER_TAG}}_Regular'
    GENOME_FILE   = GENOME_DIR / f"{{GENOME_CHOICE}}.txt"
    DECODED_FILE  = OUT_GENOME / f'DECODED_GENOME_{{GENOME_CHOICE}}_{{K_MER_TAG}}_Regular'
    HUFFMAN_TREE  = OUT_GENOME / f'HUFFMAN_TREE_GENOME_{{GENOME_CHOICE}}_{{K_MER_TAG}}_Regular'
    
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

NUC_ENCODING = {{
    "A": "00",
    "C": "01",
    "G": "10",
    "T": "11",
}}

TWO_BIT_ENCODING = {{
    "00": "A",
    "01": "C",
    "10": "G",
    "11": "T",
}}

VARIATION_FLAG = {{
    'SNPS': 0,
    'DELETIONS': 1,
    'INSERTIONS': 2,
}}
'''

with open('config.py', 'w') as f:
    f.write(config_content)

print("✓ Updated config.py for k_mer_huffman")
PYEOF

# Create output directories if they don't exist
mkdir -p ../output/data
mkdir -p ../output/csv
mkdir -p ../output/plots

# Copy chr21.txt to Ash1_v2_CHR21.txt for huffman coding
if [ ! -f "../../dnazip/data/chr/Ash1_v2_CHR21.txt" ]; then
    echo -e "${GREEN}Creating Ash1_v2_CHR21.txt from chr21.txt...${NC}"
    cp "$CHR_FILE" "../../dnazip/data/chr/Ash1_v2_CHR21.txt"
fi

echo -e "${GREEN}Running k_mer_huffman.py...${NC}"
python3 k_mer_huffman.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ k_mer_huffman.py completed successfully${NC}"
else
    echo -e "${RED}✗ k_mer_huffman.py failed${NC}"
fi

cd "$SCRIPT_DIR"

# ============================================
# 3. Run dnazip with chr21 variant file
# ============================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}[3/3] Running dnazip...${NC}"
echo -e "${BLUE}============================================================${NC}"

VARIANT_FILE="$SCRIPT_DIR/dnazip/data/variants/GRCh38_ash1_v2.2_chr21_sorted_variants.txt"

if [ ! -f "$VARIANT_FILE" ]; then
    echo -e "${RED}Error: Variant file not found: $VARIANT_FILE${NC}"
    echo -e "${YELLOW}Expected file: GRCh38_ash1_v2.2_chr21_sorted_variants.txt${NC}"
    echo -e "${YELLOW}Please make sure the variant file is in dnazip/data/variants/${NC}"
else
    cd "$SCRIPT_DIR/dnazip/code"
    
    # Update constants.py to use chr21 variant file
    echo -e "${GREEN}Configuring dnazip for chr21...${NC}"
    
    python3 << 'PYEOF'
from pathlib import Path

config_content = '''from pathlib import Path  

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
'''

with open('constants.py', 'w') as f:
    f.write(config_content)

print("✓ Updated constants.py for dnazip chr21")
PYEOF

    # Create necessary directories
    mkdir -p ../data/output/csv
    mkdir -p ../data/huffman_trees
    mkdir -p ../figures
    
    # Run dnazip
    echo -e "${GREEN}Running dnazip.py...${NC}"
    echo -e "${YELLOW}Note: This may take a while for large variant files${NC}"
    
    python3 dnazip.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ dnazip completed successfully${NC}"
    else
        echo -e "${RED}✗ dnazip failed${NC}"
    fi
    
    cd "$SCRIPT_DIR"
fi

# ============================================
# Summary
# ============================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}BENCHMARK SUMMARY${NC}"
echo -e "${BLUE}============================================================${NC}"

echo -e "\n${GREEN}Results locations:${NC}"

echo -e "\n${YELLOW}[1] biocompress_1:${NC}"
if [ -f "$SCRIPT_DIR/biocompress_1/data/Ash1_v2_CHR21_11.bin" ]; then
    SIZE=$(du -h "$SCRIPT_DIR/biocompress_1/data/Ash1_v2_CHR21_11.bin" 2>/dev/null | cut -f1)
    echo -e "  ${GREEN}✓${NC} Compressed file: biocompress_1/data/Ash1_v2_CHR21_11.bin ($SIZE)"
else
    echo -e "  ${YELLOW}→${NC} Compressed file: biocompress_1/data/Ash1_v2_CHR21_11.bin"
fi
echo -e "  ${YELLOW}→${NC} Metrics: biocompress_1/data.csv"

echo -e "\n${YELLOW}[2] k_mer_huffman (k=8):${NC}"
if [ -f "$SCRIPT_DIR/huffman_coding/output/data/ENCODED_Ash1_v2_CHR21_K_MER_8.bin" ]; then
    SIZE=$(du -h "$SCRIPT_DIR/huffman_coding/output/data/ENCODED_Ash1_v2_CHR21_K_MER_8.bin" 2>/dev/null | cut -f1)
    echo -e "  ${GREEN}✓${NC} Compressed file: huffman_coding/output/data/ENCODED_Ash1_v2_CHR21_K_MER_8.bin ($SIZE)"
else
    echo -e "  ${YELLOW}→${NC} Compressed file: huffman_coding/output/data/ENCODED_Ash1_v2_CHR21_K_MER_8.bin"
fi
echo -e "  ${YELLOW}→${NC} Metrics: huffman_coding/output/csv/huffman_times.csv"

echo -e "\n${YELLOW}[3] dnazip (k=8, dbSNP=ON, Huffman=ON):${NC}"
if [ -f "$SCRIPT_DIR/dnazip/data/output/GRCh38_ash1_v2.2_chr21_False_True_True_8_Encoded.bin" ]; then
    SIZE=$(du -h "$SCRIPT_DIR/dnazip/data/output/GRCh38_ash1_v2.2_chr21_False_True_True_8_Encoded.bin" 2>/dev/null | cut -f1)
    echo -e "  ${GREEN}✓${NC} Compressed file: dnazip/data/output/GRCh38_ash1_v2.2_chr21_False_True_True_8_Encoded.bin ($SIZE)"
else
    echo -e "  ${YELLOW}→${NC} Compressed file: dnazip/data/output/GRCh38_ash1_v2.2_chr21_False_True_True_8_Encoded.bin"
fi
echo -e "  ${YELLOW}→${NC} Figure: dnazip/figures/GRCh38_ash1_v2.2_chr21_False_True_True_8_Figure.png"
echo -e "  ${YELLOW}→${NC} Metrics: dnazip/data/output/csv/GRCh38_ash1_v2.2_chr21_times.csv"

# ============================================
# Generate Comparison Plot
# ============================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}Generating Comparison Plot...${NC}"
echo -e "${BLUE}============================================================${NC}"

python3 << 'PLOTEOF'
import sys
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

# Add dnazip code to path
sys.path.insert(0, str(Path.cwd() / 'dnazip' / 'code'))

# Use helper function from combined_plots
def file_size_mb(file_path):
    """Get file size in MB"""
    if not os.path.exists(file_path):
        return np.nan
    return os.path.getsize(file_path) / (1024 * 1024)

# Configuration
BASE_DIR = Path.cwd()
GENOME_FILE = BASE_DIR / 'dnazip' / 'data' / 'chr' / 'Ash1_v2.2_chr21.txt'
BIOCOMP_BIN = BASE_DIR / 'dnazip' / 'data' / 'chr' / 'Ash1_v2_CHR21_11.bin'
HUFFMAN_BIN = BASE_DIR / 'huffman_coding' / 'output' / 'data' / 'ENCODED_Ash1_v2_CHR21_K_MER_8.bin'
DNAZIP_BIN = BASE_DIR / 'dnazip' / 'data' / 'output' / 'GRCh38_ash1_v2.2_chr21_False_True_True_8_Encoded.bin'
VARIANT_FILE = BASE_DIR / 'dnazip' / 'data' / 'variants' / 'GRCh38_ash1_v2.2_chr21_sorted_variants.txt'
OUTPUT_PLOT = BASE_DIR / 'figures' / 'chr21_compression_comparison.png'

# Get file sizes
genome_size = file_size_mb(GENOME_FILE)
variant_size = file_size_mb(VARIANT_FILE)
biocomp_size = file_size_mb(BIOCOMP_BIN)
huffman_size = file_size_mb(HUFFMAN_BIN)
dnazip_size = file_size_mb(DNAZIP_BIN)

print(f"\nFile Sizes:")
print(f"  Original Genome: {genome_size:.2f} MB")
print(f"  Variant File:    {variant_size:.2f} MB")
print(f"  Biocompress_1:   {biocomp_size:.2f} MB")
print(f"  K-mer Huffman:   {huffman_size:.2f} MB")
print(f"  DNAZip:          {dnazip_size:.2f} MB")

# Calculate compression ratios
biocomp_ratio = biocomp_size / genome_size if genome_size > 0 else np.nan
huffman_ratio = huffman_size / genome_size if genome_size > 0 else np.nan
dnazip_ratio = dnazip_size / genome_size if genome_size > 0 else np.nan

print(f"\nCompression Ratios:")
print(f"  Biocompress_1:  {biocomp_ratio:.4f}x")
print(f"  K-mer Huffman:  {huffman_ratio:.4f}x")
print(f"  DNAZip:         {dnazip_ratio:.4f}x (variants) / {(dnazip_size/genome_size):.4f}x (genome)")

# Create the plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# --- Plot 1: File Sizes ---
methods = ['Biocompress_1', 'K-mer Huffman\n(k=8)', 'DNAZip', 'VCF']
sizes = [biocomp_size, huffman_size, dnazip_size, variant_size]
colors = ['#1E88E5', '#D81B60', '#FFC107', '#4CAF50']
labels = ['Biocompress_1', 'K-mer Huffman (k=8)', 'DNAZip', 'VCF']

x = np.arange(len(methods))
width = 0.6

bars = ax1.bar(x, sizes, width, color=colors, edgecolor='black', linewidth=2)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    if not np.isnan(height):
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} MB', ha='center', va='bottom', 
                fontsize=10)

ax1.set_ylabel('File Size (MB)', fontsize=14)
ax1.set_xticks(x)
ax1.set_xticklabels(methods, fontsize=11)
ax1.legend(bars, labels, fontsize=12, loc='upper right')
ax1.grid(axis='y', alpha=0.3)

# --- Plot 2: Compression Ratios ---
# Only show ratios for the 3 compression methods (not variant)
methods_ratio = methods[:3]  # Exclude variant from ratio plot
ratios = [biocomp_ratio, huffman_ratio, dnazip_ratio]
colors_ratio = colors[:3]  # Exclude variant color

bars_ratio = ax2.bar(methods_ratio, ratios, width, color=colors_ratio, edgecolor='black', linewidth=2)

# Add value labels
for bar, ratio in zip(bars_ratio, ratios):
    height = bar.get_height()
    if not np.isnan(height):
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{ratio:.4f}x', ha='center', va='bottom',
                fontsize=12)

ax2.set_ylabel('Compression Ratio', fontsize=14)
ax2.set_xticklabels(methods_ratio, fontsize=11)
ax2.grid(axis='y', alpha=0.3)

# Overall title
fig.suptitle(f'ash1_v2.2_chr21: {genome_size:.2f} MB', 
             fontsize=18, y=1.02)

plt.tight_layout()

# Save the plot
OUTPUT_PLOT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_PLOT, dpi=300, bbox_inches='tight')
print(f"\n✓ Plot saved to: {OUTPUT_PLOT}")
PLOTEOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Comparison plot created!${NC}"
    if [ -f "$SCRIPT_DIR/figures/chr21_compression_comparison.png" ]; then
        SIZE=$(du -h "$SCRIPT_DIR/figures/chr21_compression_comparison.png" | cut -f1)
        echo -e "${YELLOW}→ Plot saved: figures/chr21_compression_comparison.png ($SIZE)${NC}"
    fi
else
    echo -e "${RED}✗ Failed to generate comparison plot${NC}"
fi

echo -e "\n${GREEN}✓ Compression benchmarks complete!${NC}"
