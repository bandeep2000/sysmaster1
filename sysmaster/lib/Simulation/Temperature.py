from ViriImports import *
import time

VGCDPTSETTING = "vgc-dpt-settings"

class tempSim:

	def __init__(self,host):
       
		self.host = host
		self.enabledTemp = 0
		self.host.clear_dmesg_syslogs()

		self.vm = vgcMonitor(self.host)
       
	def enableTemperatureSim(self):

		trace_info("ENABLING TEMPERATURE SIMULATION")

		time.sleep(20)	
    
		if self.host.ifVgcRpmLoaded("stats") != 1:
			raise ViriError("stats build must be install")

		self.host.stopVgcDriver()
		self.host.run_command_chk_rc("echo -e 'options vgcv2 sim_gw_temperature=1\noptions vgcv3 sim_gw_temperature=1' > /etc/modprobe.d/vgc.conf")
		self.host.startVgcDriver()

		o = self.host.run_command_chk_rc("cat /sys/module/vgcv2/parameters/sim_gw_temperature /sys/module/vgcv3/parameters/sim_gw_temperature | awk '{sum+=$1} END {print sum}'")
		out = o['output']
		print out
		if out[1] != '2':
			raise ViriError("enabling temperature simulation failed in /sys/module/vgcv*/parameters/sim_gw_temperature")

		self.enabledTemp = 1

		return 1

	def disableTemperatureSim(self):
		
		trace_info("DISABLING TEMPERATURE SIMULATION")
    
		if self.host.ifVgcRpmLoaded("stats") != 1:
			raise ViriError("stats build must be install")

		self.host.stopVgcDriver()
#		self.host.run_command_chk_rc("sed -i 's/sim_gw_temperature=1/sim_gw_temperature=0/' /etc/modprobe.d/vgc.conf")
		self.host.run_command_chk_rc("rm -f /etc/modprobe.d/vgc.conf")
		self.host.startVgcDriver()

		o = self.host.run_command_chk_rc("cat /sys/module/vgcv2/parameters/sim_gw_temperature /sys/module/vgcv3/parameters/sim_gw_temperature | awk '{sum+=$1} END {print sum}'")
		out = o['output']
		print out
		if out[1] != '0':
			raise ViriError("disabling temperature simulation failed in /sys/module/vgcv*/parameters/sim_gw_temperature")

		self.enabledTemp = 0

		self.host.clear_dmesg_syslogs()

		return 1

	def getVGCTemperature(self,device):

		devDetails = self.vm.getDeviceDetails(device)
		vgc_temp = devDetails['temp']

		return vgc_temp

	def verifySetTemperature(self,temp,device):

		if self.getVGCTemperature(device) != str(temp):
			raise ViriError("set temp != detected temp")
		
		return 1

	def setTemperature(self,temp,device):
       
