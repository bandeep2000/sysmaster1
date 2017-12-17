#!/usr/bin/python
from Machine.Host import Host
from VgcUtils import *

#from Tests1 import *
#from IOS import *
from ViriImports import *
import sys
from Trace import *
from VirExceptions import *

import time

server = "sysmaster"
diskcheckerFile = "diskchecker-raw.pl"
serverDiskCheckerPath = "/root/megastress/%s"%diskcheckerFile
diskcheckerDownloadPath = " http://spica.virident.info/sqa/tools/%s"%diskcheckerFile


def isDiskCheckerRunningServer(h,port):
    """ checks to see if diskchecker is running on server, takes server object and port as input"""
    cmdIfRunning = "ps -eaf | grep \"diskchecker-ra[w].pl -l %s\""%port
    
    o  = h.run_command(cmdIfRunning)
    rc = o['rc']
    
    if rc == 0:
        return True
    return False

def isDiskCheckerRunningClient(client):
    
    """takes client object returns True if diskchecker process is running,false otherwise """
    cmdIfRunning = "ps -eaf | grep \"diskchecker-ra[w].pl\""
    
    o  = client.run_command(cmdIfRunning)
    rc = o['rc']
    
    if rc == 0:
        return True
    return False

def parsePid(out):
    
    for l in out:
    
        if re.search("root\s+(\d+).*",l):
            m = re.search("root\s+(\d+).*",l)
            pid = m.group(1)
            return pid
    
    else:
        return ""
        
def getDiskcheckerPidServer(h,port):
    cmdIfRunning = "ps -eaf | grep \"diskchecker-ra[w].pl -l %s\""%port
    
    o  = h.run_command(cmdIfRunning)
    rc = o['rc']
    out = o['output']
    
    return parsePid(out)

def getDiskcheckerPidClient(client):
    cmdIfRunning = "ps -eaf | grep \"diskchecker-ra[w].pl\""
    
    o  = client.run_command_chk_rc(cmdIfRunning)
    rc = o['rc']
    out = o['output']
    
    return parsePid(out)
    
def killDiskcheckerProcessClient(client):
    pid = getDiskcheckerPidClient(client)
    client.run_command_chk_rc("kill -9 %s"%pid)

def diskcheckerCreateClient(client,server,port,drive,size,blkSize):
    """takes client object server NAME(not object), port,drive as /dev/vgca0,size of drive to be used
    block size as input, starts the diskchecker client with create """
    #./diskchecker-raw.pl -s spica:1000002 create /dev/vgca0 8192 8192
    
    if size == int(0) or blkSize == int(0):
        raise DiskCheckerError("disk size '%s' or bs '%s' passed as 0"%(size,blkSize))
    
    #chkifVgcDevPart(drive)
    # create command and run in background
    cmd = "./%s -s %s:%s create %s %s %s&"%(diskcheckerFile,server,port,drive,size,blkSize)
    trace_info("Running command '%s'"%cmd)
    client.run_command(cmd)
    
    if isDiskCheckerRunningClient(client):
        return 1
    
    raise DiskCheckerError("diskchecker is not running on client")
    sys.exit(1)
   
def downloadDiskchecker(client):
 
    if not client.if_file_exists(diskcheckerFile):
          trace_info("Downloading diskchecker")
          client.wget_file(diskcheckerDownloadPath)
    
    client.run_command_chk_rc("chmod +x %s"%diskcheckerFile)
    
    return 1

