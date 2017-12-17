#!/usr/bin/python
import sys
import  time
from Parsers import *
from Trace import *
from Util import *
from Host import *
FIO = "/root/sqa-1.2/perf-tests/fio"

class IO:
    def __init__(self,host):
        self.host = host
        #self.device = device
class FIO(IO):


    # some output from fio man page
        # rwmixcycle=int
        #     How many milliseconds before switching between reads and writes for a mixed workload. Default: 500ms.
        # rwmixread=int
        #     Percentage of a mixed workload that should be reads. Default: 50.
        # rwmixwrite=int
        #     Percentage of a mixed workload that should be writes. If rwmixread and rwmixwrite are given and do not sum to 100%,
        #     the latter of the two overrides the first. This may interfere with a given rate setting,
        #     if fio is asked to limit reads or writes to a certain rate. If that is the case, then the distribution may be skewed. Default: 50.
        #
        # do_verify=bool
        #     Run the verify phase after a write phase. Only valid if verify is set. Default: true.
        # verify=str
        #     Method of verifying file contents after each iteration of the job. Allowed values are:
        #
        # loops=int
        #     Specifies the number of iterations (runs of the same workload) of this job. Default: 1.
        # time_based
        #     If given, run for the specified runtime duration even if the files are completely read or written.
        #     The same workload will be repeated as many times as runtime allows.
        # norandommap
        #     Normally fio will cover every block of the file when doing random I/O.
        #     If this parameter is given, a new offset will be chosen without looking at past I/O history.
        #     This parameter is mutually exclusive with verify.
        #
        # overwrite=bool
        #     If writing, setup the file first and do overwrites. Default: false.
        # blocksize_range=irange[,irange], bsrange=irange[,irange]
        #     Specify a range of I/O block sizes. The issued I/O unit will always be a multiple of the minimum size,
        #     unless blocksize_unaligned is set. Applies to both reads and writes
        #     if only one range is given, but can be specified separately with a comma seperating the values.
        #     Example: bsrange=1k-4k,2k-8k. Also (see blocksize).
        #
        # size=int
        #     Total size of I/O for this job. fio will run until this many bytes have been transfered, unless limited by other options (runtime, for instance).
        #    Unless nrfiles and filesize options are given, this amount will be divided between the available files for the job. If not set,
        #     fio will use the full size of the given files or devices.
        #     If the the files do not exist, size must be given. It is also possible to give size as a percentage between 1 and 100.
        #     If size=20% is given, fio will use 20% of the full size of the given files or devices.
        # fill_device=bool, fill_fs=bool
        #     Sets size to something really large and waits for ENOSPC (no space left on device) as the terminating condition.
        #     Only makes sense with sequential write. For a read workload, the mount point will be filled first then IO started on the result.
        #     This option doesn't make sense if operating on a raw device node, since the size of that is already known by the file system.
        #     Additionally, writing beyond end-of-device will not return ENOSPC there.
        # --output=filename
        #
    def _if_param_passed_append(self,param,str,comm):

            # argument that don't take any arguments, for example , --thread, 
            #--thread=0 is error
            no_arg_params = {"group_reporting":1,
                              "thread":1,
                              "time_based":1,
                              "norandommap":1}

            if param:

                if no_arg_params.has_key(str):
                    append = " --%s"%str
                else:
                    # add --size=500G, as example 
                    append = " --%s=%s"%(str,param) 
                comm= comm + append

            return comm


    # default values 1 means enable, for example, thread=1 means --thread will
    # be appended to fio
    def _run(self,
            rw,  #read = Sequential reads,write=Sequential writes,randread = Random Read, 
                 #randwrite=Random write,rw mixed sequential reads and writes, 
                 #randrw=mixed random,reads and writes
            size = None, # size be defalut is none which means the whole deisk
            name = "jobs",
            thread = 1, # thread by default is enabled
            ioengine = "psync",
            iodepth = 0,
            bs = 0 ,
            bsrange = 0,
            numjobs = 1 ,
            runtime = 60,
            rwmixwrite = 0,
            rwmixread = 0,
            rwmixcycle = 0,
            fsync = 0,
            end_fsync = 1 ,
            norandommap = 1,
            randrepeat = 0,
            time_based = 1,
            direct =1,
            invalidate = 1,
            group_reporting = 1,
            eta = "never",
            do_verify = None,
            verify_str = None,
            sync = 0,
            loops = 0,
            fill_device = 0,
            output = 0,
            ):
           #comm = FIO + " --name=job --filename= " + device + "--size=500G --bs=4K " + \
           #        " --time_based --runtime=60 --numjobs=1 --ioengine=libaio " + \
           #        "--iodepth=256 --invalidate=1 --rw=randread --rwmixread=100 " + \
           #        "--group_reporting  --direct=1 --norandommap --randrepeat=0 " + \
           #        "--eta=never --thread"
           FIO = "/root/sqa-1.2/perf-tests/fio"

           self.check_if_rw_valid(rw) # check if rw has valid

           if (bs == 0 and bsrange == 0):
               print "Both block size and bsrange are zero, please pass one with non zero values"
               sys.exit(1)
           if bs and bsrange :
               print "Both block size and bsrange are defined, please pass only one with defined value"
               sys.exit(1)

           self.check_if_ioengine_valid(ioengine)

           if ioengine == "libaio" and iodepth == 0:
               print "ioengine is libaio, but iodepth = 0"
               print "Please pass iodepth with non zero value"
               sys.exit(1)

           self.if_param_zero_one(rwmixwrite,"rwmixwrite")
           self.if_param_zero_one(rwmixread,"rwmixread")
           self.if_param_zero_one(rwmixcycle,"rwmixcycle")
           self.if_param_zero_one(fsync,"fsync")
           self.if_param_zero_one(end_fsync,"end_fsync")
           self.if_param_zero_one(norandommap,"norandommap")
           self.if_param_zero_one(randrepeat,"randrepeat")
           self.if_param_zero_one(time_based,"time_based")
           self.if_param_zero_one(direct,"direct")
           self.if_param_zero_one(invalidate,"invalidate")
           self.if_param_zero_one(group_reporting,"group_reporting")

           # initialize minimum command needed
           comm = "%s --name=%s --filename=%s --ioengine=%s --rw=%s --eta=%s --runtime=%i --numjobs=%i --randrepeat=%i"%(FIO,name,self.device,ioengine,rw,eta,runtime,numjobs,randrepeat) 

            # optional parameters to append
            # if size is passed, append size to the command
           comm = self._if_param_passed_append(size,"size",comm)
           comm = self._if_param_passed_append(end_fsync,"end_fsync",comm)
           comm = self._if_param_passed_append(iodepth,"iodepth",comm)
           comm = self._if_param_passed_append(norandommap,"norandommap",comm)
           comm = self._if_param_passed_append(time_based,"time_based",comm)
           comm = self._if_param_passed_append(direct,"direct",comm)
           comm = self._if_param_passed_append(invalidate,"invalidate",comm)
           comm = self._if_param_passed_append(group_reporting,"group_reporting",comm)
           comm = self._if_param_passed_append(rwmixwrite,"rwmixwrite",comm)
           comm = self._if_param_passed_append(rwmixread,"rwmixread",comm)
           comm = self._if_param_passed_append(rwmixcycle,"rwmixcycle",comm)
           comm = self._if_param_passed_append(do_verify,"do_verify",comm)
           comm = self._if_param_passed_append(verify_str,"verify",comm)
           comm = self._if_param_passed_append(loops,"loops",comm)
           comm = self._if_param_passed_append(fsync,"fsync",comm)
           comm = self._if_param_passed_append(sync,"sync",comm)
           comm = self._if_param_passed_append(fill_device,"fill_device",comm)
           comm = self._if_param_passed_append(output,"output",comm)
           comm = self._if_param_passed_append(bs,"bs",comm)
           comm = self._if_param_passed_append(thread,"thread",comm)

           print "INFO: Runnning FIO command = '%s'"%comm
           #sys.exit(1)

           regex_verify = "err=\s*0"


           o = self.host.run_command_verify_out(comm,verify_regex = regex_verify)
           out = o['output']

           return parse_fio_output(out)
    
    def run(self,dev_p,bs,time,rw,ioengine = "psync",numjobs="256",rw_perc = None,ba = None, fsync = None,size = None):
       
        dir  = "/root/fio6"
	fioFile = "fio-" + self.host.cat_etc_issue()
	fioFilePath = dir + "/" + fioFile
        cmd = "%s --name=job --filename=%s --time_based --runtime=%s --numjobs=%s --ioengine=%s  --invalidate=1  --group_reporting      --eta=never --thread --norandommap"%(fioFilePath,dev_p,time,numjobs,ioengine)
        
	
		#self.host.rmdir(dir)
	self.host.mkdir(dir,force = 1)
	self.host.run_command_chk_rc("cd %s"%dir)
	self.host.wget_file("http://spica/sqa/tools/%s"%fioFile)
	
	self.host.run_command_chk_rc("chmod +x %s"%fioFile)
	# cd back to current dir
	self.host.run_command_chk_rc("cd")
		
		
	# chk if dev pattern is present
	if not re.search("dev",dev_p):
		if not size:
			trace_error("size not passed in fio, with not raw device '%s'"%dev_p)
			sys.exit(1)
        if rw == "randread":
           str = " --rw=randread --rwmixread=100" 
           cmd = cmd + str
        elif rw == "randwrite":
            str = " --rw=randwrite --rwmixwrite=100" 
            cmd = cmd + str
        elif rw == "randrw":
            if not rw_perc:
               trace_error("rw passed as %s but rw percentage is '%s'"%(rw,rw_perc))
               sys.exit(1)
            str = " --rw=randrw --rwmixwrite=%s"%rw_perc 
            cmd = cmd + str
        else:
            print "Unknown rw value in fio"
            sys.exit(1)

        direct_str = " --direct=1"
        if fsync:
            cmd = cmd + " --fsync=%s"%fsync
            direct_str = " --direct=0"

        cmd = cmd + direct_str

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

        #print "INFO: Running fio cmd '%s'"%cmd
        timeout = time + "200"
        #print timeout
        #sys.exit(1)
        print "INFO: Running command '%s'"%cmd
        o = self.host.run_command_chk_rc(cmd,timeout = int(timeout))
        out = o['output']
        return parse_fio_output(out)

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
             
         self.host.run_command_chk_rc(comm,timeout = timeout)
         return 1
     def fill_drive_patt(self,device,pattern = "AA",timeout = 89000):
         dev_size = self.host.get_bdev(device)

         # if you won't catch the exception ,after no space left on device,
         # return code is non zero and command will fail
         try:
             self.write_pattern(device,pattern,count = dev_size,timeout = timeout)
             #self.host.run_command_chk_rc("ls1")
         except CommandError:
             pass
         return 1


     def read_hex(self,device,bs = 32768, count = 1, skip = None,verbose = 1):
       check_if_vgc_part(device)
     #def run(self,o_dev,i_dev,bs,count,seek = 0,hexdump = False):
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

        for p in patt:
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
     
     def runWriteIO(self,outputDevice, bs = "1G",count = "10"):
         
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
       


