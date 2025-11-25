#!/bin/bash

# Master script to run all genome preparation and compression benchmark scripts in order

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}    GENOME DATA PREPARATION & COMPRESSION BENCHMARKS${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e ""

# Track overall start time
OVERALL_START=$(date +%s)

# Function to run a script and check for errors
run_script() {
    local script_name=$1
    local script_desc=$2
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[$(date +%H:%M:%S)] Running: ${script_desc}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    START=$(date +%s)
    
    if [ -f "$SCRIPT_DIR/$script_name" ]; then
        bash "$SCRIPT_DIR/$script_name"
        EXIT_CODE=$?
        
        END=$(date +%s)
        DURATION=$((END - START))
        
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✓ ${script_desc} completed successfully (${DURATION}s)${NC}"
            return 0
        else
            echo -e "${RED}✗ ${script_desc} failed with exit code ${EXIT_CODE}${NC}"
            echo -e "${YELLOW}Do you want to continue? (y/n)${NC}"
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                echo -e "${RED}Aborting pipeline${NC}"
                exit 1
            fi
            return 1
        fi
    else
        echo -e "${RED}✗ Script not found: $script_name${NC}"
        echo -e "${YELLOW}Skipping...${NC}"
        return 1
    fi
}

# ============================================
# Step 1: Setup Python Environment
# ============================================
run_script "setup_env.sh" "Setup Python Environment"

VENV_NAME="venv"
source "$SCRIPT_DIR/$VENV_NAME/bin/activate"

# ============================================
# Step 2: Setup Tools (bigBedToBed)
# ============================================
run_script "setup_tools.sh" "Setup Tools"

# ============================================
# Step 3: Download Genomes
# ============================================
run_script "download_genomes.sh" "Download Genome Assemblies"

# ============================================
# Step 4: Extract Chromosomes (includes cleaning)
# ============================================
run_script "extract_chromosomes.sh" "Extract Chromosomes"

# ============================================
# Step 5: Process dbSNP Data
# ============================================
run_script "process_dbsnp.sh" "Process dbSNP Data"

# ============================================
# Step 6: Unzip VCF Files
# ============================================
run_script "unzip_vcf_files.sh" "Unzip VCF Files"

# ============================================
# Step 7: Run Compression Benchmarks
# ============================================
run_script "run_compression_benchmarks.sh" "Run Compression Benchmarks"

# ============================================
# Summary
# ============================================
OVERALL_END=$(date +%s)
OVERALL_DURATION=$((OVERALL_END - OVERALL_START))
HOURS=$((OVERALL_DURATION / 3600))
MINUTES=$(((OVERALL_DURATION % 3600) / 60))
SECONDS=$((OVERALL_DURATION % 60))

echo -e "\n${CYAN}================================================================${NC}"
echo -e "${GREEN}ALL STEPS COMPLETED!${NC}"
echo -e "${CYAN}================================================================${NC}"
echo -e "${YELLOW}Total runtime: ${HOURS}h ${MINUTES}m ${SECONDS}s${NC}"
echo -e ""
echo -e "${GREEN}Results:${NC}"
echo -e "  ${YELLOW}→${NC} Genomes: genomes/"
echo -e "  ${YELLOW}→${NC} Chromosomes: dnazip/data/chr/"
echo -e "  ${YELLOW}→${NC} dbSNP data: dnazip/data/dbSNP/"
echo -e "  ${YELLOW}→${NC} Variant files: dnazip/data/variants/"
echo -e "  ${YELLOW}→${NC} Compression results: See run_compression_benchmarks.sh output"
echo -e "  ${YELLOW}→${NC} Comparison plot: figures/chr21_compression_comparison.png"
echo -e ""
echo -e "${GREEN}✓ Pipeline complete!${NC}"
