from config import HEIGHT, DNA_FILE, DNA_FILE_PATH
from converter import decodeFibonacci, binaryToBase, decodeBinary
import math

open(DNA_FILE_PATH+ DNA_FILE + "_dencoded.txt", "w").close()
outputFile = open(DNA_FILE_PATH+DNA_FILE + "_dencoded.txt", "a", encoding="utf-8")
with open(DNA_FILE_PATH+DNA_FILE + "_encoded.txt", "r") as file:
    inputFile = file.read()

def parseNum(i): 
    num = ""
    while(num[-2:] != "11"):
        num+=inputFile[i]
        i+=1
    print(num)
    print(decodeFibonacci(num))
    return decodeFibonacci(num), len(num)

def parseNumPos(i, window=None):
    num=""
    if(window):
        k =  math.ceil(math.log2(window))
    for x in range(k):
        num+=inputFile[i+x]
    index = num.find("11")
    if(index==-1):
        type="binary"
    else:
        num+=inputFile[i+k+1]
        if(num[index+2]=="0"):
            type="fibonacci"
        else:
            type="binary"

    if(type=="binary"):
        return decodeBinary(num), len(num)
    else:
        return decodeFibonacci(num), len(num)


def parseBases(num, position):
    bases=""
    for i in range(num):
        bases+=(binaryToBase(inputFile[position:position+2]))
        position+=2
    return bases

def parseFactors(num, position, outputDraft):
    window = len(outputDraft)
    factors = []
    for i in range(num):
        factorLength, length = parseNum(position)
        position+=length
        factorType = inputFile[position]
        position+=1
        factorPos, length = parseNumPos(position, window)
        position+=length
        factor = (factorLength, factorType, factorPos-1)
        factors.append(factor)
        window+=factorLength
        print(factor)
    return factors, position

def decodeFactors(factors, outputDraft):
    for factor in factors:
        print(factor)
        # print(len(outputDraft))
        if(factor[1]=="0"):
            for i in range(factor[0]):
                outputDraft+=outputDraft[factor[2]+i]
        if(factor[1]=="1"):
            length = len(outputDraft)
            table = str.maketrans("ACTG", "TGAC")
            for i in range(factor[0]):
                outputDraft+=outputDraft[length-factor[2]+i].translate(table)
    return outputDraft


def main():
    outputDraft = ""
    type = "bases"
    i=0
    while(i<len(inputFile)):
        num, length = parseNum(i)
        i+=length

        if (type == "bases"):
            bases = parseBases(num, i)
            i+=num*2
            type="factors"
            outputDraft+=bases

        elif(type == "factors"):
            factors, i = parseFactors(num, i, outputDraft)
            print("i:", i)
            outputDraft=decodeFactors(factors, outputDraft)
            type= "bases"

    
    outputFile.write(outputDraft)

if __name__ == "__main__":
    main()