from config import DNA_FILE, DNA_FILE_PATH
import sys

with open(DNA_FILE_PATH+DNA_FILE + ".txt", "r") as file:
    original = file.read()
with open(DNA_FILE_PATH+DNA_FILE + "_dencoded.txt", "r") as file:
    decoded = file.read()

def main():
    for i in range(len(decoded)):
        if(decoded[i]!=original[i]):
            print("NOT MATCHING")
            sys.exit()
    print("MATCHING")
            
        

if __name__ == "__main__":
    main()