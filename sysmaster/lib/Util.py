import os
import sys
import time
import datetime
import re
import ConfigParser
from Trace import *
from VirExceptions import *
from Variables import *
import commands
import urllib2

def chk_status(rc,command,verbose = True):
    exp_rc = 0
    
    if rc != exp_rc:
        print " "
        print "Command Failed: ",
        print "Expected return code for command '%s' is '%i', expected '%i'"%(command,rc,exp_rc)
        print "exiting ..."
        sys.exit(1)
    if verbose == 1:
        print "SUCCESS: Succesfully seem to execute command '%s' as return code is '%i'"%(command,rc)
    
    return 0

def run_os_command(command,verbose = 0):
    rc = os.system(command)
    # expected return code
    exp_rc = 0
    if rc != exp_rc:
        print " "
        print "Command Failed: ",
        print "Expected return code for command '%s' is '%i', expected '%i'"%(command,rc,exp_rc)
        print "exiting ..."
        sys.exit(1)
    if verbose == 1:
        print "SUCCESS: Succesfully seem to execute command '%s' as return code is '%i'"%(command,rc)

    return 0

def utils_run_os_command_using_command(command,errorStrings = []):
    if not is_var_list(errorStrings):
        raise ViriError("errorString not passed as list/array")
    
    rc,output = commands.getstatusoutput(command) 
    chk_status(rc,command)

    output = output.split("\n")
    
    for err in errorStrings:
        for o in output:
	  if re.search(err,o):
	      raise ViriError("Found error string '%s' in output '%s'"%(err,output))
    return output

def compareStr(expected,found,str):
    
    if expected == found:
        trace_info("expected '%s' found '%s' in '%s' "%(expected,found,str))
        return 1
    
    trace_error("'%s' expected '%s' found '%s'"%(str,expected,found))
    sys.exit(1)

def printOutput(output):
    print "("
    for l in output:
        print l
    print ")"
    
    return 1

def utils_if_value_in_brackets(string):
    
    # gets 13 and 12  from  '13 (12 G)',also removes GB example in 20 GB,returns 20
    regex = "(\d+)\s*\((\d+)\s*\S+\)"
    c = re.compile(regex)
    
    if c.search(string):
	m = c.search(string)
	#return m.group(1),m.group(2)
	return m.group(1)
    
    if re.search('(\d+)\s*(\S+)?',string):
       m = re.search('(\d+)\s*(\S+)?',string)
       return m.group(1)

    if re.search('(\d+)\s+.*',string):
       return m.group(1)
    
    return string
    #raise ViriError("Did not find regex '%s' in string '%s'"%(regex,string))

def incrementFileNameIfExists(filePath,ext = None):
    """ takes file as example "file0", return 0 if file doesnt exist increment if exists
     file1 if exitst returns 2 """
    try:
     m = re.search("(.*)(\d+)$",filePath)
     filePathStripped = m.group(1)
     num =  m.group(2)
    except:
     raise ViriValuePassedError("ERR: file '%s' doesnt seem to have number appended"%file)
     
    for c in range(1,100):
       # if file exist increment number
       filePath = filePathStripped + num
       if ext:
         filePath = filePath + "." +  ext
       if os.path.isfile(filePath):
         num = int(num)  + 1
         num = str(num)
         continue
       else:
           break

    return filePath

def ifFileExists(filePath):
    if os.path.isfile(filePath):
        return True
    return False

def chkIfFileExists(filePath):
    
    if ifFileExists(filePath):
       return True
    raise ViriError("File '%s' doesn't exits"%filePath)

# on the host , not on test machine
def rmFileIfExists(filePath):
    if os.path.isfile(filePath):
	os.system("rm %s"%filePath)
    return 1

def createDirectoryifNotExists(directory):
    """creates directory if doens't exits"""
    if not os.path.isdir(directory):
        os.makedirs(directory)

