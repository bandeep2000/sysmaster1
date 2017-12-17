#from ViriImports import *
from VirExceptions import *
from Trace import *
import re

class parted:
	
    def __init__(self,host):
        self.host = host
	self.parted = "parted"
    
    def util_divide_disk_equal_size(self,size,no):

        """takes inputs size and partitions, example, divides 400G disk
    
        into 4 partitions, this can be used for parted, returns {0: [0, 95], 1: [96, 191], 2: [192, 287], 3: [288, 383]}
        return dictionary with starting,ending size"""

        initial = 1

        size = size - 20

        var = size/no
        dict =  {}
        for l in range(0,no):
            final = initial + var
            dict[l] = []
            dict[l] = [initial,final]
            initial = final + 1
        return  dict

    def get_all_partitions(self,devPart):
        
        """ return STRING array as ['0','1','2','3']"""
        
        #command =  parted -s %s print|awk '/^ / {print $1}'"%devPart
        command =  "parted -s %s print"%devPart
        o = self.host.run_command_chk_rc(command)
        
        """
        
            parted -s /dev/vgca0 print;echo $?
            parted -s /dev/vgca0 print;echo $?
            Model: Unknown (unknown)
            Disk /dev/vgca0: 2222GB
            Sector size (logical/physical): 512B/512B
            Partition Table: gpt
            
            Number  Start   End     Size   File system  Name     Flags
            1      1000kB  530GB   530GB               primary
            2      530GB   1060GB  530GB               primary
            3      1060GB  1590GB  530GB               primary
            4      1590GB  2119GB  530GB               primary
        
                """
        #print o['output']
        partitions = []
	
	for l in o['output']:
	    print l
	
        for l in o['output']:
            #print "l=",
            #print l
            # all partitions start with space
            # e.g ' 1      1000kB  530GB   530GB               primary   '
	    
	    # number followed by number folled by k|G .*
	    regex = "\s*(\d+)\s+\d+.*"
            if re.search(regex,l):
                
                m = re.match(regex,l)
                partitions.append( m.group(1))
              
        #print partitions
	#sys.exit(1)
        return partitions  
        
    def remove_all_partitions(self,devPart):
          
          partitions = self.get_all_partitions(devPart)
          
          # run -  parted -s /dev/vgca0 rm 1
          for part in partitions:
             self.host.run_command_chk_rc("%s -s %s rm %s"%(self.parted,devPart,part))
         
    def clear_device_beginning_sectors(self,devPart):
        
        cmd =  "dd if=/dev/zero of=%s bs=1M count=1"%devPart
	trace_info("Cleaning up partition on device %s"%devPart)
        self.host.run_command_chk_rc(cmd)
        
        return 1
    
    def is_gpt_partion_present(self,devPart):
        
        """ 
        
        """
        # [root@sqa12-redhat6 ~]# parted -s /dev/vgca0 print;echo $?
        #Error: /dev/vgca0: unrecognised disk label

        # TO DO
        # check for rc only
        # could add the above ERRor sting with more confimation
        cmd =  "parted -s %s print"%devPart
        o = self.host.run_command(cmd)
        
        if o['rc'] != 0:
            return False
        
        return True

    def create_partitions(self,devPart,partitions):

         self.clear_device_beginning_sectors(devPart)
         disk_size = int(self.host.get_bdev(devPart))
         
         # convert bytes to MB
         disk_size = disk_size/1024
         disk_size = disk_size/1024

         dict =  self.util_divide_disk_equal_size(disk_size,int(partitions))
         
         # parted /dev/vgca0 --script mklabel gpt
         #  parted  /dev/vgca0 -a opt --script mkpart primary 1 1048576
         self.host.run_command_chk_rc("%s %s  --script mklabel gpt"%(self.parted,devPart))
         for part in dict.keys():
             
             # array that has start ending
             # [1111222124536, 2222444249070]
             part_values = dict[part]
             trace_info("Using start/end partions in MB as %s"%part_values)
             #sys.exit(1)

             # for redhat 5 chaning this 
	     #self.host.run_command_chk_rc("%s %s -a opt --script mkpart extended %i %i "%(self.parted,devPart,part_values[0],part_values[1]))
	     self.host.run_command_chk_rc("%s %s  --script mkpart extended %i %i "%(self.parted,devPart,part_values[0],part_values[1]))
         
         # do verifications
         # TO DO add /dev/vgca0p1 etc. verifications also
         # right now it is just from parted it is making share
         found_partitions = len(self.get_all_partitions(devPart))
         string = "Found partions '%i', expected '%s' "%(found_partitions,partitions)
         if int(partitions) != found_partitions:
             raise ViriError(string)
         
         trace_info(string)
         return 1
    
    def get_soft_partitions(self,devPart):
        """ returns ['/dev/vgca0p1', '/dev/vgca0p2', '/dev/vgca0p3', '/dev/vgca0p4']"""
        parts = self.get_all_partitions(devPart)
        
        softPartitions = []
        
        for part in parts:
            part = devPart + "p" + part
            softPartitions.append(part)
            
        return softPartitions
            
            
            
            
             
             
             
        
        
