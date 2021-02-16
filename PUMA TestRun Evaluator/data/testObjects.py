class testMotor:
    '''
    A test motor with a test motor ID, that was recognised in the testing procedure.
    Takes a variable Name as parameter
    '''
    TestRunCount = 0
    TestMotorCount = 0
    def __init__(self, name):
        self.__name = name
        self.__tests = []
        testMotor.TestMotorCount += 1
    
    def getName(self):
        return self.__name

    def getTestCount(self):
        return self.__TestRunCount
    
    def addTestRun(self, startTime, testStand, files):
        try:
            TestRunCount += 1
            self.__tests.append({TestRunCount, testRun(startTime, testStand, files)})
        except Exception as err:
            print('Error:', err)
    
    def getTestRuns(self):
        return self.__tests

    
class testRun:
    '''
    A single test run of a test motor
    '''
    def __init__(self, startTime, testStand, files):
        self.__startTime = startTime
        self.__testStand = testStand
        self.__testFiles = files
    
    def getStartTime(self):
        return self.__startTime
    
    def getTestStand(self):
        return self.__testStand

    def getTestFiles(self):
        return self.__testFiles

class testCollection:
    '''
    A class of all test subjects with their runs.
    '''
    __testCollection = []
    def __init__(self, __CollectionName):
        self.__collectionName = __CollectionName
    
    def getCollectionName(self):
        return self.__collectionName
    
    def getAllTests(self):
        return self.__testCollection
