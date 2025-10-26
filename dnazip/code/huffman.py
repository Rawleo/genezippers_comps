'''
 * Author: Ryan Son
 * Modified Date: Oct. 7, 2025
 * File: huffman.py
 * Summary: Given an input of human genomic sorted variants, it will map insertions 
            using the Huffman coding algorithm and output a huffman tree with an associated 
            encoding dictionary.
'''


import re, ast
from constants import *


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
    k             = k_mer_size
    regex_k       = k * '.'
    k_mer_array   = re.findall(regex_k, ins_seq)
    
    return k_mer_array  


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
'''
def run_insr_huffman(ins_seq, k_mer_size):
    encoding_map    = {}
    k               = k_mer_size
    k_mer_array     = insertions_to_kmers(ins_seq, k)
    ins_frq_dict    = build_frequency_dict(k_mer_array)
    huffman_root    = build_huffman_tree(ins_frq_dict)
    
    map_encodings(huffman_root, encoding_map, "")
        
    return encoding_map
        

'''
Decode a string of 1's and 0's by traversing a Huffman tree.
@params: 
 * encoded_text - encoded string of 1's and 0's.
 * root - Huffman tree root to traverse.
@return:
 * result - the decoded string.
 * buffer - extra bits to process as regular NUC encodings. 
'''
def decode_huffman(encoded_text, root):
    result = ""
    buffer = ""
    curr = root
    for char in encoded_text:
        if char == "0":
            curr = curr.leftChild
            buffer += "0"
        else:
            curr = curr.rightChild
            buffer += "1"
        if curr.leftChild is None and curr.rightChild is None:
            result += curr.symbol
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
def load_map_from_file(filepath):
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