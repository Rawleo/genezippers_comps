# Code to help reformate the beginning of chr fasta files.
# Edit the characters inbetween the / /

for file in *chr*; do
    mv "$file" "${file/CM*_/}"
done