DNA_FILE = "ecoli"
DNA_FILE_PATH = "../dnazip/data/chr/"
DNA_FILE_TXT = DNA_FILE + ".txt"
DNA_FILE_FA = DNA_FILE + ".fa"
HEIGHT = 8
COMPARE_LENGTH = 50

with open(DNA_FILE_PATH+DNA_FILE_TXT, "r") as file:
       CONTENT = file.read()
