#!/bin/bash
# Copyright (C) 2007-2011 Virident Systems, Inc.

# This sample script will run fio tests to verify the baseline perforamnce for Virident PCIe device.
# In order to run these test, one must have root access on the system.
# If the observed test results are significantly different than expected results, please contact Virident Support.

# Test Config: *DO NOT MODIFY*

PID=$$
device=$1
testtime=20
ramp_time=5
testspan=10G
fio=./fio
fiover=1.58
DASHLINE="---------------------------------------------------------------------------"

if [ -b "$device" ]; then
	echo ""
else
	echo "Usage: test.sh </dev/vgca0>"
	echo "Device \"$device\" not found. Please pass Virident block device (example:/dev/vgca0) as argument."
	exit 1
fi

umount $device > /tmp/umount.log 2>&1
if [ "X`mount | grep $device`X" == "XX" ]; then
	echo ""
else
	echo "Failed... $device still mounted.  Check /tmp/umount.log for detail.  Aborting..."
	mount | grep $device
	exit
fi

if [ -x $fio ]; then
	fv=`$fio --version | cut -d" " -f2`
	if [ $fv != "$fiover" ]; then
		echo "FIO $fiover is needed for this test,found $fv"
		exit
	fi
else
	echo -e -n "$fio is needed in $fio directory with read & execute permision to run the test\n"
	exit
fi

# Make REALLY sure they want to run
#clear

echo "*** VIRIDENT FlashMAX PERFORMANCE TEST ***"
echo $DASHLINE
echo -e 'WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!\n\n'
echo -e 'THIS TEST WILL DESTROY ANY DATA AND FILESYSTEMS ON THE VIRIDENT DEVICE.\n\n'
echo -e "Please type the word \"yes\" and hit return to continue, or anything else\nto abort.\n"
echo $DASHLINE
echo -n "Really run performance test?  [no/yes]  "

CONTINUE=noway
read CONTINUE

if [ "$CONTINUE" != "yes" ]; then
	echo -e "\n\nPerformance test aborted, data untouched."
	exit
fi
# Adding /usr/bin and /usr/sbin to PATH
PATH=$PATH:/usr/bin:/usr/sbin/ ;export PATH

# Make sure we are root, as this script requires access to block device
if [ "`whoami`" != "root" ]; then
	echo "Please run this script as root because it needs raw /dev access."
	exit
fi
# Make sure we have FIO
if [ ! -x $fio ]; then
	echo -e -n "$fio is needed in $fio directory with read & execute permision to run the test\n"
	exit
fi


# Make sure we have drivers loaded
vgc=$(lsmod | grep -i "vgcdrive" | head -1 | cut -d" " -f1)
if [ -z "$vgc" ]; then
	echo "ERROR: Please load the drivers as per the instructions in User Guide."
	exit
fi


# Collecting card information, may fail if drivers are not loaded or check is commented out

echo $DASHLINE
if [ -x /usr/bin/dpkg ]; then
	devv=$(dpkg -l | grep vgc | awk '{print $2 "-" $3}' )
else
	devv=$(rpm -qa | grep vgc )
fi

