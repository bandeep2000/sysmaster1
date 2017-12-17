from pysphere import *
from ViriImports import *
import time

"""

This class ignores any VMs in the datacenter with the word 'golden' in its names.

Some Features of this class requires VMWare Tools to be installed on the VM.

=========

Example vmx passthrough configuration

pciPassthru0.id = "06:00.0"
pciPassthru0.deviceId = "0x43"
pciPassthru0.vendorId = "0x1a78"
pciPassthru0.systemId = "55282eaa-fc86-4380-7dcc-002590c3c822"
pciPassthru1.id = "130:00.0"
pciPassthru1.deviceId = "0x43"
pciPassthru1.vendorId = "0x1a78"
pciPassthru1.systemId = "55282eaa-fc86-4380-7dcc-002590c3c822"
pciPassthru2.id = "131:00.0"
pciPassthru2.deviceId = "0x40"
pciPassthru2.vendorId = "0x1a78"
pciPassthru2.systemId = "55282eaa-fc86-4380-7dcc-002590c3c822"
sched.mem.min = "10000"
pciPassthru0.pciSlotNumber = "-1"
pciPassthru1.pciSlotNumber = "-1"
pciPassthru2.pciSlotNumber = "-1"
pciPassthru0.present = "TRUE"
pciPassthru1.present = "TRUE"
pciPassthru2.present = "TRUE"

"""

