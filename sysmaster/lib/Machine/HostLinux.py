#!/usr/bin/python

#from ViriImports import *
from Errors import syslogErrors
import paramiko
from Host import Host
from Host import CommandError
from Trace import *
import re
from Util import *
#from Util import *
import commands

"""
import paramiko,sys
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(
    paramiko.AutoAddPolicy())
ssh.connect('sqa11', username="root", password= "0011231")
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(sys.argv[1])
#print ssh_stdin
print ssh_stdout.readlines()
print ssh_stderr.readlines()
exit_status = ssh_stdout.channel.recv_exit_status()
print exit_status
"""

#WINEXE="/home/bandeepd/windows/scanman/source/bin/winexe"
U_NAME = "root"
PASSWD = "0011231"
#PASSWD = "$viri123"

class ConnectionError(Exception):
      pass

class hostLinux(Host):
    
    def __init__(self,name,u_name = U_NAME,passwd = PASSWD,logon = 1):
	
	Host.__init__(self,name)

        self.name           = name
        self.user           = u_name
        self.passwd         = passwd
        self.ssh            = ""
        
	if logon == 1:
	    
            self.logon()

    def logon(self, check_crash_dir = 1, check_kdump = 1):
        
	#return 1
	
	trace_info("Logging on to '%s'"%self.name)
        ssh = paramiko.SSHClient()
	#print "Setting missing paramiki keys"
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

	#if not if_ping_successful(self.name):
        #    trace_info("Unable to connect to '%s'"%self.name)
	#    raise ConnectionError("Unable to connnect %s"%self.name)

        
        
        retry_count = 25 # count changed to 25
	for c in range(1,retry_count):
	   try:
	      #print "Connecting to host"
              ssh.connect(self.name, username= self.user, password= self.passwd,timeout = "10")
	      break
              
	   except:
	      sleep_time(10,"after unable to connect to machine %s,retries '%i'"%(self.name,c))
	      continue
        else:
	
	    raise ConnectionError("Unable to ssh to '%s'"%self.name)

	
        # Initialize ssh
        self.ssh = ssh
	#self.connection = self.ssh # hack to do
        
        # Uncomment this

	if check_kdump == 1:
	    self.is_kdump_operational()

	if check_crash_dir == 1:
	    self.is_crash_dir_empty()

	self.set_panic_softlockup()

    def is_kdump_operational(self):
        self.set_panic_softlockup()
    
	trace_info("checking if kdump is running")
	comm = "service kdump status"
	try:
		kdump_status = self.run_command(comm)
		print kdump_status
		if 'operational' not in kdump_status['output'][1]:
		    active = 0
		    for l in kdump_status['output']:
			if 'Active: active' in l:
				active = 1
			if 'Active: activating' in l:
				active = 1
			if 'Active: inactive' in l:
				active = 0
		    if active == 0:
			raise ViriError("kdump service is not running")
		trace_success("kdump is operational")
	except:
		try:
			comm = "service boot.kdump status"
			kdump_status = self.run_command(comm)
			print kdump_status
			if 'running' not in kdump_status['output'][1]:
				trace_error("kdump is not running on sles")
			else:
				trace_success("kdump service is running on sles")
		except:
			comm = "kdump-config status"
			kdump_status = self.run_command(comm)
			print kdump_status
			if 'ready to kdump' not in kdump_status['output'][1]:
				trace_error("kdump is not running on ubuntu")
			else:
				trace_success("kdump service is running on ubuntu")
			
    
    def run_command(self,command,timeout = None,bg = False,bgFile = None ):
	
	if not self.ssh:
            self.logon()

        found_bg = 0
        if re.search("(.*)&$",command):

          found_bg = 1
          m = re.search("(.*)&$",command)
          command = m.group(1)
          #command = command + ' > /dev/null 2>&1 &'
        if bg:
          if found_bg == 1:
              raise ViriError("bg is set but & at the end of the command '%s' also passed")
	  # set the variable if bg is set
	  found_bg = 1

	if found_bg == 1: 
	  # check if bg file is passed
	  if bgFile:
           command = command + ' >%s&'%bgFile
	  else:
           command = command + ' > /dev/null 2>&1 &'

        trace_info("Linux: %s : Running command '%s'"%(self.name,command))
        
        t1 = get_epoch_time()
 
        try:
         stdin, stdout,stderr = self.ssh.exec_command(command)
	
	# Control C did not work TO DO!
	except KeyboardInterrupt:
	    self.ssh.close()
	    sys.exit(1)
        
        output = stdout.readlines()
        
        # print on screen 
        #print stdout.read()
	#print stdin.read()
        
        #print stdterr.read()
	
        # remove \n from array
        output = [ l.strip() for l in output]
        
        # TO DO , hack with pexpect commmand used to get added, so adding this
        output.insert(0,command)
        
        rc = stdout.channel.recv_exit_status()
      
        rc = int(rc)

        tTaken = get_epoch_time() - t1
  
        out = {'outputerr': stderr.readlines(),
               'output'    : output,
	       'time'      : tTaken,
               'rc'        : rc}
        
        #print out['output']     
        return out
    
    def reboot(self):
	
	self.run_command_chk_rc("reboot")
	self.ssh.close()
	self.ssh            = ""
	self.is_machine_down_successful()
	is_hostup(self.name)
	
    def run_command_chk_rc(self,command,verbose = 0, timeout = None):
       """ """
       # need another method here and not using from pararent class, outputerr is given 
       # which is different
       o = self.run_command(command)
       rc = o['rc']
       out = o['output']

       if rc != 0:
           err = "Couldn't run the command '%s', found return code as '%i'"%(command,rc)
           trace_error(err)

           print "details = ("
           for l in out:
               print l
           print ")"
           
           out = o['outputerr']
           out.insert(0,err)
           

           raise CommandError(out)

       if verbose:
         printOutput(out)
       
       return o
    def vgc_sec_er(self,device,option):
       if option != "purge" and option != "clear" and option != "verbose" and option != "default":
           print "ERR: Please pass option as purge /clear /default/verbose"
           sys.exit(1)
       #vgcSecErPath= "/usr/lib/virident/vgc-secure-erase"
       vgcSecErPath= "vgc-secure-erase"
       comm = "%s --%s --yes %s"%(vgcSecErPath,option,device)
       trace_info("Running vgc secure erase command '%s'"%comm)

       t1 = get_epoch_time()

       if option == "default":
          comm = "%s %s --yes"%(vgcSecErPath,device)
       t2 = get_epoch_time()
       tDiff = t2 - t1

       o = self.run_command_chk_rc(comm)

       for l in o['output']:
           print l

       trace_info("Time took to run secure erase '%i' secs"%tDiff)

       return 1
       


