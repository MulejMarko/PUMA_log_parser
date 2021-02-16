import os

file_dir = "M:\Projects\_Stubler_EOL_logs\Source_logs\EOL1\mes\\base"
file_list = []

for file in os.listdir(file_dir):
    file_list.append(os.path.join("", file))

def last_4chars(x):
    return(x[-14:])

file_list = sorted(file_list, key = last_4chars)

for file in file_list:
    print(file)