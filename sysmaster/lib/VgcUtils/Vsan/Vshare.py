import sys,time

from ViriImports import *
from VsanUtils import vsanUtils
#from HostLinux import *

import IB
"""
vgc-vshare-config: FlashMAX Connect Software Suite 1.0(54080.V3)

Too few arguments

Usage: vgc-vshare-config <command> [command options]
           --create-target  --size <vShare-device-size (GB)> <vShare-name> <backing-dev>
           --create-initiator --target <target hostname> --uuid <vShare-uuid> <vShare-name> 
           --start <vShare-device-name> 
           --stop <vShare-device-name> 
           --grant-access <initiator-hostname> <vShare-device-name> 
           --revoke-access <initiator-hostname> <vShare-device-name> 
           --delete-initiator <vShare-device-name> 
           --delete-target <vShare-device-name>
           --delete-all
           --help

    The UUID gets generated when "target" is created. Then the same UUID should be used to create the "initiator".

    User should run grant-access to allow an "initiator" connect to a "target".

    User should run revoke-access to disconnect an "initiator" from a "target".
"""

STOPPED      = "Stopped"
DISCONNECTED = "Disconnected"
CONNECTED    = "Connected"
STARTED      = "Started"
ROLES        = ['initiator','target']

class vgcVshare(vsanUtils):
  def __init__(self ,initiator,target,vsharename ,device,size):
     self.vsharename = vsharename
     self.size  = size
     self.backing_device = device
     self.initiator = initiator
     self.target = target
     self.vgcVshareConfig = "vgc-vshare-config"
     self.vgcVshareMonitor = "vgc-vshare-monitor"
     self.feature          = "vshare"
  
  def create_objects(self):
    
     inits = [ create_host(init) for init in self.initiator]
     self.initiator = inits
     self.target = hostLinux(self.target)
     

  def viri_device(self, ):
    
     return self.backing_device
    
  def create_ibguids_string(self,host):
      """
      takes portGuids as input,return line as --ibguid1 0x11.. --ibguid2 0x22
      """
      # TO DO check if array is > 2
      
      portGuids = host.ib().get_port_guids()
      c = 1
      line = " "
      for pguid in portGuids:
        line = line + "--ibguid%i %s "%(c,pguid)
        c +=1
      line = line.rstrip()
      return line
    
  def create_initiator(self,withPortGuids = 0):
     # --create-initiator --target <target hostname> --uuid <vShare-uuid> <vShare-name>
     command = "%s --create-initiator  --target %s --uuid %s %s "%(self.vgcVshareConfig,self.target.name,self.get_target_uuid(),self.vsharename)
     
     
     for init in self.initiator:
       if withPortGuids:
         command = command + self.create_ibguids_string(init)
        
       init.run_command_chk_rc(command)
       self.grant_access_on_target(withPortGuids)
    
  def create_target(self,withPortGuids = 0):
     # --create-target  --size <vShare-device-size (GB)> <vShare-name> <backing-dev>
     
     command = "%s --create-target  --size %s %s %s "%(self.vgcVshareConfig,self.size,self.vsharename,self.backing_device)
     line = ""
     #if withPortGuids:
     #   command = command + self.create_ibguids_string("target")
     #print command
     self.target.run_command_chk_rc(command)
     #sys.exit(1)
     return 1

  def get_device(self):
      return "/dev/" + self.vsharename
    
  def get_details(self,host,attrib = ""):
       
       cmd = "%s --detail %s"%(self.vgcVshareMonitor,self.get_device())
       output = host.run_command_chk_rc(cmd)['output']
       parsedOutput = parse_vgc_vshare_monitor(output)
     
       # TO DO, with attribute, it is taking get_device
       if attrib:
          print parsedOutput[self.get_device()][attrib]
          return parsedOutput[self.get_device()][attrib] 

       return parsedOutput

  def get_target_uuid(self):
      return self.get_details(self.target)[self.get_device()]['target_uuid']

  def get_state(self,host):

    return self.get_details(host)[self.get_device()]['state']
    
  def get_state_initiator_target(self):
      
      target_state = self.get_state("target")
      initiator_state = self.get_state("initiator")
      return (target_state,initiator_state)

  def compare_state(self,role,expectedState):
    
     """takes role as "initiator or target, expected state and compares the state, tries 4 times
     raise if the state is not reached"""
     
     for host in self.get_role_object(role):
      #try four times
      for c in range(0,4):
         
         foundState = self.get_state(host)
         
         if foundState == expectedState:
           
           trace_info("Success:Found state '%s',expected '%s' for '%s'"%(foundState,expectedState,role))
           return True
         trace_info("Found state '%s',expected '%s' for '%s',retrying..."%(foundState,expectedState,role))
         sleep_time(2,"after finding state")
         continue
       
      raise ViriError("Found state '%s',expected '%s', for '%s' even after retries"%(foundState,expectedState,role))
  
  

  
  def chk_state_target_init(self,expected_state):
    
      """ {'initiator':'disconnected','target':'Started'} """
      # 
      if self.compare_state("initiator",expected_state['initiator']):
          pass
      
      if self.compare_state("target",expected_state['target']):
          pass
  
      return True

  def is_disconnected(self):
    
      # TO DO, what is the disconnected state
      return self.chk_state_target_init({'initiator':DISCONNECTED,'target':STARTED})
            
  def is_connected(self):
    
      return self.chk_state_target_init({'initiator':CONNECTED,'target':STARTED})

  def change_access_on_target(self,access,withPortGuids = 0):
 
      accessType = {'grant':{'string':'grant-access','state':"Connected"},'revoke':{'string':'revoke-access','state':"Disconnected"}}
    
      # --grant-access <initiator-hostname> <vShare-device-name>
      
      for init in self.initiator:
          command = "%s --%s %s %s"%(self.vgcVshareConfig,accessType[access]['string'],init.name,self.get_device())
          if access == "grant":
             if withPortGuids:
                 command = command + self.create_ibguids_string("target")
          self.target.run_command_chk_rc(command)
      
      #trace_info("Waiting few secs after changing access on target to '%s'"%access)
      #time.sleep(3)
  
  def grant_access_on_target(self,withPortGuids = 0):
    
     self.change_access_on_target("grant")
     self.is_connected()

  def revoke_access(self):
      # --grant-access <initiator-hostname> <vShare-device-name>
      self.change_access_on_target("revoke")
      self.is_disconnected()
      

     
  def get_role_object(self,role):
    
    # return the intiator/target object
    if role == "initiator":
           return self.initiator
    elif role == "target":
           return [self.target] # make it a list/array
    else:
           raise ViriError("Valid values for role are target or initiator and not '%s'"%role)

  def stop(self,role):
    
    cmd = "%s --stop %s"%(self.vgcVshareConfig,self.get_device())
    
    trace_info("Stopping %s"%role)
    print ""
    
    for host in self.get_role_object(role): host.run_command_chk_rc(cmd)
    
    # in stop state init and target ahd different states
    expected_state = {"initiator": {'initiator': STOPPED,'target':STARTED},
                     "target": {'initiator': DISCONNECTED,'target':STOPPED} }
    
    # dict to pass is dependent on role,
    # if you stop init for example, init role should be stopped while target started
    # so for target pass dict as {'initiator': DISCONNECTED,'target':STOPPED}
    self.chk_state_target_init(expected_state[role])


  def enable(self,mode = "" ):
    
       
       self.target.vgcconfig.enable_vsan_feature(self.viri_device(),"vshare",mode)
       

  def is_attribute_increasing(self,role,attribute ):

    """ check if attribute is increasing"""
    value = utils_if_value_in_brackets(self.get_details(role,attribute))
    valueB = int(utils_if_value_in_brackets(self.get_details(role,attribute)))

    sleep_time(3,"After setting attribute %s"%attribute)

    # remove GB if there with any attrib value, also gets 13 from 13 ( 1 Gib), ignores 1 Gib
    # Util have  it
    valueA = int(utils_if_value_in_brackets(self.get_details(role,attribute)))

    trace_info("Vshare Found value after '%i',before '%i'"%(valueA,valueB))

    if valueA > valueB:
      return True

    return False

    
  def is_reads_writes_increasing(self,role):
    if not self.is_attribute_increasing(role,"total_bytes_written"):
       raise ViriError("Write bytes not increasing , role %s"%role)

    trace_info_dashed("Writes seem to be increasing fine")
    
    return 1

  def create_vshare_reset_backend(self,mode = "", withPortGuids = 0):
    
    self.deleteAll("initiator")
    self.deleteAll("target")
    self.enable(mode = mode)
    self.create(withPortGuids)# add port Guids, TO DO
    
  def create(self,withPortGuids = 0):
     self.create_target(withPortGuids)
     self.create_initiator(withPortGuids)

  def run_io_testcases(self):
    
    for role in ROLES:
      
    
      # DELETE while IO beind done
      for host in self.get_role_object(role): host.run_dd(self.get_device())
      # delete all will fail, TO DO file a bug for return code
      self.deleteAll(role)
      self.is_connected()
    
    
      for host in self.get_role_object(role): host.wait_for_dd_to_complete()
      
      self.check_for_errors()

      

      for host in self.get_role_object(role): host.run_dd(self.get_device())
      self.stop(role)
      for host in self.get_role_object(role): host.wait_for_dd_to_complete()
      self.start(role)
      
      self.check_for_errors()
      
      for host in self.get_role_object(role): host.run_dd(self.get_device())
      self.is_reads_writes_increasing(role)
      for host in self.get_role_object(role): host.wait_for_dd_to_complete()
      
      self.check_for_errors()
     
    
  def start(self,role):
    
    cmd = "%s --start %s"%(self.vgcVshareConfig,self.get_device())
    
    trace_info("Starting %s"%role)
    print ""
    
    for host in self.get_role_object(role): host.run_command_chk_rc(cmd)
    # check both intiator and trgt should be connected
    self.is_connected()
  
  def run_negetive_testcases(self):
    
    
    cmds = [ 'vgc-vshare-config --delte','vgc-vshare-monitor --delte']
    
    for cmd in cmds:
      self.initiator.run_negetive_command(cmd)
      self.target.run_negetive_command(cmd)
    
    self.initiator.run_negetive_command("%s --revoke-access vsan40 %s"%(self.vgcVshareConfig,self.get_device()))
    self.initiator.run_negetive_command("%s --grant-access vsan40 %s"%(self.vgcVshareConfig,self.get_device()))
    # RESTART Driver after grant and revoke access on initiator bug was file,also check if connection occured
    self.initiator.restartVgcDriver()
    self.is_connected()
      
  def deleteAll(self,role):
    """deletes all vshares present """
    
    cmd = "echo 'yes' |%s --delete-all"%self.vgcVshareConfig
    for host in self.get_role_object(role): host.run_command_chk_rc(cmd)
    
  
  def check_for_errors(self, ):
    
    # Commenting the region since read_write errors have been removed
    #for role in ROLES:
    #  
    #  for errType in ['total_read_errors',  'total_write_errors' ]:
    #    
    #    errors = self.get_details(role,errType)
    #    
    #    if errors != "0":
    #       raise ViriError("Found error '%s' as '%s'"%(errType,errors))
    #    trace_info("Found error '%s' as '%s'"%(errType,errors))
    #      
    # 
    #trace_info("No Read/write errors found on vshare")
    
    for role in ROLES:
      for host in self.get_role_object(role): host.is_crash_dir_empty()
      for host in self.get_role_object(role): host.print_syslogs_dmesg()
    
    self.target.chk_if_ue_errors(self.backing_device)
    self.target.chk_if_dpp_errors(self.backing_device)
    
    return 1
 
  def name(self, ):
    pass
  
  
  def run_fs_testcases(self, ):
    
    trace_info_dashed("Vshare Running filesystem testcases ")
    # create filesystem on both target and init
    for role in ROLES:
      
      trace_info_dashed("Vshare Running filesystem testcases on role '%s'"%role)
      
      if role == "target":
        # target doesnt allow service restart in create_all_fs tests
        # so stopping it
        self.stop("initiator")
      for host in self.get_role_object(role): host.create_all_fs(self.get_device())
      
      if role == "target":
        # start initiator back,after stopping as done before
        self.start("initiator")
      
      trace_info_dashed("Vshare DONE Running filesystem testcases on role '%s'"%role)
    trace_info_dashed("Vshare: DONE !!!! Running ALL filesystem testcases ")
    return 1
  
  def runAll(self, ):
    #self.run_io_testcases()
    #self.run_negetive_testcases()
    
    
    self.run_fs_testcases()
    
    self.check_for_errors()
  
    sys.exit(1)
    for role in ROLES:
     for c in range(1,2):
      for host in self.get_role_object(role): host.power_cycle()
      self.is_connected()
    
    self.check_for_errors()
    for role in ROLES:
      
      trace_info_dashed("Running for role %s"%role)
      for c in range(1,2):
        self.stop(role)
        self.start(role)
        self.is_connected()
        
    self.check_for_errors()
    
    for c in range(1,4):
      self.revoke_access()
      self.grant_access_on_target()
      
    self.check_for_errors()

      
    
    
      
    
  
    

    
  
   
