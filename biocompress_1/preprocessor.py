from config import CONTENT, DNA_FILE, DNA_FILE_PATH

open(DNA_FILE_PATH + DNA_FILE + ".txt", "w").close()
outputFile = open(DNA_FILE_PATH + DNA_FILE + ".txt", "a", encoding="utf-8")

def main():
    for i in CONTENT:
        if (i in ['A', 'C', 'T', 'G']):
            outputFile.write(i)
            

if __name__ == "__main__":
    main()