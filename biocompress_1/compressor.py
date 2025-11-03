from AGCT_tree import create_tree, find_factor
from config import HEIGHT, DNA_FILE, CONTENT,DNA_FILE_PATH, COMPLEMENT_TABLE
from converter import base_to_binary, encode_factor, encode_fibonacci
from typing import Optional
from tqdm import tqdm


open(DNA_FILE_PATH + DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "w").close()
output_file = open(DNA_FILE_PATH + DNA_FILE + "_" + str(HEIGHT) + "_encoded.txt", "a", encoding="utf-8")
TREE = create_tree(HEIGHT)

#for searching for factors beyond tree, compare input postion and factor postion and count how many bases match
def extended_search(i, position, kind):
    i=i+HEIGHT
    position=position+HEIGHT
    add_length = 0
    if i>len(CONTENT)-1:
        return add_length
    if kind=="factor":
        while(CONTENT[i]==CONTENT[position]):
            add_length+=1
            i+=1
            position+=1
            if i>len(CONTENT)-1:
                return add_length
    if kind=="palindrome":
        while(CONTENT[i].translate(COMPLEMENT_TABLE) == CONTENT[position]):
            add_length+=1
            i+=1
            position+=1
            if i>len(CONTENT)-1:
                return add_length
    return add_length

#finds longest factor or palindrome in the tree
def longest_factor_or_palindrome(i: int) -> tuple[Optional[list[int]], Optional[int], Optional[str]]:
    string = CONTENT[i:i+HEIGHT]
    palindrome = string.translate(COMPLEMENT_TABLE)
    factor_position = find_factor(string, TREE)

    #if the longest factor is the length of tree, do an extended search and only return longest
    if factor_position[1]==HEIGHT:
        add_length = 0
        position_number = 0
        position_number_temp = 0
        if factor_position[0]:
            for position in factor_position[0]:
                add_length_temp = extended_search(i, position, "factor")
                if add_length_temp > add_length: 
                    add_length = add_length_temp
                    position_number = position_number_temp
                position_number_temp +=1 
            factor_position=([factor_position[0][position_number]], factor_position[1]+add_length)

    #if the longest palindrome is the length of tree, do an extended search and only return longest
    palindrome_position = find_factor(palindrome, TREE)
    if palindrome_position[1]==HEIGHT:
        add_length = 0
        position_number = 0
        position_number_temp = 0
        if palindrome_position[0]:
            for position in palindrome_position[0]:
                add_length_temp = extended_search(i, position, "palindrome")
                if add_length_temp > add_length: 
                    add_length = add_length_temp
                    position_number = position_number_temp
                position_number_temp +=1
            palindrome_position=([i-palindrome_position[0][position_number]], palindrome_position[1]+add_length) #relative positioning
    #niche case for short palindromes
    elif palindrome_position[1]:
        palindrome_position=([i-palindrome_position[0][0]],palindrome_position[1]) #relative positioning
    #if both a factor and palindrome were found, compare their lengths and return longest
    if factor_position[1] and palindrome_position[1]:
        if factor_position[1] >= palindrome_position[1]:
            return (factor_position[0], factor_position[1], "factor")
        else:
            return (palindrome_position[0], palindrome_position[1], "palindrome")
    return (None, None, None)


#searches tree for factors, adds current input to tree, returns encoding of longest factor or bases
def process(i: int):
    segment = CONTENT[i:i+HEIGHT]
    longest_factor = longest_factor_or_palindrome(i)
    TREE.create_positions(segment, i)

    #if a longest factor was found, encode it into (binary, kind, length)
    if longest_factor[0]:
        longest_factor = encode_factor(longest_factor, i)
        return longest_factor
    else: 
        return (base_to_binary(CONTENT[i]), "base", 1)
    

#writes length of the block, then writes each factor or base to output file
def write_buffer(buffer):
    if buffer[0][1]=="base":
        length=0
        for item in buffer:
            length+=item[2]
        output_file.write(encode_fibonacci(length))
    else:
        output_file.write(encode_fibonacci(len(buffer)))
    for item in buffer:
        output_file.write(item[0])


#adds factors and bases to buffer and manages when to write to output file
def encode(processed, buffer):
    if len(buffer)==0:
        return [processed]
    #if the input kind doesn't match the kinds in the buffer, write to output file and clear buffer
    if (processed[1]=="base" and buffer[0][1]!= "base") or (processed[1]!="base" and buffer[0][1]== "base"):
        write_buffer(buffer)
        buffer=[]
    buffer.append(processed)
    return buffer
                

def main():
    length = len(CONTENT)
    position = 0
    buffer=[]
    with tqdm(total=length, desc="Compressing", unit="bytes") as pbar:
        while(position<len(CONTENT)):
            processed = process(position)
            buffer = encode(processed, buffer)
            position+=processed[2]
            
            pbar.update(processed[2])
    write_buffer(buffer)
    output_file.close()

if __name__ == "__main__":
    main()