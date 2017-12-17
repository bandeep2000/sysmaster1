
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
	    self.name    = cardName
	    self.host        = host
	    self.partitions  = []
	    #self.setAttributes()
    
    
    def setAttributes(self):
	    #initialise vgmonitor object
	    vm = self.host.vgcmonitor
	    parsedOut = vm.getDeviceDetails(self.cardName)
	    
	    partitions = parsedOut['part']
	    
	    # initialize partition object
	    # NEED to add more attrib here
	    for part in partitions:
		    
		    life = partitions[part]['life']
		    reads = partitions[part]['read']
		    writes = partitions[part]['write']
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
    def getSerial(self):
        return self.host.vgcmonitor.getCardSerial(self.name)
