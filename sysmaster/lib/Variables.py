SIM_PERR=" /usr/local/ltp/testcases/bin/sim_perr"
#VGCPROC = "/usr/lib/virident/vgcproc"
VGCPROC = "/usr/lib/vgc/vgcproc"
#latestBuild = "C6.50744"
latestBuild = "C7A.58605"
DEFAULT_PARTITION = "0"

EXPECTED_GOOD_STATE = "Good"

ipmitool = "ipmitool"

#DEV = "/dev/"
DEV = ".*"

#  a lot of variables here name after the function they 
# were declared
VGC_DEV_LETTER =  "vgc[a-z]"
VGC_DEV = DEV + VGC_DEV_LETTER
GET_DEVICE_LETTER_REGEX = DEV + "vgc([a-z])(\d+)*"

# Set device regex
DEV_RE =  "(%svgc[a-z])"%DEV
# set device regex with partition

DEV_RE_PART1 = "%svgc[a-z]\d+"%DEV

# with brackets same as PART1
DEV_RE_PART = "(%s)"%DEV_RE_PART1

VGC_REGEX = "(%s)\s+mode=(\S+)\s+sector-size=(\S+)\s+raid=(\S+)"%DEV_RE_PART1

# dollar was added
#VGC_DRIVE_PART_REGEX    = "(%s)\d+$"%VGC_DEV
VGC_DRIVE_PART_REGEX    = "(%s)\d+"%VGC_DEV
VGC_DEVICE_REGEX        = "%s$"%VGC_DEV
RM_DEVICE_REGEX         = "%s(%s\d+)"%(DEV,VGC_DEV_LETTER)

# vshare
VSHARE_REGEX    	= "%svshare\d+" % (DEV)
