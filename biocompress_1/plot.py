import pandas as pd
import matplotlib.pyplot as plt
import sys

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

def height_vs_time(csv_path: str = "./data.csv"):
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

    # Plot
    plt.figure(figsize=(9, 6))
    bar_width = 0.6

    # Stacked bars
    plt.bar(
        df["tree_height"],
        df["tree_creation_time"],
        color="royalblue",
        width=bar_width,
        label="Tree Creation Time"
    )
    plt.bar(
        df["tree_height"],
        df["compressor_time"],
        bottom=df["tree_creation_time"],
        color="darkorange",
        width=bar_width,
        label="Compressor Time"
    )

    # Labels and title
    plt.xlabel("Tree Height")
    plt.ylabel("Time (seconds)")
    plt.title("Tree Creation and Compression Time vs. Tree Height")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.legend()

    # Save and show
    plt.tight_layout()
    plt.savefig("tree_time_stacked_bar.png", dpi=300)
    plt.show()


def main():
    # height_vs_memory_and_time()
    height_vs_time()



if __name__ == "__main__":
    main()