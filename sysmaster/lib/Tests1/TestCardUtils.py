#!/usr/bin/python

# Run the vgc-config option on the zion card
# Will give error message if fails
# if no error, it is success

# TO DO
# VGc-config and vgc-monitor no option need to be more robust
# right now they are checking for only one string 

import sys

#sys.path.append("/home/bandeepd/python")

from Host import *
from Trace import *
from Util import *
from Specs import *
from VirExceptions import *
from TestRun import *
from Parsers import *
from VgcUtils import *
from VariablesUtil import *



vgcConfig = "vgc-config"
vgcMonitor = "vgc-monitor"
vgcDiags = "vgc-diags"
vgcBeacon = "vgc-beacon"
VgcConfigRegex = r'/dev/vgc[a-z]+\d+\s+mode=max(capacity|performance)\s+sector-size=(512|4096)\s+raid=(enabled|disabled)'

class TestUtils(testRun):

   def is_vgcconfig_regex_present(self,output):
	regex = r'.*vgc[a-z]+\d+\s+mode=max(capacity|performance)\s+sector-size=(512|4096)\s+raid=(enabled|disabled)'
        
        chkifStringPresentArray(output,regex)
	        
   def verifyReadWrites(self,devPart):
	   cmd_w = "dd if=/dev/zero of=%s bs=1M count=1000 oflag=direct"%devPart
           cmd_r = "dd of=/dev/null if=%s bs=1M count=1000 iflag=direct"%devPart

	   tcaseNameWrites = "Total Flash Bytes writes"
	   tcaseNameReads = "Total Flash Bytes reads"
           
           device = get_vgc_dev_from_part(devPart)
	   self.setCardAttributes(device)
	   
	   # spareLife Left need to be changed to flash reserve left
           # spare Life was old
           # TO DO , this should be the start of the function
	   self.run_testcase(tcaseNameWrites,cmd_w)
	   self.verifyLifeAttributesChanged(devPart,
	                          lifeOperator = "lessthanequal",
	                          readOperator = "greaterthanequal",
	                          writeOperator = "greater",
	                          spareLifeLeftOperater = "greaterthanequal")
	   
	   self.print_tcase_success(tcaseNameWrites,"Writes from NOR got increased")
	   
	   self.run_testcase(tcaseNameReads,cmd_r)

	   self.verifyLifeAttributesChanged(devPart,
	                          lifeOperator = "lessthanequal",
	                          readOperator = "greater",
	                          writeOperator = "greaterthanequal",
	                          spareLifeLeftOperater = "greaterthanequal")
				  
	   self.print_tcase_success(tcaseNameReads,"Reads from NOR got increased")

   def resetCard(self,device):
       

       testcaseDetails = {'device':device,'testcaseName': "vgc-config -reset",'reasonPassed': "parameters got configured fine"}
       self.run_testcase1(testcaseDetails)

   def confCardModes(self,device):
           
           supportedPart = self.host.vgcmonitor.get_supported_partitions_array(device)
           # TO DO this should be a global variable

	   modes = ['maxperformance', 'maxcapacity']

	   for n in supportedPart:
		   
	       for m in modes:
	           self.confCard1(device,m,n)
		   devPartArray = []
		   if n == "1":
			   devPartArray = [device + "0"]
		   elif n == "2":
			   devPartArray = [device + "0", device + "1"]
                   else:
                       raise ViriError("Unknown n  value found in device configuration value = '%s'"%n)
		   
		   #print devPartArray
		   for devPart in devPartArray:
			   self.confPart(devPart,m,n)

   # configures card using -d, not -p
   def confCard1(self,device,mode,n):
	   
          
           testcaseName = "vgc-config mode %s-n:%s"%(mode,n)
         
           self.setPrintRunningTestCase(testcaseName)

	   o= self.host.vgcconfig.confCard(device,mode,n)
	   rc = o['rc']
	   tdiff = o['time']
	   
	   self.setTestCaseRcTime(testcaseName,rc,tdiff)
	   
	   self.print_tcase_success(testcaseName,"parameters got configured fine")
	       
   def confPart(self,devPart,mode,n):
	 
           testcaseName = "vgc-config partition '%s' mode:%s -n:%s"%(devPart,mode,n)
           self.setPrintRunningTestCase(testcaseName)
     
	   o = self.host.vgcconfig.confPartition(devPart,mode)

	   rc = o['rc']
	   tdiff = o['time']
	   
	   self.setTestCaseRcTime(testcaseName,rc,tdiff)
	  
	   self.print_tcase_success(testcaseName,"parameters got configured fine")

   def is_str_exists_list(self,list1,str1):
        
        for l in list1:
           
            if re.search(str1,l):
                
                return True
        
        return False
   
   def verifyRWStimulus(self,stimulus,devPart, loops = 2):

	   tcaseName = stimulus + ",loops=%i"%loops
           
           self.setPrintRunningTestCase(tcaseName)
           
           t1 = get_epoch_time()
   
           for c in range(0,loops):
               trace_info("Starting loop '%i' for testcase tcaseName %s"%(c,tcaseName))
 
	       if stimulus == "reboot":

		   self.host.reboot()
              
               else:
                  
                   self.host.run_command_chk_rc(stimulus)

           t2 = get_epoch_time()
           tdiff = t2 - t1
           self.setTestCaseRcTime(tcaseName,"0",tdiff)
         
	   self.verifyLifeAttributesChanged(devPart)
	   self.print_tcase_success(tcaseName,"Reads,writes,life attr change")
           
           return 1
               
      
   def createFilesysMultipleTimes(self,devPart,filesys,options = None,loops = 4):
       
       check_if_vgc_part(devPart)
       t1 = get_epoch_time()

       # TO DO , Hack done for vsan
       devPart1 = devPart
       if self.mntPoint:
           devPart1 = self.mntPoint
           
       
       tcaseName = "FileSystem '%s' on device '%s' '%i' times"%(filesys,devPart1,loops)
       self.setPrintRunningTestCase(tcaseName)
       for c in range(0,loops):
           trace_info("Starting loop '%i' for testcase  '%s'"%(c,tcaseName))
           self.host.create_fs(devPart1,filesys,options)

       t2 = get_epoch_time()
       
       # if above passed rc will be 0
       rc = "0"
       
       tdiff = t2 - t1

       self.setTestCaseRcTime(tcaseName,rc,tdiff)

       self.chkErrorsSyslogsDmesg()
       self.chkDevForErrors(devPart)
       self.print_tcase_success(tcaseName,"No errors in syslogs, return code fine")
       
       
   def verifyRWMounts(self,devPart,mntPnt,filesys,loop = 1,details = ""):

           
           tcaseName = "Fileystems: mount/umount buffered IO device '%s' filesys '%s' %i times %s"%(devPart,filesys,loop,details)
           self.setPrintRunningTestCase(tcaseName)
           
           check_if_vgc_part(devPart)

           self.chkDevForErrors(devPart)
	   
	   self.chkErrorsSyslogsDmesg()
	   # clean up umount first before starting
	   self.host.umount(devPart)

           self.host.mount_fs_all(devPart,mntPnt,filesys)

	   # setc card attribs first
	   device = get_vgc_dev_from_part(devPart)
	   self.setCardAttributes(device)
	   
	   file1 = mntPnt + "/file1"
	   file2 = mntPnt + "/file2"
	   
	   mdsum1 = self.host.create_file_dd_get_md5sum(file1)
	   
	   fio = FIO(self.host)
	   
	   t1  = get_epoch_time()
	   
           for c in range(0,loop):
               trace_info("Starting loop '%i' for testcase  %s"%(c,tcaseName))
               #tcaseName = "%s%i"%(tcaseName,c)
	       
	       fio.run(file2,"16K","300",rw_perc ="70",rw = "randrw",fsync ="8",size = "1G")
	       self.host.umount_fs(devPart)
	       
	       self.host.run_command_chk_rc("service vgcd restart")
	       
	       # NEED to change this
	       #self.host.installBuild(self.build)
	       
	       self.host.mount_fs(devPart,mntPnt)
	       mdsum2 = self.host.get_md5sum(file1)
	       cmp_md5sum(mdsum1,mdsum2,"mounting fs %i"%c)
	   
	       self.verifyLifeAttributesChanged(devPart)
	       
	   t2 = get_epoch_time()
	   tdiff = t2 - t1
	 
           rc = "0" # this is hack
           self.setTestCaseRcTime(tcaseName,rc,tdiff)
	   
	   #umount , part of clean up after test
	   self.host.umount_fs(devPart)
	   #check for Errors
	   self.chkErrorsSyslogsDmesg()
           self.chkDevForErrors(devPart)
	   self.print_tcase_success(tcaseName,"Reads,writes,life attr change,md5sum matches ")
   
   def runVgcConfigNoOption(self):
	    tcaseName = "vgc-config -default"
	    output  = self.run_testcase(tcaseName,"vgc-config")
            # this is assuming if return code fails, it will fail
            if self.is_vgcconfig_regex_present(output):
                printOutput(output)
	        self.print_tcase_success(tcaseName,"Found vgc-config regex ")
            return 1
            
   def runVgcMonitorNoOption(self):
	    tcaseName = "vgc-monitor -default"
	    output  = self.run_testcase(tcaseName,"vgc-monitor")
            # this is assuming if return code fails, it will fail
            if self.is_vgcmonitor_regex_present(output):
                printOutput(output)
	        self.print_tcase_success(tcaseName,"Found vgc-monitor regex ")
            return 1
            
   def runVgcConfigLOption(self):
	    tcaseName = "vgc-config -l"
	    output = self.run_testcase(tcaseName,"vgc-config -l")
            if self.is_vgcconfig_regex_present(output):
	        self.print_tcase_success(tcaseName,"Found vgc-config regex")
            return 1
	    #self.print_tcase_success(tcaseName,"Found vgc-config regex")
            
   def run_man_page_testcase(self,util,strToCheck):
       tcaseName = "man %s"%util
       cmd = "man %s | cat"%util
       output = self.run_testcase(tcaseName,cmd)
       
       #print output
    
       if self.is_str_exists_list(output,strToCheck):
	   str = "String '%s' seem to present in man page of '%s'"%(strToCheck,util)
           printOutput(output)
	   self.print_tcase_success(tcaseName,str)
	   return 1
       
       trace_error("Error Occured")
       printOutput(output)
       self.print_tcase_failed(tcaseName,"did not find the string '%s' in the output "%strToCheck)
       raise TestCaseFailed ("Testcase '%s' Failed, did not find the string '%s' in the output "%(tcaseName,strToCheck))
       #sys.exit(1)
   
   
   def run_help_testcase(self,util,strToCheck):
       tcaseName = "%s --help"%util
       cmd = tcaseName # command and testcase is same
       output = self.run_testcase(tcaseName,cmd)
    
       if self.is_str_exists_list(output,strToCheck):
	   str = "String '%s' seem to present in man page of '%s'"%(strToCheck,util)
           printOutput(output)
	   self.print_tcase_success(tcaseName,str)
	   return 1
       
       self.print_tcase_failed(tcaseName,"did not find the string '%s' in the output"%strToCheck)
       raise TestCaseFailed ("Testcase '%s' Failed, did not find the string '%s' in the output "%(tcaseName,strToCheck))
       
   
   ############################################## 
   # VGC-MONITOR
   ###############################################
   def verifyVgcMonOuput(self,device):
	 
	   tcaseName = "vgc-monitor --detailed"
	   cmd = tcaseName
	  
	   # this is hack by Bandeep need to actually give real return codes and time
           # this testcase is fine no need to do put in the failed
	   self.testcase_append(tcaseName,"0","0")
	   self.host.verify_vgc_monitor_zion_output(device)
	
	   self.print_tcase_success(tcaseName,"parameters seem to be present")

   def is_vgcmonitor_regex_present(self,output):
        
        regex = "Card Name\s+Num Partitions\s+Card Type\s+Status"
	
        chkifStringPresentArray(output,regex)
	
        # Add this later,catch exception
	#raise ViriError("Couldn't find the regex '%s' in vgc-monitor output"%regex)
	
   def vgc_monitor_testcases(self):
    
       
       self.run_man_page_testcase("vgc-monitor",vgcMonManStr)
       self.run_help_testcase("vgc-monitor",vgcMonHelpStr)
       
   ############################################## 
   # VGC-CONFIG
   ###############################################
   def vgc_config_help_man_testcases(self):
    
       self.run_man_page_testcase("vgc-config",vgcConfManStr)
       self.run_help_testcase("vgc-config",vgcConfHelpStr)

   ############################################## 
   # VGC-BEACON
   ###############################################
   
   def vgc_beacon_testcases(self,dev):
 
      self.run_man_page_testcase("vgc-beacon",vgcBeaconManStr)
      self.run_help_testcase("vgc-beacon",vgcBeaconHelpStr)

      self.host.vgcBeacon.setDevice(dev)
      
      for status in self.host.vgcBeacon.get_valid_status():
	 
         testcaseName = "vgc-beacon %s"%status
         #self.run_testcase1({'device':dev,'testcaseName':testcaseName,'reasonPassed':"return code seems fine"})
         #verifications = {'chkErrorsSyslogsDmesg':1,
         #                 'chkDppErrors':{'devPart':'/dev/vgca0'},
         #                 'verifyLifeAttributesChanged': {'devPart':'/dev/vgca0',
         #                                               'operators' : {'lifeOperator':"lessthanequal"},
         #                                               }
         #               }
         #self.run_testcase1({'device':dev,'testcaseName':testcaseName,'reasonPassed':"return code seems fine",'verifications':verifications})
         self.run_testcase1({'device':dev,'testcaseName':testcaseName,'reasonPassed':"return code seems fine"})

      # need to remove this
      #return 1 
 
      for stimulus in ["service restart",'reboot' ]:
	      
	      testcaseName = "vgc-beacon %s"%stimulus
	      
	      if stimulus == "driverRestart":
		  testcaseName = "vgc-beacon %s"%stimulus
              self.run_testcase1({'device':dev,'testcaseName':testcaseName,
                                'reasonPassed':"Status before and after was good"})
	
	     
      return 1

        
   def vgcMonitorUnknownDrive(self,device):
     
        testCaseDetails = { 'device': device,
                        'testcaseName':"vgc-monitor -d %s"%device,
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                        'cmdinParalell': "vgc-config -d %s -r -f"%device,
                         'expectedResult': "fail",
                         'waitAfterRunning' :60,
                         'tlinkTestCaseName': "vgc-monitor concurrent with vgc-config",
                         }
        self.run_testcase1(testCaseDetails)

        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-monitor -d /dev/vgcz",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-monitor unknown drive",
                         }
        self.run_testcase1(testCaseDetails)
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-config -d /dev/vgcz",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-config unknown drive",
                         }
        self.run_testcase1(testCaseDetails)
        
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-monitor -ggg",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-monitor --illegal option",
                         }
        self.run_testcase1(testCaseDetails)
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-config -ggg",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-config --illegal option",
                         }
        self.run_testcase1(testCaseDetails)

   def vgc_diags_testcases(self,device):
    
  
    self.run_man_page_testcase("vgc-diags",vgcDiagsManStr)
    self.run_help_testcase("vgc-diags",vgcDiagsHelpStr)
    
 
    self.run_testcase1({'device' : "",
                        'testcaseName' : "vgc-diags",
                        'reasonPassed' :"tar file create sucess",
                        'cmdinParalell' :"vgc-config -d %s -r -f"%device,
                        'tlinkTestCaseName':"vgc-diags concurrent with vgc-config",
                        'waitAfterRunning' :60})

    testCaseDetails = { 'device': device,
                        'testcaseName':"vgc-diags",
                        'reasonPassed':"tar file create sucess",
                        'cmdinParalell':"dd if=/dev/zero of=%s0 bs=1G count=40 oflag=direct"%device,
                        'tlinkTestCaseName': "vgc-diags with I/O",
                        'waitAfterRunning':30 }

    self.run_testcase1(testCaseDetails)
    
    testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-diags",
                        'reasonPassed':"tar file create success"}
                        
    self.run_testcase1(testCaseDetails)
    
    testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-diags --verbose",
                        'reasonPassed':"tar file create success"}
                        
    self.run_testcase1(testCaseDetails)
   
   def runAllFilesystems(self,device):

       
       partition = "0"
       
       devPart = device + partition
       
       self.printDeviceHostDetails(device)
       
       self.setCardAttributes(device)

       #return 1
       
       # TO DO this should get from the host class
       filesystems = ['xfs',"ext3","ext3","ext4"]
       
       self.host.is_all_fs_binaries_present()

       for fs in filesystems:
          self.createFilesysMultipleTimes(devPart,filesys = fs ,options = None,loops = 5)

       for fs in filesystems:
          self.verifyRWMounts(devPart,"/nand4",fs,loop = 2)
          
       self.verifyRWStimulus("service vgcd restart",devPart,loops = 2)
       
       return 1

    

