import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Import seaborn for better aesthetics
import numpy as np
import os
from config import *
from pathlib import Path
import sys
from typing import Union

# --- PART 1: Data Loading and Processing ---
# (Functions load_raw_data, process_for_space_savings_plot,
#  process_for_time_plot, process_for_filesize_plot are unchanged)

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
    """
    required_cols = {'variant_name', 'k_mer_size', 'time_type', 'time (sec)'}
    if not required_cols.issubset(df.columns):
        print(f"Error: DataFrame is missing columns for time plot. "
              f"Must contain: {required_cols}", file=sys.stderr)
        return pd.DataFrame()

    df_filtered = df[df['time_type'].isin(['CPU'])].copy()
    df_agg = df_filtered.groupby(['variant_name', 'k_mer_size', 'time_type'])['time (sec)'].mean().reset_index()
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
# (Functions get_avg_size_gb, get_total_size_gb are unchanged)

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
            print(f"Error: File not found at {file_path}", file=sys.stderr)
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
            print(f"Error: File not found at {file_path}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            return None
            
    if files_found == 0:
        print("Error: No files found for total calculation.", file=sys.stderr)
        return None
        
    total_gb = total_bytes / (1024**3) # Convert bytes to Gigabytes
    return total_gb


# --- PART 2: Plotting Functions (Refactored) ---

def plot_space_savings(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots space savings vs. k-mer size using sns.lineplot for a cleaner look
    and saves the figure to a file.
    
    Args:
        df_agg: The aggregated DataFrame from process_for_space_savings_plot.
        output_path: The file path to save the resulting plot image.
    """
    if df_agg.empty:
        print("Cannot plot: No space savings data to plot.", file=sys.stderr)
        return

    # 1. Create the plot
    fig, ax = plt.subplots(figsize=(11, 7))

    # Get a list of unique k-mer sizes for setting x-ticks
    k_mer_sizes = sorted(df_agg['k_mer_size'].unique())

    # 2. Use sns.lineplot()
    # This automatically handles looping, colors, markers, and the legend.
    sns.lineplot(
        data=df_agg,
        x='k_mer_size',
        y='space_savings',
        hue='variant_name',   # Color lines by variant
        style='variant_name', # Also change line/marker style
        markers=True,
        markersize=9,
        linewidth=2.5,
        ax=ax
    )

    # 3. Customize the plot
    ax.set_xlabel('k-mer Size', fontsize=14, labelpad=10)
    ax.set_ylabel('Space Savings', fontsize=14, labelpad=10)
    
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_xticks(k_mer_sizes)

    # 4. Customize legend
    # Move legend to the side
    ax.legend(
        title='Variant',
        bbox_to_anchor=(1.03, 1), 
        loc='upper left', 
        borderaxespad=0.,
        fontsize='11'
    )
    
    # 5. Clean up appearance
    sns.despine(ax=ax) # Remove top and right spines
    plt.tight_layout()

    # 6. Save the plot
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality plot saved as {output_path}")
    
    plt.close(fig)