def isStringPresentArray(array,string):

    if  [  l  for l in array if re.search(string,l) ]:
	return 1
    return 0

def chkifStringPresentArray(array,string):
    
    if isStringPresentArray(array,string):
	return True
    raise ViriError("String '%s', not present in array '%s'"%(string,array))

def getArrayDiff(arr1,arr2):
    """returns an array difference in first array, second array"""
    
    diffBetFirst   =  list(set(arr1) - set(arr2))
    diffBetSecond  = list(set(arr2) - set(arr1))
    
    return diffBetFirst,diffBetSecond

def isArraysEqual(arr1,arr2):

    if len(arr1) != len(arr2):
        err = "Arrays length not equal, arr1 = '%s' arr2 = '%s'"%(arr1,arr2)
        print "ERR: %s"%err
	return False,err
    diff = [ i for i,j in  zip(arr1,arr2) if i !=j]
    
    if not diff:
        str = "Arrays equal, arr1 = '%s' arr2 = '%s'"%(arr1,arr2)
	print "INFO: %s"%str
        return True, ""
    err = "Arrays not equal, arr1 = '%s' arr2 = '%s', difference = '%s'"%(arr1,arr2,diff)

    print "ERR: %s"%err
    return False,err
    
    #raise ArrayUnEqual,err

def run_ipmi_lan_command(ip_addr,command,u_name,passwd):
    command = ipmitool + " -I lan -H %s -U %s -P %s %s"%(ip_addr,u_name,passwd,command) 
    return run_os_command(command,verbose = 1)

def run_ipmi_lan_pw_command(ip_addr,status,u_name,passwd,wait = 0):
    command = "chassis power " + status
    rc = run_ipmi_lan_command(ip_addr,command,u_name,passwd)

    if wait !=0:
        print "INFO: Waiting '%i' secs"%wait
        time.sleep(wait)

    return rc 

def utils_run_command(cmd,chkStatus = True):

    rc = os.system(cmd)

    if chkStatus:
	
	if rc != 0:
	    raise ViriError("Command '%s' Failed with rc as '%i'"%(cmd,rc))
	
    # if rc ==0 or chkStatus is False
    return rc

def if_ping_successful(ip_addr):
    rc = os.system("ping -c 1  %s"%ip_addr)
    if rc == 0:
        return True
    return False

def is_hostup(ip_addr,retry_c = 140, sleep_t = 35,wait = 10):
    """ wait is after the machine is up to wait"""
    
    for c in range(1,retry_c):
        print "-" * 40
        print "INFO: Pinging machine '%s' '%i' times"%(ip_addr,c)
        print "-" * 40
        #print " "

        if not if_ping_successful(ip_addr):
            #print " "
            print "INFO: Host still not up, retrying..."
            print "INFO: Waiting '%i' sec"%(sleep_t)
            time.sleep(sleep_t)
            continue
        else:
             print "INFO: Host seem up"
             #wait = 300
             print "Waiting %i sec"%wait 
             time.sleep(wait)
             return True

    print "-" * 40
    print "ERR: Machine not up after '%i' tries"%retry_c
    sys.exit(1)
    return False

def if_vgc_dev(device):
    #if re.match("/dev/vgc[a-z]$",device):
    print VGC_DEVICE_REGEX
    print device
    #sys.exit(1)

    
    if re.search(VGC_DEVICE_REGEX,device):
        return True
    return False

def is_vgc_dev_without_part(device):
    if not if_vgc_dev(device):
        trace_error("vgc device passed as %s please pass without partition"%device)
        sys.exit(1)
    return 1

def if_vgc_dev_part(device):
    #if re.match("/dev/vgc[a-z]\d+",device):
    if re.match(VGC_DRIVE_PART_REGEX,device) or re.match(VSHARE_REGEX,device):
        return True
    return False

def remove_dev(device):
    return re.sub("/dev/","",device)

