from constants import *
from metrics import *
import matplotlib.pyplot as plt
import numpy as np

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
    # num_files = len(genome_file_paths)
    num_files = 1

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

    
    labels = ['Huffman', 'Biocompress 1', 'VCF', 'DNAZip']
    colors = ['#b52a8fff', '#1E88E5', '#004D40', '#FFC107']

    # Make figure
    plt.figure(figsize=(7, 4))
    
    # Formatting
    x = x = np.arange(num_files)

    plt.bar(x-3, huffman_sizes, color='#b52a8fff', width=1.25, edgecolor='black', linewidth=2)
    plt.bar(x-1, biocomp_sizes, color='#1E88E5', width=1.25, edgecolor='black', linewidth=2)
    plt.bar(x+1, var_sizes, color='#004D40', width=1.25, edgecolor='black', linewidth=2)
    plt.bar(x+3, dnazip_sizes, color='#FFC107', width=1.25, edgecolor='black', linewidth=2)
    
    
   

    # plt.title(f"Comparison of File Sizes Across Chromosomes ({algorithm_name})", pad=20, fontsize=14)
    
    # plt.xticks(x, [f'PAN027_Mat_V1 \n Original Size: {original_sizes[0]} MB', 
    #                f'T2T_CHM13_V2 \n Original Size: {original_sizes[1]} MB', 
    #                f'Han1 \n Original Size: {original_sizes[2]} MB'], fontsize=14)

    plt.suptitle('Compressed File Size for Various Methods', fontsize=16, weight='bold', y=0.98)
    plt.title(f'Genome File: PAN027_Mat_V1 | Original Size: {original_sizes[0]} MB', fontsize=13)


    plt.ylabel("Size (MB)", fontsize=16, labelpad=15, weight='bold')
    plt.legend(labels, fontsize=12, loc='upper right')
    plt.xticks([])

    plt.tight_layout()
    plt.show()
    plt.savefig(output_file_path, dpi=800)

def compare_ash_triplets(file_paths, output_file_path):

    vint_size = file_size(file_paths[0])
    vint_delta_dbsnp_size = file_size(file_paths[1])
    vint_delta_size = file_size(file_paths[2])

    labels = ['VINT', 'VINT + DELTA + dbSNP', 'VINT + DELTA']
    colors = ['#ffe79e', '#ffd75e', '#FFC107']

    plt.figure(figsize=(7, 4))
    bars = plt.bar(labels,
            [vint_size, vint_delta_dbsnp_size, vint_delta_size],
            color = colors,
            edgecolor='black',
            linewidth=2,
            width=.6)

    plt.xticks([])
    plt.ylabel("Compressed File Size (MB)", weight='bold', fontsize=14)
    # plt.xlabel("DNAZip Variant", weight='bold', fontsize=14)
    plt.title("Compressed File Sizes for DNAZip Variants", weight='bold', fontsize=16)

    plt.legend(bars, labels, 
               loc='upper right', 
               title='DNAZip Variants')

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

    ash_bin_paths = ['/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/ash1_VINT_False_False_Encoded.bin',
                     '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/ash1_VINT_True_True_Encoded.bin',
                     '/Accounts/saxerg/genezippers/comps_f25_rgj/dnazip/data/output/ash1_VINT_True_False_Encoded.bin']

    all_compression_comparisons(genome_file_paths, 
                                huffman_bin_paths, 
                                biocomp_bin_paths, 
                                var_file_paths, 
                                dnazip_bin_paths, 
                                '/Accounts/arroyoruizj/comps_f25_rgj/figures/algorithm_comp.png')

    compare_ash_triplets(ash_bin_paths, './test_ash_gen.png')

            

main()