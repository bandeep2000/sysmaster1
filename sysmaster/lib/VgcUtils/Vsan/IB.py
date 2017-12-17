import Parsers
from Util import *
from Trace import *
class infiniBand:
  def __init__(self ,host):
     self.host = host
  
  def run_command(self,command):
    o = self.host.run_command_chk_rc(command)
    out = o['output']
    return out[1:]
  
  def get_port_guids(self, ):
    
    return self.run_command("ibstat -p")
  
  def get_hca_port_guids(self,hca):
    """ retrns port guids gievne hca """
    return self.run_command("ibstat %s -p"%hca)
  
  def get_sw_host_connections(self,hca,port):
    
    """
    
    [root@vsanqa28 ~]# {'0x0002c90300ea4741': {'swPort': '2', 'hostPort': 1, 'hca': 'mlx4_1', 'swGuid': '0x0002c9020047b608'},
       '0x0002c90300225671': {'swPort': '3', 'hostPort': 1, 'hca': 'mlx4_0', 'swGuid': '0x0002c9020047b618'}}

    """
    
    dict = {}
    
    dict2 = self.get_all_hca_port_guids()
    
    for l in self.run_command("ibnetdiscover -C %s -P %s -p | grep ^CA| grep %s"%(hca,port,self.host.name)):
       a = l.split()
       #hostPort = a[2]
       hostGuid =  a[3]
       swPort = a[9]
       swGuid = a[10]
       
       hca,hostPort = self.get_port_from_guid(hostGuid)
       dict[hostGuid] = {'swPort': swPort,'swGuid': swGuid,'hca':hca,'hostPort':hostPort}
    
    return dict
    print dict

      
  def get_port_from_guid(self,guid):
    """ tuple mlx4_0,1
    takes guid  as input,
    returns None if not found
    
    """
    dict2 = self.get_all_hca_port_guids();
    # {'mlx4_0': ['0x002590ffff48141d']}

    #print dict2.keys();sys.exit(1)
    
    for hca in dict2.keys():
      guids = dict2[hca]
      
      c = 1
      for expguid in guids:
        if guid == expguid:
          return hca,c
      c = c+1
    # return None, if guid not found
    print "ERR: Not able to find guid '%s' from '%s'"%(guid,dict2);sys.exit(1)
    return None    
    
    
  def get_hcas(self, ):
    """ returns arrays as [mlx4_0, mlx4_1]"""
    return self.run_command("ibstat -l")
  
  def get_switches(self,hca,port):
    
    cmd = "ibswitches -C %s -P %s"%(hca,port)
    
    output = self.run_command(cmd)
    
    if len(output) == 0:
      trace_info("No switches found")
      return None
    
    # split based on ":" first , then on space
    return output[0].split(":")[1].split()[0]
    
    a = output.split(":")
    
  def get_hca_port_guids1(self,hca1):
  
  
       dict = {}
       hca = ""
       # ibstat  | egrep "mlx4|Port GUID"
       for l in self.run_command('ibstat  | egrep "mlx4|Port GUID"'):
       
          if re.search("CA",l):
                a = l.split()
                hca = a[1]
                
                hca = hca.replace("'","")# replace '
                dict[hca] = []
          if re.search("Port GUID",l):
                guid = Parsers.getSingleSplitRight(l)
                dict[hca].append(guid)
       
       return dict[hca1]

  def get_all_hca_port_guids(self):
    
    dict = {}
    for hca in  self.get_hcas():
      #print self.c
      dict[hca] =  self.get_hca_port_guids1(hca)
      
    return dict
  
  def get_hca_port_state(self):
    """
    returns e.g
    Dual port card
    {'mlx4_0': {1: 'Active', 2: 'Initializing'}}
    
    Two card, not dual port
    {'mlx4_0': {1: 'Active'}, 'mlx4_1': {1: 'Active'}}
    """
    
    dict = {}
    
    hcas_portGuids = self.get_all_hca_port_guids()
    for hca in hcas_portGuids:
      
      portGuids = hcas_portGuids[hca]
      
      dict1 = {}
      for port in range(1,len(portGuids)+1):
          print "%s %s"%(hca,port)
          
          dict1[port] = self.get_port_state(hca,port)
          
      dict[hca] = dict1
    
    return dict
  
  def is_port_up(self,hca,port):
    
    for c in range(1,4):
      state = self.get_port_state(hca,port)
      if  state  == 'Active':
        return True
      trace_info("Port not up fount status '%s',retrying.."%state)
      sleep_time(3,"after port not up")
      continue
    else:
      trace_info("Port state not active, even after 3 tries")
      return False
      
        
          
  def get_port_state(self,hca,port):
    return self.get_ibstat_port_details(hca,port,attrib = 'state')
  
  def get_ibstat_port_details(self,hca,port,attrib = None):
    
    cmd = "ibstat %s %s"%(hca,port)
    
    parsedOutput = Parsers.parseSplit( self.run_command(cmd),add_underscore = 1)
    
    # if attribute return that other wise everything
    if attrib:
      return parsedOutput[attrib]
    return parsedOutput
      
      
    
    
  