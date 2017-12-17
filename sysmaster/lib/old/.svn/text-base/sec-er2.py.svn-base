#!/usr/bin/python
import sys,time
from Host import Host

h = Host("sqa05")
h.logon()
h.vgc_sec_er("/dev/vgca0",sys.argv[1])

#h.connection.interact()
#h.get_ipmi_ip_addr()
sys.exit(1)


for i in range(1,50):

    print "-" * 80
    print "Starting iteration %i"%i
    print "-" * 80
    h.vgc_sec_er("/dev/vgca0","purge")
    print " "
