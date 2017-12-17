#from ViriImports import *
#from Host import *
class raid:
    def __init__(self,host,devicesPart):
        self.host        = host
        self.devicesPart = devicesPart
        self.raidCreated  = 0
    
    def removeRaid(self):
        
        for cmd in ["mdadm --stop /dev/md0", "mdadm --remove /dev/md0"]:
            self.host.run_command(cmd)
        
        for disk in self.devicesPart:
            self.host.run_command("mdadm --zero-superblock %s"%disk)
        
        return 1
 
    def createRaid(self,raidLevel):
        
        
        #mdadm --create /dev/md0 --level=mirror --raid-devices=2 /dev/vgca0 /dev/vgcb0
        
        cmd = "mdadm --create /dev/md0 --level=%s --raid-devices=%i "%(raidLevel,len(self.devicesPart))
        
        for disk in self.devicesPart:
		# append string
		cmd = cmd + disk + " "
        
        #print cmd
        #sys.exit(1)
        
        o = self.host.run_command(cmd,exp_out_prompt = ["Continue creating array","yes"])
        
        rc =  o['rc']
        out = o['output']
        
        if rc != 0:
           err = "Couldn't run the command '%s', found return code as '%i'"%(cmd,rc)
           trace_error(err)

           print "details = ("
           for l in out:
               print l
           print ")"
           out.insert(0,err)
           raise CommandError(out)
        
        (foundDevices,noDevices,foundRaidLevel) = self.get_mdadm_detail_raid_devices()
        
        #foundDevices  = ['/dev/vgca0','/dev/vgcb1']
        isArraysEqual(foundDevices, self.devicesPart)
        
        str = "Found raid level '%s', expected '%s'"%(raidLevel,foundRaidLevel)
        if raidLevel == foundRaidLevel:
	    trace_info(str)
	else:
	    raiseViriError(str)
        
        self.raidCreated = 1
        return 1

    def get_mdadm_detail(self):
	
	""" return {'Chunk Size': '512K', 'Working Devices': '2', 'Raid Devices': '2', 
	'Raid Level': 'raid0', 'Creation Time': 'Sat Dec  8 17', 'devices': ['/dev/vgca0', '/dev/vgcb0'], 'UUID': 'd40a3e25', 'Array Size': '3255532544 (3104.72 GiB 3333.67 GB)', 'Failed Devices': '0', 'State': 'clean', 'Version': '1.2', 'Events': '0', 'Persistence': 'Superblock is persistent', '/dev/md0': '', 'Spare Devices': '0', 
	'Name': 'sqa12-ubuntu1204', 'size': '3333.67', 'Active Devices': '2',
	'Total Devices': '2', 'Update Time': 'Sat Dec  8 17'}"""
	
        # mdadm: cannot open /dev/md0: No such file or directory
        
        try:
          o = self.host.run_command_chk_rc("mdadm --detail /dev/md0")
          return parse_mdadm_detail(o['output'])
        except CommandError:
	  return None
	  
    def is_raid_present(self):
	dict =  self.get_mdadm_detail()
	
	if not dict:
	    return False
	
	return True
 
    def stopRaid(self):
	
	if not self.raidCreated:
	    raise ViriError("raid not created but stop raid called")
	
	self.host.run_command_chk_rc("mdadm --stop /dev/md0")
	
	if not self.is_raid_present():
	    trace_info("raid seem to have stopped sucessfully")
	    return 1
	
	print self.get_mdadm_detail()
	raise ViriError("Failed to stop raid")
	
    def get_mdadm_detail_raid_devices(self):
	""" returns devices details and no of devices in raid"""
	
	dict = self.get_mdadm_detail()
	
	if not dict:
	    return None
	
	#print dict
	devices = dict['devices']
	raidLevel = dict['Raid Level']
	
	# remove raid from raid0
	m = re.search("raid(\d+)",raidLevel)
	raidLevel = m.group(1)
	
	
	return (devices,len(devices),raidLevel)
	
	
        
        
        
        
        
        
