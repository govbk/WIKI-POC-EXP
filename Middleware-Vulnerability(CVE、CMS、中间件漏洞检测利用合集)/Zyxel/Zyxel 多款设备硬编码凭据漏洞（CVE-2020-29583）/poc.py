#!/usr/bin/env python3
#
# Scanner for potentially vulnerable ZyXEL products (CVE-2020-29583)
# https://github.com/2d4d/scan_CVE-2020-29583
#

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable warnings
import argparse
from netaddr import IPNetwork
import multiprocessing
import time
import subprocess
import re

import sys
import os

############################# kind of config ################################################
# set how many processes can run concurrently. gives missing file descriptor errors on my system if higher than ~1050 so 500 is a good value
max_processes    = 500
# max_processes * new_process_wait = "seconds a process has before it gets killed". should be >= 5, more is better for reliable results on slow networks
new_process_wait = 0.04

# if server doesn't respond before timeout, we assume it's patched
# setting the timeout too low can result in false negatives
timeout_secs = 5

# timeout to wait for all processes to be finished
timeout_end = timeout_secs + 2

###############################################################################################

def asn_to_ip(asn):
    # use ASN listings to enumerate whois information for scanning.
    cidr_list = []
    command = 'whois -h whois.radb.net -- \'-i origin %s\' | grep -Eo "([0-9.]+){4}/[0-9]+" | head' % (asn)
    asn_convert = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr_read = asn_convert.stderr.read().decode('utf-8')
    asn_convert = asn_convert.stdout.read().decode('utf-8').splitlines()

    # if we don't have whois installed
    if "whois: not found" in stderr_read:
        print("[-] In order for ASN looks to work you must have whois installed. Type apt-get install whois as an example on Debian/Ubuntu.")
        sys.exit()
    # iterate through cidr ranges and append them to list to be scanned
    for cidr in asn_convert:
        cidr_list.append(cidr)
    return cidr_list

def submit_url(url):
    with requests.Session() as s:
        r = requests.Request(method='GET', url=url)
        prep = r.prepare()
        prep.url = url
        try:
            return s.send(prep, verify=False, timeout=timeout_secs)
        except:
            # send fails hard on openssl errors like sslv3 only but that shouldn't happen in recently patched "security" devices
            pass

# checking if webpage is vulnerable version (can't distinguish between patched or not, the password is on twitter ... )
def webcheck(target, targetport, verbose):

    try:
        url1 = ("https://%s:%s" % (target,targetport))

        print("Webcheck on: %s                            " % url1, end="\r") # Cleaning up output a little

        req1 = submit_url(url1)

        if req1:
            cont1 = str(req1.content)

            if (
                    # vuln USG40
                    'v=200406233228' in cont1 or
                    # vuln ZyWall 310 or 1100
                    'v=201016202846' in cont1 or
                    # vuln ZyWall 110
                    'v=201017003047' in cont1 
                ):
                print("[\033[91m!\033[0m] This is a vulnerable ZyXEL device: %s                                                                " % (target))
                # write to log and flush to have the results if something crashes
                logfile.write("Vulnerable: " + target + "\n")
                logfile.flush()
            else:
                r = re.search(r'<title>(.+?)</title>', cont1)
                if r:
                    title = r.group(1).upper()

                    for device in CVE_2020_29583_devices:
                        if device in title:
                            print("[+] This is a potentially vulnerable ZyXEL device: %s %s                                                                " % (target, title))
                            # write to log and flush to have the results if something crashes
                            logfile.write(target + " device: " + device + "\n")
                            logfile.flush()
                            vulnServers.append(target)
                            break
            return 1

    # handle exception errors due to timeouts
    except requests.ReadTimeout:
        if verbose == True: print("[-] ReadTimeout: Server %s timed out and didn't respond on port: %s." % (target, targetport))
        pass

    except requests.ConnectTimeout:
        if verbose == True: print("[-] ConnectTimeout: Server %s did not respond to a web request or the port (%s) is not open." % (target, targetport))
        pass

    except requests.ConnectionError:
        if verbose == True: print("[-] ConnectionError: Server %s did not respond to a web request or the port (%s) is not open." % (target,targetport))
        pass

    # all other exceptions:
    except requests.exceptions.RequestException as e:
        print(e)

