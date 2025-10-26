from vint import *
from bitfile import *
from decode import *
from huffman import *
from constants import *
import pandas as pd


'''
Build the required Huffman encoding map as a dictionary, then export
the encoding map to a text file for use by the decoder. 
@params: 
 * variants_df - dataframe of all of the variant information.
@return:
 * encoding_map - a dictionary containing unique k-mer symbols with their corresponding frequency.
'''
def create_and_export_huffman_map(variants_df):
    # Grab insertion dataframe for all chromosomes
    insr_df = variants_df.where(variants_df['var_type'] == 2).dropna()
    
    # Split insertions into relevant nucleotides
    insr_df["var_info"] = insr_df["var_info"].apply(lambda x: x.split('/')[1])
    
    # Concatenate all insertion sequences for Huffman coding
    ins_seq = ''.join(insr_df["var_info"].astype(str).tolist())

    # Produce encoding_map
    encoding_map = run_insr_huffman(ins_seq, K_MER_SIZE)
    
    # Export and save the encoding_map dictionary
    export_as_txt(f"{TREE_PATH}", encoding_map)
    
    return encoding_map


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
    ins_seq_bitstr  = encode_insertions(encoding_map, ins_seq_kmer)
    
    return ins_seq_bitstr


'''
Append the whole insertion sequence of each chromosome to a file.
@params: 
 * chr - the current chromosome.
 * ins_seq - the insertion sequence of the given chromosome to export. 
@return:
 * None, but appends the original insertion sequences of each chromosome to the file.
'''
def create_insertion_seq_file(chr, ins_seq):
    result = f"{chr} Insertion Sequence: " + ins_seq + '\n'
    append_as_txt(INS_SEQ_CONCAT, result)
    
    
'''
Append the whole insertion sequence of each chromosome to a file.
@params: 
 * chr - the current chromosome.
 * ins_seq - the insertion sequence of the given chromosome to export. 
@return:
 * None, but appends the original insertion sequences of each chromosome to the file.
'''
def create_insertion_dec_file(chr, ins_seq):
    result = f"{chr} Insertion Sequence: " + ins_seq + '\n'
    append_as_txt(INS_DEC_CONCAT, result)
    

'''
Encodes the insertion data for a given chromosome into its respective bitstring and VINTs.
@params: 
 * insr_df - insertion dataframe of the current chromosome.
 * encoding_map - the Huffman encoding map dictionary.
 * k_mer_size - the integer size of the k-mers.
@return:
 * insr_size_vint - VINT representation of the total number of insertions in the dataframe.
 * pos_bitstr - Concatenated bitstring of all of the positions encoded as VINTs.
 * len_bitstr - Concatenated bitstring of all of the insertion lengths encoded as VINTs.
 * bitstr_len_vint - VINT representation of the total length of 1's and 0's in the bitstr. 
 * ins_seq_bitstr - Encoding of the concatenated insertion sequences as 1's and 0's.
'''
def encode_ins(insr_df, encoding_map, k_mer_size):
    # Current chromosome
    chr = insr_df["chr"].values[0]
    
    # Calculate size of insertions and convert to VINT
    insr_size_vint = writeBitVINT(insr_df.shape[0])
    
    # Convert positions to VINTs
    insr_df["pos"] = insr_df["pos"].astype(int).apply(writeBitVINT)
    
    # Split insertions into relevant nucleotides
    insr_df["var_info"] = insr_df["var_info"].apply(lambda x: x.split('/')[1])
    
    # Calculate length of each insertion sequence
    insr_df["var_length"] = insr_df["var_info"].apply(lambda x: len(x)).apply(writeBitVINT)

    # Concatenate all insertion sequences for Huffman coding
    ins_seq = ''.join(insr_df["var_info"].astype(str).tolist())
    
    # Concatenate all position VINTs
    pos_bitstr = ''.join(insr_df["pos"].astype(str).tolist())
    
    # Concatenate all position length VINTs
    len_bitstr = ''.join(insr_df["var_length"].astype(str).tolist())
    
    # Encode remainder bits
    # remainder_bits = ins_seq[:]
    # print("Extra:", len(ins_seq) % k_mer_size)
    remainder_nuc_len = len(ins_seq) % k_mer_size
    
    remainder_nucs = ins_seq[len(ins_seq) - remainder_nuc_len:]
    # print(chr, ", extra Nucs:", remainder_nucs)
    
    remainder_bitstr = ''.join([(NUC_ENCODING[x]) for x in remainder_nucs])
    # print(remainder_bitstr)

    # Huffman encoding of the current chromosome's insertion sequences
    ins_seq_bitstr  = ins_seq_to_bitstr(ins_seq, encoding_map, k_mer_size)
    ins_seq_bitstr += remainder_bitstr

    # Create file with before encoding output
    create_insertion_seq_file(chr, ins_seq)

    # VINT for bitstring length
    bitstr_len_vint = writeBitVINT(len(ins_seq_bitstr))
        
    return insr_size_vint, pos_bitstr, len_bitstr, bitstr_len_vint, ins_seq_bitstr


