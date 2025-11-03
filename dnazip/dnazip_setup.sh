#!/bin/bash

# --- Directory Configuration ---
DATA_DIR="./data"
CHR_DIR="${DATA_DIR}/chr"
DBSNP_DIR="${DATA_DIR}/dbSNP"
VCF_DIR="${DATA_DIR}/vcf"
VARIANT_DIR=${DATA_DIR}/variants

# --- Executable Files ---
DBSNP_PY="./code/preprocess_dbsnp.py"
BIGBEDTOBED="./tools/bigBedToBed"

# --- Filename Configuration ---
BIGBED_FILE="dbSnp155Common.bb"
BIGBED_BASENAME="dbSnp155Common.bb"

# --- URLs ---
HG38_BASE_URL="https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/"
BIGBED_URL="https://hgdownload.soe.ucsc.edu/gbdb/hg38/snp/dbSnp155Common.bb"
BINARY_URL="https://hgdownload.soe.ucsc.edu/admin/exe/"

# --- CHROMOSOMES ---
CHROMOSOMES=(
    "chr1" "chr2" "chr3" "chr4" "chr5" "chr6" "chr7" "chr8" "chr9" "chr10"
    "chr11" "chr12" "chr13" "chr14" "chr15" "chr16" "chr17" "chr18" "chr19"
    "chr20" "chr21" "chr22" "chrX" "chrY"
)

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "A unified script for bioinformatics data preparation with organized output."
    echo ""
    echo "Commands:"
    echo "  --create-missing-subdirectories Creates missing subdirectories for the DNAZip project."
    echo "  --download-hg38                 Downloads hg38 genome files into '${CHR_DIR}/'."
    echo "  --prepare-dbsnp                 Prepares dbSNP files in '${DBSNP_DIR}/'."
    echo "  --process-dbsnp                 Converts the dbSNP files to the appropriate format."
    echo "  --run-all                       Run everything."
    echo "  --download-giab-trio            Automatically downloads the GIAB HG002, HG003, and HG004 VCFs into '${VCF_DIR}/'."
    echo "  --process-vcf                   Processes the HG002-4 .vcf files from '${VCF_DIR}/'."
    echo "  --guide                         Displays the full user and methods guide."
    echo "  --help, -h                      Show this help message."
    echo ""
    exit 1
}

show_guide() {
cat << 'EOF'

--------------------------------------------------------------------------------
Prerequisites
--------------------------------------------------------------------------------

Before you begin, ensure you have the following software installed:

1. `bcftools`: A powerful toolset for manipulating VCF files.
2. `bigBedToBed`: Unpacks .bb file for common dbSNPs.
3. Standard Unix Tools: The script uses `wget`, `awk`, and `sort`, which are
   pre-installed on virtually all Linux and macOS systems.

--------------------------------------------------------------------------------
GIAB Trio Variant Processing
--------------------------------------------------------------------------------

This script can automatically download and process the high-confidence VCF
files for the GIAB Ashkenazim Trio (Son HG002, Father HG003, Mother HG004).

To run the entire automated pipeline, use the `--run-all` command:

   Example:
   ./dnazip_pipeline.sh --process-vcf

The script will perform the following steps for each of the three samples:
1.  Check if the VCF file exists in the './data/vcf/' directory.
2.  If not found, it will download the correct file from the GIAB FTP server.
3.  Process the VCF file into the sorted, comma-separated format.
4.  Save the output to a file named 'HG00#_GRCh38_sorted_variants.txt'.

--------------------------------------------------------------------------------
Output Format
--------------------------------------------------------------------------------

The output is a comma-separated text file with four columns:
Flag,Chromosome,Position,Alleles

Example line: 0,chr20,64283802,C/T

1.  **Flag**: An integer (0, 1, or 2) indicating the variant type.
    * `0`: SNP (Single Nucleotide Polymorphism) or MNP (Multi-Nucleotide Polymorphism).
    * `1`: Deletion.
    * `2`: Insertion.

2.  **Chromosome**: The chromosome identifier (e.g., `chr20`).

3.  **Position**: The 1-based genomic coordinate of the variant.

4.  **Alleles**: A representation of the reference and alternate alleles.
    * For SNPs/MNPs (`Flag 0`): `REF/ALT` (e.g., `C/T`)
    * For Deletions (`Flag 1`): `REF/---` (e.g., `GTC/---`)
    * For Insertions (`Flag 2`): `---/ALT` (e.g., `---/AAG`)

The final file is numerically sorted by Flag, then chromosomally by Position.

EOF
exit 0
}

