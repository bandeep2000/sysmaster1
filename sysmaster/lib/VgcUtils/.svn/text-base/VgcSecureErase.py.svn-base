# -*- coding: utf-8 -*-
from  ViriImports import *
VGC_SEC_ER = "vgc-secure-erase"

SEC_ERASE_OPTIONS = {
                  'clear': 1,
                  'purge': 1,
                  'verbose': 1,
                  'default': 1
                  
                 }
                 
WRITE_PATTERN = "AA"
VERIFY_PATTERN = "A"
CLEAR_PATTERN  = "."
#DEFAULT_PARTITION = "0"

class vgcSecureErase:
	
    def __init__(self,host):
        self.host = host
	self.vgcSecureErase = VGC_SEC_ER
        
        self.io = DD(self.host)
        if not self.host.is_binary_present("dcfldd"):
             raise ViriError("dcfldd not present, please download")
    
    def chk_valid_sec_er_opt(self,option):

        if not SEC_ERASE_OPTIONS.has_key(option):
             raise ViriError( "ERR: Please pass option as %s,instead as '%s'"%(SEC_ERASE_OPTIONS.keys(),option))
        
        return 1
        
    def run(self,device,option,partition = DEFAULT_PARTITION):
       devPart = device + partition
       
       self.chk_valid_sec_er_opt(option)

       comm = "%s --%s %s"%(self.vgcSecureErase,option,devPart)
       trace_info("Running vgc secure erase command '%s'"%comm)
       if option == "default":
          comm = "%s %s"%(self.vgcSecureErase,devPart)
       self.host.connection.sendline(comm)
       rc = self.host.connection.expect(["Do you want to continue","Device or resource busy"])
       if rc == 1:
           err = "Found 'Device or resource busy' in command '%s'"%comm
           trace_error(err)
           raise DeviceBusy(err)
       self.host.connection.sendline("yes")
       self.host.connection.expect(self.host.expected_prompt,14000)
       output = self.host.connection.before.strip()
       output_a = output.split("\r\n")
       
       sleep_time(60,"after vgc sec erase")
       return output_a
       
    
    def sanity_tcase(self,device,partition = DEFAULT_PARTITION):
        
        devPart = device + partition
        
        for sec_opt in SEC_ERASE_OPTIONS.keys() :
	  self.io.write_pattern(devPart,WRITE_PATTERN)
	  self.io.verify_pattern(devPart,VERIFY_PATTERN)
	  self.run(device,sec_opt,partition)
	  
	  self.io.verify_pattern(devPart,CLEAR_PATTERN)
         
        return 1
         
    def fill_drive_tcase(self,device,option,partition = DEFAULT_PARTITION):
        """runs secure erase option filling whole drive with pattern a, verifies  """
        self.chk_valid_sec_er_opt(option)
        
        devPart = device + partition
        
        self.io.fill_drive_patt(devPart,WRITE_PATTERN)
    
        self.io.verify_pattern_entire_drive(device = devPart, pattern = VERIFY_PATTERN)
        self.host.vgc_sec_er(devPart,option)

        self.io.verify_pattern_entire_drive(device = devPart, pattern = CLEAR_PATTERN)

        return 1

