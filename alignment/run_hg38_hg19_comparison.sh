#!/bin/bash

# This script efficiently automates the per-chromosome genome alignment between hg38 and hg19.
# It only downloads the chromosomes specified in the user's range and skips any
# files that already exist, making it fast and efficient for repeated runs.
#
# It accepts 0 to 2 optional command-line arguments for a chromosome range.
#
# Usage (all chroms): ./compare_hg38_vs_hg19_efficient.sh
# Usage (range):      ./compare_hg38_vs_hg19_efficient.sh 1 5

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 0. Configuration and Prerequisite Check ---

# Check for command-line arguments
if [ "$#" -gt 2 ]; then
    echo "Error: Invalid number of arguments."
    echo "Usage: $0 [Start Chrom] [End Chrom]"
    exit 1
fi

# Hardcode the genome assemblies
REF_CODENAME="hg38"
TARGET_CODENAME="hg19"
START_CHROM="$1"
END_CHROM="$2"

if [ -n "$START_CHROM" ] && [ -z "$END_CHROM" ]; then
    END_CHROM="$START_CHROM"
fi

echo "🚀 Starting efficient comparison: $REF_CODENAME vs $TARGET_CODENAME..."
if [ -n "$START_CHROM" ]; then
    echo "  Range:     Chromosomes $START_CHROM to $END_CHROM"
fi
echo ""

echo "🔧 Setting up directory structure..."
GENOME_DIR="files/genomes"
OUTPUT_DIR="files/output"
mkdir -p "$GENOME_DIR" "$OUTPUT_DIR"
echo ""

echo "🔎 Checking for required dependencies..."
COMMANDS=("wget" "gunzip" "git" "python3" "nucmer" "delta-filter" "show-snps" "bcftools")
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Error: Required command '$cmd' is not installed or not in your PATH."
        exit 1
    fi
done
echo "✅ All dependencies found."
echo ""

# --- Helper Function for Progress Bar ---
progress_bar() {
    local progress=$1
    local total=$2
    local bar_size=40
    local percentage=$(( (progress * 100) / total ))
    local done_size=$(( (progress * bar_size) / total ))
    
    # Create the bar string
    bar=$(printf "%${done_size}s" "" | tr ' ' "#")
    todo=$(printf "%$((bar_size - done_size))s" "")
    
    # Print the progress bar
    printf "\rProgress: [${bar}${todo}] ${percentage}%% (${progress}/${total})"
    if [ "$progress" -eq "$total" ]; then echo ""; fi
}

# --- 1. Acquire and Prepare FASTA Files from UCSC ---
echo "--- 1. Acquiring and Preparing FASTA files from UCSC ---"
REF_CHROM_DIR="$GENOME_DIR/${REF_CODENAME}"
TARGET_CHROM_DIR="$GENOME_DIR/${TARGET_CODENAME}"

