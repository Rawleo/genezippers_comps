from constants import *
import os

def file_size(file_path):

    return os.path.getsize(file_path) / (2 ** 20)


def compression_ratio(orig_file_path, enc_file_path):

    orig_file_size = file_size(orig_file_path)
    enc_file_size = file_size(enc_file_path)

    return round(enc_file_size / orig_file_size, 4)


def space_saving(orig_file_path, enc_file_path):

    comp_ratio = compression_ratio(orig_file_path, enc_file_path)

    return round(1 - comp_ratio, 4)

