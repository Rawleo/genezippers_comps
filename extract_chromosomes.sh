#!/bin/bash

# Script to extract chromosomes from genome assemblies using reader.py

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GENOMES_DIR="$SCRIPT_DIR/genomes"
OUTPUT_DIR="$SCRIPT_DIR/dnazip/data/chr"
READER_SCRIPT="$SCRIPT_DIR/dnazip/code/reader.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}EXTRACTING CHROMOSOMES FROM GENOME ASSEMBLIES${NC}"
echo -e "${BLUE}============================================================${NC}"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if reader.py exists
if [ ! -f "$READER_SCRIPT" ]; then
    echo -e "${RED}Error: reader.py not found at $READER_SCRIPT${NC}"
    exit 1
fi

# ============================================
# 1. Extract all chromosomes from GRCh38
# ============================================
echo -e "\n${BLUE}[1/2] Processing GRCh38...${NC}"
echo -e "${BLUE}------------------------------------------------------------${NC}"

GRCH38_INPUT="$GENOMES_DIR/GRCh38/GRCh38.fna"

if [ ! -f "$GRCH38_INPUT" ]; then
    echo -e "${RED}Error: GRCh38 file not found at $GRCH38_INPUT${NC}"
else
    # Array of GRCh38 chromosome IDs and names
    declare -a CHROMS=(
        "NC_000001.11:chr1"
        "NC_000002.12:chr2"
        "NC_000003.12:chr3"
        "NC_000004.12:chr4"
        "NC_000005.10:chr5"
        "NC_000006.12:chr6"
        "NC_000007.14:chr7"
        "NC_000008.11:chr8"
        "NC_000009.12:chr9"
        "NC_000010.11:chr10"
        "NC_000011.10:chr11"
        "NC_000012.12:chr12"
        "NC_000013.11:chr13"
        "NC_000014.9:chr14"
        "NC_000015.10:chr15"
        "NC_000016.10:chr16"
        "NC_000017.11:chr17"
        "NC_000018.10:chr18"
        "NC_000019.10:chr19"
        "NC_000020.11:chr20"
        "NC_000021.9:chr21"
        "NC_000022.11:chr22"
        "NC_000023.11:chrX"
        "NC_000024.10:chrY"
        "NC_012920.1:chrM"
    )
    
    # Extract each chromosome
    for CHROM_PAIR in "${CHROMS[@]}"; do
        IFS=':' read -r CHROM_ID CHR_NAME <<< "$CHROM_PAIR"
        OUTPUT_FILE="$OUTPUT_DIR/${CHR_NAME}.fna"
        
        echo -e "\n${GREEN}Extracting ${CHR_NAME} (${CHROM_ID})...${NC}"
        
        python3 << EOF
import sys
sys.path.insert(0, '$SCRIPT_DIR/dnazip/code')
from reader import extract_chromosomes

try:
    count = extract_chromosomes('$GRCH38_INPUT', '$OUTPUT_FILE', ['$CHROM_ID'])
    if count > 0:
        print('✓ Saved to $OUTPUT_FILE')
    else:
        print('✗ Chromosome not found')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
EOF
        
    done
fi

# ============================================
# 2. Extract chr21 from Ash1 v2.2
# ============================================
echo -e "\n${BLUE}[2/2] Processing Ash1 v2.2...${NC}"
echo -e "${BLUE}------------------------------------------------------------${NC}"

ASH1_INPUT="$GENOMES_DIR/Ash1_v2.2/Ash1_v2.2.fa"
ASH1_OUTPUT="$OUTPUT_DIR/Ash1_v2.2_chr21.fna"

if [ ! -f "$ASH1_INPUT" ]; then
    echo -e "${RED}Error: Ash1 v2.2 file not found at $ASH1_INPUT${NC}"
else
    echo -e "\n${GREEN}Extracting chr21 from Ash1 v2.2...${NC}"
    echo -e "${YELLOW}Trying multiple ID variants...${NC}"
    
    python3 << EOF
import sys
sys.path.insert(0, '$SCRIPT_DIR/dnazip/code')
from reader import extract_chromosomes

# Try common chromosome 21 naming patterns
chr21_variants = ['chr21', '21', 'chromosome21', 'Chromosome21', 'CM000683.2']

try:
    count = extract_chromosomes('$ASH1_INPUT', '$ASH1_OUTPUT', chr21_variants)
    if count > 0:
        print('✓ Saved to $ASH1_OUTPUT')
    else:
        print('✗ chr21 not found. Check chromosome IDs in the file.')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
EOF
fi

# ============================================
# Clean Ash1_v2.2_chr21 to .txt format
# ============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Cleaning Ash1_v2.2_chr21...${NC}"
echo -e "${BLUE}=========================================${NC}"

ASH1_FNA="$OUTPUT_DIR/Ash1_v2.2_chr21.fna"
ASH1_TXT="$OUTPUT_DIR/Ash1_v2.2_chr21.txt"

if [ -f "$ASH1_FNA" ]; then
    echo -e "${GREEN}Converting $ASH1_FNA to cleaned .txt format...${NC}"
    
    python3 << CLEANEOF
import sys
sys.path.insert(0, '$SCRIPT_DIR/dnazip/code')
from reader import fa_to_txt

try:
    fa_to_txt('$ASH1_FNA', '$ASH1_TXT')
    print('✓ Created cleaned file: Ash1_v2_CHR21.txt')
except Exception as e:
    print(f'✗ Error cleaning Ash1 chr21: {e}')
    sys.exit(1)
CLEANEOF
    
    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$ASH1_TXT" | cut -f1)
        echo -e "${GREEN}✓ Cleaned Ash1_v2_CHR21.txt ($SIZE)${NC}"
    else
        echo -e "${RED}✗ Failed to clean Ash1_v2.2_chr21${NC}"
    fi
else
    echo -e "${YELLOW}Ash1_v2.2_chr21.fna not found, skipping cleaning${NC}"
fi

# ============================================
# Summary
# ============================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}EXTRACTION SUMMARY${NC}"
echo -e "${BLUE}============================================================${NC}"

# Count extracted files
GRCH38_COUNT=$(find "$OUTPUT_DIR" -name "GRCh38_*.fna" | wc -l)
ASH1_COUNT=$(find "$OUTPUT_DIR" -name "Ash1_v2.2_*.fna" | wc -l)

echo -e "\n${GREEN}GRCh38 chromosomes extracted: $GRCH38_COUNT${NC}"
echo -e "${GREEN}Ash1 v2.2 chromosomes extracted: $ASH1_COUNT${NC}"
echo -e "\n${YELLOW}All files saved to: $OUTPUT_DIR${NC}"
echo -e "\n${GREEN}✓ Chromosome extraction complete!${NC}"
