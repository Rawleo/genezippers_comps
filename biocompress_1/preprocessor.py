from config import CONTENT, DNA_FILE, DNA_FILE_PATH


open(DNA_FILE_PATH + DNA_FILE + ".txt", "w").close()
output_file = open(DNA_FILE_PATH + DNA_FILE + ".txt", "a", encoding="utf-8")

def main():
    for i in CONTENT:
        if i.upper() in ['A', 'C', 'T', 'G']:
            output_file.write(i.upper())
            

if __name__ == "__main__":
    main()