# Function to download chromosomes one-by-one based on the user's selected range
download_chromosomes_selectively() {
    local CODENAME="$1"
    local CHROM_DIR="$2"
    local BASE_URL="https://hgdownload.soe.ucsc.edu/goldenPath/${CODENAME}/chromosomes/"
    
    declare -a chroms_to_download
    
    # Determine which chromosomes to download based on user input
    if [ -z "$START_CHROM" ]; then
        # If no range is specified, default to all standard chromosomes
        chroms_to_download=(
            "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10"
            "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19"
            "chr20" "chr21" "chr22" "chrX" "chrY" "chrM"
        )
    else
        # Otherwise, only add chromosomes from the numeric range to the list
        for i in $(seq "$START_CHROM" "$END_CHROM"); do
            chroms_to_download+=("chr${i}")
        done
        # You could add non-numeric chromosomes here if needed, e.g.,
        # chroms_to_download+=("chrX" "chrY")
    fi

    echo "Checking for '$CODENAME' chromosomes..."
    mkdir -p "$CHROM_DIR"
    
    local PWD_ORIGINAL=$(pwd)
    cd "$CHROM_DIR"

    local TOTAL_CHROMS=${#chroms_to_download[@]}
    local CURRENT_CHROM=0

    for CHR in "${chroms_to_download[@]}"; do
        CURRENT_CHROM=$((CURRENT_CHROM + 1))
        local FA_FILE="${CHR}.fna"
        
        # Check if the final uncompressed file already exists. If so, skip.
        if [ -f "$FA_FILE" ]; then
            progress_bar "$CURRENT_CHROM" "$TOTAL_CHROMS"
            continue
        fi

        # If it doesn't exist, download and unpack it
        local GZ_FILE="${CHR}.fa.gz"
        wget -q -O "$GZ_FILE" "${BASE_URL}${GZ_FILE}"
        
        if [ -f "$GZ_FILE" ]; then
            gunzip -c "$GZ_FILE" > "$FA_FILE"
            rm "$GZ_FILE"
        else
             echo "Warning: Could not download ${GZ_FILE}. It may not exist for this assembly."
        fi
        progress_bar "$CURRENT_CHROM" "$TOTAL_CHROMS"
    done
    
    cd "$PWD_ORIGINAL"
    echo "  ✅ Verification for '$CODENAME' complete."
}

download_chromosomes_selectively "$REF_CODENAME" "$REF_CHROM_DIR"
download_chromosomes_selectively "$TARGET_CODENAME" "$TARGET_CHROM_DIR"
echo ""

# --- 2. Install all2vcf (unchanged) ---
echo "--- 2. Installing all2vcf ---"
if [ ! -d "all2vcf" ]; then git clone https://github.com/MatteoSchiavinato/all2vcf.git &> /dev/null; fi
if [ ! -d "all2vcf/all_to_vcf" ]; then
    (cd all2vcf && python3 -m venv all_to_vcf && source all_to_vcf/bin/activate && pip install -r ../requirements.txt > /dev/null && deactivate)
fi
echo "✅ all2vcf setup complete."
echo ""

# --- 3. Per-Chromosome Genome Comparison ---
echo "--- 3. Running Per-Chromosome Comparison ---"
declare -a VCF_FILES_TO_MERGE
declare -a files_to_process

# This logic correctly selects files for processing based on the user's range
# or defaults to all available .fna files if no range was given.
if [ -z "$START_CHROM" ]; then
    files_to_process=($(ls -v "$REF_CHROM_DIR"/chr*.fna))
else
    for i in $(seq "$START_CHROM" "$END_CHROM"); do
        found_file="$REF_CHROM_DIR/chr${i}.fna"
        if [ -f "$found_file" ]; then files_to_process+=("$found_file"); fi
    done
fi

TOTAL_FILES=${#files_to_process[@]}
CURRENT_FILE=0
echo "Found $TOTAL_FILES chromosomes to process."

source all2vcf/all_to_vcf/bin/activate
for ref_chrom_file in "${files_to_process[@]}"; do
    CURRENT_FILE=$((CURRENT_FILE + 1))
    CHROM_BASENAME=$(basename "$ref_chrom_file" .fna)
    progress_bar "$CURRENT_FILE" "$TOTAL_FILES"
    
    target_chrom_file="$TARGET_CHROM_DIR/${CHROM_BASENAME}.fna"
    if [ ! -f "$target_chrom_file" ]; then continue; fi

    PREFIX="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.${CHROM_BASENAME}"
    
    nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file" &> /dev/null
    delta-filter -1 "${PREFIX}.delta" > "${PREFIX}.filtered.delta" 2>/dev/null
    show-snps -H -T "${PREFIX}.filtered.delta" > "${PREFIX}.snps" 2>/dev/null
    python3 all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" > "${PREFIX}.vcf" 2>/dev/null
    
    VCF_FILES_TO_MERGE+=("${PREFIX}.vcf")
done
deactivate
echo ""

# --- 4. Merge VCFs and Clean Up ---
echo "--- 4. Merging Per-Chromosome VCFs ---"
if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then echo "❌ Error: No VCF files were generated."; exit 1; fi
FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.merged.vcf"

echo "Merging ${#VCF_FILES_TO_MERGE[@]} VCF files..."
bcftools concat --allow-overlaps -O v -o "$FINAL_VCF_FILE" $(printf "%s\n" "${VCF_FILES_TO_MERGE[@]}" | sort -V) &> /dev/null

echo "Cleaning up intermediate files..."
rm -f "$OUTPUT_DIR"/${REF_CODENAME}_vs_${TARGET_CODENAME}.chr*.{delta,filtered.delta,snps,vcf}
echo "✅ Cleanup complete."
echo ""

# --- 5. Output ---
echo "--- Pipeline Complete ---"
echo "✅ Success! The final merged pseudo-VCF file is located at: $FINAL_VCF_FILE"
ls -lh "$FINAL_VCF_FILE"