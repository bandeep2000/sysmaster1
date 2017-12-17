import ConfigParser,sys
from Util import *
class configFile():

      def __init__(self,filePath):
         
         self.file = filePath
         
         config = ConfigParser.ConfigParser()
         
         config.read(self.file)
         
         self.config = config


      def isNone(self,option):
         
         """ utility function , coverts None string to None for python"""
         if option == "None":
             return None
         return option

      def parse(self):
         
         """ returns key value pairs as dict from config file passed
         """
        
         return self.config._sections
      
      def parse_header_regex(self,regex ):
         """ returns dictionary,based on header regex"""
         dict1 = self.parse()


         for k1 in dict1.keys():
            
            if k1.startswith(regex):
               
                 dict2 = dict1[k1]

		 for k in dict2.keys():
			 v = dict2[k]
			 v = self.isNone(v)
			 dict2[k] = v
		 del dict2['__name__']

		 return dict2
         return None
         
      def get_config(self, header = "config"):
         dict1 = self.parse()

	 if dict1.has_key(header):

		 dict2 = dict1[header]

		 for k in dict2.keys():
			 v = dict2[k]
			 v = self.isNone(v)
			 dict2[k] = v
		 del dict2['__name__']

		 return dict2
         return None
 
      def create_vdbench_dict(self,dict3):
         """ creates vdbench dict, ignores vdbench multiple"""
         for name in dict3:
            
            if not name.startswith("vdbench") or name.startswith("vdbenchMultiple"):
               continue
               
            dict1 = dict3[name]
            print dict1
            
            
            blkSizes = dict1['bs']
            offsets  = dict1["offset"]
            threads  = dict1["threads"]
            devices = []
            dict2 = util_create_vdbench_hash(devices,blkSizes,offsets,threads,time)
            
            print dict2
         sys.exit(1)
      
      
      def create_fio_dicts(self,dict3 ):
         
         #dict1 = { 'rw': ['randread', 'randwrite'], 'fsync': ['None'], 'bs':['4K', '8K'],}
         """
         returns dict as dict1 = { 'rw': ['randread', 'randwrite'], 'fsync': ['None'], 'bs':['4K', '8K'],}
         ignores fioMultiple
         """
         
         dict_arr = []
         #dict1 =  {'rw': ['randrw','randrw'], 'fsync': ['8'], 'verify': [None], 'offset': [None], 'fill_drive': [None], 'numjobs': ['32','16'],'time': ['10'], 'bs': ['512-256K'], 'ioengine': ['sync'], 'rw_perc': ['50'], 'iodepth': [None], 'size': [None]}
         
         for name in sorted(dict3.keys()):
            
            dict1 = dict3[name]
            
	    if not  name.startswith('fio'):
		    continue
	    # ignore if name startw sith fio Multiple
            if name.startswith('fioMultiple'):
		    continue

            #print dict1
            rws = set(dict1['rw'])
	    #rws  = dict1.get('rws',[None])
            fsyncs = dict1['fsync']
            verifys = dict1['verify']
            num_jobs = dict1['numjobs']
            time = dict1['time']
            bses = dict1['bs']
            ioengines = dict1['ioengine']
            sizes = dict1['size']
            iodepths = dict1['iodepth']
            fsyncs = dict1['fsync']
            bas  = dict1.get('offset',[None])
            
            
            for rw in rws:
               
               for fsync in fsyncs:
                  
                  for verify in verifys:
                      
                      for num_job in num_jobs:
                        
                        for bs in bses:
                           
                           for ioengine in ioengines:
                             for fsync in fsyncs:
                              
                              for size in sizes:
                                 
                               for ba in bas:
                                 
                                 for iodepth in iodepths:
                                    
                                    for num_job in num_jobs:
                                      print size #sys.exit(1)
                        
                                      dict1 = {'rw':rw, 'numjobs':num_job,'verify':verify,'time': time[0],'bs':bs,
				          'ioengine':ioengine,'size':size,'iodepth':iodepth,'name':name,'ba':ba,'fsync':fsync,'numjobs':num_job}
                                     
                                      dict_arr.append(dict1)
                                  
         
         return dict_arr
      
      def parse_array(self):
         
         """
         
         description:
         converts into array and returns dict
         
         [fioValidation-V30_1_2]:
         
         rw: randread randwrite
         fsync: None
         
         converts into , note rw: is changed to array
         {'fioValidation-V30_1_2': {'rw': ['randread', 'randwrite'], 'fsync': ['None']
         
         returns:   dict as example
         
         {'testtype': ['fio7-4K-write', 'fio8-4K-read', 'vdbench1', 'fio1', 'fio2', 'fio3', 'fio4', ..
             'fioValidation-V30_2', 'fioValidation-V30_3', 'fioValidation-V30_4']},
             'fio7-4K-write': {'rw': ['randwrite'],
             'fsync': ['None'], 'verify': ['None'], 'offset': ['None'],
             'fill_drive': ['None'], 'numjobs': ['1'],
             'time': ['14400'], 'bs': ['4K'], 'ioengine': ['libaio'], 'rw_perc': ['None'], 'iodepth': ['256'],
             'size': ['None']},
             'vdbenchMultiple1Soft': {'time': ['30'], 'partitions': ['4'], 'modes': ['None'], 'parttype': ['soft']},
             'fio8-4K-read': {'rw': ['randread'], 'fsync': ['None'], 'verify': ['None'], 'offset': ['None'], 

         
         """
        
         dict1 = self.config._sections
         
         dict2 = {}
         for k in dict1.keys():
            
               #if k.startswith("fio"):
               
               dictValue2 = {}
               dictValue = dict1[k]
               
               # loop through other dictionary
               for k2 in dictValue.keys():
                  # ignore __name 
                  if k2 == '__name__':
                     continue
                  
                  v2 = dictValue[k2]
                  
                  # split based on spaces
                  arr = v2.split()
                  #print arr
                  
                  # convert "None" string to None in array
                  arr = [self.isNone(l) for l in arr]
                     
                  dictValue2[k2] = arr
                  
               dict2[k] = dictValue2 
         
         #print dict2
         return dict2
    
