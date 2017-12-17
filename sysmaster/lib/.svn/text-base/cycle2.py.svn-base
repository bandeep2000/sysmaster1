#!/usr/bin/python
import sys,os
from Util import *

conf_file = "/home/bandeepd/sqa/scripts/python/ipmi_conf.txt"

if not os.path.isfile(conf_file):
    print "Could not find config file '%s'"%conf_file
    sys.exit(1)



try:
   sys.argv[1]
except IndexError:
   print " Usage:"
   print " ./cycle.sh sqa05 10"
   print " ./cycle.sh sqa05 10 w -- 'w' is if you want to wait for host to come up"
   print " "
   print " Please make sure you have the ipmi information in file '%s' as "%conf_file
   print "hostname ipmi-ip-address-or-dns ipmi_user password"
   print " Example:"
   print "sqa05 ipmi-sqa05 ADMIN ADMIN"
   sys.exit(1)

host = sys.argv[1]
print "-" * 80
print "INFO: Power Cycling host '%s'"%host
print "-" * 80
print " "

try: 
    wait_aft_off = int(sys.argv[2])

except IndexError:
    print "ERR: Time in sec not passed to wait after power cycle"
    sys.exit(1)

wait = ""
try:
    wait = sys.argv[3]
    if wait != "w":
        print "Please pass second argument as 'w',if you want to wait for the host to come up"
        print " not as '%s'"%wait
except IndexError:
    pass




def open_file(file):

    try:
        f = open(file,'r')
    except:
        print "Could not open file '%s'"%file
        sys.exit(1)
    return f

def get_conf_from_file(host,file):
    f = open_file(file)

    for l in f:
        if l.startswith("#"):
           continue

        # skip empty lines
        if not l.strip():
            continue

        # remove any \n or \r from last line
        l = l.rstrip("\r\n")

        a = l.split()
        host_name = a[0]

        if host_name == host:
            try:
                ip_addr = a[1]
            except IndexError:
                print "Couldn't find the ipmi-ip address in file '%s'"%file
                sys.exit(1)
            try:
               u_name = a[2]
            except IndexError:
                print "Couldn't find the ipmi user name  in file '%s'"%file
                sys.exit(1)
            try:
                passwd = a[3]
            except IndexError:
                print "Couldn't find the passwd in file '%s'"%file
                sys.exit(1)
            break
        else:
            continue

    else:
        print "Didn't find entry in file '%s' for host '%s' "%(file,host)
        print " Please enter the ipmi information in file '%s' as:"%file
        print " "
        print "hostname ipmi-ip-address-or-dns ipmi_user password"
        print " Example:"
        print "sqa05 ipmi-sqa05 ADMIN ADMIN"
        sys.exit(1)

    return ip_addr,u_name,passwd


ip_addr,u_name,passwd = get_conf_from_file(host,conf_file)
pw_cmd = "off"
run_ipmi_lan_pw_command(ip_addr,pw_cmd,u_name,passwd)
print "Waiting %i sec"%wait_aft_off
time.sleep(wait_aft_off)
pw_cmd = "on"
run_ipmi_lan_pw_command(ip_addr,pw_cmd,u_name,passwd)


if wait == "w":
    print "-" * 50
    print "INFO: Waiting for machine to come up"
    print "-" * 50
    print " "
    wait_after_ipmi_cmd = 15
    print "INFO: Waiting '%i' secs after running the ipmi command"%wait_after_ipmi_cmd
    time.sleep(wait_after_ipmi_cmd)

    if is_hostup(host):
        print "-" * 80
        print "SUCCESS: Host '%s' is up"%host