# Checks if all required command-line utilities are installed.
check_dependencies() {
    for tool in "$@"; do
        if ! command -v "$tool" &> /dev/null; then
            echo "Error: Required utility '$tool' could not be found."
            echo "Please install '$tool' and ensure it is in your system's PATH."
            exit 1
        fi
    done
}

# CREATE dnazaip/ SUBDIRECTORIES
create_missing_subdirectories() {

    echo ""
    echo "-------------- Start Missing Subdirectories --------------"
    echo "Creating subdirectories."

    mkdir -p ./data/chr
    mkdir -p ./data/dbSNP
    mkdir -p ./data/huffman_trees
    mkdir -p ./data/output
    mkdir -p ./data/output/csv
    mkdir -p ./data/vcf
    mkdir -p ./figures
    mkdir -p ./tools

    echo "Subdirectory setup complete."
    echo "-------------- End Missing Subdirectories --------------"
    echo ""
}

# --- Download hg38 Reference Genome ---
download_genome_references() {
    echo ""
    echo "-------------- Starting Download of hg38 Chromosome Files --------------"
    echo "Output directory: ${CHR_DIR}/"
    check_dependencies "wget" "gunzip"
    mkdir -p "$CHR_DIR"

    for CHR in "${CHROMOSOMES[@]}"; do
        GZ_BASENAME="${CHR}.fa.gz"
        FA_PATH="${CHR_DIR}/${CHR}.fa"
        GZ_PATH="${CHR_DIR}/${GZ_BASENAME}"
        FULL_URL="${HG38_BASE_URL}${GZ_BASENAME}"

        echo ""
        echo "Processing ${CHR}..."

        if [ -f "$FA_PATH" ]; then
            echo "--> '${FA_PATH}' already exists. Skipping."
            continue
        fi

        echo "--> Downloading ${GZ_BASENAME}..."
        wget -q -P "$CHR_DIR" --show-progress "$FULL_URL"

        if [ $? -ne 0 ]; then
            echo "--> ERROR: Download failed for ${GZ_BASENAME}."
        else
            echo "--> Unpacking ${GZ_PATH}..."
            gunzip "$GZ_PATH"
            echo "--> Done."
        fi
    done
    echo "--- hg38 Chromosome Download Complete ---"
    echo ""
}

# --- DOWNLOAD & EXTRACT dbSNP COMMON VARIANTS ---
prepare_dbsnp() {
    echo "--- Starting Preparation of dbSNP Data ---"
    echo "Output directory: ${DBSNP_DIR}/"
    check_dependencies "wget"
    mkdir -p "$DBSNP_DIR"

    local BIGBED_FILE_PATH="${DBSNP_DIR}/${BIGBED_FILE}"

    if ! [ -f "$BIGBEDTOBED" ]; then
        echo "Error: --> '${BIGBEDTOBED}' is not in the ./tools subdirectory."
        echo "Please install at '${BINARY_URL}'. Exiting."
        exit 1
    fi

    if [ ! -f "$BIGBED_FILE_PATH" ]; then
        echo "Input file '$BIGBED_FILE_PATH' not found. Attempting to download..."
        wget -P "$DBSNP_DIR" "$BIGBED_URL"
        if [ $? -ne 0 ]; then
            echo "Error: Download failed. Please check the URL or your network connection."
            exit 1
        fi
        echo "Download complete."
    fi

    echo "Starting batch conversion of '$BIGBED_FILE_PATH'..."
    for CHR in "${CHROMOSOMES[@]}"; do
        OUTPUT_FILE="${DBSNP_DIR}/${CHR}.txt"

        # Check if the output file already exists to avoid re-processing.
        if [ -f "$OUTPUT_FILE" ]; then
            echo "--> '${OUTPUT_FILE}' already exists. Skipping."
            continue
        fi

        echo "Extracting ${CHR} to ${OUTPUT_FILE}..."
        ./tools/bigBedToBed "$BIGBED_FILE_PATH" -chrom="$CHR" "$OUTPUT_FILE"
        if [ $? -ne 0 ]; then
            echo "Warning: Command failed for ${CHR}."
        fi
    done
    echo ""
    echo "--- dbSNP Data Download Complete ---"

    process_dbsnp
}

# --- Convert dbSNP to Correct Format ---
process_dbsnp() {

    echo ""
    echo "--- Convert dbSNP to Proper Format ---"
    check_dependencies "python3"

    for CHR in "${CHROMOSOMES[@]}"; do
        INPUT_FILE="${DBSNP_DIR}/${CHR}.txt"

        if ! [ -f "$INPUT_FILE" ]; then
            echo "ERROR: --> '${INPUT_FILE}' does not exit. Please download '{$INPUT_FILE}'."
            exit 1
        fi
    done

    python3 $DBSNP_PY

    echo "--- FINISHED dbSNP to Proper Format ---"
    echo ""
}

