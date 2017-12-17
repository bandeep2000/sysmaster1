
import os
import smtplib
#from email import *

 
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
 

HOST = "172.16.50.16"

def sendemail_msg(subject, message, TO,FROM):


    FROM = "spica@virident.com"
    TO = ["bandeepd@virident.com"] # must be a list

    SUBJECT = "Hello!"

    TEXT = "This message was sent with Python's smtplib."

    # Prepare actual message

    message = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        # Send the mail

    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, TO, message)
    server.quit()


 
def sendemail_file(subject,filePath = None,
                  TO = "bandeepd@virident.com",
                  FROM="spica@virident.com"):
 
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = TO
    #msg["Cc"] = TO
    msg["Subject"] =  subject
    msg['Date']    = formatdate(localtime=True)
    textfile = "hello1"

    #fp = open(textfile, 'rb')
    # Create a text/plain message
    #msg = MIMEText(fp.read())
    #fp.close()
 
    # attach a file

    if filePath:

        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(filePath,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filePath))
        msg.attach(part)
 
    server = smtplib.SMTP(HOST)
    # server.login(username, password)  # optional
 
    try:
        #failed = server.sendmail(FROM, TO, "hello",msg.as_string())
        failed = server.sendmail(FROM, TO, msg)
        server.close()
    except Exception, e:
        errorMsg = "Unable to send email. Error: %s" % str(e)
 
if __name__ == "__main__":
    sendemail_file("test","hello1")
