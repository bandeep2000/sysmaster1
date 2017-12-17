import sys
import os
from Util import *
class GnuplotError(Exception):
  pass

def plot_and_get_http_path(configFile,graphFile):
  
   # start the plot and convert to pdf
   os.system("gnuplot %s"%configFile)
   os.system("ps2pdf %s"%graphFile)

   graphFile = graphFile + ".pdf"
   httpPath = "/var/www/html/sqa/%s"%graphFile
   rmFileIfExists(httpPath)
   os.system("mv %s %s "%(graphFile,httpPath))

   print "-"
   print "-" * 80
   print "http://sysmaster/sqa/%s"%graphFile
   
   return "http://sysmaster/sqa/%s"%graphFile

def plot1(dict1):

   """
   inputs : dictionary as example below
   
   Usage example:
from Gnuplot import *

dict1 = {'data_array' : [ 10, 40, 80],
         'title': "hello",
         'outputfile' : 'plot-del',
         'xlabel'  : 'IOPS',
         'ylabel'  : '10 sec',
}
plot1(dict1)

   returns:
   
   http path of the pdf file on the sysmaster server
   outputfile will be of this format outputfile + time_stamp + pdf
   
   Example: http://sysmaster/sqa/plot-del_2014-03-18-13-42-21.pdf
   
   """
   
  
   
   array     = dict1['data_array']
   title     = dict1['title']
   graphFile = dict1['outputfile']
   xlabel    = dict1['xlabel']
   ylabel    = dict1['ylabel']


   # temp file to store data, just giving del.txt
   datafile = "del.txt"
   # gnuplot config file
   configFile = "conf-%s"%datafile
   # output graph file name will be converted .pdf format
   graphFile = time_stamp_file(graphFile)

   # Clean up before running
   for file in [configFile,datafile,graphFile]:
       os.system("rm -rf %s"%file)
 
 
   # create datafile from the array given,used by gnuplot
   f = open(datafile,'w')

   c = 0
   for l in array:
      # x axis is just a counter 1,2,3
      c = c + 1
      # this will create datafile as 
      # 1 8
      # 2 6 etc...
      f.write("%i %s\n"%(c,l))
   f.close()

  # create gnuplot config file
   str = "set terminal postscript color\n"
   str = str +  "set output '%s'\n"%graphFile
   str = str +  "set xlabel '%s'\n"%xlabel
   str = str +  "set ylabel '%s'\n"%ylabel
   str = str + "plot "

   str1 = ""
   str1 = str1 + "'%s' using 1:2  title '%s' with linespoints,"%(datafile,title)
   str = str + str1
   str = str[:-1]

   fg = open(configFile,'w')
   print >> fg,str
   fg.close()
   
   httpPath = plot_and_get_http_path(configFile,graphFile)
   
  
  # Clean up after running 
   # ok to delete graph output file since it is coverted .pdf
   for file in [configFile,datafile,graphFile]:
       os.system("rm -rf %s"%file)
       
   return httpPath
 
def plot(dict,graphFileDetails,hostName,devPart):
   """ plot takes dict = {'file1': 'title1': 'file2':'title2'
   file1 example
   1 2.05
   2 82924.40
   3 84370.10

   graphFileDetails :
   is any details of the graph pdf file created
   it will be created plot-sqa11-vgca0 + grpahFileDetails + time stamp
   """

   # File to plot,delete first
   os.system("rm -rf del-gnuplot*")
   # config file that gnuplot uses to plot
   # gnuplot <config file>
   configFile = "del-gnuplotConf"

   # create string e.g
   # 'del4' using 1:2  title 'title' with linespoints'del4' using 1:2  title
   # 'title' with linespoints
   graphFile = "plot-%s-%s--"%(hostName,devPart)
   str1 = ""
   for datafile in dict.keys():
      #print str1
      title = dict[datafile]
      #graphFile = graphFile + title + "-"
 
      # chk if file is empty
      if os.stat(datafile)[6] == 0:
	 raise GnuplotError ("datafile %s seem empty to plot ")
      
      str1 = str1 + "'%s' using 1:2  title '%s' with linespoints,"%(datafile,title)

   graphFile  = graphFile[:-1]
   # append time stamp to the file
   
   if graphFileDetails:
     graphFile = graphFile + graphFileDetails
     
   graphFile = time_stamp_file(graphFile)

   # create config file
   # prepened string to be used in gnuplot config file
   # Note \n being used
   str = "set terminal postscript color\n"
   str = str +  "set output '%s'\n"%graphFile
   str = str +  "set xlabel '10 sec interval'\n"
   str = str +  "set ylabel 'IOPS'\n"
   str = str + "plot "

   # append str1 to str,this will create
   # plot str1
   str = str + str1

   # remove last ,
   str = str[:-1]
   
   #print str;sys.exit(1)
 
   # create config file using str
   fg = open(configFile,'w')
   print >> fg,str
   fg.close()
   os.system("gnuplot %s"%configFile)

   # this will create .pdf file
   os.system("ps2pdf %s"%graphFile)

   # delete graph file, otherwise it clutters the local directory
   os.system("rm -rf %s"%graphFile)
   
   graphFile = graphFile + ".pdf"
   httpPath = "/var/www/html/sqa/%s"%graphFile
   rmFileIfExists(httpPath)
   os.system("mv %s %s "%(graphFile,httpPath))

   print "-"
   print "-" * 80
   print "http://sysmaster/sqa/%s"%graphFile
   return "http://sysmaster/sqa/%s"%graphFile
   
def plot_host_iostat(h,devPart,iostat_file_path_host_array,verbose = 1,graphFileDetails = ""):
   """
   takes host object, device as vgca0,file absolute path eg. as inputs
   
   
   """
   c = 1
   dict = {}
   for iostat_file_path_host in iostat_file_path_host_array:
	devPart = devPart.replace("/dev/","")
	
	#for ioType in ['rw']:
	ioTypes = ['rw']
	if len(iostat_file_path_host_array) == 1:
	  ioTypes = ['reads','writes','rw']
	
	
	for ioType in ioTypes:
	 
	   # get read iostat file from host as given , then create a new one locally
	   out_w =  h.get_iostat_output(iostat_file_path_host,devPart,ioType)
	   #print out_w;sys.exit(1)
	   c = c + 1
	   datafile = "del-%s-%s-%s-%i"%(h.name,devPart,ioType,c)
	   
	   
	     
	   
	   # create dict, keep title and datafile same
	   #graph_title = datafile
	   # get relative path
	   arr = iostat_file_path_host.split("/")
	   graph_title = arr[-1] # will give  file1 from /ioDir/file1
	   
	   graph_title = "%s-%s-%s"%(ioType,devPart,graph_title)
	   
	   
	   
	   dict[datafile] = graph_title
	   rmFileIfExists(datafile)
	   f = open(datafile,'w')
     
	   i = 1
	   for l in out_w:
	     
	     # print to stdout, if verbose
	     if verbose:
	       print "%i %s"%(i,l)
	     print >> f,i,l
	     # i is horizontal axis"
	     i = i + 1
     
	   f.close()
	
	# this will have keys as files and values also same
	# plot takes dict = {'file1': 'title1': 'file2':'title2'}
   return plot(dict,graphFileDetails,h.name,devPart)
	
	#return 1




