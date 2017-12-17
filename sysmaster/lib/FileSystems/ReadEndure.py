import time
from Trace import *
from IOS import *

"""

Runs read endurance test as described in

http://corp/svn/benchmarks/endure/endure.c

# TO DO should be able to soft partition and run in paralell

Example script:
#!/usr/bin/python
from ViriImports import *
import  FileSystems.ReadEndure
m = sys.argv[1]
devPart = sys.argv[2]
runtime = "10"
hostObj  = create_host(m)

readenObj = FileSystems.ReadEndure.readendurance(hostObj)
readenObj.run(devPart,runtime = runtime)


"""

READ_ENDURE_DOWNLOAD_PATH = "http://spica/sqa/tests/endure/endure"
UTIL = "endure"

class readendurance(IO):
	
    """ class in inherits from IO"""
    
    def __init__(self,host):
        IO.__init__(self,host)
        self.util = UTIL

    def download(self):
        if self.host.if_file_exists("endure"):
           trace_info("Endure bin seem to exist, not downloading")
           return 1
           
        self.host.wget_chmod_file(READ_ENDURE_DOWNLOAD_PATH)
 
    def start(self,devPart ):
      
        self.download()
        self.host.run_command_chk_rc("nohup ./%s %s > /dev/null&"%(UTIL,devPart))

    def stop(self):
    
        #self.host.run_command_chk_rc("kill -9 `pidof endure`")
        self.host.run_command_chk_rc("killall endure")

    def run(self,devPart,runtime):
        """
        inputs : takes devices as example , '/dev/vgca0', runtime time to run in seconds
        returns : 1 on success
        raises : CommandError on failure
        Note: It will not check if there is any errors while test is running , need to use test frame work
        """
        
        self.start(devPart)
        trace_info("Readendure : Running for %s seconds "%runtime)
        time.sleep(int(runtime))
        
        self.stop()
        
        return 1



