import os
import csv
from collections import Counter
import operator

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

# main log analiser function
def analise_logs_for_barcodes(log_input, log_output):
    run_name = ''
    run_line_check = 'Checking Barcode: '
    test_buffer = []

    for log in log_input:
        testBed = log[0]
        testLogDir = log[1]

        for file in dir_log_files(testLogDir):
            print('Now in: ', file)
            with open(file, 'rt') as log_input:
                for line in log_input:
                    if run_line_check in line:
                        runname_old = run_name
                        fields = line.split(';')
                        run_name = fields[4].split('\'')[1]
                        # if not run_name == runname_old:
                        run_time = fields[1].split('.')[0].replace('-', '').replace('T','').replace(':', '')
                        if not run_name:
                            test = ['None',testBed , run_time]
                        else:
                            test = [run_name, testBed, run_time]
                        test_buffer.append(test)
            log_input.close()

    return test_buffer


# result analise function
def analise_TestBuffer(test_buffer):
    result = Counter(map(operator.itemgetter(0), test_buffer))
    return sorted(result.items(), key = operator.itemgetter(1))

    # print('The motor: ', element.key(),' has been run: ' , element.value(), ' times.')



# this is the original call to function
log_output = 'M:\Projects\_Stubler_EOL_logs\\'
log_input = [['EOL1', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL1\mes\\base\\',],\
     ['EOL2', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL2\log mes\\base\\'],\
          ['EOL3', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL3\log mes\\base\\']]


test_buffer = analise_logs_for_barcodes(log_input, log_output)

analised_buffer = analise_TestBuffer(test_buffer)
analised_buffer.reverse()
write_buffer('preliminary analises', analised_buffer, log_output)

