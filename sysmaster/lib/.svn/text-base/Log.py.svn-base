import sys
class Logger(object):
    def __init__(self,outputFile):
        self.terminal = sys.stdout
        self.log = open(outputFile, "a")

    def write(self, message):
        #self.terminal.flush()
        self.terminal.write(message)
        self.log.write(message)

class LoggerError(object):
    def __init__(self,outputFile):
        self.terminal = sys.stderr
        self.log = open(outputFile, "a")

    def write(self, message):
        #self.terminal.flush()
        self.terminal.write(message)
        self.log.write(message)