class vmware:

	def __init__(self, host, host_user, host_password, vcenter, vcenter_user, vcenter_password, datacenter):
       
		self.hostname = host 
		self.host_user = host_user
		self.host_password = host_password
		self.vcenter = vcenter
		self.vcenter_user = vcenter_user
		self.vcenter_password = vcenter_password
		self.datacenter = datacenter

		self.vm_name_list = []
		self.vm_path_list = []
		self.vm_list = []

		self.passthrough_devices = []
		self.passthrough_devices_mapped = []
		self.passthrough_config = []

		self.vcenter_connect()

		self.host = Machine.HostLinux.hostLinux(self.hostname, u_name = self.host_user, passwd = self.host_password, logon = 0)

		# for esxi host
		self.host.logon(check_kdump = 0, check_crash_dir = 0)

		self.get_passthrough_devices()

		self.get_vms()

		self.build_passthrough_vmx()

	def vcenter_connect(self):
		
		self.vcenter_connection = VIServer()
		self.vcenter_connection.connect(self.vcenter, self.vcenter_user, self.vcenter_password)

	def get_vms(self):
		
		self.vm_path_list = self.vcenter_connection.get_registered_vms(datacenter = self.datacenter)

		vm_path_list_tmp = []
		for vm_path in self.vm_path_list:
			if 'golden' not in  vm_path:
				vm_path_list_tmp.append(vm_path)
		
		self.vm_path_list = vm_path_list_tmp
		self.vm_path_list.sort()

		print self.vm_path_list 

		for vm_path in self.vm_path_list:
			vm = self.vcenter_connection.get_vm_by_path(vm_path)
			self.vm_list.append(vm)

			vm_properties = vm.get_properties()
			vm_name = vm_properties['name']
			trace_info("vm detected in datacenter: %s, %s" % (self.datacenter, vm_name))
			self.vm_name_list.append(vm_name)
		
		return 1

	def get_vm_name_list(self):
		
		return self.vm_name_list

	def get_passthrough_devices(self):

		run = self.host.run_command("lspci -vp | grep pciPassthru")	
		if run['rc'] != 0:
			raise ViriError("no passthrough devices detected on esxi host")

		output = run['output']
		output.pop(0)

		trace_info("passthrough devices detected")

		for line in output: 
			print line
			self.passthrough_devices.append(line)

		for passthrough_device in self.passthrough_devices:
			id = passthrough_device.split()[0]	
			run = self.host.run_command_get_output("lspci --v | grep %s" % id)
			self.passthrough_devices_mapped.append(run[1])

		trace_info("passthrough devices mapped")
	
		for mapped_passthrough in self.passthrough_devices_mapped:
			print mapped_passthrough	

		return 1

	def clean_vmx(self, vm_name):

		("removing passthrough devices, if any for %s" % vm_name)
		vmx = self.get_vmx(vm_name)
		self.host.run_command_chk_rc("sed -i '/^pciPassthru/ d' %s" % vmx) 
		self.host.run_command_chk_rc("sed -i '/^sched.mem.min/ d' %s" % vmx) 
		self.host.run_command_chk_rc("sed -i '/^\s*$/d' %s" % vmx)

		return 1

	def clean_all_vmx(self):
		
		for vm_name in self.vm_name_list:
			self.clean_vmx(vm_name)

		return 1

	def get_vm_memory(self, vm_name):

		vmx = self.get_vmx(vm_name)
		output = self.host.run_command_get_output("grep memSize %s" % vmx)
		memsize = output[1].split("=")[1].strip().replace('\"','') 
		print memsize

		return memsize
		
	def build_passthrough_vmx(self):

		sysID = self.host.run_command_get_output("vsish -e cat /system/systemUuid | grep 'uuid String' | cut -d: -f 2")
		sysID = sysID[1]
		trace_info("system id is %s" % sysID)

		passthrough_counter = 0

		for line in self.passthrough_devices:

			id_string = line.split()[0].lstrip('0').lstrip(':')
			id_hex = id_string.split(':')[0]
			id_dec = int(id_hex, 16)
			if id_dec < 10:
				id_dec = '0' + str(id_dec)
			id_string = id_string.replace(id_hex, str(id_dec))

			pt_id = 'pciPassthru%d.id = \"%s\"' % (passthrough_counter, id_string)
			self.passthrough_config.append(pt_id)

			pt_deviceId = 'pciPassthru%d.deviceId = \"0x%s\"' % (passthrough_counter, line.split()[1].split(':')[1].lstrip('0'))
			self.passthrough_config.append(pt_deviceId)

			pt_vendorId = 'pciPassthru%d.vendorId = \"0x%s\"' % (passthrough_counter, line.split()[1].split(':')[0])
			self.passthrough_config.append(pt_vendorId)	

			pt_systemId = 'pciPassthru%d.systemId = \"%s\"' % (passthrough_counter, sysID) 
			self.passthrough_config.append(pt_systemId)	

			pt_present = 'pciPassthru%d.present = \"TRUE\"' % passthrough_counter
			self.passthrough_config.append(pt_present)	

			passthrough_counter = passthrough_counter + 1

		trace_info("vmx configuration of passthrough devices")
		for line in self.passthrough_config:
			print line
		
		return 1

	def enable_passthrough(self, vm_name):

		self.power_off_all_vms()
		self.clean_all_vmx()
		vmx = self.get_vmx(vm_name)	
		memsize = self.get_vm_memory(vm_name)

		for line in self.passthrough_config:
			self.host.run_command_chk_rc("echo -e '%s' >> %s" % (line, vmx))

		comm = "echo -e 'sched.mem.min = \"%s\"' >> %s" % (memsize, vmx)
		self.host.run_command_chk_rc(comm)
		#comm = "echo -e 'sched.mem.minSize = \"%s\"' >> %s" % (memsize, vmx)
		#self.host.run_command_chk_rc(comm)
	
		self.power_on_vm(vm_name)

		return 1

	def power_on_vm(self, vm_name):

		trace_info("powering on vm, %s" % vm_name)
		self.vcenter_connection.get_vm_by_name(vm_name).power_on()

	def power_off_vm(self, vm_name):

		trace_info("powering off vm, %s" % vm_name)
		self.vcenter_connection.get_vm_by_name(vm_name).power_off()

	def power_off_all_vms(self):

		trace_info("powering off all vms")

		for vm in self.vm_list:
			if vm.get_status() != 'POWERED OFF':
				vm.power_off()	

	def power_on_all_vms(self):

		trace_info("powering on all vms")

		for vm in self.vm_list:
			if vm.get_status() != 'POWERED ON':
				vm.power_on()

	def get_vmx(self, vm_name):

		vmx = '/vmfs/volumes'

		for vm_path in self.vm_path_list:
			if vm_name in vm_path:
				datastore = vm_path.split()[0].replace('[','').replace(']','')	
				vmx = vmx + '/' + datastore + '/' + vm_name + '/' + vm_name + '.vmx'
				vmx = vmx.replace(' ','\ ')

		if vmx != '/vmfs/volumumes/':
			trace_info("vmx for %s is %s" % (vm_name, vmx))
			trace_info("verifying vmx file exists on hosts")
			self.host.run_command_chk_rc("ls %s" % vmx)
			return vmx
	
		raise ViriError("vmx could not be located for vm %s" % vm_name)				

	def get_vm_ip(self, vm_name):

		seconds = 0

		while seconds < 900:

			comm = "vim-cmd vmsvc/getallvms | grep '%s' | grep -v golden | cut -d' ' -f 1 | xargs vim-cmd vmsvc/get.guest | grep ipAddress | sed -n 1p | cut -d'\"' -f 2" % vm_name
			ip_address = self.host.run_command_get_output(comm)
			ip_address = ip_address[1]
		
			if ip_address.count('.') != 3:
				trace_info("vm %s, ip address not ready" % vm_name)
				trace_info("seconds elapsed: %d" % seconds)
				trace_info("sleeping for 30 seconds")
				time.sleep(30)
				seconds = seconds + 30
			else:
				return ip_address	

		raise ViriError("invalid IP address for vm")
