from VirExceptions import *
from Trace import *
import Util,sys

class driver:
   def __init__(self,host,verbose =1 ):
       self.host    = host
       self.verbose = verbose
   
   def start_stop(self,sts ):
      
      
      freem1 = self.host.memory().free()
      
      trace_info("Running driver %s"%sts)
 
      t1 = Util.get_epoch_time();print t1
      self.host.run_command("service vgcd %s"%sts)
      t2 = Util.get_epoch_time();print t2
      freem2 = self.host.memory().free()
         
      memDiff = freem2 - freem1
      tDiff   = t2 - t1
      trace_info("Used memory Difference is %i"%memDiff)
      trace_info("Time took %i"%tDiff)
      return (memDiff,tDiff)
   
   def restart(self,loops = 1):
      
      for l in range(0,loops):
         self.start_stop("restart")
   
   def stop(self):
 
         self.start_stop("stop")

   def start(self):
      
         self.start_stop("start")
        
   def isLoaded(self, ):
      
      """ Checks if the modules are loaded"""
      
      o = self.host.run_command_chk_rc("service vgcd status")
      
      out = o['output']
      
      Util.printOutput(out)
      for l in out:
         
         if "kernel modules are not loaded" in l:
            return False
         
      return True
   
   def get_driver_string(self,linux):
      
        releaseVersion = "3.2.2"
        
      	dict_prepend = { 'redhat61-vir': 'redhat6.1+-', 
                        'redhat61-emc': "EMCvPCIeSSD.RHEL6x-",
                        'redhat60-vir': 'redhat6.0-', 
                        'redhat60-emc': "EMCvPCIeSSD.RHEL60-",
                        "redhat5-vir" : "redhat5.x-",
                        "sles11sp1"   : "vgc-sles11sp1-kmp-default-%s_2.6.32.59_0.3-"%releaseVersion,
                        "sles11sp2"   : "vgc-sles11sp2-kmp-default-%s_3.0.80_0.5-"%releaseVersion}
      
        return dict_prepend[linux]

   def download_fw_installed(self,status):
      
      self.download_fw(build = self.host.vgcmonitor.getBuildNoReleaseString(),status = status)
      
   def download_fw(self,build, status,emc = 0):
      
      """ status is upgrade/downgrade"""
      
      if status == "upgrade":
         self.host.run_command_chk_rc("service vgcd start") # for 4.1, service has to be started
      
      else:
         # for downgrade it is stop
         self.host.run_command_chk_rc("service vgcd stop")
         
      linux = self.host.cat_etc_issue()
      
      found_build = 0
      for server in ["cloudy.virident.info","soloarium.virident.info","172.16.34.160","172.16.34.233"]:
          if found_build == 1:
                  break
          for pathType in ["packages","releases"]:
            
            try:
               
                 fwPath,fwTar,fwDir = Util.get_vgc_fw_path(build,linux,pathType = pathType,emc = emc,server = server)
                 self.host.wget_file(fwPath)
                 found_build = 1
                 break
              # if failed due to rpm installation error, continue, else
              # catch in except and raise
            except RpmError,e:
                 trace_info(e)
                 trace_info("Seems like install with packages =%s, " \
                  "server='%s' failed, retrying..."%(pathType,server))

                 continue
            except:
                 raise
      if found_build == 0:
               raise ViriError("Could not install the build")
     
      #fwTar = "vgc-firmware-60940.C7.tar.gz"
      #fwDir = "vgc-firmware-60940.C7"
      self.host.run_command_chk_rc("tar -xvzf %s"%fwTar)
      
      # cd to fw directory, other wise it will fail
      self.host.run_command_chk_rc("cd %s"%fwDir)
      
      script = "vgc-update.sh"
      if status == "downgrade":
         script = "vgc-downgrade.sh"
      
      for string in ['auto','yes']:
         try:
            
            self.host.run_command_chk_rc("./%s --%s"%(script,string),timeout = 3600)
                       
         except CommandError:
            print "Firmware upgrade/downgrade with %s Failed,retrying.."%string
            continue
         except:
            print "Trying again....."
            continue
         break
      else:
         print "ERR: Some error happend installing firmware downgrade, [auto/yes] did not work"
         sys.exit(1)
      
      # cd back
      self.host.run_command_chk_rc("cd")
      
      trace_info("Firmware %s seem to be done"%status)
      
      #self.host.power_cycle()
      return 1
   
   def get_servers(self):
      return ["solarium.virident.info","cloudy.virident.info"]
   
   def get_path_types(self):
      return ["packages","releases"]
      

  
    


