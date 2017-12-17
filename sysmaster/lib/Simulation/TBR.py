#import VgcProc
#import Util
#import Parsers
#import sys
#from Trace import *
#import VirExceptions
from VgcUtils import *
from ViriImports import *
MLC_DEFAULT_RETENTION_ARRAY = ['1209600', '1209600', '604800', '259200', '259200', '172800', '86400', '86400']

"""
Retention Map:
  EC low:0 EC High:2000 threshold:1209600
  EC low:2000 EC High:3000 threshold:1209600
  EC low:3000 EC High:4000 threshold:604800
  EC low:4000 EC High:5000 threshold:259200
  EC low:5000 EC High:6000 threshold:259200
  EC low:6000 EC High:7000 threshold:172800
  EC low:7000 EC High:8000 threshold:86400
  EC low:8000 EC High:2000000 threshold:86400

 
 Example Usage:
 
 #!/usr/bin/python
from Host import Host
import TBR
import sys,time
h = Host(sys.argv[1])
device ="/dev/vgca"
devPart = device + "0"

tbr = TBR.timeBasedRelocation(h)
tbr.getRetention(devPart)

"""


class timeBasedRelocation:
  
   def __init__(self,host):
       self.host = host
       self.host.ifStatsRpmLoaded("TBR")
   
   def setRetention(self,retAge,retTime):
       """Takes retention Age and retention Time as string integers"""
       
       #rmmod vgcdrive
       #modprobe vgcdrive retention_age=1600 retention_sample_time=1600
       
       trace_info("Setting retention age '%s' and retention time '%s'"%(retAge,retTime))
       self.host.rmmod("vgcdrive")
       options = "retention_age=%s retention_sample_time=%s"%(retAge,retTime)
       self.host.modprobe("vgcdrive",options)
       
       return 1
   def setRetentionAndVerify(self,retAge,retTime,devPart):
       
       # because of bug 15350, you have to set reset
       device = get_device_part(devPart)
       trace_info("Resetting device '%s' before running TBR"%device)
       self.host.vgcconfig.resetCard(device)
       
       self.setRetention(retAge,retTime)
       
       expectedRetention = int(retAge) + int(retTime)
       
       expectedRetention = str(expectedRetention)
       
       retentionArray = self.getRetention(devPart,verbose = 1 )
       
       
       
       for ret in retentionArray:
           if ret != expectedRetention:
               trace_error("Expected retention '%s' found retention '%s' in array '%s'"%(expectedRetention,ret,retentionArray))
               sys.exit(1)
            
       trace_info("Retention '%s' configured fine"%expectedRetention)
       return 1
       
   def getRetention(self,devPart,verbose = 0):
       """ take device as /dev/vgca0 , return retention as a an array"""
       
       trace_info("Getting Retention values for device '%s'"%devPart)
       drvLetter,part = get_device_letter_part(devPart)
       #vproc = self.host.vgcproc()
       
       option1 = "vgcdrive%s%s"%(drvLetter,part)
       option2 = "retention"
       output = self.host.vgcproc.run(option1,option2)
       
       if verbose: printOutput(output)
          
       dict,retentionArray = parseRetention(output)
       return retentionArray
       
   def isRetentionDefault(self,devPart):
       foundRet = self.getRetention(devPart)
       try:
       
          isArraysEqual(foundRet,MLC_DEFAULT_RETENTION_ARRAY)
       
       except VirExceptions.ArrayUnEqual:
           trace_error("Retention is not at default values")
           raise
       else:
           return 1       
       trace_error("How did i get here")
       sys.exit(1)
   def resetRetention(self):
       trace_info("Resetting retention")
       self.host.restartVgcDriver()
       # vgca0 will always be present
       self.isRetentionDefault(devPart = "/dev/vgca0")
       

       
       
       
