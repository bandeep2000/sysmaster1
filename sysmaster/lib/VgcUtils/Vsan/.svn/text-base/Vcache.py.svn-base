import sys
#from ViriImports import *
from FileSystems.MD5ReaderWriter import *
from VsanUtils import *
VCACHE_DETACHED_STATE = "DETACHED"
VCACHE_GOOD_STATE = "GOOD"

#MODES = ["write-through"]
MODES = ["write-back","write-around","write-through"]

class vgcCache(vsanUtils):
  def __init__(self ,host,name ,f_device ,b_device ,size , dirty_threshold = "" , mode = "", flush_period = ""):
     self.cachename = name
     self.f_device = f_device
     self.b_device = b_device
     
     self.dirty_threshold = dirty_threshold
     self.size       = size
     self.vgcVcacheConfig = "vgc-vcache-config"
     self.mode  = mode
     
     self.flush_period = flush_period
     
     self.host = host
     
     self.feature = "vcache"

  def is_attribute_increasing(self,attribute ):
    
    """ check if attribute is increasing"""
    valueB = int(utils_if_value_in_brackets(self.get_details(attribute)))
    
    sleep_time(3,"After setting attribute %s"%attribute)
 
    # remove GB if there with any attrib value, also gets 13 from 13 ( 1 Gib), ignores 1 Gib
    # Util have  it 
    valueA = int(utils_if_value_in_brackets(self.get_details(attribute)))
    
    trace_info("Vcache Found value after '%i',before '%i'"%(valueA,valueB))
    
    if valueA > valueB:
      return True
    
    return False

  def compare_seq_detect(self,status):
    """ takes status to compare as input, gets the actual status"""
    found_status = self.get_seq_detect()
    
    if found_status == status:
      trace_success("Sequence detection status expected'%s', found %s"%(status,found_status))
      return 1
    
    raise ViriError("Sequence detection expected status '%s',found status %s"%(status,found_status))

  def seq_detect(self,status):
    
    if status != 'on' and status != 'off':
      raise ViriError("status should be on or off for seq detection,passed as '%s'"%status)
    
    cmd = "%s  --seq-detect %s %s"%(self.vgcVcacheConfig,status,self.get_device())
    
    self.host.run_command_chk_rc(cmd)
    
    self.compare_seq_detect(status)
    
    return 1
  
  def get_seq_detect(self):
    """ return sequencence detection status on/off"""
    #return self.get_details('sequence_detection').lower()
    
    # TO DO Put write also
    return self.get_details('read_seq_detection').lower()
  
  
  def get_state(self):

    return self.get_details('status')
  
  def get_dirty_data(self):
    
    d_data = utils_if_value_in_brackets(self.get_details('total_dirty_data'))[0]
    trace_info( "Found dirty data as '%s'"%d_data)
    return d_data
 
  def get_flush_period (self,seconds = 1):
    """returns flush period as integer, defaults to returns in seconds """
 
    flush_p = self.get_details("flush_period")
    
    # remove "mins" and string
    
    flush_p = int((flush_p).replace("mins","").strip())
    
    if flush_p == 0:
      raise ViriError("Flush period found is 0")
    
    if seconds:
      flush_p =  int(flush_p) * 60
    
    trace_info("Found flush period as '%i'"%flush_p)
    return flush_p
    
  
  def get_details(self,attribute = "all"):
    """return dictionnary with details of vcache, if attribute is passed return that """
    o = self.host.run_command_chk_rc("vgc-vcache-monitor --detail %s"%(self.get_device()))
    output = o['output']

    printOutput(output)
    
    details = parse_vgc_vcache_monitor(output)
    
    if attribute == "all":
      return details[self.get_device()]
    
    try:
      
      # add self.get_device will give ['/dev/vgca0']
      return details[self.get_device()][attribute]
    
    except KeyError:
      trace_error("did not find attribute '%s' details in the vcache details '%s'"%(attribute,output))
      raise
      #sys.exit(1)

  def create(self):

    cmd = "%s --create "%self.vgcVcacheConfig
    if self.mode != "":
      cmd = cmd + " --mode "+ self.mode
    if self.flush_period != "" :
	cmd = cmd + " --flush-period  " +  self.flush_period

    if self.dirty_threshold != "":
	cmd = cmd + " --dirty-threshold  " + self.dirty_threshold
        
    cmd = cmd + " " +   " --size " + self.size  +"  " + self.cachename +" " + self.f_device  + " " + self.b_device
  
    self.host.run_command_chk_rc(cmd)
    sleep_time(3,"after creating vcache")
    
  def deleteAll(self):
    """deletes all cache present """
    
    cmd = self.vgcVcacheConfig + " --delete-all --force"
    
    self.host.run_command_chk_rc(cmd)
    # sleep, since some times there is issue
    sleep_time(5,"after deleting all caches")
  
  
  def run_negetive_testcases(self ):
    
    # clean up, TO DO, this should check if the vcache was created or not before deleting
    self.deleteAll()
    
    for mode in MODES: 
   
        trace_info_dashed("Testing for mode %s"%mode)
        self.mode = mode

	self.create()
	#continue
	cmds = [ 'vgc-vcache-config --delte','vgc-vcache-monitor --delte','vgc-vcache-config']
        for cmd in cmds:
          self.host.run_negetive_command(cmd)
    
          # run dd in bg and try to delete while io is runnin in the back ground
        self.host.run_dd(self.get_device())
        self.host.run_negetive_command("vgc-vcache-config --detach %s"%self.get_device())
        self.host.run_negetive_command("vgc-vcache-config --delete %s --force"%self.get_device())
        self.host.wait_for_dd_to_complete()
	  
        if self.is_mode_write_back():
            # for writeback cache there will be some dirty data
            
            self.host.run_negetive_command("vgc-vcache-config --detach %s"%self.get_device())
            self.host.run_negetive_command("echo \"yes\" |vgc-vcache-config --delete %s"%self.get_device())
       
            self.flush()
        
	# DO NOT Change the sequcence of the these commands!!!
	if not self.is_mode_write_back():
	  self.host.run_negetive_command("vgc-vcache-config --flush %s"%self.get_device())
	 
	# clean again,for next iteration
	self.deleteAll()
	  
	# TO DO, this is being called for all the modes, dirty threshold 0
	self.host.run_negetive_command("vgc-vcache-config --create --mode %s --size 100 - --dirty-threshold 0 %s"%(mode,self.get_device()))
	# dirty thr > size
	self.host.run_negetive_command("vgc-vcache-config --create --mode %s --size 100  --dirty-threshold 101 wb %s %s"%(mode,self.f_device,self.b_device))
	
        #if not self.is_mode_write_back():
            
        #    self.host.run_negetive_command("vgc-vcache-config --create --mode %s --size 100  --dirty-threshold 10 wb %s %s"%(mode,self.f_device,self.b_device))
	    
    trace_info("Negetive test complete")	    

  def age_based_write_back(self):
     return  int(self.get_details("age_based_write_back").replace("times","").strip())

  def has_dirty_data(self, ):
    
    if not self.is_mode_write_back():
       raise ViriError("Mode is not write-back, but trying to get dirty data")
      
    if int(self.get_dirty_data()) > 0:
      return True
    
    return False
 
  def delete(self):
    """deletes single cache only """
    
    #vgc-vcache-config --delete wb /dev/vgcb0 --force
    self.host.run_command_chk_rc("%s --delete %s %s --force"%(self.vgcVcacheConfig,self.cachename,self.f_device))
				  
  def flush(self):
    
    # vgc-vcache-config --flush wb /dev/vgcb0
				  
    cmd = "%s --flush %s"%(self.vgcVcacheConfig,self.get_device())
    
    self.host.run_command_chk_rc(cmd)
  
  def _attach_detach(self,att_det):
    
    cmd = "%s %s %s"%(self.vgcVcacheConfig,att_det,self.get_device())
 
    self.host.run_command_chk_rc(cmd)
    
    found_state =  self.get_state()
    
    if att_det == "--attach":
      expected_state = VCACHE_GOOD_STATE
    
    elif att_det == "--detach":
      expected_state = VCACHE_DETACHED_STATE
      
    compare(found_state,expected_state,"vcache after giving %s command"%att_det)
    return 0
    
  def get_device(self):
    """ returns /dev/vgcb0_wb"""
    
    return self.f_device + "_" + self.cachename
  
  def attach(self):
    
    self._attach_detach("--attach")

  def detach(self):
    
    self._attach_detach("--detach")

  def viri_device(self, ):
    
    return self.f_device

  def disable(self, ):

    self.deleteAll()
    
    self.host.vgcconfig.disable_vsan(self.f_device)
    #pass
  
  def modify(self,attrib):

    """ takes attrib as attrib = {'size':'10','dirty_threshold':'200','flush_period':'20'}"""
    
    
    # TO DO need to add verification that modify was success
    
    cmd = "%s --modify "%self.vgcVcacheConfig
    
    found_key = 0
    
    if attrib.has_key("size"):
      cmd = cmd + " --size %s"%attrib['size']
      found_key = 1
      
    if attrib.has_key("dirty_threshold"):
      cmd = cmd + " --dirty-threshold %s"%attrib['dirty_threshold']
      found_key = 1
      
    if attrib.has_key("flush_period"):
      cmd = cmd + " --flush-period %s"%attrib['flush_period']
      found_key = 1
    
    if found_key == 0:
      raise ViriError("Please pass ,size, flush period or dirty threshold in the dict passed '%s'"%attrib)
    # holding off  on modify
    #  --modify [--size <min-size in GB>] [--dirty-threshold <dirty-threshold in GB>] [--flush-period <num-minutes>] cache-name frontend-dev backend-dev

    cmd = cmd + " %s %s %s"%(self.cachename,self.f_device,self.b_device)
    
    self.detach()
    
    self.host.run_command_chk_rc(cmd)
    
    self.attach()
  
    return 0
  
  def is_mode_write_back(self):
    
    mode = self.get_details()['mode']
    
    trace_info("Found mode as '%s' "%mode)
    if mode == "Write-back":
      
      trace_info("Mode is write-back")
      return True
    
    trace_info("Mode is not write-back")
    return False
  
  
  def seq_detect_tcases(self, ):
    
    for seq in ['on','off']:
      
      # in v1.1 if seq detect is on it should remain on even
      # after starting driver, before it would get turned off
      exp_status = seq
      
      self.seq_detect(seq)
      self.host.restartVgcDriver()
      self.compare_seq_detect(exp_status)
      
    return 1
    
  
  def mdReadWriteStimulus_tcases(self,stimulus ):
   
    for mode in ["write-back","write-around","write-through"]:
      
      trace_info_dashed("Running test for mode '%s' for stimulus '%s'"%(mode,stimulus))
      self.mode = mode
      self.deleteAll()
      self.create()
      m = md5ReaderWriter(self.host)
      
      m.write(self.get_device())
      
      # sleep, since some times there is issue
      sleep_time(10,"after writing using md5writer")
      
      if stimulus == "power_cycle":
	
	self.host.power_cycle()
      
      else:
         if self.is_mode_write_back():
	   self.flush()
      
      if stimulus == "modify":
         for s in range(50,60):
	   self.modify({'size':int(s)})
      
      if stimulus == "create_all_modes":
         self.detach()
	 # Note,reading again after attaching,see below
         m.read(self.b_device)
         self.attach()
	
      m.read(self.get_device())
      trace_info_dashed("Stimulus %s Successful for mode %s"%(stimulus,mode))
      
    trace_info_dashed("Stimulus %s Successful"%stimulus)
    
  def create_all_modes_testcase(self):
    
    m = md5ReaderWriter(self.host)
    
    for mode in ["write-back","write-around","write-through"]:
      self.mode = mode
      self.deleteAll()
      self.create()
      m.write(self.get_device())
      if self.is_mode_write_back():
	self.flush()
      
      # sleep, since some times there is issue
      sleep_time(3,"after writing using md5writer")
      self.detach()
      m.read(self.b_device)
      self.attach()
      
      trace_info_dashed("Success  mode '%s' creation testcase"%mode)
    trace_success_dashed("Success all mode creation testcase")
                

  
  def power_cycle_usb_testcase(self):
   self.deleteAll()
   #sys.exit(1)

   fiotime = "100"
   fiotime = "10"
   wait_after_fio = 20
   
   
   for mode in MODES:
      self.deleteAll()
      trace_info("TEST START-----------------------------------------")
      trace_info_dashed("Running usb power cycles for mode %s"%mode)
 
      self.mode = mode
      #h.vgcconfig.enable_vsan_feature("/dev/vgca0","vcache")

      self.create()
      
      # repeat for seq detection
      for seq in ['off','on']:
       self.seq_detect(seq)
      
       #for bs in ["512-1M","4K", "512"]:
       for bs in [ "512"]:
         continue
	 trace_info_dashed("Running for seq det '%s', bs %s,mode %s"%(seq,bs,mode))
         print self.host.fio().run(self.get_device(),bs = "512",size = "512",time
	 = fiotime,rw = "randread",ioengine = "psync",numjobs = "1",rw_perc = "100",ba = None,fsync
                = None,bg = True )
         print self.host.fio().run(self.get_device(),bs = bs,time = fiotime,rw = "randrw",
                ioengine = "psync",numjobs = "1",rw_perc = "50",ba = None,fsync
                = None,bg = True )
         sleep_time(wait_after_fio,"Waiting after running Fio")

         self.host.power_cycle()
	 
	 # had a bug where you power cycle after flush
         if self.is_mode_write_back():

            self.flush()
   trace_info("Cleaning up after the test")
   self.deleteAll()
   self.create_write_back_cache()
   
   trace_info("TEST END-----------------------------------------")
   
  def create_vshare_reset_backend(self,mode = ""):
    self.deleteAll()
    self.enable(mode = mode)
    self.enable()
    self.create()

  def age_based_flush_tcase(self, ):
    
    trace_info("Running age based tcase")
    if not self.is_mode_write_back():
       raise ViriError("Mode is not write-back, age based writeback is not valid tcase")
    
    # Age base write back counter should be incremented
    self.host.run_command_chk_rc("dd if=/dev/urandom of=%s bs=1M count=1"%self.get_device())
    
    if not self.has_dirty_data():
      raise ViriError("No dirty data present")

    
    age_based_write_back1 = self.age_based_write_back() 
    
    # just add 4 to give some extra time, less that 4 was giving issues
    some_extra_time = 4
    flush_period = self.get_flush_period()
    sleep_t = flush_period + some_extra_time
    sleep_time(sleep_t,"waiting for dirty data to flush")
    age_based_write_back2 = self.age_based_write_back() 


    if age_based_write_back2 > age_based_write_back1:
       trace_info("Age base write back increased, before,'%i',after '%i'"%(age_based_write_back1,age_based_write_back2))
    else:
       raise ViriError("Age base write back did not increase, before,'%i',after '%i'"%(age_based_write_back1,age_based_write_back2))
    
    if not self.has_dirty_data():
      trace_info("Tcase success,flushing after %i seconds is fine"%flush_period)
      return 1
    
    raise ViriError("Tcase failed")
   
  def create_write_back_cache(self, ):
    
    self.mode = "write-back"
    self.create()
    
    return 1
  
  def runAllTestCases(self, ):

    
    if not self.is_mode_write_back():
       raise ViriError("Mode is not write-back, to run all testcases please start with write-back")
    
    
    for stim in ["modify","power_cyle","create_all_modes"]:
     self.mdReadWriteStimulus_tcases(stim)
    
    self.create_all_modes_testcase()
    # from parent class all fs testcass
    self.run_all_fs_testcase()
    self.seq_detect_tcases()
    
    self.power_cycle_usb_testcase()
    
    #self.age_based_flush_tcase()
      
    self.run_negetive_testcases()

  
  
  
  
    
  




