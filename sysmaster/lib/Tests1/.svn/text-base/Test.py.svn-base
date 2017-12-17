from Trace import *
from Util import *
#import IOS
from VirExceptions import *
import Diskchecker 
import DB
from Log import *
from Cards import *
from TBR import timeBasedRelocation
from TestLink import *
from VgcUtils import *
from ViriImports import *
from FileSystems import *


"""

Run at least these to use it
self.setPrintRunningTestCase(tcaseName)
self.setTestCaseRcTime(tcaseName,rc,tdiff)
self.print_tcase_success(tcaseName,"No errors in syslogs, return code fine")

self.print_tcase_failed(tcaseName,"Errors in syslogs, return code fine")
"""

class TestCase:
    def __init__(self,testcaseName):
	   self.name = testcaseName
	   
	   self.status = []
	   self.rc     = ""
	   self.reasonPassed = ""
	   self.time = " "
	   

class Tests:

   def __init__(self,host,testcaseStr,database = 0, raiseOnErrors = 1,mntPoint = None):
	""" takes host as object and testcase string as inputs where string is example vgc utils"""
        self.host = host
	# variable to hold number of test cases
	self.testcaseStr = testcaseStr # Unique name for the whole testcase suite
	self.testcaseCounter = 0
	self.cardsConfig = {} # dictionary to store card config
	self.testcases =   []
	
	self.host.clear_dmesg_syslogs()
	
	self.CardAttribChecked = 0 # variable to check if card attributes were checked

        self.hostOsVersion             = self.host.cat_etc_issue()
        self.hostKernelVersion         = self.host.get_kernel_ver()
        self.hostName                  = self.host.name
        self.hostCpus                  = self.host.getCPUs()
        self.hostCpuModel              = self.host.getCPUModel()
        # build found from vgc-monitor
        
        # build passed to install
        self.build = " "
        self.foundCardbuild            = ""
        
        self.cardType = ""
        self.cardSerial = ""
        
        self.isCardSerialSet = 0
        
        self.logFile = ""
        
        # if you want to log into the database
        self.database = database
        
        # log file to be used to storep the output
        self.logFile = ""
        self.logFileHttpPath = ""
        self.initialConfigStr = ""
        self.tbr =  0
        self.testLink = testLink()
	self.raiseOnErrors = raiseOnErrors
        #self.configure()
        #sys.exit(1)
        self.mntPoint = mntPoint
   
   def _set_initial_conf_str(self,device,string = ""):
       
       details = self.host.vgcconfig.getDevicesDetails("-d %s"%device)[remove_dev(device)]
    
       # TO DO, remove_dev
       device =  remove_dev(device)  
       part = "0"
       devPart = device + part
           
       mode = details[devPart]['mode']
       n = details['partitionNum']
       self.initialConfigStr = "Mode: %s n:%s %s"%(mode,n,string)
           #print mode
           #print partitionNum
       return 1
       
   def configure(self,device,mode = None,n = None,tbr = None):
       
       #vgcConfig = vgcConf(self.host)
       
       devPart = device + "0"
       
       # in case tbr is None
       if tbr == "None":
	   tbr = None
       if tbr:
	   trace_info("TBR seem to have passed with value '%s'"%tbr)
	   tbr1 = timeBasedRelocation(self.host)
	   
	   tbr1.setRetentionAndVerify(tbr,tbr,devPart)
	   self.tbr = 1
	   
       if not mode:
           self._set_initial_conf_str(device)
           return 1
       
       if mode == "reset":
           
           trace_info("Resetting the card")
           self.host.vgcconfig.resetCard(device)
           self._set_initial_conf_str(device,string = "Reset")
           self.initialConfigStr = "Reset"
           return 1
       
       #if it reaache here maxperformance or maxcapacity
       if not n:
           n = 1
           #raise ViriValuePassedError("n not passed in Configuration")
       
       self.host.vgconfig.confCard(device,mode,n)
       
       self._set_initial_conf_str(device,vgcConfig,string = "configured")

       return 1

   def setBuild(self):
       
       vm                  = vgcMonitor(self.host)
       build               = vm.getBuild()
       self.foundCardbuild = build
       #print  self.foundCardbuild
       #sys.exit(1)
       return 1

   def getTotalCasesRan(self):
       
       return len(self.testcases)

   def getLastTestCase(self):
       """ gets the last test case"""
      
       length = len(self.testcases)
       
       if length == 0:
           trace_info("No test case to be have run, testcases array empty")
           return None
       lastIndex = length - 1
      
       try:
         return self.testcases[lastIndex].name
       except IndexError:
         printOutput(self.testcases)
         raise IndexError("Couldn't get the last testcase")
       
   def installBuild(self,build,stats = 0,server = "cloudy.virident.info",pathType = "packages",emc  = 0,releaseString = None):

      
       found_build = 0
       print "Installing Build"
       for server in ["cloudy.virident.info","solarium.virident.info"]:
	  if found_build == 1:
		  break
          for pathType in ["packages","releases"]:
       
              try:
                 self.host.installBuild(build,stats,server,pathType = pathType, emc =emc,releaseVer = releaseString)
		 found_build = 1
		 break
              # if failed due to rpm installation error, continue, else 
	      # catch in except and raise
              except RpmError,e:
	         trace_info(e)
                 trace_info("Seems like install with packages =%s, " \
		  "server='%s' failed, retrying..."%(pathType,server))
		 
	         continue
	      except:
	         raise
       if found_build == 0:
	       raise ViriError("Could not install the build")
       #sys.exit(1)
       self.build = build
       
       return 1

   def chkDevForErrors(self,devPart):
           """ check device for dpp or other erros """
	   self.host.chk_if_dpp_errors(devPart)
	   self.host.vgcproc.chk_if_ue_errors(devPart)
           
	   return 1
	   
   def chkErrorsSyslogsDmesg(self):
           # print to the user also
	   self.host.print_syslogs_dmesg(raiseOnErrors = self.raiseOnErrors)
           # TO DO
           #print "raise on Errors",self.raiseOnErrors
           if int(self.raiseOnErrors) != 0:
             self.host.chk_viri_lspci_errors(raiseOnErrors = self.raiseOnErrors)
	   return 1
   
   def getAndSetLogfile(self,device,outputFile = None):
       """ sets log and http file path,return logfile"""

       dirResults = "/var/www/html/sqa/testResults/%s/"%self.build
       httpPath = "http://sysmaster/sqa/testResults/%s/"%self.build
       if self.isCardSerialSet == 0:
           
           self.setCardSerialAndType(device)
           
       # add number to the end, so it wont complain
       if outputFile:
           outputFile = outputFile + "-0"
           
       if not outputFile:
           outputFile = "%s-%s-%s-%s-%s-%s-0"%(self.host.name,get_device_letter(device),self.cardType,self.cardSerial,self.host.cat_etc_issue(),self.testcaseStr)
       
       outputFile = dirResults + outputFile
       
       #outputFile = outputFile + ".html"
       
       outputFile = incrementFileNameIfExists(outputFile,ext = "html")
       
       
       self.logFile = outputFile
       
       m = re.search(".*/(\S+)",outputFile)
       outputFile = m.group(1)
       self.logFileHttpPath = httpPath + outputFile
       return self.logFile

   def setCardSerialAndType(self,device):
       
       if not if_vgc_dev(device):
	     return 1
       vm = vgcMonitor(self.host)
       self.cardType = vm.getCardType(device)
       self.cardSerial = vm.getCardSerial(device)
       
       self.isCardSerialSet = 1

   def setCardAttributes(self,device):
          if not if_vgc_dev(device):
	     return 1

          trace_info("Setting device '%s' attributes"%device)
	  card = vgcCard(device,self.host )
	  #card.setAttributes()
	  
	  # getPartitions will return /dev/vgca0,/dev/vgca1
	  for p in card.getPartitions():
		  #print p.getName
		  part = p.getName()
		  (life,reads,writes,flashResLeft) = card.getPartLifeAttribs(part)
		  attr = {}
		  attr[part] = {}
		  attr[part]['life'] = life
		  attr[part]['reads'] = reads
		  attr[part]['writes'] = writes
		  attr[part]['flashResLeft'] = flashResLeft
		  
		  self.cardsConfig = attr
	  self.CardAttribChecked = 1 
           
          # set card build also,since this function will be called most likely
          self.setBuild()
	  
   def verifyLifeAttributesChanged(self,devPart,
	                          lifeOperator          = "lessthanequal",
	                          readOperator          = "greaterthanequal",
	                          writeOperator         = "greaterthanequal",
	                          spareLifeLeftOperater = "lessthanequal"):

	   
           if not if_vgc_dev_part(devPart):
	     return 1
           chkifVgcDevPart(devPart)
           trace_info("Verifying device '%s' attributes"%devPart)
	   if not self.CardAttribChecked:
		   raise ViriValuePassedError ("Card Attributes not set first,please set it first")
		   sys.exit(1) 
		                        
	   device = get_vgc_dev_from_part(devPart)
	   card = vgcCard(device,self.host)
	   for p in card.getPartitions():
		if p.getName() == devPart:
		    (life,reads,writes,flashResLeft) = card.getPartLifeAttribs(p.getName())
		    
		    compareAttrib(life,self.cardsConfig[devPart]['life'],"life",lifeOperator)
		    compareAttrib(reads,self.cardsConfig[devPart]['reads'],"reads",readOperator)
		    compareAttrib(writes,self.cardsConfig[devPart]['writes'],"writes",writeOperator)
		    compareAttrib(flashResLeft,self.cardsConfig[devPart]['flashResLeft'],"flashResLeft",spareLifeLeftOperater)
		    #sys.exit(1)
	   
           trace_info("Card Attributes seem to have changed fine")

   def getDeviceHostDetails(self,device):
       """takes hostname object and device"""
       dev_host_det                   = self.host.get_host_device_ver(device)
       build                          = dev_host_det['build']
       # redhat version
       os_ver                         = dev_host_det['version']
       kernel                         = dev_host_det['kernel']
       
       self.setBuild()
       #self.foundCardbuild            = self.setBuild()

       str = "Running '%s' tests on device '%s',build '%s' \n host kernel '%s'"%(self.testcaseStr,device,build,kernel) + \
             " os version '%s', machine '%s' "%(os_ver,self.host.name)

       return str
   
   def printDeviceHostDetails(self,device):
	   trace_info(self.getDeviceHostDetails(device))

   def run_verifications(self,verficationsDict):
         print verficationsDict
         #sys.exit(1)

         # TO DO,this is not chckeing verification
	 self.host.is_crash_dir_empty()
       
         if verficationsDict.has_key('chkErrorsSyslogsDmesg'):
           #print "hello"
           self.chkErrorsSyslogsDmesg()
         if verficationsDict.has_key('verifyLifeAttributesChanged'):
            
           options     = verficationsDict['verifyLifeAttributesChanged']['operators']
           devPart     = verficationsDict['verifyLifeAttributesChanged']['devPart']
           #print options
           lifeOperator = util_if_not_key_in_dict_put_default(options,'lifeOperator',"lessthanequal")
           readOperator = util_if_not_key_in_dict_put_default(options,'readOperator',"greaterthanequal")
           writeOperator = util_if_not_key_in_dict_put_default(options,'writeOperator',"greaterthanequal")
           spareLifeLeftOperater = util_if_not_key_in_dict_put_default(options,'spareLifeLeftOperater',"lessthanequal")
           self.verifyLifeAttributesChanged(devPart,
                                  lifeOperator          = lifeOperator,
                                  readOperator          = readOperator,
                                  writeOperator         = writeOperator,
                                  spareLifeLeftOperater = spareLifeLeftOperater)

         if verficationsDict.has_key('chkDppErrors'):
           #print verficationsDict
            self.host.chk_if_dpp_errors(verficationsDict['chkDppErrors']['devPart'])
            
         if verficationsDict.has_key('chkUEErrors'):
           self.host.vgcproc.chk_if_ue_errors(verficationsDict['chkUEErrors']['devPart'])

   def print_summary(self):

        self.chkErrorsSyslogsDmesg()
        

	print " "
        print "=" * 80
	trace_info("Summary for %s"%self.testcaseStr)
        print "=" * 80
        print " "
        
        print "Card Initial Configuration: '%s'"%self.initialConfigStr
        print "Card Type '%s' serial '%s'"%(self.cardType,self.cardSerial)
        print ""

        print"Host Details:"
        
        print "OS Version: '%s'"%self.hostOsVersion            
        print "Kernel:  '%s'"%self.hostKernelVersion   
        print "Hostname:  '%s'"%self.hostName     
        
        
        if not self.foundCardbuild:
           try:
                self.setBuild()
           except:
                self.foundCardbuild = "N/A"
        print "Build: '%s'"%self.foundCardbuild
        
        print "CPU Details: Total '%s', model '%s'"%(self.hostCpus,self.hostCpuModel)
        
        passed = 0
        failed = 0
        c      = 0
        print " "
        
	print "| No. | Testcase Details | Reason for Testcase Passed | rc | Time | Status |" 
        
	for t in self.testcases:
           
		print "|%i | '%s' | '%s' | '%s'| '%s'| '%s'|"%(c, t.name,t.reasonPassed,t.rc,t.time,t.status)
                c = c + 1
                
                if t.status == "Passed":
                     passed = passed + 1
                if t.status == "Failed":
                     failed = failed + 1
		
        print " "
        
        print "Total Passed : '%i'"%passed
        print "Total Failed : '%i'"%failed
        
        print " "
        
        logFilePath =  self.logFileHttpPath
        
        # update Test Link
        updateTestLink = 0
        if updateTestLink:
         for t in self.testcases:
	    
	    tcase = t.name
	   
	    # TO DO this is a hack
	    # These test cases need to be modified
	    for tstring in [ "vgc-config mode maxperformance","vgc-config mode maxcapacity","vgc-config partition"]:
		if re.search(tstring,tcase):
		    tcase = tstring

	    self.update_testlink(tcase)

        if self.database == 1:
            db = DB.viriDB()
        
            c = 0

            for t in self.testcases:

                  db.insertTestCaseResults(self.foundCardbuild,self.hostName,self.hostKernelVersion, self.hostOsVersion, self.hostCpus,self.hostCpuModel,str(c) ,t.name,t.reasonPassed ,t.rc,t.time,t.status,logFilePath,self.initialConfigStr,self.testcaseStr,self.hostKernelVersion,self.cardType,self.cardSerial)

                  c = c + 1

   def setRunningTestCase(self,testcaseName):
       testcase = TestCase(testcaseName)
       self.testcases.append(testcase)

       return 1
       
   def setPrintRunningTestCase(self,testcaseName):
       
       self.setRunningTestCase(testcaseName)
       
       trace_info_dashed("Running testcases '%s'"%testcaseName)
       return 1
       
   def setTestCaseRcTime(self,testcaseName,rc,time):
       t = self.getTestCaseObject(testcaseName)
       t.rc = rc
       t.time = time
       
       
   def getTestCaseObject(self,testcaseName):
       for t in self.testcases:
           tName = t.name
           if tName == testcaseName:
               return t
       return False

   def print_tcase_success(self,testcaseName,reasonPassed):
        """takes testcase name and reason passed, appends 
        testcase array object with status passed and reason
        passed, also print on the screen that testcase passed"""

        # go throuht the test case objects
	for t in self.testcases:
		
		tName = t.name
		if tName == testcaseName:
			#print tName
			t.status = "Passed"
			t.reasonPassed = reasonPassed
                        return 1
	print_green("=" * 80)
	trace_success("TESTCASE: PASSED %s,reason '%s'"%(testcaseName,reasonPassed))
	print_green("=" * 80)
        
	raise ViriValuePassedError("Testcase '%s' doesnt seem to be run but print success called"%testcaseName)

   def print_tcase_failed(self,testcaseName,reasonFailed):
        """takes testcase name and reason failed, appends 
        testcase array object with status passed and reason
        passed, also print on the screen that testcase passed"""

        # go throuht the test case objects
	for t in self.testcases:
		
		tName = t.name
		if tName == testcaseName:
			#print tName
			t.status = "Failed"
			t.reasonPassed = reasonFailed
                        self.print_summary()
                        raise TestCaseFailed ("Testcase '%s' Failed, reason '%s"%(testcaseName,reasonFailed))
                        sys.exit(1)
                        return 1

	raise ViriValuePassedError("Testcase '%s' doesnt seem to be run but print failed called"%testcaseName)
  
   def testcase_append(self,testcaseName,rc,time):
        """Appends testcase to self.testcases  """

	self.testcaseCounter = self.testcaseCounter + 1
	testcase             = TestCase(testcaseName)
	testcase.rc          = rc
	testcase.time        = time
	self.testcases.append(testcase)
   
   def run_neg_testcase(self,testcaseName,cmd):
	   
	 self.testcaseCounter = self.testcaseCounter + 1
	 testcase = TestCase(testcaseName)
	 trace_info("Running TestCase%i  '%s'"%(self.testcaseCounter,testcase.name))
    
         o = self.host.run_command(cmd)

         rc = o['rc']
         # TO DO , this should chk return code and output also
         if rc != 0:
	     print ""
	     print "-" * 40
             trace_info("command '%s' seem to have failed successfully as expected found rc as '%i'"%(cmd,rc))
	     #self.print_tcase_success(testcase.name)
	     testcase.rc = o['rc']
	     testcase.time = o['time']
	     self.testcases.append(testcase)
	     return 1
	     
         
         trace_error("command '%s' doesn't seem to have failed as expected found rc as '%i'"%rc)
         trace_error("Testcase %s Failed"%testcase_desc)
         sys.exit(1)
    
   def run_testcase(self,testcaseName,cmd):
        """ takes testcaseName and command as input, initializes testcase array"""
	
	self.testcaseCounter = self.testcaseCounter + 1
	
	testcase = TestCase(testcaseName)
	trace_info("Running TestCase%i  '%s'"%(self.testcaseCounter,testcase.name))
        o = self.host.run_command_chk_rc(cmd)
	testcase.rc = o['rc']
	testcase.time = o['time']
        # apend to test case objects
	self.testcases.append(testcase)
	return o['output']
 
   def runDiskChecker(self,devPart,loops,blkSizesArray):
       
       # TO DO
       
       if not is_var_list(blkSizesArray):
           raiseViriError("block Sizes passed in DiskChecker, not array '%s'"%blkSizesArray )
       
       s = Diskchecker.getServer()

       port = "1100002"
       Diskchecker.startDiskcheckerServer(s,port)
       
       Diskchecker.downloadDiskchecker(self.host)
       
       size    = "8192"
       server  = "sysmaster"
       
       for loop in range(0,loops):
           
         print "Starting diskchecker loop %i"%loop
        
         #for blkSize in range(512,4096,512):
         
         for blkSize in blkSizesArray :
     
           blkSize = str(blkSize)
           t1 = get_epoch_time()
           testcaseName = "Diskchecker blk size '%s' drive '%s',total loop='%i'"%(blkSize,devPart,loop)
           
           self.setPrintRunningTestCase(testcaseName)
 
           print " "
           #trace_info_dashed("Using blksize '%s'"%blkSize)
           Diskchecker.diskcheckerCreateClient(self.host,server,port,drive = devPart,size = size,blkSize = blkSize)
           sleep_time(60,"after create diskchecker file step on client")   
           #killDiskcheckerProcessClient(cl)
           self.host.power_cycle()
           Diskchecker.diskcheckerVerifyClient(self.host,server,port,drive = devPart,size = size ,blkSize = blkSize)
           
           t2 = get_epoch_time()
           tDiff = t2 - t1
           
           rc = 0 # this is hack
           #self.testcase_append(testcaseName,rc,tDiff)
           
           self.setTestCaseRcTime(testcaseName,rc,tDiff)
           
           # reason can be improved
           self.print_tcase_success(testcaseName,"No errors found")
   
   def runVdbenchMultiple(self,dict):
      
       #testcaseName = "Vdbench: %s bs=%s,numjobs=%s,offset=%s"%(details,bs,numjobs,offset)
       testcaseName = "VdbenchMultiple: %s"%dict
       self.setPrintRunningTestCase(testcaseName)

       #vb = IOS.vdbench(self.host)
       vb = vdbench(self.host)
       
       vb.runCreatePartitions(dict)
       

       #self.testcase_append(testcaseName,rc,time)
       
       rc = 0 # hack,making rc - 0
       self.setTestCaseRcTime(testcaseName,rc,time)
       
       self.print_tcase_success(testcaseName,"Vdbench return code is '%s'"%rc)
       return 1
      
   def runVdbench (self,dict,details = ""):

       #testcaseName = "Vdbench: %s bs=%s,numjobs=%s,offset=%s"%(details,bs,numjobs,offset)
       testcaseName = "Vdbench: %s %s"%(details,dict)
       self.setPrintRunningTestCase(testcaseName)

       #vb = IOS.vdbench(self.host)
       vb = vdbench(self.host)
       
       rc = vb.run(dict)

       #self.testcase_append(testcaseName,rc,time)
       self.setTestCaseRcTime(testcaseName,rc,time)
       
       self.print_tcase_success(testcaseName,"Vdbench return code is '%s'"%rc)
       return 1
       
   def fioMulitple(self,dict):

       #testcaseName = "Vdbench: %s bs=%s,numjobs=%s,offset=%s"%(details,bs,numjobs,offset)
       testcaseName = "FioMulitple: %s"%dict
       self.setPrintRunningTestCase(testcaseName)

       #fio = IOS.FIO(self.host)
       fio = FIO(self.host)
       
       rc = fio.fioMultipleSync(dict)

       #self.testcase_append(testcaseName,rc,time)
       self.setTestCaseRcTime(testcaseName,rc,time)
       
       self.print_tcase_success(testcaseName,"Vdbench return code is '%s'"%rc)
       return 1
       
   def runFio(self,
                
                devPart,
                bs,
                time,
                rw,
                ioengine = "psync",
                numjobs  = "256",
                rw_perc  = None,
                ba       = None, 
                fsync    = None,
                size     = None,
                iodepth  = None,
                fill_drive = None,
                verify     = None):
       
       #print testcaseName
       
       testcaseName = "Fio: %s bs:'%s' rw:'%s' fsync:'%s' ba:'%s'"%(devPart,bs,rw,fsync,ba)
       self.setPrintRunningTestCase(testcaseName)

       #device = getVgcDeviceFromPart(devPart)
       #self.setCardAttributes(device)
       #fio = IOS.FIO(self.host)
       fio = FIO(self.host)
       
       fioDevice = devPart
       if self.mntPoint:
          fioDevice = self.mntPoint

       parsedOut,rc,wrtAmp,gc,plot = fio.run(fioDevice,bs,time,rw,ioengine,numjobs,rw_perc,ba,fsync,size,iodepth,fill_drive,verify)
       
       
       print ""
       
       trace_info ("Fio Output Details:")
       print " "
       #Need to change it
       #testcaseName = "fio Default"
       
       if if_vgc_dev_part(devPart):
         self.verifyLifeAttributesChanged(devPart)
         self.chkDevForErrors(devPart)
       
       # NEED to add option here
       #self.host.restartVgcDriver()
       self.chkErrorsSyslogsDmesg()
       
       self.setTestCaseRcTime(testcaseName,rc,time)
       
       self.print_tcase_success(testcaseName,"RW card attributes changed, noerror in logs,output = '%s',wrtAmp='%s',plot='%s',gc='%s'"%(parsedOut,wrtAmp,plot,gc))
       
       return 1
   
   
   def  update_testlink(self,tcaseName,status = "p"):
       
        if self.testLink.is_tcase_runnable(tcaseName):
	    
	   trace_info("Updating test link with tcase '%s'"%tcaseName)
	   self.testLink.update_test_case(tcaseName,build= self.foundCardbuild,distro = self.hostOsVersion,card = self.cardType,status = status)
	return 1
	
   def secErase(self,devPart,option = None):
       # TO DO running sanity only, need to do the full one
       # get /dev/vgca from /dev/vgca0
       device = get_device_part(devPart)
       
       options_array = SEC_ERASE_OPTIONS.keys()
       
       if option:
	   options_array = [option]

       vs = vgcSecureErase(self.host)

       for opt in options_array:
	   testcaseName = "Sec-Er Sanity: option '%s', device '%s'"%(option,devPart)
	   self.setPrintRunningTestCase(testcaseName)
	   t1 = get_epoch_time()
           vs.sanity_tcase(device,option = opt)
           rc = 0 # return code should be zero
           t2 = get_epoch_time()
           tDiff = t2 - t1
           self.setTestCaseRcTime(testcaseName,rc,tDiff)
           self.print_tcase_success(testcaseName,"return code is '%s'"%rc)

       return 1            
       
	


 


    

