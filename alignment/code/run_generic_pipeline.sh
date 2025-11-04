#!/bin/bash

# This generic script automates converting MUMmer4 .snps output to a pseudo-VCF file.
# It accepts two command-line arguments: the reference and target taxon names.
# It organizes files into two separate directories:
# - Genomes: 'files/genomes/'
# - Outputs: 'files/output/'

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 0. Configuration and Prerequisite Check ---

# Check for command-line arguments
if [ "$#" -ne 2 ]; then
    echo "❌ Error: Invalid number of arguments."
    echo "Usage: $0 \"<Reference Taxon Name>\" \"<Target Taxon Name>\""
    echo "Example: $0 \"Escherichia coli\" \"Salmonella enterica\""
    exit 1
fi

REF_TAXON="$1"
TARGET_TAXON="$2"

# Create simple, filesystem-safe names from the taxon names
REF_NAME=$(echo "$REF_TAXON" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
TARGET_NAME=$(echo "$TARGET_TAXON" | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

echo "🚀 Starting pipeline..."
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
COMMANDS=("datasets" "git" "python3" "nucmer" "delta-filter" "show-snps")
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Error: Required command '$cmd' is not installed or not in your PATH."
        exit 1
    fi
done
echo "✅ All dependencies found."
echo ""

# --- 1. Acquire FASTA Files ---
echo "--- 1. Acquiring FASTA files ---"
# Define full paths for the FASTA files within the genome directory
REF_FNA="$GENOME_DIR/${REF_NAME}.fna"
TARGET_FNA="$GENOME_DIR/${TARGET_NAME}.fna"

# Download Reference Genome
if [ ! -f "$REF_FNA" ]; then
    echo "Downloading '$REF_TAXON' reference genome..."
    datasets download genome taxon "$REF_TAXON" \
      --reference \
      --filename "${REF_NAME}.zip" \
      --include genome
    unzip -o "${REF_NAME}.zip"
    REF_FNA_PATH=$(find ncbi_dataset -name "*.fna" -print -quit)
    mv "$REF_FNA_PATH" "$REF_FNA"
    rm -rf ncbi_dataset README.md "${REF_NAME}.zip" # Clean up temp files
    echo "Reference genome placed in $REF_FNA"
else
    echo "Reference genome ($REF_FNA) already exists. Skipping download."
fi

# Download Target Genome
if [ ! -f "$TARGET_FNA" ]; then
    echo "Downloading '$TARGET_TAXON' target genome..."
    datasets download genome taxon "$TARGET_TAXON" \
      --reference \
      --filename "${TARGET_NAME}.zip" \
      --include genome
    unzip -o "${TARGET_NAME}.zip"
    TARGET_FNA_PATH=$(find ncbi_dataset -name "*.fna" -print -quit)
    mv "$TARGET_FNA_PATH" "$TARGET_FNA"
    rm -rf ncbi_dataset README.md md5sum.txt "${TARGET_NAME}.zip" # Clean up temp files
    echo "Target genome placed in $TARGET_FNA"
else
    echo "Target genome ($TARGET_FNA) already exists. Skipping download."
fi
echo ""

# --- 2. Install all2vcf ---
echo "--- 2. Installing all2vcf ---"
if [ ! -d "all2vcf" ]; then
    echo "Cloning all2vcf repository..."
    git clone https://github.com/MatteoSchiavinato/all2vcf.git
else
    echo "all2vcf directory already exists. Skipping clone."
fi

echo "Setting up Python virtual environment for all2vcf..."
cd all2vcf
python3 -m venv all_to_vcf
source all_to_vcf/bin/activate
echo "Installing required Python packages..."
# Assumes requirements.txt is in the base directory, one level up from here
pip install -r ../requirements.txt > /dev/null
deactivate
cd ..
echo "✅ all2vcf setup complete."
echo ""

# --- 3. Compare Genomes and Generate Pseudo-VCF ---
echo "--- 3. Running Genome Comparison and Conversion ---"
# Define file paths for intermediate and final outputs in the output directory
PREFIX="$OUTPUT_DIR/${REF_NAME}_vs_${TARGET_NAME}"
FILTERED_DELTA_FILE="${PREFIX}.filtered.delta"
SNPS_FILE="${PREFIX}.snps"
VCF_FILE="${PREFIX}.vcf"

# Step 1: Align reference with target
echo "Step 1/4: Aligning genomes with nucmer..."
nucmer -p "$PREFIX" "$REF_FNA" "$TARGET_FNA"

# Step 2: Filter for 1-to-1 alignments
echo "Step 2/4: Filtering alignments with delta-filter..."
delta-filter -1 "${PREFIX}.delta" > "$FILTERED_DELTA_FILE"

# Step 3: Identify SNPs and INDELs
echo "Step 3/4: Identifying variants with show-snps..."
show-snps -H -T "$FILTERED_DELTA_FILE" > "$SNPS_FILE"

# Step 4: Convert .snps to pseudo-VCF format
echo "Step 4/4: Converting .snps file to pseudo-VCF with all2vcf..."
source all2vcf/all_to_vcf/bin/activate
python3 all2vcf/all2vcf mummer \
  --snps "$SNPS_FILE" \
  --reference "$REF_FNA" \
  > "$VCF_FILE"
deactivate
echo ""

# --- 4. Output ---
echo "--- Pipeline Complete ---"
echo "✅ Success! The pseudo-VCF file has been created at: $VCF_FILE"
ls -lh "$VCF_FILE"