#!/bin/bash

# Script to unzip VCF files in the variants directory

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VARIANTS_DIR="$SCRIPT_DIR/dnazip/data/variants"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Unzipping VCF Files${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if variants directory exists
if [ ! -d "$VARIANTS_DIR" ]; then
    echo -e "${RED}Error: Variants directory not found at $VARIANTS_DIR${NC}"
    exit 1
fi

cd "$VARIANTS_DIR"

# Check if vcf_files.zip exists
if [ -f "vcf_files.zip" ]; then
    echo -e "${GREEN}Found vcf_files.zip${NC}"
    echo -e "${YELLOW}Unzipping...${NC}"
    
    unzip -o vcf_files.zip
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully unzipped vcf_files.zip${NC}"
        
        # List the extracted files
        echo -e "\n${YELLOW}Extracted files:${NC}"
        find . -name "*.vcf" -o -name "*.vcf.gz" | while read file; do
            SIZE=$(du -h "$file" | cut -f1)
            echo -e "  ${GREEN}✓${NC} $(basename "$file") ($SIZE)"
        done
    else
        echo -e "${RED}✗ Failed to unzip vcf_files.zip${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}No vcf_files.zip found in $VARIANTS_DIR${NC}"
fi

# Also unzip any individual .vcf.gz files
echo -e "\n${GREEN}Checking for individual .vcf.gz files...${NC}"
VCF_GZ_COUNT=$(find . -maxdepth 1 -name "*.vcf.gz" | wc -l)

if [ $VCF_GZ_COUNT -gt 0 ]; then
    echo -e "${YELLOW}Found $VCF_GZ_COUNT .vcf.gz files${NC}"
    
    for vcf_gz in *.vcf.gz; do
        if [ -f "$vcf_gz" ]; then
            VCF_NAME="${vcf_gz%.gz}"
            
            # Check if already unzipped
            if [ -f "$VCF_NAME" ]; then
                echo -e "${YELLOW}  → $VCF_NAME already exists. Skipping.${NC}"
            else
                echo -e "${GREEN}  → Unzipping $vcf_gz...${NC}"
                gunzip -k "$vcf_gz"
                
                if [ $? -eq 0 ]; then
                    SIZE=$(du -h "$VCF_NAME" | cut -f1)
                    echo -e "${GREEN}    ✓ Created $VCF_NAME ($SIZE)${NC}"
                else
                    echo -e "${RED}    ✗ Failed to unzip $vcf_gz${NC}"
                fi
            fi
        fi
    done
else
    echo -e "${YELLOW}No .vcf.gz files found${NC}"
fi

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

VCF_COUNT=$(find . -maxdepth 1 -name "*.vcf" | wc -l)
VCF_GZ_COUNT=$(find . -maxdepth 1 -name "*.vcf.gz" | wc -l)

echo -e "${GREEN}VCF files (.vcf): $VCF_COUNT${NC}"
echo -e "${GREEN}Compressed VCF files (.vcf.gz): $VCF_GZ_COUNT${NC}"
echo -e "${YELLOW}Location: $VARIANTS_DIR${NC}"

echo -e "\n${GREEN}✓ Done!${NC}"
