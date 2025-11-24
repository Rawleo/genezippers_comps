#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path
from typing import List, Union

# Add the current directory to sys.path to ensure local imports work
try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd()
sys.path.append(str(SCRIPT_DIR))

# Import metrics and constants if available
try:
    from metrics import *
    from constants import *
except ImportError:
    print("Warning: 'metrics' or 'constants' modules not found. Some functions may fail.")

# --- Helper Function ---
def file_size(file_path: Path) -> float:
    """
    Gets the size of a file in Megabytes (MB).
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024) # Convert bytes to MB
    except FileNotFoundError:
        return np.nan
    except Exception as e:
        print(f"Error reading size of {file_path.name}: {e}", file=sys.stderr)
        return np.nan

# --- Functions from plot.py ---

def compression_comparison(original_file_path, bin_file_path, file_name, output_file_path):
    '''
    Creates bar chart comparing compressed file size vs. raw file size
    '''
    # Get sizes of files
    original_size = file_size(Path(original_file_path))
    bin_size = file_size(Path(bin_file_path))

    # Get metrics - assuming these functions are available from metrics.py
    try:
        comp_ratio = compression_ratio(original_file_path, bin_file_path)
        space_savings = space_saving(original_file_path, bin_file_path)
    except NameError:
        comp_ratio = "N/A"
        space_savings = "N/A"

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
    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=600)
    plt.close()


def clustered_compression_compare(input_file_paths, enc_file_paths, algorithm_name, output_file_path):
    '''
    Creates clustered bar charts to visualize compression comparison across multiple files
    '''

    input_file_sizes = []
    enc_file_sizes = []
    file_names = []
    number_of_files = len(input_file_paths)

    # Get metrics
    for i in range(number_of_files):

        input_size = file_size(Path(input_file_paths[i]))
        input_file_sizes.append(input_size)

        bin_size = file_size(Path(enc_file_paths[i]))
        enc_file_sizes.append(bin_size)

        file_name = input_file_paths[i].split('/')[-1]
        file_names.append(file_name.split('.')[0])

    # Make figure
    plt.figure(figsize=(10, 6))
    
    # Formatting
    x = np.arange(number_of_files)
    plt.bar(x-0.1, enc_file_sizes, color='#1E88E5', width=0.2, edgecolor='black', linewidth=2)
    plt.bar(x+0.1, input_file_sizes, color='#D81B60', width=0.2, edgecolor='black', linewidth=2)
    plt.xticks(x, file_names)
    plt.title(f"Comparison of File Sizes Across Chromosomes ({algorithm_name})", pad=20, fontsize=14)
    plt.xlabel("Chromosome (1/4th)", fontsize=14, labelpad=10)
    plt.ylabel("Size (MB)", fontsize=14, labelpad=15)
    plt.legend(['Encoded File', 'Raw File'])
    plt.tight_layout()

    # Save file to output file path
    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=600)
    plt.close()


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
        tot_original_sizes += file_size(Path(genome_file_paths[i]))
        tot_huffman_sizes += file_size(Path(huffman_bin_paths[i]))
        tot_biocomp_sizes += file_size(Path(biocomp_bin_paths[i]))
        tot_var_sizes += file_size(Path(var_file_paths[i]))
        tot_dnazip_sizes += file_size(Path(dnazip_bin_paths[i]))

    # Compute averages
    avg_original_sizes = tot_original_sizes / num_files
    avg_huffman_sizes = tot_huffman_sizes / num_files
    avg_biocomp_sizes = tot_biocomp_sizes / num_files
    avg_var_sizes = tot_var_sizes / num_files
    avg_dnazip_sizes = tot_dnazip_sizes / num_files

    # X values (genome counts)
    x = np.array(x_range)

    f_huffman = x * avg_huffman_sizes
    f_biocomp1 = x * avg_biocomp_sizes
    f_var = (x * avg_var_sizes) + avg_original_sizes
    f_dnazip = (x * avg_dnazip_sizes) + avg_original_sizes

    # Create figure
    plt.figure(figsize=(10, 6))

    # Plot each algorithm’s scaling curve
    plt.plot(x, f_huffman, color='#D81B60', linewidth=2.5, marker='o', label='Huffman')
    plt.plot(x, f_biocomp1, color='#1E88E5', linewidth=2.5, marker='s', label='Biocompress 1')
    plt.plot(x, f_var, color='#004D40', linewidth=2.5, marker='D', label='VCF')
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
    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=600)
    plt.close()


def all_compression_comparisons_v1(genome_file_paths, huffman_bin_paths, biocomp_bin_paths, var_file_paths, dnazip_bin_paths, output_file_path):
    '''
    Creates bar chart comparing:
    * original genome
    * huffman compression
    * biocompress output
    * variants (vcf) file
    * dnazip output
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
        original_sizes.append(round(file_size(Path(genome_file_paths[i])), 2))
        huffman_sizes.append(file_size(Path(huffman_bin_paths[i])))
        biocomp_sizes.append(file_size(Path(biocomp_bin_paths[i])))
        var_sizes.append(file_size(Path(var_file_paths[i])))
        dnazip_sizes.append(file_size(Path(dnazip_bin_paths[i])))
    
    labels = ['DNAZip', 'VCF', 'Biocompress 1', 'Huffman']
    colors = ['#FFC107', '#004D40', '#1E88E5', '#D81B60']

    # Make figure
    plt.figure(figsize=(15, 7))
    
    # Formatting
    x = np.arange(num_files)
    plt.bar(x-0.3, dnazip_sizes, color='#FFC107', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x-0.1, var_sizes, color='#004D40', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x+0.1, biocomp_sizes, color='#1E88E5', width=0.2, edgecolor='black', linewidth=1)
    plt.bar(x+0.3, huffman_sizes, color='#D81B60', width=0.2, edgecolor='black', linewidth=1)

    # Extract genome names for labels
    genome_names = [Path(p).stem.replace('_Genome', '') for p in genome_file_paths]
    xtick_labels = [f'{name} \n Original Size: {size} MB' for name, size in zip(genome_names, original_sizes)]

    plt.xticks(x, xtick_labels, fontsize=14)
    plt.ylabel("Size (MB)", fontsize=18, labelpad=15, weight='bold')
    plt.xlabel("Genomes", fontsize=18, labelpad=15, weight='bold')
    plt.legend(labels, fontsize=14, loc='upper center', ncols=4, bbox_to_anchor=(0.5, 1.12))

    plt.tight_layout()
    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=800)
    plt.close()

# --- Functions from plot_2.py ---

def plot_grouped_compression_all_variants(variants_dir: Path, output_dir: Path, output_plot_path: Path):
    """
    Creates a clustered bar chart comparing raw variant file sizes
    against the four different encoded combinations.
    """
    
    # --- 1. Define Variants and Combinations ---
    variant_names = [
        # 'hg38_Han1_genome', 
        'hg38_ash1_genome', 
        # 'hg38_pan027_genome', 
        # 'hg38_T2T-CHM13_genome',
        'hg38_ash1_chr21',
    ]
    
    raw_path_template = variants_dir / "{variant}_sorted_variants.txt"
    
    combinations = {
        'VINT': {
            'path_template': output_dir / "{variant}_False_False_False_0_Encoded.bin",
            'color': '#ffe79e' # Indigo
        },
        'VINT + Delta': {
            'path_template': output_dir / "{variant}_True_False_False_0_Encoded.bin",
            'color': '#ffd75e' # Red/Pink
        },
        'VINT + Delta + Huffman (8-mer)': {
            'path_template': output_dir / "{variant}_True_False_True_8_Encoded.bin",
            'color': '#FFC107' # Yellow
        },
        'VINT + Delta + Huffman (8-mer) + dbSNP': {
            'path_template': output_dir / "{variant}_True_True_True_8_Encoded.bin",
            'color': '#FFb107' # Turquoise
        }
    }
    
    combo_names = list(combinations.keys())
    file_sizes = {name: [] for name in combo_names}
    raw_sizes_mb_list = [] 
    x_labels = [] 

    print("--- Collecting File Size Data (plot_grouped_compression_all_variants) ---")

    all_sizes_for_max = [] 
    for variant in variant_names:
        x_labels.append(variant.replace('hg38_', ''))

        # print(f"\nProcessing: {variant}")
        
        raw_f_path = Path(str(raw_path_template).format(variant=variant))
        raw_size_mb = file_size(raw_f_path)
        raw_sizes_mb_list.append(raw_size_mb) 
        
        for name in combo_names:
            f_path = Path(str(combinations[name]['path_template']).format(variant=variant))
            size_mb = file_size(f_path)
            if not np.isnan(size_mb):
                all_sizes_for_max.append(size_mb)
            file_sizes[name].append(size_mb)

    # --- 4. Create the Plot ---
    plt.figure(figsize=(7, 9)) 
    plt.grid(False)
    
    num_variants = len(x_labels)
    num_bars = len(combo_names)
    
    x = np.arange(num_variants)
    width = 0.15 
    
    if num_bars % 2 == 1:
        offsets = np.linspace(-width * (num_bars // 2), width * (num_bars // 2), num_bars)
    else:
        offsets = np.linspace(-width * (num_bars / 2 - 0.25), width * (num_bars / 2 - 0.25), num_bars)

    for i, name in enumerate(combo_names):
        sizes = file_sizes[name] 
        color = combinations[name]['color']
        
        bar_container = plt.bar(
            x + offsets[i], 
            sizes, 
            color=color, 
            width=width, 
            edgecolor='black', 
            linewidth=1, 
            label=name
        )
        
        comp_labels = []
        for j in range(len(sizes)): 
            comp_s = sizes[j]          
            raw_s = raw_sizes_mb_list[j] 
            
            label_text = '' 
            if not np.isnan(comp_s) and not np.isnan(raw_s) and comp_s > 0:
                label_text = f'{round(comp_s, 2)} MB'
            comp_labels.append(label_text)

        plt.bar_label(
            bar_container, 
            fmt='%s',
            labels=comp_labels,
            fontsize=12,
            padding=3,
            weight='bold',
        )

    # --- 5. Formatting ---
    final_x_labels = x_labels 
    
    if num_variants > 1:
        new_labels = []
        for name, size in zip(x_labels, raw_sizes_mb_list):
            if not np.isnan(size):
                new_labels.append(f"{name}\n(Original Size: {size:.2f} MB)")
            else:
                new_labels.append(f"{name}\n(Size N/A)")
        final_x_labels = new_labels
        
    elif num_variants == 1 and not np.isnan(raw_sizes_mb_list[0]):
        subtitle_text = f"{x_labels[0]} ({raw_sizes_mb_list[0]:.2f} MB)"
        plt.title(subtitle_text, fontsize=14, pad=10, loc='center', weight="bold")
        
    plt.ylabel("Size (MB)", fontsize=14, labelpad=15)
    plt.xticks(x, [], fontsize=12)
    plt.tick_params(axis='y', which='both', length=4)
    plt.yticks(fontsize=12)

    if all_sizes_for_max:
        current_max = max(all_sizes_for_max)
        plt.ylim(top=current_max * 1.20) 
    
    plt.legend(
        fontsize=12, 
        loc='upper right', 
        ncol=1,
        frameon=True       
    )
    
    plt.tight_layout(pad=1.0, rect=[0, 0, 1, 0.96]) 

    # --- 6. Save the Plot ---
    output_plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_plot_path}")
    plt.close()

# --- Functions from plot_3.py ---

def plot_grouped_compression_two_variants(variants_dir: Path, output_dir: Path, output_plot_path: Path):
    """
    Creates a clustered bar chart comparing raw variant file sizes
    against the four different encoded combinations.
    Plots exactly two variants side-by-side.
    """
    
    variant_names = [
        'hg38_Han1_genome', 
        # 'hg38_ash1_genome', 
        'hg38_pan027_genome', 
        'hg38_T2T-CHM13_genome',
        # 'hg38_ash1_chr21',
    ]
    
    raw_path_template = variants_dir / "{variant}_sorted_variants.txt"
    
    combinations = {
        'VINT': {
            'path_template': output_dir / "{variant}_False_False_False_0_Encoded.bin",
            'color': '#ffe79e' # Indigo
        },
        'VINT + Delta': {
            'path_template': output_dir / "{variant}_True_False_False_0_Encoded.bin",
            'color': '#ffd75e' # Red/Pink
        },
        'VINT + Delta + Huffman (8-mer)': {
            'path_template': output_dir / "{variant}_True_False_True_8_Encoded.bin",
            'color': '#FFC107' # Yellow
        },
        'VINT + Delta + Huffman (8-mer) + dbSNP': {
            'path_template': output_dir / "{variant}_True_True_True_8_Encoded.bin",
            'color': '#FFb107' # Turquoise
        }
    }
    
    combo_names = list(combinations.keys())
    file_sizes = {name: [] for name in combo_names}
    raw_sizes_mb_list = [] 
    x_labels = [] 

    print("--- Collecting File Size Data (plot_grouped_compression_two_variants) ---")

    for variant in variant_names:
        x_labels.append(variant.replace('hg38_', ''))

        raw_f_path = Path(str(raw_path_template).format(variant=variant))
        raw_size_mb = file_size(raw_f_path)
        raw_sizes_mb_list.append(raw_size_mb) 
        
        for name in combo_names:
            f_path = Path(str(combinations[name]['path_template']).format(variant=variant))
            size_mb = file_size(f_path)
            file_sizes[name].append(size_mb)

    # --- 3.5 Extract sizes for independent Y-axis scaling ---
    genome_sizes_for_max = []
    chr21_sizes_for_max = []
    for name in combo_names:
        sizes_for_combo = file_sizes[name]
        if len(sizes_for_combo) == 2: 
            if not np.isnan(sizes_for_combo[0]):
                genome_sizes_for_max.append(sizes_for_combo[0])
            if not np.isnan(sizes_for_combo[1]):
                chr21_sizes_for_max.append(sizes_for_combo[1])

    # --- 4. Create the Plot ---
    num_variants = len(x_labels)
    num_bars = len(combo_names)
    
    if num_variants != 2:
        print(f"Warning: plot_grouped_compression_two_variants expects exactly 2 variants, found {num_variants}. Skipping plot.")
        return
        
    fig, (ax1, ax2) = plt.subplots(
        nrows=1, 
        ncols=2, 
        figsize=(8, 9), 
        sharey=False      # Independent Y-axes
    )
    
    width = 0.15 
    
    if num_bars % 2 == 1:
        offsets = np.linspace(-width * (num_bars // 2), width * (num_bars // 2), num_bars)
    else:
        offsets = np.linspace(-width * (num_bars / 2 - 0.25), width * (num_bars / 2 - 0.25), num_bars)

    for i, name in enumerate(combo_names):
        sizes = file_sizes[name] 
        color = combinations[name]['color']
        
        # --- Plot for AX1 (Genome) ---
        size_g = sizes[0]
        
        bar_container_g = ax1.bar(
            offsets[i], 
            size_g, 
            color=color, 
            width=width, 
            edgecolor='black', 
            linewidth=1, 
            label=name 
        )
        
        # --- Plot for AX2 (Chr21) ---
        size_c = sizes[1]
        
        bar_container_c = ax2.bar(
            offsets[i], 
            size_c, 
            color=color, 
            width=width, 
            edgecolor='black', 
            linewidth=1
        )
        
        # --- Label for AX1 (Genome) ---
        label_text_g = '' 
        if not np.isnan(size_g) and size_g > 0:
            label_text_g = f'{round(size_g, 2)}'
        
        ax1.bar_label(
            bar_container_g, 
            fmt='%s',
            labels=[label_text_g], 
            fontsize=12,
            padding=3,
            weight='bold',
        )

        # --- Label for AX2 (Chr21) ---
        label_text_c = ''
        if not np.isnan(size_c) and size_c > 0:
            label_text_c = f'{round(size_c, 2)}'

        ax2.bar_label(
            bar_container_c, 
            fmt='%s',
            labels=[label_text_c], 
            fontsize=12,
            padding=3,
            weight='bold',
        )

    # --- 5. Formatting ---
    if not np.isnan(raw_sizes_mb_list[0]):
        ax1_title = f"{x_labels[0]}\n({raw_sizes_mb_list[0]:.2f} MB)"
    else:
        ax1_title = f"{x_labels[0]}\n(N/A)"
    ax1.set_title(ax1_title, fontsize=14, weight="bold")
    
    if not np.isnan(raw_sizes_mb_list[1]):
        ax2_title = f"{x_labels[1]}\n({raw_sizes_mb_list[1]:.2f} MB)"
    else:
        ax2_title = f"{x_labels[1]}\n(N/A)"
    ax2.set_title(ax2_title, fontsize=14, weight="bold")

    ax1.set_ylabel("Size (MB)", fontsize=14, labelpad=15)
    
    ax1.set_xticks([])
    ax2.set_xticks([])
    
    ax1.tick_params(axis='y', which='both', length=4)
    ax1.tick_params(axis='y', labelsize=12)
    
    ax2.tick_params(axis='y', which='both', length=4)
    ax2.tick_params(axis='y', labelsize=12)
    ax2.set_ylabel("Size (MB)", fontsize=14, labelpad=15)
    ax2.yaxis.set_label_position("right") 
    ax2.yaxis.tick_right() 
    
    ax1.grid(False)
    ax2.grid(False)

    if genome_sizes_for_max:
        current_max_g = max(genome_sizes_for_max)
        ax1.set_ylim(top=current_max_g * 1.25) 
    
    if chr21_sizes_for_max:
        current_max_c = max(chr21_sizes_for_max)
        ax2.set_ylim(top=current_max_c * 1.25) 
        
    handles, labels = ax1.get_legend_handles_labels()
    
    fig.legend(
        handles,
        labels,
        fontsize=12, 
        loc='lower center',            
        bbox_to_anchor=(0.5, 0.02),  
        ncol=len(combo_names)//2,         
        frameon=True,    
        edgecolor='black',   
    )
    
    plt.tight_layout(pad=1.0, rect=[0, 0.1, 1, 0.96]) 

    output_plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_plot_path}")
    plt.close()

# --- Functions from plot_4.py ---

def plot_combined_ratio(variants_dir: Path, output_dir: Path, output_plot_path: Path):
    """
    Creates a SINGLE grouped bar chart comparing COMPRESSION RATIO (Raw / Compressed)
    for all variants on one plot.
    """
    
    variant_names = [
        'hg38_pan027_genome', 
        'hg38_T2T-CHM13_genome',
        'hg38_Han1_genome', 
        # 'hg38_ash1_genome', 
        # 'hg38_ash1_chr21',
    ]
    
    raw_path_template = variants_dir / "{variant}_sorted_variants.txt"
    
    combinations = {
        'VINT': {
            'path_template': output_dir / "{variant}_False_False_False_0_Encoded.bin",
            'color': '#ffe79e' # Indigo
        },
        'VINT + Delta': {
            'path_template': output_dir / "{variant}_True_False_False_0_Encoded.bin",
            'color': '#ffd75e' # Red/Pink
        },
        'VINT + Delta + Huffman': {
            'path_template': output_dir / "{variant}_True_False_True_8_Encoded.bin",
            'color': '#FFC107' # Yellow
        },
        'VINT + Delta + Huffman + dbSNP': {
            'path_template': output_dir / "{variant}_True_True_True_8_Encoded.bin",
            'color': '#FFb107' # Turquoise
        }
    }
    
    combo_names = list(combinations.keys())
    
    ratio_data = {name: [] for name in combo_names}
    raw_sizes_mb_list = [] 
    base_x_labels = [] 

    print("--- Collecting File Size Data & Calculating Ratios (plot_combined_ratio) ---")

    for i, variant in enumerate(variant_names):
        short_name = variant.replace('hg38_', '').replace('ash1', 'ash1_v2.2') 
        base_x_labels.append(short_name)

        raw_f_path = Path(str(raw_path_template).format(variant=variant))
        raw_size_mb = file_size(raw_f_path)
        raw_sizes_mb_list.append(raw_size_mb)
        
        for name in combo_names:
            f_path = Path(str(combinations[name]['path_template']).format(variant=variant))
            compressed_size_mb = file_size(f_path)
            
            ratio = np.nan
            if not np.isnan(compressed_size_mb) and not np.isnan(raw_size_mb) and compressed_size_mb > 0:
                ratio = compressed_size_mb / raw_size_mb
            
            ratio_data[name].append(ratio)

    num_variants = len(base_x_labels)
    num_bars = len(combo_names)
    
    if num_variants == 0:
        print("Error: No variants found. Exiting.")
        return
        
    fig, ax = plt.subplots(figsize=(7, 9))
    
    x = np.arange(num_variants)
    width = 0.15 
    
    if num_bars % 2 == 1:
        offsets = np.linspace(-width * (num_bars // 2), width * (num_bars // 2), num_bars)
    else:
        offsets = np.linspace(-width * (num_bars / 2 - 0.25), width * (num_bars / 2 - 0.25), num_bars)

    max_ratio_val = 0
    for i, name in enumerate(combo_names):
        ratios = ratio_data[name] 
        color = combinations[name]['color']
        
        valid_ratios = [r for r in ratios if not np.isnan(r)]
        if valid_ratios:
            max_ratio_val = max(max_ratio_val, max(valid_ratios))

        bar_container = ax.bar(
            x + offsets[i], 
            ratios, 
            width, 
            label=name, 
            color=color, 
            edgecolor='black', 
            linewidth=1
        )
        
        labels = [f'{r:.1f}x' if not np.isnan(r) else '' for r in ratios]
        ax.bar_label(
            bar_container, 
            labels=labels, 
            padding=3, 
            fontsize=10, 
            weight='bold'
        )

    ax.set_ylabel("Compression Ratio (Compressed / Raw)", fontsize=14, labelpad=15)
    
    final_xticklabels = []
    for i, label in enumerate(base_x_labels):
        raw_mb = raw_sizes_mb_list[i]
        if not np.isnan(raw_mb):
            final_xticklabels.append(f"{label}\n({round(raw_mb, 2)} MB)")
        else:
            final_xticklabels.append(f"{label}\n(N/A)")
            
    ax.set_xticks(x)
    ax.set_xticklabels(final_xticklabels, fontsize=12, weight='bold')
    
    ax.tick_params(axis='y', labelsize=12)
    ax.set_axisbelow(True) 
    ax.set_ylim(0, max_ratio_val * 1.15) 
    
    ax.legend(
        loc='upper center', 
        bbox_to_anchor=(0.5, -0.15), 
        ncol=2, 
        fontsize=12, 
        frameon=True, 
        edgecolor='black'
    )

    plt.tight_layout()

    output_plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_plot_path}")
    plt.close()

# --- Functions from plot_5.py ---

def plot_grouped_compression_n_variants(variants_dir: Path, output_dir: Path, output_plot_path: Path):
    """
    Creates a clustered bar chart comparing raw variant file sizes
    against the four different encoded combinations.
    Plots N variants side-by-side.
    """
    
    variant_names = [
        # 'hg38_pan027_genome', 
        # 'hg38_T2T-CHM13_genome',
        # 'hg38_Han1_genome', 
        'hg38_ash1_genome', 
        'hg38_ash1_chr21',
    ]
    
    raw_path_template = variants_dir / "{variant}_sorted_variants.txt"
    
    combinations = {
        'VINT': {
            'path_template': output_dir / "{variant}_False_False_False_0_Encoded.bin",
            'color': '#ffe79e' # Indigo
        },
        'VINT + Delta': {
            'path_template': output_dir / "{variant}_True_False_False_0_Encoded.bin",
            'color': '#ffd75e' # Red/Pink
        },
        'VINT + Delta + Huffman': {
            'path_template': output_dir / "{variant}_True_False_True_8_Encoded.bin",
            'color': '#FFC107' # Yellow
        },
        'VINT + Delta + Huffman + dbSNP': {
            'path_template': output_dir / "{variant}_True_True_True_8_Encoded.bin",
            'color': '#FFb107' # Turquoise
        }
    }
    
    combo_names = list(combinations.keys())
    file_sizes = {name: [] for name in combo_names}
    raw_sizes_mb_list = [] 
    x_labels = [] 

    print("--- Collecting File Size Data (plot_grouped_compression_n_variants) ---")

    for variant in variant_names:
        short_name = variant.replace('hg38_', '').replace('ash1', 'ash1_v2.2') 
        x_labels.append(short_name)

        raw_f_path = Path(str(raw_path_template).format(variant=variant))
        raw_size_mb = file_size(raw_f_path)
        raw_sizes_mb_list.append(raw_size_mb) 
        
        for name in combo_names:
            f_path = Path(str(combinations[name]['path_template']).format(variant=variant))
            size_mb = file_size(f_path)
            file_sizes[name].append(size_mb)

    num_variants = len(x_labels)
    max_sizes_per_variant = [[] for _ in range(num_variants)]
    for name in combo_names:
        sizes_for_combo = file_sizes[name]
        for j in range(num_variants):
            if j < len(sizes_for_combo) and not np.isnan(sizes_for_combo[j]):
                max_sizes_per_variant[j].append(sizes_for_combo[j])

    num_bars = len(combo_names)
    
    if num_variants == 0:
        print("Error: No variants found or processed. Exiting.")
        return
        
    fig, axes = plt.subplots(
        nrows=1, 
        ncols=num_variants, 
        figsize=(4 * num_variants, 9), 
        sharey=False      
    )
    
    if num_variants == 1:
        axes = [axes]
    
    width = 0.15 
    
    if num_bars % 2 == 1:
        offsets = np.linspace(-width * (num_bars // 2), width * (num_bars // 2), num_bars)
    else:
        offsets = np.linspace(-width * (num_bars / 2 - 0.25), width * (num_bars / 2 - 0.25), num_bars)

    for i, name in enumerate(combo_names):
        sizes = file_sizes[name] 
        color = combinations[name]['color']
        
        for j, ax in enumerate(axes):
            if j >= len(sizes) or j >= len(raw_sizes_mb_list):
                continue 
                
            size_j = sizes[j]
            
            bar_container = ax.bar(
                offsets[i], 
                size_j, 
                color=color, 
                width=width, 
                edgecolor='black', 
                linewidth=1, 
                label=name if j == 0 else "" 
            )
            
            label_text = '' 
            if not np.isnan(size_j) and size_j > 0:
                label_text = f'{round(size_j, 2)}'
            
            ax.bar_label(
                bar_container, 
                fmt='%s',
                labels=[label_text], 
                fontsize=12,
                padding=3,
                weight='bold',
            )

    for j, ax in enumerate(axes):
        if j < len(raw_sizes_mb_list) and not np.isnan(raw_sizes_mb_list[j]):
            ax_label_text = f"{x_labels[j]}\n(VCF: {raw_sizes_mb_list[j]:.2f} MB)"
        else:
            ax_label_text = f"{x_labels[j]}\n(N/A)"

        ax.set_xlabel(ax_label_text, fontsize=14, labelpad=15)

        if j == 0:
            ax.set_ylabel("Size (MB)", fontsize=14, labelpad=15)
        
        ax.set_xticks([])
        
        ax.tick_params(axis='y', which='both', length=4)
        ax.tick_params(axis='y', labelsize=12)
        
        if j == num_variants - 1 and num_variants > 1:
            ax.set_ylabel("Size (MB)", fontsize=14, labelpad=15)
            ax.yaxis.set_label_position("right") 
            ax.yaxis.tick_right()
        
        ax.grid(False)

        if max_sizes_per_variant[j]: 
            current_max = max(max_sizes_per_variant[j])
            if not np.isnan(current_max):
                ax.set_ylim(top=current_max * 1.25) 
            
    handles, labels = axes[0].get_legend_handles_labels()
    
    fig.legend(
        handles,
        labels,
        fontsize=12, 
        loc='upper center',            
        bbox_to_anchor=(0.5, 1.0),  
        ncol=len(combo_names)//2, 
        frameon=True,    
        edgecolor='black',   
    )
    
    plt.tight_layout(pad=1.0, rect=[0, 0.0, 1, 0.90]) 

    output_plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_plot_path}")
    plt.close()

# --- Functions from super.py and super_copy.py ---

def all_compression_comparisons_vcf_dnazip(
    genome_file_paths: List[Path], 
    huffman_bin_paths: List[Path], 
    biocomp_bin_paths: List[Path], 
    var_file_paths: List[Path], 
    dnazip_bin_paths: List[Path], 
    output_file_path: Path
):
    """
    Creates a clustered bar chart comparing ONLY VCF and DNAzip.
    """
    
    num_files = len(genome_file_paths)
    
    ratios = {
        'VCF': [],
        'DNAzip': []
    }

    raw_sizes_mb = []
    
    x_labels_short = [fp.stem.replace('_Genome', '') for fp in genome_file_paths]

    print("--- Collecting Data & Calculating Ratios (all_compression_comparisons_vcf_dnazip) ---")
    
    for i in range(num_files):
        raw_size = file_size(genome_file_paths[i])
        raw_sizes_mb.append(raw_size)
        
        if np.isnan(raw_size):
            ratios['VCF'].append(np.nan)
            ratios['DNAzip'].append(np.nan)
            continue

        def get_ratio(path):
            size = file_size(path)
            if not np.isnan(size) and size > 0:
                r = size / raw_size 
                return r
            return np.nan

        ratios['VCF'].append(get_ratio(var_file_paths[i]))
        ratios['DNAzip'].append(get_ratio(dnazip_bin_paths[i]))

    combinations = {
        'VCF': {
            'data': ratios['VCF'],
            'color': '#004D40' # Dark Green
        },
        'DNAzip': {
            'data': ratios['DNAzip'],
            'color': '#FFC107' # Amber/Gold
        }
    }
    
    combo_names = list(combinations.keys())

    final_x_labels = []
    for name, size in zip(x_labels_short, raw_sizes_mb):
        if not np.isnan(size):
            final_x_labels.append(f"{name}\n({size:.2f} MB)")
        else:
            final_x_labels.append(f"{name}\n(N/A)")

    fig, ax = plt.subplots(figsize=(6, 7))
    
    num_groups = num_files
    x = np.arange(num_groups) 
    
    bar_width = 0.30      
    inner_gap = 0.080     
    
    offset_vcf = -(bar_width / 2 + inner_gap / 2)
    offset_dnazip = (bar_width / 2 + inner_gap / 2)
    
    offsets = [offset_vcf, offset_dnazip]

    max_ratio_val = 0

    for i, name in enumerate(combo_names):
        data = combinations[name]['data']
        color = combinations[name]['color']
        
        valid_data = [d for d in data if not np.isnan(d)]
        if valid_data:
            max_ratio_val = max(max_ratio_val, max(valid_data))
        
        bar_container = ax.bar(
            x + offsets[i], 
            data, 
            bar_width, 
            label=name, 
            color=color, 
            edgecolor='black', 
            linewidth=1
        )
        
        labels = [f'{v:.4f}' if not np.isnan(v) else '' for v in data]
        ax.bar_label(
            bar_container, 
            labels=labels,
            fontsize=10,
            padding=3,
            weight='bold'
        )

    ax.set_ylabel("Compression Ratio", fontsize=14, labelpad=15)
    
    ax.set_xticks(x)
    ax.set_xticklabels(final_x_labels, fontsize=11)
    ax.tick_params(axis='y', labelsize=12)
    
    ax.set_axisbelow(True)
    ax.set_ylim(0, max_ratio_val * 1.2) 

    ax.legend(
        loc='upper center',   
        fontsize=12,
        frameon=True,
        ncol =2,
        edgecolor='black',
        facecolor='white',
        framealpha=1.0
    )
    
    plt.tight_layout()

    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_file_path}")
    plt.close()

def all_compression_comparisons_huff_bio_dnazip(
    genome_file_paths: List[Path], 
    huffman_bin_paths: List[Path], 
    biocomp_bin_paths: List[Path], 
    var_file_paths: List[Path], 
    dnazip_bin_paths: List[Path], 
    output_file_path: Path
):
    """
    Creates a clustered bar chart comparing multiple compression methods
    across multiple genomes.
    """
    
    num_files = len(genome_file_paths)

    original_sizes = []
    huffman_sizes = []
    biocomp_sizes = []
    var_sizes = []
    dnazip_sizes = []

    x_labels_short = [fp.stem.replace('_Genome', '') for fp in genome_file_paths]

    print("--- Collecting File Size Data (all_compression_comparisons_huff_bio_dnazip) ---")
    for i in range(num_files):
        orig_size = file_size(genome_file_paths[i])
        original_sizes.append(orig_size)

        huff_size = file_size(huffman_bin_paths[i])
        huffman_sizes.append(huff_size)
        
        bio_size = file_size(biocomp_bin_paths[i])
        biocomp_sizes.append(bio_size)
        
        var_size = file_size(var_file_paths[i])
        var_sizes.append(var_size)
        
        dnaz_size = file_size(dnazip_bin_paths[i])
        dnazip_sizes.append(dnaz_size)

    combinations = {
        'Huffman (8-mer)': {
            'data': huffman_sizes,
            'color': '#D81B60' # Indigo
        },
        'Biocompress 1': {
            'data': biocomp_sizes,
            'color': '#1E88E5' # Red/Pink
        },
        'DNAzip': {
            'data': dnazip_sizes,
            'color': '#FFC107' # Turquoise
        }
    }
    
    combo_names = list(combinations.keys())

    final_x_labels = []
    for name, size in zip(x_labels_short, original_sizes):
        if not np.isnan(size):
            final_x_labels.append(f"{name}\n({size:.2f} MB)")
        else:
            final_x_labels.append(f"{name}\n(N/A)")

    plt.figure(figsize=(7, 8)) 
    plt.grid(False)
    
    num_groups = num_files
    num_bars = len(combo_names)
    x = np.arange(num_groups) 
    
    step = 0.25        
    bar_width = 0.2  
    
    offsets = np.linspace(-step * (num_bars - 1) / 2, step * (num_bars - 1) / 2, num_bars)

    all_sizes_for_max = []
    for i, name in enumerate(combo_names):
        sizes = combinations[name]['data'] 
        color = combinations[name]['color']
        
        all_sizes_for_max.extend(s for s in sizes if not np.isnan(s))
        
        bar_container = plt.bar(
            x + offsets[i], 
            sizes, 
            color=color, 
            width=bar_width, 
            edgecolor='black', 
            linewidth=1, 
            label=name
        )
        
        plt.bar_label(
            bar_container, 
            fmt='%.1f',
            fontsize=10,
            padding=3,
            weight='bold',
        )

    plt.ylabel("Size (MB)", fontsize=14, labelpad=10)
    
    plt.xticks(x, final_x_labels, fontsize=12)
    
    plt.tick_params(axis='y', which='both', length=4)
    plt.yticks(fontsize=10)

    if all_sizes_for_max:
        max_height = max(all_sizes_for_max)
        plt.ylim(top=max_height * 1.25) 
    
    plt.legend(
        loc='upper center',
        ncol=num_bars,
        fontsize=12,
        frameon=True,
        edgecolor='black'
    )
    
    plt.tight_layout(pad=1.0, rect=[0, 0.1, 1, 0.96]) 

    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved successfully to {output_file_path}")
    plt.close()

def compare_ash_triplets(file_paths, output_file_path):
    """
    Plots raw sizes for Ash1 triplets.
    """
    vint_size = file_size(Path(file_paths[0]))
    vint_delta_dbsnp_size = file_size(Path(file_paths[1]))
    vint_delta_size = file_size(Path(file_paths[2]))

    labels = ['VINT', 'VINT + DELTA + dbSNP', 'VINT + DELTA']
    colors = ['#ffe79e', '#FFb107', '#ffd75e'] 

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels,
            [vint_size, vint_delta_dbsnp_size, vint_delta_size],
            color = colors,
            edgecolor='black',
            linewidth=1,
            width=0.6)
    
    plt.bar_label(bars, fmt='%.2f MB', padding=3, weight='bold')
    plt.ylabel("Compressed File Size (MB)", weight='bold', fontsize=12)
    plt.title("Ash1 Variant Compression Sizes", weight='bold', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_axisbelow(True)
    
    output_file_path = Path(output_file_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    print("Starting combined plotting script...")
    
    # Define Base Paths
    # SCRIPT_DIR is defined at the top
    PROJECT_ROOT = SCRIPT_DIR.parent
    REPO_ROOT = PROJECT_ROOT.parent
    
    # Common Paths
    DNAZIP_DATA = PROJECT_ROOT / 'data'
    VARIANTS_DIR = DNAZIP_DATA / 'variants'
    OUTPUT_DIR = DNAZIP_DATA / 'output'
    FIGURES_DIR = DNAZIP_DATA / 'figures'
    
    BIOCOMPRESS_DIR = REPO_ROOT / 'biocompress_1'
    HUFFMAN_DIR = REPO_ROOT / 'huffman_coding'
    
    # --- Data Lists ---
    genome_file_paths = [
        DNAZIP_DATA / 'PAN027_mat_v1.0/PAN027_mat_v1_Genome.txt',
        DNAZIP_DATA / 'T2T-CHM13v2.0/T2T-CHM13v2_Genome.txt',
        DNAZIP_DATA / 'Han1/Han1_Genome.txt'
    ]

    huffman_bin_paths = [
        HUFFMAN_DIR / 'output/ENCODED_PAN027_mat_v1_Genome_K_MER_8.bin',
        HUFFMAN_DIR / 'output/ENCODED_T2T-CHM13v2_Genome_K_MER_8.bin',
        HUFFMAN_DIR / 'output/ENCODED_Han1_Genome_K_MER_8.bin'
    ]

    biocomp_bin_paths = [
        BIOCOMPRESS_DIR / 'data/PAN027_mat_v1_Genome_13.bin',
        BIOCOMPRESS_DIR / 'data/T2T-CHM13v2_Genome_13.bin',
        BIOCOMPRESS_DIR / 'data/Han1_Genome_13.bin'
    ]
    
    var_file_paths = [
        VARIANTS_DIR / 'hg38_pan027_genome_sorted_variants.txt',
        VARIANTS_DIR / 'hg38_T2T-CHM13_genome_sorted_variants.txt',
        VARIANTS_DIR / 'hg38_Han1_genome_sorted_variants.txt'
    ]

    dnazip_bin_paths = [
        OUTPUT_DIR / 'pan027_VINT_True_False_Encoded.bin',
        OUTPUT_DIR / 'T2T-_CHM13_VINT_True_False_Encoded.bin',
        OUTPUT_DIR / 'Han1_VINT_True_False_Encoded.bin'
    ]
    
    # Re-ordered for super.py logic (Han1, PAN027, T2T)
    genome_file_paths_ordered = [
        DNAZIP_DATA / 'Han1/Han1_Genome.txt',
        DNAZIP_DATA / 'PAN027_mat_v1.0/PAN027_mat_v1_Genome.txt',
        DNAZIP_DATA / 'T2T-CHM13v2.0/T2T-CHM13v2_Genome.txt'
    ]
    
    huffman_bin_paths_ordered = [
        HUFFMAN_DIR / 'output/ENCODED_Han1_Genome_K_MER_8.bin',
        HUFFMAN_DIR / 'output/ENCODED_PAN027_mat_v1_Genome_K_MER_8.bin',
        HUFFMAN_DIR / 'output/ENCODED_T2T-CHM13v2_Genome_K_MER_8.bin'
    ]
    
    biocomp_bin_paths_ordered = [
        BIOCOMPRESS_DIR / 'data/Han1_Genome_13.bin',
        BIOCOMPRESS_DIR / 'data/PAN027_mat_v1_Genome_13.bin',
        BIOCOMPRESS_DIR / 'data/T2T-CHM13v2_Genome_13.bin'
    ]
    
    var_file_paths_ordered = [
        VARIANTS_DIR / 'hg38_Han1_genome_sorted_variants.txt',
        VARIANTS_DIR / 'hg38_pan027_genome_sorted_variants.txt',
        VARIANTS_DIR / 'hg38_T2T-CHM13_genome_sorted_variants.txt'
    ]
    
    dnazip_bin_paths_ordered = [
        OUTPUT_DIR / 'hg38_Han1_genome_True_False_True_8_Encoded.bin',
        OUTPUT_DIR / 'hg38_pan027_genome_True_False_True_8_Encoded.bin',
        OUTPUT_DIR / 'hg38_T2T-CHM13_genome_True_False_True_8_Encoded.bin'
    ]

    ash_bin_paths = [
        OUTPUT_DIR / 'ash1_VINT_False_False_Encoded.bin',
        OUTPUT_DIR / 'ash1_VINT_True_True_Encoded.bin',
        OUTPUT_DIR / 'ash1_VINT_True_False_Encoded.bin'
    ]

    # --- Executing Plots ---

    # 1. all_compression_comparisons_v1 (from plot.py)
    all_compression_comparisons_v1(
        [str(p) for p in genome_file_paths], 
        [str(p) for p in huffman_bin_paths], 
        [str(p) for p in biocomp_bin_paths], 
        [str(p) for p in var_file_paths], 
        [str(p) for p in dnazip_bin_paths], 
        FIGURES_DIR / 'algorithm_comp.png'
    )

    # 2. time_scale_comparison (from plot.py)
    time_scale_comparison(
        [str(p) for p in genome_file_paths], 
        [str(p) for p in huffman_bin_paths], 
        [str(p) for p in biocomp_bin_paths], 
        [str(p) for p in var_file_paths], 
        [str(p) for p in dnazip_bin_paths], 
        FIGURES_DIR / 'time_v_storage.png',
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    )

    # 3. plot_grouped_compression_all_variants (from plot_2.py)
    plot_grouped_compression_all_variants(VARIANTS_DIR, OUTPUT_DIR, FIGURES_DIR / 'storage_savings_vs_variants_plot_all.png')

    # 4. plot_grouped_compression_two_variants (from plot_3.py)
    # Note: This function expects exactly 2 variants in its internal list. 
    # Since the internal list is hardcoded in the function, it will run with whatever is there.
    plot_grouped_compression_two_variants(VARIANTS_DIR, OUTPUT_DIR, FIGURES_DIR / 'storage_savings_vs_variants_plot_two.png')

    # 5. plot_combined_ratio (from plot_4.py)
    plot_combined_ratio(VARIANTS_DIR, OUTPUT_DIR, FIGURES_DIR / 'DNAzipOptimization_Ratio.png')

    # 6. plot_grouped_compression_n_variants (from plot_5.py)
    plot_grouped_compression_n_variants(VARIANTS_DIR, OUTPUT_DIR, FIGURES_DIR / 'DNAzipOptimization_N.png')

    # 7. all_compression_comparisons_vcf_dnazip (from super.py)
    all_compression_comparisons_vcf_dnazip(
        genome_file_paths_ordered, 
        huffman_bin_paths_ordered, 
        biocomp_bin_paths_ordered, 
        var_file_paths_ordered, 
        dnazip_bin_paths_ordered, 
        FIGURES_DIR / 'DNAzipCompare.png'
    )

    # 8. compare_ash_triplets (from super.py)
    compare_ash_triplets(ash_bin_paths, FIGURES_DIR / 'ash_comparison.png')
    
    # 9. all_compression_comparisons_huff_bio_dnazip (from super_copy.py)
    all_compression_comparisons_huff_bio_dnazip(
        genome_file_paths_ordered, 
        huffman_bin_paths_ordered, 
        biocomp_bin_paths_ordered, 
        var_file_paths_ordered, 
        dnazip_bin_paths_ordered, 
        FIGURES_DIR / 'AlgorithmCompare.png'
    )

    print("All plots generated.")

if __name__ == "__main__":
    main()

