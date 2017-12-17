 #!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
from Specs import *
from VgcUtils import *
#from VirExceptions import *

""""
Example Script

#!/usr/bin/python
from Host import Host
from VgcMon import *
from Temperature import *
import sys

h = Host(sys.argv[1])
h.logon()

vm = vgcMonitor(h)
print vm.getDevStatus("/dev/vgca0")

# TO DO
# This has to modified to to have function through which devPart
"""
class vgcMonitor(vgcUtils):
	
    def __init__(self,host):
	self.vgcMonStr = "vgc-monitor" # vgc-config command string
        vgcUtils.__init__(self,host)
	
    def getDevicesDetails(self,options = None,verbose = 1 ):
	cmd = self.vgcMonStr
	if options:
		cmd = cmd +  " " + options

	i = 0
	while i < 60:
        	o = self.host.run_command(cmd)
		output = o['output']

		if verbose:
		   printOutput(output)

		if o['rc'] != 0:
			trace_info('retrying in case resource is unavailable')
			i = i + 1
			time.sleep(10)
			continue
		else:
			break
           
	return parse_vgc_monitor(output)
    
   
    def getDeviceDetails(self,device,verbose = 1):
	    """ return as {'temp': '58', '/dev/vgca': {}, 'pcigen': 'Gen2', 'rtl': '43095', 'state': 'GOOD', 'part': {'/dev/vgca0': {'life': '99.29', 'raid': 'enabled', 'read': '234036849160704', 'read_tb': '234.04TB', 'ucap': '2222', 'rcap': '3072', 'write': '381159326875144', 'state': 'GOOD', 'degraidgrps': 'none', 'raidgrps': '24', 'mode': 'maxcapacity', 'write_tb': '381.16TB', 'spareLeft': '14', 'mfailureraidgrps': 'none'}}, 'card_info': 'VIR-M2-LP-2200-2A, 3072 GiB', 'build': '3.0(44758.trunk)', 'd_uptime': '23:46', 'pcilanes': 'x8', 'serial': 'V1312B00018', 'temp_s': 'Safe'}
            
            raises if device is not present
 """        
            chkifVgcDevWithoutPart(device)
	    #device = remove_dev(device)
    	    dict = self.getDevicesDetails(options = " -d %s"%device, verbose = verbose)
            
            # check if device is present
	    device = remove_dev(device)
            #if not dict.has_key(device):
            #    print dict
            #    raise ViriError("Device '%s' doesnt seem to be present in the vgc-monitor output"%device)
            return dict
    
    
    def getDevicePartition(self,device):
	
	device = remove_dev(device)
	# returns hard partitions on device,array [/dev/vgca0,/dev/vgca1]
	devices =  self.getDeviceDetails(device)['part'].keys()
	
	# add /dev in 3.2
	devices = [ '/dev/' + dev for dev in devices]
	return devices
	
    def getDeviceAttribute(self,device,attrib):
        
        """ returns attribute of device not partition"""
        
        return self.getDeviceDetails(device)[attrib]
        
    def getDeviceStatus(self,device):
        
        """ returns the state of the card , not  the partition"""
        
        parsedOut = self.getDeviceDetails(device)
        
        #print parsedOut
        
        return parsedOut['state']
    

    def get_gbb(self,devPart ):

	i = 0
	while i < 60:
		try:
			output = self.host.run_command_get_output("vgc-monitor -d %s -e"%devPart)
			break
		except:
			i = i + 1
			time.sleep(10)
			continue

	printOutput(output)
	
	gbb = parseSplit(output,add_underscore = 1)['grown_bad_blocks']
	
	# above will return 124 (0.02%)
	# TO DO, it will return 124 only and not percentage
	# TO DO, should check if it is integer
	return gbb.split()[0]

    def _get_part_attrib_parsed_out(self,parsedOut,devPart,attrib):
	
	#if self.is_C7_build():
	devPart = remove_dev(devPart)
	return parsedOut['part'][devPart][attrib]
	
    def getDevStatus(self,devPart,verbose = 0):
        """return device partition and device status"""
        
        chkifVgcDevPart(devPart)
        
        device = get_vgc_dev_from_part(devPart)
        
	print device
	
        parsedOut = self.getDeviceDetails(device)
        
        #print parsedOut
        devState = parsedOut['state']
	
	
	devPartState = self._get_part_attrib_parsed_out(parsedOut,devPart,'state')
	
        return devState,devPartState
    
    def getCardInfo(self,device):
	    return self.getDeviceDetails(device)['card_info']
    def getCardSerial(self,device):
            try:
	        return self.getDeviceDetails(device)['serial']
            except KeyError:
                #print "("
                #print self.getDeviceDetails(device)
                #print ")"
                #raise IndexError("serial number not found for device '%s'"%device)
		return 'unknown'
    
    
    def _prepend_dev_array(self,array):
	
	# prepends dev string to array
	
	return [ "/dev/" + dev for dev in array]
    
    def getAllCards(self):
	
	# TO DO using vgcconfig, should use vgc-monitor
	return self.host.vgcconfig.getAllCards()
    
    def getAllPartitions(self,withDevStr = 1):
        parts = []
        
	for device in self.getAllCards():
	    ps = self.getDevicePartition(device)

	    for p in ps:
		p = remove_dev(p)
		parts.append(p)
	
	# prepend "dev"
	if withDevStr == 1:
	    return self._prepend_dev_array(parts)
	return parts

    def getCardsSerials(self):
	
	cardSer = {}
	for card in self.getAllCards():
	    
	    cardType = self.getCardType(card)
	    cardSerial = self.getCardSerial(card)
            cardSer[cardSerial] = cardType 
	
	return cardSer    

    def get_part_attribute(self,devPart,attrib):
	
	
	   device = get_vgc_dev_from_part(devPart)
	   #devPart = remove_dev(devPart)
	    
	   #devPart = remove_dev_soft_partition(devPart)
	   devPart = remove_soft_partition_only(devPart)
	   
