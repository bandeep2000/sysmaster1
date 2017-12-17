import DB
from Util import *
from Rpb import *
"""

#!/usr/bin/python
import sys
from RebootMachine import *

r = Reboot()
r.ipmi_powercycle(sys.argv[1])
r.rpb_powercycle(sys.argv[1])
sys.exit(1)

"""
class Reboot:
    
    def ipmi_powercycle(self,mname):
        
        db = DB.viriDB()
        ip_addr,u_name,passwd = db.getIPMI(mname)
        
        pw_cmd = "off"
        run_ipmi_lan_pw_command(ip_addr,pw_cmd,u_name,passwd)
        print "Waiting 130 sec"
        time.sleep(10)
        pw_cmd = "on"
        run_ipmi_lan_pw_command(ip_addr,pw_cmd,u_name,passwd)
        
    def rpb_powercycle(self,mname):
         
        db = DB.viriDB()
        print db.getRpb(mname)
        #rpb,port = db.getRpb(mname)
        sys.exit(1)
        r = RemotePwrBooter(rpb)
        r.logon()
        r.port_pwcycle(port)
        r.connectionClose()