def diskcheckerVerifyClient(client,server,port,drive,size,blkSize):
    #./diskchecker-raw.pl -s spica:1000002 create /dev/vgca0 8192 8192
    
    if size == int(0) or blkSize == int(0):
        raise DiskCheckerError("disk size '%s' or bs '%s' passed as 0"%(size,blkSize))
        
    #chkifVgcDevPart(drive)
    cmd = "./%s -s %s:%s verify %s %s %s"%(diskcheckerFile,server,port,drive,size,blkSize)
    #print cmd
    #sys.exit(1)
    o = client.run_command_chk_rc(cmd)

    out = o['output']

    StrSuccessRegex = "Total\s+errors:\s*0"
    found_sucess_str = 0
    print "("
    for l in out:
        print l
        if re.search(StrSuccessRegex,l):
            trace_info("Success string found in the output")
            found_sucess_str = 1
            
    print ")"
    
    if found_sucess_str == 0:
        raise DiskCheckerError("Did not find success string '%s' in diskchecker verify step for drive '%s' "%(StrSuccessRegex,drive))
    return 1
    
def startDiskcheckerServer(h,port):
    """takes server object and port as input,starst diskchecker on server """
    
    if isDiskCheckerRunningServer(h,port):
        trace_info("Seems like diskchecker is already running on port '%s'"%port)
        return 1
    trace_info("Seems like diskchecker is not already running on port %s, starting..."%port)
    cmd = "nohup %s -l %s > /dev/null&"%(serverDiskCheckerPath,port)
    h.run_command(cmd)
    
    if isDiskCheckerRunningServer(h,port):
        return 1
    
    raise DiskCheckerError ("Couldn't start diskchecker on server '%s'port '%s'"%(h.name,port))
    sys.exit(1)

def getServer(server = "sysmaster"):
    
    """returns server object"""
    s = Host(server,logfile_object = None)
    s.logon()
    return s


def runDiskChecker(dict1):
    
    """
    Take dictionary as argument
    
    example usage:
    
    dict1 = {'hostObj': h,'devPart': '/dev/vgca0', 'loops': 1}
    runDiskChecker(dict1)
    
    inputs:
    devPart: device as example /dev/vgca0
    loops : how many time to run
    diskSize : diskSize in MB, defaults 8192 MB
    
    descripition: runs diskchecker blocksize 512 to 8K , power cycles machine
     
    
    """
    
    # TO DO Make array of blkSize as function parameter
    hostObj  = dict1['hostObj']
    devPart  = dict1['devPart']
    loops    = int(dict1['loops']) # make integer in cases passed as string
    # Default Disk size 8192 MB
    diskSize = dict1.get("diskSize", "8192")
    
    port="1000000004"
 
    s = create_host(server)  # TO DO make server capital
    s.logon()
    startDiskcheckerServer(s,port)
    
    size = diskSize # size in 
    cl = hostObj # TO DO change it, since the code was copied
    
    downloadDiskchecker(cl)
    
    WAIT = 60 # after power cycling
    for c in range(0,loops):
        # PLEASE CHANGE it back!!!!!!!
        # !!!!!
        #for blkSize in range(512,8192,512):
        for blkSize in range(512,1024,512):
            trace_info_dashed("Using blksize '%s'"%blkSize)
            diskcheckerCreateClient(cl,server,port,drive = devPart,size = size,blkSize = blkSize)
            sleep_time(WAIT,"after create file step on client")
            cl.power_cycle()
            diskcheckerVerifyClient(cl,server,port,drive = devPart,size = size ,blkSize = blkSize)

    return 1
    
    
    
    
    
"""

Example Usage:
from ViriImports import *
from Diskchecker import *
s = Host("spica",logfile_object = None)
s.logon()
cl = Host(sys.argv[1],logfile_object = None)
cl.logon()
downloadDiskchecker(cl)

port="1000000004"
startDiskcheckerServer(s,port)
drive="/dev/vgcb0_wb"

blkSize = "8192"
size = "8192"

for blkSize in range(512,8192,512):
    blkSize = str(blkSize)
    print " "
    trace_info_dashed("Using blksize '%s'"%blkSize)
    diskcheckerCreateClient(cl,server,port,drive = drive,size = size,blkSize = blkSize)
    sleep_time(60,"after create file step on client")
    #killDiskcheckerProcessClient(cl)
    cl.power_cycle()
    diskcheckerVerifyClient(cl,server,port,drive = drive,size = size ,blkSize = blkSize)



"""

    


