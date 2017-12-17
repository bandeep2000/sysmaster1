#!/usr/bin/python
import sys,time
from IOS import *
from Util import *
from Host import Host

h = Host("sqa05")
h.logon()
device = "/dev/vgcc"
device_p = device + "0"
sec_opt = sys.argv[1]
dir = "/flash_max/"


#print "Please do reset card, press any key to continue.."
#raw_input()
#h.reset_card(device)
#wait = 60

#h.create_and_verify_fs(device_p,"ext3")
h.rmdir(dir)
h.mkdir(dir)
h.mount_fs(device_p,dir)
h.cp_dict(dir)
sys.exit(1)


h.mount_fs("/dev/vgcc0","/flash_max")
sys.exit(1)
print "Wating %i secs after resettting the card"%wait
for i in range(wait):
    print "Seconds Passed \r %d"%i,
    sys.stdout.flush()
    time.sleep(1)


h.run_command("vgc-monitor -d %s"%device)
io = DD(h)

def ver_patt(patt):
    for s in [ 2, 400000, 40000000, 20000000]:
        io.verify_pattern(device_p,patt,skip = s)

ver_patt(".")
io.fill_drive_patt(device_p)

ver_patt("A")

#io.write_pattern(device_p,"AA")
#io.verify_pattern(device_p,"A")
#io.verify_pattern(device_p,".")

h.vgc_sec_er(device_p,sec_opt)
ver_patt(".")
# make sure it is empty
h.run_command("vgc-monitor -d %s"%device)




sys.exit(1)


#h.connection.interact()
#h.get_ipmi_ip_addr()
sys.exit(1)


for i in range(1,50):

    print "-" * 80
    print "Starting iteration %i"%i
    print "-" * 80
    h.vgc_sec_er("/dev/vgca0","purge")
    print " "
