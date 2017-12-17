#!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
#from Host import *
#from Host import CommandError
from VgcUtils import *
from Gnuplot import *
from Config.ConfigFile import configFile


from VirExceptions import *
FIO = "/root/sqa-1.2/perf-tests/fio"

# vdbench defaults
DEFAULT_SEEKPCT = "100"
DEFAULT_RDPCT = "0"
DEFAULT_PRINTINTERVAL = "10"

"""
Usage Example:
#!/usr/bin/python
from ViriImports import *
h1 = "sqa12-redhat6"
h = Host(h1)
io = vdbench(h)

dict = { 'devices':
           {
               '/dev/vgca0': { 'threads': '16','bs':'4096','rdpct':'0','offset':'2048','seekpct':'100','offset': "2048"},
               '/dev/vgcb0': { 'threads': '16','bs':'4096','rdpct':'0','offset':'2048'},
           },
         'verify' : True,
         'time' : '15',
         'printInterval':'5',
}
print io.run(dict)
~

"""

class InvalidIOParam(Exception):
     pass

class IO:
    def __init__(self,host):
        self.host = host
        self.iostatDir = " "
        self.vgcMonWrites    = {}
        self.diskstatsWrites = {}
    
	self.stimulus = 0

    def set_stimulus(self,stimulus = 1):
        
        trace_info("Setting stimulus '%i' flag for IOs"%stimulus)
        self.stimulus = stimulus
        
    def startiostat(self,dir,file,timeGap = "10"):
        
        trace_info("Using iostat dir as %s file %s"%(dir,file))
        
        filePath = "%s/%s"%(dir,file)
        
        self.iostatDir = dir
        self.host.createDirifNotExists(self.iostatDir)
        if (self.host.if_file_exists("%s/%s"%(self.iostatDir,file))):
            trace_info("Seems like file  %s exists, removing it"%filePath)
            self.host.run_command_chk_rc("rm -rf %s"%filePath)
            
	bgFile =  "%s/%s"%(self.iostatDir,file)
      
        cmd = "iostat -mx %s "%(timeGap)
        self.host.run_command(cmd,bg = True, bgFile = bgFile)
        return 1
    
    def stopiostat(self):
        trace_info("Stopping iostat on directory %s"%self.iostatDir)
        
        #self.host.run_command("fuser -k %s/"%self.iostatDir)
        #kill -9 `pidof iostat`
        # To do , fuser is not working 
        #self.host.run_command("kill -9 `pidof iostat`")
	self.host.run_command("killall iostat")
	self.host.run_command("killall vmstat")
        return 1
    
    def setWrites(self,devPart):
        
        #self.host.run_command_chk_rc("sync")
        #sleep_time(2,"")
        
        vm = vgcMonitor(self.host)
        self.vgcMonWrites[devPart] = int(vm.getCardPartWrites(devPart))
        self.diskstatsWrites[devPart] = int(self.host.cat_proc_diskstats(devPart,type = "writes"))
        
        self.setwrites = 1
        
    def getWriteAmp(self,devPart):
        
        if not self.setwrites:
            raise InvalidIOParam("Write Amp called without setting the set Writes")
        
        #self.host.run_command_chk_rc("sync")
        #sleep_time(2,"")
        vm = vgcMonitor(self.host)
        vgcMonWrites     = int(vm.getCardPartWrites(devPart))
        diskstatsWrites  = int(self.host.cat_proc_diskstats(devPart,type = "writes"))
        
        vmDiff = vgcMonWrites - self.vgcMonWrites[devPart]
        
        sectorSize = 512
        
        diskStatsDiff = diskstatsWrites - self.diskstatsWrites[devPart] 
        
        diskStatsDiffBytes = diskStatsDiff * sectorSize

        try:
           amp = vmDiff/diskStatsDiffBytes
        except ZeroDivisionError:
           amp = "N/A"
           trace_info("disk stats diff found 0, making write Amp as '%s'"%amp)
           return amp

        trace_info("Writeamp for device '%s' = %i"%(devPart,amp))
        return amp


