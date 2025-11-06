# Genome Comparison Scripts

The core workflow uses [**MUMmer4**](https://github.com/mummer4/mummer) for alignment and [**all2vcf**](https://github.com/MatteoSchiavinato/all2vcf) for converting results to a pseudo-VCF format.

## Directory Tree

```text
alignment/
├── code/
│   ├── create_vcf.sh
│   ├── format_to_vcf.sh
│   ├── merge_vcf.sh
│   └── rename_chr.sh
│
├── files/
│   ├── genomes/
│   │   ├── ash1_v2.2/
│   │   │   ├── chr1.fasta
│   │   │   └── ... (other fastas)
│   │   ├── hg38/
│   │   │   ├── chr1.fa
│   │   │   ├── chr2.fa
│   │   │   └── ... (other fastas)
│   │   ├── PAN027/
│   │   │   ├── chr1.fasta
│   │   │   └── ... (other fastas)
│   │   └── T2T-CHM13/
│   │       ├── chr1.fasta
│   │       └── ... (other fastas)
│   │
│   ├── output_ash1_v2.2/
│   │   ├── hg38_ash1_genome.vcf
│   │   └── ... (other output files)
│   │
│   ├── output_PAN027/
│   │   ├── logs/
│   │   │   ├── chr21.log
│   │   │   └── chr22.log
│   │   │
│   │   ├── hg38_pan027_genome.vcf
│   │   ├── hg38_vs_PAN027.chr21.delta
│   │   ├── hg38_vs_PAN027.chr21.filtered.delta
│   │   ├── hg38_vs_PAN027.chr21.snps
│   │   ├── hg38_vs_PAN027.chr21.vcf
│   │   ├── hg38_vs_PAN027.chr22.delta
│   │   ├── hg38_vs_PAN027.chr22.filtered.delta
│   │   ├── hg38_vs_PAN027.chr22.snps
│   │   ├── hg38_vs_PAN027.chr22.vcf
│   │   └── ... (other output files)
│   │
│   └── output_T2T-CHM13/
│       └── ... (output files for T2T)
│
├── tools/
│   ├── all2vcf/
│   │   └── all2vcf
│   └── mummer/
│       └── bin/
│           ├── delta-filter
│           ├── nucmer
│           └── show-snps
│
├── Alignment.md
└── requirements.txt
```

## Data Source

```markdown
# Note: Genome Download Source

The genome assemblies (hg38, PAN027, ash1_v2.2, T2T-CHM13) used in this project were downloaded from the NCBI (National Center for Biotechnology Information) database.
```

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