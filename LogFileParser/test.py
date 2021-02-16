class transition_switch(object):
    '''
    Implementing Python switcher class.
    '''
    def analiser_switcher(self, transition):
        '''
        A switching function to deal with the diferent automatic run transitions
        '''
        method_name = 'analise_' + str(transition[0])
        self.switch_line = transition[1]
        default = 'analise_EndOfTest'
        method = getattr(self, method_name, lambda: default)
        return method()

    def analise_MONITOR_MANUAL(self,):
        '''
        Analise the transition from MONITOR to MANUAL
        '''
        print('Analise the transition from MONITOR to MANUAL', self.switch_line)

    def analise_MANUAL_AUTOMATIC(self):
        '''
        Analise the transition from MANUAL to AUTOMATIC
        '''
        print('Analise the transition from MANUAL to AUTOMATIC', self.switch_line)

    def analise_AUTOMATIC_MANUAL(self):
        '''
        Analise the transition from AUTOMATIC to MANUAL
        '''
        print('Analise the transition from AUTOMATIC to MANUAL', self.switch_line)
        
    def analise_MANUAL_MONITOR(self):
        '''
        Analise the transition from MANUAL to MONITOR
        '''
        print('Analise the transition from MANUAL to MONITOR', self.switch_line)
    
    def analise_EndOfTest(self):
        '''
        Analise end of testing
        '''
        print('Analise end of testing')

transition = [['MONITOR_MANUAL', 1], ['MANUAL_AUTOMATIC', 2], ['AUTOMATIC_MANUAL', 3], ['MANUAL_MONITOR', 4], ['bla', 5]]

t = transition_switch()
for tra in transition:
    t.analiser_switcher(tra)
