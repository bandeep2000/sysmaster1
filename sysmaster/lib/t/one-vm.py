#!/usr/bin/python
import os
#os.path.append("/home/bandeepd/python")
from Parsers import *
import sys
file = sys.argv[1]

f = open(file,'r')

l_a = []
for l in f:
    l = l.rstrip()
    #print l
    l_a.append(l)

o = f.readlines()
#print l_a

#print parseDuMap(l_a)['18']

#print  parse_fio_output(l_a)

print parse_vgc_monitor(l_a)['part'].keys()
o1 = parse_vgc_monitor(l_a)

print o1

verify_vgc_monitor_zion(o1)
sys.exit(1)
#print parse_vgc_config_partition(l_a)
#print parseMountOutput(l_a)
#print parse_fio_output(l_a)

#f.close()


#o1 = parse_vgc_monitor(l_a)
#verify_vgc_monitor_zion(o1)
#print get_vgc_mon_d_attr(l_a,"serial")
#print get_vgc_mon_d_attr(l_a,"state")
#print get_vgc_mon_d_part_attr(l_a,"/dev/vgca0","mode")
#print parse_etc_issue(l_a)    

#func(o)
f.close()



