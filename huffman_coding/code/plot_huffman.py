import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Still used for line plots
import numpy as np
import os
from config import * # Assuming config.py defines TIME_CSV_PATH etc.
from pathlib import Path
import sys
from typing import Union
import matplotlib.patches as mpatches # Added for complex legend

# --- PART 1: Data Loading and Processing ---

def load_raw_data(csv_path: Path) -> pd.DataFrame:
    """
    Loads the raw comparison data from a single CSV file.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}", file=sys.stderr)
        return pd.DataFrame()  # Return an empty DataFrame
    except Exception as e:
        print(f"Error loading CSV: {e}", file=sys.stderr)
        return pd.DataFrame()
    
    print(f"Successfully loaded raw data from {csv_path}")
    return df

def process_for_space_savings_plot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates data for the space savings plot.
    """
    required_cols = {'variant_name', 'k_mer_size', 'space_savings'}
    if not required_cols.issubset(df.columns):
        print(f"Error: DataFrame is missing columns for space savings plot. "
              f"Must contain: {required_cols}", file=sys.stderr)
        return pd.DataFrame()

    df_agg = df.groupby(['variant_name', 'k_mer_size'])['space_savings'].mean().reset_index()
    return df_agg

def process_for_time_plot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates data for the time comparison plot.
    Filters for 'ENCODE' and 'DECODE' types and 'CPU' time_type.
    """
    required_cols = {'variant_name', 'k_mer_size', 'type', 'time_type', 'time (sec)'}
    if not required_cols.issubset(df.columns):
        print(f"Error: DataFrame is missing columns for time plot. "
              f"Must contain: {required_cols}", file=sys.stderr)
        return pd.DataFrame()

    df_filtered = df[
        (df['type'].isin(['ENCODE', 'DECODE'])) &
        (df['time_type'] == 'CPU')
    ].copy()
    
    if df_filtered.empty:
        print("Warning: No 'ENCODE' or 'DECODE' with time_type 'CPU' data found.", file=sys.stderr)
        return pd.DataFrame()
        
    # Group by variant, k_mer, and the operation type (ENCODE/DECODE)
    df_agg = df_filtered.groupby(['variant_name', 'k_mer_size', 'type'])['time (sec)'].mean().reset_index()
    df_agg = df_agg.rename(columns={'time (sec)': 'average_time_sec'})
    
    return df_agg

def process_for_filesize_plot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates data for the file size plot.
    """
    file_size_col = 'file_size (MB)'
    required_cols = {'variant_name', 'k_mer_size', file_size_col}
    
    if not required_cols.issubset(df.columns):
        print(f"Error: DataFrame is missing columns for file size plot. "
              f"Must contain: {required_cols}", file=sys.stderr)
        return pd.DataFrame()

    df_agg = df.groupby(['variant_name', 'k_mer_size'])[file_size_col].mean().reset_index()
    return df_agg

# --- Utility Functions for Scaling Plot ---