def chkifVgcDevWithoutPart(device):
    chk_if_vdent_dev(device)
    if if_vgc_dev_part(device):
        raise ViriDeviceError,"'%s' device  passed as partition, please pass without as  e.g /dev/vgca "%device

def chkifVgcDevPart(devPart):
    if not if_vgc_dev_part(devPart):
        raise ViriDeviceError,"'%s' device not passed as partition, please pass as  e.g /dev/vgca0 "%devPart


def is_vdent_dev(device):
    if if_vgc_dev(device):
        return True
    elif if_vgc_dev_part(device):
        return True
    else:
        return False
def chk_if_vdent_dev(device):
    if is_vdent_dev(device):
        return True

    raise ViriError ("Virident device not passed,passed as '%s'"%device)
    sys.exit(1)
    
def getMask(number):
    return hex(1<<int(number))

def get_vgc_dev_from_part(device):
    """get /dev/vgca from /dev/vgca0"""
    if re.match(VGC_DRIVE_PART_REGEX,device):
        m = re.match(VGC_DRIVE_PART_REGEX,device)
        return m.group(1)

    raise ViriDeviceError("Please pass right device with partition, not as '%s'"%device)

def getVgcDeviceFromPart(devPart):
    
    if not if_vgc_dev_part(devPart):
	return 1
    
    return get_vgc_dev_from_part(devPart)


def check_if_vgc_part(device):
    
    if not if_vgc_dev_part(device):
        err = "vgc device not passed correctly,passed as '%s', no partition"%device 
        raise VirDeviceError,err
        #sys.exit(1)

    return 1

def print_dict(dict):
    
    print dict
    for k in dict.keys():
        print "%s => %s"%(k,dict[k])


# get device from partition
def get_device_part(devPart):
     """ gets /dev/vgca from /dev/vgca0"""
     check_if_vgc_part(devPart)
     m = re.search(VGC_DRIVE_PART_REGEX,devPart)
     return m.group(1)
def get_device_letter(device):
     """ get 'a' from vgca0 and vgca"""
     chk_if_vdent_dev(device)
     m = re.search(GET_DEVICE_LETTER_REGEX,device)
     return m.group(1)
def get_device_letter_part(dev_p):
     check_if_vgc_part(dev_p)
     #m = re.search("/dev/vgc([a-z])(\d+)*",dev_p)
     
     m = re.search(GET_DEVICE_LETTER_REGEX,dev_p)
     return m.group(1),m.group(2)

def get_device_letter_part1(devPart):
    """ returns a0 from vgca0"""
    arr = get_device_letter_part(devPart)

    dev = arr[0] + arr[1]
    return dev


def percentage(total,perc):
    print total
    print perc
    return (total * perc)/100
   
def isRawDevice(devPart):
    if re.search("dev",devPart):
        return True
    
    trace_info("'%s' is not raw device"%devPart)
    return False
		

def rmDevice(dev_p):
     check_if_vgc_part(dev_p)
     m = re.search(RM_DEVICE_REGEX,dev_p)
     return m.group(1)
def is_var_list(var):
    """ if variable is list/array/tuple"""
    return isinstance(var, (list, tuple))

def chkifListPassed(var):
    if not is_var_list(var):
	
        raise ViriValuePassedError("'%s' List not passed"%var)

def sleep_time(wait,str):
     trace_info("Wating '%i' secs %s"%(wait,str))
     time.sleep(wait)
     #for i in range(wait):
     #    sec_rem = wait - i
     #    print "Seconds Remaining \r %d"%sec_rem,
     #    sys.stdout.flush()
     #    time.sleep(1)
def get_card_info_prefix(card_info):
    """takes M1400I, 2048 GiB, Double decker return M1400I """
    regex = "(\S+)\s*,\s*\d+\s+GiB\s*,?.*"
    if re.search(regex,card_info):
        m = re.search(regex,card_info)
        return m.group(1)
    error = "Couldn't parse card info '%s'"%card_info
    trace_error(error)
    raise ParseError(error)

