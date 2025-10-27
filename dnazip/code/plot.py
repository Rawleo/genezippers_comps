from constants import *
from metrics import *
import matplotlib.pyplot as plt

def compression_comparison(original_file_path, bin_file_path, file_name, output_file_path):

    original_size = file_size(original_file_path)
    bin_size = file_size(bin_file_path)

    comp_ratio = compression_ratio(original_file_path, bin_file_path)
    space_savings = space_savings(original_file_path, bin_file_path)

    plt.figure(figsize=(6, 7))
    plt.bar(['Compressed File', 'Raw File'],
            height=[bin_size, original_size],
            width=0.7,
            color=['#1E88E5', '#D81B60'],
            edgecolor='black',
            linewidth=3
    )

    plt.suptitle(f"Bytes Used Per File Type ({file_name})", weight='bold', fontsize=16, linespacing=400)
    plt.title(f"Compression Ratio: {comp_ratio} | Space Savings: {space_savings}", pad=20, fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("File Type", fontsize=14, labelpad=10)
    plt.ylabel("Bytes Used", fontsize=14, labelpad=15)
    plt.tight_layout()

    plt.savefig(output_file_path, dpi=600)