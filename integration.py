#!/usr/bin/env python
#Created by Christian Bagdon and Joe Bagdon
#Christian's LinkedIn: https://www.linkedin.com/in/cbagdon
#Email: christian@bagdon.us, joe@bagdon.us

import sys, subprocess, os, fileinput, re, shutil

#Check system Python version, exit if version is not 2.7.*
if sys.version_info[0] != 2  or (sys.version_info[0] == 2 and sys.version_info[1] < 6):
	print ("Error! This script requires a Python version >= 2.6, but < 3!")
	sys.exit(1)

#Define global variables for use across multiple integrate functions
command = None
cb_server_token_input = None

#Function to delete the git repo
def delete_git():

	#Delete git directory
	print "\nRemoving git directory cbapi"

	try:
		shutil.rmtree('/root/cbapi')
		print "cbapi folder has been deleted"

	except:
		print "There is no folder to delete"
		pass

#Function to check the command. If command did not succeed, print error and exit.
def check_code():
	exit_code = command.returncode
	if exit_code != 0:
		print "\nCommand not successful! Please check command_log.txt for more details"
		sys.exit(1)
	elif exit_code == 0:
		print "\nCommand successful!"

#Assign file to commandlog variable. Will be used to pipe stdout and stderr to file.
commandlog = open("command_log.txt", "w")
print "\nA log will be created 'command_log.txt'. It will automatically be deleted if everything is successful."

#Function to delete log file
def delete_log():

	#Deleting log file since everything went fine.
	print "\nRemoving script log file since it looks like everything went good."

	try:
		os.remove('command_log.txt')
		print "Log file has been deleted."

	except:
		print "There is no log file to delete."
		pass

#Execute yum install git
print "\nExecuting 'yum install git' for later use ..."
command = subprocess.Popen(["/usr/bin/yum", "-y", "install", "git"], stdout=commandlog, stderr=commandlog)
command.wait()
commandlog.flush()
check_code()

#Cloning cbapi git repo
print "\nCloning cbapi git repo to /root/cbapi to later enable API's ..."

DIR_NAME = "/root/cbapi"
if os.path.isdir(DIR_NAME):
	shutil.rmtree(DIR_NAME)

cmd = "/usr/bin/git clone https://github.com/carbonblack/cbapi.git /root/cbapi"

try:
	command = subprocess.Popen(cmd, shell=True, stdout=commandlog, stderr=commandlog)
	command.wait()
	commandlog.flush()
	check_code()

except:
	sys.exit(1)

#The above is some what setting up the "prerequisites" for the program

#Put all integration functions or "modules" in here
def initialize():

	try:

		#Lists integration choices then prompts for choice
		print "\nList of supported integrations:  1:Wildfire | 2:FireEye"

		while True:
			integrate_choice = raw_input("\nWhich service would you like to integrate (choose corresponding number)?: ")

			if integrate_choice == "1" or integrate_choice == "2":
				break

			else:
				print "Choice not supported! Please check spelling!"

		if integrate_choice == "1":
			wildfire_integrate()

		elif integrate_choice == "2":
			fireeye_integrate()

	except KeyboardInterrupt:
		delete_git()
		sys.exit(1)

#Function to put at every end of integrateion function to prompt for another integration
def another_integration():

	try:
		while True:
			another_integrate = raw_input("\nWould you like to do another integration (y/n)?: ").lower()

			if another_integrate == "y" or another_integrate == "n":
				break

			else:
				print "\nChoice not supported! Please choice 'y' for yes, or 'n' for no!"

		if another_integrate == "y":
			initialize()

		elif another_integrate == "n":
			delete_git()
			print "\nSee you later!\n"
			sys.exit(1)

	except KeyboardInterrupt:
		delete_git()
		sys.exit(1)

