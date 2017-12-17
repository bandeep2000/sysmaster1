#from Host import *
from Parsers import *
from Trace import *
import re
from Util import *
from VirExceptions import *
from Machine.Host import CommandError

#Example usage
##!/usr/bin/python
#from LVM import *
#from ViriImports import *
#h = create_host("sqa11")

#lvm = lvmgr(h)
#lvm.pvremove("/dev/vgca0")
#lvm.vgremove("V1")
#lvm.pvcreate("/dev/vgca0")
#lvm.pvcreate("/dev/vgcb0")
#print lvm.pvdisplay("/dev/vgca0")
#lvm.vgcreate("V1",["/dev/vgca0","/dev/vgcb0"])
#lvm.lvcreate("LV1","V1","10G","--stripes 2")
#print lvm.lvdisplay("LV1","V1")

"""
[root@sqa11 ~]# dmsetup ls
V1-LV1	(253, 0)
[root@sqa11 ~]# vgchange -a n
  0 logical volume(s) in volume group "V1" now active
[root@sqa11 ~]# dmsetup ls
No devices found
[root@sqa11 ~]# 
"""

class lvmgr:
    def __init__(self,host):
        self.host = host
    def pvcreate(self,disk):
        #chkifVgcDevPart(disk)
        self.host.run_command_chk_rc("pvcreate %s"%disk)
    def pvdisplay(self,disk):
        #chkifVgcDevPart(disk)
        o = self.host.run_command_chk_rc("pvdisplay %s"%disk)
        output = o['output']
	# function in Parsers library
        return parse_pvdisplay(output)
    
    def pvremove(self,disk):
        #chkifVgcDevPart(disk)
        try:  
          self.host.run_command_chk_rc("pvremove %s -f"%disk)
        except:
            trace_info("Doesn't seem to be any physical vol on device '%s'"%disk)
            return 0
        return 1

    
    def vgcreate(self,vgName,disksArray):
	"""Example:
	    lvm.vgcreate("V1",["/dev/vgca0","/dev/vgcb0"]) """
	chkifListPassed(disksArray)
        
	cmd = "vgcreate %s "%vgName
	# create command from disk array
	for disk in disksArray:
		# append string
		cmd = cmd + disk + " "
		
        self.host.run_command_chk_rc(cmd)
	return 1

    def vgremove(self,vgName):
        try:
            self.host.run_command_chk_rc("vgremove %s -f"%vgName)
        except:
            trace_info("Doesn't seem to be any vol grp '%s' present"%(vgName))
            return 0
        return 1
    
    def _cmp_lv(self,found,expected,details,cmd):
	    
	    if found != expected:
		 raise ViriLVMError("%s found '%s' expected '%s' in cmd '%s' "%(details,found,expected,cmd))
		 sys.exit(1)
	    trace_info("%s found '%s' expected '%s' in cmd '%s' "%(details,found,expected,cmd))
	    
	    return 1
    
    # 220.00 GiB to 220G, also some times is present and sometimes not
    def _removeI(self,str):
	    
	    regex = "(\d+)\.\d+\s+(\S)i?\S+"
	    try:
	       m = re.search(regex,str)
	    except:
		    print "Error: string '%s' doesn't seem to have regex '%s'"%(str,regex)
		    sys.exit(1)
	    
	    # concat 220 and G and return
	    return m.group(1) + m.group(2)
	   
    def get_lv_path(self,vgName,lvName):
            """returns string  as /dev/V1/LV1 given V1 LV1, as example"""
	    device = "/dev/%s/%s"%(vgName,lvName)
	    #device = "/dev/mapper/%s-%s"%(vgName,lvName)
	    return device
    
    def get_lv_mount_path(self,vgName,lvName):
	    # mount uses /dev/mapper/V1-LV1 on /flash1 type xfs (rw)
	    device = "/dev/mapper/%s-%s"%(vgName,lvName)
	    return device
    
    def lvdisplay(self,lvName,vgName):
            """returns parse lvdisplay output"""
	    device = self.get_lv_path(vgName,lvName)
	    o = self.host.run_command_chk_rc("lvdisplay %s"%device)
	    output = o['output']
	    return parse_lvdisplay(output)
    
    def lvcreate(self,lvName,vgName,size,options = " "):
        
            """ creates logical volume, makes sure size logical volume gets creates  """
        
	    cmd = "lvcreate %s --size %s --name %s %s"%(options,size,lvName,vgName)
	    
	    trace_info("Runnning command '%s'"%cmd)
	    self.host.run_command_chk_rc(cmd)
	    lvdet = self.lvdisplay(lvName,vgName)
   
	    lvNameFound = lvdet['lvname']

	    vgNameFound = lvdet['vgname']
	    
	    # this is hack, sometime LVname retured ins LVStripe and sometime
	    # /dev/V1/LVStripe, seem like it is linux dependent
	    # if /dev not present create /dev/V1/LV1
	    if not re.search("/dev/.*",lvNameFound):
		trace_info("LV name '%s' found was found without /dev and volume name"%lvNameFound)
		lvNameFound = self.get_lv_path(vgNameFound,lvNameFound)
		
	    
	    lvSizeFound = lvdet['lvsize']
	    lvSizeFound = self._removeI(lvSizeFound)
	    
	    # convert V1,LV1 to /dev/V1/LV1
	    lvName = self.get_lv_path(vgName,lvName)
            print  lvNameFound
            print lvName
            
	    
	    self._cmp_lv(lvName,lvNameFound,"Logical Volume",cmd)
	    self._cmp_lv(vgName,vgNameFound,"Volume Group",cmd)
	    self._cmp_lv(size,lvSizeFound,"LV size",cmd)
          
	    return 1
    
    def getlvSize(self,lvName,vgName):
	    lvdet = self.lvdisplay(lvName,vgName)
	    lvSizeFound = lvdet['lvsize']
	    lvSizeFound = self._removeI(lvSizeFound)
	    return lvSizeFound
	
    def lvextend(self,lvName,vgName,size):
	    device = self.get_lv_path(vgName,lvName)
	    
	    cmd = "lvextend --size %s %s"%(size,device)
	    
	    self.host.run_command_chk_rc(cmd)
	    foundSize = self.getlvSize(lvName,vgName)
	    self._cmp_lv(size,foundSize,"LV size",cmd)
	    
	    return 1
    
    def lvreduce(self,lvName,vgName,size):
	    device = self.get_lv_path(vgName,lvName)
	    
	    cmd = "lvreduce --size %s %s -f"%(size,device)
	    self.host.run_command_chk_rc(cmd)
	    
	    foundSize = self.getlvSize(lvName,vgName)
	    self._cmp_lv(size,foundSize,"LV size",cmd)
	    return 1
	    
    def mount_fs_lvm(self,lvName,vgName,mntPoint,filesys):
	    
	    """takes lv name, volume group name , mount point, fileystem as inputs,
	    creates , makes sure filesystem and mount point matches
	    returs 1 on success, if MOUNT POINT/Directory is present
	    it will DELETE! it
	    Example:
	    lvm.mount_fs_lvm("LV1","V1","/flash","xfs")"""
	    
	    # create device /dev/LV1/V1
	    device = self.get_lv_path(vgName,lvName)
	    
	    # call the filesystem from host object
	    
	    for c in range(0,2):
		
	        try:
	            self.host.mount_fs_all(device,mntPoint,filesys)
		except CommandError:
		    print "INFO: Seems like mounting with %s failed, retrying with dev mapper"%device
		    self.host.umount(device)
		    device = self.get_lv_mount_path(vgName,lvName)
		    continue
	    
	    
	    # verify from mount command if it really mounted with right fileystem
	    
	    # convert to /dev/mapper/V1-LV1 and give to host object mount details
	    device = self.get_lv_mount_path(vgName,lvName)
	    getMnt = self.host.get_mount_details(device)
	    
	    #print getMnt
	    foundFilesys = getMnt[device]['filesys']
	    foundMntPnt  = getMnt[device]['mntpoint']
	    
	    cmd = "mounting lvm"
	    self._cmp_lv(filesys,foundFilesys,"filesystem",cmd)
	    self._cmp_lv(foundMntPnt,mntPoint,"mount point",cmd)
	    
	    return 1
    
    def umount_fs_lvm(self,lvName,vgName):
            """ inputs take volume group, volgrp as inputs,umounts lvm  """
	    device = self.get_lv_path(vgName,lvName)
            #print device
            #sys.exit(1)
	    #call the filesystem from host object
	    self.host.umount(device)
	    return 1
    
    def set_attributes(self,lvm,volGrp,devArray):
	"""
	sets the atributes,so it can be used later
	"""
	self.lvm = lvm
	self.devArray = devArray
	self.volGrp = volGrp
	
	return 1
   
    def cleanup(self,lvmArray,volGrp,devArray):
        """ unmounts lvms, remove volgrps, remove physical volumes, return 1 on success,
        doesnt exit if any command fails """
        chkifListPassed(devArray)
        chkifListPassed(lvmArray)
        for lvm in lvmArray:
            #print lvm
            #sys.exit(1)
            self.umount_fs_lvm(lvm,volGrp)  
         
        self.vgremove(volGrp)
        for dev in devArray:
            self.pvremove(dev)
        
	return 1    
	    
 
    def createLVMountRunIO(self,mntPoint,volGrp,lvmSize,options,runIO = True):
        #io = IOS.DD(self.host)
        #size = "100G"
        dir = "/" + mntPoint
        file = "hello"
        file = dir + "/" +  file
        lvm = mntPoint
        
               
        self.lvcreate(lvm,volGrp,lvmSize,options)
	
	# NOTE : TODO Sometimes xfs is not present doenst give a good message
        self.mount_fs_lvm(lvm,volGrp,dir,"xfs")
        
        #if runIO:
        #   io.runIO(file)
        md5sum =  self.host.create_file_dd_get_md5sum(file)
        
        return file,md5sum        

    def runLVMTestCases(self,devArray):
        
         chkifListPassed(devArray)
         
         volGrp = "V1"
         # TODO this need to be improved
         lvmArray =  ['LVStripe', 'LVMirror','LVStripe8', 'LVNoOption']
         
         self.cleanup(lvmArray,volGrp,devArray)
            
         # configure
         for dev in devArray:
             self.pvcreate(dev)
         self.vgcreate(volGrp,devArray)
         
         lvmOriginalSize = "5G"
         lvm = "LVStripe"
	 
	 #LMV stripe
	 ###################
	 
	 trace_info_dashed("Running LVStripe without  stripte size tests")
         file,md5sumBef = self.createLVMountRunIO(mntPoint = lvm,volGrp = volGrp ,lvmSize = "5G" ,
                                 options = "--stripes 2" ,runIO = False )
	 
	 
	 ####################
	 # LVM Stripe extend
	 #####################
	 startExtendSizeinGB = 6
         #endExtendSizeinGB   = 70
         endExtendSizeinGB   = 8
         testcaseName = "LVM: Stripe extend %i -> %i GB"%(startExtendSizeinGB,endExtendSizeinGB)
         #self.setPrintRunningTestCase(testcaseName)
         
	 trace_info_dashed("Running testcases %s"%testcaseName)
	 
         for size in range(startExtendSizeinGB,endExtendSizeinGB):
             size = str(size) 
             trace_info("Extending the lv to '%s'"%size)
             self.lvextend(lvm,volGrp,"%sG"%size)

             md5sumAft = self.host.get_md5sum(file)
             cmp_md5sum(md5sumBef,md5sumAft,"extend lvm")
	     
	     
	     
	     
	 ####################################
         # Reduce Test case
         ###################################
         t1 = get_epoch_time()
         # reduce back to original size
         testcaseName = "LVM: Stripe reduce back to %s"%lvmOriginalSize
	 trace_info_dashed("Running testcases %s"%testcaseName)
         #self.setPrintRunningTestCase(testcaseName)
         # extend testcase
         self.lvreduce(lvm,volGrp,size = lvmOriginalSize)
         
                
                  
         trace_info_dashed("Running LVM mirror testing")
         # Mirror Test casses
         self.createLVMountRunIO(mntPoint = "LVMirror",volGrp = volGrp ,lvmSize = "100G" ,
                                 options = "-m1 --mirrorlog core" )
                   
        
	 # Stripe test cases
	 trace_info_dashed("Running LVM stripes and stripesize testing")
         stripesize = "8"
         option = "--stripes 2 --stripesize %s"%stripesize
         self.createLVMountRunIO(mntPoint = "LVStripe8",volGrp =volGrp,lvmSize = "100G" ,
                                 options = option )
	 
	 trace_info_dashed("Running LVM No option testing")
                                 
         self.createLVMountRunIO(mntPoint = "LVNoOption",volGrp = volGrp,lvmSize = "100G" ,
                                 options = " " )
         
         
         # clean up
         self.cleanup(lvmArray,volGrp,devArray)
         
