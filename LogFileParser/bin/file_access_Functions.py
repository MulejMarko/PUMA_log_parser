import os
import csv

# function to get a list of files from a directory
def dir_log_files(f_dir):
    file_list = []
    for file in os.listdir(f_dir):
        file_list.append(os.path.join(f_dir, file))
    file_list = sorted(file_list, key = last_19chars)
    return(file_list)

# function key for the last 14 char sorting key
def last_19chars(x):
    return(x[-19:])

# .csv report writing function
def write_reports_in_file(rep_dictionary, analises_log, o_filename):
    
    with open(o_filename, 'a', newline ='') as output:
        writer = csv.writer(output)
        writer.writerow(rep_dictionary.keys())
        writer.writerow(rep_dictionary.values())

        writer.writerow([''])

        writer.writerow(['', 'Transcript quick notes'])
        for row in analises_log:
            writer.writerow(['', str(row)])
        writer.writerow([''])
    output.close()