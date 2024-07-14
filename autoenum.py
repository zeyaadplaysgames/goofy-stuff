#!/usr/bin/env python3

import argparse
import subprocess
import re
import xml.etree.ElementTree as ET
import os

gobuster_wordlist = '/usr/share/wordlists/dirb/big.txt'
workspace_name = 'autoenum_out'

def check_root():
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)

def workspace(workspace_name):
    try:
        subprocess.run(['mkdir', workspace_name], check=True)
        print(f"* Workspace '{workspace_name}' created.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating workspace '{workspace_name}': maybe it already exists?")
        print({e})
        raise

def portscan(host, output_dir):
    try:
        with open(os.path.join(output_dir, 'ports.txt'), 'w') as outfile:
            subprocess.run(['rustscan', '-a', host], stdout=outfile, text=True, check=True)
        print("* Port scanning completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error running rustscan:9. Improved Error Handling {e}")
        raise

def extract_ports_from_file(filename):
    ports = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                match = re.search(r'Open (\d+\.\d+\.\d+\.\d+):(\d+)', line)
                if match:
                    port_number = match.group(2)
                    ports.append(port_number)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        raise

    formatted_ports = ','.join(ports)
    return formatted_ports

def nmap(host, extracted_ports, output_dir):
    try:
        print('* Running nmap...')
        subprocess.run(['nmap','-sC', '-sV', '-p', extracted_ports, '-oA', os.path.join(output_dir, 'init'), host], check=True)
        print('* Nmap scan completed.')
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        raise

def grep_http(output_dir):
    http_ports = []
    try:
        tree = ET.parse(os.path.join(output_dir, 'init.xml'))
        root = tree.getroot()

        for host in root.findall('host'):
            for port in host.findall('ports/port'):
                portid = port.attrib['portid']
                for service in port.findall('service'):
                    if 'http' in service.attrib['name'].lower():
                        http_ports.append(portid)
                        print(f"HTTP Service found on Port {portid}: {service.attrib['name']}")
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        raise
    except FileNotFoundError:
        print(f"Error: File 'init.xml' not found in '{output_dir}'.")
        raise
    
    return http_ports

def run_gobuster(host, ports, output_dir):
    for port in ports:
        url = f'http://{host}:{port}'
        try:
            print(f"* Running gobuster on {url}...")
            subprocess.run(['gobuster', 'dir', '--url', url, '-o', os.path.join(output_dir, f'gobuster_{host}_{port}.txt'), '-w', gobuster_wordlist], check=True)
            print(f"* Gobuster scan on port {port} completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error running gobuster on port {port}: {e}")
            raise

if __name__ == "__main__":
    check_root
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Target host IP address.', required=True)
    parser.add_argument('--port-scan', action='store_true', help='Perform port scanning with rustscan/nmap.')
    parser.add_argument('--gobuster', action='store_true', help='Run gobuster on HTTP ports found by rustscan/nmap.')
    args = parser.parse_args()

    output_dir = os.path.abspath(workspace_name)  # Absolute path to output directory

    if not (args.port_scan or args.gobuster):
        parser.error("No action specified. Please use --port-scan or --gobuster.")

    try:
        if args.port_scan:
            workspace(output_dir)
            portscan(args.host, output_dir)  # Perform port scanning with rustscan

            # Proceed with nmap, grep_http, run_gobuster if --port-scan was specified
            extracted_ports = extract_ports_from_file(os.path.join(output_dir, 'ports.txt'))
            nmap(args.host, extracted_ports, output_dir)
            http_ports = grep_http(output_dir)

            if args.gobuster and http_ports:
                run_gobuster(args.host, http_ports, output_dir)
            elif args.gobuster and not http_ports:
                print("No HTTP ports found for gobuster.")
        else:
            print("No action specified. Use -h if you're stuck.")

    except Exception as e:
        print(f"Error: {e}")
