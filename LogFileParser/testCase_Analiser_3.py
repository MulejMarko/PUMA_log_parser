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

        writer.writerow(['Transcript quick notes'])
        for row in analises_log:
            w_row = row
            writer.writerow(w_row)
        writer.writerow([''])
    output.close()

# analiser functions

# Check if Barcode scan compleated successfully
def analise_barcode_ident(buffer, line):
    '''
    Function checks the Barcode reading.
    It takes a log buffer and checks it after the given line, if the Barcode identification and test preparation steps have been taken.
    '''
    # is checking barcode recognised
    line_start = line
    test_continuie = True

    for fields in buffer[line_start:]:
        if not buffer[0][2] in fields[2]:
            break
        if 'Barcode identified' in fields[4]:
            analises_log.append(['', fields[1], 'Barcode recognised'])
            for index in buffer[line_start:line]:
                if 'Engine Production Date' in index[4]:
                    e_Prod_Date = index[4].split(' ')[-1]
                    rep_dictionary.update({'Engine Production Date': e_Prod_Date})
            break  
        line += 1
    else:
        analises_log.append(['', buffer[line-1][1], 'ERROR: Barcode not recognised'])
        for fields in buffer[line_start:line]:
            if any(ea in fields[0] for ea in ['A', 'E']):
                analises_log.append(fields)
                test_continuie = False
    
    # check if logfile broken after last line (+2 while; +1 index, +1 next line)
    if len(buffer) < line+2:
        analises_log.append(['', buffer[line-1][1], 'ERROR: Testrun broken off after Barcode identification.'])
        test_continuie = False

    step_line['ID Confirmed'] = line
    return test_continuie
    
#  Check if prepare to start initialisad
def analise_Recognise_UUT(buffer, line):
    '''
    Function testes if the motor was sucessfully recognised for testing.
    '''
    start_line = line
    prepare_line = line
    test_continuie = False

    for fields in buffer[line:]:
        line += 1
        if not 'PrepareForTest' in fields[2]:
            continue

        try:
            if 'UUT and TST parameter fits to engine ID.' in fields[4]:
                analises_log.append(['', buffer[line-1][1], 'UUT recognised.'])
                for index in buffer[step_line['ID Confirmed']:line-1]:
                    if 'UUT parameter is' in index[4]:
                        uut_p = index[4].split('\'')[1]
                        rep_dictionary.update({'UUT Parameter': uut_p})
                    if 'TST parameter is' in index[4]:
                        tst_p = index[4].split('\'')[1]
                        rep_dictionary.update({'TST Parameter': tst_p})
                        test_continuie = True
                break
        except:
            analises_log.append(['', buffer[line-1][1], 'Warning in UUT recognised.'])
    else:
        for ae_fields in buffer[start_line:line-1]:
            if any(ea in ae_fields[0] for ea in ['A', 'E'])and 'PrepareForTest' in ae_fields[2]:
                analises_log.append(ae_fields)
        analises_log.append(['', buffer[line-1][1], 'ERROR: UUT recognition failure.'])
        test_continuie = False

    step_line['UUT recognition'] = line-1
    return test_continuie

#  Check for MANUAL and AUTOMATIC transition
    '''
    Function testes the Test Transition to Manual.
    '''
def analise_transition_MANUAL(buffer, line):
    '''
    Function that checks if the MANUAL transition occured at all.
    And therfore confirmes the docking sequence.
    '''
    start_line = line
    prepare_line = line
    test_continuie = False
    error_log = []

    for fields in buffer[start_line:]:
        if 'MANUAL' in fields[3]:
            test_continuie = True
            return test_continuie
        if any(i in fields[0] for i in ['(A)', '(E)']):
            error_log.append(fields)
        line += 1
    else:
        if len(error_log) <= 5 :
            for e in error_log: analises_log.append(e)
        else:
            for e in error_log[-5:]: analises_log.append(e)
        analises_log.append(['', buffer[line-1][1], 'ERROR: Testrun never transitioned to MANUAL.'])
        test_continuie = False
    
    return test_continuie