#		if self.enabledTemp == 0:
#			raise ViriError("temperature simulation not enabled")
       
		drvLetter= get_device_letter(device)
		cmd = "echo \"%s\" | %s -w vgcport%s/gwtemp"%(temp,VGCPROC,drvLetter)
		self.host.run_command_chk_rc(cmd)
		
		self.verifySetTemperature(temp,device)

		return 1

	def isTemperatureSafe(self,device):

		devDetails = self.vm.getDeviceDetails(device)
		
		temp_s = devDetails['temp_s']
		
		trace_info("is temperature safe?")
		if temp_s == 'Safe':	
			trace_success("temperature is safe")
		else:
			trace_error("temperature is not safe")
			raise ViriError("temperature is not safe")

	def getVGCprocFPGAtemp(self,device):

		device_letter = get_device_letter(device)	
		temp_array = []		

		comm = "/usr/lib/vgc/vgcproc /proc/driver/virident/vgcport%s/diags | egrep 'Temperature of card| Fpga'" % (device_letter)
		run = self.host.run_command(comm)
		print run
		output = run['output']
		output.pop(0)

		for line in output:
			temp = line.split("= ")[1].split()[0]	
			temp_array.append(temp)

		reporting_temp = temp_array[0]

		for temp_element in temp_array:
			if temp_element > reporting_temp:
				raise ViriError("fpga temp is greater than reporting temp")
		
		temp_match = 0
		for temp_element in temp_array:
			if temp_element == reporting_temp:
				temp_match = 1
				break
		if temp_match == 0:
			raise ViriError("fpga temp does not match reporting temp")

		return reporting_temp

	def compareVGCmonFPGAtemp(self,device):
	
		fpga_temp = self.getVGCprocFPGAtemp(device)
		trace_info("fpga temp is %s"%fpga_temp)
		
		devDetails = self.vm.getDeviceDetails(device)
		vgc_mon_temp = devDetails['temp']
		trace_info("vgc-monitor temp is %s"%vgc_mon_temp)

		if vgc_mon_temp != fpga_temp:
			raise ViriError("fpga temp != vgc-monitor temp")
		
		return 1

	def actionRequiredNotNone(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		action_required = devDetails['actionRequired']

		trace_info("expecting action required is not None")

		if action_required != 'None':
			trace_success("action required is: %s"%action_required)
		else:
			raise ViriError("action required should not be None")			

		return 1

	def actionRequiredNone(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		action_required = devDetails['actionRequired']

		trace_info("expecting action required is None")

		if action_required == 'None':
			trace_success("action required is: %s"%action_required)
		else:
			raise ViriError("action required should be None")			

		return 1

	def tempThrottleNotInactive(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		temp_throttle = devDetails['temp_throttle']

		trace_info("expecting temp throttle is not Inactive") 
		
		if temp_throttle != 'Inactive':
			trace_success("temp throttle is: %s"%temp_throttle)
		else:
			raise ViriError("temp throttle should not be Inactive")

		return 1

	def tempThrottleInactive(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		temp_throttle = devDetails['temp_throttle']

		trace_info("expecting temp throttle is Inactive") 
		
		if temp_throttle == 'Inactive':
			trace_success("temp throttle is: %s"%temp_throttle)
		else:
			raise ViriError("temp throttle should be Inactive")

		return 1

	def cardStateNotNormal(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		card_state = devDetails['cardStateDetails']

		trace_info("expecting card state is not Normal")

		if card_state != 'Normal':
			trace_success("card state is %s"%card_state)
		else:
			raise ViriError("card state should not be Normal")

		return 1

	def cardStateNormal(self, device):

		devDetails = self.vm.getDeviceDetails(device)
		card_state = devDetails['cardStateDetails']

		trace_info("expecting card state is Normal")

		if card_state == 'Normal':
			trace_success("card state is %s"%card_state)
		else:
			raise ViriError("card state should be Normal")

		return 1

	def isCardStateWarning(self,device, warning_only = 0):
		
		devDetails = self.vm.getDeviceDetails(device)
		card_status = devDetails['state']
		trace_info("expecting card state Warning")
		trace_info("card state is now: %s"%card_status)

		if card_status != "Warning":
			raise ViriError("card state should be warning")
		else:
			trace_success("card state is Warning")

		if warning_only == 1:
			return 1

		action_required = devDetails['actionRequired']

		trace_info("expecting action required is not None")

		if action_required != 'None':
			trace_success("action required is: %s"%action_required)
		else:
			raise ViriError("action required should not be None")			

		card_state = devDetails['cardStateDetails']

		trace_info("expecting card state is not Normal")

		if card_state != 'Normal':
			trace_success("card state is %s"%card_state)
		else:
			raise ViriError("card state should not be Normal")

		temp_throttle = devDetails['temp_throttle']

		trace_info("expecting temp throttle is not Inactive") 
		
		if temp_throttle != 'Inactive':
			trace_success("temp throttle is: %s"%temp_throttle)
		else:
			raise ViriError("temp throttle should not be Inactive")

		card_serial = devDetails['serial']
		
		trace_info("checking for messages in /var/log/messages for %s"%card_serial)

		comm = "grep %s /var/log/messages | grep 'reached warning threshold' | tail -n 1" % (card_serial)
		run = self.host.run_command(comm)
		print run
		
		if run['rc'] != 0:
			raise ViriError("/var/log/messages did not report reached warning threshold for %s"%card_serial)

		trace_info("checking for messages in dmesg for %s"%card_serial)

		comm = "dmesg | grep %s | grep 'reached warning threshold' | tail -n 1" % (card_serial)
		run = self.host.run_command(comm)
		print run
		
		#if run['rc'] != 0:
		#	raise ViriError("/var/log/messages did not report reached warning threshold for %s"%card_serial)
		return 1

	def isCardStateGood(self,device):
		
		devDetails = self.vm.getDeviceDetails(device)
		card_status = devDetails['state']
		trace_info("expecting card state Good")
		trace_info("card state is now: %s"%card_status)

		if card_status != "Good":
			raise ViriError("card state should be good")
		else:
			trace_success("card state is Good")

		return 1

	def getWarningTemperature(self,device):

		drive_letter = get_device_letter(device)

		comm = "%s vgcsch%s/dm | grep 'Warning Threshold'" % (VGCPROC, drive_letter)
		o = self.host.run_command_chk_rc(comm)
		print o
		output = o['output']
		
		vgcschdm_warning = output[1].split(':')[1]	

		return vgcschdm_warning

	def setWarningTemperature(self,temp,device,expect_rc = 0,verify = 1):

		comm = "%s -d %s -w %s" % (VGCDPTSETTING, device, temp)	
		
		try:
			o = self.host.run_command_chk_rc(comm)
			print o
			if o['rc'] != 0:
				raise ViriError("could not set warning temperature")
			else:
				trace_success("warning temperature set to %s"%temp)
		except:
			if expect_rc != 0:
				trace_success("invalid temperature setting was disallowed")
				return 1
			else:
				raise ViriError("invalid temperature setting was allowed")

		drive_letter = get_device_letter(device)

		if verify == 1:
			if self.getWarningTemperature(device) != str(temp):
				raise ViriError("set temperature does not match vgcsch%s/dm"%drive_letter)
			else:
				trace_success("vgcsch%s/dm warning temp == set warning temp"%drive_letter)
		
		return 1

	def setThrottleTemperature(self,temp,device, verify = 1 ):

		comm = "%s -d %s -t %s" % (VGCDPTSETTING, device, temp)	
		
		o = self.host.run_command_chk_rc(comm)
		print o
		if o['rc'] != 0:
			raise ViriError("could not set throttle temperature")
		else:
			trace_success("throttle temperature set to %s"%temp)

		if verify == 1:

			drive_letter = get_device_letter(device)
			comm = "%s vgcsch%s/dm | grep 'Throttle Threshold'" % (VGCPROC, drive_letter)
			o = self.host.run_command_chk_rc(comm)
			print o
			output = o['output']
			
			vgcschdm_throttle = output[1].split(':')[1]	

			if vgcschdm_throttle != str(temp):
				raise ViriError("set temperature does not match vgcsch%s/dm"%drive_letter)
			else:
				trace_success("vgcsch%s/dm throttle temp == set throttle temp"%drive_letter)
		
		return 1

	def setOfflineTemperature(self,temp,device):

		comm = "%s -d %s -s %s" % (VGCDPTSETTING, device, temp)	
		
		o = self.host.run_command_chk_rc(comm)
		print o
		if o['rc'] != 0:
			raise ViriError("could not set offline temperature")
		else:
			trace_success("offline temperature set to %s"%temp)

		drive_letter = get_device_letter(device)

		comm = "%s vgcsch%s/dm | grep 'Offline Threshold'" % (VGCPROC, drive_letter)
		o = self.host.run_command_chk_rc(comm)
		print o
		output = o['output']
		
		vgcschdm_offline = output[1].split(':')[1]	

		if vgcschdm_offline != str(temp):
			raise ViriError("set temperature does not match vgcsch%s/dm"%drive_letter)
		else:
			trace_success("vgcsch%s/dm offline temp == set offline temp"%drive_letter)

	def setCompliantMode(self,device):
	
		comm = "%s -d %s -m 1 -t 78" % (VGCDPTSETTING, device)

		o = self.host.run_command_chk_rc(comm)
		print o
		if o['rc'] != 0:
			raise ViriError("could not set compliant mode with throttle temperature at 78")
		else:
			trace_success("compliant mode set with throttle temperature 78")

		drive_letter = get_device_letter(device)

		comm = "%s vgcsch%s/dm | grep 'Throttle Threshold'" % (VGCPROC, drive_letter)
		o = self.host.run_command_chk_rc(comm)
		print o
		output = o['output']
		
		vgcschdm_throttle = output[1].split(':')[1]	

		if vgcschdm_throttle != '78':
			raise ViriError("set temperature does not match vgcsch%s/dm"%drive_letter)
		else:
			trace_success("vgcsch%s/dm throttle temp == set throttle temp"%drive_letter)
		
	def cardNotOffline(self,device):

		comm = "grep 'ADMIN OFFLINE' /var/log/messages | grep %s" % (device)
		run = self.host.run_command(comm)
		print run
		
		if run['rc'] != 0:
			trace_success("no offline messages found in /var/log/messages for %s"%device)
		else:
			raise ViriError("/var/log/messages reported %s is offline"%device)

		return 1

	def cardOffline(self,device):

		comm = "grep 'ADMIN OFFLINE' /var/log/messages | grep %s" % (device)
		run = self.host.run_command(comm)
		print run
		
		if run['rc'] == 0:
			trace_success("card offline message in /var/log/messages for %s"%device)
		else:
			raise ViriError("/var/log/messages did not reported %s is offline"%device)

		return 1
