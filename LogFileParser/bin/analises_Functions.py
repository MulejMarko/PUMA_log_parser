# Check if Barcode scan compleated successfully
def analise_barcode_ident(buffer, line):
    '''
    Function checks the Barcode and motor preperation.
    It takes a log buffer and checks it after the given line, if the Barcode identification and test preparation steps have been taken.
    It returns the Result notifications with time, important line breakpoints and test settings updates.
    '''
    analises_log = []
    rep_dictionary = []
    line_break = []

    line_count = 0
    for fields in buffer[line:-1]:
        if not buffer[line][2] in fields[2]:
                break
        line_count += 1
    
    # is checking barcode in at start
    try:
        for fields in buffer[line:line + line_count]:
            if 'Checking Barcode' in fields[4]: break
        else: raise Exception('Fatal Error: no barcode scan started')
    except Exception as err:
        return [fields[1], err], ['', ''], ['', '']

    # is 'Barcode identified' at the end of the sequence
    try:
        for fields in buffer[line:line + line_count]:
            if 'Barcode identified' in fields[4]:
                for index in buffer[0:line]:
                    if 'Engine Production Date' in index[4]:
                        e_Prod_Date = index[4].split(' ')[-1]
                        rep_dictionary.update({'Engine Production Date': e_Prod_Date})
                        break  
        else: raise Exception('Error: Barcode not correctly identified.')
    except Exception as err:
        return [fields[1], err], ['', ''], ['', '']
    # is there a line after last Check Barcode message