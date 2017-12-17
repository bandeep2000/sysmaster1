#!/usr/bin/python


"""

======================================================================================

USAGE EXAMPLE:

=======================================================================================
# Example usage
#!/usr/bin/python
from ViriImports import *
h = create_host("sqa05")
# example to run 'df -h' command
h.run_command_chk_rc("df -h")

print h.device('/dev/vgca0').is_gc_running()

h.vgcconfig.confPartition('/dev/vgca0','maxcapacity')

"""


import os,sys,re,time
import pexpect
import DB
from Rpb import *
from Driver.Driver import *
from  Device.Device import *
from Trace import *
from Errors import syslogErrors
from VgcUtils import *
from VgcUtils.VgcProc import vgcProc
from VgcUtils.VgcMon import vgcMonitor
from VgcUtils.VgcCfg import vgcConf
from VgcUtils.VgcBeacon import vgcBeacon
from VgcUtils.VgcCluster import vgcCluster
import VirExceptions
import  VgcUtils.Vsan.IB
from FileSystems import *
from FileSystems.MD5ReaderWriter import md5ReaderWriter
import Machine.Verifications
import Machine.Memory



sys.stdout.flush()
U_NAME = "root"
PASSWD = "0011231"
sshn = "ssh -oStrictHostKeyChecking=no -oCheckHostIP=no -oUserKnownHostsFile=/dev/null"


# This needs to be uncommented if exceptions dont work
class TIMEOUT(Exception):
   pass
class CommandError(Exception):
   pass
class InvalidValuePassed(Exception):
   pass
#class DeviceBusy(Exception):
#   pass


