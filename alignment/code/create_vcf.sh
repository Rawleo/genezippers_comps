#!/bin/bash
#
# Compare genomes chromosome-by-chromosome and create psuedo-VCFs.
#
# Usage (all chroms): ./create_vcf.sh
# Usage (range):      ./create_vcf.sh 1 5
# Usage (list):       ./create_vcf.sh 1 X M

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Global Configuration ---

# Genome assemblies
REF_CODENAME="hg38"
TARGET_CODENAME="T2T-CHM13"

# Directories
GENOME_DIR="../files/genomes"
REF_CHROM_DIR="$GENOME_DIR/$REF_CODENAME"
TARGET_CHROM_DIR="$GENOME_DIR/$TARGET_CODENAME"
OUTPUT_DIR="../files/output_${TARGET_CODENAME}"
FINAL_FORMATTED_VCF="${OUTPUT_DIR}/${REF_CODENAME}_${TARGET_CODENAME}_sorted_variants.txt"

# Parallel processing settings
MAX_JOBS=8
LOG_DIR="$OUTPUT_DIR/logs"

### Tool Pathing if in Path
# COMMANDS=("wget" "gunzip" "git" "python3" "nucmer" "delta-filter" "show-snps")

### Tool Pathing if Local
COMMANDS=("wget" "gunzip" "git" "python3" "../tools/mummer/bin/nucmer" "../tools/mummer/bin/delta-filter" "../tools/mummer/bin/show-snps")

# Global arrays
declare -a files_to_process
declare -a chromosome_ids_to_process
declare -a VCF_FILES_TO_MERGE

# --- Function Definitions ---

setup_environment() {
	echo "Setting up directory structure..."
	mkdir -p "$GENOME_DIR" "$OUTPUT_DIR" "$LOG_DIR"
	echo "Done."
	echo ""
}

check_dependencies() {
	echo "Checking for required dependencies..."
	for cmd in "${COMMANDS[@]}"; do
		if ! command -v "$cmd" &>/dev/null; then
			echo "Error: Required command '$cmd' is not installed or not in your PATH."
			exit 1
		fi
	done
	echo "All dependencies found."
	echo ""
}

### File List Generation Functions

