 #!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
from Specs import *
from VirExceptions import *
from VgcUtils import *
VSAN_ENABLED = "enabled"
VSAN_DISABLED = "disabled"

"""
from VgcCfg import *
vgcConfig = vgcConf(self.host)

details = vgcConfig.getDevicesDetails("-d %s"%device)

"""

# default sector
EXPECTED_SECTOR = "512"

class vgcConf(vgcUtils):
	
    def __init__(self,host):
	self.vgcConfStr = "vgc-config" # vgc-config command string
        vgcUtils.__init__(self,host)
	
    def getDevicesDetails(self,options = None):
        
        """ options is -d /dev/vgca """
	cmd = self.vgcConfStr
	if options:
		cmd = cmd +  " " + options
	# uncommented checking the validation of the command
        #o = self.host.run_command_chk_rc(cmd)
        o = self.host.run_command(cmd)
	output = o['output']
	return parse_vgc_config(output)
        
    def getAllCards(self):
        """return all the card in the system as array, eg. ['/dev/vgcb', '/dev/vgca']  """
	pout = self.getDevicesDetails()
        return pout.keys()
   
    def getPartitonDetails(self,devPart):
	    cmd = "%s -p %s"%(self.vgcConfStr,devPart)
	    o = self.host.run_command_chk_rc(cmd)
	    output = o['output']
	    
	    output = output[1:]
	    
	    (devPartFound,mode,sector,raid)= parse_vgc_config_partition(output)
	     
	    return (mode,sector,raid)
    
    def getCardNumPartitions(self,device):
	device = remove_dev(device)
	return self.getDevicesDetails()[device]['partitionNum']
    
    def resetCard(self,device):
	    
	    cmd = "%s -d %s -r  -f"%(self.vgcConfStr,device)
	    o = self.host.run_command_chk_rc(cmd)

	    self.verifyDefaultPartition(device)
	    
	    #return o

    def confCard(self,device,mode,n):
	    
	    cmd = "%s -d %s -m %s -n %s -f"%(self.vgcConfStr,device,mode,n)
	    o = self.host.run_command_chk_rc(cmd)

	    #forLoop = int(n) + 1 
	    forLoop = int(n)
	    for p in range(0,forLoop):
		    p = str(p)
		    #print "p = %s"%p
		    devPart = device + p
		    self.verifyPatition(devPart,mode)
	    return o
    def getDefaultSpecs(self,device):
	    
	    cardType = self.host.vgcmonitor.getCardType(device)

	    default = specsCard[cardType]['default']
            
            raid = default['raid']
            
            mode = default['mode']

            # default key enabledmaxcapacity for disabled maxcapcity
            key = raid + mode
            ucap = specsCard[cardType]['ucap'][key]
	    
	    return (ucap,default['raid'],default['mode'],default['sector'])
	    
    def getCardUsableCapSpecs(self,devPart,mode,raidKey = "enabled"):
	    """takes device as partition,number of partitions """
	    # get card partitions
	    # get /dev/vgca from /dev/vgca0 
	    device = get_vgc_dev_from_part(devPart)
	    # get number of partitions
	    # this will be used to generate key from specs file
	    cardPartitions = self.getCardNumPartitions(device)
	    specsKey = raidKey + mode 
	    
	    # if card has more that 1 partion, specs dictionary has key with no of partitions
	    # example 'enabledmaxpeformance2'
	    if int(cardPartitions) > 1:
		    # append partitions this will given to specs file
		    specsKey = specsKey + cardPartitions
	    
	    # get card type this will give 2.2TB, as example
	    # spec dictionary uses this
	    cardType = self.host.vgcmonitor.getCardType(device)
	    
	    return specsCard[cardType]['ucap'][specsKey]
	    
    def _compareParameter(self,found,expected,paramDetails,Details = " "):
	    
	    string = "Expected parameter '%s' expected '%s', found '%s'"%(paramDetails,expected,found)
	    
	    if found != expected:
		    
		    print Details
                    
                    raise ViriError(string)
            
		    sys.exit(1)
	    trace_info(string)
	    return 1
    
    def verifyDefaultPartition(self,device):

	    
	    devPart = device + "0" # 0 is default partition
	    (expectedUcap,expectedRaid,expectedMode,expectedSector) = self.getDefaultSpecs(device)
	    
	    (foundMode,foundSector,foundRaid) = self.getPartitonDetails(devPart)
	    
	    self._compareParameter(foundRaid,expectedRaid,"raid")
	    self._compareParameter(foundMode,expectedMode,"mode")
	    self._compareParameter(foundSector,expectedSector,"sector")
	    
	    foundUcap = self.host.vgcmonitor.getCardPartUcap(devPart)

	    self._compareParameter(foundUcap,expectedUcap,"user capacity")
	    
	    return 1
    	    
    def verifyPatition(self,devPart,mode):

            device = get_device_part(devPart)
	    expectedRaid = self.getDefaultSpecs(device)[1]
	    expectedSector = EXPECTED_SECTOR
	    expectedMode = mode
	    
	    (foundMode,foundSector,foundRaid) = self.getPartitonDetails(devPart)
	    
	    self._compareParameter(foundRaid,expectedRaid,"raid")
	    self._compareParameter(foundMode,expectedMode,"mode")
	    self._compareParameter(foundSector,expectedSector,"sector")
	    
	    vm = self.host.vgcmonitor
	    foundUcap = vm.getCardPartUcap(devPart)
	    
	    expectedUcap = self.getCardUsableCapSpecs(devPart,mode,expectedRaid)
	    
	    self._compareParameter(foundUcap,expectedUcap,"user capacity")
	    
	    return 1
    
    def getCardType(self,device):
	    return self.host.vgcmonitor.getCardType(device)

    def confPartition(self,devPart,mode):
	    """ configure card with -p"""

	    #return 1 # delete this
            device = get_device_part(devPart)
	    expectedRaid = self.getDefaultSpecs(device)[1]	    

	    #expectedRaid = "enabled"
	    expectedSector = EXPECTED_SECTOR
	    expectedMode = mode
	    
	    cmd = "%s -p %s -m %s -f"%(self.vgcConfStr,devPart,mode)
	    o = self.host.run_command_chk_rc(cmd)
	    
	    (foundMode,foundSector,foundRaid) = self.getPartitonDetails(devPart)
	    
	    self._compareParameter(foundRaid,expectedRaid,"raid",cmd)
	    self._compareParameter(foundMode,expectedMode,"mode",cmd)
	    self._compareParameter(foundSector,expectedSector,"sector",cmd)

	    foundUcap = self.host.vgcmonitor.getCardPartUcap(devPart)
	    
	    expectedUcap = self.getCardUsableCapSpecs(devPart,mode,expectedRaid)
	    
	    self._compareParameter(foundUcap,expectedUcap,"user capacity",cmd)
	    
	    return o


    def is_vsan_feature_enabled(self,devPart,vsanFeature) :
                o = self.host.run_command_chk_rc("%s -p %s"%(self.vgcConfStr,devPart))
                
		output = o['output']
                status = ""
		for l in output:
		  if re.search(r'%s=(\w+)'%vsanFeature, l, re.M|re.I):
	             matchobj=re.search(r'%s=(\w+)'%vsanFeature,l, re.M|re.I)
		     status =  matchobj.group(1)
                
		if status == "":
		   raise ViriError("couldn't find if vsan is enabled or disabled from output '%s'"%output)
		
		if status == VSAN_DISABLED:
		    trace_info("vsan feature %s is disbled "%vsanFeature)
		    return False
		elif status == VSAN_ENABLED:
		    trace_info("vsan feature %s is enabled "%vsanFeature)
		    return True
		
		else:
		    raise ViriError("Vsan Unknown status found '%s'"%status)
		
    def enable_vsan_feature(self,devPart,vsanFeature,mode = ""):    
	    """ where mode is maxperformance or maxpcapacity,
	     e.g h.vgcconfig.enable_vsan_feature("/dev/vgca0","vcache") """
	    if mode:
		 self.host.run_command_chk_rc("%s -p %s --enable-%s -f -m %s"%(self.vgcConfStr,devPart,vsanFeature,mode))
	    else:
                 self.host.run_command_chk_rc("%s -p %s --enable-%s -f"%(self.vgcConfStr,devPart,vsanFeature))
	    
	    if not self.is_vsan_feature_enabled(devPart,vsanFeature):
		raise ViriError("Could not enable vsan feature %s"%vsanFeature)
		
	    return 1
	
    def disable_vsan(self,devPart):
	"""h.vgcconfig.disable_vsan("/dev/vgca0")"""
	
	# TO DO add force option, with delete all
	self.host.run_command_chk_rc("%s -p %s -r -f "%(self.vgcConfStr,devPart))
	
	return 1
	
    
    
