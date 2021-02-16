import csv
import os

# function to get a list of files from a directory
def dir_log_files(f_dir):
    file_list = []
    for file in os.listdir(f_dir):
        file_list.append(os.path.join(f_dir, file))
    file_list = sorted(file_list, key = last_14chars)
    return(file_list)

# function key for the last 14 char sorting key
def last_14chars(x):
    return(x[-14:])

# function to write a sequence of result folders and results in said folders
def write_buffer(name, time, buffer, o_dir, testBed):
    """
    This function takes an index and a buffer.
    The buffer is just an iterable of iterables (ex a list of lists)
    Each buffer item is a row of values.
    """
    name_time = name + "_" + time
    o_directory = o_dir + name + '\\'
    o_filename = o_directory + name_time + '_' + testBed + '.csv'

    try:
        os.stat(o_directory)
    except:
        os.mkdir(o_directory)  

    with open(o_filename, 'w', newline ='') as output:
        writer = csv.writer(output)
        writer.writerows(buffer)
    output.close()

def parse_logs(testBed, log_input, log_output):
    NEW_LOG_DELIMITER = 'Checking Barcode: '

    run_name ="None"
    run_time =""

    current_buffer = []

    for file in dir_log_files(log_input):
        print('Now in: ', log_input)
        _index = 1
        with open(file, 'rt') as log_input:
            for line in log_input:
                # will deal ok with multi-space as long as
                # you don't care about the last column
                fields = line.split(';')
                if not NEW_LOG_DELIMITER in line or not current_buffer:
                    # If it's the first line (the current_buffer is empty)
                    # or the line does NOT contain "MYLOG" then
                    # collect it until it's time to write it to file.
                    if any(i in fields[0] for i in ['(A)', '(E)', '(I)', '(W)']):
                        current_buffer.append(fields)
                else:
                    write_buffer(run_name, run_time, current_buffer, log_output, testBed)
                    _index += 1
                    current_buffer = [fields]  # EDIT: fixed bug, new buffer should not be empty
                
                if NEW_LOG_DELIMITER in line:
                    run_name = fields[4].split('\'')[1]
                    if not run_name:
                        run_name = "None"
                    run_time = fields[1].split('.')[0].replace('-', '').replace('T','').replace(':', '')

        if current_buffer:
            # We are now out of the loop,
            # if there's an unwritten buffer then write it to file.
            write_buffer(run_name, run_time, current_buffer, log_output, testBed)
        log_input.close()


# this is the original call to function
log_output = 'M:\Projects\_Stubler_EOL_logs\Test_Files\\'
log_input = [['EOL1', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL1\mes\\base\\',],\
     ['EOL2', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL2\log mes\\base\\'],\
          ['EOL3', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL3\log mes\\base\\']]
          
for l_input in log_input:
    parse_logs(l_input[0], l_input[1], log_output)