from Util import *
from Parsers import *
import sys
from Trace import *
#from VirExceptions import ViriError

class verifications():
    
    def __init__(self,host):
        
        self.host = host
        self.cardAttributes = None
	# TO DO make one variable
	self.cardStaticAttributes = {}
        
    def set_cards_static_attributes(self):
	
	trace_info("Setting all cards static attributes")
	for device in self.host.vgcmonitor.getAllCards():
	    
	    self.cardStaticAttributes[device] = self.host.vgcmonitor.getDeviceDetails(device)
    
    def set (self, ):
	
	self.set_cards_static_attributes()
	
    def run(self,set_variables = True ):
        """
	self.host.verifications().run()

	inputs: 
	set_variables - set it to false if you want it to verify
	after some test
	setting it to True will set and compare right away, might not be useful

	"""
        
    
        #if self.host.chk_if_dpp_errors(devPart):
        #     raise ViriError("Found dpp errors on device %s"%devPart)
        #self.host.chk_if_ue_errors(devPart)
        
        #self.set_card_attributes()
	
	
	trace_info("Running verfications")
        
        self.host.is_crash_dir_empty()
        #self.host.chk_viri_lspci_errors()
        self.host.print_syslogs_dmesg()
	#Uncomment this
        #self.chk_viri_lspci_errors()
	# Uncomment
	#self.chk_errors_in_sylogs_dmesg()
	self.is_unrecoverable_zero()

	for device in self.host.vgcmonitor.getAllCards():
	   self.host.vgcmonitor.is_device_good_state(device)
	   
	if set_variables:
	    trace_info("Verifications: Setting attributes")
	    self.set_card_attributes()
	    self.set_used_memory()
	    self.set()
	    
	    return 1
	
        trace_info("Verifications: Comparing attributes")
        # TO DO improve Login here, too many comparing
        self.compare_card_attributes()
	self.compare_vgc_mon_static_attributes()
        self.print_used_memory_diff()


    def is_unrecoverable_zero(self):
	
	cardPartitions = self.host.vgcmonitor.getAllPartitions(withDevStr = 0)
	
	for devPart in cardPartitions:
	    
	    unrecoverable_errors = self.host.vgcproc.unrecoverable_errors(devPart)
	    if  unrecoverable_errors > 0:
		raise ViriError("Found some unrecoverable errors '%i' on device '%s' "%(unrecoverable_errors,devPart))
	    
	    trace_info("Found unrecoverable errors  '%i' on device '%s' "%(unrecoverable_errors,devPart))
	
	return 1
    
    def chk_viri_lspci_errors(self,raiseOnErrors = 1):
   
       found_errors = 0
       
       #  lspci -s 0000:04:00.0 -vvv | grep DevSta
       # lspci -d 1a78: -D
       viri_pci_ids = self.host.lspci_get_viri_pci_ids()
       if not viri_pci_ids:
          trace_info("No Virident lspci devices found to check errors")
          return 1
      
       for pci_id in viri_pci_ids:
          o = self.host.run_command_chk_rc("lspci -s %s -vvv | grep DevSta"%pci_id)
          trace_info("Checking lspci issues for device id '%s'"%pci_id)
          output =  o['output']
          rc = parse_lspci_vv_chk_error(output[1],self.host.name, raiseOnErrors)
          if rc == 2:
             if raiseOnErrors == 1:
                raise ViriError("Found lspci errors on Virident device")
             found_errors = 1
          
       return found_errors
    
    def get_card_attributes(self):
        
        cardPartitions = self.host.vgcmonitor.getAllPartitions(withDevStr = 0)
        
        dict1 = {}
        
        for cardPartition in cardPartitions:
            dict2 = {}
            device = cardPartition[:-1]
	    gbb = self.host.vgcmonitor.get_gbb(device)

        
            dict2  = self.host.vgcmonitor.getDeviceDetails(device)['part'][cardPartition]
            #life = dict2['life']
            write = dict2['write']
            read = dict2['read']
            
	    ce     = self.host.vgcproc.get_ue_errors(cardPartition,errType = "CE")[0]
            ue     =  self.host.vgcproc.get_ue_errors(cardPartition,errType = "UE")[0]
	    tuple1 = (write,read,gbb,ce,ue)
	    
            dict1[cardPartition] = tuple1
        
        return dict1
    
     
    def  set_card_attributes(self):
        print "INFO: Setting card attributes"
        self.cardAttributes = self.get_card_attributes()
 
    def compare_card_attributes(self, ):
      
        finalAttributes   = self.get_card_attributes()
        initialAttributes = self.cardAttributes
        
             
        for devPart in initialAttributes.keys():
            initialRead =   initialAttributes[ devPart][1]
            finalRead =   finalAttributes[ devPart][1]
            
            initialWrite =   initialAttributes[ devPart][0]
            finalWrite =   finalAttributes[ devPart][0]
            initialGBB =   initialAttributes[ devPart][2]
            finalGBB =   finalAttributes[ devPart][2]
	    
	    initialCE =   initialAttributes[ devPart][3]
            finalCE =   finalAttributes[ devPart][3]
	    
	    initialUE =   initialAttributes[ devPart][4]
            finalUE =   finalAttributes[ devPart][4]

            #'lifeOperator',"lessthanequal"
            compareAttrib(finalRead,initialRead,"read  %s"%devPart,
	         "greaterthanequal",raiseOnFail = 0)
            compareAttrib(finalWrite,initialWrite,"writes %s"%devPart,
	       "greaterthanequal",raiseOnFail = 0)
            compareAttrib(finalGBB,initialGBB,"gbb %s"%devPart,
	       "equal",raiseOnFail = 0)
	    
	    compareAttrib(initialCE,finalCE,"ce %s"%devPart,
	       "equal",raiseOnFail = 0)
            
	    compareAttrib(initialUE,finalUE,"ue %s"%devPart,
	       "equal",raiseOnFail = 0)
    
    def set_used_memory(self, ):
	
	self.initial_used_memory = self.host.memory().used()
	
    def chk_errors_in_sylogs_dmesg(self):

	self.chk_soft_lockup()
        
	# TO DO there is is a similar function in Host.py, need to clean it up
	#errors_regex = ['VGC:\s*\[\S+:E\].*', 'Event R2']
	errors_regex = ['Event R2','VGC:\s*\[\S+:E\].*','vgcd.pid not readable','Virident FlashMAX Drive init script','vgcd.service entered failed']
	#out = ["VGC: [0000000800d90e03:I] EU stabilization Read FAILED : Ctx 1, plane 0, page 194, offset 0x3d1e1840000, write-mask 0x00000000, 0 0 0 0 6 6 0 0"]
        
	found_errors = 0
	#output_array = []
	for cmd in ["echo 123 >> /var/log/messages && cat /var/log/messages | grep -v 'Failed to get exclusive access, another operation may be in progress. Resource temporarily unavailable.'","dmesg"]:
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

    def chk_soft_lockup(self):

	comm = "grep 'soft lockup' /var/log/messages"
	run = self.host.run_command(comm)	
	if run['rc'] == 0:
		self.host.kernel_panic()
		raise ViriError("Found soft lockup in /var/log/messages")
	else:
		trace_success("soft lockup not found in /var/log/messages")
	
	return 1
    
    def compare_vgc_mon_static_attributes(self):
	
	"""
	compares vgcmonitor parse dictionary with static valuses
	raises on failures
	"""
	
	if self.cardStaticAttributes == {}:
	    
	    raise ViriError("Static attribues not set cards, but trying to compare")
	
	# attributes that dont change
	# Other might change such as temperature but should remain safe
	vgc_mon_static_attributes = ['pcigen','rtl','actionRequired','cardStateDetails','card_info','build','pcilanes','serial','temp_s']
	
	
	for device in self.cardStaticAttributes.keys():
	    vgcmonDictInitial = self.cardStaticAttributes[device]
	    vgcmonDictFinal   = self.host.vgcmonitor.getDeviceDetails(device)
	
	    for vgc_mon_key in vgc_mon_static_attributes:
	    
	      value1 = vgcmonDictInitial[vgc_mon_key]
	      value2 = vgcmonDictFinal[vgc_mon_key]
	    
	      compareAttrib(value2,value1,"%s %s"%(device,vgc_mon_key),
	       "equal",raiseOnFail = 1)
	
	
	
    def print_used_memory_diff(self,):
	
	final_mem = int(self.host.memory().used())
	init_mem = int(self.initial_used_memory)
	diff = final_mem - init_mem
	
	trace_info("Initial used memory %i, final used mem %i, diff %i"%(init_mem,final_mem,diff))
             
             
             
             
             
             
             

