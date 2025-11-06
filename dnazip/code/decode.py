import pandas as pd
import numpy as np
from constants import *
from bitfile import *


def add_padding(bit_string):
    """
    Remove padding bits from the beginning of a bit string.
    Padding bits are leading zeros before the first '1'.
    
    @params:
    * bit_string: String of binary digits
        
    @return:
    * bit_string[padding:] - Bit string with padding removed
    """
    # Initialize padding counter
    padding = 0
    
    # Count leading zeros until first '1' is found
    while bit_string[padding] != '1':
        padding += 1

    # Return bit string with padding removed
    return bit_string[padding:]


def readBinFile(file_to_bin_file):
    """
    Read a binary file and convert its contents to a bit string
    
    @params:
    * file_to_bin_file: Path to the binary file to read
    
    @return:
    * bit_string: String of binary digits representing the file contents
    """
    # Open file in binary read mode
    with open(file_to_bin_file, 'rb') as f:
        # Read all binary data from file
        binary_data = f.read()
        
        # Convert binary data to string of bits
        bit_string = BytesToBitString(binary_data)

    return bit_string


def parse_vints(bit_string, size):
    """
    Parse variable-length integers (VINTs) from a bit string
    
    @params:
    * bit_string: String of binary digits
    * size: Number of VINTs to parse
    
    @return:
    * items: List of parsed integers
    * shifted_bits: Total number of bits read
    """
    # Initialize empty list for parsed integers
    items = []
    # Track total bits shifted/read
    shifted_bits = 0

    # Parse 'size' number of VINTs
    for _ in range(size):
        # Read one VINT and get its value and bits consumed
        pos, bits_shifted = readBitVINT_from(bit_string, shifted_bits)
        # Update total bits shifted
        shifted_bits += bits_shifted
        # Add parsed integer to results list
        items.append(pos)

    return items, shifted_bits