class Host:
   def __init__(self,name,logfile_object = sys.stdout,u_name = U_NAME,passwd = PASSWD):

        self.name           = name
        self.logfile        = logfile_object
        self.user           = u_name
        self.passwd         = passwd
     
        self.expected_prompt = "\[\S+@\S+\s+\S*~?\]#\s|\S+@\S+:~#\s|root@.*# |~ # "

        self.connection = None
        self.ssh   = None # after host Linux got added
        
        self.vgcproc = vgcProc(self)
        self.vgcmonitor = vgcMonitor(self)
        self.vgcconfig = vgcConf(self)
        self.parted    = parted(self)
        self.vgcBeacon = vgcBeacon(self)
        self.vgcdiags = vgcDiags(self)
        self.driver = driver(self)

   def logon(self):
      
        """
        inputs: None
        details: logins to the machine using ssh/serail
        returns: raises exception on failure
        """

        trace_info("Logging on to  machine '%s'"%self.name)
        
        for c in range(1,3):
                  
          try:
            self.connection = pexpect.spawn(sshn + " " + self.user + "@" + self.name,
                                            logfile = self.logfile)
            # if no passwd,linux prompt will be passed 
            rc = self.connection.expect([".*(p|P)assword",self.expected_prompt],100)
            break
          except pexpect.EOF:
            continue
        else:
            raise ViriError("Unable to connect to '%s'"%self.name)
            
         
        # if no passwd prompt found,return
        if rc == 1:
            return 1

        self.connection.sendline(self.passwd)
        try:
            self.connection.expect(self.expected_prompt,100)
        except pexpect.TIMEOUT:
            raise pexpect.TIMEOUT("Timeout occured to get prompt '%s' after putting password"%self.expected_prompt)
      
         
        #self.set_ssh_timeout()
        return 1

   
   def set_panic_softlockup(self, ):
      
      trace_info("Setting syctl value to crash on soft lockup, is set to 0,Please change it back!!!")

      # is set to 0, please change it back to 1
      self.run_command("sysctl -w kernel.softlockup_panic=0")
      # TO DO check if it is already there
      # You could run command sysctl -q kernel.softlockup_panic first, if it
      # already there then dont touch it
      self.run_command('echo "kernel.softlockup_panic=0" >> /etc/sysctl.conf')
      return 1
         
   def vgccluster(self):
        self.vgccluster = vgcCluster(self)
	return self.vgccluster

   def md5rw(self):
       """
       returns: md5 reader write tool object, utility used by swqa team to for data validation
       """
       return md5ReaderWriter(self)
      
   def set_ssh_timeout(self):
       trace_info("Setting ssh timeout")
       cmd_del = "sed -i '/ClientAliveInterval/d' /etc/ssh/sshd_config"
       cmd_set = 'echo "ClientAliveInterval 18060" >> /etc//ssh/sshd_config'
       
       self.run_command_chk_rc(cmd_del)
       self.run_command_chk_rc(cmd_set)
       self.run_command_chk_rc("service sshd restart")
       return 1
   
  
       
   def ser_logon(self,term_srv,port):
      
         """
         logs through the serial console
         """
      
        
         str = "telnet %s %s"%(term_srv,port)
         try:
            self.connection = pexpect.spawn(str,
                                            logfile = self.logfile)
            # if no passwd,linux prompt will be passed 
            rc = self.connection.expect(["login:"],100)
            self.connection.sendline(self.user)
            rc = self.connection.expect([".*(p|P)assword",self.expected_prompt],100)
            self.connection.sendline(PASSWD)
         except pexpect.EOF:
            trace_error("Unable to connect to '%s'"%self.name)
            sys.exit(1)
   
   
   def ifStatsRpmLoaded(self,str = " "):
      
       """
       inputs : None
       returs: returns true if vgcd stats rpm loaded
       
       
       """
       
       if not self.ifVgcRpmLoaded("stats"):
           trace_error("Stat rpm not loaded %s"%str)
           #return False
           sys.exit(1)
       return 1
       
   def modprobe(self,module,options = " "):
      
       """
       inputs : module and options
       description: loads module using modprobe command
       returns 1 : on sucess and exception on failure
       """
       cmd = "modprobe %s "%module
       if options:
           cmd = cmd + options
       self.run_command_chk_rc(cmd)
       return 1
      
   def rmmod(self,module):
      
       """
       inputs : module and options
       description: unloads module using modprobe command
       returns 1 : on success and exception on failure
       """
      
       """
       inputs: module
       
       """
       # TODO rmmod should be full path with variable defined
       self.run_command_chk_rc("rmmod %s"%module)
       return 1
       
   def getKernelNoRpm(self,kernel):
      
           """
           inputs : takes kernel rpm
           description: utility function removes rpm
           returns : kernel with no rpm
           """
	   k = re.search("kernel-(.*)\.rpm",kernel)
	   return k.group(1)
   def getKernelNo86(self,kernel):
      
           
	   j = re.search("kernel-(.*)\.x86_64\.rpm",kernel)
	   return j.group(1)
   
   def upgradeSlesKernel(self,kernel):
	   
	   trace_info("Upgrading to kernel '%s'"%kernel)
	   
	   path = "http://pxe/sles-rpms/"
	   ver = self.cat_etc_issue()
	   if ver == "sles11sp1":
		   str = "sles11sp1/"
	   elif ver == "sles11sp2":
	   	   str = "sles11sp2/"
           elif ver == "sles11":
	   	   str = "sles11/"
           elif ver == "sles10sp4":
	   	   str = "sles10sp4/"
           elif ver == "sles10sp3":
	   	   str = "sles10sp3/"
	   else:
		   raise ViriError("Unsupported sles kernel upgrade on ver '%s'"%ver)
	       
	   path = path + str 
	   # get http path, common for redhat5 and 6
           kernelPath = path + kernel
	   
	   kernStrComp = get_sles_kernel_from_rpm(kernel)
	   
	   if self.get_kernel_ver()   == kernStrComp:
               print "Found installed kernel  as same returning"
               return 2

           # try three times
	   for loop in range(1,3):
		   
	       cmd = "rpm -Uvh %s --oldpackage"%kernelPath
	       trace_info("Running cmd '%s'"%cmd)
	       o = self.run_command(cmd)
	   
	       rc = o['rc']
	       out = o['output']
	    
	       if rc == 0:
		   break
	       else:
                   # check if firmware string is found
		   found_firmware_str = 0
		   for l in out:
			   if re.search("is needed by",l):
				found_firmware_str = 1
				break
	           if found_firmware_str == 1:
			   
		       trace_info("Found string 'is needed' in output")
		       
                       kernelRpmBase = get_sles_base_from_rpm(kernel)
		       pathFw = path + kernelRpmBase
		       cmdfw = "rpm -ivh %s "%pathFw
                       
		       self.run_command_chk_rc(cmdfw)
		       
		       continue
		   else:
			   raise ViriError ("Failed to upgrade sles kernel %s"%kernel)
                           print "("
                           for l in out:
                               print l
                           print ")"
			   sys.exit(1)
	   self.reboot()
	   
	   if self.get_kernel_ver()   == kernStrComp:
		   trace_info("Upgrade to kernel %s successful"%kernel)
		   return 1
	   trace_error("Upgrade to kernel unsuccessful successful, found '%s', expected '%s'"%(self.get_kernel_ver(),kernel))
	   sys.exit(1)
   
   def upgradeKernel(self,kernel):
	   
	   trace_info("Upgrading to kernel '%s'"%kernel)
	   
	   path = "http://pxe/redhat-rpms/"
	   ver = self.cat_etc_issue()
	   if ver == "redhat6":
		   str = "rhel6/"
	   elif ver == "redhat5":
		   str = "rhel5/"
           elif ver == "sles11sp1":
		   self.upgradeSlesKernel(kernel)
                   return 1
           elif ver == "sles11sp2":
		   self.upgradeSlesKernel(kernel)
                   return 1
           
           elif re.search("sles",ver):
		   self.upgradeSlesKernel(kernel)
                   return 1
	   else:
		   trace_error("Unsupported kernel upgrade on ver '%s'"%ver)
		   sys.exit(1)
	   
	   #kernel = "kernel-2.6.32-131.0.15.el6.x86_64.rpm"
           if re.search("src",kernel):
               print "ERR: string contains src in kernel %s"%kernel
               sys.exit(1)
	       
	   path = path + str 
	   # get http path, common for redhat5 and 6
           kernelPath = path + kernel
           
	   #print path
	   # kernel-2.6.32-131.2.1.el6.x86_64.rpm
	   #remove rpm and kernel from passed kernel
	   # to be used for redhat6 uname -r comparision
	   k = re.search("kernel-(.*)\.rpm",kernel)
	   kernStrRH6 = k.group(1)
	   
	   j = re.search("kernel-(.*).x86_64\.rpm",kernel)
	   kernStrNo86 = j.group(1)
	   
	   #kerel str to compare, rh5 has no x86 in uname -r
	   kernStrComp = kernStrRH6
	   if ver == "redhat5":
		  kernStrComp =  kernStrNo86
	   
	   
	   if self.get_kernel_ver()   == kernStrComp:
               print "Found installed kernel  as same returning"
               return 2

           # try three times
	   for loop in range(1,3):
		   
	       cmd = "rpm -Uvh %s --oldpackage"%kernelPath
	       trace_info("Running cmd '%s'"%cmd)
	       o = self.run_command(cmd)
	   
	       rc = o['rc']
	       out = o['output']
	       outerr = ""


               # if using HostLinux, it will have output err,key also
               # check if ,if not pass
	       try:
	         outerr = o['outputerr']
	       except:
	         pass
	    
	       if rc == 0:
		   break
	       else:
                   # check if firmware string is found
		   found_firmware_str = 0
		   for l in out:
			   if re.search("kernel-firmware",l):
				found_firmware_str = 1
				break
	           if found_firmware_str == 1:
			   
		       trace_info("Found string with kernel firmware in output")
		       fwRpmStr = "kernel-firmware-" + kernStrNo86 + ".noarch.rpm"
		       pathFw = path + fwRpmStr
		       cmdfw = "rpm -Uvh %s "%pathFw
				#print cmdfw 
				#sys.exit(1)
		       self.run_command_chk_rc(cmdfw)
		       
		       continue
		   else:
			   trace_error("Failed to upgrade to kernel %s"%kernel)
                           print "("
                           for l in out:
                               print l
                           print ")"
			   print outerr 
			   sys.exit(1)

           print "Rebooting host"
	   print " "
	   self.reboot()
	   
	   
	   
	   if self.get_kernel_ver()   == kernStrComp:
	           trace_info("Upgrade to kernel successful, found kernel'%s',expected rpm '%s'"%(self.get_kernel_ver(),kernel))
		   return 1
	   raise ViriError("Upgrade to kernel unsuccessful, found '%s', expected '%s'"%(self.get_kernel_ver(),kernel))

   def run_command_no_rc(self,command,timeout = 600):
       
       print command
       #sys.exit(1)
       
       self.connection.sendline(command)
       self.connection.expect(self.expected_prompt,timeout)
       
       output = self.connection.before.strip()
       output_a = output.split("\r\n")
       
       output_a1 = [ i .rstrip() for i in output_a]
       print output_a1
       return output_a1
   
   def run_command(self,command,
                     timeout = 3600,
                     verbose = 0, 
                     exp_out_prompt = [],
                     verboseOutput = 0,
                     verboseTime = 0,
                     bg = False):
      
        """
        inputs:
        
        command - command as "df -h"
        bg- backgroud is True or False
        verboseTime- will display time took if enabled
        verbose- will print the commnad return  code, need to change the name
        verboseOutput- will print output of command on the sdtout
        timeout- how long to wait for the command, default is 1 hour, 3600 sec
        ----------
        
        description: runns command as example, df -h
        returns: dictionary, example
        
              {'output_str': output,
               'output'    : outputarray,
	       'time'      : "10",
               'rc'        : 0}
        
        where rc is return code, time is time taken
        output is useful key 
        """
        if self.connection == None:
            self.logon()
        
        # back ground we cand add 2>&1
	sTime = get_epoch_time()
        
        
        # if bg process
        
        if re.search(".*&$",command):
            
            self.connection.sendline(command)
            self.connection.expect(self.expected_prompt,timeout)
            return 1

        if bg:
            append = " >/dev/null 2>&1&"
            command = command + append
            self.connection.sendline(command)
            self.connection.expect(self.expected_prompt,timeout)
            return 1
         
         # End bg process
            
        trace_info("Running command '%s'"%command)
        # add the return code with command
        command = command + ';echo $?'

        #trace_info("timeout for command '%s' is %i"%(command,timeout))

        self.connection.sendline(command)
        #self.connection.wait() #added by bandeep
        
        # it is array, expected prompt
        expected_prompt = [self.expected_prompt]
        #expected_prompt = "test"
        
        if exp_out_prompt:
            if len(exp_out_prompt) != 2:
                trace_error("Please pass exp_out_prompt with length 2, passed as")
                print exp_out_prompt
                sys.exit(1)
            expected_prompt.append(exp_out_prompt[0])
            
        for i in range(0,2):
            try:
                returnrc = self.connection.expect(expected_prompt,timeout)
            except pexpect.TIMEOUT:
                print "-" * 40
                raise pexpect.TIMEOUT ("ERROR: command '%s' timedout"%command)
                
            except pexpect.EOF:
                print "-" * 40
                trace_error("ERROR: command '%s' EOF pexpect happened"%command)
                
                print " "
                
                output = self.connection.before.strip()
                output_a = output.split("\r\n")
                printOutput(output_a)
                
                print " "
                raise
                
            
            except:
                print "-" * 40
                print "ERR: unkown exception occured in pexpect"
                raise 
            if returnrc == 0:
                break
            elif returnrc == 1:
                self.connection.sendline(exp_out_prompt[1])
                continue
                _
        output = self.connection.before.strip()
        output_a = output.split("\r\n")
    
       
        # remove the expected prompt  from the end
        # To do
        output_a.pop()
        #print output_a
        
        #output_a = output_a[1:] # remove command
   
        # get the return code
        rc = output_a.pop()

        # check the return code, should be integer, if not, something is wrong
        # could have with pexpect 
        try:
            rc = int(rc)
        except ValueError:
            
            printOutput(output_a)
            trace_error("Could not convert return code of command '%s' to integer"%command)
            trace_error("Expecting integer found '%s'"%rc)
            sys.exit(1)


        if verbose == 1: print "INFO: Found return code of command '%s' as '%i'" %(command,int(rc))
	eTime = get_epoch_time()
	tTaken = eTime - sTime
	if verboseTime: 
            trace_info("Time took to run command '%s' '%s' secs"%(command,tTaken))
	
        #print "rc = '%s'"%rc
        #print output
        #for l in output:
            #print "l = '%s'"%l
        # return output_str as raw output
        # return output as normalized which is more useful 
        out = {'output_str': output,
               'output'    : output_a,
	       'time'      : tTaken,
               'rc'        : rc}
        
        
        if verboseOutput: 
            trace_info("Output of command '%s'"%command) 
            output = out['output']
            printOutput(output)
        
        return out

   def run_command_chk_rc(self,command,timeout = 3600,verbose = 1):
      
       """
       inputs: command as example "mount"
       description : same as run_command method but checks, if return code is 0 , if not, raises exception
       returns : dictionary similar to run_command method
       """
       o = self.run_command(command,timeout = timeout)
       rc = o['rc']
       out = o['output']

       if rc != 0:
           err = "Couldn't run the command '%s', found return code as '%i'"%(command,rc)
           trace_error(err)

           print "details = ("
           for l in out:
               print l
           print ")"
           out.insert(0,err)
           raise CommandError(out)

       if verbose:
         printOutput(out)
       return o
   
   def run_command_get_output(self,command ):
      """
      returns output of command given as array and not as dictionary, runs run_command method
      """
      o = self.run_command_chk_rc(command)
      return o['output']
      
   

   def run_command_verify_out(self,command,verify_regex = None,errors = [],timeout = 600,chkrc = 1):
      
        

        if chkrc == 1:
            o = self.run_command_chk_rc(command,timeout = timeout)

        else:
            o = self.run_command(command,timeout = timeout)

        out = o['output']

        if not is_var_list(errors):
            trace_error("Please pass errors as list")
            sys.exit(1)

        if verify_regex:
            found_out = 0
            for l in out:

                if re.search(verify_regex,l):
                    print "INFO: Found '%s' output in command '%s'"%(verify_regex,command)
                    found_out = 1
            if found_out == 0:
                    print "ERR: Couldn't find '%s' output in command '%s'"%(verify_regex,command)
                    sys.exit(1)
        # this and above could be combined and written as a function
        
        for e in errors:
            for l in out:
                if re.search(e,l):
                    trace_error("Found error '%s' in command '%s'"%(e,command))
                    raise CommandError

        
        return o
		
   def run_negetive_command(self,cmd,details = ""):
      """ where details is as string that describes what you can put after running a tests"""

      o = self.run_command(cmd)
      rc = o['rc']


      if rc != 0:
	  
         trace_info_dashed("command '%s' seem to have failed successfully as expected, found rc as '%i' %s"%(cmd,rc,details))
	 printOutput(o['output'])
         printOutput(o['outputerr'])
         return 1
      
	
      raise ViriError("command '%s' doesn't seem to have failed as expected found, rc as '%i' %s"%(cmd,rc,details))

   def run_command_single_output(self,cmd):
       """
       inputs: command, as uname -a
       details: useful for command that only print single line output
       returns: output as array
       """
       o = self.run_command_chk_rc(cmd)
       
       output = o['output']
       
       return output[1:]
   
   def run_command_chk_rc_no_output(self,cmd):
      
       """
       description: runs command , makes sure there is not output of command, useful in some scenarios
       """
       
       """ check if no output of command is there, raises exception if it is there """
       
       o = self.run_command_chk_rc(cmd)
       
       # remove the first element which is the command itself
       out = o['output'][1:]
       
       if len(out) == 0:
           
           trace_info("No output of command '%s' found as expected"%cmd)
           return 1
       
       raise ViriError("expected no output of command '%s' but found %s"%(cmd,out))
   
   def memory(self ):
      """
      inputs: None
      returns: memory object
      """
      m = Machine.Memory.memory(self);return m
 
   def is_gc_running(self,devPart):
      """
      inputs: device as /dev/vgca0
      description: return if GC(Gargbage collection) is running
      returns True /False , takes /dev/vgca0 as input
      """
      v = vgcPart(devPart,self)
      return v.is_gc_running()
   
   def device(self,devPart):
      
      """
      inputs: device as /dev/vgca0
      returns: device object
      
      Usage example:
      
      d =host.device.('/dev/vgca0')
      d.is_gc_running()
      
      """
      
      v = vgcPart(devPart,self)
      return v
  
  
   def get_host_details(self):
      
        """
        returns : dictionary of host details, linux /kernel version,cpu details
        """
      
        dict1 = {}
        dict1['os_ver']         = self.cat_etc_issue()
        dict1['kernel']         = self.get_kernel_ver()
        dict1['hostname']       = self.name
        dict1['numcpus']        = self.getCPUs()
        dict1['cpu_model']      = self.getCPUModel()
        
        trace_info_dashed("Getting host details")
        
        print dict1
        return dict1
        
   def ifProcessRunning(self,process):
       
       # add[f]io to fio
       f = process[:1] # get first letter from string
       l = process[1:] # get rest of the string
       f = '[' + f + ']' # convert l to [l]
       process =  f + l 

       cmdIfRunning = "ps -eaf | grep \"%s\""%process
    
       o  = self.run_command(cmdIfRunning)
       rc = o['rc']
  
       if rc == 0:
        return True
       return False
   
   def chkIfProcessRunning(self,process):
       
       if self.ifProcessRunning(process):
                trace_info("'%s' process seem to be started fine"%process)
                return 1
       else:
                raise ViriError("'%s' process doesn't seem to be started"%process)   

   def isIORunning(self,devPart):
      
       """
       inputs: device , example /dev/vgca0
       returns : True if I/O running, False if not
       """
       befIO = int(self.cat_proc_diskstats(devPart,"total"))
       trace_info("Found total stats before %s for device '%s'"%(befIO,devPart))
       
       sleep_time(2,"waiting 1 sec")
       aftIO = int(self.cat_proc_diskstats(devPart,"total"))
       trace_info("Found total stats after %s for device '%s'"%(aftIO,devPart))
       
       diff = aftIO - befIO
       
       trace_info("Found before IO %i after IO %i diff %i"%(befIO,aftIO,diff))
       
       if diff <= 2:
           return False
       
       #if diff == 0:
           #return False
       return True

   def cat_proc_diskstats(self,devPart,type):
      
       """
       inputs: /dev/vgca0, type as reads,writes or rw(both read and write as total)
       returns: returns reads as example "314", if 314 reads are done as example
       """
       #devPart = rmDevice(devPart)
       devPart = remove_dev(devPart)
       
       trace_info("Getting diskstats for device '%s',removed 'device' string"%devPart)
       
       cmd = "cat /proc/diskstats | grep %s"%devPart
       
       if type == "reads":
           cmd =  "%s | awk '{print $6}'"%cmd
       elif type == "writes":
           cmd =  "%s | awk '{print $10}'"%cmd
       elif type == "total":
           cmd =  "%s | awk '{print $6 + $10}'"%cmd
       else:
           raise InvalidValuePassed("Unkown Value %s"%type)
      
       return self.run_command_single_output(cmd)[0]

   def startStress(self):
      
      """
      details: starts cpu stress test on machine in background and returns
      """
      
      self.wget_chmod_file("http://spica/sqa/tools/stress")
      
      cpus = self.getCPUs()
      
      cmd =  "./stress --cpu %s --vm 30  --vm-bytes 128M"%cpus
      self.run_command(cmd,bg = True)
      
   def stopStress(self):
      """
      details: stops stress test
      """
      self.run_command("killall stress")
   
   def startVgcDriver(self):
      
      self.driver.start()
      
   def restartVgcDriver(self):
      
      self.driver.restart()
      
   def getCPUs(self):
       
       """
       returns no of cpus, example "24"
       """
       cmd = 'grep -w "processor" /proc/cpuinfo | tail -1'
       output = self.run_command_single_output(cmd)
       
       noCpus = parseSplit(output)['processor']
  
       return noCpus
   
   def getCPUModel(self):
       
       cmd = 'grep -w "model name" /proc/cpuinfo | tail -1'
       output = self.run_command_single_output(cmd)
       
       cpuModel = parseSplit(output)['model name']
       
       return cpuModel
       
   def clear_dmesg(self):
       print "Clearing dmesg"
       self.run_command_chk_rc("dmesg -c>/dev/null")
       return 1
   
   def clear_dmesg_syslogs(self):
      
        """
        description : clears both dmesg/syslogs
        returns : 1 on success
        """
        
	self.clear_dmesg()
	self.clear_syslogs()
	return 1
   
   def get_machine_type(self):
      """ returns Machine type and model as tuple
      example:
      ('HP', 'ProLiant DL380p Gen8')
      """
      out = self.run_command_get_output("dmidecode -t system")
      return parse_dmidecode(out)
      
      
   def clear_syslogs(self):
       print "Clearing syslogs"
       self.run_command_chk_rc("echo \" \" > /var/log/messages")
       return 1
      
   # Deprecate, use print_syslogs_dmesg instead
   def get_dmesg(self,chkForErrors = 1,raiseOnErrors = 1):
       o = self.run_command_chk_rc("dmesg")
       print "Getting dmesg"

       out =  o['output']
       print "("
       for l in out:
           print l
       print ")"
       
       if chkForErrors:
	   self.chk_for_errors_dmesg_syslogs(out,raiseOnErrors)
       return 1
   
   def chk_for_errors_dmesg_syslogs(self,output,raiseOnErrors = 0):
	   
	for l in output:
	  
           for e in syslogErrors:
	       if re.search(e,l):
                   strErr = "Found error str '%s' in dmesg or syslog line '%s'"%(e,l)
                   if raiseOnErrors == 1:
                     
		      raise ViriError(strErr)
		      sys.exit(1)
                   trace_error(strErr)
	return 1
       
   def print_syslogs_dmesg(self,chkForErrors = 1,raiseOnErrors = 0):
       """
       inputs: None
       print syslogs and dmesg to the output
       raises on errros
       
       """
       for cmd in ["cat /var/log/messages","dmesg"]:
         o = self.run_command_chk_rc(cmd)
         print "Getting %s"%cmd

         out =  o['output']
       
         if chkForErrors:
	   self.chk_for_errors_dmesg_syslogs(out,raiseOnErrors)

       return 1
   
 
   def verify_card_good_state(self,device):
       
       """
       input: device as /dev/vgca
       details:verfies card is in good state
       returns: 1 on succes, exception on failure
       
       """
       
       #EXPECTED_GOOD_STATE = "Good"
       
       
       if not if_vgc_dev(device):
             return 1

       
       vm = vgcMonitor(self)
       
       state =  vm.getDeviceStatus(device)
       
       if state != EXPECTED_GOOD_STATE:
           raise ViriError("Card '%s' is not in '%s' state, found state as '%s'"%(device,EXPECTED_GOOD_STATE,state))
       return 1
  
   def get_bdev(self,devPart):
      
       """
       details : runs blockdev command
       """
       cmd = "blockdev --getsize64 %s"%devPart
       out =  self.run_command_chk_rc(cmd)
       o  = out['output']
       bsize =  o[1]

       try:
           bsize = int(bsize)
       except ValueError:
           trace_error("Couldn't find the bdev for device %s as integer, found '%s' instead"%(device,bsize))
           sys.exit(1)

       return bsize

   def get_ipmi_ip_addr(self):
        """
        returns : ipmi ip address of the host
        """
        command = "ipmitool lan print  | grep \"IP Address\" | grep -v Source | awk -F \":\" '{print $2}'"
        out = self.run_command_chk_rc(command)
        output = out['output']
        print output

   def if_file_exists(self,file_path):

       # --color option was given since is changing pexpect
       command = "ls --color=none " + file_path

       out = self.run_command(command)
       rc = out['rc']

       if rc == 0:
           return True

       return False
   
   def rmFileifExists(self,file_path):
       
       if self.if_file_exists(file_path):
            self.run_command_chk_rc("rm -rf %s*"%file_path)
       return 1
   def createDirifNotExists(self,dir):
       
       if self.if_file_exists(dir):
            return 1
       self.mkdir(dir)
       return 2
 
   def create_fs(self,device,fs,options = None):
       """ Example Usage: 
       h = Host("sqa05")
       h.create_fs("/dev/vgca0","ext3"," -J size=400") 
       h.create_fs("/dev/vgca0","xfs") """

       #self.connection.setwinsize(400,400)

       #command = "mkfs." + fs + " " +  device
       expected_prompt = self.expected_prompt

       # expected prompt had to be changed
       # this is hack
       # ext3/4 filesys get stuck, seems like if the expected prompt is complicated
       # pexpect gets stuck
       self.expected_prompt ='~( |\])# '
       

       command = "mkfs.%s %s"%(fs,device)

       if options:
           command = command + " " +  options

       # xfs requires -f option
       if fs == "xfs":
           command = command + " -f" 
       self.run_command_chk_rc(command)
       
       self.expected_prompt = expected_prompt 
       return 1

   def mount_fs(self,device,mnt_point):
       
       if not mnt_point.startswith("/"):
	       trace_error("Mount point '%s' doesnt starts with /"%mnt_point)
	       sys.exit(1) 
       command = "mount %s %s"%(device,mnt_point)
       self.run_command_chk_rc(command)
       
       
       out = self.run_command_chk_rc("mount | grep  %s"%device)
       
       trace_info("Output of mount")
       output = out['output']
       printOutput(output)
       
       out = self.run_command_chk_rc("file -s %s"%device)
       
       trace_info("Output of file -s")
       output = out['output']
       printOutput(output)
         
       return 1
   
   def get_mount_details(self,device):
	"""get filesystem and mount point,device from mount command
	takes device as input
        
        returns e.g. {'/dev/vgca0': {'mntpoint': '/hello', 'perm': 'rw', 'filesys': 'xfs'}}
        """
        
	cmd = "mount | grep %s"%device
	
	o = self.run_command_chk_rc(cmd)
	output = o['output']
	
	pOut = parseMountOutput(output)
	
	return pOut
   
   def mount_fs_all(self,device,mnt_point,filesys):
       
     
       """ deltes mnt point if present,creats fs and mounts """
       self.run_command("umount %s"%device)
       self.mkdir(mnt_point,force = 1)
       
       self.create_fs(device,filesys)
       self.mount_fs(device,mnt_point)
       found_fs = self.get_mount_details(device)[device]['filesys']
       
       if filesys == found_fs:
         print "INFO: Successfully created fs '%s' on device '%s'"%(filesys,device)
         return 1
       
       raise ViriError("Not able to create fs '%s' on device, please check mount command"%filesys)
      
   
   def getDuMap(self,device):
       
       vproc = vgcProc(self)
       return vproc.getDuMap(device)

   def confVgcdConfMount(self,devPart,mntPnt,fs):
       #/dev/vgca0   /mnt  ext3    noauto,defaults        0 0
       str = "%s %s %s noauto,defaults        0 0"%(devPart,mntPnt,fs)
       cmd = "echo %s >> /etc/fstab"%str
       self.run_command_chk_rc(cmd)
       self.mkdir(mntPnt)
       #MOUNT_POINTS=""
       #sed -i 's/MOUNT_POINTS=\"\"/MOUNT_POINTS=\"\/nand4\"/' /etc/sysconfig/vgcd.conf
       cmd = "sed -i 's/MOUNT_POINTS=\"\"/MOUNT_POINTS=\"\"/' /etc/sysconfig/vgcd.conf"
       self.run_command_chk_rc(cmd)

       cmd = "sed -i 's/MOUNT_POINTS=\"\"/MOUNT_POINTS=\"\%s\"/' /etc/sysconfig/vgcd.conf"%mntPnt
       self.run_command_chk_rc(cmd)
       return 1

   def umount_fs(self,device):
       command = "umount %s "%device
       self.run_command_chk_rc(command)
       return 1

   def umount(self,device):
       try:
          self.umount_fs(device)
       # Hmm, TO DO why is CommandError not catched, have to pass VirExceptions
       except VirExceptions.CommandError:
          trace_info("Seems like device %s is already unmounted"%device)
          pass
 
   def mount(self,device,mnt_point):
       try:
          self.mount_fs(device,mnt_point)
       except CommandError:
          trace_info("Seems like device %s is already mounted"%device)
          pass

   def get_md5sum(self,file):
       comm = "md5sum %s | awk '{print $1}'"%file
       o = self.run_command_chk_rc(comm)
       md5sum = o['output']
       return md5sum[1]
   
   def create_fs_get_md5sum_umount(self,devPart,mntPnt):
      """
      inputs  : device and mount Pnt , as example /nand
      details : creates ext4 filesystem, gets md5sum file and unmounts , uses file
         as file1
      returns : md5sum
      """
        
      filesys = "ext4"
      self.umount(devPart)
        
      self.mount_fs_all(devPart,mntPnt,filesys)
      file1 = mntPnt + "/file1"
      mdsum1 = self.create_file_dd_get_md5sum(file1)
      self.umount_fs(devPart)
      return mdsum1
   
   def mount_get_md5sum_umount(self,devPart,mntPnt,mdsum1):
      
      """
      inputs  : device and mount Pnt , md5sum to compare
      details : mounts ,gets md5sum,umounts, compares
      returns : 1 on success, exception on failure
      """
      
      self.mount_fs(devPart,mntPnt)
        
      file1 = mntPnt + "/file1" # Create file name file1
      mdsum2 = self.get_md5sum(file1)
      cmp_md5sum(mdsum1,mdsum2,"mounting fs")
      return 1
   
   def create_file_dd_get_md5sum(self,filePath):
	   io = DD(self)
	   io.runIO(filePath)
	   md5sum = self.get_md5sum(filePath)
	   return md5sum
   # this should t ake care of ubuntu also 

   def is_ubuntu_installed(self):
       if self.if_file_exists("/usr/bin/dpkg"):
          trace_info("Ubuntu seem to be the OS")
          return True
       return False
        
   
   def is_vgc_rpm_installed(self):
       
       # TOD vgc|vfstore to be a variable

       if self.is_ubuntu_installed():
          return 1
       
       o = self.run_command("rpm -qa | egrep \"vgc|vfstore\"")
       ##o = self.run_command("rpm -qa | grep \"vgc|vfstore\"")
       
       out = o['output']
       
       # Remove the command from output
       out = out[1:]
 
       if len(out) == 0:
	   trace_info("Virident drivers doesn't seem to be installed")
	   return False
       return True
       
   def ifVgcRpmLoaded(self,rpm):
       
       """takes rpm as a paramter, checks if it is present"""
       
       try:
          self.run_command_chk_rc("rpm -qa | egrep \"vgc|vfstore\" | grep %s"%rpm)
       except:
           
          trace_error("rpm %s doesn't seem to be loaded"%rpm)
          return False
          sys.exit(1)
       trace_info("vgc rpm '%s' seem to be present"%rpm)
       return 1
       
   def stopVgcDriver(self):
       """ exits if fail to stop,returns 1 on success,returns 2 if
       driver are not installed, 3 if driver is not present already """
       trace_info("Stopping vgcd driver")
       o = self.run_command("service vgcd stop")
       rc = o['rc']
       out = o['output']

       errString = "ERROR"
       if isStringPresentArray(out[1:],errString):

                trace_error("Failed to stop Driver, found string %s"%errString)
                sys.exit(1)
           
       driverAlreadyUnloadedStr = "kernel modules are not loaded"
       if isStringPresentArray(out[1:],driverAlreadyUnloadedStr):
               trace_info("Seems like driver already unloaded")
	       
       driverNotInstalledStr = "unrecognized service"
       if isStringPresentArray(out[1:],driverNotInstalledStr):
               trace_info("Seems like driver not installed while unloading driver, found string '%s'"%driverNotInstalledStr)
	       return 2
       driverNotInstalledStrSlesSP2 = "no such service"
       if isStringPresentArray(out[1:],driverNotInstalledStrSlesSP2):
               trace_info("Seems like driver not installed while unloading driver, found string '%s'"%driverNotInstalledStr)
	       return 3
           
       return 1
       
       
   def get_ubuntu_installed(self):
      
      cmd =  "dpkg --list  | egrep \"vgc|vfstore\" | awk '{print $2}'"
      self.run_command_chk_rc(cmd)
      
   def rmVgcdDrivers(self):
	  
	   # for rpm only
	# first try to stop the driver 
	# if rc is not 1 then just return
	
	if not self.is_vgc_rpm_installed():
	    return 1
	
	rc = self.stopVgcDriver()
        
        # just check rc as 1, other return code already 
        if rc == 1:
                   trace_info("Removing drivers")
                   cmd = "rpm -qa | egrep \"vgc|vfstore\" | xargs rpm -ev"
                   if self.is_ubuntu_installed():
                     #TO DO : Use Purge also
                     cmd = "dpkg --list | egrep \"vgc|vfstore\" |  awk '{print $2}' | xargs dpkg --remove"
                     
		   self.run_command_chk_rc(cmd)
        return rc
   
   def create_file(self,file):
       #comm = "dd if=/dev/urandom of=%s bs=1G count=1"%file
       comm = "dd if=/dev/urandom of=%s bs=4K count=1000 oflag=direct"%file
       self.run_command_chk_rc(comm)
       self.run_command_chk_rc("sync")
       return 1
   def get_kernel_ver(self):
       """
       returns : kernel version
       """
       kernel = self.run_command_chk_rc("uname -r")['output'][1]
       trace_info("Found kernel '%s'"%kernel)
       return kernel

   def cat_etc_issue(self):
      
       """
       
       returns: relevant distros, examples are redhat6,redhat5,sles11sp2, sless11sp1
       Usage example:
       
       print h.cat_etc_issue()  # will print redhat6 where h is the host object
       
       """
       if not self.if_file_exists("/etc/issue"):       
           trace_error("/etc/issue doesn't exists")
           sys.exit(1)
       o = self.run_command_chk_rc("cat /etc/issue")
       out = o['output']
       
       try:
          p = parse_cat_etc_issue(out)
       except:
	  trace_info("Cound'nt find the version from /etc/issue,Trying from kernel")
	  # this is hack and need to be re written
	  kernel = self.get_kernel_ver()
	  
	  if re.search("2\.6\.32",kernel):
		  trace_info("Seem like redhat6 kernel")
		  return "redhat6"
	  elif re.search("2\.6\.18",kernel):
		  trace_info("Seem like redhat5 kernel")
		  return "redhat5"
	  else:
		trace_error("Failed fo find linux flavor")
		sys.exit(1)

       return p
   
   def cat_etc_issue1(self):
      
      """ same as cat_etc_issue method, but return redhat61 or 60, depending on the kernel"""
      linux = self.cat_etc_issue()
      kernel = self.get_kernel_ver()
      
      if linux == "redhat6":
         m = re.search("2.6.32-(\d+).*el6.*",kernel)
         minorVer = m.group(1)
         if int(minorVer) >= 131:
            return "redhat61"
         return "redhat60"
      
      return linux
   def inStatsSame(self):
       build = self.vgcmonitor.getBuildOnly()
       
       build = reverse_build(build)
       
       self.installBuild(build,stats = 1,emc = 0)

   def installBuildStatsSame(self):
       """installs the stats build from the current build """
       build = self.vgcmonitor.getBuildOnly()
       
       build = reverse_build(build)
       
       self.installBuild(build,stats = 1,emc = 0)
       
   def installBuild(self,build,stats = None,server = "cloudy.virident.info", toolsTest = 1,pathType = "releases",emc = 1,firmware = "0",releaseVer = None,rdma = None):
   
	
	"""h.installBuild("C4.46300")"""
	
        try:
          emc = int(emc)
          #firmware = int(firmware)
          toolsTest = int(toolsTest)
          stats = int(stats)
          
        except:
            print "ERR: Couln't convert some value to integer in install Build"
            raise


        if firmware != "0":
            if (firmware != "downgrade" and firmware != "upgrade"
                 and firmware != False):
               raise ViriError("Not valid firmware value '%s'"%firmware)
            
        releaseVersion = "3.2"

        #  TO DO,hack
        if build == "C6.50744":
           releaseVersion = "3.1"
        if build == "C6.51287":
           releaseVersion = "3.1.1"
        if build.startswith("C7A"):
           releaseVersion = "3.2.1"
           
	
        # TO DO
        #releaseVersionEMC = "1.0.SP1.GA"
        releaseVersionEMC = "1.3.GA"
        
    
        releaseVersionDash = releaseVersion + "-"

        # ovoer fide if passed
        if releaseVer:
           releaseVersion = releaseVer
           # TO DO 

           releaseVersionDash = releaseVersion + "-"
        redhatPrepend = "kmod-vgc-"

        # TO DO improve logic here
        if emc:
	    releaseVersionDash = releaseVersionEMC + "-"
            releaseVersion = releaseVersionEMC

        revBuild = reverse_build(build)
        
        # for 3.2.4 Build , hack
        if "_DPP" in build:
            #>>> '60469.C7A_DPP'.replace('_','.')
            #'60469.C7A.DPP'
            print "Found _DPP in build, in build '%s'"%build
            revBuild = reverse_build(build)
            revBuild = revBuild.replace('_','.')
        
        #print revBuild 
        #sys.exit(1)
        
        trace_info_dashed("Installing build '%s'"%build)
        
        
        if emc and stats:
            raise ViriValuePassedError("Both emc and stats are true, please remove one of them")

        print "-"
	linux = self.cat_etc_issue()
	kernel = self.get_kernel_ver()
	
 
        #httpPath = get_build_string(build,linux,pathType,emc,server)
  
	
	trace_info("Found linux distro '%s'"%linux)

        found_redhat = "0"
        found_ubuntu = "0"
	prependstr = " "
	
        
	# TO DO add emc support 
	# Redhat 5 needs not deps for now
	if linux == "redhat6":
	    found_redhat = "1"
	    try:
               m = re.search("2.6.32-(\d+).*el6.*",kernel)
	       minorVer = m.group(1)
	       
	       #print minorVer
	       if int(minorVer) >= 131:
		
		    prependstr = "redhat6.1+-"
                    
                    if emc:
                     prependstr = "EMCvPCIeSSD.RHEL6x-"
          
	       elif int(minorVer) == 71:
		    #prependstr = "kmod-vgc-2.6.32-71.el6.x86_64-3.0-"
		    prependstr = "redhat6.0-"
                    
                    if emc:
                     prependstr = "EMCvPCIeSSD.RHEL60-"
                  
	       else:
		    trace_error("Couldn't find the prepend string for redhat6 '%s'"%kernel)
		    sys.exit(1)
			
	    except:
		trace_error("could get the minor version for Redhat6 kernel '%s'"%kernel)
		sys.exit(1)
	       
	elif linux == "redhat5":
	        found_redhat = "1"
                #prependstr = "kmod-vgc-2.6.18-8.el5-3.0-"
                prependstr = "redhat5.x-"
                if emc:
                     prependstr = "EMCvPCIeSSD.RHEL5x-"

	elif linux == "sles11sp1":
            
		
		prependstr = "vgc-sles11sp1-kmp-default-%s_2.6.32.59_0.3-"%releaseVersion

	elif linux == "sles11sp2":
  
                #prependstr ="vgc-sles11sp2-kmp-default-%s_3.0.58_0.6.6-"%releaseVersion
                prependstr ="vgc-sles11sp2-kmp-default-%s_3.0.80_0.5-"%releaseVersion
	elif linux == "sles11sp3":
	        prependstr = "vgc-sles11sp3-kmp-default-%s_3.0.76_0.11-"%releaseVersion

	elif re.search("ubuntu",linux):
               #found_ubuntu = 1
               found_ubuntu = "1"
               prependstr = "vgc-"
	else:
		trace_error("Couldn't find linux version %s"%linux)
		sys.exit(1)
	
	# if redhat prepend kmod-vgc and add 3.1 in the end
	if found_redhat == "1":
	    # kmod-vgc + rehdat6.1+ + 3.1-
	    prependstr = redhatPrepend +  prependstr + releaseVersionDash

	lastStr = ".x86_64.rpm"
        
	lastStrStats = ".stats" + lastStr
        
        
        # TO DO for vha.
        for comm in ["service corosync stop", "service pacemaker stop","service cman stop"]:
           self.run_command(comm)
        
        # for downgrade do not remove drivers, yet
        if firmware == "downgrade":
            self.run_command_chk_rc("service vgcd stop")
         
            self.driver.download_fw_installed(status = "downgrade")

	# TO OD make 3.1 variable
   
	httpPathUtils1 = "vgc-utils-" + releaseVersionDash + revBuild + lastStr
	httpPathTools1 = "vgc-tools-" + releaseVersionDash + revBuild + lastStr
	httpPathTests1 = "vgc-tests-" + releaseVersionDash + revBuild + lastStr
        httpPathRdma1  = "vgc_rdma-" + kernel + "-"  + releaseVersionDash + revBuild + lastStr
        
        found_driver_rpms = 0
        # variosus srivers
        for server in self.driver.get_servers():
         
           if found_driver_rpms == 1:
               break
           for pathType in self.driver.get_path_types():
               httpPath = get_build_string(build,linux,pathType,emc,server)
               httpPathUtils = httpPath + httpPathUtils1
               httpPathTools = httpPath + httpPathTools1
               httpPathTests = httpPath + httpPathTests1
               httpPathRdma  = httpPath + httpPathRdma1
       
               if stats:
                       lastStr = lastStrStats
               
               httpPathDrv = httpPath + prependstr + revBuild + lastStr
                     
               cmd = "rpm -ivph %s %s "%(httpPathDrv,httpPathUtils)
               #print cmd;sys.exit(1)
             
               if rdma:
                 cmd = cmd + httpPathRdma
                 
               cmd = cmd + " --nodeps"
       
               self.rmVgcdDrivers()
       
               trace_info("Installing drivers")
               
                # UBUNTU
               if found_ubuntu == "1":
                   driverString = "vgc-" + kernel + "_" + releaseVersionDash  + revBuild + "_amd64.deb"
                   driverUtils = "vgc-utils" + "_" + releaseVersionDash  + revBuild + "_amd64.deb"
                   drivers = [driverString ,driverUtils]
                   string = ""
                   
                   
                   for driver in drivers:
                      path = httpPath + driver
                      
                      # for Ubuntu RpmError will go to the next loop if failed
                      try:
                        self.wget_file(path)
                      # Host.py doesnt catch this exception only RpmError, need to modify
                      # HostLinux.py should work fine.
                      except RpmError:
                        
                        trace_info("Retrying failed to get rpms on %s"%path)
                        continue
                        
                      except VirExceptions.CommandError :
                        trace_info("Retrying failed to get rpms on %s"%path)
                        continue
                      string = string + driver + " "
                      #self.run_command_chk_rc("dpkg -i %s"%driver)
                   #print string
                   cmd = "dpkg -i %s"%string
         
               try:
                 self.run_command_chk_rc(cmd)
                 found_driver_rpms = 1
                 break
	       # TODO for some reason if you have HostLinux class
	       # exception only work with  VirExceptions.CommandError and no
	       # CommandError
               
               
               except CommandError: # for Host.py TOD0
                  
                  trace_info("Seems like install with packages =%s, " \
                  "server='%s' failed, retrying..."%(pathType,server))
                  continue
               except VirExceptions.CommandError,e:
                 #print e
                 #raise RpmError("rpm Install Failed")
                 trace_info("Seems like install with packages =%s, " \
                  "server='%s' failed, retrying..."%(pathType,server))
                 continue
        
        if found_driver_rpms == 0:
            raise RpmError("Could not find driver rpms")
       
             
        if firmware == "downgrade":
           # need to add sleep, since we might run into issues
           sleep_time(45, "before power cycling for downgrade")
           self.power_cycle()
           #trace_info("Please power cycle machine after fw downgrade")
           sys.exit(1)
           
        if firmware == "upgrade":
            #print "Exiting";sys.exit(1)
            
            self.driver.download_fw(build,status = "upgrade")
            
            self.power_cycle()
            #print "Please Power cycle the machine!!!!"
            return 1
            
	
        # TO DO Ubunutu hack, wont install tools
        if found_ubuntu == "0":
	 if toolsTest:
		cmd = "rpm -ivph %s %s --nodeps"%(httpPathTools,httpPathTests)
                trace_info("Installing tools and stats rpms")
		#trace_info("Running command cmd '%s'"%cmd)
                
               
		self.run_command_chk_rc(cmd)

	self.startVgcDriver()
        
        cmd = "rpm -qa | grep vgc"
        
        if found_ubuntu == 1:
           cmd = "dpkg --list | egrep \"vgc|vfstore\""
        
        #self.run_command_chk_rc("rpm -qa | grep vgc")
	self.run_command_chk_rc("vgc-monitor")
        
        trace_success_dashed("Install seems successful")
	#sys.exit(1)
	return 1
        
   def is_binary_present(self,bin):
       """ runs 'which' command to see if the binary is present """
       trace_info ("INFO: Cheking if binary '%s' is  present"%bin)
       comm = "which %s"%bin
       try:
          self.run_command_chk_rc(comm)
       except CommandError:
          trace_info ("INFO: Seems like binary '%s' is not present"%bin)
          return False
       
       trace_info ("INFO: Seems like binary '%s' is  present"%bin)
       return True
   
   def get_fs_binaries(self, ):
      
      return ['mkfs.xfs','mkfs.ext4','mkfs.ext3','mkfs.ext2' ]
      pass
   
   def install_xfs(self, ):
      self.host_run_commmand("yum -y install xfsprogs")
      
 
   def is_all_fs_binaries_present(self):
       
       FS_BINARIES = self.get_fs_binaries()
       
       for bin in FS_BINARIES:
           if not self.is_binary_present(bin):
               sys.exit(1)
           
   
   def create_all_fs(self,devPart ):
      mntPnt = "/nand5"
      for filesys in ['xfs','ext4','ext3','ext2' ]:
         
        self.umount(devPart)
        
        self.mount_fs_all(devPart,mntPnt,filesys)
        file1 = mntPnt + "/file1"
        mdsum1 = self.create_file_dd_get_md5sum(file1)
        self.umount_fs(devPart)
        
        # Stimulus
        self.run_command_chk_rc("service vgcd restart")
        sleep_time(3,"after restarting service")
        
        self.mount_fs(devPart,mntPnt)
        mdsum2 = self.get_md5sum(file1)
        cmp_md5sum(mdsum1,mdsum2,"mounting fs %s"%filesys)
        
        self.umount_fs(devPart)
        
   
     
   def mkdir(self,dir,force =1 ):
       
       if force == 1:
	     try:
                self.run_command_chk_rc("rm -rf %s"%dir)
             except CommandError:
                print "INFO: Seems like directory to remove doesn't exist"
                
	       
	       
       comm = "mkdir %s"%dir
       self.run_command_chk_rc(comm)
       return 1

   def rmdir(self,dir):
       comm = "rm -rf %s"%dir
       try:
          self.run_command_chk_rc(comm)
       except CommandError:
          print "INFO: Seems like directory to remove doesn't exist"
          sys.exit(1)
       return 1

   def scp(self,dest,userid,passwd):

       prompt_regex = "password"
       rc = self.connection.expect([prompt_regex],timeout = 60)
       self.connection.sendline(passwd)
       self.connection.expect(self.expected_prompt,140)

   def vgc_sec_er(self,device,option):
       if option != "purge" and option != "clear" and option != "verbose" and option != "default":
           print "ERR: Please pass option as purge /clear /default/verbose"
           sys.exit(1)
       #vgcSecErPath= "/usr/lib/virident/vgc-secure-erase"
       vgcSecErPath= "vgc-secure-erase"
       comm = "%s --%s %s"%(vgcSecErPath,option,device)
       trace_info("Running vgc secure erase command '%s'"%comm)

       t1 = get_epoch_time()
       
       if option == "default":
          comm = "%s %s"%(vgcSecErPath,device)
       self.connection.sendline(comm)
       rc = self.connection.expect(["Do you want to continue","Device or resource busy"])
       if rc == 1:
           err = "Found 'Device or resource busy' in command '%s'"%comm
           trace_error(err)
           raise DeviceBusy(err)
       self.connection.sendline("yes")
       self.connection.expect(self.expected_prompt,14000)
       output = self.connection.before.strip()
       output_a = output.split("\r\n")
       t2 = get_epoch_time()
       tDiff = t2 - t1

       trace_info("Time took to run tests '%i' secs"%tDiff)
       return output_a

   # run in the background
   def vgc_sec_er_b(self,device_p,option):
       comm = "echo \"yes\" |vgc-secure-erase --%s %s&"%(option,device_p)

       self.run_command(comm)
       return 1


   def kill_proc(self,proc):
       """
       details: kill process given its id
       """
       self.run_command_chk_rc("kill -9 `pidof %s`"%proc,timeout = 1000)
       return 1
   def ser_reload(self,ser = "vgcd"):
       self.run_command_chk_rc("service %s reload"%ser,timeout = 1000)
   def ser_sts(self,sts,ser = "vgcd"):
       self.run_command_chk_rc("service %s %s"%(ser,sts),timeout = 1000)
 

   def chk_valid_vgc_conf_opt(self,opt,opt_param):

       if opt == "5":
           dict = self.get_vgc_conf_valid_raid()
           if not dict.has_key(opt_param):
               trace_error("Vaild option for opt '%s' is '%s', passed '%s'"%(opt,dict.keys(),opt_param))
               sys.exit(1)
       elif opt == "s":
           dict = self.get_vgc_conf_valid_sector()
           if not dict.has_key(opt_param):
               trace_error("Vaild option for opt '%s' is '%s', passed '%s'"%(opt,dict.keys(),opt_param))
               sys.exit(1)
       elif opt == "m":
           dict = self.get_vgc_conf_valid_mode()
           if not dict.has_key(opt_param):
               trace_error("Vaild option for opt '%s' is '%s', passed '%s'"%(opt,dict.keys(),opt_param))
               sys.exit(1)
       else:
           trace_error("Invalid option opt '%s'"%opt)
           sys.exit(1)
 


 
   
   def is_machine_down_successful(self):
      
        """
        returns: True if machine down is successful
        """
        for i in range(0,16):
           wait = 10
           
           sleep_time(wait, "after reboot") 
        
	   if not if_ping_successful(self.name):
		print "INFO:ping unsucessful, host seem to reboot"
                break
           else:
               trace_info("Ping still succesful,retrying..")
               continue
               
               
	else:
		raise ViriError( "ERR: ping seem to successful,reboot failed")
		sys.exit(1)
       
        return 1
      
   def reboot(self):
      
        """
        description: soft reboots machine using reboot command
        """
        
       
        # This is incase this method is called twice
        if self.connection == None:
            self.logon()
      
        trace_info("Rebooting host")
        #self.run_command("reboot")
	self.connection.sendline("reboot")
        
        self.is_machine_down()

        return 1
      
   
   def is_machine_down(self,wait_for_up = True):
      
      """
      description: check if machine is down, resets the ssh and connection variables,
      waits for it be up
      """
      
      self.is_machine_down_successful()

      if self.connection:
       self.connection.close()
       self.connection = None
       
      if self.ssh:
         self.ssh.close()
         self.ssh = None
     
     
      if wait_for_up:
         is_hostup(self.name)
   
         sleep_time(60,"after host is up")
      
      return True
 
   def power_cycle(self,wait = 10):
            """
            inputs: None
            details: power cycles the machine, get the ipmi or remote power booter details from database
            if ipmi is not present , uses remote power booter, waits for the machine to come up
            returns: 1 on success, exception on failure
            """
            
            cmd = ""
	    db = DB.viriDB()
            # try to power cycle using prpb
	    (ip_addr,ipmiUser,ipmiPasswd) =  db.getIPMI(self.name)
	    if ip_addr:
	       for pw_cmd in ['off','on']:
	         run_ipmi_lan_pw_command(ip_addr,pw_cmd ,ipmiUser,ipmiPasswd)
		 sleep_time(10,"after impi power off waiting")
            else:
             rpb,rpbPort = db.getRpb(self.name)
	     #rpb_power_cycle(rpb,rpbPort)
	     r = RemotePwrBooter(rpb)
	     r.logon()
	     r.port_pwcycle(rpbPort)
             r.connectionClose()
            
            # this method will also make connections as None, forcing it to
            # to reinitialize after reboot
            self.is_machine_down()

            return 1

 
 
   def get_iostat_output(self,file,device,inputType):
       """
       inputs: takes input type as reads, writes,rw
       returns list as '5059.80', '4983.50', '5091.30', '5046.30', '5052.10', '5037.60']
       """
       
       if inputType == "reads":
           awk_string = "$4"
       elif inputType == "writes":
           awk_string = "$5"
       elif inputType == "rw":
           awk_string = "$4 + $5"
       else:
           raise ViriError("Invalid inputType value passed to iostat '%s'"%inputType)
       
       if not self.if_file_exists(file):
           raise ViriError("File '%s' file doesnt exists on host"%file)
       o = self.run_command_chk_rc("cat %s| grep %s| awk '{print %s}'"%(file,device,awk_string))
       
       return o['output'][1:]
       
       

   def get_fs(self,device):
       # check_if_vgc_part(device)
       cmd = "file -s %s"%device
       o = self.run_command_verify_out(cmd,errors = ["No such file"])
       out = o['output']

       regex = ".*\s(\S+)\s+filesystem data"

       fs = ""
       for l in out:
           if re.search(regex,l):
               m = re.search(regex,l)
               fs = m.group(1)
       if not fs:
           trace_error("Couldn't get the file system on device '%s'"%device)
           trace_error("regex '%s' not found in the output of command "%regex)
           print_red("Output = '%s'"%out)
           sys.exit(1)
       # return in lower case letters
       return fs.lower()

   def create_and_verify_fs(self,device,fs,options = None):
       self.create_fs(device,fs,options)
       fs_found = self.get_fs(device)
       if fs == fs_found:
           trace_success("Created filesys '%s' found filesystem '%s' on device %s"%(fs,fs_found,device))
           return 1

       trace_error("Created fs %s found filesystem %s on device %s"%(fs,found_fs,device))
       sys.exit(1)


   def is_directory_empty(self,directory ):
      
      if not self.if_file_exists(directory):
         raise ViriError("directory '%s' doesn't exist"%directory)
      count = self.run_command_single_output("ls -a %s | wc -l"%directory)
      count = int(count[0])
      # . and .. in empty exists still
      
      #trace_info("Found items '%i' items in directory %s"%(count,directory))
      if count > 2:
         
         trace_info("Found items '%i' items in directory, so it is not empty %s"%(count,directory))
         return False
      
      trace_info("Found items '%i' items in directory, so it should be empty %s"%(count,directory))
      return True
   
   def is_crash_dir_empty(self):
      """
      details: check to see if /var/crash is empty,raise exception if not
      """
      
      if not self.is_directory_empty("/var/crash"):
         raise ViriError("crash directory not empty")
      
      return 1
   
   def cp(self,src_file,dst_file):
       cmd = "cp %s %s"%(src_file,dst_file)
       self.run_command_chk_rc(cmd)
       return 1
   def cp_dict(self,dst_file):
       self.cp("/usr/share/dict/linux.words",dst_file)
       return 1
   def get_part_usable_cap(self,device):
       cmd = "vgc-monitor -d %s | grep \"%s\""%(device,device)
       o =  self.run_command_chk_rc(cmd)

       out =  o['output']

       part_usable_cap = {}

       for l in out:
       # if   /dev/vgcc0          2048 GiB            500 GB              enabled   GOOD
           if re.search("/dev/vgc[a-z]\d+.*",l):
               l_a = l.split()
               us_cap = l_a[3]
