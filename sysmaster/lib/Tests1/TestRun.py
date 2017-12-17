from Test import *

class testRun(Tests):
   def run_testcase1(self,testCaseDetails):

           
           device = testCaseDetails['device']
           testcaseName = testCaseDetails['testcaseName']
           rc =  util_if_not_key_in_dict_put_default(testCaseDetails,'rc',0)
           cmdinParalell = util_if_not_key_in_dict_put_default(testCaseDetails,'cmdinParalell',"")
           tlinkTestCaseName = util_if_not_key_in_dict_put_default(testCaseDetails,'tlinkTestCaseName',"")
           waitAfterRunning = util_if_not_key_in_dict_put_default(testCaseDetails,'waitAfterRunning',0)
           isTestCaseCommand = util_if_not_key_in_dict_put_default(testCaseDetails,'isTestCaseCommand',False)
           expectedResult = util_if_not_key_in_dict_put_default(testCaseDetails,'expectedResult',"pass")
           reasonPassed = util_if_not_key_in_dict_put_default(testCaseDetails,'reasonPassed',"")
           verifications = util_if_not_key_in_dict_put_default(testCaseDetails,'verifications',"")

           if tlinkTestCaseName:
             self.setPrintRunningTestCase(tlinkTestCaseName)
           else:
             self.setPrintRunningTestCase(testcaseName)
           
	   
           if cmdinParalell:
	      
               self.host.run_command(cmdinParalell , bg = True)
           
	   
           # set time here
           time1 = get_epoch_time()
           
           if testcaseName == "vgc-config -reset":
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
           
           time2 = get_epoch_time()
	   tdiff = time2 - time1
           
           # if test link name is passed inititialize that 
           if tlinkTestCaseName:
               testcaseName = tlinkTestCaseName

           self.setTestCaseRcTime(testcaseName,rc,tdiff)
            
           if verifications:
               self.run_verifications(verifications)
           #self.testcase_append(testcaseName,rc,time)
	   self.print_tcase_success(testcaseName,reasonPassed)
           

           if waitAfterRunning:
             trace_info("Waiting '%i' secs after running '%s' testcase"%(waitAfterRunning,testcaseName))
             time.sleep(waitAfterRunning)           
           