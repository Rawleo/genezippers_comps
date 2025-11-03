from constants import *
import pandas as pd
import os
import time
import datetime as dt

def file_size(file_path):

    return os.path.getsize(file_path) / (2 ** 20)


def compression_ratio(orig_file_path, enc_file_path):

    orig_file_size = file_size(orig_file_path)
    enc_file_size = file_size(enc_file_path)

    return round(enc_file_size / orig_file_size, 4)


def space_saving(orig_file_path, enc_file_path):

    comp_ratio = compression_ratio(orig_file_path, enc_file_path)

    return round(1 - comp_ratio, 4)


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
    return round(end_time - start_time, 4)


'''
Appends data to a csv if it exists, otherwise creates one. 
@params: 
 * type - type string (0=ENCODE, 1=DECODE)
 * time_type - time type string (0=CPU, 1=WALL)
@return:
 * difference - between the two inputs
'''
def record_timings(type, time_type, total_time, csv_path):
    
    enc_file_size  = file_size(ENC_FILE_PATH)
    tree_file_size = file_size(TREE_PATH)
    
    # Determine type string (0=ENCODE, 1=DECODE)
    if (type == 0):
        op_type_str = "ENCODE"
    else: 
        op_type_str = "DECODE"

    # Determine time type string (0=CPU, 1=WALL)
    if (time_type == 0):
        time_type_str = "CPU"
    else: 
        time_type_str = "WALL"
 
    time_data = {
        'variant_name' : VARIANT_NAME,
        'datetime' : [dt.datetime.now()],
        'k_mer_size' : [K_MER_SIZE],
        'type' : [op_type_str],     
        'time_type' : [time_type_str],
        'time (sec)' : [round(total_time, 4)],
        'file_size (MB)' : [round(enc_file_size, 4)],
        'tree_size (MB)' : [round(tree_file_size, 4)],
        'DELTA_POS' : DELTA_POS,
        'DBSNP_ON' : DBSNP_ON,
        'HUFFMAN_ON' : HUFFMAN_ON,
    }
     
    time_row_df = pd.DataFrame(time_data)
    
    file_exists = os.path.exists(csv_path)
    
    time_row_df.to_csv(
        csv_path, 
        mode='a',             
        index=False,          
        header=not file_exists
    )