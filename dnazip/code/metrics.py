from constants import *
import os
import time

def file_size(file_path):

    return os.path.getsize(file_path)


def compression_ratio(orig_file_path, enc_file_path):

    orig_file_size = file_size(orig_file_path)
    enc_file_size = file_size(enc_file_path)

    return round(enc_file_size / orig_file_size, 3)


def space_savings(orig_file_path, enc_file_path):

    comp_ratio = compression_ratio(orig_file_path, enc_file_path)

    return round(1 - comp_ratio, 3)


'''
Gets the current times for the program.
@params: 
 * None
@return:
 * wall_time - current wall time 
 * cpu_time - current cpu time
'''
def record_current_times():
    wall_time = time.time()
    cpu_time = time.process_time()
        
    return cpu_time, wall_time


'''
Returns the difference between the two values
@params: 
 * end_time
 * start_time
@return:
 * difference - between the two inputs
'''
def time_difference(end_time, start_time):
    return end_time - start_time

