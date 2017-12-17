#!/usr/bin/python
import os,sys,re,time
import pexpect
from Trace import *
from Host import Host
from Parsers import *
#from IOS import *
from Trace import *
#from UtilWindows import *
#from VirExceptions import *
#from Errors import syslogErrors

from Variables import *
#from VgcProc import *

#from Host import *

import commands

""" 
from Machine.HostWindows import *
h = hostWindows("sqa12-windows")
h.run_command("vgc-monitor")

"""

WINEXE="/home/bandeepd/sqa/scripts/systemqa/lib/Machine/winexe"


U_NAME = "administrator"
PASSWD = "$viri123"


class hostWindows(Host):
    
    def __init__(self,name,logfile_object = sys.stdout,u_name = U_NAME,passwd = PASSWD):

        Host.__init__(self,name)
        self.name           = name
        self.logfile        = logfile_object
        self.user           = u_name
        self.passwd         = passwd
    
    def run_command(self,command):
        
        
        """
        commands.getstatusoutput("source/bin/winexe -U administrator --password source/bin/winexe -U administrator --password '$viri123' //broken2 'vgc-monitor -d vgca'")


        """
        trace_info("Win: Running command '%s'"%command)
        
        t1 = get_epoch_time()
	
	
        cmd = "%s -U %s --password '%s' //%s '%s'  "%(WINEXE,self.user,self.passwd,self.name,command)

        print cmd
        
        
        rc,output_a =  commands.getstatusoutput(cmd)
        
        output_a = output_a.split("\r\n")
        
        #print "ouput =",output_a
        
        #for l in output_a:
            #print "l=", l
        
        
        #sys.exit(1)
        rc = int(rc)
        #print cmd
        
        tTaken = get_epoch_time() - t1
        output = ""
        #sys.exit(1)
        out = {'output_str': output,
               'output'    : output_a,
	       'time'      : tTaken,
               'rc'        : rc}
        
        #print out['output']     
        return out
    
    def run_command_chk_rc(self,command):
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
           out.insert(0,err)
           raise CommandError(out)

       return o

    def cat_etc_issue(self):
       return "windows"

    def get_kernel_ver(self):
       return "winKernel"

    def getCPUs(self):
       return "N/A"
    def getCPUModel(self):

       return "N/A"

    def print_syslogs(self):
        trace_info("Function deoesnt work for windows")
        return 1

    def get_dmesg(self):
        trace_info("Function deoesnt work for windows")
        return 1

    def clear_dmesg_syslogs(self):
       trace_info( "Not clearing dmesg since it is windows")
       return 1