class FIO(IO):

    def download(self):
       fioFile = "fio-" + self.host.cat_etc_issue()
       #this could be removed
       fioFilePath = "./" + fioFile
       fioDownloadPath = "http://spica.virident.info/sqa/tools/"
       
       if not self.host.if_file_exists(fioFilePath):
	  self.host.wget_file("%s/%s"%(fioDownloadPath,fioFile))
	
	  self.host.run_command_chk_rc("chmod +x %s"%fioFile)

    def run(self,dev_p,bs,time,rw,ioengine = "psync",numjobs="256",rw_perc = None,
                 ba = None, fsync = None,size = None,iodepth = None,
		 fill_drive = None,verify = None, bg = False,mntPoint =
		 None,cpus_allowed = None,name = "job"):
       
        # mysql -h centos1 -u root -p
        if fill_drive:
            # TO DO this should be a function in host
            trace_info("Filling drive '%s'"%dev_p)
            self.host.run_command("dd if=/dev/zero of=%s bs=1G oflag=direct"%dev_p)
        
        
        dir  = "/root/fio6"
	fioFile = "fio-" + self.host.cat_etc_issue()
        #size = "10G" # Remove this
        
	#fioFilePath = dir + "/" + fioFile
        fioDeviceName = dev_p
        
        if mntPoint:
          #device,mnt_point,filesys
          # TO DO umounting this first, using file1 mount, should be user configurable
          self.host.run_command("umount %s"%dev_p)
          #mnt = "/file1"
          
          # remove dev in /dev/vgca0 
          mnt = "/nand1-" +  dev_p.replace("/dev/",'')
          if not size:
               raise InvalidIOParam("Fio: device %s not raw device,size value '%s' is not defined"%(dev_p,size))
          self.host.mount_fs_all(dev_p,mnt, mntPoint['filesys'])
          fioDeviceName = mnt + "/file2"
        
        #this could be removed
        fioFilePath = "./" + fioFile
        cmd = "%s --name=%s --filename=%s --time_based --runtime=%s --numjobs=%s --ioengine=%s  --invalidate=1  --group_reporting --randrepeat=0   --eta=never --thread --norandommap"%(fioFilePath,name,fioDeviceName,time,numjobs,ioengine)

	if cpus_allowed != None:
		cmd = cmd + " --cpus_allowed=%s"%cpus_allowed
        
        # sync and libaio seem to have io depth
        if ioengine == "sync" or ioengine == "libaio":
           if ioengine == "libaio":
             if not iodepth:
                raise ViriError("fio ioengine passed as libaio, but iodepth not passed")
             cmd = cmd + " --iodepth=%s"%iodepth
        
	iostatFile = "iostat-bs-%s-ba-%s-ioengine-%s-threads-%s"%(bs,ba,ioengine,numjobs)
        iostatFile = time_stamp_file(iostatFile)
	        
        fioDownloadPath = "http://spica.virident.info/sqa/tools/"
        #self.host.rmFileifExists(fioFile)
        if not self.host.if_file_exists(fioFilePath):
	  self.host.wget_file("%s/%s"%(fioDownloadPath,fioFile))
	
	  self.host.run_command_chk_rc("chmod +x %s"%fioFile)
	
        rawDevice = 1
        if not isRawDevice(fioDeviceName):
            if not size:
                raise InvalidIOParam("Fio: device %s not raw device,size value '%s' is not defined"%(dev_p,size))
            rawDevice = 0

        if rw == "randread":
           str = " --rw=randread --rwmixread=100" 
           cmd = cmd + str
        elif rw == "randwrite":
            str = " --rw=randwrite --rwmixwrite=100" 
            cmd = cmd + str
        elif rw == "write":
            str = " --rw=write --rwmixwrite=100" 
            cmd = cmd + str
        elif rw == "read":
            str = " --rw=read --rwmixread=100" 
            cmd = cmd + str
        elif rw == "randrw":
            if not rw_perc:
               trace_error("rw passed as %s but rw percentage is '%s'"%(rw,rw_perc))
               sys.exit(1)
            str = " --rw=randrw --rwmixwrite=%s"%rw_perc 
            cmd = cmd + str
        elif rw == "rw" or rw == "readwrite":
            if not rw_perc:
               trace_error("rw passed as %s but rw percentage is '%s'"%(rw,rw_perc))
               sys.exit(1)
            str = " --rw=rw --rwmixwrite=%s"%rw_perc 
            cmd = cmd + str
        else:
            print "Unknown rw value in fio",rw
            raise InvalidIOParam ("Fio rw unknown value passed")
            sys.exit(1)

        direct_str = " --direct=1"
        if fsync:
            cmd = cmd + " --fsync=%s"%fsync
            direct_str = " --direct=0"

        cmd = cmd + direct_str

        if size == "None":
		size = None
        if size:
            cmd = cmd + " --size=%s"%size

        # if - is given in blocksize, use bsrange, otherwise use bs
        if re.search("-",bs):
            cmd = cmd + " --bsrange=%s"%bs
        else:
            cmd = cmd + " --bs=%s"%bs

        # if block aligned is given
        if ba:
            cmd = cmd + " --ba=" + ba

        if verify:
            #cmd = " --verify=crc32c-intel --verify_fatal=1 --verify_dump=1"
            cmd = cmd + " --verify=%s --verify_fatal=1 --verify_dump=1"%verify

        timeout = time + "200"
        
        wrtAmp = "N/A"
        found_vdent_dev = 0
        if re.search( ".*vgc[a-z]+\d$",dev_p):
          found_vdent_dev = 1
          self.setWrites(dev_p)
          
        #if if_vgc_dev_part(dev_p):
            #self.setWrites(dev_p)
        #print "INFO: Running command '%s'"%cmd
        
        # TO DO add iostat with bg
        if bg:
            trace_info("Running fio command in bg")
            self.host.run_command(cmd,timeout = int(timeout),bg = bg)
            self.host.chkIfProcessRunning("fio")
        
            return 1

        gc_triggered = "GC-N/A"
        # Gheck GC
        if found_vdent_dev:
          gc_triggered = "gc-no"
          trace_info("Checking gc status before running the test")
          if self.host.is_gc_running(dev_p):
               gc_triggered = "gc-b"
          
              
        # start command here
        
        
	self.startiostat("ioDir",iostatFile)
        o = self.host.run_command_chk_rc(cmd,timeout = int(timeout))
        self.stopiostat()
        
        # Check GC
        if found_vdent_dev:
          trace_info("Checking gc status after running the test")
          if self.host.is_gc_running(dev_p):
               #if gc was already triggered, leave it as b,
               # b means before suggesting gc was already triggered before the test was running
               
               if not gc_triggered == "gc-b":
                    
                  gc_triggered = "gc-a"
        
        # TO DO, without raw device plost not working
        plot = 'plotN/A'
        iostatFile1 = "N/A"
        if rawDevice:
          iostatFile1 = "/root/ioDir/%s"%iostatFile
	  plot = plot_host_iostat(self.host,fioDeviceName,[iostatFile1],verbose = 0,graphFileDetails = iostatFile)

        out = o['output']
        rc = o['rc']
        
        #if if_vgc_dev_part(dev_p):
        if found_vdent_dev:
            wrtAmp = self.getWriteAmp(dev_p)
        
	printOutput(out)
	self.host.is_crash_dir_empty()

	if self.stimulus == 1:
           #self.host.restartVgcDriver()
           self.host.power_cycle()
        #print parse_fio_output(out),rc,wrtAmp,gc_triggered,plot
        dictFio = parse_fio_output(out)
        dictFio['iostatFile'] = iostatFile1
        dictFio['wa'] = wrtAmp
        dictFio['gc'] = gc_triggered
        dictFio['plot'] = plot

        return dictFio
     

    def rw(self,dictValues):
     
          """
          Usage from ViriImports import *
          h = create_host("c240m3-1")
          
          h.fio().run1({'devPart':'/dev/vgca0','time':'10')

          fio = h.fio()
          fio.set_stimulus()
          fio.rw(dict(devPart = '/dev/vgca0',time = '30',
             mntPoint = {'filesys':'ext3'},size = "100G" ))
          
          """
          
          return self.run(
                    dev_p = dictValues['devPart'],
                    time = dictValues['time'],
                    bs       = dictValues.get('bs',"4K"),
                    
                    rw       = dictValues.get('rw',"randrw"),
                    
                    ioengine = dictValues.get('ioengine',"libaio"),
                    iodepth  = dictValues.get('iodepth',"1"),
                    numjobs  = dictValues.get('numjobs',"256"),
                    rw_perc  = dictValues.get('rw_perc',"50"),
                    ba       = dictValues.get('ba',None),
                    mntPoint = dictValues.get('mntPoint',""),
                    fsync    = dictValues.get('fsync',""),
                    verify   = dictValues.get('verify',""),
                    size     = dictValues.get('size',""),
                    bg       = dictValues.get('bg',False),
                    cpus_allowed = dictValues.get('cpus_allowed',None),
                    name     = dictValues.get('name',"job")
   
   
                  )


    
    def perf(self,dictValues ):
          """ dictValues = {'devPart': devPart, 'time': time, 'gc': 0, 'rws':['randwrite'],'bss':['4K'],'threads':['1']}"""
          self.set_stimulus(stimulus = 0)
          self.drive_filled = 0
          dict = {}
          
          
          time = dictValues['time']
          devPart = dictValues['devPart']
          gc = dictValues['gc']
          bg = False
          
          size = "1G"
          #  remove G for dd
          # Note Need to change Logic here!!!!, it work only if G is given
          if  dictValues.has_key('size'): size = dictValues['size']
          dd_size = size.rstrip('G')
          
          
                  
          
          bss     = ['4K','8k','16K']
          rws     = ['randwrite','randread','write']
          threads = ['1','16','256']
          if  dictValues.has_key('bss'): bss = dictValues['bss']
          if dictValues.has_key('rws'):rws = dictValues['rws']
          if dictValues.has_key("threads"): threads = dictValues['threads']
          
          
          reset_done_initially = 0
          
          for bs in bss:
            for rw in rws:
               if "read" in rw:
		       
                 if self.drive_filled == 0:
                   self.host.device(devPart).fill_drive(size = dd_size) # TO DO
                   #print "Hee";sys.exit(1)
                   self.drive_filled = 1
                   
             
               for th in threads :
                 trace_info_dashed("Running test for bs bs %s,rw %s,threads %s, gc = %i"%(bs,rw,th,gc))
                 key = "%s-%s-%s"%(bs,th,rw)
                 
                 dev = self.host.device(devPart)
                 # if gc, make sure it is runnning,else not gc, reset device,
                 # if it is running

                 if gc == 1:
                    dev.create_gc()
                 elif gc == 0:
                    # in quick loops, you don't want to reset everytime
                    if reset_done_initially == 0:
                       dev.reset()
                       reset_done_inititally = 1
                    else:
                    
                       dev.is_gc_running_reset()
                       
               
                 dict[key] = self.run(
                    devPart,
                    bs = bs,
                    time = time,
                    rw = rw,
                    ioengine = "libaio",
                    numjobs = th,
                    iodepth = "1",
                    ba = None,
                    size = size,
                    bg = bg,
                    mntPoint = "")
                 # TO DO , power cycle
                 if bg:
                    wait_time = int(time) - 10
                    sleep_time(wait_time, "After running fio")
                    self.host.power_cycle() # Stimulus TO DO
          #print dict;sys.exit(1)
          self.print_perf(dict)
          return dict

    def verify(self,devPart,size = "1M"):
        
        
        self.download() 
        
        # always use hexa decimal,since fio might no fail
        verify_pattern = "0x112"
        
        for rw in ["randwrite", "randread"]:
            cmd = ("./fio-redhat6 --name=perf  --numjobs=4 --iodepth=1 --ioengine=libaio  --invalidate=1 " +
              "--group_reporting --thread --norandommap  --bs=4K  --filename=%s --direct=1 --verify=meta  "%devPart + 
              " --rw=%s --size=%s --eta=never --verify_pattern=%s"%(rw,size,verify_pattern))
            
            if rw == "randread":
               cmd = cmd  + " --verify_fatal=1 --verify_dump=1"
               self.host.power_cycle()
               #self.host.run_command_chk_rc("service vgcd restart")
               pass
            self.host.run_command_chk_rc(cmd)
        
        trace_info("Fio Data Verification succeded")

     
     
    def print_perf(self,dictAll):
     
     print "wload,",
     for rw in ['read','write']:
       for k in ['iops','runt','bw','avglat']:
         print "%s-%s,"%(k,rw),
     print "wa",
     print "gc,",
     print "plot,",
     
     for wload in dictAll.keys():
         dict = dictAll[wload]
         print ""
         print "%s,"%wload,
         for rw in ['read','write']:
             for k in ['iops','runt','bw','avglat']:
                 print "%s,"%dict[rw][k],
         print "%s,"%dict['wa'],
         print "%s,"%dict['gc'],
         print "%s"%dict['plot'],

     
        
    def check_if_rw_valid(self,rw):
        dict = {'read'    :1,
                'write'   :1,
                'randread':1,
                'rw'      :1,
                'randrw'  :1 }

        return self.check_valid_param(dict,rw,"rw")
    
    def check_if_ioengine_valid(self,ioengine):
        dict = {'sync'    :1,
                'psync'   :1,
                'vsync'   :1,
                'libaio'   :1,
                'posixaio'   :1,
                'solarisaio'   :1,
                'windowsaio'   :1,
                'mmap'   :1,}
        
        return self.check_valid_param(dict,ioengine,"ioengine")
    
    # simulates mysql load
    def fioMultipleSync(self,dict):
	
	devPart = dict['devPart']
	time    = dict['time']
	# to do just do one variabl
	partType = "soft"
	# get devices partitions after partitioing
	devices = self.host.get_create_partitions(devPart,partitions ="2",partType = "soft",modes = "random")
	
	firstDevice = devices[0]
	
	secondDevice = devices[1]
	
	runtime = time
	# start in background
	# to do , this shold check if both the threads are running
	self.run(firstDevice,
                bs        = "16K",
                time      = runtime,
                rw        = "randrw",
                ioengine  = "psync",
                numjobs   = "256",
                rw_perc   = "50",
                ba        = None, 
                fsync     = None,
                size      = None,
                iodepth   = None,
                fill_drive = None,
                verify     = None,
                bg         = True)
        
        self.run(secondDevice,
                bs = "512",
                time = runtime,
                rw = "write",
                ioengine = "psync",
                numjobs  = "1",
                rw_perc  = None,
                ba       = None, 
                fsync    = "8",
                size     = None,
                iodepth  = None,
                fill_drive = None,
                verify     = None)
	
	#clean up
        if partType == "soft":
           self.host.parted.remove_all_partitions(devPart)
        
        
        # reset card, if hard partition
        if partType == "hard":
	   
	   dev = get_device_part(devPart)
	   self.host.vgcconfig.resetCard(dev)

        

    # check if valid values are integer 1 or 0
    def if_param_zero_one(self,param,param_str):
        dict = {0    :1,
                1    :1}
        return self.check_valid_param(dict,param,param_str)


    def check_valid_param(self,dict,param, param_str):
        
        if dict.has_key(param):
            return 1

        print "ERR: parameter '%s' doesn't have valid values"%param_str
        print "Valid Values are:"
        for key in dict:
            print key
        sys.exit(1)

    def run_io (self,rw,size = None,numjobs = 256, ioengine = "psync",runtime = 60,iodepth = 0 ,rwmixwrite = 0, rwmixread = 0,rwmixcycle = 0,bs = 0, bsrange =0, fsync = 0  ):
        """ does random read writes by default,
        takes device , size as input, 
           block size as input"""
        return self._run(runtime = runtime, iodepth = iodepth,rwmixwrite = rwmixwrite,rwmixread = rwmixread,rwmixcycle = rwmixcycle,bs = bs,bsrange = bsrange,fsync = fsync,size = size,rw = rw,numjobs = numjobs,ioengine = ioengine)

    def run_randomio(self,size = None,bs = "4K",bsrange = 0,runtime = 60 ,rwmixwrite = 0,rwmixread = 0,rwmixcycle =0 ,fsync = 0, rw = "randrw",numjobs = 1):
        return self.run_io(size = size,bs = bs,bsrange = bsrange,rw = rw,rwmixwrite = rwmixwrite ,rwmixread = rwmixread,rwmixcycle = rwmixcycle,fsync = fsync,runtime = runtime,numjobs = numjobs)