# --- DOWNLOAD GIAB Trio .vcf VARIANT FILES ---
download_giab_trio() {
    echo ""
    echo "--- Starting Automated Download of GIAB Ashkenazim Trio ---"
    check_dependencies "wget"

    local SAMPLES=("HG002" "HG003" "HG004")
    local URLS=(
        "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG002_NA24385_son/NISTv4.2.1/GRCh38/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz"
        "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG003_NA24149_father/NISTv4.2.1/GRCh38/HG003_GRCh38_1_22_v4.2.1_benchmark.vcf.gz"
        "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/AshkenazimTrio/HG004_NA24143_mother/NISTv4.2.1/GRCh38/HG004_GRCh38_1_22_v4.2.1_benchmark.vcf.gz"
    )

    mkdir -p "$VCF_DIR"

    # --- Download all necessary VCF files ---
    echo "--> Checking for and downloading required VCF files..."
    for i in "${!SAMPLES[@]}"; do
        local sample=${SAMPLES[$i]}
        local vcf_url=${URLS[$i]}
        local input_vcf_basename=$(basename "$vcf_url")
        local input_vcf_path="${VCF_DIR}/${input_vcf_basename}"

        if [ ! -f "$input_vcf_path" ]; then
            echo "    -> Downloading VCF for ${sample}..."
            wget -q -P "$VCF_DIR" --show-progress "$vcf_url"
            if [ $? -ne 0 ]; then
                echo "    -> ERROR: Download failed for ${sample}."
            else
                echo "    -> Download for ${sample} complete."
            fi
        else
            echo "    -> VCF for ${sample} already exists."
        fi
    done
    echo "--> Download check complete."
    echo ""

    # --- Verify all files exist, so they can be processed further ---
    local all_files_present=true
    for vcf_url in "${URLS[@]}"; do
        local input_vcf_basename=$(basename "$vcf_url")
        local input_vcf_path="${VCF_DIR}/${input_vcf_basename}"
        if [ ! -f "$input_vcf_path" ]; then
            echo "Error: Missing VCF file '${input_vcf_basename}' after download attempt. Cannot proceed."
            all_files_present=false
        fi
    done

    if [ "$all_files_present" = false ]; then
        exit 1
    fi
    echo "--- All VCF files verified. ---"
    echo ""
}

