#!/bin/bash

# Script to clean all downloaded genomes using reader.py and export to dnazip/data/chr

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

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Cleaning Genome Files${NC}"
echo -e "${BLUE}=========================================${NC}"

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${GREEN}Creating output directory: $OUTPUT_DIR${NC}"
    mkdir -p "$OUTPUT_DIR"
fi

# Check if reader.py exists
if [ ! -f "$READER_SCRIPT" ]; then
    echo -e "${RED}Error: reader.py not found at $READER_SCRIPT${NC}"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Function to clean a genome file
clean_genome() {
    local GENOME_NAME=$1
    local INPUT_FILE=$2
    local OUTPUT_FILE="$OUTPUT_DIR/${GENOME_NAME}.txt"
    
    echo -e "\n${GREEN}Processing $GENOME_NAME...${NC}"
    
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${RED}Error: Input file not found: $INPUT_FILE${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Input: $INPUT_FILE${NC}"
    echo -e "${YELLOW}Output: $OUTPUT_FILE${NC}"
    
    # Run the Python script to clean the genome
    python3 << EOF
import sys
sys.path.insert(0, '$SCRIPT_DIR/dnazip/code')
from reader import fa_to_txt

try:
    fa_to_txt('$INPUT_FILE', '$OUTPUT_FILE')
    print('✓ Successfully cleaned $GENOME_NAME')
except Exception as e:
    print(f'Error processing $GENOME_NAME: {e}')
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        # Get file size for confirmation
        SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo -e "${GREEN}✓ Cleaned genome saved: $OUTPUT_FILE ($SIZE)${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to clean $GENOME_NAME${NC}"
        return 1
    fi
}

# Process each genome
echo -e "\n${BLUE}Processing genomes...${NC}"

# 1. GRCh38
clean_genome "GRCh38" "$GENOMES_DIR/GRCh38/GRCh38.fna"

# 2. PAN027 mat v1.0
clean_genome "PAN027_mat_v1.0" "$GENOMES_DIR/PAN027_mat_v1.0/PAN027_mat_v1.0.fna"

# 3. Ash1 v2.2
clean_genome "Ash1_v2.2" "$GENOMES_DIR/Ash1_v2.2/Ash1_v2.2.fa"

# 4. Han1
clean_genome "Han1" "$GENOMES_DIR/Han1/Han1.fna"

# 5. T2T-CHM13v2.0
clean_genome "T2T-CHM13v2.0" "$GENOMES_DIR/T2T-CHM13v2.0/T2T-CHM13v2.0.fna"

# =============================================
# Summary
# =============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Cleaning Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

TOTAL_FILES=$(find "$OUTPUT_DIR" -name "*.txt" | wc -l)
echo -e "${GREEN}Total cleaned genomes: $TOTAL_FILES${NC}"

echo -e "\n${YELLOW}Cleaned files:${NC}"
for file in "$OUTPUT_DIR"/*.txt; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        size=$(du -h "$file" | cut -f1)
        echo -e "  ${GREEN}✓${NC} $filename ($size)"
    fi
done

echo -e "\n${GREEN}Genome cleaning complete!${NC}"
echo -e "${YELLOW}Cleaned genomes are located in: $OUTPUT_DIR${NC}"
