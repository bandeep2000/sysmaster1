from TestCardUtils import *
class testRunUtils(TestUtils):

   # for test purposes  
   def runAllUtils1(self,device):
        
       partition = "0"
       
       devPart = device + partition

       self.printDeviceHostDetails(device)
       self.runVgcConfigNoOption()
       self.runVgcConfigLOption()
       #self.confCardModes(device)
       #self.resetCard(device)
       self.vgc_beacon_testcases(device)
       self.vgc_monitor_testcases()
       
       #self.vgc_diags_testcases(device)
       
       #self.vgcMonitorUnknownDrive(device)
  
       return 1
    
   def runAllUtils(self,device):
       
       partition = "0"
       
       devPart = device + partition
       
       self.printDeviceHostDetails(device)
       
       self.setCardAttributes(device)
       
       #raise TestCaseFailed("HEEE")
       self.runVgcMonitorNoOption()
       
       self.vgc_beacon_testcases(device)
       
       self.vgc_config_help_man_testcases()
       
       self.verifyVgcMonOuput(device)
      
       # TO DO this cover a lot more
       self.vgcMonitorUnknownDrive(device)
       
       self.vgc_diags_testcases(device)

       self.setCardAttributes(device)
       self.verifyReadWrites(devPart)

       #self.verifyRWStimulus("reboot",devPart)

       # calling after service restart testcase since driver up time have issues
       # need to resolve it
       #self.verifyVgcMonOuput(device)
       self.verifyLifeAttributesChanged(devPart)

       # added new code
       for i in range(1,2):
         self.confCardModes(device)
         self.resetCard(device)

       self.runVgcConfigNoOption()
       self.runVgcConfigLOption()

       self.vgc_monitor_testcases()


       
       print "INFO: Sleeping 60 seconds after util testcases"
       time.sleep(120)
