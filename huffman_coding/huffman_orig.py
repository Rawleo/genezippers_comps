'''
 * Author: Ryan Son
 * Date: Sept. 18, 2025
 * File: huffman_coding.py
 * Summary: Given a list of text files to encode using the Huffman codign algorithm, 
            this script will losslessly compress those text files. It will output a 
            .bin file containing the encoded text represented as bytes, two resultant
            files from the decoding of the .bin file and of the encoded bit_string that
            did not get encoded into bytes. It will also output the encoding_map used 
            to create the encoded .bin files. 
'''

'''
Node Class for implementing a binary tree.
'''
class Node:

    def __init__(self, symbol, frequency, leftChild=None, rightChild=None):
        self.symbol = symbol
        self.frequency = frequency
        self.leftChild = leftChild
        self.rightChild = rightChild


'''
Read in an input file.
@params: 
 * input_file - text file to be read
@return:
 * text - the contents of the file as a string
'''
def read_in_file(input_file):
    file_in = open(input_file, "r")
    text = (file_in.read())
    return text


'''
Build the required dictionary, mapping each symbol to their frequency.
@params: 
 * input_text - string to be processed to assign each unique symbol a frequency
@return:
 * freq_dict - a dictionary containing the unique symbol with their corresponding frequency.
'''
def build_frequency_dict(input_text):
    freq_dict = {}
    for char in input_text:
        if char not in freq_dict:
            freq_dict[char] = 1
        else:
            freq_dict[char] += 1
    return freq_dict


'''
Build the huffman tree according to their frequencies.
@params: 
 * freq_dict - a dictionary containing the unique symbol with their corresponding frequency.
@return:
 * nodes - the binary Huffman Tree beginning at the root.
'''
def build_huffman_tree(freq_dict):
    nodes = []
    for symbol, freq in freq_dict.items():
        nodes.append(Node(symbol, freq))

    while len(nodes) > 1:
        # Sort nodes by frequency using key parameter and lambda function in the sorted function
        nodes = sorted(nodes, key=lambda n: n.frequency)
        left = nodes.pop(0)
        right = nodes.pop(0)
        parent = Node(left.symbol + right.symbol,
                      left.frequency + right.frequency, left, right)
        nodes.append(parent)
    # Return the root node or return nothing if empty
    return nodes[0] if nodes else None


'''
Assign correct binary tree mapping to each unique symbol using recursion.
@params: 
 * root - the binary Huffman Tree beginning at the root.
 * curr - the current node of the tree
@return:
 * encoding_map - a dictionary for each unique symbol corresponding to their unique encoding
'''
def map_encodings(root, encoding_map, current):
    if root is None:
        return
    if root.leftChild is None and root.rightChild is None:
        encoding_map[root.symbol] = current
        return

    map_encodings(root.leftChild, encoding_map, current + "0")
    map_encodings(root.rightChild, encoding_map, current + "1")


'''
Encode the string according to its mapping.
@params: 
 * encoding_map - a dictionary for each unique symbol corresponding to their unique encoding
 * text - input string to be encoded
@return:
 * encoded_text - output text after it has been encoded by dict
'''
def encode_text(encoding_map, text):
    encoded_text = ""
    for char in text:
        encoded_text += str(encoding_map[char])
    return encoded_text


'''
Decode the encoded string to retrieve the original string.
@params: 
 * encoded_text - output text after it has been encoded by dict
 * root - the binary Huffman Tree beginning at the root.
@return:
 * result - the original text after it has been decoded.
'''
def decode(encoded_text, root):
    result = ""
    curr = root
    for char in encoded_text:
        if char == "0":
            curr = curr.leftChild
        else:
            curr = curr.rightChild
        if curr.leftChild is None and curr.rightChild is None:
            result += curr.symbol
            curr = root
    return result


'''
Read in binary file from bytes to bits to string. For some reason it adds a leading zero....
@params: 
 * filename - filename of .bin file
@return:
 * bits - the original huffman encoded bits
'''
def read_bin(filename):
    with open(filename + '.bin', 'rb') as file:
        data = file.read()
        # print(data)
        bits = ''.join(format(byte, '08b') for byte in data)
        # print(bits)
    # Remove leading zero
    return bits[1:]


'''
Export as binary file consisting of the encoded string transformed into bytes.
The binary_string consists of a string of 1's and 0's, this string is then
converted into an actual binary integer. From here, it is then converted into bytes.
This transformation is accomplished by calculating the number of bytes required to 
represent the given binary integer. Adding 7 to the length of the binary integer is
done to round up to the nearest byte, so if a string is not entirely divisible by 8, 
there will still be a byte representation of the bits that are left. This is then sorted
in big-endian order.
@params: 
 * export_name - chosen filename 
 * binary_str - the encoded huffman string
@return:
 * Exports a .bin file of the encoded string now as bytes to the current directory
'''
def export_as_binary(export_name, binary_str):
    byte_value = int(binary_str, 2).to_bytes((len(binary_str) + 7) // 8,
                                             byteorder='big')
    # print(byte_value)
    with open(export_name + ".bin", "wb") as file:
        file.write(byte_value)
        
        
'''
Export input text as txt file.
@params: 
 * export_name - chosen filename 
 * text - input string to be exported
@return:
 * Exports a text file to the current directory.
'''
def export_as_txt(export_name, text):
    with open(export_name + ".txt", "w") as file:
        file.write(str(text))


'''
Run the program.
'''
def main():
    file_list = ["DNA", "Emma", "random", "sample_text"]
    for file_name in file_list:
        
        export_name = "export_files/" + file_name

        encoding_map    = {}
        text            = read_in_file("input_files/" + file_name + ".txt")
        freq_dict       = build_frequency_dict(text)
        root            = build_huffman_tree(freq_dict)
        
        map_encodings(root, encoding_map, "")
        
        encoded_text = encode_text(encoding_map, text)
        
        export_as_binary(export_name, encoded_text)
        export_as_txt(export_name + "_encoded", encoded_text)
        export_as_txt(export_name + "_encoding_map", encoding_map)
        
        bin_file            = read_bin(export_name)
        result              = decode(encoded_text, root)
        result_from_bytes   = decode(bin_file, root)
        
        export_as_txt(export_name + "_decoded", result)
        export_as_txt(export_name + "_decoded_bin", result_from_bytes)

    
    # print("\n")
    # print("Default encoding: " + encoded_text)
    # print("\n")
    # print("Encoding from .bin file: " + bin_file)
    # print("Decoded from .bin file: " + result_from_bytes)
    # print("\n")


if __name__ == "__main__":
    main()
