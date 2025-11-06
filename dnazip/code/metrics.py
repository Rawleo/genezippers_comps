from constants import *
import pandas as pd
import os
import time
import datetime as dt


def file_size(file_path):
    '''
    Gets the file size in MB of a file

    @params:
    * file_path: path to the file

    @return:
    * size in megabytes (MB)
    '''
    return os.path.getsize(file_path) / (2 ** 20)


def compression_ratio(orig_file_path, enc_file_path):
    '''
    Calculates compression ratio between original and encoded files

    @params:
    * orig_file_path: path to original file
    * enc_file_path: path to encoded file

    @return:
    * ratio of encoded size / original size, rounded to 4 decimals
    '''
    orig_file_size = file_size(orig_file_path)
    enc_file_size = file_size(enc_file_path)
    return round(enc_file_size / orig_file_size, 4)


def space_saving(orig_file_path, enc_file_path):
    '''
    Calculates space savings percentage from compression

    @params:
    * orig_file_path: path to original file
    * enc_file_path: path to encoded file 

    @return:
    * space savings as percentage (1 - compression ratio), rounded to 4 decimals
    '''
    comp_ratio = compression_ratio(orig_file_path, enc_file_path)
    return round(1 - comp_ratio, 4)


def record_current_times():
    '''
    Gets the current times for the program.

    @return:
    * wall_time: current wall time 
    * cpu_time: current cpu time
    '''
    wall_time = time.time()
    cpu_time = time.process_time()
        
    return cpu_time, wall_time


def time_difference(end_time, start_time):
    '''
    Returns the difference between the two values

    @params: 
    * end_time
    * start_time
    
    @return:
    * difference: between the two inputs
    '''
    return round(end_time - start_time, 4)


def record_timings(type, time_type, total_time, csv_path):
    '''
    Appends data to a csv if it exists, otherwise creates one. 

    @params: 
    * type: type string (0=ENCODE, 1=DECODE)
    * time_type: time type string (0=CPU, 1=WALL)

    @return:
    * difference: between the two inputs
    '''
    
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