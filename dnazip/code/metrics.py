from constants import *
import os

def get_file_size(file_path):

    return os.path.getsize(file_path)


def compression_ratio(orig_file_path, enc_file_path):

    orig_file_size = get_file_size(orig_file_path)
    enc_file_size = get_file_size(enc_file_path)

    return round(enc_file_size / orig_file_size, 3)


def space_saving(orig_file_path, enc_file_path):

    compression_ratio =  compression_ratio(orig_file_path, enc_file_path)

    return round(1 - compression_ratio, 3)

