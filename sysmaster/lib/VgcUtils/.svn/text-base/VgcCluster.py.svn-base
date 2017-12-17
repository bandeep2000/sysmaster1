 #!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
from Specs import *
from VirExceptions import *
from VgcUtils import *
VSAN_ENABLED = "enabled"
VSAN_DISABLED = "disabled"

"""

Create Share example:
[root@cperf-14 ~]# vgc-cluster share-create -S cperf-15 -d /dev/vgca0 -A
cperf-14 -N "Net 1 (IB)"  -s 60 -n share1
VSHARE_CREATE0000000732
Request Succeeded
[root@cperf-14 ~]# vgc-cluster share-delete -n space1
Share object "space1" does not exist.
[root@cperf-14 ~]# vgc-cluster share-delete -n share1
VSHARE_DELETE0000000733
Request Succeeded
[root@cperf-14 ~]# vi


"""

# default sector
EXPECTED_SECTOR = "512"

class vgcCluster(vgcUtils):
	
    def __init__(self,host):
	#self.vgcConfStr = "vgc-config" # vgc-config command string
        vgcUtils.__init__(self,host)
    
    def space_list(self):
        out = self.host.run_command_get_output("vgc-cluster space-list")
	return parse_space_list(out)
    
    def get_space_state(self,space,expected_state = None,tries = 20):
        
	
	try:
	   space_state = self.space_list()[space]
	except KeyError:
	   print "ERROR: Space '%s' not found"%space
	   raise
	
	if not expected_state: return space_state

        for c in range(1,tries):
	   if self.space_list()[space] == expected_state:
		   return True
           print "Waiting to get expected state '%s', found '%s'"%(expected_state,space_state)
	   time.sleep(10)
	   continue
	else:
           print "Did not get  expected state '%s', found '%s'"%(expected_state,space_state)
	   raise

    def domain_list(self):
        out = self.host.run_command_get_output("vgc-cluster domain-list")
	return parse_domain_list(out)
    
    def get_machines_in_domain(self): 
        print self.domain_list().keys()

	
