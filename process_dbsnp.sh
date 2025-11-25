#!/bin/bash

# Script to prepare and process dbSNP data using bigBedToBed and preprocess_dbsnp.py

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# --- Directory Configuration ---
DATA_DIR="$SCRIPT_DIR/dnazip/data"
DBSNP_DIR="${DATA_DIR}/dbSNP"

# --- Executable Files ---
DBSNP_PY="$SCRIPT_DIR/dnazip/code/preprocess_dbsnp.py"
BIGBEDTOBED="$SCRIPT_DIR/tools/ucsc_bin/bigBedToBed"

# --- Filename Configuration ---
BIGBED_FILE="dbSnp155Common.bb"

# --- URLs ---
BIGBED_URL="https://hgdownload.soe.ucsc.edu/gbdb/hg38/snp/dbSnp155Common.bb"
BINARY_URL="https://hgdownload.soe.ucsc.edu/admin/exe/"

# --- CHROMOSOMES ---
CHROMOSOMES=(
    "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10"
    "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19"
    "chr20" "chr21" "chr22" "chrX" "chrY"
)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Checks if all required command-line utilities are installed
check_dependencies() {
    for tool in "$@"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${RED}Error: Required utility '$tool' could not be found.${NC}"
            echo -e "${YELLOW}Please install '$tool' and ensure it is in your system's PATH.${NC}"
            exit 1
        fi
    done
}

# --- DOWNLOAD & EXTRACT dbSNP COMMON VARIANTS ---
prepare_dbsnp() {
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${GREEN}Starting Preparation of dbSNP Data${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${YELLOW}Output directory: ${DBSNP_DIR}/${NC}"
    
    check_dependencies "wget"
    mkdir -p "$DBSNP_DIR"

    local BIGBED_FILE_PATH="${DBSNP_DIR}/${BIGBED_FILE}"

    # Check if bigBedToBed tool exists
    if ! [ -f "$BIGBEDTOBED" ]; then
        echo -e "${RED}Error: '${BIGBEDTOBED}' is not found.${NC}"
        echo -e "${YELLOW}Please install it from '${BINARY_URL}' or run setup_tools.sh${NC}"
        exit 1
    fi

    # Download bigBed file if it doesn't exist
    if [ ! -f "$BIGBED_FILE_PATH" ]; then
        echo -e "${YELLOW}Input file '$BIGBED_FILE_PATH' not found.${NC}"
        echo -e "${GREEN}Attempting to download...${NC}"
        wget -P "$DBSNP_DIR" "$BIGBED_URL"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Download failed. Please check the URL or your network connection.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Download complete.${NC}"
    else
        echo -e "${GREEN}✓ BigBed file already exists: $BIGBED_FILE_PATH${NC}"
    fi

    # Extract dbSNP data for each chromosome
    echo -e "\n${GREEN}Starting batch conversion of '$BIGBED_FILE_PATH'...${NC}"
    for CHR in "${CHROMOSOMES[@]}"; do
        OUTPUT_FILE="${DBSNP_DIR}/${CHR}.txt"

        # Check if the output file already exists to avoid re-processing
        if [ -f "$OUTPUT_FILE" ]; then
            echo -e "${YELLOW}→ '${OUTPUT_FILE}' already exists. Skipping.${NC}"
            continue
        fi

        echo -e "${GREEN}Extracting ${CHR} to ${OUTPUT_FILE}...${NC}"
        "$BIGBEDTOBED" "$BIGBED_FILE_PATH" -chrom="$CHR" "$OUTPUT_FILE"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Warning: Command failed for ${CHR}.${NC}"
        else
            echo -e "${GREEN}✓ ${CHR} extracted successfully${NC}"
        fi
    done
    
    echo -e "\n${GREEN}✓ dbSNP Data Download Complete${NC}"
}

# --- Convert dbSNP to Correct Format ---
process_dbsnp() {
    echo -e "\n${BLUE}=========================================${NC}"
    echo -e "${GREEN}Converting dbSNP to Proper Format${NC}"
    echo -e "${BLUE}=========================================${NC}"
    
    check_dependencies "python3"

    # Verify all chromosome files exist
    local all_files_present=true
    for CHR in "${CHROMOSOMES[@]}"; do
        INPUT_FILE="${DBSNP_DIR}/${CHR}.txt"

        if ! [ -f "$INPUT_FILE" ]; then
            echo -e "${RED}ERROR: '${INPUT_FILE}' does not exist.${NC}"
            echo -e "${YELLOW}Please run prepare_dbsnp first or download manually.${NC}"
            all_files_present=false
        fi
    done

    if [ "$all_files_present" = false ]; then
        exit 1
    fi

    # Check if preprocess_dbsnp.py exists
    if ! [ -f "$DBSNP_PY" ]; then
        echo -e "${RED}Error: Python script not found: $DBSNP_PY${NC}"
        exit 1
    fi

    echo -e "${GREEN}Running preprocess_dbsnp.py...${NC}"
    cd "$SCRIPT_DIR/dnazip"
    python3 "$DBSNP_PY"
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ FINISHED dbSNP to Proper Format${NC}"
    else
        echo -e "\n${RED}✗ Error processing dbSNP data${NC}"
        exit 1
    fi
}

# --- Main Script Logic ---
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}dbSNP PREPARATION AND PROCESSING${NC}"
echo -e "${BLUE}============================================================${NC}"

# Step 1: Prepare dbSNP (download and extract)
prepare_dbsnp

# Step 2: Process dbSNP (convert to proper format)
process_dbsnp

# Summary
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}SUMMARY${NC}"
echo -e "${BLUE}============================================================${NC}"

# Count processed files
EXTRACTED_COUNT=$(find "$DBSNP_DIR" -name "chr*.txt" | wc -l)
echo -e "${GREEN}✓ Chromosomes extracted: $EXTRACTED_COUNT${NC}"
echo -e "${YELLOW}dbSNP data location: $DBSNP_DIR${NC}"

echo -e "\n${GREEN}✓ dbSNP preparation and processing complete!${NC}"
