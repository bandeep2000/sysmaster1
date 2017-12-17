import os
import sys
import time
import re
import ConfigParser
from Trace import *
#from VirExceptions import *
from Variables import *
from Util import *
import Machine.HostLinux 
import Machine.HostWindows 
from Parsers import *
from VgcUtils import *
from FileSystems import *
from Errors import syslogErrors
from Specs import *
from Cards import *
from VMware import *

#from VgcUtils.Vsan.Vshare import *

def create_host(host,logon =1 ):
   h = Machine.HostLinux.hostLinux(host,logon = logon)
   return h
def create_host_windows(host ):
   h = Machine.HostWindows.hostWindows(host)
   return h

def create_host_serial(host,logon = 1 ):
   import Machine.Host
   h = Machine.Host.Host(host)
   return h

        

