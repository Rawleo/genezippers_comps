import re
from config import *
from huffman import *


'''
 * Author: Ryan Son
 * Modified Date: Nov. 2, 2025
 * File: k_mer_huffman.py
 * Summary: Huffman encoding/decoding of an entire human genome dividing it into k-mers.
'''


'''
Transform input text into an array of k-mers, or k-symbol items.
@params: 
 * seq - the text sequence to transform.
 * k_mer_size - the integer size of the k-mer.
@return:
 * k_mer_array - an array of k-mers that will be used for Huffman encoding.
'''
def seq_to_kmers(seq, k_mer_size):
    k = k_mer_size
    regex_k = k * '.'
    k_mer_array = re.findall(regex_k, seq)

    return k_mer_array


'''
Encode an insertion sequence into its bitstring representation with a 
Huffman encoding map dictionary.
@params: 
 * seq - string to be processed to into an array of k-mers and then bitstring.
 * encoding_map - the Huffman encoding map dictionary.
 * k_mer_size - the size of the k-mers.
@return:
 * seq_bitstr - the final encoded bitstring represented as 1's and 0's.
'''
def seq_to_bitstr(seq, encoding_map, k_mer_size):
    seq_kmer = seq_to_kmers(seq, k_mer_size)
    seq_bitstr = encode_k_mer_array(encoding_map, seq_kmer)

    return seq_bitstr


'''
Encode the k_mer_array into a string of bits using Huffman encoding.
@params: 
 * encoding_map - the Huffman encoding dictionary to encode the array.
 * k_mer_array - an array of k-mers that will be used for huffman encoding.
@return:
 * bitstr - Python string containing 1's and 0's.
'''
def encode_k_mer_array(encoding_map, k_mer_array):
    bitstr = ""

    for k_mer in k_mer_array:

        bitstr += encoding_map[k_mer]

    return bitstr


'''
Function used to create the Huffman encoding map for encoding. 
@params: 
 * ins_seq - the text sequence to transform.
 * k_mer_size - the integer size of the k-mer.
@return: 
 * encoding_map - the Huffman encoding dictionary to encode the array.
 * len(k_mer_array) - number of k_mers encoded.
'''
def run_k_mer_huffman(seq, k):
    encoding_map = {}
    k_mer_array  = seq_to_kmers(seq, k)
    frq_dict = build_frequency_dict(k_mer_array)
    huffman_root = build_huffman_tree(frq_dict)

    map_encodings(huffman_root, encoding_map, "")
    export_as_txt(str(HUFFMAN_TREE), encoding_map)

    seq_bitstr = encode_k_mer_array(encoding_map, k_mer_array)

    return seq_bitstr, encoding_map, len(k_mer_array)


def huff_encoding():
    sequence_data = read_in_file(GENOME_FILE)

    bitstr, encoding_map, k_mer_array_len = run_k_mer_huffman(
        sequence_data, K_MER_SIZE)

    remainder_nuc_len = len(sequence_data) % K_MER_SIZE
    remainder_nucs = sequence_data[len(sequence_data) - remainder_nuc_len:]
    remainder_bitstr = ''.join([(NUC_ENCODING[x]) for x in remainder_nucs])
    
    k_mer_vint = writeBitVINT(k_mer_array_len)
    bitstr += remainder_bitstr
    final_bitstr = k_mer_vint + bitstr

    export_as_binary(str(GENOME_BIN), final_bitstr)
    

def huff_decoding():
    bit_string                      = read_bin(str(GENOME_BIN))
    bit_string                      = add_padding(bit_string)
    number_of_kmers, bits_shifted   = readBitVINT(bit_string)
    bit_string                      = bit_string[bits_shifted:]
    encoding_map                    = load_dict_from_file(str(HUFFMAN_TREE))
    huffman_root                    = reconstruct_huffman_tree(encoding_map)
    sequence, buffer                = decode_huffman(bit_string, huffman_root, number_of_kmers)

    # Process non-Huffman encoded nucleotides
    extra_nucs = ''.join([
        TWO_BIT_ENCODING[buffer[(i * 2):((i * 2) + 2)]]
        for i in range(len(buffer) // 2)
    ])

    sequence += extra_nucs

    export_as_txt(str(DECODED_FILE), sequence)


def main():
    huff_encoding()
    huff_decoding()


if __name__ == "__main__":
    main()
