#!/usr/bin/python3
#
# 
# 
# Bugs/Issues: 
# 
# If there is no user defined application groups this script will fail, must create at least one placeholder application group for now.
#
#

# Standard library imports
import base64
import codecs
import datetime
import getpass
import ipaddress
import json
from os import system, name
import pathlib
import sys
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Third party imports
import colored
from colored import stylize
#from dotenv import load_dotenv

# Local application imports
from sp_orchhelper import OrchHelper


# Disable Certificate Warnings
urllib3.disable_warnings(category=InsecureRequestWarning)

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
# Console text highlight color parameters
#
red_text = colored.fg("red") + colored.attr("bold")
green_text = colored.fg("green") + colored.attr("bold")
blue_text = colored.fg("steel_blue_1b") + colored.attr("bold")
orange_text = colored.fg("dark_orange") + colored.attr("bold")
#
##########################################################################################################
#
# The following section is to check for stored credentials, and if found use them to login to the Orchestrator,
# or fallback to gathering user input.
#
##########################################################################################################
#
# Check for stored credentials generated from "python3 capture_credentials.py"
#
fileUserCheck = pathlib.Path(".orch_user.out") 
filePasswdCheck = pathlib.Path(".orch_passwd.out")
fileIPCheck = pathlib.Path(".orch_ip.out")
#
# If file with encoded username is found, decode data and use value, else enter username.
#
if fileUserCheck.exists ():
    print (stylize("NOTICE: ", red_text) + "Using Stored Credentials for Orch Username, use capture_credentials.py to update.")
    time.sleep( 0.2 )
    fileUser = open(".orch_user.out", "r").read()
    user = base64.b64decode(fileUser).decode('utf-8')
else:
    user = input ("Enter Valid Orchestrator Username:")
#
# If file with encoded password is found, decode data and use value, else enter password.
#
if filePasswdCheck.exists ():
    print (stylize("NOTICE: ", red_text) + "Using Stored Credentials for Orch Password, use capture_credentials.py to update.")
    time.sleep( 0.2 )
    filePasswd = open(".orch_passwd.out", "r").read()
    password = base64.b64decode(filePasswd).decode('utf-8')
else:
    password = getpass.getpass("Enter Password: ")
#
# If file with encoded Orch IP is found, decode data and use value, else enter IP.
#
if fileIPCheck.exists ():
    print (stylize("NOTICE: ", red_text) + "Using Stored IP for Orch IP, use capture_credentials.py to update.")
    time.sleep( 0.2 )
    fileIP = open(".orch_ip.out", "r").read()
    orch_url = base64.b64decode(fileIP).decode('utf-8')
else:
    orch_url = input ("Enter Orchestrator IP Address/Hostname: ")
#
##########################################################################################################
#
# Gather New B2B App Group Name
#
print ()
app_group_name = input (stylize("Enter New B2B Application Group Name: ", orange_text))
print ()
#
# Gather file with subnets
#
print ()
b2b_subnets = input (stylize("Enter File Name w/B2B Subnets: ", orange_text))
print ()
#
# Read in b2b_nets.txt and break it down...
#
f = codecs.open(b2b_subnets, 'r', encoding='utf-8')
lines = f.readlines()
f.close()
list = []
for i in range(len(lines)):
    list.append(lines[i].strip())
#
# Login to Orchestrator
#
orch = OrchHelper(orch_url, user, password)
orch.login()
#
##########################################################################################################
#
print ()
#
# For Each CIDR in B2B Nets convert to IP Range and then to Integer and push to Orchestrator as Address Map
#
app_def_names = []
#
for i in range(len(list)):
    net = ipaddress.ip_network(list[i], False)
        #
    if (net.network_address == net.broadcast_address):
            hostmin = net.network_address
            hostmax = net.broadcast_address
            app_def_net = net.network_address
    else:
            hostmin = net.network_address + 1
            hostmax = net.broadcast_address - 1
            app_def_net = net.network_address
    #
    ip_start = int(hostmin)
    ip_end = int(hostmax)
    #
    request_app_defs = orch.post_userDefined_app_addressMap(ip_start, ip_end, name=app_group_name + "_" + str(app_def_net), description="", priority=100)
    #
    if request_app_defs.status_code == (200):
        app_def_names.append(app_group_name + "_" + str(app_def_net))
    #
    else:
        print (stylize("Something went wrong...",red_text))
        print ("Error Returned :" + request_app_defs)
        print (app_group_name+ "_" + str(app_def_net))

#
##########################################################################################################
#
# Get current Application Groups config...
#
request_app_group = orch.get_userDefined_appGroups().json()
#
# Parse output as JSON
#
json_object = json.dumps(request_app_group)
json_data = json.loads(json_object)
#
# If no User Defined Application Groups exist, create one with the provided name
#
output_filename = 'new_app_groups.json'

if request_app_group.get("result") == "Not found" or request_app_group == {}:
    print("No existing User Defined Application Groups, creating new...")

    # Log the local data
    output_filename = 'new_app_groups.json'

    with open(output_filename, 'w') as new_json_file:
        p1 = '{ "'
        p2 = app_group_name
        p3 = '" : { "apps": ['
        p4 = ', '.join(['"{}"'.format(value) for value in app_def_names])
        p5 = '], "parentGroup": null }}'
        new_app_group = p1 + p2 + p3 + p4 + p5
        new_json_file.writelines(new_app_group)

    with open(output_filename, 'r') as data_file:
        data = json.load(data_file)

    post_app_groups = orch.update_userDefined_appGroups(data)

    exit()  
else:
    output_filename = 'current_app_groups.json'
    with open(output_filename, 'w') as data_file:
        write = data_file.write(json_object)

#
##########################################################################################################
#
input_filename = output_filename
output_filename = 'new_app_groups.json'
#
# Open/Read file with current Application Groups/Membership
#
with open(input_filename, 'r') as current_json_file:
    data = current_json_file.read()
    # Trim closing brackets
    trim = data[:-2]
#
# Create new file and write current App Groups and append new group
# 
# Note: This is super awful... need to improve this...
#
with open(output_filename, 'w') as new_json_file:
    #
    #print (app_def_names)
    #
    p1 = '}, "'
    p2 = app_group_name
    p3 = '" : { "apps": ['
    p4 = ', '.join(['"{}"'.format(value) for value in app_def_names])
    p5 = '], "parentGroup": null }}'
    new_app_group = p1 + p2 + p3 + p4 + p5
    new_json_file.writelines(trim)
    new_json_file.writelines(new_app_group)
#
print()
#
##########################################################################################################
#
input_filename = output_filename
#
# Read file with new App Groups and Post to Orchestrator....
#
with open(input_filename, 'r') as data_file:
        data = json.load(data_file)
        # Blank post to prevent duplications - ?
        blank = {}
        post_app_groups = orch.update_userDefined_appGroups(blank)
        # Post new App Groups Data
        post_app_groups = orch.update_userDefined_appGroups(data)
#
print ()
#
# If 200 OK print happy message...
#
if post_app_groups.status_code == (200):
    print (stylize("New Application Group: ",blue_text) + app_group_name + stylize(" added successfully!",green_text))
#
# Else print sad message...
#
else:
    print (stylize("Something went wrong...",red_text))
    print ("Error Returned :" + post_app_groups)
print()
#
##########################################################################################################
#
# Logout of Orchestrator - Our work here is done...
#
orch.logout()
print()
#
##########################################################################################################
#