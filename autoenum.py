#!/usr/bin/env python3

import subprocess
from pathlib import Path
import os
import sys
import re
import shutil

gobuster_wordlist_default = '/usr/share/wordlists/dirb/big.txt'
nmap_outfile_default = 'initial'

# Colors for success and error
green = '\033[92m'
red = '\033[91m'
white = '\033[97m'
bold = '\033[1m'
reset = '\033[0m'
blue = '\033[94m'

# [*] errors are going to be marked as {red}{bold}[!]{reset}
# [*] green is {green}{bold}[{reset}{bold}*{green}]{reset}

if __name__ == "__main__":
    required_programs = ['rustscan', 'gobuster', 'nikto']
    missing_programs = [program for program in required_programs if not shutil.which(program)]
    
    if missing_programs:
        print(f'{red}{bold}[!]{reset} Missing required programs: {", ".join(missing_programs)}')
        if 'rustscan' in missing_programs:
            print(f'{red}{bold}[!]{reset} rustscan is not installed, download it from their GitHub')
        a = input('Would you like to install them (y/n)? ')
        if a.lower() == 'y':
            for program in missing_programs:
                subprocess.run(['apt-get', 'install', program, '-y']) 
        else:
            exit()
    
    uid = os.geteuid()
    if uid == 0:
        print(f'{blue}[~]{reset} Running this script as {red}{bold}root{reset}...')
        current_dir = os.getcwd()
        output_dir = input('Enter the location to save all the output files > ')
        if output_dir == '' or output_dir == '\n':
            output_dir = 'autoenum_out'
        workspace_path = Path(current_dir) / output_dir
        print(f'Saving files to {workspace_path}')

        if workspace_path.exists():
            if workspace_path.is_dir():
                print(f'{red}{bold}[!]{reset} Directory {workspace_path} already exists!\n')
                sure1 = input('Would you like to delete it? y/n > ')
                if sure1.lower() != 'y':
                    exit()
                else:
                    sure2 = input('Are you sure? y/n > ')
                    if sure2.lower() == 'y':
                        subprocess.run(['rm', '-rf', str(workspace_path)])
                        print(f'{red}{bold}[!]{reset} Directory deleted. Restarting the script...')
                        os.execv(sys.executable, ['python3'] + sys.argv)
                    else:
                        os.execv(sys.executable, ['python3'] + sys.argv)
            else:
                print(f'{red}{bold}[!]{reset} Path exists but is not a directory: {workspace_path}')
                sys.exit(1)
        else:
            try:
                workspace_path.mkdir(parents=True, exist_ok=False)
                print(f'{blue}[~]{reset} Directory created at {workspace_path}\n')
            except Exception as e:
                print(f'{red}{bold}[!]{reset} Unexpected error: {e}')
                sys.exit(1)

        host = input('What is the host you are enumerating? > ')
        nmap_outfile = input("Enter a name for your nmap scan's file > ")
        if not nmap_outfile:
            nmap_outfile = 'initial'
        print(f'saving the nmap scan as {nmap_outfile}')
        print(f'{blue}[~]{reset} Running rustscan on {host}...')

        try:
            rustscan_output_file = workspace_path / 'rustscan.txt'
            with open(rustscan_output_file, 'w') as outfile:
                subprocess.run(['rustscan', '-a', host, '--', '-sC', '-sV', '-A', '-T4', '-O', '-vvv', '-oA', str(workspace_path / nmap_outfile)], stdout=outfile, text=True, check=True)
            print(f'{green}{bold}[{reset}{bold}*{green}]{reset} Rustscan completed successfully')

            http_ports = []
            with open(rustscan_output_file, 'r') as file:
                for line in file:
                    if re.search(r'open.*http', line):
                        match = re.search(r'(\d+)/tcp', line)
                        if match:
                            port = match.group(1)
                            http_ports.append(port)
            
            if http_ports:
                print(f'{blue}[~]{reset} Found HTTP ports: {", ".join(http_ports)}')
                for port in http_ports:
                    run_gobuster = input(f'HTTP port found at {host}:{port}. Run Gobuster? y/n > ')
                    nikto = input('Also run nikto? (y/n) > ')
                    if run_gobuster.lower() == 'y':
                        try:
                            gobuster_output = workspace_path / f'gobuster_{port}.txt'
                            gobuster_wordlist = input('Enter the path to your Gobuster wordlist: ')
                            if not gobuster_wordlist:
                                gobuster_wordlist = '/usr/share/wordlists/dirb/big.txt'
                                print(f'{blue}[~]{reset} No wordlist given, defaulting to {gobuster_wordlist}')
                            if not Path(gobuster_wordlist).is_file():
                                print(f'{red}{bold}[!]{reset} Wordlist file not found: {gobuster_wordlist}')
                                sys.exit(1)
                            with open(gobuster_output, 'w') as outfile:
                                subprocess.run(['gobuster', 'dir', '-u', f'http://{host}:{port}', '-w', gobuster_wordlist, '-x', 'php,js,html,txt', '-o', str(gobuster_output)], stdout=outfile, text=True, check=True)
                            print(f'{green}{bold}[{reset}{bold}*{green}]{reset} Gobuster scan on port {port} completed successfully')
                        except subprocess.CalledProcessError as e:
                            print(f'{red}{bold}[!]{reset} Error running Gobuster on port {port}: {e}')
                    if nikto.lower() == 'y':
                        try:
                            subprocess.run(['nikto', '-h', f'{host}:{port}'], check=True)
                            print(f'{green}{bold}[{reset}{bold}*{green}]{reset} Nikto scan on port {port} completed successfully')
                        except subprocess.CalledProcessError as e:
                            print(f'{red}{bold}[!]{reset} Error running Nikto on port {port}: {e}')
            else:
                print(f'{blue}[~]{reset} No HTTP ports found.')

        except subprocess.CalledProcessError as e:
            print(f'{red}{bold}[!]{reset} Error running rustscan: {e}')
            sys.exit(1)
    else:
        print(f'{red}{bold}[!]{reset} You are {green}{bold}not root{reset}')