'''
Decodes the insertion data for a given chromosome into its respective bitstring and VINTs.
@params: 
 * bit_string - insertion dataframe of the current chromosome.
 * huffman_root - the Huffman tree necessary for decoding traversal.
 * chr - the current chromosome.
@return:
 * ins_df - insertion dataframe with the sorted and decoded nucleotide information.
 * bit_string - the rest of the bit_string to decode further.
'''
def decode_ins(bit_string, huffman_root, chr):
    ### Get number of position, length, nucleotide rows.
    ins_size, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]
    # print("Ins Size: " + str(ins_size))

    ### All INS positions
    ins_pos, ins_pos_bits = parse_vints(bit_string, ins_size)
    bit_string = bit_string[ins_pos_bits:]
    # print("Insertion Positions Decoded")

    ### All INS lengths
    ins_lens, ins_len_bits = parse_vints(bit_string, ins_size)
    bit_string = bit_string[ins_len_bits:]

    ### Length of INS bitstring
    bitstr_len, bits_shifted = readBitVINT(bit_string)
    bit_string = bit_string[bits_shifted:]
    # print("Bitstr Len: " + str(bitstr_len))

    ### Process INS bitstring
    huffman_bitmap = bit_string[:bitstr_len]
    bit_string = bit_string[bitstr_len:]

    ### Final insertion sequence
    ins_seq, buffer  = decode_huffman(huffman_bitmap, huffman_root) 
    
    # Process non-Huffman encoded nucleotides
    extra_nucs = ''.join([TWO_BIT_ENCODING[buffer[(i*2):((i*2)+2)]] for i in range(len(buffer) // 2)])

    # Append Huffman portion with non-Huffman 
    ins_seq += extra_nucs
    
    # Export decoded insertion sequences for each chr
    create_insertion_dec_file(chr, ins_seq)
    
    # Create dictionary to pass into the data frame
    ins_data = {
        "chr" : chr,
        "ins_pos" : ins_pos,
        "ins_lens" : ins_lens,
        "start_pos" : None,
        "end_pos" : None,
        "ins_nucs" : None,
    }

    # Create data frame with the above information
    ins_df = pd.DataFrame(ins_data)
    
    # Get the end position for indexing the insertion sequence
    ins_df['end_pos'] = ins_df.ins_lens.cumsum()
    
    # Get the start position for indexing the insertion sequence
    ins_df['start_pos'] = ins_df.end_pos - ins_df.ins_lens
    
    # Apply row-wise the respective nucleotides given the range
    ins_df['ins_nucs'] = ins_df.apply(lambda x: ins_seq[x.start_pos : x.end_pos], axis=1)
        
    return ins_df, bit_string


def main():
    return
    
    
if __name__ == "__main__":
    main()