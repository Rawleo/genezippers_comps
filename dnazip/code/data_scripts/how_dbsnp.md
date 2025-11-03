# Script: Download dbSNP Chromosomes

This document contains a bash script designed to extract SNP data for individual chromosomes from a UCSC `bigBed` file (e.g., `dbSnp155Common.bb`).

The script iterates through a predefined list of human chromosomes, running the `bigBedToBed` utility for each one and saving the output to a separate text file named after the chromosome (e.g., `chr1.txt`).

## Prerequisites

1.  **`bigBedToBed` Utility**: You must have the [UCSC Kent command-line utilities](http://hgdownload.soe.ucsc.edu/admin/exe/) installed. The `bigBedToBed` executable needs to be in your system's PATH.
2.  **Input File**: The source `bigBed` file (`dbSnp155Common.bb` by default), [UCSC downloads page](https://hgdownload.soe.ucsc.edu/gbdb/hg38/snp/) must be located in the same directory where the script is run. If it is not, the bash script will automatically download it.

## How to Use

1.  Find the script named `create_db_snps.sh`.
2.  Place your `.bb` file in the same directory.
3.  Make the script executable by running this command in your terminal:
    ```
    chmod +x create_db_snps.sh
    ```
4.  Execute the script:
    ```
    ./create_db_snps.sh
    ```