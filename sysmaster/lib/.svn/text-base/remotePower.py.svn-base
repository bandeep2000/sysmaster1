#!/usr/bin/python
from rpbDetails import rpbInfo
from Rpb import *
from Util import *
import sys

host = sys.argv[1]
rpb = rpbInfo[host]['rpb']
rpbPort = rpbInfo[host]['port']


#sqa12 pwr29 4

# pwr 28 port 7 -sqa05
def rpb_power_cycle(rpb,port):
   r = RemotePwrBooter(rpb)
   r.logon()
   r.port_pwcycle(port)
   r.connectionClose()

rpb_power_cycle(rpb,rpbPort)