#Opens filename "Wildfire.repo", assigns to repofile, and opens with option "write" (w)
def wildfire_integrate():

	try:

		global commandlog, command, cb_server_token_input

		repofile = open(os.path.join("/etc/yum.repos.d/", "Wildfire.repo"), "w")
		print "\nWriting Wildfire .repo file..."

		#Writes to Wildfire repo
		repofile.write("[Wildfire]\n\nname=Wildfire\n" \
					   "baseurl=https://yum.carbonblack.com/enterprise/integrations/wildfire/x86_64\n\n" \
					   "gpgcheck=0\n"
					   "enabled=1\n\n"
					   "metadata_expire=60\n"
					   "sslverify=1\n\n"
					   "sslclientcert=/etc/cb/certs/carbonblack-alliance-client.crt\n"
					   "sslclientkey=/etc/cb/certs/carbonblack-alliance-client.key\n")

		#Signify closing of interaction with repofile
		repofile.close()
		print "Writing successful!"

		#Execute yum info python-cb-wildfire-bridge.
		print "\nExecuting 'yum info python-cb-wildfire-bridge' ..."

		command = subprocess.Popen(["/usr/bin/yum", "info", "python-cb-wildfire-bridge"], stdout=commandlog, stderr=commandlog)
		command.wait()
		commandlog.flush()
		check_code()

		#Execute yum install python-cb-wildfire-bridge
		print "\nExecuting 'yum install python-cb-wildfire-bridge' ..."

		command = subprocess.Popen(["/usr/bin/yum", "-y", "install", "python-cb-wildfire-bridge"], stdout=commandlog, stderr=commandlog)
		command.wait()
		commandlog.flush()
		check_code()

		#Ensuring that there is no old API key in the config file.
		#This is a slightly crude implementation combining python and bash.
		os.system("sed -e 's/wildfire_api_keys=.*$/wildfire_api_keys=/' /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf > /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf.bak; mv /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf.bak /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf")
		os.system("sed -e 's/carbonblack_server_token=.*$/carbonblack_server_token=/' /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf > /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf.bak; mv /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf.bak /etc/cb/integrations/carbonblack_wildfire_bridge/carbonblack_wildfire_bridge.conf")

		#Assigns input string to var api_keys, then writes to conf file
		api_keys_input = raw_input("\nEnter Wildfire api keys (Semi-colon between each key if multiple): ")
		api_keys = "wildfire_api_keys=" + api_keys_input
		print "\nEntering API keys..."

		#Finds API keys line then adds keys from api_keys
		for line in fileinput.input(os.path.join("/etc/cb/integrations/carbonblack_wildfire_bridge/", "carbonblack_wildfire_bridge.conf"), inplace = 1):
			print line.replace("wildfire_api_keys=", api_keys),

		#Checks to see if user has already ran the another integration
	    #and input a server token, using the token variable.
	    #if not, prompt for that token.
		if cb_server_token_input == None:
			cb_server_token_input = raw_input("\nEnter CarbonBlack Server Token: ")

		cb_server_token = "carbonblack_server_token=" + cb_server_token_input
		print "\nEntering Carbon Black Server Token..."

		#Finding CB Server Token line then adds token from cb_server_token variable
		for line in fileinput.input(os.path.join("/etc/cb/integrations/carbonblack_wildfire_bridge/", "carbonblack_wildfire_bridge.conf"), inplace = 1):
			print line.replace("carbonblack_server_token=", cb_server_token),

		#Start Wildfire bridge and print output
		print "\nStarting Wildfire bridge ..."

		try:
			command = subprocess.Popen(["/etc/init.d/cb-wildfire-bridge", "start"], stdout=commandlog, stderr=commandlog)
			command.wait()
			commandlog.flush()
			check_code()

		except:
			sys.exit(1)

		#Running api
		print "\nAdding Wildfire to Carbon Black API feed"
		cmd = "python /root/cbapi/client_apis/python/example/feed_add.py -c https://127.0.0.1 -a %s -n -u http://localhost:4000/wildfire/json -e True" % cb_server_token_input
		try:
			command = subprocess.Popen(cmd, shell=True, stdout=commandlog, stderr=commandlog)
			command.wait()
			commandlog.flush()
			check_code()

		except:
			sys.exit(1)

		delete_log()

		#Final message to user if everything finishes successful
		print "\nAll processes completed successfully!"

		another_integration()

	except KeyboardInterrupt:
		delete_git()
		sys.exit(1)

