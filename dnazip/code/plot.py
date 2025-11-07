from constants import *
from metrics import *
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def compression_comparison(original_file_path, bin_file_path, file_name, output_file_path):
    '''
    Creates bar chart comparing compressed file size vs. raw file size

    @params:
    * original_file_path: file path of uncompressed file
    * bin_file_path: file path of binary compressed file
    * file_name: name of file getting compared
    * output_file_path: file path where figure should be output
    '''
    # Get sizes of files
    original_size = file_size(original_file_path)
    bin_size = file_size(bin_file_path)

    # Get metrics
    comp_ratio = compression_ratio(original_file_path, bin_file_path)
    space_savings = space_saving(original_file_path, bin_file_path)

    # Make figure
    plt.figure(figsize=(7, 7))
    plt.bar(['Compressed File', 'Raw File'],
            height=[bin_size, original_size],
            width=0.7,
            color=['#004D40', '#D81B60'],
            edgecolor='black',
            linewidth=3
    )

    # Formattting
    plt.suptitle(f"Megabytes Used Per File Type ({file_name})", weight='bold', fontsize=16, linespacing=400)
    plt.title(f"Compression Ratio: {comp_ratio} | Space Savings: {space_savings}", pad=20, fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("File Type", fontsize=14, labelpad=10)
    plt.ylabel("File Size (MB)", fontsize=14, labelpad=15)
    plt.tight_layout()

    # Save file to output file path
    plt.savefig(output_file_path, dpi=600)


def clustered_compression_compare(input_file_paths, enc_file_paths, algorithm_name, output_file_path):
    '''
    Creates clustered bar charts to visualize compression comparison across multiple files

    @params:
    * input_file_paths: list of file paths of uncompressed files
    * enc_file_paths: list of file paths of binary compressed files
    * algorithm_name: name of algorithm (biocompressq or DNAZip)
    * output_file_path: file path where figure should be output
    '''

    input_file_sizes = []
    enc_file_sizes = []
    file_names = []
    number_of_files = len(input_file_paths)

    # Get metrics
    for i in range(number_of_files):

        input_size = file_size(input_file_paths[i])
        input_file_sizes.append(input_size)

        bin_size = file_size(enc_file_paths[i])
        enc_file_sizes.append(bin_size)

        file_name = input_file_paths[i].split('/')[-1]
        file_names.append(file_name.split('.')[0])

    # Make figure
    plt.figure(figsize=(10, 6))
    
    # Formatting
    x = x = np.arange(number_of_files)
    plt.bar(x-0.1, enc_file_sizes, color='#1E88E5', width=0.2, edgecolor='black', linewidth=2)
    plt.bar(x+0.1, input_file_sizes, color='#D81B60', width=0.2, edgecolor='black', linewidth=2)
    plt.xticks(x, file_names)
    plt.title(f"Comparison of File Sizes Across Chromosomes ({algorithm_name})", pad=20, fontsize=14)
    plt.xlabel("Chromosome (1/4th)", fontsize=14, labelpad=10)
    plt.ylabel("Size (MB)", fontsize=14, labelpad=15)
    plt.legend(['Encoded File', 'Raw File'])
    plt.tight_layout()

    # Save file to output file path
    plt.savefig(output_file_path, dpi=600)


def time_scale_comparison(genome_file_paths, huffman_bin_paths, biocomp_bin_paths, var_file_paths, dnazip_bin_paths, output_file_path, x_range):

    num_files = len(genome_file_paths)

    # Initialize totals
    tot_original_sizes = 0
    tot_huffman_sizes = 0
    tot_biocomp_sizes = 0
    tot_var_sizes = 0
    tot_dnazip_sizes = 0

    # Accumulate sizes
    for i in range(num_files):
        tot_original_sizes += file_size(genome_file_paths[i])
        tot_huffman_sizes += file_size(huffman_bin_paths[i])
        tot_biocomp_sizes += file_size(biocomp_bin_paths[i])
        tot_var_sizes += file_size(var_file_paths[i])
        tot_dnazip_sizes += file_size(dnazip_bin_paths[i])

    # Compute averages
    avg_original_sizes = tot_original_sizes / num_files
    avg_huffman_sizes = tot_huffman_sizes / num_files
    avg_biocomp_sizes = tot_biocomp_sizes / num_files
    avg_var_sizes = tot_var_sizes / num_files
    avg_dnazip_sizes = tot_dnazip_sizes / num_files

    # X values (genome counts)
    x = np.array(x_range)

    # Approximate scaling constants (in MB or GB)
    gzip_genome_size = 20
    gzip_var_size = 10
    gzip_dbsnp_size = 5
    dnazip_enc_size = 1

    # # Compute scaling functions
    # f_genomes = x * gzip_genome_size
    # f_vars = (x * gzip_var_size) + gzip_genome_size
    # f_dnazip = (x * dnazip_enc_size) + gzip_genome_size + gzip_dbsnp_size
    # f_dnazip_nodbsnp = (x * dnazip_enc_size) + gzip_genome_size

    f_huffman = x * avg_huffman_sizes
    f_biocomp1 = x * avg_biocomp_sizes
    f_var = (x * avg_var_sizes) + avg_original_sizes
    f_dnazip = (x * avg_dnazip_sizes) + avg_original_sizes

    # Create figure
    plt.figure(figsize=(10, 6))

    # Plot each algorithm’s scaling curve
    plt.plot(x, f_huffman, color='#D81B60', linewidth=2.5, marker='o', label='Huffman')
    # plt.fill_between(x, 0, f_huffman, color='#D81B60', alpha=0.1)

    plt.plot(x, f_biocomp1, color='#1E88E5', linewidth=2.5, marker='s', label='Biocompress 1')
    # plt.fill_between(x, 0, f_biocomp1, color='#1E88E5', alpha=0.1)

    plt.plot(x, f_var, color='#004D40', linewidth=2.5, marker='D', label='VCF')
    # plt.fill_between(x, 0, f_var, color='#004D40', alpha=0.1)

    plt.plot(x, f_dnazip, color='#FFC107', linewidth=2.5, marker='P', label='DNAZip')
    plt.fill_between(x, 0, f_dnazip, color='#FFC107', alpha=0.2)

    # Formatting
    plt.xlabel('Number of Genomes', fontsize=14, weight='bold', labelpad=10)
    plt.ylabel('Storage Requirements (MB)', fontsize=14, weight='bold')
    plt.title('Scaling of Storage Requirements Across Compression Methods', fontsize=16, pad=15, weight='bold')
    plt.xticks(x_range[::5], fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()

    # Save and show
    plt.savefig(output_file_path, dpi=600)
    plt.show()


def all_compression_comparisons(genome_file_paths, huffman_bin_paths, biocomp_bin_paths, var_file_paths, dnazip_bin_paths, output_file_path):
    '''
    Creates bar chart comparing:
    * original genome
    * huffman compression
    * biocompress output
    * variants (vcf) file
    * dnazip output

    @params:
    * genome_file_path: 
    * huffman_bin_path:
    * biocomp_bin_path:
    * var_file_path:
    * dnazip_bin_path:
    '''
    #Get number of genomces compared
    num_files = len(genome_file_paths)

    # Get sizes of files
    original_sizes = []
    huffman_sizes = []
    biocomp_sizes = []
    var_sizes = []
    dnazip_sizes = []

    for i in range(num_files):

        original_sizes.append(round(file_size(genome_file_paths[i]), 2))
        huffman_sizes.append(file_size(huffman_bin_paths[i]))
        biocomp_sizes.append(file_size(biocomp_bin_paths[i]))
        var_sizes.append(file_size(var_file_paths[i]))
        dnazip_sizes.append(file_size(dnazip_bin_paths[i]))

    
    labels = ['DNAZip', 'VCF', 'Biocompress 1', 'Huffman']
    colors = ['#FFC107', '#004D40', '#1E88E5', '#D81B60']

    # Make figure
    plt.figure(figsize=(15, 7))
    
    # Formatting
    x = x = np.arange(num_files)
    plt.bar(x-0.3, dnazip_sizes, color='#FFC107', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x-0.1, var_sizes, color='#004D40', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x+0.1, biocomp_sizes, color='#1E88E5', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x+0.3, huffman_sizes, color='#D81B60', width=0.2, edgecolor='black', linewidth=1)

    # plt.title(f"Comparison of File Sizes Across Chromosomes ({algorithm_name})", pad=20, fontsize=14)
    
    plt.xticks(x, [f'PAN027_Mat_V1 \n Original Size: {original_sizes[0]} MB', 
                   f'T2T_CHM13_V2 \n Original Size: {original_sizes[1]} MB', 
                   f'Han1 \n Original Size: {original_sizes[2]} MB'], fontsize=14)
    plt.ylabel("Size (MB)", fontsize=18, labelpad=15, weight='bold')
    plt.xlabel("Genomes", fontsize=18, labelpad=15, weight='bold')
    plt.legend(labels, fontsize=14, loc='upper center', ncols=4, bbox_to_anchor=(0.5, 1.12))

    plt.tight_layout()
    plt.show()
    plt.savefig(output_file_path, dpi=800)

def main():

    genome_file_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/PAN027_mat_v1.0/PAN027_mat_v1_Genome.txt',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/T2T-CHM13v2.0/T2T-CHM13v2_Genome.txt',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/Han1/Han1_Genome.txt']

    huffman_bin_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/huffman_coding/output/ENCODED_PAN027_mat_v1_Genome_K_MER_8.bin',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/huffman_coding/output/ENCODED_T2T-CHM13v2_Genome_K_MER_8.bin',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/huffman_coding/output/ENCODED_Han1_Genome_K_MER_8.bin']

    biocomp_bin_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/biocompress_1/data/PAN027_mat_v1_Genome_13.bin',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/biocompress_1/data/T2T-CHM13v2_Genome_13.bin',
                         '/Accounts/saxerg/genezippers/comps_f25_rgj/biocompress_1/data/Han1_Genome_13.bin']
    
    var_file_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/variants/hg38_pan027_genome_sorted_variants.txt',
                      '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/variants/hg38_T2T-CHM13_genome_sorted_variants.txt',
                      '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/variants/hg38_Han1_genome_sorted_variants.txt']

    dnazip_bin_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/pan027_VINT_True_False_Encoded.bin',
                        '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/T2T-_CHM13_VINT_True_False_Encoded.bin',
                        '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/Han1_VINT_True_False_Encoded.bin']

    all_compression_comparisons(genome_file_paths, 
                                huffman_bin_paths, 
                                biocomp_bin_paths, 
                                var_file_paths, 
                                dnazip_bin_paths, 
                                '/Accounts/arroyoruizj/comps_f25_rgj/figures/algorithm_comp.png')

    time_scale_comparison(genome_file_paths, 
                          huffman_bin_paths, 
                          biocomp_bin_paths, 
                          var_file_paths, 
                          dnazip_bin_paths, 
                          '/Accounts/arroyoruizj/comps_f25_rgj/figures/time_v_storage.png',
                          [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

main()
