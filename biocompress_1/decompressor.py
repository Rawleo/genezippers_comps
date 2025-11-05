from config import DNA_FILE, DNA_FILE_PATH, HEIGHT, COMPLEMENT_TABLE
from converter import decode_fibonacci, decode_binary
import math
from tqdm import tqdm


open(DNA_FILE_PATH+ DNA_FILE + "_" + str(HEIGHT) + "_decoded.txt", "w").close()
output_file = open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_decoded.txt", "a", encoding="utf-8")
with open(DNA_FILE_PATH+DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "r") as file:
    input_file = file.read()
PAIR_TO_BASE = {"11":"A","10":"C","01":"T","00":"G"}

#reads chars from i until it hits 11 and returns decoded number
def parse_number(i): 
    end = input_file.find("11", i)
    num = input_file[i : end + 2]
    return decode_fibonacci(num), len(num)

#reads bits from i, determines whether binary or fibonacci and returns number
def parse_number_position(i, window):
    k =  math.ceil(math.log2(window)) #max length of binary number
    num = input_file[i : i + k]
    index = num.find("11")
    if index==-1: #if no 11, then must be binary
        kind="binary"
    else: 
        num+=input_file[i+k] #read in additional bit to account for added bit
        if num[index+2]=="0":
            kind="fibonacci"
            num=num[:index+2] #cut off at 11
        else:
            kind="binary"

    if kind=="binary":
        return decode_binary(num), len(num)
    else:
        return decode_fibonacci(num), len(num)+1
    

#reads in num*2 bits starting at position and converts to bases
def parse_bases(num, position):
    chunk = input_file[position : position + 2*num]
    return ''.join(PAIR_TO_BASE[chunk[i:i+2]] for i in range(0, len(chunk), 2))


#reads in num factors and processes them, returns length kind and position as ints
def parse_factors(num, position, output_draft):
    window = len(output_draft)
    factors = []
    for i in range(num):
        factor_length, length = parse_number(position)
        position+=length
        factor_kind = input_file[position]
        position+=1 #only 1 bit for the kind
        factor_position, length = parse_number_position(position, window)
        position+=length
        factor = (factor_length, factor_kind, factor_position-1)
        factors.append(factor)
        window+=factor_length #accounts for new factor created, as it hasn't been written to output_draft yet
    return factors, position


#takes in factor lengths and positions and writes correct copying to output_draft
def decode_factors(factors, output_draft):
    for factor in factors:
        if factor[1]=="0": #factor
            for i in range(factor[0]):
                output_draft+=output_draft[factor[2]+i]
        if factor[1]=="1": #palindrome
            length = len(output_draft)
            for i in range(factor[0]):
                output_draft+=output_draft[length-factor[2]+i].translate(COMPLEMENT_TABLE) #relative positioning
    return output_draft


def main():
    output_draft = ""
    kind = "bases"
    i=0
    length_input = len(input_file)
    with tqdm(total=length_input, desc="Decompressing", unit="bytes") as pbar:
        prev_i = 0
        while(i<len(input_file)): #alternates between bases and factors
            num, length = parse_number(i)
            i+=length
            if kind == "bases":
                bases = parse_bases(num, i)
                i+=num*2
                kind="factors"
                output_draft+=bases
            elif kind == "factors":
                factors, i = parse_factors(num, i, output_draft)
                output_draft=decode_factors(factors, output_draft)
                kind= "bases"
            pbar.update(i - prev_i)
            prev_i = i
        output_file.write(output_draft)


if __name__ == "__main__":
    main()