def fireeye_integrate():

	try:

	  global commandlog, command, cb_server_token_input
	  count = 0

	  ######Temp writing the wildfire repo to install the latest cbapi rpm that's not included
	  ######in the FireEye repo. Temporary fix.
	  repofile = open(os.path.join("/etc/yum.repos.d/", "Wildfire.repo"), "w")
	  print "\nWriting Wildfire .repo file..."

	  #Writes to Wildfire repo
	  repofile.write("[Wildfire]\n\nname=Wildfire\n" \
					 "baseurl=https://yum.carbonblack.com/enterprise/integrations/wildfire/x86_64\n\n" \
					 "gpgcheck=0\n"
					 "enabled=1\n\n"
					 "metadata_expire=60\n"
					 "sslverify=1\n\n"
					 "sslclientcert=/etc/cb/certs/carbonblack-alliance-client.crt\n"
					 "sslclientkey=/etc/cb/certs/carbonblack-alliance-client.key\n")

	  #Signify closing of interaction with repofile
	  repofile.close()
	  print "Writing successful!"
	  ##################Temp Repo Written Above#############

	  repofile = open(os.path.join("/etc/yum.repos.d/", "FireEye.repo"), "w")
	  print "\nWriting FireEye .repo file..."

	  #Writes to FireEye epo
	  repofile.write("[FireEye]\n\nname=FireEye\n" \
					 "baseurl=https://yum.carbonblack.com/enterprise/integrations/fireeye/x86_64\n\n" \
					 "gpgcheck=0\n"
					 "enabled=1\n\n"
					 "metadata_expire=60\n"
					 "sslverify=1\n\n"
					 "sslclientcert=/etc/cb/certs/carbonblack-alliance-client.crt\n"
					 "sslclientkey=/etc/cb/certs/carbonblack-alliance-client.key\n")

	  #Signify closing of interaction with repofile
	  repofile.close()
	  print "Writing successful!"

	  #Execute yum info python-cb-fireeye-bridge
	  print "\nExecuting 'yum info python-cb-fireeye-bridge' ..."

	  command = subprocess.Popen(["/usr/bin/yum", "info", "python-cb-fireeye-bridge"], stdout=commandlog, stderr=commandlog)
	  command.wait()
	  commandlog.flush()
	  check_code()

	  #Execute yum install python-cb-fireeye-bridge
	  print "\nExecuting 'yum install python-cb-fireeye-bridge' ..."

	  command = subprocess.Popen(["/usr/bin/yum", "-y", "install", "python-cb-fireeye-bridge"], stdout=commandlog, stderr=commandlog)
	  command.wait()
	  commandlog.flush()
	  check_code()

	  #Ensure there is no old Carbonblack_server_token
	  #This is a slightly crude implementation combining python and bash
	  os.system("sed -e 's/carbonblack_server_token=.*$/carbonblack_server_token=/' /etc/cb/integrations/carbonblack_fireeye_bridge/carbonblack_fireeye_bridge.conf > /etc/cb/integrations/carbonblack_fireeye_bridge/carbonblack_fireeye_bridge.conf.bak; mv /etc/cb/integrations/carbonblack_fireeye_bridge/carbonblack_fireeye_bridge.conf.bak /etc/cb/integrations/carbonblack_fireeye_bridge/carbonblack_fireeye_bridge.conf")

	  #Checks to see if user has already ran the wildfire integration
	  #and input a server token, using the token variable.
	  #if not, prompt for that token.
	  if cb_server_token_input == None:
		cb_server_token_input = raw_input("\nEnter CarbonBlack Server Token: ")

	  cb_server_token = "carbonblack_server_token=" + cb_server_token_input

	  #Find CB Server Token line then replace with cb_server_token
	  for line in fileinput.input(os.path.join("/etc/cb/integrations/carbonblack_fireeye_bridge/", "carbonblack_fireeye_bridge.conf"), inplace = 1):
		print line.replace("carbonblack_server_token=", cb_server_token),

	  #Start FireEye bridge
	  print "\nStarting FireEye bridge ..."

	  try:
		command = subprocess.Popen(["/etc/init.d/cb-fireeye-bridge", "start"], stdout=commandlog, stderr=commandlog)
		command.wait()
		commandlog.flush()
		check_code()

	  except:
		sys.exit(1)

	  print "\nEditing iptables ..."

	  #Edit iptables with function

	  file = open(os.path.join("/etc/sysconfig", "iptables"), "r")

	  for line in file:

		  if "INPUT -p tcp -m state --state NEW -m tcp --dport 3000 -j ACCEPT" in line:
			  print "\niptables is already configured..."
			  count +=1

	  file.close()

	  if count == 0:
		  file = open(os.path.join("/etc/sysconfig", "iptables"), "r")

		  for line in file:
			  if "INPUT" and "j ACCEPT" in line:
				  count +=1

		  cmd = "/sbin/iptables -I INPUT %s -m state --state NEW -m tcp -p tcp --dport 3000 -j ACCEPT" % count
		  print "\nEntering new line in iptables..."

		  command = subprocess.Popen(cmd, shell=True, stdout=commandlog, stderr=commandlog)
		  command.wait()
		  commandlog.flush()
		  check_code()

		  #Saving iptables
		  print "Saving iptables..."

		  command = subprocess.Popen(["service", "iptables", "save"])
		  command.wait()
		  commandlog.flush()
		  check_code()

	  print "\nEditing finished!"

	  #Running API
	  print "\nAdding FireEye to Carbon Black API feed"

	  cmd = "python /root/cbapi/client_apis/python/example/feed_add.py -c https://127.0.0.1 -a %s -n -u http://localhost:3000/fireeye/json -e True" % cb_server_token_input

	  try:
		  command = subprocess.Popen(cmd, shell=True, stdout=commandlog, stderr=commandlog)
		  command.wait()
		  commandlog.flush()
		  check_code()

	  except:
		  sys.exit(1)

	  delete_log()

	  #"Final" message to user if everything is successful
	  print "\nAll processes completed successfully!"

	  another_integration()

	except KeyboardInterrupt:
		delete_git()
		sys.exit(1)

initialize()
