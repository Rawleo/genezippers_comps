'''
 * Author: Ryan Son
 * Date: Sept. 18, 2025
 * File: analysis.py
 * Summary: This script calculates the size of the original text files and the size of the
            encoded bit_strings. It will then calculate the compression ratio and space savings
            of each pair of files. These values are then used to compute the Excel charts used 
            in the HuffmanCoding.docx file. 
'''

import huffman_orig as h

'''
Counting the total number of characters in the input string.
@params:
 * input_text - the input text string to be read
@returns:
 * count - the total number of characters in the text file
'''
def count_char(input_text):
    return len(input_text)

'''
Compute the compression ratio between the compressed file and the original file
@params:
 * encoded_size - the size of the file in bits
 * orginal_size - the size of the file in bits
@returns:
 * The ratio of the compression algorithm
'''
def compression_ratio(encoded_size, original_size):
    return round(encoded_size/original_size, 2)

def main():
    file_list = ["DNA", "Emma", "random", "sample_text"]
    
    for filename in file_list:
        input_text   = h.read_in_file("input_files/" + filename + ".txt")
        encoded_text = h.read_in_file("export_files/" + filename + "_encoded.txt")
        size_in_bits = count_char(input_text) * 8
        size_in_bits_encoded = count_char(encoded_text)
                
        size_in_bytes = size_in_bits / 8
        size_in_bytes_encoded = size_in_bits_encoded / 8
        
        ratio = compression_ratio(size_in_bits_encoded, size_in_bits)
        savings = round(1 - ratio, 2)

        print(filename)
        print("original", size_in_bits, "bits")
        print("encoded", size_in_bits_encoded, "bits")
        print("original", size_in_bytes, "bytes")
        print("encoded", size_in_bytes_encoded, "bytes")
        print("Compression Ratio:", ratio)
        print("Savings:", savings * 100, "%")
        print()
    
if __name__ == "__main__":
    main()