def analise_ControlState_transitions(buffer, line):
    '''
    Function testes the Test Transition to Manual.
    '''
    start_line = line
    transition_log = []
    current_state = 'MONITOR'

    old_state_line = line

    for fields in buffer[start_line:]:
        if any(i in fields[3] for i in ['MONITOR', 'MANUAL', 'AUTOMATIC']) and not fields[3] == current_state:
            transition_log.append([current_state + '_' + fields[3], old_state_line])
            current_state = fields[3]
            old_state_line = line
        line += 1
    #else:
    #    for e in transition_log: analises_log.append(e)
    return transition_log


class transition_switch(object):
    '''
    Implementing Python switcher class.
    '''
    def analiser_switcher(self, transition):
        '''
        A switching function to deal with the diferent automatic run transitions
        '''
        transition_phase = transition[0]
        self.current_buffer = transition[1]
        self.lastPrecondition_line = transition[2]

        method_name = 'analise_' + str(transition_phase.replace('Goto ', ''))
        default = 'analise_EndOfTest'
        method = getattr(self, method_name, lambda: default)
        return method()

    def analise_MONITOR_MANUAL(self):
        '''
        Analise the transition from MONITOR to MANUAL
        '''
        start_line = self.lastPrecondition_line
        line = self.lastPrecondition_line
        buffer = self.current_buffer
        phase_continuie = False
        error_log = []

        for fields in buffer[start_line:]:
            line += 1

            if phase_continuie and any(am in fields[3] for am in ['AUTOMATIC', 'MONITOR']):
                break

            if any(i in fields[0] for i in ['(A)', '(E)']):
                error_log.append(fields)
            
            if not 'SystemController' in fields[2]:
                continue

            # test for MANUAL transition
            if all(elem in fields[4] for elem in ['M', 'A', 'N', 'U', 'L']):
                step_line['MANUAL mode'] = line

                if phase_continuie:
                    if len(error_log) <= 5 :
                        for e in error_log: analises_log.append(e)
                    else:
                        for e in error_log[-5:]: analises_log.append(e)
                    analises_log.append(['', buffer[line-1][1], 'Testrun attempted transition to MANUAL mode.'])
                else:
                    analises_log.append(['', buffer[line-1][1], 'Testrun transitioned to MANUAL mode.'])
                
                error_log = []
                phase_continuie = True

        return phase_continuie

    def analise_MANUAL_AUTOMATIC(self):
        '''
        Analise the transition from MANUAL to AUTOMATIC
        '''
        start_line = self.lastPrecondition_line
        line = self.lastPrecondition_line
        buffer = self.current_buffer
        phase_continuie = False
        error_log = []

        for fields in buffer[start_line:]:
            line += 1

            if phase_continuie and any(am in fields[3] for am in ['MANUAL', 'MONITOR']):
                break

            if any(i in fields[0] for i in ['(A)', '(E)']):
                error_log.append(fields)

            if not 'SystemController' in fields[2]:
                continue
            
            # test for MANUAL transition
            if all(elem in fields[4] for elem in ['A', 'U', 'T', 'O', 'M', 'I', 'C']):
                step_line['AUTOMATIC mode'] = line
                
                if phase_continuie:
                    if len(error_log) <= 5 :
                        for e in error_log: analises_log.append(e)
                    else:
                        for e in error_log[-5:]: analises_log.append(e)
                    analises_log.append(['', buffer[line-1][1], 'Testrun attempted transition to AUTOMATIC mode.'])
                else:
                    analises_log.append(['', buffer[line-1][1], 'Testrun transitioned to AUTOMATIC mode.'])
                
                error_log = []
                phase_continuie = True

        return phase_continuie

    def analise_AUTOMATIC_MANUAL(self):
        '''
        Analise the transition from AUTOMATIC to MANUAL
        '''

        start_line = self.lastPrecondition_line
        line = self.lastPrecondition_line
        buffer = self.current_buffer
        phase_continuie = False
        error_log = []

        # first part to determine if the test loaded correctly

        for fields in buffer[start_line:]:
            if 'SelectInitialStep' in fields[2]:
                analises_log.append(['', buffer[line][1], 'AUTOMATIC Testrun successfully loaded and started.'])
                step_line['SBV Run prepared'] = line
                phase_continuie = True
                break
            if any(i in fields[0] for i in ['(A)', '(E)']):
                error_log.append(fields)

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
            if len(error_log) <= 5 :
                for e in error_log: analises_log.append(e)
            else:
                for e in error_log[-5:]: analises_log.append(e)
            analises_log.append(['', buffer[line-1][1], 'ERROR: SBV run sequence file load failed.'])
            phase_continuie = False
        
        if not phase_continuie: return phase_continuie

        # second part to evaluate the automatic testing
        error_log = []
        leave_log = []
        start_line = line

        d_phases = rep_dictionary['Automation phases']
        d_steps = rep_dictionary['Automation steps']
        phases = 0
        steps = 0

        for fields in buffer[start_line:]:
            line += 1

            if any(i in fields[0] for i in ['(A)', '(E)']):
                error_log.append(fields)  
            if 'LeaveAutomatic' in fields[2] and 'has been' in fields[4]:
                leave_log = []
                leave_log.append(fields)
            
            if any(am in fields[3] for am in ['MANUAL', 'MONITOR']):
                if steps == d_steps and phases == d_phases:
                    analises_log.append(['', buffer[line-1][1], 'AUTOMATIC run successfully compleated for ' + str(steps) + ' steps and ' +  str(phases) +  ' phases.'])
                    analises_log.append(leave_log)
                    step_line['Testrun stoped'] = line-1
                    rep_dictionary['Testrun succeded'] = 'Test compleated.'
                else:
                    analises_log.append(['', buffer[line-1][1], 'AUTOMATIC run failed at step ' + str(steps) + ' and phase ' + str(phases) + '.'])
                    if len(error_log) <= 5 :
                        for e in error_log: analises_log.append(e)
                    else:
                        for e in error_log[-5:]: analises_log.append(e)
                    for l in leave_log: analises_log.append(l)
                    step_line['Testrun stoped'] = line-1

                phase_continuie = True
                break
            
            if 'step index' in fields[4]:
                steps = fields[4].split('#')[1].split(' ')[0]
            if 'for phase' in fields[4]:
                phases = fields[4].split('#')[1].split(' ')[0].replace(',', '').replace('.', '')
        else:
            analises_log.append(['', buffer[line-1][1], 'CAUTION: AUTOMATIC run has been forcfully interupted.'])
            if len(error_log) <= 5 :
                for e in error_log: analises_log.append(e)
            else:
                for e in error_log[-5:]: analises_log.append(e) 
            step_line['Testrun aborted'] = line-1
            phase_continuie = False

        analises_log.append(['', buffer[line-1][1], 'Testrun transitioned to MANUAL mode.'])

        # end of automatic run evaluation
        return phase_continuie

    def analise_MANUAL_MONITOR(self):
        '''
        Analise the transition from MANUAL to MONITOR
        '''
        phase_continuie = True
 
        start_line = self.lastPrecondition_line
        line = self.lastPrecondition_line
        buffer = self.current_buffer
        error_log = []

        for fields in buffer[start_line:]:
            line += 1
            if any(am in fields[3] for am in ['MANUAL', 'AUTOMATIC']):
                break
            if any(i in fields[0] for i in ['(A)', '(E)']):
                error_log.append(fields)

        if len(error_log) <= 5 :
            for e in error_log: analises_log.append(e)
        else:
            for e in error_log[-5:]: analises_log.append(e)
        analises_log.append(['', buffer[line-1][1], 'Testrun transitioned to MONITOR.'])

        return phase_continuie
    
    def analise_EndOfTest(self):
        '''
        Analise end of testing
        '''
        phase_continuie = False
        start_line = self.lastPrecondition_line
        buffer = self.current_buffer
        analises_log.append(['', buffer[start_line][1], 'Switcher: End of testing.'])

        return phase_continuie       