def url_accessible(url):
    try:
        u = urllib2.urlopen(url)
        u.close()
        return True
    except urllib2.HTTPError:
        return False


def get_card_type(cardInfo):
    """ return 2.2TB for 2.2 TB and 550GB for 550 """
    #if re.search("2200",cardInfo):
    # TO DO this need to be made more robust
    # NOTE using V1 card if condition first,
    # GC..will be matched first, 550 string is present in V1 and V2 both
    #V1_regex = "(GC(M|N)\d+)\s+.*"
    V1_regex = "(GC(M|N)\d+)"
    
    print cardInfo;time.sleep(4)
    # return card Info as it is
    if re.search(V1_regex,cardInfo):
	    #m = re.search(V1_regex,cardInfo)
            return cardInfo
    
    elif re.search("2200",cardInfo):
	    return "2.2TB"
    #elif re.search("550",cardInfo):
    elif re.search("550",cardInfo):
	    return "550GB"
    elif re.search("1100",cardInfo):
	    return "1.1TB"
  
    elif re.search("1650",cardInfo):
	    return "1.6TB"
    elif re.search("4[48]00",cardInfo):
	    return "4.8TB"
  
    else:
        #raise ViriError("Couldn't find the card type from card info '%s'"%cardInfo)
	return 'unknown'
	#sys.exit(1) 
    
def removeStartingZero(number):
    
    """removes 0 from 00 01, return number if doesn't with 0 """
    
    if re.search("0(\d+)",number):
        m = re.search("0(\d+)",number)
        number = m.group(1)
    return number

def getInteger(string):
    
    """removes 0 from 00 01, return number if doesn't with 0 """
    
    if re.search("(\d+)",string):
        m = re.search("(\d+)",string)
        string = m.group(1)
    return string

def get_epoch_time():
    return int(time.time())

def get_build_string(build,linuxFlavor,pathType,emc, server ):

    """returns string as http://cloudy/packages/packages.trunk.46750/redhat6/RPMS/ """

    if pathType != "releases" and pathType != "packages":
	    trace_error("%s path type is not valid"%pathType)
	    
            sys.exit(1)
            
    emc = int(emc)

    # LAtest chagnes added Virident and EMC in the path
    s1 = "VIRIDENT"
    if emc:
        s1 = "EMC"

    str = "http://%s/%s/packages.%s/%s/%s/RPMS/x86_64/"%(server,pathType,build,s1,linuxFlavor)
    return str

def get_vgc_fw_path(build,linuxFlavor,pathType = "packages",emc = 0,server = "cloudy.virident.info"):

    # http://solarium/packages/packages.trunk.43188/ubuntu1004/RPMS/x86_64/vgc-firmware-trunk.43188.tar.gz"
    str =  get_build_string(build,linuxFlavor,pathType,emc,server)
    
    str_fw = "vgc-firmware-%s.tar.gz"%reverse_build(build)
    if emc:
        str_fw = "vfstore-firmware-%s.tar.gz"%(build)
        # change - to . , hack
        if linuxFlavor == "sles11sp1":
            str_fw = "vfstore-firmware.%s.tar.gz"%reverse_build(build)
            
        
    #str = str + "/" + str_fw
    str = str  + str_fw
    
        
    strDir = "vgc-firmware-%s"%reverse_build(build)
    
    if emc:
        strDir = "vfstore-firmware-%s"%reverse_build(build)

    return (str,str_fw,strDir)

def is_rpm_ver(linuxFlavor):

    if re.search("ubuntu",linuxFlavor):
        return False
    elif re.search("redhat|sles",linuxFlavor):
        return True

    trace_error("Could'nt determine if build is rpm or not, linux Flavor '%s'"%linuxFlavor)
    sys.exit(1)

