#!/bin/bash

# This script efficiently automates the per-chromosome genome alignment between hg38 and hg19.
# It only downloads the chromosomes specified in the user's range and skips any
# files that already exist, making it fast and efficient for repeated runs.
#
# It accepts 0 to 2 optional command-line arguments for a chromosome range.
#
# Usage (all chroms): ./run_chromosome_comparison.sh
# Usage (range):      ./run_chromosome_comparison.sh 1 5

# Exit immediately if a command exits with a non-zero status.
set -e

# Check for command-line arguments
if [ "$#" -gt 2 ]; then
    echo "Error: Invalid number of arguments."
    echo "Usage: $0 [Start Chrom] [End Chrom]"
    exit 1
fi

# Genome assemblies
REF_CODENAME="hg38"
TARGET_CODENAME="Ash1_v2.2"
START_CHROM="$1"
END_CHROM="$2"


REF_CHROM_DIR="files/genomes/hg38"
TARGET_CHROM_DIR="files/genomes/Ash1_v2.2"

if [ -n "$START_CHROM" ] && [ -z "$END_CHROM" ]; then
    END_CHROM="$START_CHROM"
fi

echo "Starting comparison: $REF_CODENAME vs $TARGET_CODENAME..."
if [ -n "$START_CHROM" ]; then
    echo "  Range:     Chromosomes $START_CHROM to $END_CHROM"
fi
echo ""

echo "Setting up directory structure..."
GENOME_DIR="files/genomes"
OUTPUT_DIR="files/output"
mkdir -p "$GENOME_DIR" "$OUTPUT_DIR"
echo ""

echo "Checking for required dependencies..."
COMMANDS=("wget" "gunzip" "git" "python3" "./tools/mummer/bin/nucmer" "./tools/mummer/bin/nucmer" "./tools/mummer/bin/nucmer" "bcftools")
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: Required command '$cmd' is not installed or not in your PATH."
        exit 1
    fi
done
echo " All dependencies found."
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

# --- Per-Chromosome Genome Comparison ---
echo "--- Running Per-Chromosome Comparison ---"
declare -a VCF_FILES_TO_MERGE
declare -a files_to_process

# This logic correctly selects files for processing based on the user's range
# or defaults to all available .fna files if no range was given.
if [ -z "$START_CHROM" ]; then
    files_to_process=($(ls -v "$REF_CHROM_DIR"/chr*.fa))
else
    for i in $(seq "$START_CHROM" "$END_CHROM"); do
        found_file="$REF_CHROM_DIR/chr${i}.fa"
        if [ -f "$found_file" ]; then files_to_process+=("$found_file"); fi
    done
fi

TOTAL_FILES=${#files_to_process[@]}
CURRENT_FILE=0
echo "Found $TOTAL_FILES chromosomes to process."

for ref_chrom_file in "${files_to_process[@]}"; do
    CURRENT_FILE=$((CURRENT_FILE + 1))
    CHROM_BASENAME=$(basename "$ref_chrom_file" .fa)
    progress_bar "$CURRENT_FILE" "$TOTAL_FILES"

    echo "Current: $CURRENT_FILE"
    echo ""
    echo "Base: $CHROM_BASENAME"
    echo ""

    
    target_chrom_file="$TARGET_CHROM_DIR/${CHROM_BASENAME}.fasta"
    if [ ! -f "$target_chrom_file" ]; then continue; fi

    PREFIX="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.${CHROM_BASENAME}"

    echo "Prefix: $PREFIX"
    echo ""

    
    ./tools/mummer/bin/nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file" &> /dev/null
    ./tools/mummer/bin/delta-filter -1 "${PREFIX}.delta" > "${PREFIX}.filtered.delta" 2>/dev/null
    ./tools/mummer/bin/show-snps -H -T "${PREFIX}.filtered.delta" > "${PREFIX}.snps" 2>/dev/null
    python3 tools/all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" > "${PREFIX}.vcf" 2>/dev/null
    
    VCF_FILES_TO_MERGE+=("${PREFIX}.vcf")
done
echo ""

# --- 4. Merge VCFs and Clean Up ---
echo "--- 4. Merging Per-Chromosome VCFs ---"
if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then echo " Error: No VCF files were generated."; exit 1; fi
FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.merged.vcf"

echo "Merging ${#VCF_FILES_TO_MERGE[@]} VCF files..."
bcftools concat --allow-overlaps -O v -o "$FINAL_VCF_FILE" $(printf "%s\n" "${VCF_FILES_TO_MERGE[@]}" | sort -V) &> /dev/null

echo "Cleaning up intermediate files..."
rm -f "$OUTPUT_DIR"/${REF_CODENAME}_vs_${TARGET_CODENAME}.chr*.{delta,filtered.delta,snps,vcf}
echo " Cleanup complete."
echo ""

# --- 5. Output ---
echo "--- Pipeline Complete ---"
echo " Success! The final merged pseudo-VCF file is located at: $FINAL_VCF_FILE"
ls -lh "$FINAL_VCF_FILE"





