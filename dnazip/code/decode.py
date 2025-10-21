import pandas as pd
import numpy as np
import os
import ast
from constants import *
from bitfile import *
from huffman import *

VARIANT_NAME    = 'HG004_GRCh38'
ENC_FILE_PATH   = f"../data/output/{VARIANT_NAME}_Encoded.bin"
CHR_FILE_PATH   = '../data/chr/'
TREE_PATH       = f"../data/huffman_trees/{VARIANT_NAME}.txt"

def decode(file_to_bin_file):
    
    with open(file_to_bin_file, 'rb') as f:
        binary_data = f.read()

        bit_string = BytesToBitString(binary_data)

        bitmap_size, bit_string = readBitVINT(bit_string)
        print(bitmap_size)
        
# def decode_insertions(insertion_stream):
    
#     insr_size_vint 
#     pos_bitstr 
#     len_bitstr
#     bitstr_len_vint
#     ins_seq_bitstr
    
#     return

def decode_deletions():
    
    return

def createRefGen(chr): 
    
    refGen = []
    
    with open(CHR_FILE_PATH + chr + ".fa", 'r', encoding='utf-8') as f:
        f.readline()
        
        while True: 
            char=f.read(1)
            
            if not char:
                break
            if char != '\n':
                refGen.append(char)
        
    return refGen


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
        
        
def main():   
    
    encoding_map = load_map_from_file(TREE_PATH)
    root = reconstruct_huffman_tree(encoding_map)
    
    map_encodings(root, encoding_map, "")
    
    print(encoding_map)
  
    
       
if __name__ == "__main__":
    main()