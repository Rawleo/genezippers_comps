import reader
from constants import *
from pathlib import Path  


def main():
    
    CHR_DIR    = BASE_DIR / 'data' / 'chr' 
    OUTPUT_DIR = BASE_DIR / 'data' / 'chr' / 'genome.txt'
    OUTPUT_CHR = BASE_DIR / 'data' / 'chr' / 'chr21.txt'
    
    # RUN THIS TO CREATE genome.txt
    # reader.combine_chrs(CHR_DIR, OUTPUT_DIR)
    
    # RUN THIS TO CREATE chr21.txt
    reader.clean_chr(CHR_DIR, OUTPUT_CHR, "chr21")
    
    # print(CHR_DIR)
    # print(__init__)
    
    pass
    
if __name__ == "__main__":
    main()