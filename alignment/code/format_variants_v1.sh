#!/bin/bash

# This script reformats a VCF-like file to a specific CSV format.
# It assigns a flag based on the variant type:
# 0 = SNP/substitution
# 1 = Deletion
# 2 = Insertion
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
# BEGIN block runs once before processing any lines.
BEGIN {
    # Set the Output Field Separator to a comma.
    OFS=","
}

# This main block runs for every line in the input file.
# It skips any lines that start with a "#" (header lines).
!/^#/ {
    # Default flag is 0 for SNPs.
    flag = 0

    # Check for Deletion (REF is longer than ALT).
    if (length($4) > length($5)) {
        flag = 1
    }
    # Check for Insertion (REF is shorter than ALT).
    else if (length($4) < length($5)) {
        flag = 2
    }

    # Print the transformed columns.
    # We no longer add "chr" since the input column ($1) already has it.
    print flag, $1, $2, $4"/"$5
}
' "$1" | sort -t ',' -k 1,1n -k 2,2V -k 3,3n

# --- Script End ---