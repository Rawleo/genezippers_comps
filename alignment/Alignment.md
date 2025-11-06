# Genome Comparison Scripts

The core workflow uses [**MUMmer4**](https://github.com/mummer4/mummer) for alignment and [**all2vcf**](https://github.com/MatteoSchiavinato/all2vcf) for converting results to a pseudo-VCF format.

## Tools Used

This suite of scripts relies on several command-line bioinformatics and utility tools:

* [**MUMmer4**](https://github.com/mummer4/mummer): A system for rapidly aligning entire genomes.
* [**all2vcf**](https://github.com/MatteoSchiavinato/all2vcf): A tool to convert various alignment formats to VCF.
* [**Git**](https://git-scm.com/): A version control system used to download `all2vcf`.
* [**Python 3**](https://www.python.org/): The programming language required to run `all2vcf`.
* **Standard Utilities**:
  * [**wget**](https://www.gnu.org/software/wget/)
  * [**tar**](https://www.gnu.org/software/tar/)
  * [**gunzip**](https://www.gnu.org/software/gzip/)
  * [**awk**](https://www.gnu.org/software/gawk/)

-----

## 1\. `create_vcf.sh`

This is the first script for aligning reference to target genomes by a chromosome-by-chromosome.

* **Purpose**:
  * **Reference vs. Target**: The script is configured to allow comparison between reference and target genomes.
* **Usage**:
  * **Genomes**: Requires a chromosome-by-chromosome break down of each genome.

    ```bash
    ./create_vcf.sh [Start Chrom] [End Chrom]
    ```

* **Examples**:
  * **Compare all standard chromosomes**:

    ```bash
    ./create_vcf.sh
    ```

  * **Compare a specific range (chromosomes 20 to 22)**:

    ```bash
    ./create_vcf.sh 20 22
    ```

  * **Compare a list of chromosomes**:

    ```bash
    ./create_vcf.sh X Y 20
    ```

* **Output**: A merged VCF file named `files/output_TARGET/hg38_vs_TARGET_START_END.merged.vcf`.

-----

## 2\. `merge_vcf.sh`

This is merges several VCF files in one directory into one large file. Useful for final formatting.

-----

## 3\. `format_vcf.sh`

Transforms psuedo-vcf into a formatted text file for use by our DNAZip implementation.