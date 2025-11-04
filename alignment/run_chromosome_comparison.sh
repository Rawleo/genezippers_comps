#!/bin/bash
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
TARGET_CODENAME="hg19"
START_CHROM="$1"
END_CHROM="$2"

REF_CHROM_DIR="files/genomes/$REF_CODENAME"
TARGET_CHROM_DIR="files/genomes/$TARGET_CODENAME"
FINAL_FORMATTED_VCF="files/output/${REF_CODENAME}_${TARGET_CODENAME}_sorted_variants.txt"

if [ -n "$START_CHROM" ] && [ -z "$END_CHROM" ]; then
	END_CHROM="$START_CHROM"
fi

echo ""
echo "=========== CHROMOSOME COMPARISON ==========="
echo ""
echo "Starting comparison: $REF_CODENAME vs $TARGET_CODENAME..."
if [ -n "$START_CHROM" ]; then
	echo "Range: Chromosomes $START_CHROM to $END_CHROM"
fi
echo ""

echo "Setting up directory structure..."
GENOME_DIR="files/genomes"
OUTPUT_DIR="files/output"
mkdir -p "$GENOME_DIR" "$OUTPUT_DIR"
echo ""

echo "Checking for required dependencies..."

# Tool Pathing if in $PATH.
COMMANDS=("wget" "gunzip" "git" "python3" "nucmer" "delta-filter" "show-snps" "bcftools")

# Tool Pathing if locally installed.
# COMMANDS=("wget" "gunzip" "git" "python3" "./tools/mummer/bin/nucmer" "./tools/mummer/bin/delta-filter" "./tools/mummer/bin/show-snps" "bcftools")

for cmd in "${COMMANDS[@]}"; do
	if ! command -v "$cmd" &>/dev/null; then
		echo "Error: Required command '$cmd' is not installed or not in your PATH."
		exit 1
	fi
done
echo "All dependencies found."
echo ""

# 1. Use awk to process the file and generate the formatted output.
# 2. Pipe (|) the output of awk directly into the multi-level sort command.
format_to_vcf() {
	awk '
# Helper function to generate a string by repeating a character N times.
function repeat(char, n,    result, i) {
    result = ""
    for (i = 1; i <= n; i++) {
        result = result char
    }
    return result
}

# BEGIN block runs once before processing any lines.
BEGIN {
    # Set the Output Field Separator to a comma.
    OFS=","
}

# This main block runs for every line in the input file.
!/^#/ {
    # Default values are for SNPs (where REF and ALT lengths are equal).
    flag = 0
    ref_out = $4
    alt_out = $5
    
    # --- Indel Logic ---
    # This block only runs if the REF and ALT alleles have different lengths.
    if (length($4) != length($5)) {
        # 1. Find the number of common characters at the beginning of the alleles.
        common_prefix_len = 0
        min_len = (length($4) < length($5)) ? length($4) : length($5)
        for (i = 1; i <= min_len; i++) {
            if (substr($4, i, 1) != substr($5, i, 1)) {
                break
            }
            common_prefix_len++
        }
        
        # 2. Extract the part of the alleles that is actually different.
        ref_change = substr($4, common_prefix_len + 1)
        alt_change = substr($5, common_prefix_len + 1)

        # 3. Apply new formatting based on variant type.
        if (length($4) > length($5)) { # Deletion
            flag = 1
            ref_out = ref_change
            alt_out = repeat("-", length(ref_change))
        } 
        else { # Insertion
            flag = 2
            ref_out = repeat("-", length(alt_change))
            alt_out = alt_change
        }
    }

    # Print the final, formatted line.
    print flag, $1, $2, ref_out"/"alt_out
}
' "$1" | sort -t ',' -k 1,1n -k 2,2V -k 3,3n >$2
}

# --- Begin Per-Chromosome Genome Comparison ---
echo "--- Running Per-Chromosome Comparison ---"
echo ""

declare -a files_to_process

# Selects files for processing based on the user's range
# or defaults to all available fasta files if no range was given.
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

# Activate Python Environment (if necessary).
source all2vcf/all_to_vcf/bin/activate

# --- Process Each Chromosome With Parallelization ---
for ref_chrom_file in "${files_to_process[@]}"; do (
	CURRENT_FILE=$((CURRENT_FILE + 1))
	CHROM_BASENAME=$(basename "$ref_chrom_file" .fna)

	target_chrom_file="$TARGET_CHROM_DIR/${CHROM_BASENAME}.fna"

	if [ ! -f "$target_chrom_file" ]; then continue; fi

	PREFIX="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.${CHROM_BASENAME}"

	# Tool Pathing if installed in $PATH.
	nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file" &>/dev/null
	delta-filter -1 "${PREFIX}.delta" >"${PREFIX}.filtered.delta" 2>/dev/null
	show-snps -H -T "${PREFIX}.filtered.delta" >"${PREFIX}.snps" 2>/dev/null
	python3 all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" >"${PREFIX}.vcf" 2>/dev/null

	# Tool Pathing if locally installed.
	# ./tools/mummer/bin/nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file" &> /dev/null
	# ./tools/mummer/bin/delta-filter -1 "${PREFIX}.delta" > "${PREFIX}.filtered.delta" 2>/dev/null
	# ./tools/mummer/bin/show-snps -H -T "${PREFIX}.filtered.delta" > "${PREFIX}.snps" 2>/dev/null
	# python3 tools/all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" > "${PREFIX}.vcf" 2>/dev/null

) & done

# Wait for all parallelized processes to complete.
wait

# Deactivate Python Environment (if necessary).
deactivate

# --- Locating VCF Files ---
unset VCF_FILES_TO_MERGE
declare -a VCF_FILES_TO_MERGE

if [ -z "$START_CHROM" ]; then
	OUTPUT_DIR="files/output"
	VCF_FILES_TO_MERGE=($(ls -v "$OUTPUT_DIR"/*.chr*.vcf))
else
	for i in $(seq "$START_CHROM" "$END_CHROM"); do
		OUTPUT_DIR="files/output"
		found_file=$(ls -v "${OUTPUT_DIR}/"*.chr${i}.vcf)
		if [ -f "$found_file" ]; then VCF_FILES_TO_MERGE+=("$found_file"); fi
	done
fi

echo "Found VCF Files: ${VCF_FILES_TO_MERGE[@]}"
if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then
	echo " Error: No VCF files were generated."
	exit 1
fi

# --- Cleaning Used Files ---
# echo "Cleaning up intermediate files..."
# rm -f "$OUTPUT_DIR"/${REF_CODENAME}_vs_${TARGET_CODENAME}.chr*.{delta,filtered.delta,snps,vcf}
# echo " Cleanup complete."
# echo ""

# --- Merging ---
echo ""
echo "--- Merging Per-Chromosome VCFs ---"
echo ""
FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.merged.vcf"
rm $FINAL_VCF_FILE 2>/dev/null || true
for vcf_file in "${VCF_FILES_TO_MERGE[@]}"; do cat $vcf_file >>$FINAL_VCF_FILE; done

# --- Output ---
echo " Success! The final merged pseudo-VCF file is located at:"
ls -lh "$FINAL_VCF_FILE"

echo ""
echo "=========== END CHROMOSOME COMPARISON ==========="
echo ""
