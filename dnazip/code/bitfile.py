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

    @params:
    * bit_string (str): a sequence of '0' and '1' characters representing bytes.

    @return:
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
    """
    Read a Variable Integer (VINT) from a bit string starting at bit index `start`.
    The VINT is encoded in 8-bit bytes where the MSB (bit 0 of each byte) is a
    continuation flag: '1' means more bytes follow, '0' marks the final byte.
    The remaining 7 bits of each byte are payload (little-endian in 7-bit groups).

    @param:
     * bit_string (str): sequence of '0'/'1' characters representing bytes.
     * start (int): bit index at which to begin reading (must be a multiple of 8
                    for correct byte-alignment).
    @return:
     * num (int): decoded integer value
     * bits_used (int): number of bits consumed (multiple of 8)
    """
    num = 0             # accumulated integer value from 7-bit groups
    shift = 0           # number of bit positions to shift the next 7-bit group
    bytes_used = 0      # number of bytes consumed while decoding
    i = start           # current bit index into bit_string

    # Process one byte (8 bits) at a time as long as a full byte is available
    while i + 8 <= len(bit_string):
        byte = bit_string[i:i+8]   
        bits = byte[1:]              
        bit_val = int(bits, 2)      
        num |= (bit_val << shift)    

        shift += 7                
        bytes_used += 1             
        i += 8                  

        # If MSB is '0', this byte is the final VINT byte; stop reading more bytes
        if byte[0] == '0':
            break

    bits_used = bytes_used * 8       # total bits consumed
    return num, bits_used


def export_as_binary(export_name_with_extension, bitstr):
    """
    Convert a bit string to bytes and append those bytes to a file.

    @param:
    * export_name_with_extension (str) - destination filename (with extension)
    * bitstr (str) - string of '0' and '1' characters to write as binary

    Note:
    * The bit string is interpreted as a big-endian integer and then converted
      to the minimal number of bytes required to represent it. If the bit
      string length is not a multiple of 8, the conversion pads the highest
      bits as needed by the integer-to-bytes conversion.
    """
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
