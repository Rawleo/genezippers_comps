#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import sys
from typing import Union

# --- PART 1: Helper Functions ---

def file_size(file_path: Path) -> float:
    """
    Gets the size of a file in Megabytes (MB).
    
    Args:
        file_path: The path to the file.

    Returns:
        The file size in MB, or np.nan if not found.
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024) # Convert bytes to MB
    except FileNotFoundError:
        # Suppress "File not found" for this version, as it's expected
        # for missing combinations. Return np.nan so it's plotted as empty.
        pass
    except Exception as e:
        print(f"Error reading size of {file_path.name}: {e}", file=sys.stderr)
        return np.nan
    return np.nan

# --- PART 2: Plotting Function ---

def plot_grouped_compression_by_variant(variants_dir: Path, output_dir: Path, output_plot_path: Path):
    """
    Creates a clustered bar chart comparing raw variant file sizes
    against the four different encoded combinations.
    
    Args:
        variants_dir: Path to the 'data/variants' directory.
        output_dir: Path to the 'data/output' directory.
        output_plot_path: The full file path to save the resulting plot.
    """
    
    # --- 1. Define Variants and Combinations ---
    
    variant_names = [
        'hg38_Han1_genome', 
        # 'hg38_ash1_genome', 
        'hg38_pan027_genome', 
        'hg38_T2T-CHM13_genome'
    ]
    
    # Define Raw Path Template Separately
    raw_path_template = variants_dir / "{variant}_sorted_variants.txt"
    
    # Remove 'Raw Variant' from plotted combinations
    combinations = {
        # 'Raw Variant': { ... } # Removed from plot
        'Baseline': {
            'path_template': output_dir / "{variant}_False_False_False_0_Encoded.bin",
            'color': '#1E88E5' # Blue
        },
        'dbSNP': {
            'path_template': output_dir / "{variant}_False_True_False_0_Encoded.bin",
            'color': '#FFC107' # Yellow
        },
        'dbSNP + Huffman (8-mer)': {
            'path_template': output_dir / "{variant}_False_True_True_8_Encoded.bin",
            'color': '#43A047' # Green
        },
        'Delta + dbSNP + Huffman (8-mer)': {
            'path_template': output_dir / "{variant}_True_True_True_8_Encoded.bin",
            'color': '#004D40' # Dark Green/Teal
        }
    }
    
    combo_names = list(combinations.keys())
    file_sizes = {name: [] for name in combo_names}
    raw_sizes_mb_list = [] # List to store raw sizes for ratio calculation
    x_labels = [] # To store the shortened variant names

    print("--- Collecting File Size Data ---")

    # --- 2. Loop Through Files and Get Sizes ---
    all_sizes_for_max = [] # To calculate plot limits
    for variant in variant_names:
        # Store the short name (e.g., 'Han1')
        x_labels.append(variant.replace('hg38_', '').replace('_genome', ''))
        print(f"\nProcessing: {variant}")
        
        # --- Get the Raw Size First ---
        raw_f_path = Path(str(raw_path_template).format(variant=variant))
        raw_size_mb = file_size(raw_f_path)
        raw_sizes_mb_list.append(raw_size_mb) # Store for ratio
        
        if not np.isnan(raw_size_mb):
            print(f"  Found Raw: {raw_f_path.name} (Size: {raw_size_mb:.2f} MB)")
        else:
            print(f"  NOT FOUND Raw: {raw_f_path.name}")
            
        # --- Get Compressed Sizes ---
        for name in combo_names:
            f_path = Path(str(combinations[name]['path_template']).format(variant=variant))
            
            size_mb = file_size(f_path)
            if not np.isnan(size_mb):
                print(f"  Found: {f_path.name} (Size: {size_mb:.2f} MB)")
                all_sizes_for_max.append(size_mb)
            else:
                 print(f"  NOT FOUND: {f_path.name}")
            
            file_sizes[name].append(size_mb) # Append size or np.nan

    # --- 3. Create DataFrame for Plotting ---
    df_plot = pd.DataFrame(file_sizes, index=x_labels)
    print("\n--- Final Data for Plotting (MB) ---")
    print(df_plot.to_markdown(numalign="left", stralign="left", floatfmt=".2f"))

    # --- 4. Create the Plot ---
    
    # ***MODIFIED***: Adjusted figsize for better aspect ratio with new header
    plt.figure(figsize=(10, 9)) 
    
    num_variants = len(x_labels)
    num_bars = len(combo_names)
    
    x = np.arange(num_variants)
    width = 0.15 
    
    # Adjust offsets to be centered around 0 for a single group
    if num_bars % 2 == 1:
        offsets = np.linspace(-width * (num_bars // 2), width * (num_bars // 2), num_bars)
    else:
        offsets = np.linspace(-width * (num_bars / 2 - 0.5), width * (num_bars / 2 - 0.5), num_bars)


    for i, name in enumerate(combo_names):
        sizes = file_sizes[name] # List of sizes for this combo (one per variant)
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
        
        # --- Calculate Compression Ratio Labels ---
        comp_labels = []
        # Loop over each variant's result for this combination
        for j in range(len(sizes)): 
            comp_s = sizes[j]          # Compressed size for variant j
            raw_s = raw_sizes_mb_list[j] # Raw size for variant j
            
            label_text = '' # Default to empty
            if not np.isnan(comp_s) and not np.isnan(raw_s) and comp_s > 0:
                ratio = raw_s / comp_s
                label_text = f'1:{ratio:.1f}'
            
            comp_labels.append(label_text)

        # --- Add compression ratio labels ---
        plt.bar_label(
            bar_container, 
            fmt='%s',
            labels=comp_labels,
            fontsize=12,
            padding=3,
        )

    # --- 5. Formatting (in the style of the example) ---
    
    # ***MODIFICATION START***
    # Create the final labels for the x-axis
    
    final_x_labels = x_labels # Default to simple names
    
    if num_variants > 1:
        # If more than one variant, create new labels with raw size
        new_labels = []
        for name, size in zip(x_labels, raw_sizes_mb_list):
            if not np.isnan(size):
                # Add newline for better formatting
                new_labels.append(f"{name}\n({size:.2f} MB)")
            else:
                new_labels.append(f"{name}\n(Size N/A)")
        final_x_labels = new_labels
        
    elif num_variants == 1 and not np.isnan(raw_sizes_mb_list[0]):
        # If only one variant, keep original behavior:
        # Add the raw size as a subtitle
        subtitle_text = f"{x_labels[0]} (Raw Size: {raw_sizes_mb_list[0]:.2f} MB)"
        # Use plt.title for the subtitle, positioned below suptitle
        plt.title(subtitle_text, fontsize=14, pad=10, loc='center')
    
    # ***MODIFICATION END***
    
    # plt.xlabel("Variant", fontsize=14, labelpad=15)
    plt.ylabel("Size (MB)", fontsize=14, labelpad=15, fontweight='bold')
    
    # ***MODIFICATION***: Use the new 'final_x_labels' list
    plt.xticks(x, final_x_labels, fontsize=12)
    plt.yticks(fontsize=12)
    
    # Adjust Y-axis limit to make space for labels AND legend
    if all_sizes_for_max:
        current_max = max(all_sizes_for_max)
        # Add padding to make room for 2-row legend
        plt.ylim(top=current_max * 1.20) 
    
    # Legend in 2 rows (max) inside the plot
    num_items = len(combo_names)
    # Calculate columns needed for 2 rows
    num_cols = int(np.ceil(num_items / 2)) 
    
    plt.legend(
        fontsize=12, 
        loc='upper center', # Place inside, at the top center
        ncol=num_cols,       # Arrange in 2 rows
        frameon=True       
    )
    
    plt.tight_layout(pad=1.0, rect=[0, 0, 1, 0.96]) # rect=[left, bottom, right, top]

    # --- 6. Save the Plot ---
    output_plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved successfully to {output_plot_path}")
    plt.close()
   
if __name__ == "__main__":
    
    # --- Set Global Plot Style ONCE ---
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # --- Define Paths ---
    
    # Define paths relative to the script's location
    # Path to the directory containing this script (dnazip/code/)
    try:
        SCRIPT_DIR = Path(__file__).resolve().parent
    except NameError:
        print("Running in an environment where __file__ is not defined. Using CWD.")
        SCRIPT_DIR = Path.cwd()

    # Path to the project root (dnazip/)
    PROJECT_ROOT = SCRIPT_DIR.parent
    
    # Base all data paths on the project root
    BASE_DIR = PROJECT_ROOT / 'data'
    VARIANTS_DIR = BASE_DIR / 'variants'
    OUTPUT_DIR = BASE_DIR / 'output'
    
    # Save to 'data/figures'
    FIGURES_DIR = BASE_DIR / 'figures'
    OUTPUT_PLOT_PATH = FIGURES_DIR / 'storage_savings_vs_variants_plot_all.png'

    # --- Run Plotting Function ---
    if not VARIANTS_DIR.is_dir() or not OUTPUT_DIR.is_dir():
        print(f"Error: Required directories 'data/variants' or 'data/output' not found.", file=sys.stderr)
        # Print the absolute paths for easier debugging
        print(f"Looked for: {VARIANTS_DIR.resolve()} and {OUTPUT_DIR.resolve()}", file=sys.stderr)
        sys.exit(1)
        
    plot_grouped_compression_by_variant(VARIANTS_DIR, OUTPUT_DIR, OUTPUT_PLOT_PATH)

    print("\nAll plotting complete.")