class DD(IO):
     def write_pattern(self,device,pattern,bs = 32768,count = 1,timeout = 600,verbose = 1 ):
         check_if_vgc_part(device)
         comm = "dcfldd textpattern=%s of=%s bs=%i count=%i"%(pattern,device,bs,count)
         if verbose:
             trace_info("Writing pattern '%s' on device '%s'"%(pattern,device))
             trace_info("command used '%s'"%comm)
            
         if not self.host.is_binary_present("dcfldd"):
             raise ViriError("dcfldd not present, please download")
         self.host.run_command_chk_rc(comm,timeout = timeout)
         return 1
     def fill_drive_patt(self,device,pattern = "AA",timeout = 89000):
         dev_size = self.host.get_bdev(device)

         # if you won't catch the exception ,after no space left on device,
         # return code is non zero and command will fail
         try:
             self.write_pattern(device,pattern,count = dev_size,timeout = timeout)
             #self.host.run_command_chk_rc("ls1")
         
         except:
             # to do command error is not getting catched here
             pass
         return 1


     def read_hex(self,device,bs = 32768, count = 1, skip = None,verbose = 1):
       check_if_vgc_part(device)
     
       comm = "dd if=%s bs=%i count=%i iflag=direct | hexdump -C"%(device,bs,count)
       if skip:
           comm = "dd if=%s bs=%i count=%i iflag=direct skip=%s | hexdump -C"%(device,bs,count,skip)
       #self.run(
       err = ["No such file or directory"]
       trace_info("Running command '%s'"%comm)
       o = self.host.run_command_verify_out(comm,errors = err)
       o = o['output']

       for l in o:
           regex = "\S+\s+(.*)\|(\S+)\|"
           if re.search(regex,l):
               m = re.search(regex,l)
               patt_hex = m.group(1)
               patt = m.group(2)
       try:
          patt
       except NameError:
          trace_error("Variable patt not defined in command '%s'"%comm)
          raise
          sys.exit(1)
       try:
          patt_hex
       except NameError:
          trace_error("Variable patt_hex not defined in command '%s'"%comm)

          raise
          sys.exit(1)

       return (patt,patt_hex)
     def verify_pattern(self,device,pattern,bs = 32768,count =1,skip = None,verbose = 1):
        patt,patt_hex = self.read_hex(device,bs = bs,count = count,skip = skip)

	split_patt = [patt[i:i+2] for i in range(0, len(patt), 2)]
	for p in split_patt:
	
        #for p in patt:
            if p == pattern:
                continue
            else:
                trace_error("Expected pattern '%s' found '%s'"%(pattern,p))
                sys.exit(1)
        if verbose:
                trace_success("Expected pattern '%s' found '%s' on device '%s'"%(pattern,patt,device))
        return 1
     def verify_pattern_entire_drive(self,device,pattern,bs = 32768,verbose = 1):
         block_dev = self.host.get_blockdev(device)

         last_block = (int(block_dev)/bs) - 33; # just 33 random no, dcfldd end of disk was giving issues

         middle_block = (last_block/2) 

         #offsets = [ last_block, middle_block , 0  ]

         #for oset in offsets:
         while last_block > 0:
             #self.verify_pattern(device = device,pattern = pattern,skip = oset)
             self.verify_pattern(device = device,pattern = pattern,skip = last_block)
             last_block = last_block - 32768

     #def runReadIO(self,

   # by default 40 GB
     def runIO(self,outputDevice,inputDevice ="/dev/zero",bs = "1G",count = "4", flag = "oflag"):
	     comm = "dd if=%s of=%s bs=%s count=%s %s=direct "%(inputDevice,outputDevice,bs,count,flag)
	     self.host.run_command_chk_rc(comm)
             return 1
     
     def runWriteIO(self,outputDevice, bs = "1G",count = "40"):
         
         self.runIO(outputDevice,"/dev/zero",bs,count)
     def runReadIO(self,inputDevice, bs = "1G",count = "10",flag = "iflag"):
         
         self.runIO("/dev/null",inputDevice,bs,count,flag)

    
     def run(self,o_dev,i_dev,bs,count,seek = 0,hexdump = False):
       comm = "dd if=%s of=%s bs=%s count=%i "%(input_dev,bs,count,device)
       if seek != 0:
           comm = command + " seek=" + seek
       if hexdump:
           comm = command + "| hexdump -C" 
       self.run_command_verify_out(comm,timeout = 1000,verify_regex = "record")
       return 1
       
