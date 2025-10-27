from config import CONTENT
import math


#encodes a number with fibonaci encoding. Like binary but instead of 1248, its 12358, and ends with 1
def encodeFibonacci(num):
    fibNumbers = [1,2]
    while(fibNumbers[len(fibNumbers)-1]<=num):
        fibNumbers.append(fibNumbers[len(fibNumbers)-1]+fibNumbers[len(fibNumbers)-2])
    del fibNumbers[len(fibNumbers)-1]
    code = []
    for val in reversed(fibNumbers):
        if(num>=val):
            code.insert(0,"1")
            num -= val
        else:
            code.insert(0,"0")
    code.append("1")
    binaryCode = "".join(code)
    return binaryCode


#decodes input fibonacci number and returns int
def decodeFibonacci(num):
    decoded = 0
    num = num[:-1]
    fibNumbers = [1,2]
    while(len(fibNumbers)<len(num)):
        fibNumbers.append(fibNumbers[-1]+fibNumbers[-2])
    for i in range(len(num)):
        if(num[i]=="1"):
            decoded+=fibNumbers[i]
    return decoded


#encodes a number into binary, adds a 1 after the first 11 if it exists
def encodeBinary(num, i):
    binary = str(bin(num)[2:])
    k =  math.ceil(math.log2(i))
    binary = binary.zfill(k)
    index = binary.find("11")
    if (index != -1): 
        binary = binary[:index + 2] + '1' + binary[index + 2:]
    return binary


#decodes input binary string into an int, removes added 1 if it exists
def decodeBinary(num):
    index = num.find("111")
    if(index != -1):
        num = num[:index]+num[index+1:]
    return int(num,2)


#converts a base to 2 bit encoding
def baseToBinary(base: str):
    mapping = {
            "A": "11",
            "C": "10",
            "T": "01",
            "G": "00",
        }
    return mapping.get(base, "11")


#converts 2 bit encoding to base
def binaryToBase(base):
    mapping = {
            "11": "A",
            "10": "C",
            "01": "T",
            "00": "G",
        }
    return mapping.get(base, "A")


#converts factor into binary encoding. Returns encoding, type, length
def encodeFactor(factor, i):
    length = factor[1]
    type = factor[2]
    position = factor[0][0]+1
    if(type=="factor"): #encoding type bit
        typeEncoded="0"
    else:
        typeEncoded="1"
    posFib=encodeFibonacci(position)+"0"
    posBin=encodeBinary(position, i)
    if(len(posBin)<len(posFib)): #determines if binary or fibonnaci encoding is more efficient
        positionEncoded=posBin
    else:
        positionEncoded=posFib
    lengthEncoded=encodeFibonacci(length)
    if((factor[1]*2)<=len(lengthEncoded+typeEncoded+positionEncoded)): #determines if more efficient to encode as bases instead of factor
        if(type=="factor"):
            string = CONTENT[factor[0][0]:factor[0][0]+length]  
        elif(type=="palindrome"):
            string = CONTENT[i-factor[0][0]:i-factor[0][0]+length] #relative positioning
            table = str.maketrans("ACTG", "TGAC")
            string = string.translate(table)
        binary = ""
        for base in string:
            binary+=baseToBinary(base)
        type = "base"
        encoded = binary
    else:
        encoded = lengthEncoded+typeEncoded+positionEncoded
    return (encoded, type, length)

