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

# analioser functions

# Check if Barcode scan compleated successfully
def analise_barcode_ident(buffer, line):
    #line = step_line['Barcode scan']

    for fields in buffer[line:-1]:
        if not buffer[0][2] in fields[2]:
            break
        if 'Barcode identified' in fields[4]:
            analises_log.append('Barcode recognised')
            for index in buffer[step_line['Barcode scan']:line]:
                if 'Engine Production Date' in index[4]:
                    e_Prod_Date = index[4].split(' ')[-1]
                    rep_dictionary.update({'Engine Production Date': e_Prod_Date})
            break  
        line += 1
    else:
        analises_log.append('ERROR: Barcode not recognised')
    step_line['ID Confirmed'] = line
    
#  Check if prepare to start initialisad
def analise_prepare_test(buffer, line):
    #line = step_line['ID Confirmed']

    for fields in buffer[line:-1]:
        line += 1
        if not 'PrepareForTest' in fields[2]:
            continue

        if 'UUT and TST parameter fits to engine ID.' in fields[4]:
            analises_log.append('Test initialisation succeded')
            for index in buffer[step_line['ID Confirmed']:line-1]:
                if 'UUT parameter is' in index[4]:
                    uut_p = index[4].split('\'')[1]
                    rep_dictionary.update({'UUT Parameter': uut_p})
                if 'TST parameter is' in index[4]:
                    tst_p = index[4].split('\'')[1]
                    rep_dictionary.update({'TST Parameter': tst_p})
            break
    else:
        analises_log.append('ERROR: Test initialisation failed')
    step_line['Initialisation'] = line

#  Check for MANUAL and AUTOMATIC transition
    '''
    --->
    (this actually allows me to check all the state transitions)
    <---
    '''
def analise_ControlState_transition_1(buffer, line):
    #line = step_line['Initialisation']

    for fields in buffer[line:-1]:
        line += 1
        if not 'SystemController' in fields[2]:
            continue
        
        # test for MANUAL transition
        if all(elem in fields[4] for elem in ['M', 'A', 'N', 'U', 'L']):
            analises_log.append('Test transitioned to MANUAL mode')
            step_line['MANUAL mode'] = line

        # test fo AUTOMATIC tarnsition
        if all(elem in fields[4] for elem in ['A', 'U', 'T', 'O', 'M', 'I', 'C']):
            analises_log.append('Test transitioned to AUTOMATIC mode')
            step_line['AUTOMATIC mode'] = line
            break
    else:
        if step_line['MANUAL mode']:
            analises_log.append('ERROR: Test transition to AUTOMATIC failed!')
        else:
            analises_log.append('ERROR: Test transition to MANUAL mode failed')

def analise_run_preparation(buffer, line):
    #line = step_line['AUTOMATIC mode']


    for fields in buffer[line:-1]:
        if 'SelectInitialStep' in fields[2]:
            analises_log.append('SBV run sequence file succesfully loaded')
            step_line['SBV Run prepared'] = line
            break

        if 'GetDataFromStack' in fields[2] and all(elem in fields[4] for elem in ['data', 'from', 'stack:']):
            test_csv = fields[4].split(':')[1].replace(' ', '')
            rep_dictionary['SBVRun File'] = test_csv
        
        if all(elem in fields[4] for elem in ['steps', 'parsed:']):
            auto_steps = fields[4].split(':')[1].replace(' ', '').replace('.', '')
            rep_dictionary['Automation steps'] = auto_steps
        if all(elem in fields[4] for elem in ['number', 'of', 'phases:']):
            auto_phases = fields[4].split(':')[1].replace(' ', '').replace('.', '')
            rep_dictionary['Automation phases'] = auto_phases
        if all(elem in fields[4] for elem in ['Total', 'runtime']):
            auto_time = fields[4].split(' [s]')[0].split(' ')[-1]
            rep_dictionary['Automation runtime'] = auto_time
        
        line += 1
    else:
        analises_log.append('ERROR: SBV run sequence file load failed')

