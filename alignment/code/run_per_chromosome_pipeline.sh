#!/bin/bash


### ISSUE WITH NAMING OF THE CHROMOSOMES, NEED TO FIX, BUT OTHERWISE THIS MAY NOT BE NEEDED.



# This script automates per-chromosome genome alignment using MUMmer4
# and converts the output to a pseudo-VCF file.
# It splits multi-FASTA genome files into individual chromosome files,
# aligns each corresponding pair, and then merges the results.
#
# It accepts two command-line arguments: the reference and target taxon names.
# It organizes files into two separate directories:
# - Genomes: 'files/genomes/'
# - Outputs: 'files/output/'

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 0. Configuration and Prerequisite Check ---

# Check for command-line arguments
if [ "$#" -ne 2 ]; then
    echo "Error: Invalid number of arguments."
    echo "Usage: $0 \"<Reference Taxon Name>\" \"<Target Taxon Name>\""
    echo "Example: $0 \"Escherichia coli\" \"Salmonella enterica\""
    exit 1
fi

REF_TAXON="$1"
TARGET_TAXON="$2"

# Create simple, filesystem-safe names from the taxon names
REF_NAME=$(echo "$REF_TAXON" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
TARGET_NAME=$(echo "$TARGET_TAXON" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

echo "  Starting per-chromosome pipeline..."
echo "  Reference: $REF_TAXON (as ${REF_NAME})"
echo "  Target:    $TARGET_TAXON (as ${TARGET_NAME})"
echo ""

echo "🔧 Setting up directory structure..."
# Define the separate directories for genomes and output files.
GENOME_DIR="files/genomes"
OUTPUT_DIR="files/output"
# Create the target directories if they don't already exist.
mkdir -p "$GENOME_DIR"
mkdir -p "$OUTPUT_DIR"
echo "Genome files will be placed in: $GENOME_DIR"
echo "Output files will be placed in: $OUTPUT_DIR"
echo ""

echo "🔎 Checking for required dependencies..."
# Added 'awk' for splitting FASTA and 'bcftools' for merging VCFs
COMMANDS=("datasets" "git" "python3" "nucmer" "delta-filter" "show-snps" "awk" "bcftools")
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Error: Required command '$cmd' is not installed or not in your PATH."
        exit 1
    fi
done
echo "All dependencies found."
echo ""

# --- 1. Acquire and Prepare FASTA Files ---
echo "--- 1. Acquiring and Preparing FASTA files ---"
# Define full paths for the main FASTA files
REF_FNA_FULL="$GENOME_DIR/${REF_NAME}.fna"
TARGET_FNA_FULL="$GENOME_DIR/${TARGET_NAME}.fna"

# Define directories for split chromosome files
REF_CHROM_DIR="$GENOME_DIR/${REF_NAME}_chroms"
TARGET_CHROM_DIR="$GENOME_DIR/${TARGET_NAME}_chroms"

# Function to download and split a genome into per-chromosome files
download_and_split() {
    local TAXON_NAME="$1"
    local SIMPLE_NAME="$2"
    local FULL_FNA_PATH="$3"
    local CHROM_DIR="$4"

    # Download the full genome if it doesn't already exist
    if [ ! -f "$FULL_FNA_PATH" ]; then
        echo "Downloading '$TAXON_NAME' genome..."
        datasets download genome taxon "$TAXON_NAME" \
          --reference \
          --filename "${SIMPLE_NAME}.zip" \
          --include genome
        unzip -o "${SIMPLE_NAME}.zip"
        local FNA_PATH=$(find ncbi_dataset -name "*.fna" -print -quit)
        mv "$FNA_PATH" "$FULL_FNA_PATH"
        rm -rf ncbi_dataset README.md "${SIMPLE_NAME}.zip"
        echo "Genome placed in $FULL_FNA_PATH"
    else
        echo "Genome ($FULL_FNA_PATH) already exists. Skipping download."
    fi

    # Split the genome into per-chromosome files if the directory is empty
    if [ ! -d "$CHROM_DIR" ] || [ -z "$(ls -A "$CHROM_DIR")" ]; then
        echo "Splitting '$TAXON_NAME' genome into chromosome files..."
        mkdir -p "$CHROM_DIR"
        # Use awk to split the multi-FASTA file based on sequence headers '>'
        awk -F ' ' '/^>/ {
            if (out) close(out);
            # Sanitize the sequence name to create a valid filename
            fname = substr($1, 2);
            gsub(/[^a-zA-Z0-9._-]/, "_", fname);
            out = dir "/" fname ".fna";
        } { print > out }' dir="$CHROM_DIR" "$FULL_FNA_PATH"
        echo "Chromosome files placed in $CHROM_DIR"
    else
        echo "Chromosome directory ($CHROM_DIR) already exists and is not empty. Skipping split."
    fi
}

# Process both reference and target genomes
download_and_split "$REF_TAXON" "$REF_NAME" "$REF_FNA_FULL" "$REF_CHROM_DIR"
download_and_split "$TARGET_TAXON" "$TARGET_NAME" "$TARGET_FNA_FULL" "$TARGET_CHROM_DIR"
echo ""

# --- 2. Install all2vcf ---
echo "--- 2. Installing all2vcf ---"
if [ ! -d "all2vcf" ]; then
    echo "Cloning all2vcf repository..."
    git clone https://github.com/MatteoSchiavinato/all2vcf.git
else
    echo "all2vcf directory already exists. Skipping clone."
fi

# Set up Python virtual environment only if it doesn't already exist
if [ ! -d "all2vcf/all_to_vcf" ]; then
    echo "Setting up Python virtual environment for all2vcf..."
    cd all2vcf
    python3 -m venv all_to_vcf
    source all_to_vcf/bin/activate
    echo "Installing required Python packages..."
    pip install -r ../requirements.txt > /dev/null
    deactivate
    cd ..
fi
echo "✅ all2vcf setup complete."
echo ""

# --- 3. Per-Chromosome Genome Comparison and Conversion ---
echo "--- 3. Running Per-Chromosome Comparison and Conversion ---"

# Array to hold paths of generated VCF files for later merging
declare -a VCF_FILES_TO_MERGE

# Activate python venv once before the loop for efficiency
source all2vcf/all_to_vcf/bin/activate

# Loop through each chromosome of the reference genome
for ref_chrom_file in "$REF_CHROM_DIR"/*.fna; do
    if [ -e "$ref_chrom_file" ]; then
        CHROM_BASENAME=$(basename "$ref_chrom_file" .fna)
        echo "Processing chromosome: $CHROM_BASENAME..."

        # Find the corresponding target chromosome file by matching names
        target_chrom_file="$TARGET_CHROM_DIR/${CHROM_BASENAME}.fna"
        if [ ! -f "$target_chrom_file" ]; then
            echo "⚠️  Warning: No corresponding target chromosome file found for '$CHROM_BASENAME'. Skipping."
            continue
        fi

        # Define file paths for this chromosome's intermediate and final outputs
        PREFIX="$OUTPUT_DIR/${REF_NAME}_vs_${TARGET_NAME}.${CHROM_BASENAME}"
        FILTERED_DELTA_FILE="${PREFIX}.filtered.delta"
        SNPS_FILE="${PREFIX}.snps"
        VCF_FILE="${PREFIX}.vcf"

        # Step 1: Align reference chromosome with target chromosome
        echo "  Step 1/4: Aligning with nucmer..."
        nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file"

        # Step 2: Filter for 1-to-1 alignments
        echo "  Step 2/4: Filtering alignments with delta-filter..."
        delta-filter -1 "${PREFIX}.delta" > "$FILTERED_DELTA_FILE"

        # Step 3: Identify SNPs and INDELs
        echo "  Step 3/4: Identifying variants with show-snps..."
        show-snps -H -T "$FILTERED_DELTA_FILE" > "$SNPS_FILE"

        # Step 4: Convert .snps to pseudo-VCF format
        echo "  Step 4/4: Converting .snps to pseudo-VCF..."
        python3 all2vcf/all2vcf mummer \
          --snps "$SNPS_FILE" \
          --reference "$ref_chrom_file" \
          > "$VCF_FILE"

        # Add the generated VCF file to our list for merging
        VCF_FILES_TO_MERGE+=("$VCF_FILE")
        echo "VCF for $CHROM_BASENAME created at $VCF_FILE"
        echo ""
    fi
done

# Deactivate the python environment
deactivate
echo ""

# --- 4. Merge VCFs and Clean Up ---
echo "--- 4. Merging Per-Chromosome VCFs ---"

if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then
    echo "Error: No VCF files were generated. Nothing to merge."
    exit 1
fi

FINAL_VCF_FILE="$OUTPUT_DIR/${REF_NAME}_vs_${TARGET_NAME}.merged.vcf"

echo "Merging ${#VCF_FILES_TO_MERGE[@]} VCF files into one..."
# Use bcftools to concatenate all the individual VCF files.
# The list of files is sorted to ensure correct ordering.
bcftools concat --allow-overlaps -O v -o "$FINAL_VCF_FILE" $(printf "%s\n" "${VCF_FILES_TO_MERGE[@]}" | sort)

echo "Cleaning up intermediate files..."
# Remove the individual chromosome VCFs and other alignment files
for vcf in "${VCF_FILES_TO_MERGE[@]}"; do
    chrom_prefix=${vcf%.vcf}
    rm -f "${chrom_prefix}.delta" "${chrom_prefix}.filtered.delta" "${chrom_prefix}.snps" "${chrom_prefix}.vcf"
done
echo "Cleanup complete."
echo ""

# --- 5. Output ---
echo "--- Pipeline Complete ---"
echo "Success! The final merged pseudo-VCF file has been created at: $FINAL_VCF_FILE"
ls -lh "$FINAL_VCF_FILE"