#!/bin/bash
#
# Find and merge VCF files based on chromosome arguments.
# Used in the event that create_vcf.sh fails to properly
# merge VCF files into one large VCF file.
#
# Usage (all chroms): ./merge_vcfs.sh
# Usage (range):      ./merge_vcfs.sh 1 5
# Usage (list):       ./merge_vcfs.sh 1 X M

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Global Configuration ---

# Genome assemblies
REF_CODENAME="hg38"
TARGET_CODENAME="Han1"

# Directories
GENOME_DIR="../files/genomes"
OUTPUT_DIR="../files/output_${TARGET_CODENAME}/merge"

# Global array to be populated by the find function
declare -a VCF_FILES_TO_MERGE

# --- Function Definitions ---

### Setup Functions

setup_environment() {
	echo "Setting up directory structure..."
	mkdir -p "$GENOME_DIR" "$OUTPUT_DIR"
	echo "Done."
	echo ""
}

### File List Generation Functions

find_vcfs_to_merge() {
	echo "--- Locating VCF Files ---"

	# Regex to check if a string is a non-negative integer
	local integer_regex='^[0-9]+$'
	local start_chrom="$1"
	local end_chrom="$2"

	if [ "$#" -eq 0 ]; then
		# No arguments, merge all found VCFs
		echo "No specific chromosomes given, merging all VCFs found in $OUTPUT_DIR/"
		VCF_FILES_TO_MERGE=($(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.vcf" | sort -V 2>/dev/null || true))

	elif [ "$#" -eq 2 ] && [[ "$start_chrom" =~ $integer_regex ]] && [[ "$end_chrom" =~ $integer_regex ]]; then
		# Two numeric arguments: process as a range
		echo "Processing chromosome range: $start_chrom to $end_chrom"
		for chrom_id in $(seq "$start_chrom" "$end_chrom"); do
			local found_files_list=($(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.chr${chrom_id}.vcf" 2>/dev/null || true))
			if [ ${#found_files_list[@]} -gt 0 ]; then
				VCF_FILES_TO_MERGE+=("${found_files_list[@]}")
			else
				echo "Warning: VCF file not found for '$chrom_id' (checked for *.chr${chrom_id}.vcf)"
			fi
		done

	else
		# One or more arguments: process as a list
		echo "Looking for VCFs matching: $@"
		for chrom_id in "$@"; do
			# Find VCF files matching the chromosome ID, e.g., *.chrX.vcf
			local found_files_list=($(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.chr${chrom_id}.vcf" 2>/dev/null || true))

			if [ ${#found_files_list[@]} -gt 0 ]; then
				VCF_FILES_TO_MERGE+=("${found_files_list[@]}")
			else
				# Handle common M -> MT mapping
				if [[ "$chrom_id" == "M" || "$chrom_id" == "m" ]]; then
					local found_files_mt_list=($(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.chrMT.vcf" 2>/dev/null || true))
					if [ ${#found_files_mt_list[@]} -gt 0 ]; then
						VCF_FILES_TO_MERGE+=("${found_files_mt_list[@]}")
						echo "Note: Mapping input 'M' to '*.chrMT.vcf'"
					else
						echo "Warning: VCF file not found for '$chrom_id' (checked for *.chr${chrom_id}.vcf and *.chrMT.vcf)"
					fi
				else
					echo "Warning: VCF file not found for '$chrom_id' (checked for *.chr${chrom_id}.vcf)"
				fi
			fi
		done
	fi

	echo ""
	echo "Found ${#VCF_FILES_TO_MERGE[@]} VCF files to merge."

	if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then
		echo " Error: No VCF files were found."
		return 1 # Failure
	fi

	echo "FILES: ${VCF_FILES_TO_MERGE[@]}"
	return 0 # Success
}

### Finalize and Merge Functions

merge_vcf_files() {
	local final_vcf_file="$1"

	echo ""
	echo "--- Merging Per-Chromosome VCFs ---"
	echo "Output file: $final_vcf_file"

	# Remove old file if it exists
	rm -f "$final_vcf_file" 2>/dev/null || true

	# Concatenate all found VCFs
	for vcf_file in "${VCF_FILES_TO_MERGE[@]}"; do
		cat "$vcf_file" >>"$final_vcf_file"
	done

	echo "Merging complete."
	ls -lh "$final_vcf_file"
}

# --- Main ---

main() {
	echo ""
	echo "=========== VCF MERGING SCRIPT ==========="
	echo ""

	# Run setup
	setup_environment

	# Find which VCFs to process based on CLI args
	if ! find_vcfs_to_merge "$@"; then
		# The function returned 1 (false) if no VCFs were found
		echo "Exiting."
		exit 1
	fi

	# --- Generate Output Filename ---
	local FINAL_VCF_FILE
	local integer_regex='^[0-9]+$'
	local START_CHROM="$1"
	local END_CHROM="$2"

	if [ "$#" -eq 0 ]; then
		# No arguments: all chromosomes
		FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}_all_chromosomes.merged.vcf"
	elif [ "$#" -eq 2 ] && [[ "$START_CHROM" =~ $integer_regex ]] && [[ "$END_CHROM" =~ $integer_regex ]]; then
		# Numeric range
		FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}_chroms_${START_CHROM}_to_${END_CHROM}.merged.vcf"
	else
		# A list of arguments
		local list_name=$(echo "$@" | tr ' ' '_') # Create a name like "1_X_M"
		FINAL_VCF_FILE="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}_chroms_list_${list_name}.merged.vcf"
	fi

	# Run the merge
	merge_vcf_files "$FINAL_VCF_FILE"

	echo ""
	echo "=========== MERGING COMPLETE ==========="
	echo ""
}

# Pass all command-line arguments to the main function
main "$@"
