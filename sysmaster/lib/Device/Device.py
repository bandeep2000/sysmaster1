#from ViriImports import *
from Util import *
import FileSystems.LVM 
from Trace import *

class vgcPart:
    def __init__(self,cardPart,host):
            self.cardName    = get_device_part(cardPart)
            self.host        = host
	    self.cardPart    = cardPart
	    self.partitions  = []
	    self.lvm = None
	    # flag to check if card was already reset
	    # no need to reset and  trigger gc every time
	    self.configured  = 0 
    def is_gc_running(self):
        return self.host.vgcproc.is_gc_running(self.cardPart)
    
    def clear_initial_sectors(self):
	self.host.run_command_chk_rc("dd if=/dev/zero of=%s bs=1M count=1 oflag=direct"%self.cardPart)

    def umount(self):
	
	self.host.umount(self.cardPart)
	
    def reset(self,mode = None):
	"""
	inputs : mode as maxperformance or maxcapacity, None as default
	if None  , it resets the card which is factory defaults, vgc-config -r -f ..
	Note: It will reset using -d not as -p option, so it will do at the card level
	"""

        if mode:
	   # sometimes when new build comes they suggest do factory reset,
           # doing that before configuring the mode

           trace_info("Resetting card with factory defaults")
	   self.host.run_command_chk_rc("vgc-config -d %s -rf"%self.cardName)
           trace_info("Configuring card with mode '%s'"%mode)
	   self.host.run_command_chk_rc("vgc-config -d %s -m %s -f -n 1"%(self.cardName,mode))

	   return 1

	# TO DO, user vgcproc
        trace_info("Resetting card with factory defaults")
	self.host.run_command_chk_rc("vgc-config -d %s -rf"%self.cardName)

    def create_fs(self,mntPnt = "/nand1",filesys = "xfs"):
       """ deltes mnt point if present,creats fs and mounts """ 
       self.host.mount_fs_all(self.cardPart,mntPnt,filesys)
       return 1

    def setup(self,options):
	
       """ if lvm is passed, uses size as 200G  """
       # TODO add option if fs is not passed return
       fs    = options.get('fs',None)
       gc    = options.get('gc',None)
       mode  = options.get('mode',None)
       lvm   = options.get('lvm',None)
       
       
       lvmArray = options.get('lvmArray', None)
       # mntPnt is lower case, config parser 
       mntPnt = options.get('mntpnt',None)

       # no need to reset or configure everytime
       # TO DO , this has to be improved what if you change mode
       
       if self.configured == 0:
        if mode:
        
          self.reset(mode = mode)
	# initialize it
	self.configured = 1

        # if it is string 0 still make it None
        if int(gc) == 0:
	  gc = None
        if gc:
	    
	  self.create_gc()
	  
    
       # Create lvm first and then fileystem   
       if lvm:
          self.create_lvm(additional_devArray = lvmArray, mntPnt = mntPnt ,fs = fs,size = "200G")
	  return 1

       # TODO, self.configured should chk if filesystem has already been done, do not recreate it
       # helpful in validation tests, otherwise create fs again will destroy data
       if fs:
	  if mntPnt is None:
	    raise ViriError("fs specified but no mountpoint")
          self.create_fs(filesys = fs,mntPnt = mntPnt)

       return 1
        
    def is_gc_running_reset(self):
	"""
	
	descriptions: if gc is running, reset card to disable it
	
	"""
	
	if self.is_gc_running():
	    self.reset()
	    return 1
	
        return 2

    def read_entire_drive(self, bs = "1G"):
	
	trace_info("Started Reading drive")
	cmd = "dd if=%s of=/dev/null bs=%s iflag=direct"%(self.cardPart,bs)
	
	self.host.run_command(cmd)
	trace_info("Finished Reading drive")
	
	
	pass
    
    def fill_drive(self,count = 1,size = None, bs = "1G" ):
	""" size is in GB"""
	trace_info("Filling card %i times,size=%s"%(count,size))
	for c in range(0,count):
	   cmd = "dd if=/dev/zero of=%s bs=%s oflag=direct"%(self.cardPart,bs)
	   if size:
	      cmd = "dd if=/dev/zero of=%s bs=1G oflag=direct count=%s"%(self.cardPart,size)
	    
           self.host.run_command(cmd)
	trace_info("Done! Filling card %i times,size=%s"%(count,size))
	return 1
	#trace_info("Done! Filling card %i times "%count)
  
    def create_lvm(self,additional_devArray = None, mntPnt = "/LVStripe" ,fs = "ext3",size = "100G"):
	"""
	creates LVM with vg as V1 and LVM as LV1,fileystem as ext3 on mntpnt /LVStripe
	additional_devArray is ['/dev/vgcb0'], if device is /dev/vgca0 for this object as example
	Note: will remove the above  lvm and volume groups before starting
	"""
	if not additional_devArray:
	    devArray = [self.cardPart]
	
	else:
	    additional_devArray.append(self.cardPart)
	    devArray = additional_devArray
	
	lvm = FileSystems.LVM .lvmgr(self.host)
	
	volGrp = "V1"
        lvm1 = "LV1"

        lvm.cleanup([lvm1],volGrp,devArray)
 
        for dev in devArray:
           lvm.pvcreate(dev)
        lvm.vgcreate(volGrp,devArray)

	dir1 = mntPnt
         
        lvm.lvcreate(lvName = lvm1,vgName = volGrp,size = size )
      
        lvm.mount_fs_lvm(lvm1,volGrp,dir1,fs)
	
	#lvm.cleanup([lvm1],volGrp,devArray)
	
	# set attributes, it will help in clean up first
	lvm.set_attributes(lvm1,volGrp,devArray)
	
	self.lvm = lvm
	
	#self.clean_up_lvm()
	
        return 1
    
    def get_serial(self ):
	
	return self.host.vgcmonitor.getCardSerial(self.cardName)
    
    def get_build(self):
	
	return self.host.vgcmonitor.getBuild()
 
    def clean_up_lvm(self, ):
	
	if not self.lvm:
	    raise ViriError("LVM not set, but being used")
	
	self.lvm.cleanup([self.lvm.lvm],self.lvm.volGrp,self.lvm.devArray)
	
	return 1

    def create_gc(self):
	
	"""
	description: returns inf gc is running, if not creates it
	"""
	if self.is_gc_running():
	  trace_info("Seems like gc is already runnning,not triggering")
	  return True
	trace_info("Filling card twice")
	self.fill_drive(count =2 )
	
	fio = self.host.fio()
	# make sure stimulus is 0,otherwise it might reset vgcproc values,after driver reset
	fio.set_stimulus(stimulus = 0)
	fio.run(dev_p = self.cardPart,rw ="randwrite",bs = "8k",time = "1800")
	for c in range(1,10):
	  if self.is_gc_running():
            return True
	else:
	  raise ViriError("Could not get gc to trigger")
	
        trace_info("Reading entire drive after creating gc")
        self.read_entire_drive()



#h = create_host("mdemo1")
#v = vgcCard("/dev/vgca",h)
#print v.create_gc()

