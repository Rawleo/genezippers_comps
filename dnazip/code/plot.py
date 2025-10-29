from constants import *
from metrics import *
import matplotlib.pyplot as plt
import numpy as np

def compression_comparison(original_file_path, bin_file_path, file_name, output_file_path):

    original_size = file_size(original_file_path)
    bin_size = file_size(bin_file_path)

    comp_ratio = compression_ratio(original_file_path, bin_file_path)
    space_savings = space_saving(original_file_path, bin_file_path)

    plt.figure(figsize=(7, 7))
    plt.bar(['Compressed File', 'Raw File'],
            height=[bin_size, original_size],
            width=0.7,
            color=['#1E88E5', '#D81B60'],
            edgecolor='black',
            linewidth=3
    )

    plt.suptitle(f"Megabytes Used Per File Type ({file_name})", weight='bold', fontsize=16, linespacing=400)
    plt.title(f"Compression Ratio: {comp_ratio} | Space Savings: {space_savings}", pad=20, fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("File Type", fontsize=14, labelpad=10)
    plt.ylabel("File Size (MB)", fontsize=14, labelpad=15)
    plt.tight_layout()

    plt.savefig(output_file_path, dpi=600)

def clustered_compression_compare(input_file_paths, enc_file_paths, algorithm_name, output_file_path):

        input_file_sizes = []
        enc_file_sizes = []
        file_names = []
        number_of_files = len(input_file_paths)

        for i in range(number_of_files):

                input_size = file_size(input_file_paths[i])
                input_file_sizes.append(input_size)

                bin_size = file_size(enc_file_paths[i])
                enc_file_sizes.append(bin_size)

                file_name = input_file_paths[i].split('/')[-1]
                file_names.append(file_name.split('.')[0])


        plt.figure(figsize=(10, 6))

        x = x = np.arange(number_of_files)
        plt.bar(x-0.1, enc_file_sizes, color='#1E88E5', width=0.2, edgecolor='black', linewidth=2)
        plt.bar(x+0.1, input_file_sizes, color='#D81B60', width=0.2, edgecolor='black', linewidth=2)

        plt.xticks(x, file_names)
        plt.title("Comparison of File Sizes Across Chromosomes (Biocompress)", pad=20, fontsize=14)
        plt.xlabel("Chromosome (1/16th)", fontsize=14, labelpad=10)
        plt.ylabel("Size (MB)", fontsize=14, labelpad=15)
        plt.legend(['Encoded File', 'Raw File'])
        plt.tight_layout()
        plt.savefig('../figures/biocompress_compare_compress_16.png', dpi=600)
        plt.show()