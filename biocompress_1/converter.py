from config import CONTENT, COMPLEMENT_TABLE
import math


#encodes a number with fibonaci encoding. Like binary but instead of 1248, its 12358, and ends with 1
def encode_fibonacci(num):
    fibonacci_numbers = [1,2]
    while(fibonacci_numbers[len(fibonacci_numbers)-1]<=num):
        fibonacci_numbers.append(fibonacci_numbers[len(fibonacci_numbers)-1]+fibonacci_numbers[len(fibonacci_numbers)-2])
    del fibonacci_numbers[len(fibonacci_numbers)-1]
    code = []
    for val in reversed(fibonacci_numbers):
        if num>=val:
            code.insert(0,"1")
            num -= val
        else:
            code.insert(0,"0")
    code.append("1")
    binary_code = "".join(code)
    return binary_code


#decodes input fibonacci number and returns int
def decode_fibonacci(num):
    decoded = 0
    num = num[:-1]
    fibonacci_numbers = [1,2]
    while(len(fibonacci_numbers)<len(num)):
        fibonacci_numbers.append(fibonacci_numbers[-1]+fibonacci_numbers[-2])
    for i in range(len(num)):
        if num[i]=="1":
            decoded+=fibonacci_numbers[i]
    return decoded


#encodes a number into binary, adds a 1 after the first 11 if it exists
def encode_binary(num, i):
    binary = str(bin(num)[2:])
    k =  math.ceil(math.log2(i))
    binary = binary.zfill(k)
    index = binary.find("11")
    if index != -1: 
        binary = binary[:index + 2] + '1' + binary[index + 2:]
    return binary


#decodes input binary string into an int, removes added 1 if it exists
def decode_binary(num):
    index = num.find("111")
    if index != -1:
        num = num[:index]+num[index+1:]
    return int(num,2)


#converts a base to 2 bit encoding
def base_to_binary(base: str):
    mapping = {
            "A": "11",
            "C": "10",
            "T": "01",
            "G": "00",
        }
    return mapping.get(base, "11")


#converts 2 bit encoding to base
def binary_to_base(base):
    mapping = {
            "11": "A",
            "10": "C",
            "01": "T",
            "00": "G",
        }
    return mapping.get(base, "A")


#converts factor into binary encoding. Returns encoding, kind, length
def encode_factor(factor, i):
    length = factor[1]
    kind = factor[2]
    position = factor[0][0]+1
    if kind=="factor": #encoding kind bit
        kind_encoded="0"
    else:
        kind_encoded="1"
    position_fibonacci=encode_fibonacci(position)+"0"
    position_binary=encode_binary(position, i)
    if len(position_binary)<len(position_fibonacci): #determines if binary or fibonnaci encoding is more efficient
        position_encoded=position_binary
    else:
        position_encoded=position_fibonacci
    length_encoded=encode_fibonacci(length)
    if (factor[1]*2)<=len(length_encoded+kind_encoded+position_encoded): #determines if more efficient to encode as bases instead of factor
        if kind=="factor":
            string = CONTENT[factor[0][0]:factor[0][0]+length]  
        elif kind=="palindrome":
            string = CONTENT[i-factor[0][0]:i-factor[0][0]+length] #relative positioning
            string = string.translate(COMPLEMENT_TABLE)
        binary = ""
        for base in string:
            binary+=base_to_binary(base)
        kind = "base"
        encoded = binary
    else:
        encoded = length_encoded+kind_encoded+position_encoded
    return (encoded, kind, length)

