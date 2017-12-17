#!/usr/bin/python
#import sys
#import  time
#from Parsers import *
#from Trace import *
#from Util import *
#from Specs import *
#from Variables import *
#from VgcProc import *
#from VirExceptions import *
from Machine.Host import *
#from FileSystems import *
from ViriImports import *
#from Util import *

"""

Example Usage:
h = Host(sys.argv[1])
h.logon()
e = errorSim(h)
e.simulateErrors("/dev/vgca0","0","1","read")


"""

class errorSim:
	
    def __init__(self,host):
        self.host = host
        
        if not self.host.ifVgcRpmLoaded("stats"):
           raise ViriError("Stat rpm not loaded for error simulation")
           sys.exit(1)
           
        if not self.host.ifVgcRpmLoaded("tools"):
           raise ViriError("tools rpm not loaded for  error simulation")
           sys.exit(1)
    def simulateErrors(self,devPart,duNo,subChNo,op,runIO = False,dpp = None):
        
        """takes du no, subChannel as inputs
        
        for example in the following output 
        "z00du00(DB-SL-MSL-CH-SCH) : 00-00-0-0-0 01-01-0-0-0 04-04-2-0-0 ..."
        duNo is 0 and subchannel 0 is 00-00-0-0-0 and 1 is 01-01-0-0-0
        
        So command to simulate errors on du0 and subchanel 0 will be 
        eObject.simulateErrors("/dev/vgca0","0","1","read")
        """
        chkifVgcDevPart(devPart)
        
        if runIO:
          self.runWriteIO(devPart)
        
        drvLetter,part = get_device_letter_part(devPart)
        
        vgproc = vgcProc(self.host)
        (slmask,chmask,schmask) = vgproc.getSlChSubChMask(devPart,duNo,subChNo)
        
        trace_info("Found slmask chmask subchmask as '%s' '%s' '%s' for du '%s' sbch '%s' "%(slmask,chmask,schmask,duNo,subChNo))
        
        """sim_perr --gw $drvLetter --zone 0 --req add_psim --op read --slmask 0x2 --chmask 0x8 --schmask 0x4 --prob 1 --extra_info 0 --no_per_sec   - simulates read failures on the various slice,channel and subchannle masks """
        cmd = "%s --gw %s --zone %s --req add_psim --op %s "%(SIM_PERR,drvLetter,part,op)
        
        cmd = cmd + " --slmask %s --chmask %s --schmask %s --prob 1"%(slmask,chmask,schmask)
        
        if not dpp:
           cmd = cmd + " --extra_info 0 --no_per_sec"
        else:
           
           if dpp != "cmed" and dpp !="cmec":
               raise ViriError("dpp valued not passed as cmed or cmec, passed as '%s'"%dpp) 
           cmd = cmd + " --no_per_sec" + " --%s"%dpp
        
        self.host.run_command_chk_rc(cmd)
        
        if runIO:
          self.runReadIO(devPart)
          
        return 1
        
    def runWriteIO(self,devPart):
        
        chkifVgcDevPart(devPart)
        io = DD(self.host)
        io.runWriteIO(devPart)
        return 1
    
    def runReadIO(self,devPart):
        
        chkifVgcDevPart(devPart)
        io = DD(self.host)
        io.runReadIO(devPart)
        return 1
    
    def simulateSubChFailure(self,devPart,duNo,subChNo, runIO = False ):

        #self.host.run_command_check_rc("dd if=/dev/zero of=
        
        chkifVgcDevPart(devPart)
        if runIO:
           self.runWriteIO(devPart)
        
        drvLetter,part = get_device_letter_part(devPart)
        
        #vgproc = vgcProc(self.host)
        vgproc = self.host.vgcproc
        (sl,ch,sch) = vgproc.getSlChSubCh(devPart,duNo,subChNo)
        
        trace_info("Found sl ch subch as '%s' '%s' '%s' for du '%s' sbch '%s' "%(sl,ch,sch,duNo,subChNo))
        
        #echo "1,1,1" | vgcproc -w /proc/driver/virident/bba/sim_bad_schans
        
        cmd = "echo \"%s, %s, %s\" | %s -w /proc/driver/virident/b2mua/sim_bad_schans"%(sl,ch,sch,VGCPROC)
        
        self.host.run_command_chk_rc(cmd)
        
        if runIO:
           self.runReadIO(devPart)
        return 1
    
    def get_fdparm_state(self,devPart):
        chkifVgcDevPart(devPart)
        
        o = self.host.run_command_chk_rc("/usr/lib/vgc/fdparm --show %s"%devPart)
        
        output = o['output']
        
        dict = parse_fdparm_output(output)
        
        return dict['State']
        
        
    
    def get_device_attr(self,device,verbose = 1):
        
        """('Good', 'Normal', 'None', 'READY', '99.94%') """
        vm = vgcMonitor(self.host)
        
        dict = vm.getDeviceDetails(device,verbose)
        
        ####################################
        #### PLEASE NOTE assumption is partion 0
        # TO DO partition 1
        ##############################
        devPart = device + "0"
        
        cardState       = dict['state']
        actionRequired   = dict['actionRequired']
        cardStateDetails = dict['cardStateDetails']
        flashReserveLeft = dict['part'][devPart]['flashReserveLeft']
        partState        = dict['part'][devPart]['partState']
        rlife        = dict['part'][devPart]['life']
        
        return (cardState,cardStateDetails,actionRequired,partState,flashReserveLeft,rlife)
        
    
    def cleanUp(self,device):
        
        self.host.ifVgcRpmLoaded("tools")
        vconf = vgcConf(self.host)
        drvLetter = get_device_letter(device)
        
        o = self.host.run_command_chk_rc("cat /sys/module/vgcmgmt/parameters/ro")
        
        out = o['output']
        print out
        
        self.host.run_command_chk_rc("rmmod vgcmgmt")
        self.host.run_command_chk_rc("modprobe -v vgcmgmt ro=0")
        cmd = "cat /sys/module/vgcmgmt/parameters/ro"
        o = self.host.run_command_chk_rc(cmd)
        
        out = o['output']
        output = out[1]
        if output != "0":
            trace_info("Found output of command '%s' not 0 but %s"%(cmd,output))
            sys.exit(1)
        try:
           self.host.run_command("clr_dyn_bb /dev/vgcmgmt%s-bb"%drvLetter)
        except:
           trace_info("Bandeep hack, this command doesnt seem to return interger code")

        vconf.resetCard(device)
        
        return 1
        
        
        
        
        
        
        
        
        
        
        
