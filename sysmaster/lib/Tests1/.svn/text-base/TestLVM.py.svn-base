from ViriImports import *
#import IOS
from Util import *
from TestRunUtils import *

"""
Example Usage
#!/usr/bin/python
import sys
from Host import Host
from TestLVM import *

h = Host(sys.argv[1],logfile_object = None)

t = LVMTests(h,"lvm")


"""
class LVMTests(testRunUtils):
    
    def __init__(self,host,desc,raiseOnErrors,mntPoint = None):
        print raiseOnErrors
        TestUtils.__init__(self,host,desc,raiseOnErrors = raiseOnErrors,mntPoint = mntPoint)
        #self.lvm = LVM.lvmgr(self.host)
        self.lvm = lvmgr(self.host)
        
        
    def createLVMountRunIO(self,mntPoint,volGrp,lvmSize,options,runIO = True):
        #io = IOS.DD(self.host)
        #size = "100G"
        dir = "/" + mntPoint
        file = "hello"
        file = dir + "/" +  file
        lvm = mntPoint
        
        t1 = get_epoch_time()
        testcaseName = "LVM: options = %s"%options
        self.setPrintRunningTestCase(testcaseName)
        self.lvm.lvcreate(lvm,volGrp,lvmSize,options)
        self.lvm.mount_fs_lvm(lvm,volGrp,dir,"xfs")
        
        #if runIO:
        #   io.runIO(file)
        md5sum =  self.host.create_file_dd_get_md5sum(file)
        
        t2 = get_epoch_time()
        tdiff = t2 - t1
        
        rc = "0" # rc will be zero if above command passes
        self.setTestCaseRcTime(testcaseName, rc, tdiff)
       
        self.print_tcase_success(testcaseName,"Commands didn't fail")
        return file,md5sum
    
    def runValidationStripe(self,devArray,time = "43200" ):
        
        
         volGrp = "V1"
         lvm = "LV1"
         
         self.lvm.cleanup([lvm],volGrp,devArray)
        
         for dev in devArray:
           self.lvm.pvcreate(dev)
         self.lvm.vgcreate(volGrp,devArray)
         
         
         
         dir = "/LVStripe"
         
         self.lvm.lvcreate(lvName = lvm,vgName = volGrp,size = "100G",options = "--stripes 2" )
         
         #self.lvm.mount_fs_lvm(lvm,volGrp,dir,"xfs")
         self.lvm.mount_fs_lvm(lvm,volGrp,dir,"ext3")
         
         details = "LVM stripes2"
         
         fileName = dir + "/hello"
         
         dict = { 'devices':
           {
               #'/raid/hello': { 'threads': '256','bs':'8192','size':'400G'},
               fileName: { 'threads': '16','bs':'4096','size':'80G'},
           },
         'verify' : True,
         'time' : time,
         'printInterval':'10',
          }

         
         
         
         self.runVdbench(dict,details = details)
                      
         self.lvm.cleanup([lvm],volGrp,devArray)
         return 1
                      
        
    def runLVMTestCases(self,devArray):
        
         chkifListPassed(devArray)
         
         volGrp = "V1"
         # this need to be improved
         lvmArray =  ['LVStripe', 'LVMirror','LVStripe8', 'LVNoOption']
         
         self.lvm.cleanup(lvmArray,volGrp,devArray)
            
         # configure
         for dev in devArray:
             self.lvm.pvcreate(dev)
         self.lvm.vgcreate(volGrp,devArray)
         
         lvmOriginalSize = "5G"
         lvm = "LVStripe"
         file,md5sumBef = self.createLVMountRunIO(mntPoint = lvm,volGrp = volGrp ,lvmSize = "5G" ,
                                 options = "--stripes 2" ,runIO = False )
         
         #md5sumBef =  self.host.create_file_dd_get_md5sum(file)
         
         # extend testcase
         t1 = get_epoch_time()
         startExtendSizeinGB = 6
         #endExtendSizeinGB   = 70
         endExtendSizeinGB   = 8
         testcaseName = "LVM: Stripe extend %i -> %i GB"%(startExtendSizeinGB,endExtendSizeinGB)
         self.setPrintRunningTestCase(testcaseName)
         
         for size in range(startExtendSizeinGB,endExtendSizeinGB):
             size = str(size) 
             trace_info("Extending the lv to '%s'"%size)
             self.lvm.lvextend(lvm,volGrp,"%sG"%size)

             md5sumAft = self.host.get_md5sum(file)
             cmp_md5sum(md5sumBef,md5sumAft,"extend lvm")
         
         t2 = get_epoch_time()
         tdiff = t2 - t1
        
         rc = "0" # rc will be zero if above command passes
         self.setTestCaseRcTime(testcaseName, rc, tdiff)
         self.print_tcase_success(testcaseName,"Commands didn't fail")
         
         ####################################
         # Reduce Test case
         ###################################
         t1 = get_epoch_time()
         # reduce back to original size
         testcaseName = "LVM: Stripe reduce back to %s"%lvmOriginalSize
         self.setPrintRunningTestCase(testcaseName)
         # extend testcase
         self.lvm.lvreduce(lvm,volGrp,size = lvmOriginalSize)
         
         t2 = get_epoch_time()
         tdiff = t2 - t1
         rc = "0" # rc will be zero if above command passes
         self.setTestCaseRcTime(testcaseName, rc, tdiff)
         self.print_tcase_success(testcaseName,"Commands didn't fail")
         
       
         
         self.createLVMountRunIO(mntPoint = "LVMirror",volGrp = volGrp ,lvmSize = "100G" ,
                                 options = "-m1 --mirrorlog core" )
                   
                   
         stripesize = "8"
         option = "--stripes 2 --stripesize %s"%stripesize
         self.createLVMountRunIO(mntPoint = "LVStripe8",volGrp =volGrp,lvmSize = "100G" ,
                                 options = option )
                                 
         self.createLVMountRunIO(mntPoint = "LVNoOption",volGrp = volGrp,lvmSize = "100G" ,
                                 options = " " )
         
         
         # clean up
         self.lvm.cleanup(lvmArray,volGrp,devArray)
         
         #self.print_summary()
     
        
         
         
         
         
         
         
         
