#just some wifi autopwn script
#things to add:
#airodump-ng 
#capturing the wpa handshake (better if program detects)
#automatically deauthing clients
#maybe automatically cracking the handshake?

import os
import time
import sys

def proceed():
	# defining this goofy text effect, might delete later :/
	print("Before you start this script,note that all your network interfaces will be closed. Your internet connection will be cut.\n Please use this script for ethical hacking purposes 🙏🙏")
	print('Proceeding in 5..\n')
	time.sleep(0.5)
	print('Proceeding in 4..\n')
	time.sleep(0.5)
	print('Proceeding in 3..\n')
	time.sleep(0.5)
	print('Proceeding in 2..\n')
	time.sleep(0.5)
	print('Proceeding in 1..\n')
	time.sleep(0.5)

# checking if user is root or not
if os.geteuid() == 0 :
	proceed()
		
	yesorno = input('do you still want to proceed? y/n ')

	if yesorno == 'y':
	#configuring airmon-ng and killing conflicting processes
		print('killing conflicting proccesses')
		os.system('airmon-ng check kill &')
		time.sleep(3)
		os.system('ip a')
		print('\n')
		interface = input('which Network interface would you like to use? ')
		os.system('airmon-ng start ' + interface)
		print('\n')
		time.sleep(2)
		print('airmon-ng is up:)\n')
		
		#getting network mac address and channel of wifi network to attack
		print('starting airodump-ng, press ctrl + C when ready\n')
		print()
		print()
		print()
		os.system ('airodump-ng ' + interface)
		time.sleep(5)
		bssid = input('what is the BSSID of the network your are going to attack? ')
		channel = input('on what channel is the network that you are going to attack on? ')
		output = input('what do you want your output file to be called? ')
		#setting up airodump ng to target a specific network
		os.system('airodump-ng -w' + output) 

		
	else :
		print('ok then closing lol')
		exit()
else:
	#scripts closes if not run as root
	print("\nThis script must be run as root")
	time.sleep(1)
	exit()