populate_chromosome_lists() {
	echo "--- Locating Chromosome Files ---"

	# Regex to check if a string is a non-negative integer
	local integer_regex='^[0-9]+$'
	local start_chrom="$1"
	local end_chrom="$2"

	if [ "$#" -eq 0 ]; then
		# No arguments provided, process all chromosomes
		echo "No specific chromosomes given, processing all..."
		local all_files=($(find "$REF_CHROM_DIR" -maxdepth 1 -name "chr*.fa" | sort -V))
		for f in "${all_files[@]}"; do
			files_to_process+=("$f")
			# Get '1' from '.../chr1.fa', or 'X' from '.../chrX.fa'
			local chrom_id=$(basename "$f" .fa | sed 's/^chr//')
			chromosome_ids_to_process+=("$chrom_id")
		done

	elif [ "$#" -eq 2 ] && [[ "$start_chrom" =~ $integer_regex ]] && [[ "$end_chrom" =~ $integer_regex ]]; then
		# Two numeric arguments: process as a range
		echo "Processing chromosome range: $start_chrom to $end_chrom"
		for chrom_id in $(seq "$start_chrom" "$end_chrom"); do
			local found_file="$REF_CHROM_DIR/chr${chrom_id}.fa"
			if [ -f "$found_file" ]; then
				files_to_process+=("$found_file")
				chromosome_ids_to_process+=("$chrom_id") # Add ID to list
			else
				echo "Warning: Chromosome file not found for '$chrom_id' (looked for $found_file)"
			fi
		done

	else
		# One or more arguments (e.g., "1", "X", "M", or "1 X"): process as a list
		echo "Looking for specific chromosomes: $@"
		for chrom_id in "$@"; do
			local found_file="$REF_CHROM_DIR/chr${chrom_id}.fa"

			if [ -f "$found_file" ]; then
				files_to_process+=("$found_file")
				chromosome_ids_to_process+=("$chrom_id") # Add ID to list
			else
				# Handle common M -> MT mapping
				if [[ "$chrom_id" == "M" || "$chrom_id" == "m" ]]; then
					local found_file_mt="$REF_CHROM_DIR/chrMT.fa"
					if [ -f "$found_file_mt" ]; then
						files_to_process+=("$found_file_mt")
						chromosome_ids_to_process+=("MT") # Add 'MT' ID to list
						echo "Note: Mapping input 'M' to 'chrMT.fa'"
					else
						echo "Warning: Chromosome file not found for '$chrom_id' (checked $found_file and $found_file_mt)"
					fi
				else
					echo "Warning: Chromosome file not found for '$chrom_id' (looked for $found_file)"
				fi
			fi
		done
	fi

	local TOTAL_FILES=${#files_to_process[@]}
	echo "Found $TOTAL_FILES chromosomes to process."
	echo "FILES: ${files_to_process[@]}"
	echo ""
}

find_output_vcfs() {
	echo "--- Locating VCF Files for Merging ---"

	if [ "$#" -eq 0 ]; then
		# No script arguments were provided, so we processed all. Merge all found VCFs.
		echo "Merging all found VCFs..."
		VCF_FILES_TO_MERGE=($(ls -v "$OUTPUT_DIR"/*.chr*.vcf 2>/dev/null || true))
	else
		# Arguments were provided, so we use our processed list
		echo "Merging VCFs for processed IDs: ${chromosome_ids_to_process[@]}"
		for chrom_id in "${chromosome_ids_to_process[@]}"; do
			# Find VCF files matching the chromosome ID, e.g., *.chrX.vcf
			local found_files_list=($(find "$OUTPUT_DIR" -maxdepth 1 -type f -name "*.chr${chrom_id}.vcf" 2>/dev/null || true))

			if [ ${#found_files_list[@]} -gt 0 ]; then
				VCF_FILES_TO_MERGE+=("${found_files_list[@]}")
			else
				echo "Warning: VCF file not found for processed ID '$chrom_id' (checked for *.chr${chrom_id}.vcf)"
			fi
		done
	fi

	echo "Found ${#VCF_FILES_TO_MERGE[@]} VCF files to merge."
	if [ ${#VCF_FILES_TO_MERGE[@]} -eq 0 ]; then
		echo " Error: No VCF files were generated or found."
		return 1 # Return failure
	fi
	return 0 # Return success
}

### Core Processing Functions

# This function defines all the work for a single chromosome
process_chromosome() {
	# exit if any command fails.

	set -e

	local ref_chrom_file="$1"
	local CHROM_BASENAME=$(basename "$ref_chrom_file" .fa)

	# Define all file paths
	local target_chrom_file="$TARGET_CHROM_DIR/${CHROM_BASENAME}.fasta"
	local PREFIX="$OUTPUT_DIR/${REF_CODENAME}_vs_${TARGET_CODENAME}.${CHROM_BASENAME}"

	# Skip if the target file doesn't exist
	if [ ! -f "$target_chrom_file" ]; then
		echo "Skipping ${CHROM_BASENAME}: Target file $target_chrom_file not found."
		return 0 # Exit function successfully
	fi

	echo "STARTING: $CHROM_BASENAME (Target: $target_chrom_file)"

	# Tool Pathing if installed in $PATH.
	# nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file" &>/dev/null
	# delta-filter -1 "${PREFIX}.delta" >"${PREFIX}.filtered.delta" 2>/dev/null
	# show-snps -H -T "${PREFIX}.filtered.delta" >"${PREFIX}.snps" 2>/dev/null
	# python3 all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" >"${PREFIX}.vcf" 2>/dev/null

	# Tool Pathing if locally installed.
	./../tools/mummer/bin/nucmer -p "$PREFIX" "$ref_chrom_file" "$target_chrom_file"
	./../tools/mummer/bin/delta-filter -1 "${PREFIX}.delta" >"${PREFIX}.filtered.delta"
	./../tools/mummer/bin/show-snps -H -T "${PREFIX}.filtered.delta" >"${PREFIX}.snps"
	python3 ../tools/all2vcf/all2vcf mummer --snps "${PREFIX}.snps" --reference "$ref_chrom_file" >"${PREFIX}.vcf"

	echo "COMPLETED: $CHROM_BASENAME"
}

run_parallel_processing() {
	echo "--- Running Per-Chromosome Comparison ---"
	echo "Processing up to $MAX_JOBS chromosomes in parallel..."
	echo "Individual job logs will be written to $LOG_DIR"
	echo ""

	# Export the function so subshells launched with '&' can see it
	export -f process_chromosome
	# Export supporting variables needed by the sub-shell
	export TARGET_CHROM_DIR OUTPUT_DIR REF_CODENAME TARGET_CODENAME

	local job_count=0
	for ref_chrom_file in "${files_to_process[@]}"; do
		local CHROM_BASENAME=$(basename "$ref_chrom_file" .fa)
		local LOG_FILE="$LOG_DIR/${CHROM_BASENAME}.log"

		# Launch the job in the background, redirecting ALL output (stdout and stderr)
		# to its own dedicated log file.
		process_chromosome "$ref_chrom_file" &>"$LOG_FILE" &

		# Increment job counter
		job_count=$((job_count + 1))

		# If we've hit the max, wait for *one* job to finish
		# before launching the next one.
		if [ "$job_count" -ge "$MAX_JOBS" ]; then
			wait -n # Waits for the next job to exit
			job_count=$((job_count - 1))
		fi
	done

	# Wait for all remaining background jobs to finish
	echo "Waiting for all remaining jobs to complete..."
	wait
	echo "All jobs finished."
	echo ""
}

### Finalize and Format Functions

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
            
            # Check if the insertion string contains a comma (e.g., "C,T" or "G,C")
            if (index(alt_change, ",")) {
                
                # 1. Yes, comma found. Split the string into an array.
                #    "G,C" becomes items[1]="G", items[2]="C"
                n = split(alt_change, items, ",")
                
                # 2. Loop through each item in the array
                for (i = 1; i <= n; i++) {
                    current_alt = items[i]
                    
                    # 3. Create dashes based on the length of *this specific item*
                    current_ref = repeat("-", length(current_alt))
                    
                    # 4. Print the line for this item
                    print flag, $1, $2, current_ref"/"current_alt
                }
                
                # 5. Skip the default print statement at the end of the script block
                next 
            } 
            else {
                # No comma found, proceed as normal
                ref_out = repeat("-", length(alt_change))
                alt_out = alt_change
            }
        }
    }

    # Print the final, formatted line (only for SNPs, Deletions, and non-split Insertions)
    print flag, $1, $2, ref_out"/"alt_out
}
' "$1" | sort -t ',' -k 1,1n -k 2,2V -k 3,3n >$2

	echo "Formatting complete."
	ls -lh "$2"
}

merge_and_finalize() {
	# This entire section was commented out in the original script.
	# It is preserved here for future use.

	# echo "Use merge_vcf.sh to merge the processed files together."

	# --- Cleaning Used Files ---
	# echo "Cleaning up intermediate files..."
	# rm -f "$OUTPUT_DIR"/${REF_CODENAME}_vs_${TARGET_CODENAME}.chr*.{delta,filtered.delta,snps,vcf}
	# echo " Cleanup complete."
	# echo ""

	# --- Merging ---
	echo ""
	echo "--- Merging Per-Chromosome VCFs ---"

	# Need to get args again to build name
	local START_CHROM="$1"
	local END_CHROM="$2"

	local MERGED_VCF_NAME="${REF_CODENAME}_vs_${TARGET_CODENAME}"
	if [ -n "$START_CHROM" ]; then
		if [ "$START_CHROM" == "$END_CHROM" ]; then
			MERGED_VCF_NAME+="_chrom_${START_CHROM}"
		else
			MERGED_VCF_NAME+="_chroms_${START_CHROM}_to_${END_CHROM}"
		fi
	else
		MERGED_VCF_NAME+="_all_chroms"
	fi

	local FINAL_VCF_FILE="$OUTPUT_DIR/${MERGED_VCF_NAME}.merged.vcf"

	rm -f "$FINAL_VCF_FILE" 2>/dev/null || true
	for vcf_file in "${VCF_FILES_TO_MERGE[@]}"; do
		cat "$vcf_file" >>"$FINAL_VCF_FILE"
	done

	echo "Success! The final merged pseudo-VCF file is located at:"
	ls -lh "$FINAL_VCF_FILE"
	echo ""

	# --- Output ---
	echo " --- Creating Final Formatted File --- "
	format_to_vcf "$FINAL_VCF_FILE" "$FINAL_FORMATTED_VCF"
}

# --- Main Execution ---

main() {
	# Print header
	echo ""
	echo "=========== CHROMOSOME COMPARISON ==========="
	echo ""
	echo "Starting comparison: $REF_CODENAME vs $TARGET_CODENAME..."
	if [ "$#" -gt 0 ]; then
		echo "Range/List: $@"
	fi
	echo ""

	# Run setup and checks
	setup_environment
	check_dependencies

	# Find which chromosomes to process based on CLI args
	populate_chromosome_lists "$@"

	# Exit if no files were found to process
	if [ ${#files_to_process[@]} -eq 0 ]; then
		echo "Error: No chromosome files found to process. Exiting."
		exit 1
	fi

	# Activate Python Environment (if necessary).
	# source all2vcf/all_to_vcf/bin/activate

	# Run the core alignment and VCF generation in parallel
	# run_parallel_processing

	# Deactivate Python Environment (if necessary).
	# deactivate

	# Find the output files that were just created
	if ! find_output_vcfs "$@"; then
		# The function returned 1 (false) if no VCFs were found
		echo "Exiting due to no VCF files found."
		exit 1
	fi

	# We pass $1 and $2 for the file naming logic inside
	merge_and_finalize "$1" "$2"

	echo ""
	echo "=========== END CHROMOSOME COMPARISON ==========="
	echo ""
}

# Pass all command-line arguments to the main function
main "$@"
