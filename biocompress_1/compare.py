from config import DNA_FILE, DNA_FILE_PATH, COMPARE_LENGTH
import sys

with open(DNA_FILE_PATH+DNA_FILE + ".txt", "r") as file:
    original = file.read()
with open(DNA_FILE_PATH+DNA_FILE + "_dencoded.txt", "r") as file:
    decoded = file.read()

def main():
    for i in range(len(original)):
        if decoded[i]!=original[i]:
            print("NOT MATCHING")
            print("Location:", i)
            print("Error:")
            print(original[i-5:i+COMPARE_LENGTH])
            print(decoded[i-5:i+COMPARE_LENGTH])
            sys.exit()
    print("MATCHING")
            
        

if __name__ == "__main__":
    main()