def analise_automatic_run(buffer, line):
    #line = step_line['SBV Run prepared']
    final_run = False
    start_line = line

    d_phases = rep_dictionary['Automation phases']
    d_steps = rep_dictionary['Automation steps']
    phases = 0
    steps = 0

    analises_log.append('Automatic testrun started')

    for fields in buffer[line:-1]:
        line += 1
        if not 'AUTOMATIC' in fields[3]:
            msg = []
            ctrl = ''
            for fields in buffer[start_line:line-1]:
                if 'LeaveAutomatic' in fields[2]:
                    ctrl += fields[4] + ' '
            if not all(elem in ctrl for elem in ['operation', 'finished', 'result']):
                for fields in buffer[line:-1]:
                    if 'AUTOMATIC' in fields[3]:
                        step_line['Testrun stoped'] = line
                        msg.append('Testrun Warning: stopped')
                        rep_dictionary['Testrun was interupted'] = 'True'
                        final_run = False
                        break
                else:
                    step_line['Testrun aborted'] = line
                    msg.append('Testrun ERROR: Aborted')
                    final_run = True
                    rep_dictionary['Testrun succeded'] = 'False'
                for fields in buffer[step_line['SBV Run prepared']:line]:
                    if 'LeaveAutomatic' in fields[2]:
                        msg.append(fields[4])
            else:
                for fields in buffer[step_line['SBV Run prepared']:line]:
                    if 'LeaveAutomatic' in fields[2]:
                        msg.append(fields[4])
                step_line['Testrun finished'] = line
                rep_dictionary['Testrun succeded'] = 'True'
                final_run = True
                analises_log.append('Testrun finnished succesfully.')
            analises_log.append(msg)
            break                  # important for the first "for" loop
        
        if 'step index' in fields[4]:
            steps = fields[4].split('#')[1].split(' ')[0]
        if 'for phase' in fields[4]:
            phases = fields[4].split('#')[1].split(' ')[0].replace(',', '').replace('.', '')
    return final_run
        


# START of Program
#
# this is the original call to function
result_out = 'M:\Projects\_Stubler_EOL_logs\Result_Analises\\'
main_test_dir = 'M:\Projects\_Stubler_EOL_logs\Test_Results\\'

analises_file = 'M:\Projects\_Stubler_EOL_logs\preliminary analises.csv'

# prepare testcases
#tests = ['192320017VF20SED', '191840001VF20SED', '192060043VF20SED']

tests = []
with open(analises_file, 'rt') as analises:
    csv_read = csv.reader(analises, delimiter=',')
    csv_list = list(csv_read)
analises.close()
for an in csv_list[0:6]:
    tests.append(an[0])


# look up or create the analises result folder
try:
    os.path.isfile(result_out)
except:
    os.mkdir(result_out)

for test_case in tests:
    test_log_dir = main_test_dir + test_case + '\\'
    _index = 0

    # create or clear the initial report file
    o_filename = result_out + test_case + '.csv'
    with open(o_filename, 'w', newline ='') as output:
        writer = csv.writer(output)
        writer.writerow(['', 'Report for motor testing:', test_case])
        writer.writerow([''])
    output.close()

    for file in dir_log_files(test_log_dir):
        # print('Now processing: ', file)
        log_Name = file.split('\\')[-1]
        rep_dictionary = {'try': '', 'log Name': '', 'log Time': '', 'Motor ID': '', 'Engine Production Date': '', 'UUT Parameter': '', 'TST Parameter': ''}
        rep_dictionary.update({'log Name': log_Name})
        analises_log = []

        with open(file, 'rt') as log_input:
            csv_read = csv.reader(log_input, delimiter=',')
            current_buffer = list(csv_read)
        log_input.close()

        _index += 1
        rep_dictionary.update({'try': _index})

        run_name = current_buffer[0][4].split('\'')[1]
        if not run_name:
            run_name = "None"
        run_time = current_buffer[0][1].split('.')[0] #.replace('-', '').replace('T','').replace(':', '')
        rep_dictionary.update({'log Time': run_time})
        rep_dictionary.update({'Motor ID': run_name})

        step_line = {'Barcode scan': 0}

        # check if barcode scan succeded
        try:
            analise_barcode_ident(current_buffer, step_line['Barcode scan'])
        except:
            analises_log.append('Barcode not scanned.')

        #  Check if prepare to start initialisad
        try:
            analise_prepare_test(current_buffer, step_line['ID Confirmed'])
        except:
            analises_log.append('Initialisation Failed')

        #  Check if prepare to start succeded in MANUAL transition
        try:
            analise_ControlState_transition_1(current_buffer, step_line['Initialisation'])
        except:
            analises_log.append('Control state never transitioned trough MANUAL and AUTOMATIC.')

        try:
            final_run = False
            test_start = step_line['AUTOMATIC mode']
            while not final_run:
                #  Check if automatic testrun preparation was sucessful
                analise_run_preparation(current_buffer, test_start)
                #  analise automatic test run
                final_run = analise_automatic_run(current_buffer, step_line['SBV Run prepared'])
                if step_line['Testrun stoped']:
                    test_start = step_line['Testrun stoped']
        except:
            analises_log.append('Testrun end')

        # write to .csv
        write_reports_in_file(rep_dictionary, analises_log, o_filename)

        

            
            

