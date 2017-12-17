#!/usr/bin/python
import pexpect
import sys,time
from Trace import *
U_NAME = "admin"
PASSWD = "virident123"
#PASSWD = "admin"

class RemotePwrBooter:
    
    #def __init__(self,name,logfile_object = None,u_name = U_NAME,passwd = PASSWD):
    def __init__(self,name,logfile_object = sys.stdout,u_name = U_NAME,passwd = PASSWD):

        self.name           = name
        self.logfile        = logfile_object
        self.user           = u_name
        self.passwd         = passwd
      
	self.expectedPrompt = ">\s*$"
        self.connection = None
    def logon(self):

      for password in ['admin','virident123']:
	# Try connecting first
        try:
	    print "Connecting to '%s'"%self.name
            self.connection = pexpect.spawn("telnet %s"%self.name,logfile = self.logfile)
	    
            
        except pexpect.EOF:
            trace_error("Unable to connect to '%s'"%self.name)
            sys.exit(1)

	try:
          self.expectLine("User Name\s+:")
	  self.sendLine(self.user)
	  self.expectLine("Password\s+:")
	  self.sendLine(self.passwd)
	  self.expectLine(self.expectedPrompt)
	  break
        except:
	  trace_info("Seems like some issue with password,retrying...")
	  continue
      else:
	  raise

    def connectionClose(self):
        self.connection.close()

    def sendLine(self,str):
        print "INFO: Sending comamnd '%s'"%str
	self.connection.sendline(str + "\r")
    def expectLine(self,str_arr):
            print "INFO: Waiting for  '%s'"%str_arr
	    try:
               return self.connection.expect(str_arr,10)
	    except pexpect.EOF:
	       trace_error("Timeout happend waiting for '%s'"%str_arr)
	       sys.exit(1)
    def sendExpect(self,str):
        self.sendLine(str)
        #self.expectLine(">\s*$")
        self.expectLine(self.expectedPrompt)
    def enter_port(self,port):
        print "INFO: Entering port '%s'"%port

        self.sendExpect("1")
        self.sendExpect("2")
        self.sendExpect("1")

        self.sendExpect(port)
        self.sendExpect("1")
 
    def run_pwcycle_opt(self,opt):
        print "INFO: Running pw cycle option '%s'"%opt
        self.sendLine(opt)
        self.expectLine("to cancel\s+:\s*")
        self.sendLine("YES")

        # Sometimes it says press Enter to continue
        for l in range(1,3):
            rc = self.expectLine([self.expectedPrompt,"Press"] )
            print "rc = '%s'"%rc
            if int(rc) == 0:
                return 1

            elif int(rc) == 1:
                # press enter
                self.sendLine("")
                continue

            else:
                print "Unknown rc found '%s'"%rc
                print "Did not find > or Press in the output"
                sys.exit(1)

        return 1

    def port_pwcycle(self,port,wait=10):
        self.enter_port(port)

        # option 2 is for off
        self.run_pwcycle_opt("2")
        print "INFO: Waiting '%s' secs"%wait
        time.sleep(wait)
        self.run_pwcycle_opt("1")



 







