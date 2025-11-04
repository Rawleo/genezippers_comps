#!/bin/bash

# This script reformats a VCF-like file to a specific CSV format.
# It assigns a flag and normalizes indel representation:
# 0 = SNP/substitution (e.g., A/G)
# 1 = Deletion (e.g., CACACG/------)
# 2 = Insertion (e.g., --/AT)
# The final output is sorted by flag, then chromosome, then position.

# --- Script Start ---

# Check if an input file was provided.
if [ -z "$1" ]; then
    # If no file is provided, print a usage message to standard error.
    echo "Usage: $0 <input_file>" >&2
    exit 1
fi

# 1. Use awk to process the file and generate the formatted output.
# 2. Pipe (|) the output of awk directly into the multi-level sort command.
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
    
    # --- Advanced Indel Logic ---
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
' "$1" | sort -t ',' -k 1,1n -k 2,2V -k 3,3n

# --- Script End ---