# Duplicates the style of the original DNAZip implementation.
# Formats indels with full nucleotides on one side and dashes for
# the length difference on the other, without trimming the anchor base.
process_vcf() {
    # Stop the script if any command fails
    set -e

    # --- 1. Configuration ---
    SAMPLES=("HG004" "HG002" "HG003")

    mkdir -p "$VARIANT_DIR"

    echo ""
    echo "Being processing of .vcf variant files with bcftools."
    echo "================================================="

    # --- Check for necessary tools ---
    if ! command -v bcftools &> /dev/null; then
        echo "Error: bcftools is not installed or not in your PATH."
        echo "Download bcftools and ensure it is executable."
        echo "https://www.htslib.org/download/"
        exit 1
    fi
    if ! command -v awk &> /dev/null; then
        echo "Error: awk is not installed or not in your PATH."
        exit 1
    fi

    echo "Starting variant processing for ${#SAMPLES[@]} samples..."

    # --- 2. Main Loop ---
    for SAMPLE_ID in "${SAMPLES[@]}"; do
        echo "================================================="
        echo "Processing sample: $SAMPLE_ID"
        echo "================================================="

        # --- Variable Setup ---
        INPUT_VCF="${VCF_DIR}/${SAMPLE_ID}_GRCh38_1_22_v4.2.1_benchmark.vcf.gz"
        FINAL_OUTPUT="${VARIANT_DIR}/${SAMPLE_ID}_GRCh38_sorted_variants.txt"
        NORMALIZED_VCF="${VCF_DIR}/${SAMPLE_ID}.norm.vcf.gz"
        SNPS_TXT="${VCF_DIR}/${SAMPLE_ID}.snps.txt"
        MNPS_TXT="${VCF_DIR}/${SAMPLE_ID}.mnps.txt"
        DELS_TXT="${VCF_DIR}/${SAMPLE_ID}.dels.txt"
        INS_TXT="${VCF_DIR}/${SAMPLE_ID}.ins.txt"

        if [ ! -f "$INPUT_VCF" ]; then
            echo "Warning: Input file not found for $SAMPLE_ID. Skipping."
            continue
        fi

        # --- STEP 1: Normalize VCF ---
        echo "-> Step 1/4: Normalizing VCF to split and left-align variants..."
        bcftools norm -m - "$INPUT_VCF" -Oz -o "$NORMALIZED_VCF"
        bcftools index "$NORMALIZED_VCF"

        # --- STEP 2: Query each variant type with advanced formatting ---
        echo "-> Step 2/4: Querying SNPs, MNPs, deletions, and insertions..."

        # Query Single-Nucleotide Polymorphisms (SNPs)
        bcftools query -i 'STRLEN(REF)==1 && STRLEN(ALT)==1 && TYPE="snp"' \
            -f'0,%CHROM,%POS,%REF/%ALT\n' "$NORMALIZED_VCF" > "$SNPS_TXT"

        # Query Multi-Nucleotide Polymorphisms (MNPs) and filter for first letter
        bcftools query -i 'STRLEN(REF)>1 && STRLEN(REF)==STRLEN(ALT)' \
            -f'0,%CHROM,%POS,%REF/%ALT\n' "$NORMALIZED_VCF" | \
            awk -F '[,/]' '{printf "%s,%s,%s,%s/%s\n", $1, $2, $3, substr($4,1,1), substr($5,1,1)}' > "$MNPS_TXT"

        # --- Reusable AWK script for advanced indel formatting ---
        AWK_INDEL_SCRIPT='
        {
            ref=$4; alt=$5;
            
            # Deletion: REF is longer than ALT
            if (length(ref) > length(alt)) {
                len_diff = length(ref) - length(alt);
                dashes = "";
                for (i=1; i<=len_diff; i++) { dashes = dashes"-" }
                ref_out = ref;
                alt_out = dashes;
            }
            # Insertion: ALT is longer than REF
            else if (length(alt) > length(ref)) {
                len_diff = length(alt) - length(ref);
                dashes = "";
                for (i=1; i<=len_diff; i++) { dashes = dashes"-" }
                ref_out = dashes;
                alt_out = alt;
            }
            # Fallback for any other case (should not be hit by bcftools query)
            else {
                ref_out = ref;
                alt_out = alt;
            }
            
            printf "%s,%s,%s,%s/%s\n", $1, $2, $3, ref_out, alt_out
        }'

        # Query Deletions and pipe to the AWK script
        bcftools query -i 'STRLEN(REF) > STRLEN(ALT)' -f'1,%CHROM,%POS,%REF/%ALT\n' "$NORMALIZED_VCF" | \
            awk -F '[,/]' "$AWK_INDEL_SCRIPT" > "$DELS_TXT"

        # Query Insertions and pipe to the AWK script
        bcftools query -i 'STRLEN(REF) < STRLEN(ALT)' -f'2,%CHROM,%POS,%REF/%ALT\n' "$NORMALIZED_VCF" | \
            awk -F '[,/]' "$AWK_INDEL_SCRIPT" > "$INS_TXT"

        # --- STEP 3: Concatenate ---
        echo "-> Step 3/4: Creating the unified file: $FINAL_OUTPUT..."
        cat "$SNPS_TXT" "$MNPS_TXT" "$DELS_TXT" "$INS_TXT" | sort -u > "$FINAL_OUTPUT"

        # --- STEP 4: Clean Up ---
        echo "-> Step 4/4: Cleaning up intermediate files for $SAMPLE_ID..."
        rm "$NORMALIZED_VCF" "$NORMALIZED_VCF.csi"
        rm "$SNPS_TXT" "$MNPS_TXT" "$DELS_TXT" "$INS_TXT"

        echo "Success! Unified file created: $FINAL_OUTPUT"
    done

    echo "================================================="
    echo "All samples processed successfully."
    echo ""
}

# --- Main Script Logic: Argument Parsing ---

echo ""
echo "BEGINNING DNAZIP PROJECT SET-UP"
echo "================================================="

if [ "$#" -eq 0 ]; then
    echo "Error: No command provided."
    usage
fi

case "$1" in
    --create-missing-subdirectories)
        create_missing_subdirectories
        ;;
    --download-hg38)
        download_genome_references
        ;;
    --prepare-dbsnp)
        prepare_dbsnp
        ;;
    --process-dbsnp)
        process_dbsnp
        ;;
    --download-giab-trio)
        download_giab_trio
        ;;
    --process-vcf)
        process_vcf
        ;;
    --run-all)
        create_missing_subdirectories
        download_genome_references
        prepare_dbsnp
        download_giab_trio
        process_vcf
        ;;
    --guide)
        show_guide
        ;;
    -h|--help)
        usage
        ;;
    *)
        echo "Error: Unknown command '$1'"
        usage
        ;;
esac

echo "FINISHED DNAZIP PROJECT SET-UP"
echo "================================================="
echo ""

exit 0