def plot_time_comparison_faceted_bar(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots average CPU time as a faceted bar chart.
    
    Args:
        df_agg: The aggregated DataFrame from process_for_time_plot.
        output_path: The file path to save the resulting plot image.
    """
    if df_agg.empty:
        print("Cannot plot: No aggregated time data to plot.", file=sys.stderr)
        return
        
    drop_variant = df_agg[df_agg['variant_name'] == 'Ash1_v2_CHR21.txt'].index
    df_agg.drop(drop_variant, inplace=True)
    print(df_agg)

    # Create a FacetGrid (catplot is a convenient wrapper)
    g = sns.catplot(
        data=df_agg,
        kind='bar',
        x='k_mer_size',
        y='average_time_sec',
        # hue='time_type',    # REMOVED: Data is already filtered to only 'CPU'
        col='variant_name', # Creates a new column (facet) for each genome
        height=6,           # Height of each facet
        aspect=0.8,         # Aspect ratio of each facet
        sharex=False,
        # palette=...       # REMOVED: Will use the global palette set in main
    )

    # 5. Customize the plot
    g.set_axis_labels('k-mer Size', 'Average Time (sec)')
    g.set_titles('{col_name}') # Set facet titles to the genome name
    # g.legend.set_title('Time Type') # REMOVED: No longer have a hue legend
    
    # Add a main title above all facets
    plt.suptitle('Average CPU Time by k-mer Size and Genome', y=1.03, fontsize=18)
    
    g.despine() # Remove top and right spines from each facet

    # 6. Save the plot
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality bar chart saved as {output_path}")
    
    plt.close()

def plot_ash1_file_size(df_agg: pd.DataFrame, output_path: Path) -> None:
    """
    Plots file size vs. k-mer size for *only* the 'ash1' genome,
    using sns.lineplot.
    
    Args:
        df_agg: An aggregated DataFrame from process_for_filesize_plot.
        output_path: The file path to save the resulting plot image.
    """
    
    file_size_col = 'file_size (MB)'
    
    # --- 1. Validate Data ---
    if df_agg.empty:
        print("Cannot plot: No file size data to plot.", file=sys.stderr)
        return
        
    if file_size_col not in df_agg.columns:
        print(f"Error: Cannot plot. Column '{file_size_col}' not found in DataFrame.", file=sys.stderr)
        return

    # --- 2. Filter Data ---
    ash1_data = df_agg[df_agg['variant_name'] == 'Ash1_v2_Genome.txt'].sort_values(by='k_mer_size')

    if ash1_data.empty:
        print("Cannot plot: No data found for 'Ash1_v2_Genome.txt' genome.", file=sys.stderr)
        return

    # --- 3. Set up Plot ---
    fig, ax = plt.subplots(figsize=(10, 6))
    k_mer_sizes = sorted(ash1_data['k_mer_size'].unique())

    # --- 4. Create Plot ---
    # Use sns.lineplot for a consistent look
    sns.lineplot(
        data=ash1_data,
        x='k_mer_size',
        y=file_size_col,
        marker='o',
        markersize=9,
        linewidth=2.5,
        ax=ax
    )

    # --- 5. Customize Plot ---
    ax.set_xlabel('k-mer size', fontsize=14, labelpad=10) 
    ax.set_ylabel('file size (MB)', fontsize=14, labelpad=10)
    ax.set_title('ash1 Genome: File Size vs. k-mer size', fontsize=16, pad=20)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_xticks(k_mer_sizes)
    # ax.legend(loc='best', fontsize='12') # REMOVED: Legend is redundant
    
    sns.despine(ax=ax) # Clean up spines
    plt.tight_layout()

    # --- 6. Save Plot ---
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality 'ash1' plot saved as {output_path}")
    
    plt.close(fig)
    
def plot_scaling_comparison_log(
    avg_uncompressed_gb: float, 
    avg_dnazip_variants_gb: float, 
    base_dnazip_gb: float, 
    avg_huffman_gb: float, 
    output_png: Path
) -> None:
    """
    Creates and saves the scaling plot using Seaborn on a log scale.
    """
    # 1. Create the data
    num_genomes = np.arange(1, 51)
    y_uncompressed = num_genomes * avg_uncompressed_gb
    y_huffman = num_genomes * avg_huffman_gb
    y_dnazip = (num_genomes * avg_dnazip_variants_gb) + base_dnazip_gb
    
    # 2. Assemble into a DataFrame
    df_plot = pd.DataFrame({
        'Number of Genomes': num_genomes,
        'Uncompressed': y_uncompressed,
        'Huffman k=8': y_huffman,
        'DNAZip': y_dnazip
    })
    
    # 3. Melt the DataFrame for Seaborn
    df_melted = df_plot.melt(
        'Number of Genomes', 
        var_name='Method', 
        value_name='Total Storage Size (GB)'
    )
    
    # 4. Create the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 5. Plot with sns.lineplot
    sns.lineplot(
        data=df_melted,
        x='Number of Genomes',
        y='Total Storage Size (GB)',
        hue='Method',
        style='Method', # Vary line style and markers
        markers=True,
        markersize=8,
        linewidth=2,
        ax=ax
    )
    
    # 6. Customize the plot
    ax.set_title('Storage Scaling by Number of Genomes', fontsize=16, fontweight='bold')
    ax.set_xlabel('Number of Genomes (x)', fontsize=14)
    
    # --- LOG SCALE MODIFICATIONS ---
    ax.set_ylabel('Total Storage Size (GB) [log scale]', fontsize=14)
    ax.set_yscale('log')
    # --- END MODIFICATIONS ---
    
    ax.legend(fontsize=12, loc='upper left', title='Method')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    
    sns.despine(ax=ax)
    plt.tight_layout()
    
    # 7. Save the plot
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"\nScaling plot (log scale) saved as {output_png}")
    
    plt.close(fig)

def plot_scaling_comparison(
    avg_uncompressed_gb: float, 
    avg_dnazip_variants_gb: float, 
    base_dnazip_gb: float, 
    avg_huffman_gb: float, 
    output_png: Path
) -> None:
    """
    Creates and saves the scaling plot using Seaborn on a linear scale.
    """
    # 1. Create the data
    num_genomes = np.arange(1, 51)
    y_uncompressed = num_genomes * avg_uncompressed_gb
    y_huffman = num_genomes * avg_huffman_gb
    y_dnazip = (num_genomes * avg_dnazip_variants_gb) + base_dnazip_gb
    
    # 2. Assemble into a DataFrame
    df_plot = pd.DataFrame({
        'Number of Genomes': num_genomes,
        'Uncompressed': y_uncompressed,
        'Huffman k=8': y_huffman,
        'DNAZip': y_dnazip
    })
    
    # 3. Melt the DataFrame for Seaborn
    df_melted = df_plot.melt(
        'Number of Genomes', 
        var_name='Method', 
        value_name='Total Storage Size (GB)'
    )
    
    # 4. Create the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 5. Plot with sns.lineplot
    sns.lineplot(
        data=df_melted,
        x='Number of Genomes',
        y='Total Storage Size (GB)',
        hue='Method',
        style='Method', # Vary line style and markers
        markers=True,
        markersize=8,
        linewidth=2,
        ax=ax
    )
    
    # 6. Customize the plot
    ax.set_title('Storage Scaling by Number of Genomes', fontsize=16, fontweight='bold')
    ax.set_xlabel('Number of Genomes (x)', fontsize=14)
    ax.set_ylabel('Total Storage Size (GB) (y)', fontsize=14)
    
    ax.legend(fontsize=12, loc='upper left', title='Method')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    sns.despine(ax=ax)
    plt.tight_layout()
    
    # 7. Save the plot
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches='tight')
    print(f"\nScaling plot (linear scale) saved as {output_png}")
    
    plt.close(fig)

if __name__ == "__main__":
    
    # --- Set Global Plot Style ONCE ---
    sns.set_style("whitegrid")
    sns.set_context("talk") # Use "talk" for larger, presentation-ready fonts
    sns.set_palette("deep") # Use a modern, high-contrast color palette
    
    # --- 1. Load Raw Data ONCE ---
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

    # --- 2. Run Space Savings Plot ---
    print("\n--- Generating Space Savings plot ---")
    df_space_agg = process_for_space_savings_plot(df_raw)
    if not df_space_agg.empty:
        try:
            plot_space_savings(df_space_agg, PLOT_OUT_PATH)
        except NameError:
             print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("Skipping space savings plot due to data processing error.")

    # --- 3. Run Time Comparison Plot ---
    print("\n--- Generating Time Comparison bar chart ---")
    df_time_agg = process_for_time_plot(df_raw)
    if not df_time_agg.empty:
        try:
            BAR_PLOT_OUT_PATH = PLOT_OUT_PATH.parent / 'time_comparison_bar_chart.png'
            plot_time_comparison_faceted_bar(df_time_agg, BAR_PLOT_OUT_PATH)
        except NameError:
            print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("Skipping time comparison plot due to data processing error.")

    # --- 4. Run 'ash1' File Size Plot ---
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

    # --- 5. Run Scaling Plot ---
    # (File path definitions are unchanged)
    print("\n--- Generating Scaling Comparison plot ---")
    
    base_chr_path = Path("../dnazip/data/chr")
    base_dbsnp_path = Path("../dnazip/data/dbSNP")
    base_dnazip_path = Path("../dnazip/data/output")
    base_huffman_path = Path("output")
    uncompressed_files = [
        base_chr_path / "Ash1_v2_Genome.txt",
        base_chr_path / "PAN027_mat_v1_Genome.txt",
        base_chr_path / "T2T-CHM13v2_Genome.txt",
    ]
    dnazip_variant_files = [
        base_dnazip_path / "hg38_ash1_genome_Encoded.bin",
        base_dnazip_path / "hg38_pan027_genome_Encoded.bin",
        base_dnazip_path / "hg38_T2T-CHM13_Encoded.bin",
    ]
    huffman_files = [
        base_huffman_path / "ENCODED_Ash1_v2_Genome_K_MER_8.bin",
        base_huffman_path / "ENCODED_PAN027_mat_v1_Genome_K_MER_8.bin",
        base_huffman_path / "ENCODED_T2T-CHM13v2_Genome_K_MER_8.bin",
    ]
    chr_fa_files = [
        base_chr_path / "chr1.fa", base_chr_path / "chr2.fa",
        base_chr_path / "chr3.fa", base_chr_path / "chr4.fa",
        base_chr_path / "chr5.fa", base_chr_path / "chr6.fa",
        base_chr_path / "chr7.fa", base_chr_path / "chr8.fa",
        base_chr_path / "chr9.fa", base_chr_path / "chr10.fa",
        base_chr_path / "chr11.fa", base_chr_path / "chr12.fa",
        base_chr_path / "chr13.fa", base_chr_path / "chr14.fa",
        base_chr_path / "chr15.fa", base_chr_path / "chr16.fa",
        base_chr_path / "chr17.fa", base_chr_path / "chr18.fa",
        base_chr_path / "chr19.fa", base_chr_path / "chr20.fa",
        base_chr_path / "chr21.fa", base_chr_path / "chr22.fa",
        base_chr_path / "chrX.fa", base_chr_path / "chrY.fa",
    ]
    dbsnp_txt_files = [
        base_dbsnp_path / "chr1.txt", base_dbsnp_path / "chr2.txt",
        base_dbsnp_path / "chr3.txt", base_dbsnp_path / "chr4.txt",
        base_dbsnp_path / "chr5.txt", base_dbsnp_path / "chr6.txt",
        base_dbsnp_path / "chr7.txt", base_dbsnp_path / "chr8.txt",
        base_dbsnp_path / "chr9.txt", base_dbsnp_path / "chr10.txt",
        base_dbsnp_path / "chr11.txt", base_dbsnp_path / "chr12.txt",
        base_dbsnp_path / "chr13.txt", base_dbsnp_path / "chr14.txt",
        base_dbsnp_path / "chr15.txt", base_dbsnp_path / "chr16.txt",
        base_dbsnp_path / "chr17.txt", base_dbsnp_path / "chr18.txt",
        base_dbsnp_path / "chr19.txt", base_dbsnp_path / "chr20.txt",
        base_dbsnp_path / "chr21.txt", base_dbsnp_path / "chr22.txt",
        base_dbsnp_path / "chrX.txt", base_dbsnp_path / "chrY.txt",
    ]

    # --- Calculate all components ---
    
    print("--- Calculating Uncompressed Average ('m') ---")
    avg_uncompressed = get_avg_size_gb(uncompressed_files)

    print("\n--- Calculating Huffman k=8 Average ('m') ---")
    avg_huffman = get_avg_size_gb(huffman_files)
    
    print("\n--- Calculating DNAZip Variant Average ('m') ---")
    avg_dnazip_variants = get_avg_size_gb(dnazip_variant_files)

    print("\n--- Calculating DNAZip Base Size ('b') ---")
    base_dnazip = get_total_size_gb(chr_fa_files + dbsnp_txt_files)

    # --- Create plot if all data is available ---
    if all([avg_uncompressed, avg_huffman, avg_dnazip_variants, base_dnazip]):
        try:
            SCALING_PLOT_PATH     = PLOT_OUT_PATH.parent / 'genome_scaling_plot.png'
            SCALING_PLOT_PATH_LOG = PLOT_OUT_PATH.parent / 'genome_scaling_plot_log.png'
            plot_scaling_comparison(
                avg_uncompressed, 
                avg_dnazip_variants, 
                base_dnazip, 
                avg_huffman, 
                SCALING_PLOT_PATH
            )
            plot_scaling_comparison_log(
                avg_uncompressed, 
                avg_dnazip_variants, 
                base_dnazip, 
                avg_huffman, 
                SCALING_PLOT_PATH_LOG
            )
        except NameError:
            print("Skipping plot: PLOT_OUT_PATH not defined in config.py", file=sys.stderr)
    else:
        print("\nScaling plot generation skipped.", file=sys.stderr)
        print("One or more file averages/totals could not be calculated.", file=sys.stderr)
        print("Please check that all files exist, especially the 'dbsnp_txt_files' placeholders.", file=sys.stderr)

    print("\nAll plotting complete.")