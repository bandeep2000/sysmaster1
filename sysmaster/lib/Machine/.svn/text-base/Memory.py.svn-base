class memory():
    
    
    def __init__(self,host):
        self.host = host
    
    def get_all(self): 
      """
      returns: memory details as  {'total': '24020', 'free': '17438', 'used': '6581'}
      """
      
      out = self.host.run_command_get_output("free -m")
      
      dict1 = {}
      for l in out:
        
         print l # Verbose print it
         if l.startswith('Mem'):
            
            mem_a =  l.split()
            
            dict1['total'] = int(mem_a[1])
            dict1['used'] = int(mem_a[2])
            dict1['free'] = int(mem_a[3])
      
      return dict1
    
    
    def free(self):
        
        return self.get_all()['free']
    
    def used(self):
        
        return self.get_all()['used']