from pathlib import Path
import time, json, subprocess, sys, csv, os
sys.path.append(str(Path(__file__).resolve().parent.parent))
from dnazip.code.bitfile import export_as_binary
from config import DNA_FILE_PATH, DNA_FILE, HEIGHT, DNA_FILE_TXT

bin_file_path = DNA_FILE_PATH + DNA_FILE + "_" + str(HEIGHT) + ".bin"
original_file_path = DNA_FILE_PATH+DNA_FILE_TXT
open(bin_file_path, "w").close()

FIELD_NAMES = [
    "genome",
    "tree_height",
    "tree_memory",
    "total_compression_time",
    "tree_creation_time",
    "compressor_time",
    "compression_ratio",
    "space_savings",
    "original_file_size",
    "encoded_file_size",
]

def file_size(file_path):

    return os.path.getsize(file_path) / (2 ** 20)


def compression_ratio(orig_file_path, enc_file_path):

    orig_file_size = file_size(orig_file_path)
    enc_file_size = file_size(enc_file_path)

    return round(enc_file_size / orig_file_size, 4), orig_file_size, enc_file_path

def print_metrics(data):
    csv_filepath = "./data.csv"
    file_exists = os.path.isfile(csv_filepath)
    with open(csv_filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)

        # If file doesn't exist yet, write the header first
        if not file_exists:
            writer.writeheader()

        # Append a new row
        writer.writerow(data)
    return 0

def calculate_metrics(data):
    compression_ratio_val, original_file_size, encoded_file_size = compression_ratio(original_file_path,bin_file_path)
    space_saving = 1 - compression_ratio_val
    height = HEIGHT
    genome = DNA_FILE

    data.update({
        "compression_ratio": compression_ratio_val,
        "space_savings": space_saving,
        "tree_height": height,
        "genome": genome,
        "original_file_size": original_file_size,
        "encoded_file_size": encoded_file_size
    })
    return data

def main():
    print("=== Starting pipeline ===")

    print("Step 1: Running compress.py")
    start=time.time()
    result = subprocess.run(["python", "compressor.py"], check=True, text=True, stdout=subprocess.PIPE, stderr=None)  
    compression_metrics = json.loads(result.stdout)
    end=time.time()
    print(f"Total Compression Time: {end - start:.2f} seconds")

    with open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "r") as file:
        text_file = file.read()
    export_as_binary(DNA_FILE_PATH + DNA_FILE  + "_" + str(HEIGHT) + ".bin", text_file)

    print("Step 2: Running decompress.py")
    start=time.time()
    subprocess.run(["python", "decompressor.py"], check=True)
    end=time.time()
    print(f"Total Decompression Time: {end - start:.2f} seconds")

    print("=== Pipeline complete ===")

    all_metrics = calculate_metrics(compression_metrics)
    print_metrics(all_metrics)



if __name__ == "__main__":
    main()