# more attrib can be added later
               part = l_a[0]
               part_usable_cap[part] = {} 
               part_usable_cap[part]['us_cap'] = us_cap 
       # return {'/dev/vgcc0': {'us_cap': '500'}}
       return part_usable_cap
   def get_part_mode(self,device):
       """get partition mode,takes input as /dev/vgca0"""
       cmd = "vgc-config --p %s  | grep -A1 \"Current Configuration\" | grep %s"%(device,device) 
       o =  self.run_command_chk_rc(cmd)
       out = o['output']
       l_a = out[1].split()
       
       l_m = l_a[1]
       l_m_a = l_m.split("=")

       mod =  l_m_a[1]

       return mod
   
 
		   
   def parse_vgc_config(self,out):
       dict = {}

       for l in out:
           if re.search("/dev/vgc[a-z]\d+",l):
               a  = l.split()
               dev_p = a[0]
               dict[dev_p] = {}

               mode_str = a[1]
               mode_a   = mode_str.split("=")
               mode    = mode_a[1]

               sec_str = a[2]
               sec_a   = sec_str.split("=")
               sec     = sec_a[1]
               
               raid_str = a[3]
               raid_a   = raid_str.split("=")
               raid     = raid_a[1]
               dict[dev_p]['raid'] = raid
               dict[dev_p]['sector'] = sec 
               dict[dev_p]['mode'] =  mode 
	 
       return dict
	   
   def vgc_config1(self):
       """get partition mode,takes input as /dev/vgca0"""
       o =  self.run_command_chk_rc("vgc-config")
       out = o['output']
       
       dict = self.parse_vgc_config(out)
       return dict 

   def get_card_attr(self,device,attr):
       return self.run_vgc_monitor(device)[attr]

   def get_card_serial(self,device):
       """get card serial,takes input as /dev/vgca"""
       return self.get_card_attr(device,"serial")
   def get_card_part_attr(self,device,attr):
       check_if_vgc_part(device)
       # get /dev/vgca out of /dev/vgca0
       dev = get_device_part(device)
       """get card serial,takes input as /dev/vgca"""
       return self.run_vgc_monitor(dev)['part'][device][attr]

   def get_card_part_rw(self,dev_p):
       check_if_vgc_part(dev_p)
       dev = get_device_part(dev_p)
       vgcMon = self.run_vgc_monitor(dev)
       dict = {}
       read  = vgcMon['part'][dev_p]['read']
       write = vgcMon['part'][dev_p]['write']
       return (read,write) 

   def get_card_part_rw_life(self,dev_p):
       check_if_vgc_part(dev_p)
       dev = get_device_part(dev_p)
       vgcMon = self.run_vgc_monitor(dev)
       dict = {}
       read  = vgcMon['part'][dev_p]['read']
       write = vgcMon['part'][dev_p]['write']
       life = vgcMon['part'][dev_p]['life']
       return (read,write,life) 



   def get_offset_0_pbn(self,drive):
       """takes a0 and map as inputs"""
       option = "map"
       cmd = "%s /proc/driver/virident/vgcdrive%s/%s | head -1"%(VGCPROC,drive,option)
       o =  self.run_command_chk_rc(cmd)
       x = o['output'][1]
       x_a = x.split()
       return x_a[1]

 


   def get_host_device_ver(self,device):
       """takes /dev/vgcc0 or /dev/vgcc as input,print kernel, cat /etc/isue"""

       #chk_if_vdent_dev(device)

       # if device is
       
       if not if_vgc_dev(device):
             device = "NotVgcDev"

       
       elif if_vgc_dev_part(device):
           device = get_vgc_dev_from_part(device)
       build = self.run_vgc_monitor(device)['build']
       
       #build = self.get_card_part_main_attr(device)['build']
       kernel = self.get_kernel_ver()
       ver = self.cat_etc_issue()

       det = {}

       det['kernel'] = kernel 
       det['version'] = ver  # version of redhat
       det['build']   = build

       return det

   def if_file_has_string(self,string,file):

       if not self.if_file_exists(file):
           trace_error("File '%s' doesn't exist in the system"%file)
           sys.exit(1)
       o = self.run_command("grep \"%s\" %s"%(string,file))
       rc = o['rc']

       if rc == 0:
           trace_info("Found string '%s' in file '%s' ,grep rc = '%i'"%(string,file,rc))
           return True

       trace_info(" Didn't find string '%s' in file '%s' ,grep rc = '%i'"%(string,file,rc))
       return False

   def get_blockdev(self,dev_p):
       cmd = "blockdev --getsize64 " + dev_p
       o =  self.run_command_chk_rc(cmd)
       blocks =  o['output'][1]
       try:
           int(blocks)
       except ValueError:
           trace_error("Found blocks as '%s' not as integer"%blocks)
           raise
       
       return blocks

   def wget_file(self,filePath):
      
      try:

          self.run_command_chk_rc("wget %s"%filePath)
      except CommandError:
          raise RpmError( "ERR: wget to path '%s' failed"%filePath)

   def wget_chmod_file(self,filePath):

      """ removes file if exits, does chmod +x"""
      
      fileName = self.wgetReturnFileName(filePath)
      
      self.run_command_chk_rc("chmod +x %s"%fileName)
      
      return fileName
      
   def wgetReturnFileName(self,filePath):
       
       # get file
       
       try:
          m = re.search(".*/(\S+)$",filePath)
          file = m.group(1)
       
       except:
          trace_error("Couln't get file name from wget file path '%s'"%filePath)
          raise

       self.rmFileifExists(file)
       self.wget_file(filePath)
       return file
       
      
      
   
   def untar_and_unzip_file(self,file):
         """untars file and unzips file"""
         self.run_command_chk_rc("tar -xvzf %s"%file)
         
         return 1
   def untar_and_unzip_file_cd(self,file,dir):
         
         self.untar_and_unzip_file(file)
         self.run_command_chk_rc("cd %s"%dir)
         
         return 1
         
   def chmod(self,filePath,perm):
      
      try:

          self.run_command_chk_rc("chmod %s %s"%(perm,filePath))
      except CommandError:
          print "ERR: Change of permission '%s' to file '%s' failed"%(perm,filePath) 
          sys.exit(1)
   
   def ifDriverLoaded(self):
        vm = vgcMonitor(self)
     	return vm.ifDriverLoaded()
  
   def if_dpp_errors_drive_vgcopt(self,drvLetter,vgcprocOpt,partition = "0"):
           o = self.run_command_chk_rc("%s /proc/driver/virident/vgcdrive%s%s/%s | grep DPP"
                        %(VGCPROC,drvLetter,partition,vgcprocOpt))

           out = o['output']
           out.pop(0) # remove command
           for l in out:
               print l
               l_a = l.split(":")
               #print l_a
               #sys.exit(1)
               try:
                  error = l_a[1]
               except IndexError:
                   printOutput(out)
                   raise IndexError ("Couldn't split string '%s'"%l_a)
               error = error.strip() # remove any white space
               if int(error) > 0:
                   str =  "Found dpp error '%s' for drive '%s' details '%s' vgcproc option as '%s'"%(error,drvLetter,l,vgcprocOpt)
                   print str
                   return True,str
                   #sys.exit(1)
               #print "error = '%s'"%error

           return False, " "

   def if_dpp_errors(self,dev_p):

        drvLetter,partition = get_device_letter_part(dev_p)

        for opt in ["bb_stats", "bdev"]:
            sts,str = self.if_dpp_errors_drive_vgcopt(drvLetter,"bb_stats",partition)
            if sts:
               trace_error(str)
               return sts,str

        return False, " "

   def chk_if_dpp_errors(self,dev_p):
        sts,str = self.if_dpp_errors(dev_p)

        if sts:
            return True
        return False
   
   def get_ue_errors(self,devPart):
       
       """
       returns: UE errors found as integer,with errors string as tuple, 
       inputs : example /dev/vgca0  """

       return self.vgcproc.get_ue_errors(devPart)
   
   def chk_if_ue_errors(self,devPart):
       
       """ raises exception if ue errors on device Passed, as /dev/vgca0"""
       
       self.vgcproc.chk_if_ue_errors(devPart)
  
   def create_kernel_panic(self):
       # (sleep 10 && echo c >/proc/sysrq-trigger)&
       self.run_command_chk_rc("(sleep 10 && echo c >/proc/sysrq-trigger)&")
   
   def verifications(self):
      
      v = Machine.Verifications.verifications(self)
      return v
 
   def lspci_get_viri_pci_ids(self):
       """returns ['0000:04:00.0', '0000:86:00.0']"""
       o = self.run_command_chk_rc("lspci -d 1a78: -D")
       out = o['output']
       
       ids = []
       for l in out:
         
         if re.search("Virident",l):
            l_a = l.split()
            ids.append(l_a[0])
       return ids

   
   def chk_viri_lspci_errors(self):
      
      self.verifications().chk_viri_lspci_errors()

   def run_dd(self,devPart,bs = "1G",count = "1",bg = True):

      self.run_command("dd if=/dev/zero of=%s bs=%s count=%s oflag=direct"%(devPart,bs,count),bg = bg)
      self.chkIfProcessRunning("dd if")

   def wait_for_dd_to_complete(self):
      for i in range(1,100):
          if not self.ifProcessRunning("dd if"):
            trace_info("dd seem to have completed fine")
            return True
	  sleep_time(5,"dd is still running,waiting for it to complete, iteration %i"%i)
      raise ViriError("dd failed to stop")

   
   def vdbench(self):
      
      """
      returns vdbench object
      
      """
      return vdbench(self)

   def ib(self, ):
      """
      
      returns Infiniband object
      """
      ib = VgcUtils.Vsan.IB.infiniBand(self)
      return ib
      
   
   def fio(self):
      """
      returns fio object
      """
      return FIO(self)
   
   def get_create_partitions(self,devPart,partitions,partType = "soft",modes = "random"):
        
        # partitions should be at least gt than 1
        if int(partitions) < 2:
            raise ViriError("partitions '%s' less thant 2 passed"%partitions)

        devices = []
        
        if partType == "soft":
	    
	    self.parted.create_partitions(devPart,partitions)
            devices = self.parted.get_soft_partitions(devPart)
            
            return devices
        
        ## IF partType is hard,continue..
        #########
        # get /dev/vgca from /dev/vgca0
        
        hard_partitions_allowed = "2"
        
        device = get_vgc_dev_from_part(devPart)
        
        #  devices = ["/dev/vgca0","/dev/vgca1"]
        if partType == "hard":
	  
	  # get supported partitions from vgc-monitor
	  if self.vgcmonitor.get_supported_partions(device) != hard_partitions_allowed:
	      
	      trace_info("card doesnt seem to support '%s' partitions"%hard_partitions_allowed)
              # return 2 , if card doenst support
	      return 2
	  
          # configure using vgcconfig    
          self.vgcconfig.confCard(device,mode = "maxcapacity",n = hard_partitions_allowed)

          # if random
          if modes == "random":
	       
	       # TO DO , using partition 1,should make it 0 or 1
	       partition = "1"
	       devPart1 = device + partition
	       # confPartition(self,devPart,mode)
	       self.vgcconfig.confPartition(devPart1,mode = "maxperformance")
	
	return self.vgcmonitor.getDevicePartition(device)

   def crash(self):
      """
      crash the host 
      called by self.kernel_panic()
      """

      self.run_command_chk_rc('echo 1 > /proc/sys/kernel/sysrq')
      self.run_command_chk_rc('(sleep 15; echo c > /proc/sysrq-trigger) &')

   def clear_var_crash(self):
	trace_info("Clearing /var/crash/*")
	comm = "rm -rfv /var/crash/*"
	self.run_command_chk_rc(comm)

   def kernel_panic(self, clear_logs = 1, clear_crash_dump = 1, power_cycle = 0):
      """
      create kernel panic
      default is not to power cycle the unit, clear /var/crash/*, clear dmesg and syslog
      kdump will power cycle unit after collecting crash_dump
      """

      self.crash()

      trace_info("waiting 30 seconds")
      sys.stdout.flush()
      time.sleep(30)

      self.is_machine_down_successful()

      if power_cycle == 1:
	self.power_cycle()
      else:
	is_hostup(self.name)

      self.logon(check_crash_dir = 0) # needed for paramiko

      if clear_crash_dump == 1:
	self.clear_var_crash()

      if clear_logs == 1:
	self.clear_dmesg_syslogs()

   def get_load_averages(self):
      """
      returns a list of floating point averages from the top command
      [0] is one minute average
      [1] is five minute average
      [2] is fifteen minute average
      """

      comm = self.run_command('top -b -n 1 | grep load | head -n 1 | cut -d: -f 4')
      output = comm['output'][1]

      load_averages = []
      one_minute = output.split(', ')[0]
      five_minute = output.split(', ')[1]
      fifteen_minute = output.split(', ')[2]

      load_averages.append(float(one_minute))
      load_averages.append(float(five_minute))
      load_averages.append(float(fifteen_minute))

      return load_averages
