import csv
import os

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

# analioser functions

# Check if Barcode scan compleated successfully
def analise_barcode_scan(buffer):
    test_buffer = []
    for fields in buffer:
        if not buffer[0][2] in fields[2]:
            break
        test_buffer.append(fields)
    if 'Barcode identified' in test_buffer[-1][4]:
        analises_log.append('Barcode recognised')
        for index in range(len(test_buffer)):
            if any('Engine Production Date' in s for s in test_buffer[index]):
                e_Prod_Date = test_buffer[index][4].split(' ')[-1]
                rep_dictionary.update({'Engine Prod Date': e_Prod_Date})
    else:
        analises_log.append('ERROR: Barcode reading')

#  Check if prepare to start initialisad
def analise_prepare_test(buffer):
    indices = [buffer.index(i) for i in buffer if 'PrepareForTest' in i[2]]
    test_buffer = buffer[indices[0]:indices[-1]+1]
    if any('UUT and TST parameter fits to engine ID.' in s for s in test_buffer):
        analises_log.append('Test initialisation started')
    else:
        analises_log.append('Test initialisation FAILED')
    index1 = [test_buffer.index(i) for i in buffer if 'UUT parameter is' in i[4]]
    index2 = [test_buffer.index(i) for i in buffer if 'TST parameter is' in i[4]]
    uut_p = test_buffer[index1[0]][4].split('\'')[1]
    tst_p = test_buffer[index2[0]][4].split('\'')[1]
    rep_dictionary.update({'UUT Parameter': uut_p})
    rep_dictionary.update({'TST Parameter': tst_p})

#  Check for MANUAL and AUTOMATIC transition
    '''
    --->
    (this actually allows me to check all the state transitions)
    <---
    '''
def analise_ControlState_transition(buffer):
    indices = [buffer.index(i) for i in buffer if 'AutomationSystemController' in i[2]]
    print(indices)
    test_buffer = []
    for i in indices:
        test_buffer.append(buffer[i])
        print(buffer[i])
    
    ana_ControlState = []
    # test for MANUAL transition
    err = [0, 0]
    for buff in test_buffer:
        if all(elem in buff[4] for elem in ['M', 'A', 'N', 'U', 'L']):
            analises_log.append('Test transitioned to MANUAL mode')
            err[0] = 1
            err[1] += 1
            break
    if  err[0] == 0:
        analises_log.append('Test transition to MANUAL mode failed')
    else:
        # test fo AUTOMATIC tarnsition
        for buff in test_buffer[err[1]:-1]:
            if all(elem in buff[4] for elem in ['A', 'U', 'T', 'O', 'M', 'I', 'C']):
                analises_log.append('Test transitioned to AUTOMATIC mode')
                err[0] = 2
                err[1] += 1
                break
        if  err[0] == 1:
            analises_log.append('Test transition to AUTOMATIC failed!')



# this is the original call to function
main_test_dir = 'M:\Projects\_Stubler_EOL_logs\Test_Results\\'
test_case1 = '191570014VF20SUV'
test_case2 = '190510001VF20SED'
test_case3 = ''

test_log_dir = main_test_dir + test_case1 + '\\'
_index = 0

for file in dir_log_files(test_log_dir):
    print('Now processing: ', file)
    log_Name = file.split('\\')[-1]
    rep_dictionary = {'try': '', 'log Name': '', 'log Time': '', 'Motor ID': '', 'Engine Production Date': ''}
    rep_dictionary.update({'log Name': log_Name})
    analises_log = []

    with open(file, 'rt') as log_input:
        csv_read = csv.reader(log_input, delimiter=',')
        current_buffer = list(csv_read)  
    _index += 1
    rep_dictionary.update({'try': _index})

    run_name = current_buffer[0][4].split('\'')[1]
    if not run_name:
        run_name = "None"
    run_time = current_buffer[0][1].split('.')[0].replace('-', '').replace('T','').replace(':', '')
    rep_dictionary.update({'log Time': run_time})
    rep_dictionary.update({'Motor ID': run_name})

    # check if barcode scan succeded
    analise_barcode_scan(current_buffer)

    #  Check if prepare to start initialisad
    analise_prepare_test(current_buffer)
    #  Check if prepare to start succeded in MANUAL transition
    analise_ControlState_transition(current_buffer)

    print(rep_dictionary)
    print(analises_log)
    print(current_buffer[-1])

        
        

