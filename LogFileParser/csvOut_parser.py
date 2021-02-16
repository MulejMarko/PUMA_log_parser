import csv
import os

NEW_LOG_DELIMITER = 'Checking Barcode: '

def write_buffer(name, time, buffer):
    """
    This function takes an index and a buffer.
    The buffer is just an iterable of iterables (ex a list of lists)
    Each buffer item is a row of values.
    """
    name_time = name + "_" + time
    filename = 'M:\Projects\LogFileParser\msg\{}\{}.csv'.format(name, name_time)
    directory = 'M:\Projects\LogFileParser\msg\{}\\'.format(name)

    try:
        os.stat(directory)
    except:
        os.mkdir(directory)  

    with open(filename, 'w', newline ='') as output:
        writer = csv.writer(output)
        writer.writerows(buffer)

current_buffer = []
_index = 1

run_name = "none"
run_time =""

with open('M:\Projects\LogFileParser\msg\messages_base.prn', 'rt') as log_input:
    for line in log_input:
        # will deal ok with multi-space as long as
        # you don't care about the last column
        fields = line.split(';')
        if not NEW_LOG_DELIMITER in line or not current_buffer:
            # If it's the first line (the current_buffer is empty)
            # or the line does NOT contain "MYLOG" then
            # collect it until it's time to write it to file.
            current_buffer.append(fields)
        else:
            write_buffer(run_name, run_time, current_buffer)
            _index += 1
            current_buffer = [fields]  # EDIT: fixed bug, new buffer should not be empty

        if NEW_LOG_DELIMITER in line:
            run_name = fields[4].split('\'')[1]
            run_time = fields[1].split('.')[0].replace('-', '').replace('T','').replace(':', '')
    if current_buffer:
        # We are now out of the loop,
        # if there's an unwritten buffer then write it to file.
        write_buffer(run_name, run_time, current_buffer)
