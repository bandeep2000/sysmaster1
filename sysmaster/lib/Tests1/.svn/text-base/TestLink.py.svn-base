from Util import *
import sys,re
from Trace import *

DEFAULT_TPLAN = "V2_Linux_3.0"
class testLink:
  def __init__(self):
       
       self.runnable_tcases = {}
       self.tcases          = {}
       self.tplan           = DEFAULT_TPLAN

  def get_platform_string(self,distro,card):
      
      plat_prefix = { "redhat6" : "RHEL 6.x (x86)-",
                      "redhat5" : "RHEL 5.x (x86)-",
                      "sles11sp1": "SLES 11 SP1-",
                      "sles11sp2": "SLES 11 SP2-",}
      
      card_string = {"2.2TB": "2200",
                     "550GB": "550",
                     "1.1TB": "1100"}
      
      string = plat_prefix[distro] + card_string[card]
      
      return string
  
  def get_build_string(self,build):
      
      print utils_split_build(build)
      s1,s2 = utils_split_build(build)
      
      string = "Release %s.%s"%(s1,s2)
      
      return string
  
  def run(self,command):
      
      trace_info("TestLink: Running cmd '%s'"%command)

      output = utils_run_os_command_using_command(command,errorStrings = ["error","ERROR"])
      
      # TO DO need to remove the first element
      return output
  
  def get_runnable_tcases(self):
      
      if   self.runnable_tcases:
	  return self.runnable_tcases
	  
      #runnable_tcases = {}
      for l in self.run('tlink list test_cases_runnable --tplan "%s"'%self.tplan):
	  
	  self.runnable_tcases[l] = 1
      
      return self.runnable_tcases
      
  def get_tcases(self):
      
      if   self.tcases:
	  return self.tcases
      
      #self.tcases= self.run('tlink list test_cases --tplan "%s"'%self.tplan)
      
      for l in self.run('tlink list test_cases --tplan "%s"'%self.tplan):
	  
	  self.tcases[l] = 1

      return self.tcases
   
  def is_tcase_runnable(self,tcase):
      
      if self.get_runnable_tcases().has_key(tcase):
	  trace_info("'%s'tcase is runnable "%tcase)
	  return True
      
      #for l in self.get_runnable_tcases().keys():
      #  if re.search(l,tcase):
      #	     raise ViriError("Found tcase from tlink '%s' but comparision as '%s'"%(l,tcase))
      trace_info("'%s'tcase is not runnable "%tcase)
      return False
      #raise ViriError("Testcase '%s' is not runnable/present"%tcase)
 
  def update_test_case(self,tcase,build,distro,card,status) :
      
      #if status != "f" and status != "p":
      #  print "status %s value not passed correctly, valid is f or p"%status
      #	  sys.exit(1)
      
      self.is_tcase_runnable(tcase)
      # return RHEL ..2200 from  redhat6 , 2.2TB  
      platform = self.get_platform_string(distro,card)
      
      build    = self.get_build_string(build)
 
      cmd = 'tlink report %s --tplan "%s" --tcase "%s" --build "%s" --platform "%s"'%(status,self.tplan,tcase,build,platform)
      
      trace_info("Running  command '%s'"%cmd)
     
      self.run(cmd)
 
      
      return 1
       
   
   
 
       
       
