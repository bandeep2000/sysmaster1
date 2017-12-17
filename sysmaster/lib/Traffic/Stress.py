STRESS_DOWNLOAD_PATH = "http://spica/sqa/tools/stress"

"""

class to start stress on the system, this will create cpu load and others

Example script :

#!/usr/bin/python
from ViriImports import *
import  Traffic.Stress
m = sys.argv[1] # machine name on command line
hostObj  = create_host(m)

# create stress object
s = Traffic.Stress.stress(hostObj)

s.start()
sleep_time(10, "after running stress")
s.stop()

"""

class stress():
    
    def __init__(self,host):
        
        """ takes host object as parameter """
        
        self.host = host
        
    def download(self):
        
      # TO DO should delete if stress already exists       
      self.host.wget_chmod_file(STRESS_DOWNLOAD_PATH)
      
    
    def start(self):
        
      """
      starts the stress testt
      """
      self.download()
      cpus = self.host.getCPUs()
      
      cmd =  "./stress --cpu %s --vm 30  --vm-bytes 128M"%cpus
      self.host.run_command(cmd,bg = True)
    
    def stop(self):
      """
      details: stops stress test
      """
      self.host.run_command("killall stress")