def get_build_suffix(linuxFlavor,build,pathType):
     build_str = build

     # if trunk is not found reverse it
     if not re.search("trunk",build):build_str = reverse_build(build)

     if re.search("ubuntu",linuxFlavor):
	    append_str = "_3.0-" + build_str + "_amd64.deb"
     elif  re.search("redhat|sles",linuxFlavor):
	    append_str = "-3.0-" + build_str + ".x86_64.rpm"
     else:
	    trace_error("Coundn't determine the linux flavor to append string, linuxflavour '%s'"%linuxFlavor)
	    sys.exit(1)

     return append_str

def get_vgc_driver_path(build,linuxFlavor,kernel,pathType = "packages",stats = None):
    
    #http://solarium/packages/packages.trunk.43188/redhat6/RPMS/x86_64/vgc-drivers-2.6.32-71.el6.x86_64-3.0-trunk.43188.x86_64.rpm
    # http://solarium/packages/packages.trunk.43188/ubuntu1004/RPMS/x86_64/vgc-drivers-2.6.32-27-generic_3.0-trunk.43188_amd64.deb
    # http://172.16.33.208/packages/packages.C3.43522/redhat6/RPMS/x86_64/vgc-drivers-2.6.32-131.0.15.el6.x86_64-3.0-43522.C3.x86_64.rpm
    
    
    append_str = get_build_suffix(linuxFlavor,build,pathType)	  
    http_path = get_build_string(build,linuxFlavor,pathType)
   
    # create vgc-drivers-2.6.32.12-0.7-default
    vgc_kernel = "vgc-drivers-%s"%(kernel)
    if stats:
	    vgc_kernel = "vgc-drivers-stats-%s"%(kernel)
    
    # create http://solarium/packages/packages.C3.43522/sles11sp1/RPMS/x86_64/vgc-drivers-2.6.32.12-0.7-default
    http_path = http_path + vgc_kernel

    
    http_path = http_path + append_str

    # vgc-drivers-2.6.32.12-0.7-default + "-3.0-43522.C3.x86_64.rpm"
    driver_string = vgc_kernel + append_str
    return http_path,driver_string

def get_build_ver_number(build):
    """returns C3 and 422222 from C3.42222"""
    
    if not build:
        raise ViriValuePassedError("Build string seems empty")
    
    b_s = build.split(".")
    try:
       build_ver = b_s[0]
    except IndexError:
       trace_error("Could not get build version from build string '%s'"%build)
       raise
       
    try:
       build_number = b_s[1]
    except IndexError:
       trace_error("Could not get build number from build string '%s'"%build)
       raise

    return (build_ver,build_number)

def reverse_build(build):
	(build_ver,build_number) = get_build_ver_number(build)
	str = build_number + "." + build_ver
	return str

def get_vgc_utils_path(build,linuxFlavor,pathType = "packages"):

    #str = "http://%s/%s/packages.%s/%s/RPMS/x86_64/vgc-utils"%(server,pathType,build,linuxFlavor,build)
    str1 = get_build_string(build,linuxFlavor,pathType)

    append_str = get_build_suffix(linuxFlavor,build,pathType)
    str = "vgc-utils" + append_str
    return str1 + str,str

def _is_rw_greater(val1,val2,str,tcaseDetail):
    if int(val2) > int(val1):
        trace_success("%s value after '%s' > value before '%s' for testcase '%s'"%(str,val2,val1,tcaseDetail))
        return True
    trace_error("%s value after '%s' is not  > value before '%s' for testcase '%s'"%(str,val2,val1,tcaseDetail))
    sys.exit(1)

def _is_rw_greaterOrEqual(val1,val2,str,tcaseDetail):
    if int(val2) >=  int(val1):
        trace_success("%s value after '%s' >= value before '%s' for testcase '%s'"%(str,val2,val1,tcaseDetail))
        return True
    trace_error("%s value after '%s' is not >= value before '%s' for testcase '%s'"%(str,val2,val1,tcaseDetail))
    sys.exit(1)

