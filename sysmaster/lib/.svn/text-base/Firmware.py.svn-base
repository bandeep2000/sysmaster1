from ViriImports import *
import subprocess

VGCCONFIG = 'vgc-config'
SSH = 'sshpass -p 0011231 ssh root@'

class firmware:

	def __init__(self,host,firmware_directory = '/dev/null'):
       
		self.host = host
		self.vm = vgcMonitor(self.host)

		self.host.clear_dmesg_syslogs()

		self.firmware_directory = firmware_directory

		self.vgcupdate = firmware_directory + '/vgc-update.sh'
		self.vgcdowngrade = firmware_directory + '/vgc-downgrade.sh'

		self.expected_bootrom = []
		self.expected_firwmare = []

		self.firmware61033_60174 = ''
		self.firmware52879 = ''
		self.firmware49755 = ''

	def vgcUpdateHelp(self):

		trace_info("running vgc-update.sh --help")	
		comm = "%s --help" % self.vgcupdate
     		run = self.host.run_command(comm)
		output = run['output']
		outputerr = run['outputerr']
		rc = run['rc']
		print run

		if rc != 0:
			raise ViriError("vgc-update.sh rc is %s" % rc)


		trace_info("expecting the following FMII:")	

		expect_FM2 = ['\tvgc-update.sh    [-d|--drive <drive>] [-y|--yes] [-F|--force]\n', '\tvgc-update.sh    [-O|--boot-rom] [-d|--drive <drive>]\n', '\tvgc-update.sh    [-e|--erase-boot-rom] [-d|--drive <drive>]\n', '\tvgc-update.sh    -l|--list\n', '\tvgc-update.sh    -h|--help\n', '\tvgc-update.sh    update firmware on all drives\n', '\t-d | --drive          :  drive name eg. vgc[a,b,c...] \n', '\t-O | --boot-rom       :  update boot rom\n', '\t-e | --erase-boot-rom :  erase boot rom\n', '\t-l | --list           :  list information of drives\n', '\t-y | --yes            :  firmware update proceeds without user confirmation\n', '\t-F | --force          :  forced firmware update\n', '\t                         this can load the firmware even if target firmware version and current firmware version are same\n']

		print expect_FM2

		trace_info("expecting the following FMIII:")	

		expect_FM3 = ['\tvgc-update.sh    [-d|--drive <drive>] [-y|--yes] [-F|--force]\n', '\tvgc-update.sh    [-O|--boot-rom] [-d|--drive <drive>]\n', '\tvgc-update.sh    [-e|--erase-boot-rom] [-d|--drive <drive>]\n', '\tvgc-update.sh    -l|--list\n', '\tvgc-update.sh    -h|--help\n', '\tvgc-update.sh    update firmware on all drives\n', '\t-d | --drive          :  drive name e.g. vgc[a,b,c...] \n', '\t-O | --boot-rom       :  update boot rom\n', '\t-e | --erase-boot-rom :  erase boot rom\n', '\t-l | --list           :  list information of drives\n', '\t-y | --yes            :  firmware update proceeds without user confirmation\n', '\t-F | --force          :  forced firmware update\n', '\t                         this can load the firmware even if target firmware version and current firmware version are same\n']

		print expect_FM3

		trace_info("detected the following:")			

		print outputerr

		if expect_FM3 == outputerr or expect_FM2 == outputerr:
			trace_success("update help expected == update help detected")
		else:
			raise ViriError("update help expected != update help detected")

	def getFirmware(self,device):

		devDetails = self.vm.getDeviceDetails(device)
		firmware = devDetails['rtl']

		return firmware

	def getBootROM(self,device):

		devDetails = self.vm.getDeviceDetails(device)
		bootrom = devDetails['boot_rom']

		return bootrom 

	def getBootability(self,device):

		devDetails = self.vm.getDeviceDetails(device)
		bootability = devDetails['bootable']

		return bootability

	def runCommand(self,comm):
		
		trace_info("running command, %s" % comm)

		p = subprocess.Popen(comm, shell=True, stderr=subprocess.PIPE)
 
		while True:
			out = p.stderr.read(1)
			if out == '' and p.poll() != None:
				break
			if out != '':
				sys.stdout.write(out)
				sys.stdout.flush()

		rc = p.wait()

		return rc

	def updateForce(self):

		trace_info("running vgc-update.sh -F")
		
		comm = "%s%s %s -F -y" % (SSH, self.host.name, self.vgcupdate)
		print comm

		p = subprocess.Popen(comm, shell=True, stderr=subprocess.PIPE)
 
		while True:
			out = p.stderr.read(1)
			if out == '' and p.poll() != None:
				break
			if out != '':
				sys.stdout.write(out)
				sys.stdout.flush()

		rc = p.wait()

		if rc != 0:
			raise ViriError("vgc-update.sh -F rc is %s" % rc)
		else:
			trace_success("vgc-update.sh -F rc is %s" % rc)

	def eraseBootROM(self,device):

		trace_info("running vgc-update.sh -e -d %s"%device)
		
		comm = "%s%s %s -e -d %s -y" % (SSH, self.host.name, self.vgcupdate, device)
		print comm

		p = subprocess.Popen(comm, shell=True, stderr=subprocess.PIPE)
 
		while True:
			out = p.stderr.read(1)
			if out == '' and p.poll() != None:
				break
			if out != '':
				sys.stdout.write(out)
				sys.stdout.flush()

		rc = p.wait()

		if rc != 0:
			raise ViriError("vgc-update.sh -e -d %s rc is %s" % (device,rc))
		else:
			trace_success("vgc-update.sh -e -d %s rc is %s" % (device,rc))

	def programBootROM(self,device):

		trace_info("running vgc-update.sh -O -d %s" % device)
		
		comm = "%s%s %s -O -d %s -y" % (SSH, self.host.name, self.vgcupdate, device)
		print comm

		p = subprocess.Popen(comm, shell=True, stderr=subprocess.PIPE)
 
		while True:
			out = p.stderr.read(1)
			if out == '' and p.poll() != None:
				break
			if out != '':
				sys.stdout.write(out)
				sys.stdout.flush()

		rc = p.wait()

		if rc != 0:
			raise ViriError("vgc-update.sh -O -d %s rc is %s" % (device,rc))
		else:
			trace_success("vgc-update.sh -O -d %s rc is %s" % (device,rc))

	def compareFirmware(self,device):

		trace_info("comparing firmware")

		expected = self.getExpectedFirmware()
		detected = self.getFirmware(device)
		
		if detected in expected:
			trace_success("expected firmware == detected firmware, %s, for card %s" % (detected,device))
		else:
			raise ViriError("expected firmware != detected firmware for card %s" % device)
		
		return 1

	def compareBootROM(self,device):

		trace_info("comparing boot rom")
		
		expected = self.getExpectedBootROM()
		detected = self.getBootROM(device)

		if detected == 'not applicable':
			trace_info("card does not support boot rom")
			return 1

		if detected in expected:
			trace_success("expected boot rom == detected boot rom, %s, for card %s" % (detected,device))
		else:
			raise ViriError("expected boot rom != detected boot rom for card %s" % device)

		return 1

	def getExpectedBootROM(self):

		comm = "cd %s && ls *.romx | cut -d. -f1 | sed 's/[^0-9]//g'" % self.firmware_directory
		run = self.host.run_command(comm)
		output = run['output']

		for line in output:
			self.expected_bootrom.append(line)

		return self.expected_bootrom

	def getExpectedFirmware(self):

		comm = "cd %s && ls *.rbf* | awk -F'svn' '{print $2}' | sed 's/[^0-9]//g'" % self.firmware_directory 
		run = self.host.run_command(comm)
		output = run['output']

		for line in output:
			self.expected_firwmare.append(line)

		return self.expected_firwmare

	def setBootability(self,device,enable_disable):

		trace_info("setting bootability for %s to %s" % (device,enable_disable))

		detected = self.getBootROM(device)

		if detected == 'not applicable':
			trace_info("card does not support boot rom")
			return 1
		
		comm = "%s -d %s -b %s -f" % (VGCCONFIG, device, enable_disable)
		run = self.host.run_command(comm)

		print run
		rc = run['rc']
		
		if rc == 0:
			trace_success("%s, rc is %s" % (comm,rc))
		else:
			raise ViriError("%s, rc is %s" % (comm,rc))

	def setFirmware61033_60174(self, path): 
		
		self.firmware61033_60174 = path

	def setFirmware52879(self,path):
		
		self.firmware52879 = path

	def setFirmware49755(self,path):
		
		self.firmware49755 = path
	
	def setFirmwareDirectory(self,path):

		self.firmware_directory = path

	def getFirmware61033_60174(self):
		
		return self.firmware61033_60174

	def getFirmware52879(self):
		
		return self.firmware52879

	def getFirmware49755(self):
		
		return self.firmware49755

	def uninstallVGC(self):

		trace_info("uninstalling vgc")

		comm = "%s%s \"rpm -qa | grep vgc | xargs rpm -e\"" % (SSH, self.host.name)

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" % comm)

		return 1

	def installVGC(self,path):

		trace_info("installing vgc")

		comm = "%s%s \"cd %s; rpm -ivh kmod* vgc-utils*\"" % (SSH, self.host.name, path) 

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" % comm)

		self.host.reboot()

		return 1

	def resetCard(self,device):

		vm = vgcConf(self.host)
		vm.resetCard(device)

		return 1

	def flash61033_60174(self):

		trace_info("flashing 61033/60174")

		comm = "%s%s %s/vgc-firmware*/vgc-update.sh -y -F" % (SSH, self.host.name, self.firmware61033_60174)

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" %comm)

		return 1

	def downgrade61033_60174(self, device):

		trace_info("downgrading from 61033/60174")

		comm = "%s%s %s/vgc-firmware*/vgc-downgrade.sh -y -F -d %s" % (SSH, self.host.name, self.firmware61033_60174, device)

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" %comm)

		return 1

	def flash52879(self):

		trace_info("flashing 52879")

		self.host.stopVgcDriver()

		comm = "%s%s %s/vgc-firmware*/vgc-update.sh -y -F" % (SSH, self.host.name, self.firmware52879)

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" % comm)

		return 1

	def flash49755(self):

		trace_info("downgrading to 49755")

		self.host.stopVgcDriver()

		comm = "%s%s \"cd %s/vgc-firmware*; ./vgc-downgrade.sh -y -F\"" % (SSH, self.host.name, self.firmware52879)

		rc = self.runCommand(comm)
		if rc != 0:
			raise ViriError("%s, rc != 0" % comm)

		return 1
