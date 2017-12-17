#from ViriImports import *

from Trace import *
from Util import *
"""
"""

class vgcUtils:
	
    def __init__(self,host):
        self.host = host
    
    def run(self,cmd,verify_regex,options = ""):
        
        """ verify_regex is string to verify """
	
	if options:
	    cmd = cmd + " " + options
    
        trace_info("Running cmd '%s', with verify regex as '%s'"%(cmd,verify_regex))
        o = self.host.run_command_verify_out(cmd,verify_regex)
	output = o['output']
	
	printOutput(output)
	return output
	
       
	    
       
