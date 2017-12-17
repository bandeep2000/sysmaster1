
#specs = {'VIR-M2-LP-550-2A': {'ucap':{'raid':{'enabled':{'mode':{'maxperformace':'220'}}}}}}
# usable capacity , key is raid+mode
# this dictionary is old and depcreated , use the one below!!
# DO NOT USE THIS DICT!! DEPRECATED

"""
[root@mdemo1 ~]# vgc-config -d /dev/vgce -n 2 -m maxcapacity
vgc-config: 3.1(50140.C6)

*** WARNING: this operation will erase ALL data on this drive, type <yes> to continue: yes

*** Formatting drive.  Please wait... ***
[root@mdemo1 ~]# vgc-monitor -d /dev/vgce
vgc-monitor: 3.1(50140.C6)

Driver Uptime: 2 days 19:35
Card_Name      Raw_Capacity   Num_Partitions      Status
/dev/vgce      2048 GiB       2                   Good

  Serial Number      : VS001D2-000049
  Card Info          : GCM1400 (Double decker), 2048 GiB
                       Rev : FlashMax 33248, module 32977, x8 Gen1
  Temperature        : 48 C (Safe)
  Card State Details : Normal
  Action Required    : None


  Partition           Raw_Capacity        Usable_Capacity     RAID
  /dev/vgce0          1024 GiB            702 GB              enabled

    Mode                          : maxcapacity
    Total Flash Bytes             : 10423711618048 (10.42TB) (reads)
                                    11731924537803 (11.73TB) (writes)
    Remaining Life                : 92.21%
    Partition State               : READY
    Flash Reserves Left           : 98.30%

  Partition           Raw_Capacity        Usable_Capacity     RAID
  /dev/vgce1          1024 GiB            702 GB              enabled

    Mode                          : maxcapacity
    Total Flash Bytes             : 10907921119232 (10.91TB) (reads)
                                    11731894140928 (11.73TB) (writes)
    Remaining Life                : 92.20%
    Partition State               : READY
    Flash Reserves Left           : 99.60%
[root@mdemo1 ~]# vgc-config -d /dev/vgce -n 2 -m maxperformance
vgc-config: 3.1(50140.C6)

*** WARNING: this operation will erase ALL data on this drive, type <yes> to continue: yes

*** Formatting drive.  Please wait... ***
[root@mdemo1 ~]# vgc-monitor -d /dev/vgce
vgc-monitor: 3.1(50140.C6)

Driver Uptime: 2 days 19:47
Card_Name      Raw_Capacity   Num_Partitions      Status
/dev/vgce      2048 GiB       2                   Good

  Serial Number      : VS001D2-000049
  Card Info          : GCM1400 (Double decker), 2048 GiB
                       Rev : FlashMax 33248, module 32977, x8 Gen1
  Temperature        : 49 C (Safe)
  Card State Details : Normal
  Action Required    : None


  Partition           Raw_Capacity        Usable_Capacity     RAID
  /dev/vgce0          1024 GiB            615 GB              enabled

    Mode                          : maxperformance
    Total Flash Bytes             : 10423717614592 (10.42TB) (reads)
                                    11731982143947 (11.73TB) (writes)
    Remaining Life                : 92.20%
    Partition State               : READY
    Flash Reserves Left           : 98.76%

  Partition           Raw_Capacity        Usable_Capacity     RAID
  /dev/vgce1          1024 GiB            615 GB              enabled

    Mode                          : maxperformance
    Total Flash Bytes             : 10907927115776 (10.91TB) (reads)
                                    11731951616000 (11.73TB) (writes)
    Remaining Life                : 92.18%
    Partition State               : READY
    Flash Reserves Left           : 99.70%
[root@mdemo1 ~]#                


"""