#          # commenting the code, 3.2 and above have
	   #if self.is_C7_build():
	   
	   
	   
	   devPartWithoutDev = remove_dev(devPart)
	   # try with remove partition first, and then try with Part
	   try: 
	      return self.getDeviceDetails(device)['part'][devPartWithoutDev][attrib]
	      trace_info("Unable to find attrib '%s' for device '%s',retrying with dev"%(attrib,devPartWithoutDev))
	   except KeyError:
	      try:
	         return self.getDeviceDetails(device)['part'][devPart][attrib]
	      except KeyError:
		 raise ViriError("Unable to find attrib '%s' for device '%s'"%(attrib,devPart))
	      
	
    def getCardPartUcap(self,devPart):
	    #device = get_vgc_dev_from_part(devPart)
	    #devPart = remove_dev(devPart)
	    
	    #devPart = remove_dev_soft_partition(devPart)
	    #return self.getDeviceDetails(device)['part'][devPart]['ucap']
	   
            return self.get_part_attribute(devPart,'ucap')
    
    def getCardPartWrites(self,devPart):
          
	    return self.get_part_attribute(devPart,'write')
	   
    def getCardType(self,device):
            """takes device as /dev/vgca, returns 2.2TB or 550GB """
	    cardInfo = self.getCardInfo(device)
            
            # this function definded in Util.py
	    return get_card_type(cardInfo)
    
    def get_supported_partions(self,device):
        
        """ return as string 2 for 2.2TB and 1 for 550GB """
        # return from Specs.py
        # specsCard['2.2TB']['partitions']
        return specsCard[self.getCardType(device)]['partitions']
    
    def get_supported_partitions_array(self,device):   
        """ returns array string elements ['1','2'] if 2 """
        partitions = int(self.get_supported_partions(device))
        
        partitions = partitions + 1
        
        # str used to return array with elements as string
        return [str(i) for i in range(1,partitions)]

    def ifDriverLoaded(self):
        # TO DO this command will just fail
        # further not being ussed
	o = self.host.run_command_chk_rc(self.vgcMonStr)
		
	out = o['output']
        
        DRIVER_NOT_LOADED_STRING = "driver *NOT* loaded"
	for l in out:
            if re.search(DRIVER_NOT_LOADED_STRING,l):
                raise ViriError("Driver doesn't seem to be loaded,Found string '%s'"%DRIVER_NOT_LOADED_STRING)
				
	return 1     
		        
    def getBuild(self):
        
        try:
   
	        return self.getDevicesDetails()['build']
        except KeyError:
                print "("
                print self.getDeviceDetails(device)
                print ")"
                raise IndexError("build not found for device '%s'"%device)

    def getBuildOnly(self):
        
	regex = "\S+\((\S+)\)"
        build = self.getBuild() 
        if re.search(regex,build):
            m = re.search(regex,build)
            build = m.group(1)
        
        return build
	    
		    
    def is_device_good_state(self,device):
	
	compare("Good",self.getDeviceAttribute(device,'state'),"device %s"%device,raiseOnError = 1)
	return 1
    
    def getBuildNoReleaseString(self):
	str = self.getBuild()
	str_a = str.split(".")
	
	return "%s.%s"%(str_a[-1],str_a[-2])
	
	
    def is_C7_build(self):
	
	# if it ends with C7
	if re.search('.*.C7$',self.getBuildOnly()):
	    print "vgc-monitor: Found 3.2 build"
	    return True
	return False
	
	    
	    
	    
	    
    
    
