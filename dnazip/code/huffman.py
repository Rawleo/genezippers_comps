'''
 * Author: Ryan Son
 * Modified Date: Oct. 7, 2025
 * File: huffman.py
 * Summary: Given an input of human genomic sorted variants, it will map insertions 
            using the Huffman coding algorithm and output a huffman tree with an associated 
            encoding dictionary.
'''

import re, sys, argparse, os, vint, ast
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

        
def insertions_to_kmers(ins_seq, k_mer_size):
    
    k             = k_mer_size
    regex_k       = k * '.'
    k_mer_array   = re.findall(regex_k, ins_seq)
    
    return k_mer_array  


def encode_insertions(encoding_map, k_mer_array):
    
    ins_bitstr    = ""
    
    for k_mer in k_mer_array:
        
        ins_bitstr += encoding_map[k_mer]
        
    return ins_bitstr


def export_as_txt(export_name, text):
    with open(export_name + ".txt", "w") as file:
        file.write(str(text))
        

def decode_huffman(encoded_text, root):
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


def load_map_from_file(filepath):
    """
    Reads a text file containing a Python dictionary literal
    and parses it into a dict object.
    
    Args:
        filepath: The path to the text file.

    Returns:
        The parsed dictionary.
    """
    with open(filepath, 'r') as f:
        file_content = f.read()
        
    encoding_map = ast.literal_eval(file_content)
    
    return encoding_map


def reconstruct_huffman_tree(encoding_map):
    """
    Reconstructs the Huffman tree from a given encoding map,
    using the user-provided Node class.
    
    Args:
        encoding_map: A dictionary mapping symbols to their
                      binary Huffman code (e.g., {'A': '0', 'B': '11'}).

    Returns:
        The root node (Node) of the reconstructed tree.
    """

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
        
        
def run_huffman(ins_seq, k_mer_size):
    
    # Testing if extra_nuc code worked
    # ins_seq += "ATC"
    
    encoding_map    = {}
    k               = k_mer_size
    k_mer_array     = insertions_to_kmers(ins_seq, k)
    ins_frq_dict    = build_frequency_dict(k_mer_array)
    huffman_root    = build_huffman_tree(ins_frq_dict)
    
    map_encodings(huffman_root, encoding_map, "")
        
    extra_nuc_bitstr    = "".join(NUC_ENCODING[x] for x in ins_seq[:(len(ins_seq) % k)])
    insr_seq_bitstr     = encode_insertions(encoding_map, k_mer_array)
    insr_seq_bitstr     += extra_nuc_bitstr
        
    return insr_seq_bitstr, encoding_map