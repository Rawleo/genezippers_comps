import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from dnazip.code.helper.bitfile import export_as_binary
from config import DNA_FILE_PATH, DNA_FILE, HEIGHT
import time

open(DNA_FILE_PATH + DNA_FILE + "_" + str(HEIGHT) + ".bin", "w").close()

def main():
    print("=== Starting pipeline ===")

    print("Step 1: Running compress.py")
    start=time.time()
    subprocess.run(["python", "compressor.py"], check=True)
    end=time.time()
    print(f"Elapsed time: {end - start:.2f} seconds")

    with open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "r") as file:
        textFile = file.read()
    export_as_binary(DNA_FILE_PATH + DNA_FILE  + "_" + str(HEIGHT) + ".bin", textFile)

    print("Step 2: Running decompress.py")
    start=time.time()
    subprocess.run(["python", "decompressor.py"], check=True)
    end=time.time()
    print(f"Elapsed time: {end - start:.2f} seconds")

    print("=== Pipeline complete ===")

if __name__ == "__main__":
    main()