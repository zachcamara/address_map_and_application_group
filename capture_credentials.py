#
import base64
import getpass
import colored
from colored import stylize
from os import system, name
#
# Console text highlight color parameters
#
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")
#
# Clear Screen
#
def clear(): 
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear') 
clear()
#
# Create files for encoded storage of credentials and IP
# 
fileUser = open(".orch_user.out",'wb') 
filePasswd = open(".orch_passwd.out",'wb') 
fileIP = open(".orch_ip.out", 'wb')
#
# Gather user input for Orchestrator username, password, and IP
#
print ()
print(stylize("--- GATHERING CREDENTIALS ---",red_text))
print()
orchuser = input ("Enter Orchestrator Username: ")
print()
orchpasswd = getpass.getpass("Enter Orchestrator Password: ")
print()
orchip = input ("Enter Active Orchestrator IP: ")
print()
#
# Encode values for storage
#
encode_user = base64.b64encode(orchuser.encode("utf-8"))
encode_passwd = base64.b64encode(orchpasswd.encode("utf-8"))
encode_ip = base64.b64encode(orchip.encode("utf-8"))
#
# Write encoded values to file
#
fileUser.write(encode_user)
filePasswd.write(encode_passwd)
fileIP.write(encode_ip)
#
# Close files
#
fileUser.close()
filePasswd.close()
fileIP.close()
#
#
clear()
print ()
print(stylize("PLEASE NOTE: ",red_text))
print ()
print("The provided username, password, and IP/hostname for Orchestrator have been encoded and stored locally.")
print ()
print("The filenames are: "+ stylize(" .orch_user.out, .orch_passwd.out, and .orch_ip.out.",blue_text))
print ()
print(stylize("PLEASE DELETE THESE FILES WHEN YOU ARE DONE!",red_text))
print ()
print ()