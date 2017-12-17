 #!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
from Specs import *
from VgcUtils import *

"""
Example Script

#!/usr/bin/python
from Host import Host
from VgcMon import *
from Temperature import *
import sys

h = Host(sys.argv[1])
h.logon()

vm = vgcMonitor(h)
print vm.getDevStatus("/dev/vgca0")

"""
VGCPROC = "/usr/lib/vgc/vgcproc"
PROC = "/proc/driver/virident"

class vgcProc(vgcUtils):
	
    def __init__(self,host):
        #self.host = host
	self.vgcProcStr = VGCPROC
        vgcUtils.__init__(self,host)
    
    def run(self,option1,option2,grep = None):
	
       """
	 inputs: option1 is vgcdrivea0 and options2 is bb_stats as example, do not
	 need to give whole paths
       """
        
       cmd = "%s %s/%s/%s"%(VGCPROC,PROC,option1,option2)
       
       #if grep:
	   # added grep -v header to ignore header UE errors
	   # this is hack
           #cmd = cmd + "| grep " + grep + " | grep -v 'HEADER'"
	   #cmd = "%s | grep -i error | grep %s | egrep -v 'Superblock|HEADER'"%(cmd,grep)
       o = self.host.run_command_chk_rc(cmd)
 
       output = o['output']
       
       if not grep:
	 return output
       
       
       # TO improve logic here
       output_grep = []
       
       for l in output:
	 
	 if grep:
	    if re.search('Superblock|HEADER',l):
		continue
	    
	    if not re.search('(e|E)rrors',l):
		continue
	    if re.search(grep,l):
		 output_grep.append(l)

       # Verbose
       for l in  output_grep:
	      print l
       return output_grep
         
    def get_dpp_errors(self,devPart):
	option1 = "vgcdrive%s"%get_device_letter_part1(devPart)
	
	output = self.run(option1,"bb_stats")
	
	for l in output:
	    if re.search("DPP Read Errors",l):
		# more verbose
		print "INFO: DPP Read Error Details as '%s'"%l
		l_a = l.split(":")
		
	        return l_a[1].strip()
	# if error, raise and print output    
	printOutput(output)
	raise ViriError("Did not find DPP Read Errors string in output ")

    def get_erased_read_errors(self,devPart):
	"""
	input: /dev/vgca0 as example
	returns erase error from this example
	Data Read Errors (CE, UE, Erased, PErased, IO) : 0 0 4 0 0
	return 4  in this case as string !! Please note string not integer, you have to use
	int function to check
	raises exception, if 'Data Read Error' string is not found in the output
	"""
	option1 = "vgcdrive%s"%get_device_letter_part1(devPart)
	
	output = self.run(option1,"bb_stats")
	
	for l in output:
	    if re.search("Data Read Errors",l):
		# more verbose
		print "INFO: Erased Read Error Details as '%s'"%l
		
		l_a = l.split(":")
		# Split ['Data Read Errors (CE, UE, Erased, PErased, IO) ', ' 0 0 0 0 0']
		l_a1 = l_a[1].split()
		# split 0 0 0 0 0' and return 2 index for erased		
		return l_a1[2].strip()
	# if error, raise and print output    
	printOutput(output)
	raise ViriError("Did not find Data Read Errors string in output ")
    
    def  gc(self,devPart):
       option1 = "vgcdrive%s"%get_device_letter_part1(devPart)
       cmd = "%s %s/%s/gc"%(VGCPROC,PROC,option1)
       output =  self.run(option1,"gc")
       
       return parseSplit(output[1:],add_underscore = 1)
    
    def is_gc_running(self,devPart):
	
	    #for c in range(1,3):
	    bmoved1 = int(self.gc(devPart)['gc_bytes_moved'])
	
	    if bmoved1 == 0:
	        trace_info("GC not triggered, found gc bytes moved as '%s'"%bmoved1)
	        return False
	    
	    if bmoved1 > 0:
		trace_info("GC seem triggered, found gc bytes moved as '%s'"%bmoved1)
	        return True
	    
	    #    sleep_time(3,"after finding gc stats")
	    #    bmoved2 = int(self.gc(devPart)['gc_bytes_moved'])
	    #    
	    #    diff = bmoved2 -  bmoved1
	    #    if bmoved2 > bmoved1:
	    #	trace_info("Found diff '%i', intial value '%i',final valued '%i' gc seem to be triggered %s"%(diff,bmoved1,bmoved2,devPart))
	    #	return True
	    #    
	    #    trace_info("Found diff '%i', intial value '%i',final valued '%i' gc doesnt seem to be triggered %s"%(diff,bmoved1,bmoved2,devPart))	    
	    #
	    #    #trace_info("Found diff '%i' gc  doesnt seem to be triggered %s"%(diff,devPart))
	    #	
	    #    return False
	    
	
    def get_ue_errors(self,devPart,errType = "UE"):
	"""
	
	"""
        arr = get_device_letter_part(devPart)
        
        # concat a + 0 as a0
        dev = arr[0] + arr[1]
        
        # make vgdrivea0
        dev = "vgcdrive" + dev
        
        
        out = self.run(dev,"bb_stats",grep = errType)
        
        printOutput(out)
        return parse_ue_errors(out,errType = errType)
    
    def chk_if_ue_errors(self,devPart):
        
        """ raises exception if ue errors on device Passed"""
        (errors,errString) = self.get_ue_errors(devPart)
        
        if errors > 0:
            
            raise ViriError("Found UE errors '%i' on device '%s',error details '%s'"%(errors,devPart,errString))
        
        trace_info("No UE errors seem to be on device '%s'"%devPart)
        
        return 1
        
    def getSlChSubCh(self,devPart,duNo,subChNo):
       
        """ subChanNo start from 0"""
        dev1,part = get_device_letter_part(devPart)
        device = get_vgc_dev_from_part(devPart)
        dumap = self.getDuMap(device)
       
        key = part + duNo
       
        array = dumap[key][int(subChNo)]
       
        return array
   
    def unrecoverable_errors(self,devPart):
	
	
	arr = get_device_letter_part(devPart)
        
        # concat a + 0 as a0
        dev = arr[0] + arr[1]
        
        # make vgdrivea0
        dev = "vgcdrive" + dev
	
	out = self.run(dev,"info",grep = "Total uncorrectable errors")
	
	line = out[1]
	
	#line = "Total uncorrectable errors (UNRECOVERABLE) = 1"
	
	return int(getSingleSplitRight(line,delimit = "="))
	   
    def getSlChSubChMask(self,devPart,duNo,subChNo):
       
        #(sl,ch,subCh
        trace_info("Getting sl ch subch for device '%s' duNo '%s', subch '%s'"%(devPart,duNo,subChNo))
        sl,ch,subCh = self.getSlChSubCh(devPart,duNo,subChNo)
       
        trace_info("Found sl '%s' ch '%s' subch '%s'"%(sl,ch,subCh))
        return (getMask(sl),getMask(ch),getMask(subCh))
    
    def getDuMap(self,device):
       drvLetter = get_device_letter(device)
       o = self.host.run_command_chk_rc("%s  /proc/driver/virident/vgcsch%s/dumap "%(self.vgcProcStr,drvLetter))
       
       out = o['output']
       
       return parseDuMap(out[1:])
    
    def get_pci_id(self,device ):
	
	drvLetter = get_device_letter(device)
	 
	 
	out = self.run("vgcport%s"%drvLetter,"info")
	
	dict1 = parseSplit(out,delimit = "=")
	for k in dict1.keys():
	    if re.search("PCI",k):
		pci_id = dict1[k]
		#k_a = getSingleSplitRight(k,delimit = "=")
		#print k_a[1]
	
	return pci_id
    
    def vport_diags(self,device):
	 drvLetter = get_device_letter(device)
	 #/usr/lib/vgc/vgcproc /proc/driver/virident/vgcporta/diags
	 
	 return self.run("vgcport%s"%drvLetter,"diags")
	 

    def get_power(self,device):
	
	
	for l in self.vport_diags(device):
	    
	    if re.search("Power of card",l):
		
		power = getSingleSplitRight(l,delimit = "=")
		
		# remove W and white spaces
		return power.replace('W','').strip()
		
        
	return "N/A"
	 
    
   
        
    
