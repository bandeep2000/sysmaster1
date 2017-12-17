from Kernels import *
from Util import *
from VgcUtils.Vsan.Vcache import *

PASS = "Passed"
FAIL = "Failed"
class kernelInstall():
    
    def __init__(self,host):
        self.host = host
        
        # initialize kernels array
        self.kernelsArray = ""
	self.setArray = 0
    
    def set_kernels_array_and_get_oldest_kernel(self):
        """
        Gets oldest kernel from Array
        
        """
        
        linuxFlavor = self.host.cat_etc_issue()
        #Initialize kernels and oldest kernel from Array
        if linuxFlavor == "redhat6":
            kernels = rh6kernels
            oldestKernelFromArr = kernels[0]
            # convert into rigth format and store in the same variable
            oldestKernelFromArr = self.host.getKernelNoRpm(oldestKernelFromArr)
        elif linuxFlavor == "redhat5":
            kernels = rh5kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = self.host.getKernelNo86(oldestKernelFromArr)
        elif linuxFlavor == "sles11sp1":
            kernels = sles11sp1Kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = get_sles_kernel_from_rpm(oldestKernelFromArr)
        elif linuxFlavor == "sles11sp2":
            kernels = sles11sp2Kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = get_sles_kernel_from_rpm(oldestKernelFromArr)
        elif linuxFlavor == "sles11":
            kernels = sles11Kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = get_sles_kernel_from_rpm(oldestKernelFromArr)
        elif linuxFlavor == "sles10sp4":
            kernels = sles10sp4Kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = get_sles_kernel_from_rpm(oldestKernelFromArr)
        elif linuxFlavor == "sles10sp3":
            kernels = sles10sp3Kernels
            oldestKernelFromArr = kernels[0]
            oldestKernelFromArr = get_sles_kernel_from_rpm(oldestKernelFromArr)
        else:
            print "ERR: Unsupported linux flavr '%s',please use it for RH5/RH6/sles only"%linuxFlavor
            sys.exit(1)
        
	self.setArray = 1
        self.kernelsArray = kernels   
        return oldestKernelFromArr
 
    def install_lowest_kernel(self, ):
        
        currKernel =  self.host.get_kernel_ver()
        
        oldestKernelFromArr = self.set_kernels_array_and_get_oldest_kernel()

        if oldestKernelFromArr != currKernel:
            print "INFO:Host is not at the oldest kernel found '%s' , expected '%s'"%(currKernel,oldestKernelFromArr)
            self.host.upgradeKernel(self.kernelsArray[0])
            return True
       
	print "INFO:Host is at the oldest kernel found '%s' , expected '%s'"%(currKernel,oldestKernelFromArr)
        return True    
    
    def run_commands_after_upgrade(self):
	
	self.host.run_command_chk_rc("vgc-monitor",verbose = 1)
	
	# do some io also, note uses device as /dev/vgca0 TODO
	self.host.run_command_chk_rc("dd if=/dev/zero of=/dev/vgca0 bs=1G count=1")
	
	return 1
        #  TO DO, the following is for vcache
       
        self.host.installBuild(build = "V4.57997" ,emc = 0, releaseVer = "1.1.FC",stats = 0,rdma = 0 )
        
        backend = "/dev/sdb"
        mode = ""
        size = "30"
        dirty_threshold = size
        flush_period = "0"
        fe = "/dev/vgca0"
        vcache_name = "wb"

        vc = vgcCache(self.host,vcache_name,fe,backend, size ,dirty_threshold =dirty_threshold,
              flush_period = flush_period)
        
        vc.deleteAll()
        vc.enable()
        vc.create()
	vc.get_details()
        vc.deleteAll()
    
    def print_rpm_test_status(self,arr):
	""" function to print array,failed/pass"""
	print "-" * 85
	print "| Kernel rpm |         Reason  Pass/Fail       |       Status        | "
	print "-" * 85
	for line in arr:
		print line
		
	print "-" * 85
	trace_info("Total Kernels Tested: %i"%len(arr))
	print "-" * 85
	
	return 1
    
    def upgrade_all_kernels(self, ):
        """
	inputs      : None
	return      : 1 on success, raises on failures
	description : installs lowest kernel based on linux version and start
	upgrading to kernels , runs command as given after upgrading 

	"""


        # configure 
        if self.install_lowest_kernel():
            pass
	
        
        # run command initially
	self.run_commands_after_upgrade()
		
	#self.set_kernels_array_and_get_oldest_kernel()
        
	passed_rpms = []
	
	# exit if array is not set that initalizes kernels to be tested
	if self.setArray == 0:
	    print "ERR: array not set for kernels, please call that function to set first";sys.exit(1)
	    
	
	reason_passed = "kernel from uname -r matched"
	
        for rpm in self.kernelsArray[1:]:

            trace_info_dashed("Using kernel rpm '%s'"%rpm)
          
	    # try upgrade the kernel first
	    try:
		self.host.upgradeKernel(rpm)
		
	    except Exception,e:
		# change reason passed if failed
		reason_passed = "uname -r match/other some other reason"
		passed_rpms.append("| '%s' | %s | Failed |"%(rpm,reason_passed))
                self.print_rpm_test_status(passed_rpms)
		print e
		trace_error_dashed("Upgrade kernel test case failed,after executing commands")
		sys.exit(1)
		
	    # try running command after kernel upgrade
            try:
		self.run_commands_after_upgrade()
	    except Exception,e:
		trace_error("Some Error happend while running command after kernel upgrade")
		trace_info("Kernels rpms tested so far:")
		
		#append passed rpm first
		passed_rpms.append("| '%s' | %s | Passed |"%(rpm,reason_passed))
		self.print_rpm_test_status(passed_rpms)
		trace_error("Failed at kernel rpm %s"%rpm)
		
		trace_error(e)
		trace_error_dashed("Upgrade kernel test case failed,after executing commands")
		sys.exit(1)
	
	    trace_info_dashed("Done upgrading to kernel rpm %s"%rpm)
	    passed_rpms.append("| '%s' | %s | Passed |"%(rpm,reason_passed))
	
	# if it reaches here test passed    
	self.print_rpm_test_status(passed_rpms)
	trace_success_dashed("Kernel upgrade Test passed")
	
	return 1
            
        
    
