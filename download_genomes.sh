#!/bin/bash

# Script to download human genome assemblies from NCBI

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GENOMES_DIR="$SCRIPT_DIR/genomes"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Downloading Human Genome Assemblies${NC}"
echo -e "${BLUE}=========================================${NC}"

# Create genomes directory if it doesn't exist
if [ ! -d "$GENOMES_DIR" ]; then
    echo -e "${GREEN}Creating genomes directory...${NC}"
    mkdir -p "$GENOMES_DIR"
fi

# Function to download a genome assembly from NCBI FTP
download_genome_ftp() {
    local NAME=$1
    local FTP_URL=$2
    local OUTPUT_DIR="$GENOMES_DIR/$NAME"
    
    echo -e "\n${BLUE}=========================================${NC}"
    echo -e "${GREEN}Downloading $NAME${NC}"
    echo -e "${YELLOW}Source: NCBI FTP${NC}"
    echo -e "${BLUE}=========================================${NC}"
    
    if [ -d "$OUTPUT_DIR" ]; then
        echo -e "${YELLOW}$NAME directory already exists.${NC}"
        read -p "Do you want to redownload? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Skipping $NAME download.${NC}"
            return
        fi
        rm -rf "$OUTPUT_DIR"
    fi
    
    mkdir -p "$OUTPUT_DIR"
    
    # Construct the genomic.fna.gz filename from the FTP URL
    local BASE_NAME=$(basename "$FTP_URL")
    local GENOMIC_FILE="${BASE_NAME}_genomic.fna.gz"
    local FULL_URL="${FTP_URL}${GENOMIC_FILE}"
    
    echo -e "${GREEN}Downloading genome assembly...${NC}"
    echo -e "${YELLOW}URL: $FULL_URL${NC}"
    
    if command -v wget &> /dev/null; then
        wget -O "$OUTPUT_DIR/$GENOMIC_FILE" "$FULL_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$OUTPUT_DIR/$GENOMIC_FILE" "$FULL_URL"
    else
        echo -e "${RED}Error: Neither wget nor curl is available.${NC}"
        return
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Extracting genome file...${NC}"
        gunzip "$OUTPUT_DIR/$GENOMIC_FILE"
        echo -e "${GREEN}✓ $NAME downloaded successfully!${NC}"
        echo -e "${YELLOW}Location: $OUTPUT_DIR${NC}"
    else
        echo -e "${RED}Error: Failed to download $NAME${NC}"
    fi
    
    cd "$SCRIPT_DIR"
}

# Download each genome assembly from NCBI FTP
# 1. GRCh38 (hg38) - Human reference genome
download_genome_ftp "GRCh38" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/"

# 2. PAN027 mat v1.0 - Pangenome maternal haplotype
download_genome_ftp "PAN027_mat_v1.0" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/046/332/005/GCA_046332005.1_PAN027_mat_v1.0/"

# 3. Ash1 v2.2 - Ashkenazi genome (download directly from JHU FTP)
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Downloading Ash1 v2.2${NC}"
echo -e "${YELLOW}Source: JHU FTP Server${NC}"
echo -e "${BLUE}=========================================${NC}"

ASH1_DIR="$GENOMES_DIR/Ash1_v2.2"
ASH1_URL="ftp://ftp.ccb.jhu.edu/pub/data/Homo_sapiens/Ash1/v2.2/Assembly/Ash1_v2.2.fa.gz"

if [ -d "$ASH1_DIR" ]; then
    echo -e "${YELLOW}Ash1_v2.2 directory already exists.${NC}"
    read -p "Do you want to redownload? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Skipping Ash1_v2.2 download.${NC}"
    else
        rm -rf "$ASH1_DIR"
    fi
fi

