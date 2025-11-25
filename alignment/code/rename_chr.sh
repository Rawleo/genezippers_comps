# Code to help rename the beginning of chr fasta files.
# Does so by editing the characters inbetween the / /
# Copy & paste into the terminal after the appropriate
# changes have been made.

for file in *chr*; do
	mv "$file" "${file/* /}"
done
