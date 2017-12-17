#/usr/local/ltp/testcases/bin/md5_multi_thread_reader -f /dev/sda -b 4096 -n 2 -d 1 -x 512 -r 1 -t 256
import re,sys
#from ViriImports import *

class md5ReaderWriter:

  def __init__(self,host,options = {'bs': "4096",'num_blocks': "2",'direct': "1", 'x' : "512",'random' :"1",'threads' : "1"}):
       self.options = options
       self.host    = host
       self.writer = "/usr/local/ltp/testcases/bin/md5_multi_thread_writer"
       self.reader = "/usr/local/ltp/testcases/bin/md5_multi_thread_reader"
       self.is_write_done = 0

  def run(self,device,read_write):

       if read_write == "write":
          tool = self.writer
       if read_write == "read":
          tool = self.reader
       cmd = "%s -f %s -b %s -n %s -d %s -x %s -r %s -t %s"%(tool,device,self.options['bs'],self.options['num_blocks'],self.options['direct'],self.options['x'],self.options['random'],self.options['threads'])
       o = self.host.run_command_chk_rc(cmd)
       output = o['output']
       
       if len(output[1:]) != 0:
          print "Error: some error occured while running md5sum, it seem to have some output"
          sys.exit(1)
  def read(self,device):
        if self.is_write_done == 0:
           raise ViriErrors
        self.run(device,"read")
  def write(self,device):
        self.is_write_done = 1
        self.run(device,"write")





