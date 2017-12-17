#!/usr/bin/python
import sys,time
from IOS import *
from Util import *
from Host import Host

h = Host("sqa05")
h.logon()
device = "/dev/vgcb"
device_p = device + "0"
sec_opt = sys.argv[1]
dir = "/flash_max/"

def print_vgc_monitor():
    h.run_command("vgc-monitor -d %s"%device)
def setup():
     h.umount(device_p)
     if  h.if_file_exists(dir):
        trace_error("Dir '%s' exists"%dir)
        sys.exit(1)
     h.reset_card(device)
     sleep_time(60,"after resetting the device")
     print_vgc_monitor()

def sanity_tcase(h,device_p):

    io = DD(h)
    #for sec_opt in ['clear','purge']:
    for sec_opt in ['clear']:
        io.write_pattern(device_p,"AA")
        io.verify_pattern(device_p,"A")
        h.vgc_sec_er(device_p,sec_opt)
        sleep_time(60,"after vgc sec erase")
        io.verify_pattern(device_p,".")

# creates file sys, deletes dir, makes dir and mounts dir
def mount_fs_dir(device_p,fs,dir,options = None):
    h.create_and_verify_fs(device_p,fs,options)
    h.rmdir(dir)
    h.mkdir(dir)
    h.mount(device_p,dir)

def dict_tcase(sec_opt):
    # run set up first
    setup()

    mount_fs_dir(device_p,fs = "ext3",dir = dir,options = "-J size=400")
    h.cp_dict(dir)
    exp_file = dir + "/linux.words"
    if  h.if_file_exists(exp_file):
        trace_success("File exists")
    h.umount(device_p)
    h.vgc_sec_er(device_p,sec_opt)
    sleep_time(60,"after vgc sec erase")
    print_vgc_monitor()
    mount_fs_dir(device_p,fs = "ext3",dir = dir,options = "-J size=400")
    if not h.if_file_exists(exp_file):
        trace_success("SUCESS")
        return 1
    trace_error("FAILURE of tcase")
    print "Please check if file is not there "

def clean_up():
    h.umount(device_p)

#dict_tcase(sec_opt)
sanity_tcase(h,device_p)


