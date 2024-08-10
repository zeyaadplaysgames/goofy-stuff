#!/bin/bash

RED='\033[31m'
BLUE='\033[94m'
RESET='\033[0m'
GREEN='\033[32m'
WHITE='\033[37m'
BOLD='\033[1m'

# list of dependencies
dependencies=('rustscan' 'nmap' 'nikto' 'enum4linux')

# checks for dependencies
echo -e "${BLUE}[~]${RESET} checking if required programs are installed"

for prog in "${dependencies[@]}"; do
    if ! command -v "$prog" &> /dev/null; then
    
        until [[ "$install" == "y" || "$install" == "n" || "$install" == "Y" || "$install" == "N" ]]; do
            read -p "${BOLD}${RED}[!]${RESET} Dependency $prog is not installed, would you like to install it? (y/n): " install
        done 

        if [[ "$install" == "y" || "$install" == "Y" ]]; then
            if [[ "$prog" == 'rustscan' ]]; then
                echo -e "${BOLD}${GREEN}[${WHITE}*${GREEN}]${RESET} installing rustscan..."
                cd ~/Downloads
                wget 'https://github.com/RustScan/RustScan/releases/download/2.3.0/rustscan_2.3.0_amd64.deb' -O rustscan.deb || { echo -e "${RED}[!]${RESET} Failed to download rustscan"; exit 1; }
                sudo apt update -y
                sudo dpkg -i ~/Downloads/rustscan.deb || { echo -e "${RED}[!]${RESET} Failed to install rustscan"; exit 1; }
            else
                sudo apt update -y
                sudo apt install "$prog" -y || { echo -e "${RED}[!]${RESET} Failed to install $prog"; exit 1; }
            fi
        else
            echo "Skipping installation of $prog."
        fi
    else
        echo -e "${BOLD}${GREEN}[${WHITE}*${GREEN}]${RESET} Dependency $prog is installed."
    fi
done

# Prompt for the target host
until [ -n "$rhost" ]; do
    read -p 'What is the host that you want to enumerate? ' rhost
done

# prompts for the output directory name location
until [ -n "$out" ]; do
    read -p 'Enter the name of the directory to store output files in: ' out
done

#this just checks if the output path is absolute or inside the current dir 
if [[ "$out" = /* ]]; then
    OUTPATH="$out"
else
    OUTPATH="$(pwd)/$out"
fi

echo "Storing files in $OUTPATH"
echo -e "${BLUE}[~]${RESET} Running rustscan/nmap on $rhost"

# changes to output directory to store files
cd "$OUTPATH"

until [[ -n "$rustscan_filename" ]]; do
    read -p "Enter a name for your nmap scan on $rhost: " rustscan_filename
done

rustscan -a "$rhost" -- -sC -sV -A -oA "$rustscan_filename" || { echo -e "${RED}[!]${RESET} Rustscan failed"; exit 1; }

# setting an nmap output variable to save myself some time
nmap_output=$(cat "$OUTPATH/$rustscan_filename.nmap")

# checks for/extracts http/smb ports
http_ports=$(echo "$nmap_output" | grep -E '^[0-9]+/tcp.*open.*http' | awk '{print $1}' | cut -d'/' -f1)
smb_ports=$(echo "$nmap_output" | grep -E '^[0-9]+/tcp.*open.*(netbios-ssn|microsoft-ds)' | awk '{print $1}' | cut -d'/' -f1)

if [ -n "$smb_ports" ]; then
    until [[ "$enum4linux" == "y" || "$enum4linux" == "n" || "$enum4linux" == "Y" || "$enum4linux" == "N" ]]; do
        read -p "${BLUE}[~]${RESET} SMB port found, run enum4linux? (y/n): " enum4linux
    done

    if [[ "$enum4linux" == "y" || "$enum4linux" == "Y" ]]; then
        echo -e "${BLUE}[~]${RESET} running enum4linux on $rhost"
        enum4linux "$rhost" &
    fi
fi

# Check if any HTTP ports were found
if [ -z "$http_ports" ]; then
    echo "No HTTP ports found."
    exit 1
else
    for port in $http_ports; do
        echo -e "${BLUE}[~]${RESET} HTTP running at port $port"
        
        # Prompt to fuzz directories using Gobuster/nikto
        until [[ "$gobuster" == "y" || "$gobuster" == "n" || "$gobuster" == "Y" || "$gobuster" == "N" ]]; do
            read -p "HTTP port found on $rhost:$port. Fuzz directories with Gobuster? (y/n): " gobuster      
        done

        until [[ "$nikto" == "y" || "$nikto" == "n" || "$nikto" == "Y" || "$nikto" == "N" ]]; do
            read -p "Run nikto on $rhost:$port ? (y/n): " nikto
        done

        if [[ "$gobuster" == "y" || "$gobuster" == "Y" ]]; then
            echo "Running Gobuster on $rhost port $port..."
            gobuster dir --url "http://$rhost:$port/" --wordlist /usr/share/wordlists/dirb/big.txt -x php,html,aspx,js,txt | tee "$OUTPATH/gobuster_$port.txt" &
        fi

        if [[ "$nikto" == "y" || "$nikto" == "Y" ]]; then
            echo "Running nikto on $rhost port $port..."
            nikto -host "$rhost:$port" | tee "$OUTPATH/nikto_$port.txt" &
        fi
    done
fi

echo -e "${BOLD}${GREEN}[${WHITE}*${GREEN}]${RESET} script completed running, check the files out at $OUTPATH"
clear
exit 1
# for when in testing 
# rm $OUTPATH/ -rf
