from AGCT_tree import createTree, findFactor
from config import HEIGHT, DNA_FILE, CONTENT,DNA_FILE_PATH
from converter import baseToBinary, encodeFactor, encodeFibonacci, binaryToBase
from typing import Optional
import sys


open(DNA_FILE_PATH + DNA_FILE + "_encoded.txt", "w").close()
outputFile = open(DNA_FILE_PATH + DNA_FILE + "_encoded.txt", "a", encoding="utf-8")
TREE = createTree(HEIGHT)

#for searching for factors beyond tree, compare input postion and factor postion and count how many bases match
def extendedSearch(i, position, type):
    table = str.maketrans("ACTG", "TGAC")
    i=i+HEIGHT
    position=position+HEIGHT
    addLength = 0
    if(i>len(CONTENT)-1):
        return addLength
    if(type=="factor"):
        while(CONTENT[i]==CONTENT[position]):
            addLength+=1
            i+=1
            position+=1
            if(i>len(CONTENT)-1):
                return addLength
    if(type=="palindrome"):
        while(CONTENT[i].translate(table) == CONTENT[position]):
            addLength+=1
            i+=1
            position+=1
            if(i>len(CONTENT)-1):
                return addLength
    return addLength

#finds longest factor or palindrome in the tree
def longestFactorPalindrome(i: int) -> tuple[Optional[list[int]], Optional[int], Optional[str]]:
    string = CONTENT[i:i+HEIGHT]
    table = str.maketrans("ACTG", "TGAC")
    palindrome = string.translate(table)
    factorPos = findFactor(string, TREE)

    #if the longest factor is the length of tree, do an extended search and only return longest
    if (factorPos[1]==HEIGHT):
        addLength = 0
        positionNum = 0
        positionNumTemp = 0
        if(factorPos[0]):
            for position in factorPos[0]:
                addLengthTemp = extendedSearch(i, position, "factor")
                if (addLengthTemp > addLength): 
                    addLength = addLengthTemp
                    positionNum = positionNumTemp
                positionNumTemp +=1 
            factorPos=([factorPos[0][positionNum]], factorPos[1]+addLength)

    #if the longest palindrome is the length of tree, do an extended search and only return longest
    palindromePos = findFactor(palindrome, TREE)
    if (palindromePos[1]==HEIGHT):
        addLength = 0
        positionNum = 0
        positionNumTemp = 0
        if(palindromePos[0]):
            for position in palindromePos[0]:
                addLengthTemp = extendedSearch(i, position, "palindrome")
                if (addLengthTemp > addLength): 
                    addLength = addLengthTemp
                    positionNum = positionNumTemp
                positionNumTemp +=1
            palindromePos=([i-palindromePos[0][positionNum]], palindromePos[1]+addLength) #relative positioning
    #niche case for short palindromes
    elif(palindromePos[1]):
        palindromePos=([i-palindromePos[0][0]],palindromePos[1]) #relative positioning
    #if both a factor and palindrome were found, compare their lengths and return longest
    if(factorPos[1] and palindromePos[1]):
        if factorPos[1] >= palindromePos[1]:
            return (factorPos[0], factorPos[1], "factor")
        else:
            return (palindromePos[0], palindromePos[1], "palindrome")
    return (None, None, None)


#searches tree for factors, adds current input to tree, returns encoding of longest factor or bases
def process(i: int):
    segment = CONTENT[i:i+HEIGHT]
    longestFactor = longestFactorPalindrome(i)
    TREE.createPositions(segment, i)

    #if a longest factor was found, encode it into (binary, type, length)
    if(longestFactor[0]):
        longestFactor = encodeFactor(longestFactor, i)
        return longestFactor
    else: 
        return (baseToBinary(CONTENT[i]), "base", 1)
    

#writes length of the block, then writes each factor or base to output file
def printBuf(buffer):
    if(buffer[0][1]=="base"):
        length=0
        for item in buffer:
            length+=item[2]
        outputFile.write(encodeFibonacci(length))
    else:
        outputFile.write(encodeFibonacci(len(buffer)))
    for item in buffer:
        outputFile.write(item[0])


#adds factors and bases to buffer and manages when to write to output file
def encode(processed, buffer):
    if(len(buffer)==0):
        return [processed]
    #if the input type doesn't match the types in the buffer, write to output file and clear buffer
    if((processed[1]=="base" and buffer[0][1]!= "base") or processed[1]!="base" and buffer[0][1]== "base"):
        printBuf(buffer)
        buffer=[]
    buffer.append(processed)
    return buffer
                

def main():
    position = 0
    buffer=[]
    while(position<len(CONTENT)):
        processed = process(position)
        buffer = encode(processed, buffer)
        position+=processed[2]
    printBuf(buffer)
    outputFile.close()

if __name__ == "__main__":
    main()