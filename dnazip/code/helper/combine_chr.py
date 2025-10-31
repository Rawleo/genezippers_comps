import reader


def main():
    
    FOLDER_PATH = '/Users/ryanson/Documents/Comps/comps_repo_venvs/comps_f25_rgj/dnazip/data/chr/'
    OUTPUT_PATH = '/Users/ryanson/Documents/Comps/comps_repo_venvs/comps_f25_rgj/dnazip/data/chr/FULL_GENOME.TXT'
    
    reader.combine_chrs(FOLDER_PATH, OUTPUT_PATH)
    
    pass
    
if __name__ == "__main__":
    main()