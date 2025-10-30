from config import DNA_FILE, DNA_FILE_PATH, HEIGHT
from converter import decodeFibonacci, binaryToBase, decodeBinary
import math
from tqdm import tqdm


open(DNA_FILE_PATH+ DNA_FILE + "_" + str(HEIGHT) + "_decoded.txt", "w").close()
outputFile = open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_decoded.txt", "a", encoding="utf-8")
with open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "r") as file:
    inputFile = file.read()

#reads chars from i until it hits 11 and returns decoded number
def parseNum(i): 
    num = ""
    while(num[-2:] != "11"):
        num+=inputFile[i]
        i+=1
    return decodeFibonacci(num), len(num)

#reads bits from i, determines whether binary or fibonacci and returns number
def parseNumPos(i, window, outputDraft):
    num=""
    k =  math.ceil(math.log2(window)) #max length of binary number
    for x in range(k):
        num+=inputFile[i+x]
    index = num.find("11")
    if(index==-1): #if no 11, then must be binary
        type="binary"
    else: 
        num+=inputFile[i+k] #read in additional bit to account for added bit
        if(num[index+2]=="0"):
            type="fibonacci"
            num=num[:index+2] #cut off at 11
        else:
            type="binary"

    if(type=="binary"):
        return decodeBinary(num), len(num)
    else:
        return decodeFibonacci(num), len(num)+1
    

#reads in num*2 bits starting at position and converts to bases
def parseBases(num, position):
    bases=""
    for i in range(num):
        bases+=(binaryToBase(inputFile[position:position+2]))
        position+=2
    return bases


#reads in num factors and processes them, returns length type and position as ints
def parseFactors(num, position, outputDraft):
    window = len(outputDraft)
    factors = []
    for i in range(num):
        factorLength, length = parseNum(position)
        position+=length
        factorType = inputFile[position]
        position+=1 #only 1 bit for the type
        factorPos, length = parseNumPos(position, window, outputDraft)
        position+=length
        factor = (factorLength, factorType, factorPos-1)
        factors.append(factor)
        window+=factorLength #accounts for new factor created, as it hasn't been written to outputDraft yet
    return factors, position


#takes in factor lengths and positions and writes correct copying to outputDraft
def decodeFactors(factors, outputDraft):
    for factor in factors:
        if(factor[1]=="0"): #factor
            for i in range(factor[0]):
                outputDraft+=outputDraft[factor[2]+i]
        if(factor[1]=="1"): #palindrome
            length = len(outputDraft)
            table = str.maketrans("ACTG", "TGAC")
            for i in range(factor[0]):
                outputDraft+=outputDraft[length-factor[2]+i].translate(table) #relative positioning
    return outputDraft


def main():
    outputDraft = ""
    type = "bases"
    i=0
    lengthInput = len(inputFile)
    with tqdm(total=lengthInput, desc="Decompressing", unit="bytes") as pbar:
        while(i<len(inputFile)): #alternates between bases and factors
            num, length = parseNum(i)
            i+=length
            if (type == "bases"):
                bases = parseBases(num, i)
                i+=num*2
                type="factors"
                outputDraft+=bases
            elif(type == "factors"):
                factors, i = parseFactors(num, i, outputDraft)
                outputDraft=decodeFactors(factors, outputDraft)
                type= "bases"
            pbar.n=i
            pbar.refresh()
        outputFile.write(outputDraft)


if __name__ == "__main__":
    main()