def remove_dev_str(dev_p):
    if not if_vgc_dev_part(dev_p):
        trace_error("Device passed as %s please pass with partition"%dev_p)
        sys.exit(1)
    if re.search("/dev/(vgc[a-z]+)\d+",dev_p):
        m = re.search("/dev/(vgc[a-z]+)\d+",dev_p)
        return m.group(1)

def compare(str,found_str,str_det,raiseOnError = 1 ):
    if str == found_str:
        str_s = "Found %s as '%s', expected '%s'"%(str_det,found_str,str)
        trace_success(str_s)
        #success_array.append(str)
        return True

    if raiseOnError == 1:
      raise ViriError("Found %s as '%s' expected '%s'"%(str_det,found_str,str))
      sys.exit(1)
      
    return False

def compare_retry(str,found_str,str_det,retries = 8,wait = 2):
    
    for c in range(0,retries):
	
	if compare(str,found_str,str_det,raiseOnError = 0):
	    return True
	
        trace_info("Found %s as '%s' expected '%s',retrying.."%(str_det,found_str,str))
	sleep_time(wait,"after retrying")
	continue
    
    raise ViriError("Found %s as '%s' expected '%s',retries '%i'"%(str_det,found_str,str,retries))
    
def chk_valid_values(array,value):
    
    for l in array:
	
	if l == value:
	    return True
    
    raise ViriError("Valid values are '%s',passed '%s'"%(array,value))
	    	
def cmp_md5sum(mdsumBef,mdsumAft,details):
    if mdsumBef != mdsumAft:
	raise ViriError("md5sum before %s doesn't match after '%s'in '%s'"%(mdsumBef,mdsumAft,details))
	sys.exit(1)
    trace_info("md5sum before %s matches after '%s'in '%s'"%(mdsumBef,mdsumAft,details))
    return 1


def mail(emailAddress,subject,file ="/dev/null"):

    cmd = " mail -s \"%s\" %s<%s"%(subject,emailAddress,file)
    #print "Sending email cmd = '%s'"%cmd
    
    run_os_command(cmd)
    return 1

def get_sles_kernel_from_rpm(rpmString):
    
    # TO DO
    #regex = "kernel-default-(\S+)\.\d+\.x86_64\.rpm"
    regex = "kernel-smp-(\S+)\.\d+\.x86_64\.rpm"
    m = re.search(regex,rpmString)
    
    try:
      string = m.group(1) + "-default"
      return string
    except:
        
       raise ViriError("Couldn't get the sles kernel from  rpm  string passed  as '%s', regex '%s'"%(rpmString,regex))

def get_sles_base_from_rpm(rpmString):
    
    regex = "kernel-default-(\S+)"
    m = re.search(regex,rpmString)
    
    try:
      string = "kernel-default-base-" + m.group(1) 
      return string
    except:
        
       raise ViriError("Couldn't get the sles base from  rpm  string passed  as '%s', regex '%s'"%(rpmString,regex))

def get_info_conf_file(file,heading,subheading):
    
    """ uses config parse to return information
    
    testTypes = get_info_conf_file("fileNme1","tests","testType")
    """
    config = ConfigParser.ConfigParser()

    config.read(file)
    
    params = config.get(heading,subheading)
    
    params = params.split()
    
    return params

def utils_split_build(build):
    """ splits 3.1 and 50744.C5 from 3.1(50744.C6) """
    #(\S+)(\(\S+\))
    try:
      m = re.search('(\S+)\((\S+)\)',build)
    except:
      raise ViriError("Unable to split build '%s'"%build)
    return m.group(1),m.group(2)

def util_config_file_to_dict(filePath):
    """ converts config file into key , value pairs
    
    """
    config = ConfigParser.ConfigParser()

    config.read(filePath)
    
    return config._sections
    

