from Util import *
#from FileSystems import *
class  filesystem:
    def __init__(self,host):
        self.host = host
        
    def verifyRWMounts(self,devPart,mntPnt ,filesys,loop = 1,details = ""):

           """
           inputs:
            devPart:  Device Partition as /dev/vgca0,not as /dev/vgca..
            filesys: as ext4,ext3
            loops: loops to repeat
           
           description: creates filesystem, creates file and gets md5sum, runs fio sync on another file
           does driver restart, verifies the md5sum of the first file created matched,
           repeats this in loop including fio job, cleans up by unmounting after the test
           
           raises on failure, 1 on success
           """
           check_if_vgc_part(devPart)

	   # clean up umount first before starting
	   self.host.umount(devPart)

           self.host.mount_fs_all(devPart,mntPnt,filesys)

	
	   device = get_vgc_dev_from_part(devPart)
	
	   file1 = mntPnt + "/file1"
	   file2 = mntPnt + "/file2"
	   
	   # create file and get md5sum
           mdsum1 = self.host.create_file_dd_get_md5sum(file1)
	   
           tcaseName = "Mount/umount %s"%filesys
	   	   
           for c in range(0,loop):
               trace_info("Starting loop '%i' for testcase  %s"%(c,tcaseName))
               #tcaseName = "%s%i"%(tcaseName,c)
	       
               # Run fio fsync for 10 seconds on second file
	       self.host.fio().run(file2,"16K","10",rw_perc ="70",rw = "randrw",fsync ="8",size = "1G")
	       self.host.umount_fs(devPart)
	       
	       self.host.run_command_chk_rc("service vgcd restart")
	       
	       self.host.mount_fs(devPart,mntPnt)
	       mdsum2 = self.host.get_md5sum(file1)
               
               # compare md5sum
	       cmp_md5sum(mdsum1,mdsum2,"mounting fs %i"%c)

	   #umount , part of clean up after test
	   self.host.umount_fs(devPart)
	
    def createFilesysMultipleTimes(self,devPart,filesys,options = None,loops = 4):
       
       check_if_vgc_part(devPart)
               
       tcaseName = "FileSystem '%s' on device '%s' '%i' times"%(filesys,devPart,loops)
      
       for c in range(0,loops):
           trace_info("Starting loop '%i' for testcase  '%s'"%(c,tcaseName))
           self.host.create_fs(devPart,filesys,options)

       
       return 1
    
    
    
    def runAllFilesystems(self,devPart):

       
                  
       # TO DO this should get from the host class
       filesystems = ['xfs',"ext2","ext3","ext4"]
       
      
       
       self.host.is_all_fs_binaries_present()
       
       dict1 = {}
       
       for fs in filesystems:
          loops = 5
          self.createFilesysMultipleTimes(devPart,filesys = fs ,options = None,loops = loops)
          key1 = "%s-create-fs-%i-times"%(fs,loops)
          dict1[key1] = "PASSED"
       
       for fs in filesystems:
          self.verifyRWMounts(devPart,"/nand4",fs,loop = 2)
          key = "%s-rw-remounts"%fs
          dict1[key] = "PASSED"

       

       print "INFO:Summary:"
       for k in dict1.keys():
           print "%s => %s"%(k,dict1[k])
          
       #self.verifyRWStimulus("service vgcd restart",devPart,loops = 2)
       
       return 1

       
           