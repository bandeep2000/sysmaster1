#!/usr/bin/python
import sys,time
from Host import Host
from Util import *
from Trace import *

file = "del"
f = open(file,"w")
h = Host("sqa05",logfile_object = f)
#h.reset_card("/dev/vgca")
#h.run_vgc_monitor("/dev/vgca")


#h.connection.interact()
#h.get_ipmi_ip_addr()

device = sys.argv[1]
dev_p = device + "0"
#expected_mode = "maxperformance"
expected_mode = "maxcapacity"
expected_usable_cap = "702"

usable_cap = h.get_part_usable_cap(device)[dev_p]['us_cap']
mode = h.get_part_mode(dev_p)
serial = h.get_card_serial(device)
card_info = h.get_card_info(device)
kernel = h.get_kernel_ver()
redhat_ver = h.cat_etc_issue()

sec_er = sys.argv[2]
trace_info("-" * 80)
trace_info("Running repeated '%s' test on device '%s', serial =  '%s'"%(sec_er,device,serial))
trace_info("Card info =  '%s' ,logfile as '%s'"%(card_info,file))
trace_info(" Host Details : redhat_ver =  '%s' ,kernel version = '%s'"%(redhat_ver,kernel))
trace_info("-" * 80)
print " "


#sys.exit(1)


for i in range(1,20):

    trace_info("-" * 80)
    trace_info("Starting iteration %i"%i)
    trace_info("-" * 80)

    trace_info( "Running vgc secure '%s' command on device '%s'"%(sec_er,dev_p))
    time_s = int(time.time())
    o  = h.vgc_sec_er(dev_p,sec_er)
    print "Output Found = (" 
    for l in o:
        print l
    print ")"
    time_e = int(time.time())
    time_taken = time_e - time_s
    trace_info("time taken %i secs"%time_taken)
    sleep_time(120,"after vgc secure erase")
    usable_cap = h.get_part_usable_cap(device)[dev_p]['us_cap']
    mode = h.get_part_mode(dev_p)
    trace_info("-" * 40)
    trace_info("Found mode as  '%s', usable capacity as '%s'"%(mode,usable_cap))
    trace_info("-" * 40)
    found_err = 0
    if  usable_cap != expected_usable_cap:
        trace_error("Expected usable capacity '%s',found '%s'"%(expected_usable_cap, usable_cap))
        found_err = 1
    if  mode != expected_mode:
        trace_error("Expected mode '%s',found '%s'"%(expected_mode, mode))
        found_err = 1

    if found_err == 1:
        trace_error("Found Error")
        #print "Error found,exiting..."
        #sys.exit(1)
    
    print " "

f.close()


