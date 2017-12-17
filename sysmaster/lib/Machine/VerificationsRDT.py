from Verifications import *

class verificationsrdt(verifications):
    
    def chk_errors_in_sylogs_dmesg(self):
        
	# TO DO there is is a similar function in Host.py, need to clean it up
	#errors_regex = ['VGC:\s*\[\S+:E\].*', 'Event R2']
	errors_regex = ['Event R2','VGC:\s*\[\S+:E\].*','vgcd.pid not readable',    'Virident FlashMAX Drive init script','vgcd.service entered failed']
#	errors_regex = ['Event R2','VGC:\s*\[\S+:E\].*']
	#out = ["VGC: [0000000800d90e03:I] EU stabilization Read FAILED : Ctx 1, plane 0, page 194, offset 0x3d1e1840000, write-mask 0x00000000, 0 0 0 0 6 6 0 0"]
        
	found_errors = 0
	#output_array = []
	for cmd in ["cat /var/log/messages | grep -v 'Failed to get exclusive access, another operation may be in progress. Resource temporarily unavailable.' | grep -v 'reason ue-limit'","dmesg | grep -v 'reason ue-limit' | tee /dev/null"]:
          out = self.host.run_command_get_output(cmd)
		 
	  for l in out:
		    for e_regex in errors_regex:
		       if re.search(e_regex,l):
			  found_errors = 1
			  print l # print to std out
	                  
	                  #raise ViriError("Found regex %s matching in line as %s"%(e_regex,l))
	
        if found_errors == 1:
	   trace_error("Found some errors in syslogs or dmesg matching regex '%s'"%errors_regex)
	   raise ViriError("Found some errors in syslogs or dmesg matching regex '%s'"%errors_regex)
	return 1