def get_info_conf_file_items(file,heading):
    
    """ uses config parse to return information
    
    testTypes = get_info_conf_file("fileNme1","tests","testType")
    """
    config = ConfigParser.ConfigParser()

    config.read(file)
    
    #config._sections['First Section']
    
    #print config._sections
    dict = config._sections[heading]
    #print dict
    
    # remove __name
    del dict['__name__']
    
    return dict

def compareAttrib(attribFound,attribExpected,attrDetails,operator,raiseOnFail = 0):
	   str = "Attribute '%s'  '%s' value Found '%s' expected '%s'"%(attrDetails,operator,attribFound,attribExpected)
	   #testcase
	   if operator == "equal":
		   if attribFound  == attribExpected:
			   trace_info(str)
			   return 1
	   elif operator == "greater":
		   if attribFound  > attribExpected:
			   trace_info(str)
			   return 1
	   elif operator == "less":
		   if attribFound  < attribExpected:
			   trace_info(str)
			   return 1
	   elif operator == "greaterthanequal":
		   if attribFound  >= attribExpected:
			   trace_info(str)
			   return 1
	   elif operator == "lessthanequal":
		   if attribFound  <= attribExpected:
			   trace_info(str)
			   return 1
	   else:
		   raise ViriValuePassedError ("Unknown operator '%s'"%operator)

           # if raise on Fail,exit otherwise just warn
           
           if raiseOnFail:
                raise ValueUnEqual(str)
           
           trace_warn(str)
           return 0
 
def  util_if_not_key_in_dict_put_default(dict,key,defaultValue):
          value = ""

          try:
             value  = dict[key]

          except KeyError:
             value = defaultValue

          return value

			   	    
def util_create_vdbench_hash(devices,blocksizes,offsets,threads,time,size = None):
    """creates vdbecnch hash/dict to be passed to vdbench function """

    if len(devices) != len(blocksizes):
        raise ViriError("Devices length dont match with blocksizes")
    if len(devices) != len(offsets):
        raise ViriError("Devices length dont match with offsets")
    
    if len(devices) != len(threads):
        raise ViriError("Devices length dont match with threads")

    devicesDict = {}
    c = 0
    for dev in devices:
        devicesDict[dev] = {}

        offset = offsets[c]
        
        if offset == "None" or offset == "0":
            offset = None

        if  offset:

           devicesDict[dev]['offset'] = offset
        
        devicesDict[dev]['threads'] = threads[c]
        devicesDict[dev]['bs'] = blocksizes[c]
	devicesDict[dev]['size'] = size
        c = c + 1

    devicesDicts = {'devices':devicesDict}
    devicesDicts ['verify'] = True
    devicesDicts ['printInterval'] = "10"
    devicesDicts ['time'] = time
    return  devicesDicts


def remove_dev_soft_partition(devPart):
    
    if re.search('(/dev/)?(vgc[a-z]+\d+).*',devPart):
	m = re.search('(/dev/)?(vgc[a-z]+\d+).*',devPart)
	
	return m.group(2)
    
def remove_soft_partition_only(devPart):
    
    if re.search('(/dev/)?(vgc[a-z]+\d+).*',devPart):
	m = re.search('((/dev/)?(vgc[a-z]+\d+)).*',devPart)
	
	return m.group(1)
    
def util_string_add_underscore_lowercase(string):
    """ convers "Read done" to "read_done", adds _ and converts to lower case"""
    
    #string = string.replace(" ","_")
    # replace space with _
    string = re.sub('[,.?!\t\n ]+', '_', string)
    return string.lower()

def time_stamp_file(fname, fmt='{fname}_%Y-%m-%d-%H-%M-%S'):
    """ takes file name and returns with time stamp, e.g, 
    file2_2013-07-09-11-16-15
    """
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

    
    
    
	
	
	
 


     

    







       

    

