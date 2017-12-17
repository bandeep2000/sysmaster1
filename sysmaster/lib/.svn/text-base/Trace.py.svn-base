#!/usr/bin/python
import time

def print_blue(line):
    print "\033[1;34m%s\033[1;0m"%line
def print_green(line):
    print "\033[1;32m%s\033[1;0m"%line
def print_red(line):
    print "\033[1;31m%s\033[1;0m"%line


def get_line(str,prepend):
    curr_time = time.strftime("%Y-%m-%d %H:%M:%S")
    line = "--%s: %s: %s "%(prepend,curr_time,str) 
    return line

def get__dashed(repeat = 80):
    return "-" * repeat

def trace_info(line,dashed = False):
    line = get_line(line,"INFO") 
    #print_blue(line)
    print line
def trace_error(line):
    line = get_line(line,"ERR") 
    #print_red(line)
    print line
def trace_warn(line):
    line = get_line(line,"WARN") 
    #print_red(line)
    print line
def trace_success(line):
    line = get_line(line,"SUCCESS") 
    #print_green(line)
    print line
def trace_info_dashed(line,repeat = 80):
    line = get_line(line,"INFO") 
    print " "
    print_blue("-" * repeat)
    print_blue(line)
    print_blue("-" * repeat)
    print " "
def trace_error_dashed(line,repeat = 80):
    line = get_line(line,"ERR") 
    print_red("-" * repeat)
    print_red(line)
    print_red("-" * repeat)
def trace_success_dashed(line,repeat = 80):
    line = get_line(line,"SUCCESS") 
    print " "
    print_green("-" * repeat)
    print_green(line)
    print_green("-" * repeat)
    print " "
 



    
