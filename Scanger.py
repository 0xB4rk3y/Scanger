import sys
import ipaddress
import subprocess
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Initialize colorama
init()

def print_info(message):
    print(Fore.CYAN + message + Style.RESET_ALL)

def print_success(message):
    print(Fore.GREEN + message + Style.RESET_ALL)

def print_error(message):
    print(Fore.RED + message + Style.RESET_ALL)

def ping(ip):
    try:
       
        output = subprocess.check_output(["ping", "-n", "1", str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        if "TTL=" in output:
            return True
    except subprocess.CalledProcessError:
        return False
    return False

def scan_ip_range(start_ip, end_ip):
    devices = []


    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_ip = {executor.submit(ping, ipaddress.IPv4Address(ip_int)): ipaddress.IPv4Address(ip_int)
                        for ip_int in range(int(start_ip), int(end_ip) + 1)}


        for future in tqdm(as_completed(future_to_ip), total=len(future_to_ip), desc="Scanning IPs"):
            ip = future_to_ip[future]
            try:
                if future.result():
                    print_success(f"{ip} is active")
                    devices.append(str(ip))
                else:
                    print_info(f"{ip} is not reachable")
            except Exception as exc:
                print_error(f"{ip} generated an exception: {exc}")

    return devices

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--help":
        print("Usage:")
        print("python Scanger.py <start_ip> <end_ip>              - Scan IP range from start_ip to end_ip")
        print("python Scanger.py -f <filename.txt>                 - Scan IP addresses listed in filename.txt")
        sys.exit(0)

    if len(sys.argv) == 4:
        if sys.argv[1] == "-f":
            filename = sys.argv[2]
            try:
                with open(filename, 'r') as file:
                    ip_list = file.readlines()
                ip_list = [ip.strip() for ip in ip_list]
                print_info(f"Scanning IP addresses from file: {filename}")
                devices = []
                for ip in ip_list:
                    if ping(ip):
                        print_success(f"{ip} is active")
                        devices.append(ip)
                    else:
                        print_info(f"{ip} is not reachable")
                if devices:
                    print_info("Scan completed. Active devices found:")
                    print(f"{'IP Address':<16}    {'Status':<10}")
                    print("="*30)
                    for device in devices:
                        print(f"{device:<16}    {'Active':<10}")
                else:
                    print_info("Scan completed. No active devices found.")
            except FileNotFoundError:
                print_error(f"File not found: {filename}")
            except Exception as e:
                print_error(f"An error occurred: {e}")
            sys.exit(0)

    if len(sys.argv) != 3:
        print_error("Usage: python Scanner.py --help")
        sys.exit(1)

    try:

        start_ip = ipaddress.IPv4Address(sys.argv[1])
        end_ip = ipaddress.IPv4Address(sys.argv[2])
    except ipaddress.AddressValueError:
        print_error("Invalid IP address format")
        sys.exit(1)

    print(Fore.RED + """
  ██████  ▄████▄   ▄▄▄       ███▄    █   ▄████ ▓█████  ██▀███  
▒██    ▒ ▒██▀ ▀█  ▒████▄     ██ ▀█   █  ██▒ ▀█▒▓█   ▀ ▓██ ▒ ██▒
░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░▒███   ▓██ ░▄█ ▒
  ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓▒▓█  ▄ ▒██▀▀█▄  
▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒░▒████▒░██▓ ▒██▒
▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░  ░ ░  ░  ░▒ ░ ▒░
░  ░  ░  ░          ░   ▒      ░   ░ ░ ░ ░   ░    ░     ░░   ░ 
      ░  ░ ░            ░  ░         ░       ░    ░  ░   ░     
         ░                                                    
            """ + Style.RESET_ALL)

    print_info("Starting scan...")
    print_info(f"Scanning from {start_ip} to {end_ip}")

    devices = scan_ip_range(start_ip, end_ip)


    if devices:
        print_info("Scan completed. Active devices found:")
        print(f"{'IP Address':<16}    {'Status':<10}")
        print("="*30)
        for device in devices:
            print(f"{device:<16}    {'Active':<10}")
    else:
        print_info("Scan completed. No active devices found in the given IP range.")

if __name__ == "__main__":
    main()

# Copyright (c) 2024 Cengiz Berkay Kaya. All rights reserved.
