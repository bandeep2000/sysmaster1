from VgcUtils import *

class cardPartition:
   def __init__(self,partName,life,reads,writes,flashResLeft):
	    self.partName = partName
	    self.life    = life
	    self.reads   = reads
            self.writes =  writes
	    self.flashResLeft = flashResLeft
	    
  	    
   def getName(self):
	   return self.partName
   def getReads(self):
	   return self.reads
   def getWrites(self):
	   return self.writes
	   
   def getLife(self):
	   return self.life
   
   def getFlashResLeft(self):
	   return self.flashResLeft
   
   def returnAllAttribs(self):
	   return (self.life,self.reads,self.writes,self.flashResLeft)
	   
    
class vgcCard:
    def __init__(self,cardName,host):
	    self.cardName    = cardName
	    self.host        = host
	    self.partitions  = []
	    self.setAttributes()
    
    
    def setAttributes(self):
	    #initialise vgmonitor object
	    vm = vgcMonitor(self.host)
	    parsedOut = vm.getDeviceDetails(self.cardName)
	    
	    partitions = parsedOut['part']
	    #print partitions
	    
	    # initialize partition object
	    # NEED to add more attrib here
	    for part in partitions:
		    # part is /dev/vgca0
		    
		    #print part
		    
		    life = partitions[part]['life']
		    reads = partitions[part]['read']
		    writes = partitions[part]['write']
		    #print writes
		    #sys.exit(1)
		    flResLeft = partitions[part]['flashReserveLeft']
		    partObject = cardPartition(part,life,reads,writes,flResLeft)
		    self.partitions.append(partObject)
    	    
    def getPartLifeAttribs(self,devPart):
	    
	    """return main attribs read/writes """
	    if_vgc_dev_part(devPart)
	    for p in self.partitions:
		  
		  if p.getName() == devPart:
			  
		      return \
		       (p.getLife(),p.getReads(),p.getWrites(),p.getFlashResLeft())
		  
    
    def getPartitions(self):
        return self.partitions

    def setCritical(self):

	device_letter = get_device_letter(self.cardName)

	comm = "echo e | %s -w vgcdrive%s0/bb_credits" % (VGCPROC, device_letter)
	self.host.run_command_chk_rc(comm)

	vm = vgcMonitor(self.host)
	device_details = vm.getDeviceDetails(self.cardName)
	
	if device_details['state'] != 'Critical':
		raise ViriError("error putting card into critical state")
	else:
		trace_success("card state is critical")
	
	return 1

    def setOffline(self):
	
	comm = "rpm -qa | grep vgc-admin"
	self.host.run_command_chk_rc(comm)	

	comm = "/usr/lib/vgc/fdparm --offline /dev/%s0" % self.cardName
	self.host.run_command_chk_rc(comm)

	vm = vgcMonitor(self.host)
	device_details = vm.getDeviceDetails(self.cardName)

	if device_details['state'] != 'Warning':
		raise ViriError("error putting card into admin offline")
	else:
		trace_success("card state is warning")
	
	return 1
