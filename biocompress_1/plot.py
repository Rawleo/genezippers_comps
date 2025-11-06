import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

def height_vs_memory_and_time(csv_path: str = "./data.csv"):
    # Load the CSV
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        sys.exit(f"Error: Could not find file '{csv_path}'")

    # Check if required columns exist
    required_cols = ["tree_height", "tree_creation_time", "tree_memory"]
    for col in required_cols:
        if col not in df.columns:
            sys.exit(f"Error: Missing column '{col}' in {csv_path}")

    # Drop rows with missing values
    df = df.dropna(subset=required_cols)

    # Sort by tree_height for a cleaner plot
    df = df.sort_values("tree_height")

   # Create the figure and axis
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Plot tree creation time on the left y-axis
    color1 = "royalblue"
    ax1.set_xlabel("Tree Height")
    ax1.set_ylabel("Tree Creation Time (s)", color=color1)
    ax1.plot(df["tree_height"], df["tree_creation_time"], marker="o", color=color1, label="Tree Creation Time")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # Create secondary y-axis for memory
    ax2 = ax1.twinx()
    color2 = "firebrick"
    ax2.set_ylabel("Tree Memory (MB)", color=color2)
    ax2.plot(df["tree_height"], df["tree_memory"], marker="s", linestyle="--", color=color2, label="Tree Memory")
    ax2.tick_params(axis="y", labelcolor=color2)

    # Title and layout
    plt.title("Tree Creation Time and Memory vs. Tree Height")
    fig.tight_layout()

    # Save and show
    plt.savefig("tree_creation_time_and_memory_vs_height.png", dpi=300)
    plt.show()

def height_vs_time(csv_path: str = "./data.csv", genome=None):
    # Load the CSV
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        sys.exit(f"Error: Could not find file '{csv_path}'")

    # Check required columns
    required_cols = ["tree_height", "tree_creation_time", "compressor_time"]
    for col in required_cols:
        if col not in df.columns:
            sys.exit(f"Error: Missing column '{col}' in {csv_path}")

    # Drop rows with missing values
    df = df.dropna(subset=required_cols)

    # Sort by height
    df = df.sort_values("tree_height")
    df = df.where(df['genome'] == genome).dropna()

    # Plot
    plt.figure(figsize=(10, 5))
    bar_width = 0.6

    # Stacked bars
    plt.bar(
        df["tree_height"],
        df["tree_creation_time"],
        color="#1E88E5",
        width=bar_width,
        label="Tree Creation Time"
    )
    plt.bar(
        df["tree_height"],
        df["compressor_time"],
        bottom=df["tree_creation_time"],
        color="#FFC107",
        width=bar_width,
        label="Compressor Time"
    )

    # Labels and title
    plt.xlabel("Tree Height", fontsize=14, weight='bold', labelpad=15)
    plt.ylabel("Time (s)", fontsize=14, weight='bold', labelpad=10)
    plt.title("Algorithm Runtime vs. Tree Height", fontsize=18, weight='bold', pad=10)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(loc='upper center', ncols=2)

    # Save and show
    plt.tight_layout()
    plt.savefig("tree_time_stacked_bar.png", dpi=300)
    plt.show()

def compression_comparison(csv_path="./data.csv"):
    # Read CSV
    df = pd.read_csv(csv_path)

    # Assuming one row (or taking the last if multiple)
    row = df.iloc[-1]

    genome = row["genome"]
    height = int(row["tree_height"])
    orig_size = row["original_file_size"]
    enc_size = row["encoded_file_size"]
    ratio = row["compression_ratio"]
    savings = row["space_savings"]
    file_name = row["genome"]

    # Bar chart setup
    labels = [f"{genome} (height={height})"]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))

    plt.figure(figsize=(7, 7))
    plt.bar(['Compressed File', 'Raw File'],
            height=[enc_size, orig_size],
            width=0.7,
            color=['#004D40', '#D81B60'],
            edgecolor='black',
            linewidth=3
    )

    plt.suptitle(f"Megabytes Used Per File Type ({file_name})", weight='bold', fontsize=16, linespacing=400)
    plt.title(f"Compression Ratio: {ratio} | Space Savings: {savings}", pad=20, fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("File Type", fontsize=14, labelpad=10)
    plt.ylabel("File Size (MB)", fontsize=14, labelpad=15)
    plt.tight_layout()
    plt.savefig("tree_time_stacked_bar.png", dpi=300)
    plt.show()

def main():
    # height_vs_memory_and_time()
    height_vs_time(genome='CM021588_chr21')



if __name__ == "__main__":
    main()