def get_avg_size_gb(file_paths: list[Path]) -> Union[float, None]:
    """
    Calculates the *average* file size in Gigabytes (GB) for a list of files.
    Used for calculating the marginal cost 'm'.
    """
    total_bytes = 0
    file_count = 0
    
    for file_path in file_paths:
        try:
            file_bytes = os.path.getsize(file_path)
            total_bytes += file_bytes
            file_count += 1
            print(f"Found (for avg): {file_path.name}: {file_bytes / (1024**3):.4f} GB")
        except FileNotFoundError:
            print(f"Error: File not found at {file_path.resolve()}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            return None
            
    if file_count == 0:
        print("Error: No files found for average calculation.", file=sys.stderr)
        return None
        
    avg_bytes = total_bytes / file_count
    avg_gb = avg_bytes / (1024**3) # Convert bytes to Gigabytes
    return avg_gb

def get_total_size_gb(file_paths: list[Path]) -> Union[float, None]:
    """
    Calculates the *total* file size in Gigabytes (GB) for a list of files.
    Used for calculating the base cost 'b'.
    """
    total_bytes = 0
    files_found = 0
    
    for file_path in file_paths:
        try:
            file_bytes = os.path.getsize(file_path)
            total_bytes += file_bytes
            files_found += 1
            print(f"Found (for total): {file_path.name}: {file_bytes / (1024**3):.4f} GB")
        except FileNotFoundError:
            print(f"Error: File not found at {file_path.resolve()}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            return None
            
    if files_found == 0:
        print("Error: No files found for total calculation.", file=sys.stderr)
        return None
        
    total_gb = total_bytes / (1024**3) # Convert bytes to Gigabytes
    return total_gb


# --- PART 2: Plotting Functions ---

def plot_space_savings(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots space savings vs. k-mer size using sns.lineplot.
    
    Args:
        df_agg: The aggregated DataFrame from process_for_space_savings_plot.
        output_path: The file path to save the resulting plot image.
    """
    if df_agg.empty:
        print("Cannot plot: No space savings data to plot.", file=sys.stderr)
        return

    fig, ax = plt.subplots(figsize=(11, 7))

    k_mer_sizes = sorted(df_agg['k_mer_size'].unique())

    sns.lineplot(
        data=df_agg,
        x='k_mer_size',
        y='space_savings',
        hue='variant_name',
        style='variant_name',
        markers=True,
        markersize=9,
        linewidth=2.5,
        ax=ax
    )

    ax.set_xlabel('k-mer Size', fontsize=14, labelpad=10)
    ax.set_ylabel('Space Savings', fontsize=14, labelpad=10)
    
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_xticks(k_mer_sizes)

    ax.legend(
        title='Variant',
        loc='upper left', 
        fontsize='11',
        frameon=True
    )
    
    sns.despine(ax=ax) 
    plt.tight_layout(pad=1.0) 

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality plot saved as {output_path}")
    
    plt.close(fig)

def plot_time_comparison_grouped_bar(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots average CPU time as a grouped STACKED bar chart.
    
    X-axis: Variant Name
    Groups: k-mer Size (differentiated by hatch)
    Stacks: Encoding Time and Decoding Time (differentiated by color)
    
    Args:
        df_agg: The aggregated DataFrame from process_for_time_plot.
        output_path: The file path to save the resulting plot image.
    """
    if df_agg.empty:
        print("Cannot plot: No aggregated time data to plot.", file=sys.stderr)
        return
        
    # Drop the 'CHR21' variant if it exists
    drop_variant_mask = df_agg['variant_name'].str.contains('CHR21')
    if drop_variant_mask.any():
        print(f"Dropping variants: {df_agg[drop_variant_mask]['variant_name'].unique()}")
        df_agg = df_agg[~drop_variant_mask].copy()
        
    if df_agg.empty:
        print("Cannot plot: No data remaining after filtering.", file=sys.stderr)
        return

    x_labels = sorted(df_agg['variant_name'].unique())
    k_mers = sorted(df_agg['k_mer_size'].unique())
    
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    encode_color = colors[0]
    decode_color = colors[1]
    hatches = ['/', '\\', 'x', '.', 'o', '+', '*'] 
    
    encode_data = {k: [] for k in k_mers}
    decode_data = {k: [] for k in k_mers}
    all_times_for_max = [] 
    
    print("--- Collecting Stacked Time Data ---")

    for variant in x_labels:
        print(f"\nProcessing: {variant}")
        
        for k_mer in k_mers:
            # Get Encode Time
            encode_val = df_agg[
                (df_agg['variant_name'] == variant) & 
                (df_agg['k_mer_size'] == k_mer) &
                (df_agg['type'] == 'ENCODE')  # Use 'type' column
            ]['average_time_sec'].values
            
            # Get Decode Time
            decode_val = df_agg[
                (df_agg['variant_name'] == variant) & 
                (df_agg['k_mer_size'] == k_mer) &
                (df_agg['type'] == 'DECODE')  # Use 'type' column
            ]['average_time_sec'].values
            
            encode_sec = encode_val[0] if len(encode_val) > 0 else np.nan
            decode_sec = decode_val[0] if len(decode_val) > 0 else np.nan
            
            encode_data[k_mer].append(encode_sec)
            decode_data[k_mer].append(decode_sec)

            if not np.isnan(encode_sec) and not np.isnan(decode_sec):
                print(f"  Found k={k_mer} (Encode: {encode_sec:.2f}s, Decode: {decode_sec:.2f}s)")
                all_times_for_max.append(encode_sec + decode_sec)
            else:
                print(f"  NOT FOUND: k={k_mer} (Encode or Decode missing)")

    df_plot_enc = pd.DataFrame(encode_data, index=x_labels)
    df_plot_dec = pd.DataFrame(decode_data, index=x_labels)
    print("\n--- Final Encode Data for Plotting (sec) ---")
    print(df_plot_enc.to_markdown(numalign="left", stralign="left", floatfmt=".2f"))
    print("\n--- Final Decode Data for Plotting (sec) ---")
    print(df_plot_dec.to_markdown(numalign="left", stralign="left", floatfmt=".2f"))

    plt.figure(figsize=(16, 8))
    
    num_variants = len(x_labels)
    num_bars = len(k_mers)
    
    x = np.arange(num_variants)
    width = 0.8 / num_bars 
    offsets = np.linspace(-width * (num_bars / 2 - 0.5), width * (num_bars / 2 - 0.5), num_bars)

    for i, k_mer in enumerate(k_mers):
        encode_times = np.array(encode_data[k_mer])
        decode_times = np.array(decode_data[k_mer])
        
        total_times = encode_times + decode_times 
        
        encode_plot = np.nan_to_num(encode_times)
        decode_plot = np.nan_to_num(decode_times)
        
        hatch_pattern = hatches[i % len(hatches)]
        
        # Plot Encode (bottom) bar
        plt.bar(
            x + offsets[i], 
            encode_plot, 
            color=encode_color, 
            width=width, 
            edgecolor='black', 
            linewidth=1, 
            hatch=hatch_pattern
        )
        
        # Plot Decode (top) bar
        bar_container = plt.bar(
            x + offsets[i], 
            decode_plot, 
            bottom=encode_plot, 
            color=decode_color, 
            width=width, 
            edgecolor='black', 
            linewidth=1, 
            hatch=hatch_pattern
        )
        
        # Add labels for the *total* time on top of the stack
        plt.bar_label(
            bar_container, 
            labels=[f'{t:.2f}' if not np.isnan(t) else '' for t in total_times],
            fontsize=8, 
            padding=3
        )

    plt.xlabel("Variant", fontsize=14, labelpad=15)
    plt.ylabel("Average CPU Time (sec)", fontsize=14, labelpad=15)
    
    short_x_labels = [l.replace('.txt', '').replace('_Genome', '') for l in x_labels]
    plt.xticks(x, short_x_labels, fontsize=11, rotation=10)
    plt.yticks(fontsize=12)
    
    if all_times_for_max:
        current_max = max(all_times_for_max)
        plt.ylim(top=current_max * 1.15) 
    
    # Create Dual Legend
    color_patches = [
        mpatches.Patch(color=encode_color, label='Encode'),
        mpatches.Patch(color=decode_color, label='Decode')
    ]
    leg1 = plt.legend(
        handles=color_patches, 
        title="Time Type", 
        fontsize=12, 
        loc='upper left',
        frameon=True
    )
    
    plt.gca().add_artist(leg1)

    hatch_patches = [
        mpatches.Patch(facecolor='white', edgecolor='black', hatch=hatches[i % len(hatches)], label=f'k = {k_mer}') 
        for i, k_mer in enumerate(k_mers)
    ]
    plt.legend(
        handles=hatch_patches, 
        title="k-mer Size", 
        fontsize=12, 
        loc='upper right',
        frameon=True
    )

    plt.tight_layout(pad=1.0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nGrouped stacked bar plot saved successfully to {output_path}")
    plt.close()

def plot_ash1_file_size(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots file size vs. k-mer size for *only* the 'ash1' genome,
    using sns.lineplot.
    
    Filters out 0-value/NA points, then treats the remaining
    k-mer sizes as categorical.
    
    Args:
        df_agg: An aggregated DataFrame from process_for_filesize_plot.
        output_path: The file path to save the resulting plot image.
    """
    
    file_size_col = 'file_size (MB)'
    
    if df_agg.empty:
        print("Cannot plot: No file size data to plot.", file=sys.stderr)
        return
        
    if file_size_col not in df_agg.columns:
        print(f"Error: Cannot plot. Column '{file_size_col}' not found in DataFrame.", file=sys.stderr)
        return

    ash1_data = df_agg[df_agg['variant_name'].str.contains('Ash1_v2_Genome', case=False)].copy()

    ash1_data_filtered = ash1_data[ash1_data[file_size_col] > 0].sort_values(by='k_mer_size')
    
    if ash1_data_filtered.empty:
        print("Cannot plot: No data found for 'Ash1' genome after filtering 0/NaN values.", file=sys.stderr)
        return
        
    ash1_name = ash1_data_filtered['variant_name'].iloc[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    
    ash1_data_filtered['k_mer_size_cat'] = ash1_data_filtered['k_mer_size'].astype(str)

    print("\n--- Plotting 'ash1' file size with this filtered data: ---")
    print(ash1_data_filtered[['k_mer_size', 'k_mer_size_cat', file_size_col]].to_markdown(index=False))

    sns.lineplot(
        data=ash1_data_filtered,
        x='k_mer_size_cat', 
        y=file_size_col,
        marker='o',
        markersize=9,
        linewidth=2.5,
        ax=ax,
        sort=False
    )

    ax.set_xlabel('k-mer size', fontsize=14, labelpad=10) 
    ax.set_ylabel('file size (MB)', fontsize=14, labelpad=10)
    ax.set_title(f'{ash1_name}: File Size vs. k-mer size', fontsize=16, pad=20)
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    sns.despine(ax=ax) 
    plt.tight_layout(pad=1.0) 

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality 'ash1' plot saved as {output_path}")
    
    plt.close(fig)
    
def plot_scaling_comparison_log(
    avg_uncompressed_gb: float, 
    avg_dnazip_variants_gb: float, 
    base_dnazip_gb: float, 
    avg_huffman_gb: float, 
    avg_biocompress_gb: float,
    output_png: Path,
    max_genomes: int = 1000
) -> None:
    """
    Creates and saves the scaling plot using Seaborn on a log-log scale.
    """
    
    num_genomes = np.logspace(0, np.log10(max_genomes), num=50) 
    
    y_uncompressed = num_genomes * avg_uncompressed_gb
    y_huffman = num_genomes * avg_huffman_gb
    y_dnazip = (num_genomes * avg_dnazip_variants_gb) + base_dnazip_gb
    y_biocompress = num_genomes * avg_biocompress_gb
    
    df_plot = pd.DataFrame({
        'Number of Genomes': num_genomes,
        'Uncompressed': y_uncompressed,
        'Huffman k=8': y_huffman,
        'DNAZip': y_dnazip,
        'Biocompress': y_biocompress
    })
    
    df_melted = df_plot.melt(
        'Number of Genomes', 
        var_name='Method', 
        value_name='Total Storage Size (GB)'
    )
    
    fig, ax = plt.subplots(figsize=(9, 7))
    
    sns.lineplot(
        data=df_melted,
        x='Number of Genomes',
        y='Total Storage Size (GB)',
        hue='Method',
        style='Method',
        markers=True,
        markersize=8,
        linewidth=2,
        ax=ax
    )
    
    ax.set_title('Storage Scaling by Number of Genomes', fontsize=16)
    
    ax.set_xlabel('Number of Genomes [log scale]', fontsize=14, labelpad=10)
    ax.set_ylabel('Total Storage Size (GB) [log scale]', fontsize=14, labelpad=10)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.legend(
        fontsize=12, 
        loc='upper left', 
        title='Method',
        frameon=True
    )
    
    sns.despine(ax=ax)
    plt.tight_layout(pad=1.0) 
    
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"\nScaling plot (log-log scale) saved as {output_png}")
    
    plt.close(fig)

def plot_scaling_comparison(
    avg_uncompressed_gb: float, 
    avg_dnazip_variants_gb: float, 
    base_dnazip_gb: float, 
    avg_huffman_gb: float, 
    avg_biocompress_gb: float,
    output_png: Path
) -> None:
    """
    Creates and saves the scaling plot using Seaborn on a linear scale.
    """
    num_genomes = np.arange(1, 9)
    y_uncompressed = num_genomes * avg_uncompressed_gb
    y_huffman = num_genomes * avg_huffman_gb
    y_dnazip = (num_genomes * avg_dnazip_variants_gb) + base_dnazip_gb
    y_biocompress = num_genomes * avg_biocompress_gb
    
    df_plot = pd.DataFrame({
        'Number of Genomes': num_genomes,
        'Uncompressed': y_uncompressed,
        'Huffman k=8': y_huffman,
        'DNAZip': y_dnazip,
        'Biocompress': y_biocompress
    })
    
    df_melted = df_plot.melt(
        'Number of Genomes', 
        var_name='Method', 
        value_name='Total Storage Size (GB)'
    )
    
    fig, ax = plt.subplots(figsize=(9, 7))
    
    sns.lineplot(
        data=df_melted,
        x='Number of Genomes',
        y='Total Storage Size (GB)',
        hue='Method',
        style='Method',
        markers=True,
        markersize=8,
        linewidth=2,
        ax=ax
    )
    
    ax.set_title('Storage Scaling by Number of Genomes', fontsize=16)
    ax.set_xlabel('Number of Genomes (x)', fontsize=14, labelpad=10)
    ax.set_ylabel('Total Storage Size (GB) (y)', fontsize=14, labelpad=10)
    
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.legend(
        fontsize=12, 
        loc='upper left', 
        title='Method',
        frameon=True
    )
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    sns.despine(ax=ax)
    plt.tight_layout(pad=1.0) 
    
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"\nScaling plot (linear scale) saved as {output_png}")
    
    plt.close(fig)


if __name__ == "__main__":
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    try:
        df_raw = load_raw_data(TIME_CSV_PATH)
    except NameError:
        print("Error: TIME_CSV_PATH not defined. Check config.py.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
        
    if df_raw.empty:
        print("Failed to load raw data. Exiting.", file=sys.stderr)
        sys.exit(1)

    print("\n--- Generating Space Savings plot ---")
    df_space_agg = process_for_space_savings_plot(df_raw)
    if not df_space_agg.empty:
        try:
            plot_space_savings(df_space_agg, PLOT_OUT_PATH)
        except NameError:
             print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("Skipping space savings plot due to data processing error.")

    print("\n--- Generating Time Comparison grouped bar chart ---")
    df_time_agg = process_for_time_plot(df_raw)
    if not df_time_agg.empty:
        try:
            BAR_PLOT_OUT_PATH = PLOT_OUT_PATH.parent / 'time_comparison_grouped_bar.png'
            plot_time_comparison_grouped_bar(df_time_agg, BAR_PLOT_OUT_PATH)
        except NameError:
            print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("Skipping time comparison plot due to data processing error.")

    print("\n--- Generating 'ash1' File Size plot ---")
    df_filesize_agg = process_for_filesize_plot(df_raw)
    if not df_filesize_agg.empty:
        try:
            ASH1_PLOT_PATH = PLOT_OUT_PATH.parent / 'ash1_file_size_plot.png'
            plot_ash1_file_size(df_filesize_agg, ASH1_PLOT_PATH)
        except NameError:
            print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("Skipping 'ash1' file size plot due to data processing error.")

    print("\n--- Generating Scaling Comparison plot ---")
    
    # Define BASE_PATH
    try:
        BASE_PATH = Path(__file__).resolve().parent.parent.parent
    except NameError:
        print("WARNING: '__file__' is not defined. Using Path.cwd() as fallback.")
        print("You may need to manually adjust BASE_PATH if this is incorrect.")
        BASE_PATH = Path.cwd().parent 

    # --- Adjusted Base Paths ---
    # Paths based on BASE_PATH variable

    try:
        # Paths for DNAZip components
        base_chr_path = BASE_PATH / 'dnazip' / 'data' / 'chr'
        base_dbsnp_path = BASE_PATH / 'dnazip' / 'data' / 'dbSNP'
        base_dnazip_path = BASE_PATH / 'dnazip' / 'data' / 'output'
        
        # Path for standalone Huffman
        base_huffman_path = BASE_PATH / 'huffman_coding' / 'output' / 'data'
        
        # Path for Biocompress
        base_biocompress_path = BASE_PATH / 'biocompress_1' / 'data'        
        
        # --- File Lists ---
        
        uncompressed_files = [
            base_chr_path / "Han1_Genome.txt",
            base_chr_path / "PAN027_mat_v1_Genome.txt",
            base_chr_path / "T2T-CHM13v2_Genome.txt",
        ]
        
        dnazip_variant_files = [
            base_dnazip_path / "hg38_Han1_genome_True_True_True_8_Encoded.bin",
            base_dnazip_path / "hg38_pan027_genome_True_True_True_8_Encoded.bin",
            base_dnazip_path / "hg38_T2T-CHM13_genome_True_True_True_8_Encoded.bin",
        ]
        
        huffman_files = [
            base_huffman_path / "ENCODED_Han1_Genome_K_MER_8.bin",
            base_huffman_path / "ENCODED_PAN027_mat_v1_Genome_K_MER_8.bin",
            base_huffman_path / "ENCODED_T2T-CHM13v2_Genome_K_MER_8.bin",
        ]
        
        biocompress_files = [
            base_biocompress_path / "Han1_Genome_13.bin",
            base_biocompress_path / "PAN027_mat_v1_Genome_13.bin",
            base_biocompress_path / "T2T-CHM13v2_Genome_13.bin",
        ]
        
        chr_fa_files = [ base_chr_path / f"chr{i}.fa" for i in list(range(1, 23)) + ['X', 'Y'] ]
        dbsnp_txt_files = [ base_dbsnp_path / f"chr{i}.txt" for i in list(range(1, 23)) + ['X', 'Y'] ]
        
    except Exception as e:
        print(f"Error defining file paths for scaling plot: {e}", file=sys.stderr)
        sys.exit(1)


    print("--- Calculating Uncompressed Average ('m') ---")
    avg_uncompressed = get_avg_size_gb(uncompressed_files)

    print("\n--- Calculating Huffman k=8 Average ('m') ---")
    avg_huffman = get_avg_size_gb(huffman_files)
    
    print("\n--- Calculating DNAZip Variant Average ('m') ---")
    avg_dnazip_variants = get_avg_size_gb(dnazip_variant_files)
    
    print("\n--- Calculating Biocompress Average ('m') ---")
    avg_biocompress = get_avg_size_gb(biocompress_files)

    print("\n--- Calculating DNAZip Base Size ('b') ---")
    base_dnazip = get_total_size_gb(chr_fa_files + dbsnp_txt_files)

    if all([avg_uncompressed, avg_huffman, avg_dnazip_variants, base_dnazip, avg_biocompress]):
        try:
            SCALING_PLOT_PATH     = PLOT_OUT_PATH.parent / 'genome_scaling_plot.png'
            SCALING_PLOT_PATH_LOG = PLOT_OUT_PATH.parent / 'genome_scaling_plot_log.png'
            
            plot_scaling_comparison(
                avg_uncompressed, 
                avg_dnazip_variants, 
                base_dnazip, 
                avg_huffman, 
                avg_biocompress,
                SCALING_PLOT_PATH
            )
            
            plot_scaling_comparison_log(
                avg_uncompressed, 
                avg_dnazip_variants, 
                base_dnazip, 
                avg_huffman, 
                avg_biocompress,
                SCALING_PLOT_PATH_LOG,
                max_genomes=10000
            )
        except NameError:
            print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("\nScaling plot generation skipped.", file=sys.stderr)
        print("One or more file averages/totals could not be calculated.", file=sys.stderr)
        print("Please check that all files exist.", file=sys.stderr)

    print("\nAll plotting complete.")