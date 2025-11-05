import os

def writeBitVINT(num):
    '''
    Turns an integer value into a variable integer (VINT).
    @params: 
    * num - number (int) which should be transformed into a VINT 
    @return:
    * bit_string - (str) binary representation of VINT
    '''

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



def BytesToBitString(bytes_obj):
    '''
    Turns bytes object in to bit string.
    @params: 
    * bytes_obj - bytes object (bin) which should be transformed into a bitstring
    @return:
    * (str) binary representation of bytes object
    '''

    return ''.join(format(byte, '08b') for byte in bytes_obj)


def readBitVINT(bit_string):
    """
    Read the first Variable Integer (VINT) from a bit string.

    Params:
     * bit_string (str): a sequence of '0' and '1' characters representing bytes.

    Returns:
     * num (int): decoded integer value
     * bits_used (int): number of bits consumed from bit_string (multiple of 8)
    """

    num = 0          # accumulated integer value
    shift = 0        # bit-position shift for next 7-bit group
    bytes_used = 0   # number of bytes consumed

    # Process bit_string in 8-bit chunks (one byte at a time)
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        # If we don't have a full byte available, stop parsing
        if len(byte) < 8:
            break

        # lower 7 bits are payload (bits 1..7), MSB (byte[0]) is continuation flag
        bits = byte[1:]
        bit_val = int(bits, 2)

        # merge the 7-bit payload into the result at the current shift
        num |= (bit_val << shift)

        # next payload (if any) will occupy the next 7 bits
        shift += 7
        bytes_used += 1

        # if MSB is '0', this is the final byte of the VINT
        if byte[0] == '0':
            break

    bits_used = bytes_used * 8
    return num, bits_used

def readBitVINT_from(bit_string, start):
    num = 0
    shift = 0
    bytes_used = 0
    i = start

    while i + 8 <= len(bit_string):
        byte = bit_string[i:i+8]
        bits = byte[1:]
        bit_val = int(bits, 2)
        num |= (bit_val << shift)

        shift += 7
        bytes_used += 1

        i += 8
        if byte[0] == '0':
            break

    bits_used = bytes_used * 8
    return num, bits_used


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
def export_as_binary(export_name_with_extension, bitstr):
    
    byte_value = int(bitstr, 2).to_bytes((len(bitstr) + 7) // 8, byteorder='big')
    
    with open(export_name_with_extension, "ab") as file:
        file.write(byte_value)
        


def remove_file_if_exists(filepath):
    '''
    Deletes a file if it exists. Useful for files that are
    appended to.
    @params: 
    * filepath - file path (str) to the file to delete. 
    @return:
    * None, deletes the file if it exists.
    '''

    if os.path.exists(filepath):

        print("Removing:", filepath)
        os.remove(filepath)

    else:

        print("This file does not exist:", filepath)
        print("Continuing...") 
