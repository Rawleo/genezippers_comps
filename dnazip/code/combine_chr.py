import reader
from constants import *
from pathlib import Path  


def main():
    CHR = 'chr1'
    CHR_DIR    = BASE_DIR / 'data' / 'chr' 
    OUTPUT_DIR = BASE_DIR / 'data' / 'chr' / 'genome.txt'
    
    # RUN THIS TO CREATE genome.txt
    # reader.combine_chrs(CHR_DIR, OUTPUT_DIR)
    
    # RUN THIS TO CREATE chr21.txt
    
    for chromosome in CHROMOSOMES:
        
        OUTPUT_CHR = BASE_DIR / 'data' / 'chr' / f'{chromosome}.txt'

        reader.clean_chr(CHR_DIR, OUTPUT_CHR, chromosome)
    
    # print(CHR_DIR)
    # print(__init__)
    
    pass
    
if __name__ == "__main__":
    main()