import sys
class vgcCache:
  def __init__(self ,host,name ,f_device ,b_device ,size ,dirty_size = "" ,mode="", flush_period = ""):
     self.cachename = name
     self.f_device = f_device
     self.b_device = b_device
     
     self.dirty_size = dirty_size
     self.size       = size
     self.vgcVcacheConfig = "vgc-vcache-config"
     self.mode  = mode
     
     self.flush_period = flush_period
     self.dirty_size = dirty_size
     self.host = host
     
     
     
  def create(self):
    
    cmd = "vgc-vcache-config --create  "
    if self.mode != "":
      cmd = cmd + " --mode "+ self.mode
    if self.flush_period != "" :
	cmd = cmd + " --flush-period  " +  self.flush_period
        
    
    if self.dirty_size != "":
	cmd = cmd + " --dirty-threshold  " + self.dirty_size
        
    cmd = cmd + " " +   " --size " + self.size  +"  "+ self.cachename +" " + self.f_device  + " " + self.b_device
    
    print cmd
    sys.exit(1)
    self.host.run_command_chk_rc(cmd)
                
    
  




