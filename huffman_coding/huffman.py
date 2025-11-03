import re, ast
from config import *


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
Build the required dictionary, mapping each symbol to their frequency.
@params: 
 * input_text - string to be processed to assign each unique symbol a frequency.
@return:
 * freq_dict - a dictionary containing unique symbols with their corresponding frequency.
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
 * curr - the current node of the tree.
@return:
 * encoding_map - a dictionary for each unique symbol corresponding to their unique encoding.
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
Transform a Huffman encoding map into a Huffman tree used for decoding.
@params: 
 * encoding_map - the Huffman encoding dictionary to recreate a Huffman tree.
@return:
 * root - the binary Huffman Tree beginning at the root.
'''
def reconstruct_huffman_tree(encoding_map):
    root = Node(symbol=None, frequency=None)

    for symbol, code in encoding_map.items():
        current_node = root

        for bit in code[:-1]:
            if bit == '0':
                if current_node.leftChild is None:
                    current_node.leftChild = Node(symbol=None, frequency=None)
                current_node = current_node.leftChild
            else:
                if current_node.rightChild is None:
                    current_node.rightChild = Node(symbol=None, frequency=None)
                current_node = current_node.rightChild

        last_bit = code[-1]
        if last_bit == '0':
            current_node.leftChild = Node(symbol=symbol, frequency=None)
        else:
            current_node.rightChild = Node(symbol=symbol, frequency=None)

    return root


'''
Decode a string of 1's and 0's by traversing a Huffman tree.
@params: 
 * encoded_text - encoded string of 1's and 0's.
 * root - Huffman tree root to traverse.
@return:
 * result - the decoded string.
 * buffer - extra bits to process as regular NUC encodings. 
'''
def decode_huffman(encoded_text, root, number_of_kmers):
    result = ""
    buffer = ""
    count = 0
    curr = root
    for char in encoded_text:
        if char == "0":
            curr = curr.leftChild
            buffer += "0"
        else:
            curr = curr.rightChild
            buffer += "1"
        if curr.leftChild is None and curr.rightChild is None:
            if count == number_of_kmers: return result, buffer
            result += curr.symbol
            count += 1
            buffer = ""
            curr = root
    return result, buffer


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
    with open(export_name, "wb") as file:
        file.write(byte_value)
        
        
'''
Read in a text file of Huffman encoding map dictionary into an
actual Python dictionary to recreate a Huffman tree.
@params: 
 * filepath - path to the Huffman encoding map dictionary.
@return:
 * encoding_map - the Huffman encoding dictionary to recreate a Huffman tree.
'''
def load_dict_from_file(filepath):
    with open(filepath, 'r') as f:
        file_content = f.read()

    encoding_map = ast.literal_eval(file_content)

    return encoding_map


'''
Output a text file given the input file path and the input text.
@params: 
 * export_name - the file path to export to.
 * text - input to text to export.
@return:
 * None, but outputs a text file.
'''
def export_as_txt(export_name_with_extension, text):
    with open(export_name_with_extension, "w") as file:
        file.write(str(text))


'''
Append to a text file given the input file path and the input text.
@params: 
 * export_name - the file path to export to.
 * text - input to text to append to.
@return:
 * None, but outputs a text file.
'''
def append_as_txt(export_name, text):
    with open(export_name, "a") as file:
        file.write(str(text))


'''
Read in binary file from bytes to bits to string. For some reason it adds a leading zero....
@params: 
 * filename - filename of .bin file
@return:
 * bits - the original huffman encoded bits
'''
def read_bin(filename):
    with open(filename, 'rb') as file:
        data = file.read()
        # print(data)
        bits = ''.join(format(byte, '08b') for byte in data)
        # print(bits)
    # Remove leading zero
    return bits[1:]        


# from decode.py
def add_padding(bit_string):

    # Find first VINT
    padding = 0

    while bit_string[padding] != '1':

        padding += 1

    return bit_string[padding:]


# from bitfile.py
def writeBitVINT(num):

    bit_string = ''

    while (num >= 128):

        # Get last 7 bits and set first bit to 1
        chrByte = ((num & 0x7F) | 0x80)
        mask = 128

        for i in range(8):

            if (chrByte & mask):
                bit_string += '1'
            else:
                bit_string += '0'

            mask = mask >> 1

        # num by 7 bits
        num = num >> 7

    chrByte = num
    mask = 128

    for i in range(8):

        if (chrByte & mask):
            bit_string += '1'
        else:
            bit_string += '0'

        mask = mask >> 1
    
    return bit_string


# from decode.py
def readBitVINT(bit_string):
    
    num = 0
    shift = 0
    bytes_used = 0

    for i in range(0, len(bit_string), 8):

        byte = bit_string[i:i+8]
        if len(byte) < 8:
            break

        bits = byte[1:]
        bit_val = int(bits, 2)

        num |= (bit_val << shift)

        shift += 7
        bytes_used += 1

        if byte[0] == '0':
            break

    bits_used = bytes_used * 8
    
    return num, bits_used