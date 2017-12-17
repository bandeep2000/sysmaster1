#!/usr/bin/python
import sys
from Host import *
# Usage is hostname /dev/vgca0

success = []

def test_fs(device,mnt_pnt,fs,file):
    print_blue( "-" * 80)
    trace_info("Testing Filesystem '%s' on device '%s'"%(fs,device))
    print_blue( "-" * 80)
    file = mnt_pnt + "/" + file 

    # initialize
    h.mkdir(mnt_pnt)

    h.create_fs(device,fs)
    found_fs = h.get_fs(device)

    if found_fs != fs:
        trace_error("Found filesystem '%s', expected %s"%(found_fs,fs))
        sys.exit(1)
    #trace_success("Found filesystem '%s', expected %s"%(found_fs,fs))
    
    h.mount_fs(device,mnt_pnt)
    h.create_file(file)
    md5sum_s = h.get_md5sum(file)

    for c in range(1,100):
       h.umount_fs(device)
       h.run_command_chk_rc("service vgcd stop")
       h.run_command_chk_rc("service vgcd start")
       h.mount_fs(device,mnt_pnt)
       md5sum_f = h.get_md5sum(file)


       if md5sum_f == md5sum_s:
        print "SUCCESS: md5sum before '%s' matches after '%s' at restart '%i'"%(md5sum_s,md5sum_f,c)
        print " " 
        continue
       else:
        print "FAIL: md5sum before '%s'doesn't matches after '%s' at restart '%i'"%(md5sum_s,md5sum_f,c)
        sys.exit(1)

h = Host(sys.argv[1])
device = sys.argv[2] # /dev/vgca0
mnt_pnt = "/flash-max"
#fs = sys.argv[2]
try:
   h.umount_fs(device)
#except CommandError:
#   sys.exit(1)
except:
   print "INFO: Seems like it is filesystem is already unmounted continuing.."
   pass

#filesystems = ['ext2','ext3', 'ext4' , 'xfs']
#filesystems = ['ext3', 'ext4' , 'xfs']
filesystems = ['xfs']
for fs in filesystems:
     test_fs(device,mnt_pnt,fs,"hello")
