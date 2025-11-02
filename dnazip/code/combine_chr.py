import code.helper.reader
from pathlib import Path  

BASE_DIR     = Path(__file__).resolve().parent
OUTPUT_DIR   = BASE_DIR / 'data' / 'output'


def main():
    
    FOLDER_PATH = 'comps_f25_rgj/dnazip/data/chr/'
    OUTPUT_PATH = '/Users/ryanson/Documents/Comps/comps_repo_venvs/comps_f25_rgj/dnazip/data/chr/FULL_GENOME.TXT'
    # OUTPUT_DIR  = BASE_DIR / 'data' / 'chr'
    
    # reader.combine_chrs(FOLDER_PATH, OUTPUT_PATH)
    
    # print(constants.BASE_DIR)
    # print(__init__)
    
    pass
    
if __name__ == "__main__":
    main()