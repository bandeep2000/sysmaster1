#from ViriImports import *
from Trace import *
import re

"""
from Utilities.VgcBeacon import *

h = hostLinux(sys.argv[1])
#h.reboot()
#h.run_command("ls")
v = vgcBeacon(h,"/dev/vgca")

v.runAllStimulus()
"""

class vgcBeacon:
	
    def __init__(self,host,device = ""):
        self.host = host
	self.vgcBeaconStr = "vgc-beacon" # vgc-config command string
	self.device = ""
	
	if device:
	    self.device = device
	
    def run(self,cmd):
        
        """ options is -d /dev/vgca """
	#cmd = self.vgcBeaconStr

        if not self.device:
	    raise ViriError("vgc-Beacon: Device not set but run called")
	
        o = self.host.run_command_verify_out(cmd,verify_regex = "vgc-beacon")
	output = o['output']
	return output

    def setDevice(self,device):
	
	self.device = device

    def getStatus(self):
	
	o = self.run("%s -d %s"%(self.vgcBeaconStr,self.device))

	for l in o:
	    
	    # if #beacon = off
	    if re.search("beacon value =",l):
		l_a = l.split("=")
		return l_a[1].strip()
	
	raise ViriError("Did not find beacon = output in output '%s'"%o)
    
    def setStatus(self,status):
	
	if status == "on":
	    stat = "1"
	elif status == "off":
	    stat = "0"
	else:
	    raise ViriError("Unknown status '%s' passed"%status)
	
	trace_info("Setting device '%s' status as '%s'"%(self.device,status))
	self.run("%s -d %s -b %s"%(self.vgcBeaconStr,self.device,stat))
	
	found_status = self.getStatus()
	if  found_status != status:
	    raise ViriError("Status for device '%s' found '%s',expected '%s'"%(self.device,found_status,status)) 
	
	trace_info("Status for device '%s' found '%s',expected '%s'"%(self.device,found_status,status)) 
	
	return 1
	

    def restartStimulus(self,status,stimulus):
       
       # After machine reboot, status will always be off
       # After driver restart,status should remain what was passed
       if stimulus == "reboot":
	   expected_status_after = "off"
       elif stimulus == "driverRestart":
	   expected_status_after = status
       elif stimulus == "service restart":
	   expected_status_after = status
       else:
	   raise ViriError("Unknown stimulus passed '%s'"%stimulus)
       
       trace_info_dashed("Vgc-Beacon: Running stimulus '%s', with status as '%s'"%(stimulus,status))
       
       self.setStatus(status)
       
       status_bef = self.getStatus()

       if stimulus == "reboot":
           self.host.reboot()
       else:
	   
	   self.host.restartVgcDriver()
	   
       status_aft = self.getStatus()
       
       print "Status before '%s', status after '%s'"%(status_bef,status_aft)
       
       return 1
    
    def get_valid_status(self):
	return ['on','off']
      
    def runAllStimulus(self,stimulus):
	
	for status in self.get_valid_status():
	  
	    
	    self.restartStimulus(status,stimulus)
	
       
	    
       