specs = {
              'VIR-M2-LP-550-1A': {
                                   'ucap': {'enabledmaxperformance' :'461',
                                            'enabledmaxcapacity'    :'555',
                                            'disabledmaxcapacity'   :'634',
                                            'disabledmaxperformance':'527',},
                                   'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             }
                                  },
              'EMC-M2-LP-2200-A' : {
                                    'ucap':
                                     {'enabledmaxperformance' :'1847',
                                      'enabledmaxcapacity'    :'2222',
                                      'disabledmaxcapacity'   :'2539',
                                      'disabledmaxperformance':'2111'},
                                    'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             }
                                  },
       }

#specs = {'VIR-M2-LP-550-2A': {'ucap':{'raid':{'enabled':{'mode':{'maxperformace':'220'}}}}}}
# usable capacity , key is raid+mode
specsCard = {
              '550GB': {
                                   'ucap': {'enabledmaxperformance' :'461',
                                            'enabledmaxcapacity'    :'555',
                                            'disabledmaxcapacity'   :'634',
                                            'disabledmaxperformance':'527',},
					   
					 
                                   'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },
               '1.1TB': {
                                   'ucap': {'enabledmaxperformance' :'923',
                                            'enabledmaxcapacity'    :'1111',},
					   
					 
                                   'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },
              '1.6TB': {
                                   'ucap': {'enabledmaxperformance' :'1385',
                                            'enabledmaxcapacity'    :'1666',},
					   
					 
                                   'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },
              '2.2TB' : {
                                    'ucap':
                                     {'enabledmaxperformance' :'1847',
                                      'enabledmaxcapacity'    :'2222',
                                      'disabledmaxcapacity'   :'2539',
                                      'disabledmaxperformance':'2111',
				      'enabledmaxperformance2':'923',  # where 2 stands for card with partition 2 
				      'enabledmaxcapacity2'  :'1111',},
                                    'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1', # V3 NEED TO change back to
				   
                                 },
              
              '4.8TB' : {
                                    'ucap':
                                     {'enabledmaxperformance' :'4098',
                                      'enabledmaxcapacity'    :'4848',
                                      'disabledmaxcapacity'   :'2539',
                                      'disabledmaxperformance':'2111',
				      'enabledmaxperformance2':'2049',  # where 2 stands for card with partition 2 
				      'enabledmaxcapacity2'  :'2424',},
                                    'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'2',
                                 },
              
              'GCM1400' : {
                                    'ucap':
                                     {'enabledmaxperformance' :'1231',
                                      'enabledmaxcapacity'    :'1404',
                                      'enabledmaxperformance2':'615',  # where 2 stands for card with partition 2 
				      'enabledmaxcapacity2'  :'702',},
                                    'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'2',
                                  },
              'GCN800' : {
                                    'ucap':
                                     {'disabledmaxperformance' :'802',
                                      'disabledmaxcapacity'    :'890',
                                      'disabledmaxperformance2':'401',  # where 2 stands for card with partition 2 
				      'disabledmaxcapacity2'  :'445',},
                                    'default':{'raid':'disabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'2',
                                  },                                  
              'GCN600' : {
                                    'ucap':
                                     {'disabledmaxperformance' :'601',
                                      'disabledmaxcapacity'    :'667',},
                                    'default':{'raid':'disabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },                      
               'GCM1000': {
                                   'ucap': {'enabledmaxperformance' :'923',
                                            'enabledmaxcapacity'    :'1053',},
					   
					 
                                   'default':{'raid':'enabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },
              'GCN300' : {
                                    'ucap':
                                     {'disabledmaxperformance' :'300',
                                      'disabledmaxcapacity'    :'333',},
                                    'default':{'raid':'disabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },                 
              'GCN400' : {
                                    'ucap':
                                     {'disabledmaxperformance' :'401',
                                      'disabledmaxcapacity'    :'445',},
                                    'default':{'raid':'disabled',
                                              'mode':'maxcapacity',
                                              'sector':'512'
                                             },
                                   'partitions':'1',
                                  },                  
}

