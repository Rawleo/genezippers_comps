DNA_FILE = "chr21"
DNA_FILE_PATH = "./data/"
DNA_FILE_TXT = DNA_FILE + ".txt"
DNA_FILE_FA = DNA_FILE + ".fa"
HEIGHT = 8

with open(DNA_FILE_PATH+DNA_FILE_TXT, "r") as file:
       CONTENT = file.read()
