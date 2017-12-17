from ViriImports import *
from FileSystems.MD5ReaderWriter import *

class vsanUtils:
    def __init__(self):
        pass
    
    
    def enable(self,mode = "" ):
    
       self.host.vgcconfig.enable_vsan_feature(self.viri_device(),self.feature,mode)
   
    def run_all_fs_testcase(self, ):
      self.host.create_all_fs(self.get_device())
      return 1
    
    