#rom Util import *
#from Parsers import *
#import sys
from Trace import *

class stats():
    
    def __init__(self,host):
        
        self.host = host
        
    def download_vgc_stats(self):
        
        if not self.host.if_file_exists("/root/vgc-stats.py"):
           self.host.wget_chmod_file("http://spica/sqa/tools/perl/vgc-stats.py")
      
    def start_vgc_stats(self,util,device,dir,file,timeGap = "1"):
        
        trace_info("Using vgc-cronmon dir as %s file %s"%(dir,file))
	self.download_vgc_stats()
        
        filePath = "%s/%s"%(dir,file)
        
        self.host.createDirifNotExists(dir)
        if (self.host.if_file_exists("%s/%s"%(dir,file))):
            trace_info("Seems like file  %s exists, removing it"%filePath)
            self.host.run_command_chk_rc("rm -rf %s"%filePath)
            
	bgFile =  "%s/%s"%(dir,file)
        cmd = "./%s %s %s "%(util,device,timeGap)
        self.host.run_command(cmd,bg = True, bgFile = bgFile)
        return 1
    def kill_vgc_stats(self):
        self.host.run_command("killall vgc-stats*")
        
        
        