def start_scan_process(ip, port, verbose):
    global counter

    process = multiprocessing.Process(target=webcheck, args=(ip,port, verbose))

    process.start()

    # keep list of all running processes
    all_processes.append(process)

    # wait a bit to not create processes too fast
    time.sleep(new_process_wait)
    counter = counter + 1

    # kill the oldest process hard if more than max_processes are running, because every process uses 13 file descriptors for SSL libs
    # that's not clean programming, reason is this error in pythons OpenSSL https://github.com/pyca/pyopenssl/issues/168 
    # which prevents setting a timeout on the dtls handshake so it takes forever if the destination isn't responding
    if verbose: print("num of processes running: " + str(len(all_processes)))
    if len(all_processes) > max_processes:
        oldest_proc = all_processes.pop(0)
        # goodbye cruel world
        oldest_proc.terminate()

def parse_target_args(target, port, verbose):
    # cidr lookups for ASN lookups
    if re.match ("as\d\d\d", target, re.IGNORECASE) :
        CIDR_Blocks = asn_to_ip(target)
        for ip_block in CIDR_Blocks:
            for ip in IPNetwork(ip_block):
                start_scan_process(ip,port,verbose)

    # if we are iterating through IP addresses to scan CIDR notations
    elif "/" in target:
        for ip in IPNetwork(target):
            start_scan_process(str(ip),port,verbose)

    # if we are just using 1 IP address
    else:
        start_scan_process(target,port, verbose)


print("""
Multithreaded scanner for Undocumented user account in ZyXEL products (CVE-2020-29583)
            __
 _____   _ / _|_      ___ __
|_  / | | | |_\ \ /\ / / '_ \\
 / /| |_| |  _|\ V  V /| |_) |
/___|\__, |_|   \_/\_/ | .__/
     |___/             |_|
The scanner can use:
* IPs
* CIDR notations, for example: 192.168.1.0/24
* Hostnames
* Routing AS, e.g. as1234
* Plaintext files containing anything of the above, one entry per line, passed as e.g. file:netlist.txt
Example:  python3 scan_CVE-2020-29583.py 192.168.1.1/24            
Example3: python3 scan_CVE-2020-29583.py 192.168.1.1
Example4: python3 scan_CVE-2020-29583.py fakewebsiteaddress.com
Example5: python3 scan_CVE-2020-29583.py as15169
Example6: python3 scan_CVE-2020-29583.py file:hostfile.txt
Debian/Kali needs: apt-get install python3-netaddr
""")

# for sharing global variables in multiprocessing
manager = multiprocessing.Manager()
vulnServers = manager.list()

# collect certificates of each socket
cert_of_sock = {}

# process queue to kill oldest, FIFO
all_processes = []

# counter of scanned IPs
counter = 0

# parse our commands
parser = argparse.ArgumentParser()
parser.add_argument("target", help="server to check (defaults https)")
parser.add_argument("--port", "-p", help="the target port (default 443)")
parser.add_argument("--verbose", "-v", action='store_true', help="print out verbose information")
args = parser.parse_args()

t = time.strftime('%Y%m%dT%H%M%S')

CVE_2020_29583_devices = ('USG20-VPN', 'USG20W-VPN', 'USG40', 'USG40W', 'USG60', 'USG60W', 'USG110', 'USG210', 'USG310', 'USG1100', 'USG1900', 'USG2200', 'ZYWALL', 'ATP100', 'ATP100W', 'ATP200', 'ATP500', 'ATP700', 'ATP800', 'VNP50', 'VPN100', 'VPN300', 'VPN000', 'USG FLEX', 'FLEX 100', 'FLEX 100W', 'FLEX 200', 'FLEX 500', 'FLEX 700', 'NXC2500', 'NXC5500' )

# if we specify a verbose flag
if args.verbose:
    verbose = True
else: verbose = False

if args.port:
    targetport = args.port
else: 
    targetport = 443

log = "scan_cve_2020-29583_port_" + str(targetport) + "_" + t + ".log"
print("Writting results to logfile: " + log)

with open(log, 'a') as logfile:

    # specify file option to import host:port
    if "file:" in (args.target):
        print("[*] Importing in list of hosts from filename: %s" % (args.target))
        with open(args.target.split(':')[1], 'r') as file:
            hosts= file.read().splitlines()
        for target_line in hosts:
            parse_target_args(target_line,targetport, verbose)

    else:
        parse_target_args(args.target, targetport, verbose)

time.sleep(1)
print("wait " + str(timeout_end) + " more seconds so all processes are hopefully finnished...")
time.sleep(timeout_end)

# do a report on servers
print("Finished testing. Below is a list system(s) identified:")

print("-" * 45)
for server in vulnServers:
    print(server)

print("-" * 45)

# do a report on servers
print("Tested %s servers: Found %s to be of the vulnerable version." % (counter, len(vulnServers)))

# once more ;)
print("Results written to logfile: " + log)
