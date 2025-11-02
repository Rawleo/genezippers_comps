import reader
from constants import *
from pathlib import Path  


def main():
    
    CHR_DIR    = BASE_DIR / 'data' / 'chr' 
    OUTPUT_DIR = BASE_DIR / 'data' / 'chr' / 'genome.txt'
    
    reader.combine_chrs(CHR_DIR, OUTPUT_DIR)
    
    # print(CHR_DIR)
    # print(__init__)
    
    pass
    
if __name__ == "__main__":
    main()