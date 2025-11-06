#!/bin/bash
#
# Format the any psuedo-vcf into the DNAZip sorted format.
#
# Usage: ./format_variants.sh <input_file> <output_file>

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Function Definitions ---

### Core Formatting Function

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

# --- Main ---

main() {
	echo ""
	echo "=========== VARIANT FORMATTER ==========="
	echo ""

	# --- Argument Validation ---
	if [ "$#" -ne 2 ]; then
		echo "Error: Invalid number of arguments."
		echo "Usage: $0 <input_file> <output_file>"
		exit 1
	fi

	local input_file="$1"
	local output_file="$2"
	local output_dir=$(dirname "$output_file")

	if [ ! -f "$input_file" ] || [ ! -r "$input_file" ]; then
		echo "Error: Input file '$input_file' not found or is not readable."
		exit 1
	fi

	if [ ! -d "$output_dir" ] || [ ! -w "$output_dir" ]; then
		echo "Error: Output directory '$output_dir' does not exist or is not writable."
		exit 1
	fi

	# --- Run Formatter ---
	format_to_vcf "$input_file" "$output_file"

	echo ""
	echo "=========== FORMATTING COMPLETE ==========="
	echo ""
}

# Pass all command-line arguments to the main function
main "$@"
