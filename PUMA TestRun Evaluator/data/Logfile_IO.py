import os
import csv

# function to get a list of files from a directory
def dir_log_files(f_dir):
    file_list = []
    for file in os.listdir(f_dir):
        file_list.append(os.path.join(f_dir, file))
    file_list = sorted(file_list, key = last_14chars)
    return(file_list)

# function key for the last 14 char sorting key
def last_14chars(x):
    '''
    Returns the last 14 characters.
    '''
    return(x[-14:])

# function to write a result .csv file
def write_buffer(name, buffer, o_dir):
    """
    This function takes an index and a buffer.
    The buffer is just an iterable of iterables (ex a list of lists)
    Each buffer item is a row of values.
    """

    o_filename = o_dir + name + '.csv'

    with open(o_filename, 'w', newline ='') as output:
        writer = csv.writer(output)
        writer.writerows(buffer)
    output.close()