if [ ! -d "$ASH1_DIR" ]; then
    mkdir -p "$ASH1_DIR"
    
    echo -e "${GREEN}Downloading Ash1 v2.2 genome...${NC}"
    if command -v wget &> /dev/null; then
        wget -O "$ASH1_DIR/Ash1_v2.2.fa.gz" "$ASH1_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$ASH1_DIR/Ash1_v2.2.fa.gz" "$ASH1_URL"
    else
        echo -e "${RED}Error: Neither wget nor curl is available.${NC}"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Extracting genome file...${NC}"
        gunzip "$ASH1_DIR/Ash1_v2.2.fa.gz"
        echo -e "${GREEN}✓ Ash1 v2.2 downloaded successfully!${NC}"
        echo -e "${YELLOW}Location: $ASH1_DIR${NC}"
    else
        echo -e "${RED}Error: Failed to download Ash1 v2.2${NC}"
    fi
fi

cd "$SCRIPT_DIR"

# 4. Han1 - Han Chinese genome
download_genome_ftp "Han1" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/024/586/135/GCA_024586135.1_Han1/"

# 5. T2T-CHM13v2.0 - Telomere-to-telomere assembly
download_genome_ftp "T2T-CHM13v2.0" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/914/755/GCF_009914755.1_T2T-CHM13v2.0/"

# =============================================
# Rename files to match directory names
# =============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Renaming genome files...${NC}"
echo -e "${BLUE}=========================================${NC}"

# Rename GRCh38
if [ -f "$GENOMES_DIR/GRCh38/GCF_000001405.40_GRCh38.p14_genomic.fna" ]; then
    mv "$GENOMES_DIR/GRCh38/GCF_000001405.40_GRCh38.p14_genomic.fna" "$GENOMES_DIR/GRCh38/GRCh38.fna"
    echo -e "${GREEN}✓ Renamed GRCh38 genome file${NC}"
fi

# Rename PAN027
if [ -f "$GENOMES_DIR/PAN027_mat_v1.0/GCA_046332005.1_PAN027_mat_v1.0_genomic.fna" ]; then
    mv "$GENOMES_DIR/PAN027_mat_v1.0/GCA_046332005.1_PAN027_mat_v1.0_genomic.fna" "$GENOMES_DIR/PAN027_mat_v1.0/PAN027_mat_v1.0.fna"
    echo -e "${GREEN}✓ Renamed PAN027_mat_v1.0 genome file${NC}"
fi

# Ash1 is already correctly named (Ash1_v2.2.fa)
if [ -f "$GENOMES_DIR/Ash1_v2.2/Ash1_v2.2.fa" ]; then
    echo -e "${GREEN}✓ Ash1_v2.2 already correctly named${NC}"
fi

# Rename Han1
if [ -f "$GENOMES_DIR/Han1/GCA_024586135.1_Han1_genomic.fna" ]; then
    mv "$GENOMES_DIR/Han1/GCA_024586135.1_Han1_genomic.fna" "$GENOMES_DIR/Han1/Han1.fna"
    echo -e "${GREEN}✓ Renamed Han1 genome file${NC}"
fi

# Rename T2T-CHM13v2.0
if [ -f "$GENOMES_DIR/T2T-CHM13v2.0/GCF_009914755.1_T2T-CHM13v2.0_genomic.fna" ]; then
    mv "$GENOMES_DIR/T2T-CHM13v2.0/GCF_009914755.1_T2T-CHM13v2.0_genomic.fna" "$GENOMES_DIR/T2T-CHM13v2.0/T2T-CHM13v2.0.fna"
    echo -e "${GREEN}✓ Renamed T2T-CHM13v2.0 genome file${NC}"
fi

# =============================================
# Summary
# =============================================
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}Download Summary${NC}"
echo -e "${BLUE}=========================================${NC}"

for genome_dir in "$GENOMES_DIR"/*; do
    if [ -d "$genome_dir" ]; then
        genome_name=$(basename "$genome_dir")
        file_count=$(find "$genome_dir" -type f \( -name "*.fna" -o -name "*.fa" -o -name "*.fasta" \) | wc -l)
        echo -e "${GREEN}✓ $genome_name:${NC} $file_count FASTA files"
    fi
done

echo -e "\n${GREEN}Downloads complete!${NC}"
echo -e "${YELLOW}Genomes are located in: $GENOMES_DIR${NC}"
