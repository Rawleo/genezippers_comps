#!/bin/bash

# This script automates the comparison of E. coli (reference) and Salmonella enterica (target),
# converting MUMmer4 .snps output to a pseudo-VCF file.
# It organizes files into two separate directories:
# - Genomes: 'files/bacteria_genomes/'
# - Outputs: 'files/bacteria_output/'

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 0. Configuration and Prerequisite Check ---

echo "🚀 Starting pipeline for E. coli vs. Salmonella enterica..."
echo ""

echo "🔧 Setting up directory structure..."
# Define the separate directories for genomes and output files.
GENOME_DIR="files/bacteria_genomes"
OUTPUT_DIR="files/bacteria_output"
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
# Define full paths for the FASTA files
ECOLI_FNA="$GENOME_DIR/ecoli.fna"
SALMONELLA_FNA="$GENOME_DIR/salmonella.fna"

# Download E. coli (reference)
if [ ! -f "$ECOLI_FNA" ]; then
    echo "Downloading Escherichia coli reference genome..."
    datasets download genome taxon "Escherichia coli" \
      --reference \
      --filename ecoli.zip \
      --include genome
    unzip -o ecoli.zip
    ECOLI_FNA_PATH=$(find ncbi_dataset -name "*.fna" -print -quit)
    mv "$ECOLI_FNA_PATH" "$ECOLI_FNA"
    rm -rf ncbi_dataset README.md ecoli.zip md5sum.txt # Clean up temp files
    echo "E. coli genome placed in $ECOLI_FNA"
else
    echo "E. coli genome ($ECOLI_FNA) already exists. Skipping download."
fi

# Download Salmonella enterica (target)
if [ ! -f "$SALMONELLA_FNA" ]; then
    echo "Downloading Salmonella enterica target genome..."
    datasets download genome taxon "Salmonella enterica" \
      --reference \
      --filename salmonella.zip \
      --include genome
    unzip -o salmonella.zip
    SALMONELLA_FNA_PATH=$(find ncbi_dataset -name "*.fna" -print -quit)
    mv "$SALMONELLA_FNA_PATH" "$SALMONELLA_FNA"
    rm -rf ncbi_dataset README.md salmonella.zip # Clean up temp files
    echo "Salmonella enterica genome placed in $SALMONELLA_FNA"
else
    echo "Salmonella enterica genome ($SALMONELLA_FNA) already exists. Skipping download."
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
# Define file paths for intermediate and final outputs
PREFIX="$OUTPUT_DIR/ecoli_vs_salmonella"
FILTERED_DELTA_FILE="${PREFIX}.filtered.delta"
SNPS_FILE="${PREFIX}.snps"
VCF_FILE="${PREFIX}.vcf"

# Step 1: Align reference with target
echo "Step 1/4: Aligning genomes with nucmer..."
nucmer -p "$PREFIX" "$ECOLI_FNA" "$SALMONELLA_FNA"

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
  --reference "$ECOLI_FNA" \
  > "$VCF_FILE"
deactivate
echo ""

# --- 4. Output ---
echo "--- Pipeline Complete ---"
echo "✅ Success! The pseudo-VCF file has been created at: $VCF_FILE"
ls -lh "$VCF_FILE"