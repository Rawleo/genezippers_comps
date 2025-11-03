'''
 * Author: Ryan Son
 * Modified Date: Oct. 7, 2025
 * File: huffman.py
 * Summary: Given an input of human genomic sorted variants, it will map insertions 
            using the Huffman coding algorithm and output a huffman tree with an associated 
            encoding dictionary.
'''


import re, ast
from config import *
import huffman_orig as h
    
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
Transform input text into an array of k-mers, or k-symbol items.
@params: 
 * ins_seq - the text sequence to transform.
 * k_mer_size - the integer size of the k-mer.
@return:
 * k_mer_array - an array of k-mers that will be used for Huffman encoding.
'''


def insertions_to_kmers(ins_seq, k_mer_size):
    k = k_mer_size
    regex_k = k * '.'
    k_mer_array = re.findall(regex_k, ins_seq)

    return k_mer_array


'''
Encode an insertion sequence into its bitstring representation with a 
Huffman encoding map dictionary.
@params: 
 * ins_seq - string to be processed to into an array of k-mers and then bitstring.
 * encoding_map - the Huffman encoding map dictionary.
 * k_mer_size - the size of the k-mers.
@return:
 * ins_seq_bitstr - the final encoded bitstring represented as 1's and 0's.
'''


def ins_seq_to_bitstr(ins_seq, encoding_map, k_mer_size):
    ins_seq_kmer = insertions_to_kmers(ins_seq, k_mer_size)
    ins_seq_bitstr = encode_insertions(encoding_map, ins_seq_kmer)

    return ins_seq_bitstr


'''
Encode the k_mer_array into a string of bits using Huffman encoding.
@params: 
 * encoding_map - the Huffman encoding dictionary to encode the array.
 * k_mer_array - an array of k-mers that will be used for huffman encoding.
@return:
 * ins_bitstr - Python string containing 1's and 0's.
'''


def encode_insertions(encoding_map, k_mer_array):
    ins_bitstr = ""

    # print(k_mer_array)

    for k_mer in k_mer_array:

        ins_bitstr += encoding_map[k_mer]

    return ins_bitstr


'''
Function used to create the Huffman encoding map for encoding. 
@params: 
 * ins_seq - the text sequence to transform.
 * k_mer_size - the integer size of the k-mer.
@return: 
 * encoding_map - the Huffman encoding dictionary to encode the array.
 * len(k_mer_array) - number of k_mers encoded.
'''


def run_k_mer_huffman(ins_seq, k_mer_size):
    encoding_map = {}
    k = k_mer_size

    print("Constructing the k-mer array.")

    k_mer_array = insertions_to_kmers(ins_seq, k)

    print("Building frequency data.")

    ins_frq_dict = build_frequency_dict(k_mer_array)

    print("Building tree data.")

    huffman_root = build_huffman_tree(ins_frq_dict)

    print("Mapping tree data.")

    map_encodings(huffman_root, encoding_map, "")

    print("Exporting tree data.")

    export_as_txt(HUFFMAN_TREE, (encoding_map, len(k_mer_array)))

    print("Encoding the bitstring.")

    ins_seq_bitstr  = encode_insertions(encoding_map, k_mer_array)

    print("Done encoding.")

    return ins_seq_bitstr, encoding_map, len(k_mer_array)


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
    with open(filename + '.bin', 'rb') as file:
        data = file.read()
        # print(data)
        bits = ''.join(format(byte, '08b') for byte in data)
        # print(bits)
    # Remove leading zero
    return bits[1:]


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


def huff_encoding():

    sequence_data = read_in_file(GENOME_FILE)
    
    bitstr, encoding_map, k_mer_array_len = run_k_mer_huffman(sequence_data, K_MER_SIZE)

    remainder_nuc_len = len(sequence_data) % K_MER_SIZE
    remainder_nucs = sequence_data[len(sequence_data) - remainder_nuc_len:]
    remainder_bitstr = ''.join([(NUC_ENCODING[x]) for x in remainder_nucs])

    # Append Huffman portion with non-Huffman
    bitstr += remainder_bitstr

    h.export_as_binary(str(GENOME_BIN), bitstr)


def huff_decoding():
    
    

    bin_file = read_bin(str(GENOME_BIN))

    encoding_dict = load_dict_from_file(str(HUFFMAN_TREE))
    
    print(encoding_dict)
    number_of_kmers = encoding_dict[1]
    print(number_of_kmers)

    # huffman_root = reconstruct_huffman_tree(encoding_dict)

    # sequence, buffer = decode_huffman(bin_file, huffman_root, number_of_kmers)

    # # Process non-Huffman encoded nucleotides
    # extra_nucs = ''.join([
    #     TWO_BIT_ENCODING[buffer[(i * 2):((i * 2) + 2)]]
    #     for i in range(len(buffer) // 2)
    # ])

    # # Append Huffman portion with non-Huffman
    # sequence += extra_nucs

    # h.export_as_txt(DECODED_FILE, sequence)


def main():
    
    # print(BASE_PATH)

    # huff_encoding()
    huff_decoding()

    pass


if __name__ == "__main__":
    main()
