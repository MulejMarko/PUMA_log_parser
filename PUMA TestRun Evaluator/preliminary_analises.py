import os
import csv
import data.testObjects as tO
import data.Logfile_IO as iO


# main log analiser function
def analise_logs_for_barcodes(log_input, log_output):
    run_name = ''
    run_line_check = 'Checking Barcode: '
    test_buffer = []

    for log in log_input:
        testBed = log[0]
        testLogDir = log[1]

        for file in iO.dir_log_files(testLogDir):
            print('Now in: ', file)
            with open(file, 'rt') as log_input:
                for line in log_input:
                    if run_line_check in line:
                        fields = line.split(';')
                        run_name = fields[4].split('\'')[1]
                        run_time = fields[1]
                        run_time_n = fields[1].split('.')[0].replace('-', '').replace('T','').replace(':', '')
                        if not run_name: run_name = 'None'

                        try:
                            test_buffer.index(run_name)
                        except:
                            test_buffer.append(tO.testMotor(run_name))
                        
                        test_buffer[run_name.addTestRun(run_time, testBed, [testLogDir])]                      

    return test_buffer


# result analise function
def analise_TestBuffer(test_buffer):
    result = len(test_buffer)
    print('All tests counted: ', result)
    for motor in test_buffer:
        print('Motor name: ', motor.getName(), '. Tests on motor: ', motor.getTestCount())

    # print('The motor: ', element.key(),' has been run: ' , element.value(), ' times.')



# this is the original call to function
log_output = 'M:\Projects\_Stubler_EOL_logs\Parser_2.0\\'
log_input = ['EOL1', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL1\mes\\base\\',]
# log_input = [['EOL1', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL1\mes\\base\\',],['EOL2', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL2\log mes\\base\\'],['EOL3', 'M:\Projects\_Stubler_EOL_logs\Source_logs\EOL3\log mes\\base\\']]


test_buffer = analise_logs_for_barcodes([log_input], log_output)

analised_buffer = analise_TestBuffer(test_buffer)

# iO.write_buffer('preliminary analises', analised_buffer, log_output)

