
import smtplib

SERVER = "172.16.50.16"

FROM = "spica@virident.com"
TO = ["bandeepd@virident.com" , "bandeep2000@gmail.com"] # must be a list

message = "helllo1"
try:
   smtpObj = smtplib.SMTP(SERVER)
   smtpObj.sendmail(FROM, TO, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"
