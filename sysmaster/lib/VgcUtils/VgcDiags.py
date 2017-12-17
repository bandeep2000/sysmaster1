#from ViriImports import *
from VgcUtils import *
from Trace import *

"""
from Utilities.VgcBeacon import *
from HostLinux import *

h = hostLinux(sys.argv[1])
v = vgcDiags(h)
v.run(options = "--verbose")

"""

DIAGS_FILE = "vgc.diags.tar"

class vgcDiags(vgcUtils):
	
    def __init__(self,host):
        
	self.vgcDiagsStr = "vgc-diags" # vgc-diags command string
	
	vgcUtils.__init__(self,host)

    def run(self,options = ""):
        """ options can be --verbose or /dev/vgca"""

        output_diags_file = DIAGS_FILE
	  
        # if -p diags_dir
	if re.search("-p\s+(\S+)",options):
                # get the directory which space followed
	        m = re.search("-p\s+(\S+)",options)
		output_dir = m.group(1)
                output_diags_file = "%s/%s"%(output_dir,DIAGS_FILE)

	# CLEAN UP
        if self.host.if_file_exists(output_diags_file):
	        trace_info("Diags files exists, removing")
	        self.host.run_command_chk_rc("rm -rf %s"%output_diags_file)
	self.host.run_command("rm -rf vgcshow/")

	# call the parent method
	vgcUtils.run(self,cmd = "vgc-diags",verify_regex = "vgc-diags",options = options)
        if not self.host.if_file_exists(output_diags_file):
           raise ViriError("Did not find the diags file %s after running vgc-diags"%output_diags_file)

        trace_info("Untarring file, '%s'"%output_diags_file)
	self.host.run_command_chk_rc("tar -xvf %s"%output_diags_file)
	self.host.run_command_chk_rc("ls --color=none vgcshow")

	return 1

    def runAllOptions(self):
         output_diags_dir = "vgc.diags.dir"
         # 
	 for options in ["-p %s"%output_diags_dir,'vgca',"vgca -p %s"%output_diags_dir]:
            self.run(options = options)
	 return 1

    def runVerbose(self):
	
	vgcUtils.run(self,"vgc-diags","vgc-diags",options = "--verbose")
	return 1
	
	
	


       
	    
       
