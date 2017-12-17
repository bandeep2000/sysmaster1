#!/usr/bin/python
# import MySQL module
import MySQLdb
import sys,re
from Trace import *
# connect

HOSTDB = "sysmaster"
DBUSER    = "root"
DBPASSWD = "0011231"
DB = "viri"

"""

Usage example:

#!/usr/bin/python
# import MySQL module
# connect

import DB

db = DB.viriDB()
m = sys.argv[1]
print db.getIPMI(m)
print db.getRpb(m)


"""
class ViriDBError(Exception):
    pass


class viriDB:
    def __init__(self,host = HOSTDB,
                 user      = DBUSER ,
                 passwd    = DBPASSWD,
                 db        = DB):

        self.host   = host
        self.user   = user
        self.passwd = passwd
        self.dbName     = db
        self.cur    = " "

        self.connect()

    def connect(self):
          trace_info("Connecting to database")
          self.dbObject = MySQLdb.connect(self.host, self.user,self.passwd,self.dbName) 
          self.cur = self.dbObject.cursor()
    def commit(self):
          self.dbObject.commit()
    def close(self):
          self.dbObject.close()
    def closeCursor(self):
          self.cursor.close()
    def runSelect(self,query):
          trace_info( "Running query")
          self.cur.execute(query)
          rows = self.cur.fetchall()
          return rows
    def runSelect1(self,query):
        """ better that run Select,returns array instead of tuples """
        rows = self.runSelect(query)
        array = []
        for row in rows:
           array.append(row[0])
        return array

    def runUpdate(self,query):
          trace_info( "Running query '%s'"%query)
          self.cur.execute(query)
          return 1
    def updateCPUs(self,tb_name,cpus,cpuType):
        
        self.cur.execute("update tb set cpuType=%s where tb_name=%s",(cpuType,tb_name))
        return 1
    
    def updateCardSerial(self,tb_name,serial):
        #  update cards set tb_name="dummy" where serial="gg";
        #query = "update cards set tb_name=%s where serial=%s",(tb_name,serial)
        self.cur.execute("update cards set tb_name=%s where serial=%s",(tb_name,serial))
        return 1
    def updateMachineOSType(self,tb_name,osType):
        #  update cards set tb_name="dummy" where serial="gg";
        #query = "update cards set tb_name=%s where serial=%s",(tb_name,serial)
        self.cur.execute("update tb set osType=%s where tb_name=%s",(osType,tb_name))
        return 1
    
    def insertCardTestbedDetails(self,cardSerial,cardType,machine):
         #insert into cards values("test","hello","sqa11");
         print "INFO: Inserting into db %s %s %s"%(cardSerial,cardType,machine)
         #sys.exit(1)
         self.cur.execute("insert into cards values(%s,%s,%s)",(cardSerial,cardType,machine))
         return 1
    
    def insertTestCaseResults(self,build,machineName,kernal,osVersion, totalCpus,cpyType,testCaseid,testCaseDescription,testCaseReasonPassed,testCaseReturnCode,testCaseTimeTaken,result,logFilePath,cardInitialState,testcaseStr,hostKernel,cardType,cardSerial):
         #insert into cards values("test","hello","sqa11");
         try:
           self.cur.execute("insert into testResults values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(build,machineName,kernal,osVersion, totalCpus,cpyType,testCaseid,testCaseDescription,testCaseReasonPassed,testCaseReturnCode,testCaseTimeTaken,result,logFilePath,cardInitialState,testcaseStr,hostKernel,cardType,cardSerial))
         
         except:
              cmd = "insert into testResults values %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s"%(build,machineName,kernal,osVersion, totalCpus,cpyType,testCaseid,testCaseDescription,testCaseReasonPassed,testCaseReturnCode,testCaseTimeTaken,result,logFilePath,cardInitialState,testcaseStr,hostKernel,cardType,cardSerial)
              
              print "cmd Error '%s'"%cmd
              raise
         return 1

         
    def get2Columns(self,column1,column2,tb):
          query = "select %s,%s from tb where tb_name='%s'"%(column1,column2,tb)
          rows = self.runSelect(query)
          tuple =  rows[0]
          rpb = tuple[0]
          rpbPort = tuple[1]
          # return port as string since L gets printed
          return rpb,str(rpbPort)

    def ifDefined(self,column,columnVal):
        if not columnVal:
            err = "ERROR: column '%s' not defined value '%s'"%(column,columnVal)
            raise ViriDBError,err
            sys.exit(1)
    def getAllCardSerials(self):
	    #""" takes tb as example sqa05, returns as tuple ('ipmi-sqa05', 'ADMIN', 'ADMIN')""" 
        #  select serial from cards;
        rows = self.runSelect("""select serial from cards""")
        array = []
        for row in rows:
           array.append(row[0])
        return array
    def isCardSerialPresent(self,serial):
	    #""" takes tb as example sqa05, returns as tuple ('ipmi-sqa05', 'ADMIN', 'ADMIN')""" 
        #  select serial from cards;
        serArray = self.getAllCardSerials()
        
        for ser in serArray:
            if ser == serial:
                return True
        return False

    def _if_valid_ipmi(self,ipmi):
        
        ipmi = ipmi.strip()

	if re.search("\s+|unknown",ipmi,re.I):
	    trace_info("Found space/unknown in ipmi '%s',rejecting it.."%ipmi)
	    return False
	return True
        #pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    def getIPMI(self,machine):
	""" takes tb as example sqa05, returns as tuple ('ipmi-sqa05', 'ADMIN', 'ADMIN')""" 

	cmd="""select ipmi,ipmiUser,ipmiPasswd from machine
	 hostname='%s'"""%machine
	trace_info("Gettting ipmi information for machine '%s'"%machine)

        rows = self.runSelect("""select ipmi,ipmiUser,ipmiPassword from machines where hostname='%s'"""%machine)

	try:
          tuple = rows[0]
	except IndexError:
	  trace_error("""seems like ipmi information is not present for machine '%s'"""%machine);
	  return None,None,None

        # print tuple;
        ipmiAddr= tuple[0]
        ipmiUserId = tuple[1]
        ipmiPasswd = tuple[2]

        # check if ipmi address is defined, if not return, no need to check if
	# user id /passwd is present
        try: 
          self.ifDefined("ipmiAddr",ipmiAddr)
        
        except ViriDBError:
	  return None,None,None
          #raise ViriDBError("Couldn't find the ipmi information for tb '%s' in db, please add it"%tb)

        self.ifDefined("ipmiUserid",ipmiUserId)
        self.ifDefined("ipmiPasswd",ipmiPasswd)

	if not self._if_valid_ipmi(ipmiAddr):
		return None,None,None

        return ipmiAddr,ipmiUserId,ipmiPasswd

    def getRpb(self,machine):
	    #""" takes tb as example sqa05, returns as tuple ('pwr28', '7') 
		#"""
		
        rows = self.runSelect("""select rpb,rpbPort 
                 from machines where hostname='%s'"""%machine);
        
	try:
          tuple = rows[0]
	except IndexError:
	  trace_error("Seem like either hostname or ipmi information in not present for '%s'"%machine)
	  raise
        print "tuple = ",tuple

        rpb = tuple[0]
        # some issue with python integer  with db
        # some issue with python integer  with db
		# print L with integer and convert to string
        rpbPort = str(tuple[1])
        try:
          self.ifDefined("rpb",rpb)
        except ViriDBError:
          raise ViriDBError("Couldn't find the rpb information for tb '%s' in db, please add it"%machine)
        self.ifDefined("rpbPort",rpbPort)

        return rpb,rpbPort
    
    def getHostCardSerial(self,tb):
        # select * from cards where tb_name="sqa05";
        # select serial,cardDescription from cards where tb_name="sqa05";
        
        rows = self.runSelect("""select serial
                 from cards where tb_name='%s'"""%tb);
        
        serials = []
        
        for r in rows:
            #print r
            serials.append(r[0])
        print serials
        return serials
        #sys.exit(1)

        
    def getAllTestbeds(self):
	""" return all testbeds found in database"""
		
        rows = self.runSelect("""select hostname from machines where OS like
	'%Centos%'""");
        
        #tuple = rows[0]
        tbs = []
        for tb in rows:
            tbs.append(tb[0])
        
        return tbs


