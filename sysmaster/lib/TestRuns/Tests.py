from Util import *
from VariablesUtil import *
from Config.ConfigFile import configFile
import Machine.Verifications
import Machine.Stimulus
import  Traffic.Diskchecker

SIZE = "100G" # size if filesystem configs are used, please note higher the no the more time it will take to fill the drive
# even though the runtime specified in fio is less,utils fill the drive, so for unit testing it is better low value
DEFAULT_PART = "0" # 0 in /dev/vgca0 

class tests:
    """
    test class takes
    inputs:
    host object
    device as /dev/vgca, not as /dev/vgca0, adds 0 a default
    testfile
    confFile defaults as no
    time defaults as none
    stimulus is example driver restart after every test
    runverifications is flag with value True/False to run verifications after each test
    
    description: runs tests based on conf and test file
    
    """
    def __init__(self,host,device,testFile,confFile = None,time = "20",stimulus = None,runverifications = True):
        self.host         = host
        self.device       = device
        
        self.devPart      = device + DEFAULT_PART
        
        self.testcases           = {}
        self.total_testcases   = 0
        self.testcase_counter  = 0
        
        self.confFile     = confFile
        self.confDict     = {}
	self.set_config()
        self.testFile     = testFile
        self.time         = time
        
        self.devObj        = self.host.device(self.devPart)
        self.verifications = Machine.Verifications.verifications(self.host)
        self.stimulusObj   = Machine.Stimulus.stimulus(self.host)
        if stimulus:
             
            if not hasattr(self.stimulusObj,stimulus):
                raise ViriError("Not valid stimulus passed '%s'"%stimulus)
        self.stimulus      = stimulus
        
        self.host.clear_dmesg_syslogs() # TO DO this should be moved in the configure
        self.runverifications = runverifications # flag to run verifications /not

    
    def set_stimulus(self,stimulus):
        
        self.stimulus = stimulus
        
    def set_config(self):
        
        """
        description : sets config file if mntpnt is defined in conf file
        
        [config]
        fs:ext4
        gc:1
        mode:maxperformance
        mntPnt:/nand2
        lvm:1

        """
        
        if not self.confFile:
            return 1
        
        # TODO config file should check if fs is present, mntpnt should also be present
        # code can go into configFile
        c = configFile(self.confFile)
	
        
        self.confDict            = c.get_config()
	self.confDict['size']    = SIZE # TODO size should be config file also
        mntPnt                   = self.confDict.get('mntpnt',None)
        self.confDict['devPart'] = self.devPart
        self.mntpnt              = mntPnt
        if not mntPnt:
            return 1
        
        ioFile                   = mntPnt + "/file2" # using file2 as a name, could be any
        self.confDict['devPart'] = ioFile # this is io file, used by tools to run IO
  
    def setPrintRunningTestCase(self,testcaseName):
       
       self.setRunningTestCase(testcaseName)
       
       trace_info_dashed("Running testcases '%s'"%testcaseName)
       return 1
 
    def setRunningTestCase(self,testcaseName):
       
       self.testcases[testcaseName]

       return 1
    
    def configure(self):
        
        
        if self.confDict:
            trace_info("Using config as '%s'"%self.confDict)
            self.devObj.setup(self.confDict)
            
            return 1
        
        trace_info("Using no config file")
        
        return 1
    
    def cleanup(self):
        
        """
        tries to remove lvm,unmounts clears initial sectors
        """
        
        
	#if self.confDict.has_key('lvm
        # this has to be caught ,since if LVM is not set 
        # this will fail, even lvm is configured some tests like multiples
	# do not do self.configure
        # logic could be imporved

	try:

           self.devObj.clean_up_lvm()
	except Exception,e:
	   print e
	   trace_info("Some LVM issue happened,may be LVM was not present")
	
	# additional clean up, TODO this should go in in the DEVICE LVM class
	self.host.run_command("dmsetup remove V1-LV1") # TO DO LOGIC to be
	   #improved

        self.devObj.umount()
        # sometimes if you create soft partition, lvms fail to create
	self.devObj.clear_initial_sectors()
        
        return 1


    def get_diskchecker_file(self,c):
        print c.parse_header_regex("diskchecker")
        
    def get_vdbench_jobs_file(self,c,parsedDict):
        
        """
        takes config file object and parsed Dict for vdbench
        """
        
        job_runs_array = []
        
        d = parsedDict
        
        for name in d:
            
            if not name.startswith("vdbench"):
               continue
            
            dict1 = d[name]
            # ignore if it startswith vdbench Multiple or not vdbench
            if name.startswith("vdbenchMultiple"):
	        
                vdbenchDict            = c.parse_header_regex(name)
		vdbenchDict['devPart'] = self.devPart
		vdbenchDict['time']    = self.time
		
                job_runs_array.append({'testcaseName': name,'options' : vdbenchDict})
               
                continue
           
            blkSizes = dict1['bs']
            offsets  = dict1["offset"]
            threads  = dict1["threads"]
            
            devices = [self.devPart]
            size = None
            
            if self.confDict:
                #self.configure()
                devices = [self.confDict['devPart']] # put in array
                
                # if mount point is defined overwrite defined in test file
                if self.mntpnt:
                  size    = self.confDict['size']
            
            if self.time:
               time = self.time
        
            vdbenchDict = util_create_vdbench_hash(devices,blkSizes,offsets,threads,time,size)
            
            job_runs_array.append({'testcaseName': name,'options' : vdbenchDict})
        
        return job_runs_array
    
    
    def parse_file_run_test(self):
        
        """
        parses test file, creates job file array and starts the test
        """
        
        c = configFile(self.testFile)
        
        # will return key value pairs, values will be array
        d = c.parse_array()
        
        devPart = self.devPart
      
        job_runs_array = []
        
        # initialize vdbench array
        job_runs_array = self.get_vdbench_jobs_file(c,d)
	   
           
        arrFio = c.create_fio_dicts(d)
     
        for fioDict in arrFio:
            
            name = fioDict['name']
            
            fioDict['devPart'] = self.devPart
            if self.confDict:
               
                devices             = [self.confDict['devPart']] # put in array
                fioDict['devPart']  = self.confDict['devPart']
                
                # if mount point is defined overwrite defined in test file
                if self.mntpnt:
                  fioDict['size']     = self.confDict['size']
           
            # override time if passed
            if self.time:
               fioDict['time'] = self.time
                       
            job_runs_array.append({'testcaseName': name,'options' : fioDict})
        
        #job_runs_array = ["utils"]
        
        self.total_testcases = len(job_runs_array) + 1
        
        # add diskchcker, not since diskchcker is method alreay created
        # only need to add add options, devPart will be automatically added
        # TO DO ,logic needs to be improved hereivy
        dischecker_opts = c.parse_header_regex("diskchecker")
        if dischecker_opts:
            
            job_runs_array.append({'testcaseName': "diskchecker",'options' : dischecker_opts})
        
        # If utils
        utils = c.parse_header_regex("runAllUtils")
       
        if utils:
            
            job_runs_array.append({'testcaseName': "runAllUtils"})   
        
        for job in job_runs_array:
            self.cleanup()
            self.run_testcase(job)
            self.cleanup()
     
     	return 1
    
    
    def diskchecker(self,options):
        
        Traffic.Diskchecker.runDiskChecker(options)
        return 1

         
    def run_testcase(self,testCaseDetails):
        
           """
           inputs : dict as example
           
           testCaseDetails = {'testcaseName': 'runAllUtils'}

           description : run tests case, runs verification, adds to test case count, run stimulus as given when initializing
           """
           
           if self.runverifications:
                  self.verifications.run()
           try:        
	        
                testcaseName = testCaseDetails['testcaseName']
                
                self.testcase_counter = self.testcase_counter + 1
	        trace_info_dashed("Running test %s,counter %i , total %i"%(testcaseName,self.testcase_counter,self.total_testcases))

                rc                 = util_if_not_key_in_dict_put_default(testCaseDetails,'rc',0)
                cmdinParalell      = util_if_not_key_in_dict_put_default(testCaseDetails,'cmdinParalell',"")
                tlinkTestCaseName  = util_if_not_key_in_dict_put_default(testCaseDetails,'tlinkTestCaseName',"")
                waitAfterRunning   = util_if_not_key_in_dict_put_default(testCaseDetails,'waitAfterRunning',0)
                isTestCaseCommand  = util_if_not_key_in_dict_put_default(testCaseDetails,'isTestCaseCommand',False)
                expectedResult     = util_if_not_key_in_dict_put_default(testCaseDetails,'expectedResult',"pass")
                reasonPassed       = util_if_not_key_in_dict_put_default(testCaseDetails,'reasonPassed',"Command Successful")
                #reasonPassed       = util_if_not_key_in_dict_put_default(testCaseDetails,'reasonPassed',"Command Successful")
                
                device = self.device
                
                status = "PASS"
                
                if tlinkTestCaseName:
                  testCaseName = tlinkTestCaseName
                
                
                testCaseDict = {}
                
                if cmdinParalell:
                   
                    self.host.run_command(cmdinParalell , bg = True)
                
                
                # set time here
                time1 = get_epoch_time()
                
                # configure
                self.configure()
                
                # Run verifications before runnng the test
                
                if self.runverifications:
                  self.verifications.run()
               
                # if it has attribute
                if hasattr(self,testcaseName):
                    
                    # if doenst have options as key , run without it
                    # 
                    if not testCaseDetails.has_key('options'):
                        getattr(self,testcaseName)()
                        return 1
                        
                    options = testCaseDetails['options']
                    
                    # add device and host object
                    options['devPart'] = self.devPart
                    options['hostObj'] = self.host
                    getattr(self,testcaseName)(options)
                                    
                elif re.search("man |help ",testcaseName ):
                    
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
                    self.host.vgcconfig.confPartition(options['devPart'],options['mode'])
                                    
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
                     
                elif testcaseName.startswith("fio"):
                 
                    fioDict = testCaseDetails['options']
                    
                    # append testcaseNAme
                    testcaseName = "%s-%s"%(testcaseName,fioDict)
                    
                    fio = self.host.fio()
                    out = fio.rw(fioDict)
                    reasonPassed = out
             
                # vdbench Multiple came first
                elif testcaseName.startswith("vdbenchMultiple"):
                    
                    # no configure for multiple
                    vdbenchDict = testCaseDetails['options']
                    
                    vb = self.host.vdbench()
       
                    rc = vb.runCreatePartitions(vdbenchDict)
                  
                elif testcaseName.startswith("vdbench"):
                 
                    vdbenchDict = testCaseDetails['options']
                    vb = self.host.vdbench()
                    rc = vb.run(vdbenchDict)
                    
                elif testcaseName.startswith("utils"):
                    self.runAllUtils()
                    
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
           
           #except Exception,e:
           except IndexError:
              status = "FAIL"
              rc = "N/A"
              reasonPassed = e
              
           time2 = get_epoch_time()
	   tdiff = time2 - time1

           self.testcases[testcaseName] = {}

           # Adding wait before verifications, as this might give issues
           if waitAfterRunning:
             trace_info("Waiting '%i' secs after running '%s' testcase"%(waitAfterRunning,testcaseName))
             time.sleep(waitAfterRunning)           
           
           if self.runverifications:
            trace_info("Running verfications after the test")
            self.verifications.run(set_variables = False)
           
           # TO DO, how to take care of power cycle
           # should check if the stimulus has the 
           if self.stimulus:
              getattr(self.stimulusObj,self.stimulus)()
              if self.runverifications:
                trace_info("Running verfications after the stimulus")
                # this will not verify read/write since set_variables was false
                # before this verification, TO DO
                self.verifications.run(set_variables = False)
            
                # Valid only when stimulus is defined TO DO
                # should be passed only if initifile has gc in it since it
                # it fills the entire dirve TO DO
                #self.devObj.read_entire_drive()
                #trace_info("Running verfications after the stimulus and reading entire drive")
                #self.verifications.run(set_variables = False)
           
           
           testCaseDict['time']           = tdiff
           testCaseDict['rc']             = rc
           testCaseDict['reasonPassed']   = reasonPassed
           testCaseDict['status']         = status
           
           self.testcases[testcaseName] = testCaseDict
        
           # if test link name is passed inititialize that 
           if tlinkTestCaseName:
               testcaseName = tlinkTestCaseName


    def print_all_testcases_ran(self):
        
        """
        prints the summary of all tests cases, pass /fail
        """

	c = 0
	fail = 0

	dict1 = self.testcases
        
        # putting this code before, other wise vgc-monitor output is
        # printed
        card_serial = self.devObj.get_serial()
        build  = self.devObj.get_build()
           
        trace_info_dashed("SUMMARY!!!")
        self.host.get_host_details()
        
        print " "
     
        print " "
        print "Build Details :  '%s'"%build
        print "Card Serial   :  '%s'"%card_serial
        
        
        print "Initial Configuration:"
        print self.confDict
        print " "

	print "-" * 80
        print "| No. | Testcase Details | Reason for Testcase Passed | rc | Time | Status |"
        print "-" * 80
     
	for t in sorted(dict1.keys()):
	    sts = dict1[t]['status']

	    if sts == "FAIL":
	       fail = fail + 1


            print ("|%i | '%s' | '%s' | '%s'| '%s'| '%s'|"%
	      (c,t,dict1[t]['reasonPassed'],dict1[t]['rc'],dict1[t]['time'],sts))

	    c = c + 1
	
	print "-" * 80
	print "Total Ran %i, passed %i,failed %i"%(c,c - fail,fail)
	print "-" * 80

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
    
    def vgcMonitorUnknownDrive(self):
        
       
        testCaseDetails = { 
                        'testcaseName':"vgc-monitor -d %s"%self.device,
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                        'cmdinParalell': "vgc-config -d %s -r -f"%self.device,
                         'expectedResult': "fail",
                         'waitAfterRunning' :90,
                         'tlinkTestCaseName': "vgc-monitor concurrent with vgc-config",
                         }
        self.run_testcase(testCaseDetails)


        testCaseDetails = { 
                        'testcaseName':"vgc-monitor -d /dev/vgcz",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-monitor unknown drive",
                         }
        self.run_testcase(testCaseDetails)
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-config -d /dev/vgcz",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-config unknown drive",
                         }
        self.run_testcase(testCaseDetails)
        
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-monitor -ggg",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-monitor --illegal option",
                         }
        self.run_testcase(testCaseDetails)
        
        testCaseDetails = { 'device': "",
                        'testcaseName':"vgc-config -ggg",
                        'reasonPassed':"command failed as expected",
                        'isTestCaseCommand':True,
                         'expectedResult': "fail",
                        'tlinkTestCaseName': "vgc-config --illegal option",
                         }
        self.run_testcase(testCaseDetails)
    
    def vgc_diags_testcases(self):
    
 
        self.run_testcase({'device' : "",
                            'testcaseName' : "vgc-diags",
                            'reasonPassed' :"tar file create sucess",
                            # Command in parell, TO DO uncomment this and add
			    # check to wait since sometimes this command takes
			    # long and test fails , if cmdInParalell passed,it
			    # should wait in run_testcase
                            #'cmdinParalell' :"vgc-config -d %s -r -f"%self.device,
                            'tlinkTestCaseName':"vgc-diags concurrent with vgc-config",
                            'waitAfterRunning' :60})
    
        testCaseDetails = { 'device': self.device,
                            'testcaseName':"vgc-diags",
                            'reasonPassed':"tar file create sucess",
                            'cmdinParalell':"dd if=/dev/zero of=%s0 bs=1G count=40 oflag=direct"%self.device,
                            'tlinkTestCaseName': "vgc-diags with I/O",
                            'waitAfterRunning':30 }
    
        self.run_testcase(testCaseDetails)
        
        testCaseDetails = { 
                            'testcaseName':"vgc-diags",
                            'reasonPassed':"tar file create success"}
                            
        self.run_testcase(testCaseDetails)
        
        testCaseDetails = { 
                            'testcaseName':"vgc-diags --verbose",
                            'reasonPassed':"tar file create success"}
                            
        self.run_testcase(testCaseDetails)

    def vgc_beacon_testcases(self):
 
      self.host.vgcBeacon.setDevice(self.device)
      
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
         self.run_testcase({'testcaseName':testcaseName,'reasonPassed':"return code seems fine"})

      # need to remove this
      #return 1 
 
      for stimulus in ["service restart",'reboot' ]:
	      
	      testcaseName = "vgc-beacon %s"%stimulus
	      
	      if stimulus == "driverRestart":
		  testcaseName = "vgc-beacon %s"%stimulus
              self.run_testcase({'testcaseName':testcaseName,
                                'reasonPassed':"Status before and after was good"})
	
    
      # TO DO check why we are doing this again
      testcaseDetails = {'testcaseName': "vgc-beacon off",'reasonPassed': "parameters got configured fine"}
      self.run_testcase(testcaseDetails)
      
      return 1

    def runAllUtils(self ):
     
        self.resetCard()
        #return 1 # Need to delete this
        
        self.vgc_beacon_testcases()
        
        self.vgc_diags_testcases()
        self.vgcMonitorUnknownDrive()
        self.confCardModes()
       
    def resetCard(self):
        
        
       testcaseDetails = {'testcaseName': "vgc-config -reset",'reasonPassed': "parameters got configured fine"}
       self.run_testcase(testcaseDetails)
       
       testCaseDetails = { 
                        'testcaseName':"service vgcd restart",
                        'isTestCaseCommand':True,
                        #'cmdinParalell': "vgc-config -d %s -r -f"%self.device,
                         'expectedResult': "pass",
                         }
       self.run_testcase(testCaseDetails)
        
       for util in ["vgc-config","vgc-beacon","vgc-monitor","vgc-diags"]:
          for ttype in ["man", "help"]:
       
            testcaseDetails = {'testcaseName': "%s %s"%(ttype,util)}
            self.run_testcase(testcaseDetails)
     
       
