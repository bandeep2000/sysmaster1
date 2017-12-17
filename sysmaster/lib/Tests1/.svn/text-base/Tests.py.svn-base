from Util import *
from VariablesUtil import *
class tests:
    def __init__(self,host,device):
        self.host   = host
        self.device = device
        
        self.testcases = {}
        
    
    def setPrintRunningTestCase(self,testcaseName):
       
       self.setRunningTestCase(testcaseName)
       
       trace_info_dashed("Running testcases '%s'"%testcaseName)
       return 1
 
    def setRunningTestCase(self,testcaseName):
       
       self.testcases[testcaseName]

       return 1
    def run_testcase(self,testCaseDetails):

           try:        
                testcaseName = testCaseDetails['testcaseName']
                rc =  util_if_not_key_in_dict_put_default(testCaseDetails,'rc',0)
                cmdinParalell = util_if_not_key_in_dict_put_default(testCaseDetails,'cmdinParalell',"")
                tlinkTestCaseName = util_if_not_key_in_dict_put_default(testCaseDetails,'tlinkTestCaseName',"")
                waitAfterRunning = util_if_not_key_in_dict_put_default(testCaseDetails,'waitAfterRunning',0)
                isTestCaseCommand = util_if_not_key_in_dict_put_default(testCaseDetails,'isTestCaseCommand',False)
                expectedResult = util_if_not_key_in_dict_put_default(testCaseDetails,'expectedResult',"pass")
                reasonPassed = util_if_not_key_in_dict_put_default(testCaseDetails,'reasonPassed',"")
                
                device = self.device
                
                status = "PASS"
                testCaseName = testcaseName
                if tlinkTestCaseName:
                  testCaseName = tlinkTestCaseName
                
                
                self.testcases[testcaseName] = {}
                
                testCaseDict = {}
                
                if cmdinParalell:
                   
                    self.host.run_command(cmdinParalell , bg = True)
                
                
                # set time here
                time1 = get_epoch_time()
               
                if re.search("man |help ",testcaseName ):
                    
                    t_a = testcaseName.split()
                    
                    util =  t_a[1]
                    testType = t_a[0]
                    strToCheck = helpManString[util][testType]
                    
                    reasonPassed = self.run_man_page_testcase(util,strToCheck,testType)
                    
                elif re.search("vgc-config mode",testcaseName):
                    options = testCaseDetails['options']
                    self.host.vgcconfig.confCard(device,options['mode'],options['n'])

                elif re.search("vgc-config partition",testcaseName):
                    options = testCaseDetails['options']
                    self.host.vgcconfig.confPartition(device,options['devPart'],options['mode'])
                                    
                elif testcaseName == "vgc-config -reset":
                    self.host.vgcconfig.resetCard(device)
                # TO DO , improve the logic here
                elif testcaseName == "vgc-beacon on":
                    
                     self.host.vgcBeacon.setDevice(device)
                     self.host.vgcBeacon.setStatus("on")
                elif testcaseName == "vgc-beacon off":
                     self.host.vgcBeacon.setDevice(device)
                     self.host.vgcBeacon.setStatus("off")
                     
                elif testcaseName == "vgc-beacon reboot":
                     self.host.vgcBeacon.setDevice(device)
                     self.host.vgcBeacon.runAllStimulus("reboot")
                elif testcaseName == "vgc-beacon service restart":
                     self.host.vgcBeacon.setDevice(device)
                     self.host.vgcBeacon.runAllStimulus("driverRestart")
                elif testcaseName == "vgc-diags":
                     self.host.vgcdiags.run()
                elif testcaseName == "vgc-diags --verbose":
                     self.host.vgcdiags.runVerbose()
                # if nothing above is valid , try this
                # this could be moved up
                elif isTestCaseCommand:
                     o = self.host.run_command(testcaseName)
                     rc = o['rc']
                     
                     if expectedResult == "fail":
                         if rc > 0:
                             trace_info("Command Failed as expected")
                         else:
                             raise ViriError("Command '%s' passed, with rc as '%i'"%(testcaseName,rc))
                     if expectedResult == "pass":
                         if rc == 0:
                             trace_info("Command Passed as expected")
                         else:
                             raise ViriError("Command '%s' failed, with rc as '%i'"%(testcaseName,rc))
                            
                     
                else:
                    raise ViriError("Unknown test case '%s' passed"%testcaseName)
           
           except Exception,e:
           #except IndexError:
              status = "FAIL"
              rc = "N/A"
              reasonPassed = e
              
              
           time2 = get_epoch_time()
	   tdiff = time2 - time1
           
           testCaseDict['time']          = tdiff
           testCaseDict['rc']             = rc
           testCaseDict['reasonPassed']   = reasonPassed
           testCaseDict['status']   = status
           
           self.testcases[testcaseName] = testCaseDict
           
           
           # if test link name is passed inititialize that 
           if tlinkTestCaseName:
               testcaseName = tlinkTestCaseName

           if waitAfterRunning:
             trace_info("Waiting '%i' secs after running '%s' testcase"%(waitAfterRunning,testcaseName))
             time.sleep(waitAfterRunning)           


    def print_all_testcases_ran(self):
        print self.testcases
    

    def run_man_page_testcase(self,util,strToCheck,testType = "man"):
     
       cmd = "man %s | cat"%util
       if testType == "help":
           cmd = "%s --help"%util
        
       
       output = self.host.run_command_get_output(cmd)
       
       if self.is_str_exists_list(output,strToCheck):
	   string = "String '%s' seem to present in man page of '%s'"%(strToCheck,util)
           printOutput(output)
	   
	   return string
       
       trace_error("Error Occured")
       printOutput(output)
       
       raise ViriError ("Testcase %s '%s' Failed, did not find the string '%s' in the output "%(testType,util,strToCheck))


    def confCardModes(self):
           
           device = self.device
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
                           pass # delete this
			   self.confPart(devPart,m,n)

    # configures card using -d, not -p
    def confCard1(self,device,mode,n):
	   
          
        testcaseName = "vgc-config mode %s-n:%s"%(mode,n)
        testcaseDetails = {'testcaseName': testcaseName, 'options' : {'mode': mode, 'n': n},
	                   'reasonPassed': "parameters got configured fine"}
        self.run_testcase(testcaseDetails)

    def confPart(self,devPart,mode,n):
	 
        testcaseName = "vgc-config partition '%s' mode:%s -n:%s"%(devPart,mode,n)
        testcaseDetails = {'testcaseName' : testcaseName, 
	                   'options'      : {'devPart': devPart, 'mode': mode},
	                   'reasonPassed' : "parameters got configured fine"}
        self.run_testcase(testcaseDetails)

    def is_str_exists_list(self,list1,str1):
        
        for l in list1:
           
            if re.search(str1,l):
                
                return True
        
        return False
       
    def resetCard(self):
       
       self.confCardModes();return 1
       for util in ["vgc-config","vgc-beacon","vgc-monitor","vgc-diags"]:
          for ttype in ["man", "help"]:
       
            testcaseDetails = {'testcaseName': "%s %s"%(ttype,util)}
            self.run_testcase(testcaseDetails)
     
       
       testcaseDetails = {'testcaseName': "vgc-config -reset1",'reasonPassed': "parameters got configured fine"}
       self.run_testcase(testcaseDetails)
       
       testcaseDetails = {'testcaseName': "vgc-beacon off",'reasonPassed': "parameters got configured fine"}
       self.run_testcase(testcaseDetails)

    