# START of Program
#
# this is the original call to function
result_out = 'M:\Projects\_Stubler_EOL_logs\Result_Analises\\'
main_test_dir = 'M:\Projects\_Stubler_EOL_logs\Test_Files\\'

analises_file = 'M:\Projects\_Stubler_EOL_logs\preliminary analises.csv'

# prepare testcases
#tests = ['192320017VF20SED', '191840001VF20SED', '192060043VF20SED']

tests = []
with open(analises_file, 'rt') as analises:
    csv_read = csv.reader(analises, delimiter=',')
    csv_list = list(csv_read)
analises.close()
for an in csv_list[0:80]:
    if os.path.exists(main_test_dir + an[0]): tests.append(an[0])


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
        rep_dictionary = {'try': '', 'log Name': '', 'log Time': '', 'Motor ID': '', 'Testrun succeded': 'Test did not compleat.', 'Engine Production Date': '', 'UUT Parameter': '', 'TST Parameter': ''}
        rep_dictionary.update({'log Name': log_Name})
        analises_log = []

        with open(file, 'rt') as log_input:
            csv_read = csv.reader(log_input, delimiter=',')
            current_buffer = list(csv_read)
        log_input.close()

        _index += 1
        rep_dictionary.update({'try': _index})

        try:
            run_name = current_buffer[0][4].split('\'')[1]
        except: continue
        if not run_name:
            run_name = "None"
        run_time = current_buffer[0][1].split('.')[0] #.replace('-', '').replace('T','').replace(':', '')
        rep_dictionary.update({'log Time': run_time})
        rep_dictionary.update({'Motor ID': run_name})

        step_line = {'Barcode scan': 0}
        test_continuie = True

        # 01 check if barcode scan succeded
        try:
            test_continuie = analise_barcode_ident(current_buffer, step_line['Barcode scan'])
        except Exception as error:
            print('Inside 01 Barcode scan: ' + repr(error))
            analises_log.append(['', 'Barcode not scanned.'])


        #  02 Check if prepare to start initialisad
        if test_continuie:
            try:
                test_continuie = analise_Recognise_UUT(current_buffer, step_line['ID Confirmed'])
            except Exception as error:
                print('Inside 02 UUT recognition: ' + repr(error))
                analises_log.append(['', 'UUT recognition Failed'])

        if test_continuie:
            try:
                test_continuie = analise_transition_MANUAL(current_buffer, step_line['ID Confirmed'])
            except Exception as error:
                print('Inside 02 MANUAL recognition: ' + repr(error))
                analises_log.append(['', 'Control state never transitioned to MANUAL.'])

        #  03 research The testrun state transitions and get the review process
        if test_continuie:
            try:
                transition_log = analise_ControlState_transitions(current_buffer, step_line['UUT recognition'])
                test_continuie = True

            except Exception as error:
                print('Inside 03 Control state change: ' + repr(error))
                analises_log.append(['', 'ERROR in Control State Transitions.'])

        #   04 check automatic run trough transitions
        if test_continuie:
            try:
                phase_continuie = True
                for trans in transition_log:
                    # since this is a functional switch case we implement a Python switch class, that switches between different functions, had to be defined
                    trans_param = [trans[0], current_buffer, trans[1]] 

                    t = transition_switch()
                    phase_continuie = t.analiser_switcher(trans_param)
                    if phase_continuie == False:
                        break
                
            except Exception as error:
                print('Inside 04 Automatic: ' + repr(error))
                print(file)
                print(step_line)
                analises_log.append(['', 'Testrun end'])


        # write to .csv
        write_reports_in_file(rep_dictionary, analises_log, o_filename)

        

            
            