class vdbench(IO):
    
    def __init__(self,host):
        IO.__init__(self,host)
        self.downloaded = 0
        
        self.vbenchBashfile = ""

    def create_command(self,dict):
        
        cmd = []

        # array to store sd1,sd2, this will be used to create line2
        sd = []
        c = 1  # varialle to hold 1 sd1
        # this will create sd=sd1,lun=/dev/vgca0,thread=16,openflags=o_direct
        for device in  dict['devices'].keys():
            threads = dict['devices'][device]['threads']
            sd.append("sd%i"%c)
            line1 = "sd=sd%i,lun=%s,thread=%s"%(c,device,threads)
            try:
                offset = dict['devices'][device]['offset']
                line1 = line1 + ',offset=%s'%offset
            except KeyError:
                pass
    
            try:
                size = dict['devices'][device]['size']
		#print size;sys.exit(1)
                # if size is none
		if size == "None" or not size:
			pass
		else:
                  line1 = line1 + ',size=%s'%size

            except KeyError:
                if not isRawDevice(device):
                 
                      raise InvalidIOParam("Vdbench: device '%s' not raw device,but size is not passed"%device)
                pass
            
            # If raw deivce add o_direct
            if isRawDevice(device):
                line1  =  line1 + ",openflags=o_direct"
            cmd.append(line1)
            c = c + 1
    
        # index to get sd1,sd2
        # this will create vdbench line2 wd...
        sdIndex = 0
        wd = 1
        # create wd line and append to it
        for device in  dict['devices'].keys():
            bs = dict['devices'][device]['bs']
            try:
                rdpct = dict['devices'][device]['rdpct']
            except KeyError:
                print "rdpct not passed for device '%s', using 0"%device
                rdpct = DEFAULT_RDPCT
            try:
                seekpct = dict['devices'][device]['seekpct']
            except KeyError:
                print "seekpct not passed using for device '%s',using 100"%device
                seekpct = DEFAULT_SEEKPCT
    
            line2 = "wd=wd%i,sd=%s,xfersize=%s,rdpct=%s,seekpct=%s"%(wd,sd[sdIndex],bs,rdpct,seekpct)
            cmd.append(line2)
    
            sdIndex = sdIndex + 1
            wd = wd + 1
             
        # initailize printInterval
        try:
          printInterval = dict['printInterval']
        except KeyError:
          printInterval = DEFAULT_PRINTINTERVAL
        # initailize printInterval
        try:
          time  = dict['time']
        except KeyError:
          raise ViriError("Time not defined in vdbench")
          
        # double of printInterval
        p2int = int(printInterval) * 2
        
        if int(time) < p2int:
            raise ViriError("vdbench runtime '%s' should more than double of print Interval time %s, please pass runtime > '%i'"%(time,printInterval,p2int))
       
        line3 = "rd=run1,wd=wd*,iorate=MAX,elapsed=%s,interval=%s"%(time,printInterval)
          
        cmd.append(line3)
        return cmd

    def download(self):
        
        trace_info("Downloading vdbench")
        
        filePathDownload = "http://spica.virident.info/sqa/tools/vdbench.tar.gz"
        
        unTarfile =  self.host.wgetReturnFileName(filePathDownload)
           
        # untar could be improved to automatically find the unzipped file
        vdbenchDir = "vdbench-files"
        #unTarfile = "vdbench.tar.gz"
        
        
        self.host.untar_and_unzip_file(unTarfile)
        
        self.host.rmFileifExists(unTarfile)
        
        self.host.run_command("rm -rf output/") # rm output dir if exisits

        self.vdbenchBashfile = "%s/vdbench.bash"%vdbenchDir
        self.downloaded = 1
 
    # run mulitiple by partitioning
    #def runCreatePartitions(self,devPart,time,partitions,partType = "soft",modes = "random"):
    
    
    def runCreatePartitions(self,dict):
        """ modes is valid for hard partition only, means make 1 as partition as maxperformance,otherwise
        as maxcapacity, takes infut as dictionary"""
        
        #print dict
        devPart    = dict['devPart']
        time       = dict['time']
        partitions = dict['partitions']
        partType   = dict['parttype']
        modes      = dict['modes']
        
        devices = self.host.get_create_partitions(devPart,partitions,partType,modes)
        
        #print devices
        
        if devices == 2:
           trace_info("Seems like card doenst support, two hard partitions")
           return 1
             
        #sys.exit(1)
        
        blocksizes = []
        offsets    = []
        threads    = []
        
        start_blkSize = 4096
        start_offset  = 0
        
        for dev in devices:
            blocksizes.append(str(start_blkSize))
            offsets.append(str(start_offset))
            start_blkSize = start_blkSize * 2
            start_offset = start_offset + 1024
            
            threads.append("16")

        dict = util_create_vdbench_hash(devices,blocksizes,offsets,threads,time)

        self.run(dict)
        
        # cleanup
        # reset card 
        if partType == "hard":
	   
	   dev = get_device_part(devPart)
	   self.host.vgcconfig.resetCard(dev)
	    
        
        #clean up
        if partType == "soft":
           self.host.parted.remove_all_partitions(devPart)
        
        
        return 1
    # most of the
    def run(self,optionsDict):
        """ most of the defaults are for data validation, takes dictionary as input
        
        #!/usr/bin/python
        from Host import Host
        from IOS import *
        h = Host(sys.argv[1])


        v = vdbench(h)
        optionsDict = { 'devices':
           {
               '/dev/vgca0': { 'threads': '16','bs':'4096','rdpct':'0','offset':'2048','seekpct':'100','offset': "2048"},
               '/dev/vgcb0': { 'threads': '16','bs':'4096','rdpct':'0','offset':'2048'},
           },
         'verify' : True,
         'time' : '15',
         'printInterval':'5',
         }


        v.run(optionsDict)
        """

        # data_errors=1
        # sd=sd1,lun=/dev/vgca0,thread=256,openflags=o_direct
        # sd=sd2,lun=/dev/vgcb0,thread=256,openflags=o_direct
        # wd=wd1,sd=sd1,xfersize=16K,rdpct=0,seekpct=100
        # wd=wd2,sd=sd2,xfersize=16K,rdpct=0,seekpct=100
        # rd=run1,wd=wd*,iorate=MAX,elapsed=16h,interval=2

        #if (runtime *2) >= printInterval:
        #    raise  ViriValuePassedError("Vdbench: print interval '%s' is not double '%s', please "%(printInterval,runtime))
        
        # vdbech config command, initializing array
        # then will create file from it
        cmd = []
        
        # there is a bit of risk here,if user changed to another directory using
        # host object, then vdbench will fail
        # this will be hard to debug
        # need to improve logic here
        # 
        
        # by Defauly if True
        
        print optionsDict
        #sys.exit(1)
        verify = True
        try:
            verify = optionsDict['verify']
        except KeyError:
            pass
        
        

        #print verify
        #sys.exit(1)
        cmd = self.create_command(optionsDict)
        
        if verify:
           cmd.insert(0,"data_errors=1")
        print cmd
        #sys.exit(1)
        
        if not self.download():
             self.download()
        
        #print cmd
        
        VDBENCH_CONF_FILE = "vdbench-cfg"
        
        #self.host.run_command_chk_rc("cd /root/megastress1")
        
        self.host.run_command("rm -rf %s"%VDBENCH_CONF_FILE)
        
        for l in cmd:
           self.host.run_command_chk_rc(" echo %s >> %s"%(l,VDBENCH_CONF_FILE))
        
        command =  "%s -f %s "%(self.vdbenchBashfile,VDBENCH_CONF_FILE)
        if verify:
            command = "%s -v"%command
            
        if verify:
          trace_info("vdbench verify flag is set")
        
        timeout = optionsDict['time'] + "200" # just add 200 as extra
        
        trace_info("Starting vdbench command '%s'"%command)
        out = self.host.run_command_chk_rc(command,timeout = int(timeout))
        
        trace_info_dashed("vbench complete with verification flag as '%s' config file as:"%verify)
        
        printOutput(cmd)
        
        return out['rc']
        
        

