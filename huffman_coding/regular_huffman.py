from huffman import *
from config import *
from metrics import *


ONE_MER = "_Regular"


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
def decode_text(encoded_text, root):
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


def run_encode():
    sequence_data   = read_in_file(GENOME_FILE)
    freq_dict       = build_frequency_dict(sequence_data)
    encoding_map    = {}
    root            = build_huffman_tree(freq_dict)
    
    map_encodings(root, encoding_map, "")
    
    encoded_text    = encode_text(encoding_map, sequence_data)
    length_vint     = writeBitVINT(len(encoded_text))
    final_bitstr    = length_vint + encoded_text
    
    export_as_txt(str(HUFFMAN_TREE) + ONE_MER, encoding_map)
    export_as_binary(str(GENOME_BIN) + ONE_MER, final_bitstr)
    

def run_decode():
    bit_string              = read_bin(str(GENOME_BIN) + ONE_MER)
    bit_string              = add_padding(bit_string)
    length, bits_shifted    = readBitVINT(bit_string)
    bit_string              = bit_string[bits_shifted:]
    encoding_map            = load_dict_from_file(str(HUFFMAN_TREE) + ONE_MER)
    huffman_root            = reconstruct_huffman_tree(encoding_map)
    sequence                = decode_text(bit_string, huffman_root)
    
    export_as_txt(str(DECODED_FILE) + ONE_MER, sequence)


'''
Run the program.
'''
def main():
    
    k = 0
    
    print("Encoding:", GENOME_CHOICE)
    cpu_start, wall_start = record_current_times()
    run_encode()
    cpu_end, wall_end = record_current_times()
    record_timings(0, 0, time_difference(cpu_end, cpu_start), TIME_CSV_PATH, k)
    record_timings(0, 1, time_difference(wall_end, wall_start), TIME_CSV_PATH, k)
    cpu_start, wall_start = record_current_times()
    print("Decoding:", GENOME_CHOICE)
    run_decode()
    cpu_end, wall_end = record_current_times()
    record_timings(1, 0, time_difference(cpu_end, cpu_start), TIME_CSV_PATH, k)
    record_timings(1, 1, time_difference(wall_end, wall_start), TIME_CSV_PATH, k)
    

if __name__ == "__main__":
    main()
