#from FileSystems import IO
from IOS import IO
from Util import *

SSDBENCH_L3_DOWNLOAD_PATH = "http://spica/sqa/tests/ssdbench_l3.tar.gz"

"""
Runs ssdbench l3 , marketing performance scripts also on support page
takes about 1 day and half to run,will print the result


TO DO, to see the progress, of the script best is see the csv file which the test creates
in the end

It also create 'ssdbench_l3.xls' excel file that can be used for comparisons

Example of the csv script the test outputs:

[root@sqa11 ~]# tail -f ssdbench_l3/summary.ssdbench_l3.vgcb0.csv
Thu Dec  5 07:54:03 PST 2013
analytics,vgcb0,ttl,983.3466796875,wrbwmbs,97.6259765625,wriops,781,rdbwmbs,885.720703125,rdiops,7085
checkpointing,vgcb0,ttl,24786,wrbwmbs,96.8232421875,wriops,24786,rdbwmbs,0,rdiops,0
hft,vgcb0,ttl,162543,wrbwmbs,79.3671875,wriops,162543,rdbwmbs,0,rdiops,0
db8kpage,vgcb0,ttl,25035,wrbwmbs,87.4794921875,wriops,11197,rdbwmbs,108.1103515625,rdiops,13838
bigblock,vgcb0,ttl,104.064453125,wrbwmbs,104.064453125,wriops,208,rdbwmbs,0,rdiops,0
oltp,vgcb0,ttl,90862,p99rd,63381,p99wr,27481

TO DO , more details of the script to be put

Example script:

#!/usr/bin/python
from ViriImports import *
import  FileSystems.SSDBenchL3
hostObj = create_host(sys.argv[1])
devPart = (/dev/vgca0')
sb = FileSystems.SSDBenchL3.ssdbenchl3(hostObj)
sb.run(devPart)


"""

class ssdbenchl3(IO):
    
    """ class in inherits from IO"""

    def download(self):
        
        """
        
        downloads ssdbench l3 ,removes ssdbench_l3, if exists
        """
        
        # Clean up, remove any files
        self.host.run_command("rm -rf ssdbench_l3")
        self.host.run_command("rm -rf ssdbench_l3.tar.gz")
        
        self.host.wget_file(SSDBENCH_L3_DOWNLOAD_PATH)
        self.host.untar_and_unzip_file("ssdbench_l3.tar.gz")
    
    def run(self,devPart):
        """
        inputs : takes devices as example , '/dev/vgca0'
        description: runs ssdbench l3
        returns : output of ssdbench, see example above of sample file
        
        """
        self.download()
        self.host.run_command_chk_rc("cd ssdbench_l3/ && ./ssdbench_l3.sh dummy %s"%devPart)
        trace_info("Results for drive %s"%devPart)
        
        removeDev = remove_dev(devPart)
        
        # File name that ssdbench l3 creates
        file1 = "summary.ssdbench_l3.%s.csv"%removeDev
        file1 = "ssdbench_l3/%s"%file1


        o = self.host.run_command_chk_rc("cat %s"%file1)
        for l in o['output']:
         print l
         
        return o['output']


       