dev=$(basename $device | sed s/vgc//g | sed 's/[0-9]*//g')
pfile="/proc/driver/virident/vgcport$dev/info"
if [ -a $pfile ]; then
	cat /proc/driver/virident/vgcport$dev/info > /tmp/diags.out
else
	/usr/lib/vgc/vgcproc /proc/driver/virident/vgcport$dev/info > /tmp/diags.out
fi
ser=$(grep -i "Serial Number" /tmp/diags.out | tr -s ' '| cut -d"=" -f2)
rtl=$(grep -i "FlashMax Controller RTL rev" /tmp/diags.out | tr -s ' '  |cut -d"=" -f2)
ucode=$(grep -i "Module Controller RTL rev " /tmp/diags.out | tr -s ' ' |cut -d"=" -f2)
btype=$(grep -i "Flash Type" /tmp/diags.out | tr -s ' ' |cut -d"=" -f2 | cut -d" " -f2)
bsize=$(grep -i "Total Device Size" /tmp/diags.out | tr -s ' ' |cut -d"=" -f2)
bus=$(grep PCI /tmp/diags.out | grep -v data | cut -d"=" -f2 | tr -s ' ')
slot=$(lspci -s $bus -vv | grep -i "Width" |tail -1 |awk -F" " '{print $5}' | cut -d"," -f1)
echo -e "Card Details: $ser($btype,$bsize,$rtl,$ucode)"
echo -e "Card installed in $slot PCIe slot"
echo -e "Driver RPMS:\n$devv \n" 
echo $DASHLINE


# fio-tests start here

echo "Running Write Bandwidth Test (1MB blocks, queue depth 16, sequential)"
$fio --name=job --filename=$device --size=$testspan --filesize=$testspan --end_fsync=0 --numjobs=1 --bs=1M --ioengine=libaio --iodepth=16 --invalidate=1 --rw=write --group_reporting --eta never --direct=1 --norandommap --minimal > /tmp/wbw-$PID.log 
wbwr=$( cut -d";" -f26 /tmp/wbw-$PID.log | head -2 | tail -1 | tr -d "\n" | awk '{print int($1/1024)}' )
echo -e -n "Write Bandwidth measured is $wbwr MiB/s \n"
echo $DASHLINE


echo "Running Read Bandwidth Test (1MB blocks, queue depth 16, random)"
$fio --name=job --filename=$device --size=$testspan --filesize=$testspan --end_fsync=0 --numjobs=1 --bs=1M --ioengine=libaio --iodepth=32 --invalidate=1 --rw=randrw --rwmixwrite=0 --group_reporting --eta never --runtime=$testtime --ramp_time=$ramp_time --direct=1 --norandommap --minimal > /tmp/rbw-$PID.log 
rbwr=$(cut -d";" -f6 /tmp/rbw-$PID.log | head -2 | tail -1 | tr -d "\n" | awk '{print int($1/1024)}')
echo -e -n "Read Bandwidth measured is $rbwr MiB/s \n"
echo $DASHLINE


echo "Running 4KB Read IOPS Test (16 jobs, queue depth 32, random)" 
$fio --name=job --filename=$device --size=$testspan --filesize=$testspan --end_fsync=0 --numjobs=16 --iodepth=32 --bs=4096 --ioengine=libaio --invalidate=1 --rw=randrw --rwmixwrite=0 --group_reporting --eta never --runtime=$testtime --ramp_time=$ramp_time --direct=1 --norandommap --minimal > /tmp/riops-$PID.log 
rbw=$(cut -d";" -f6 /tmp/riops-$PID.log | head -2 | tail -1 | tr -d "\n" | awk '{print int($1)}')
riopsr=$((rbw/4096))
echo -e -n "4KB Read IOPS measured is $riopsr K \n"
echo $DASHLINE


echo "Running 4KB Write IOPS Test (16 jobs, queue depth 32, random) "
$fio --name=job --filename=$device --size=$testspan --filesize=$testspan --end_fsync=0 --numjobs=16 --iodepth=32 --bs=4096 --ioengine=libaio --invalidate=1 --rw=randrw --rwmixwrite=100 --group_reporting --eta never --runtime=$testtime --ramp_time=$ramp_time --direct=1 --norandommap --minimal > /tmp/wiops-$PID.log
wbw=$(cut -d";" -f26 /tmp/wiops-$PID.log | head -2 | tail -1 | tr -d "\n" | awk '{print int($1)}')
wiopsr=$((wbw/4096))
echo -e -n "4KB Write IOPS measured is $wiopsr K \n"
echo $DASHLINE


echo "Running 512B Read IOPS Test (16 jobs, queue depth 32, random)" 
$fio --name=job --filename=$device --size=$testspan --filesize=$testspan --end_fsync=0 --numjobs=16 --iodepth=32 --bs=512 --ioengine=libaio --invalidate=1 --rw=randrw --rwmixwrite=0 --group_reporting --eta never --runtime=$testtime --ramp_time=$ramp_time --direct=1 --norandommap --minimal > /tmp/riops512-$PID.log 
rbw=$(cut -d";" -f6 /tmp/riops512-$PID.log | head -2 | tail -1 | tr -d "\n" | awk '{print int($1)}')
riopsr=$((rbw/512))
echo -e -n "512B Read IOPS measured is $riopsr K \n"
echo $DASHLINE


# Collecting system information
echo "Printing System Information:"
echo "Distro:"
cat /etc/*-release
echo -e -n "\nKernel with boot-time information: "
uname -a
cat /proc/cmdline 
cpu=$(cat /proc/cpuinfo | grep "model name" | head -1 | awk -F":" '{print $2}' | tr -s ' ')
cpucores=$(cat /proc/cpuinfo | grep "model name" | wc -l)
mhz=$(cat /proc/cpuinfo | grep -i "cpu mhz" | awk -F":" '{print $2}' | tr -s ' ' | sort -n | head -1 | awk '{print int($1);}')

echo -e -n "$cpu has $cpucores cores running at $mhz \n"
echo $DASHLINE

# Deleting Files
rm -f /tmp/*-$PID*.log



