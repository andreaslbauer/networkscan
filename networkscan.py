#!/usr/bin/python3.6

# python program to scan network and find HTTP servers, pingable servers, ssh accessible servers
# source code at https://github.com/andreaslbauer/networkscan/blob/master/networkscan.py
# Force Jenkins build

import requests
import socket
import os
import paramiko
import time
import socket
from requests import get

# logging facility: https://realpython.com/python-logging/
import logging

# port list and base address to scan
portList = ["5000", "8080", "8081", "8088", "80", "8089", "8100"]
baseAddress = "192.168.0."
interactive = None

# print but only if interactive flag is "on"
def printIfInteractive (*args, **kwargs):
    if interactive:
        print(*args, **kwargs)

# create list of addresses on 192.168.0 subnet
def createAddressList() :
    addresses = []
    for i in range(1, 255):
        addresses.append(baseAddress + str(i))

    #addresses = ["192.168.0.100", "192.168.0.133"]

    return addresses

# attempt to ping an address
def testPing(address):
    printIfInteractive(f"\rPinging {address}                                             ", end="")

    # first try to ping the address
    pingResponse = os.system("ping -c 2 -w 3 " + address + " > /dev/null 2>&1")
    if pingResponse == 0:
        hostname = "unknown"
        try:
            hostname = socket.gethostbyaddr(address)[0]
        except Exception as e:
            pass

            printIfInteractive(f"\rPing response from {address} hostname {hostname}: {pingResponse}")

# attempt ssh connection
def testSSH(address):
    printIfInteractive(f"\rTesting ssh for {address}                  ", end="")

    nbytes = 4096
    command = "hostname && uname -a && uptime && df -h . && ps -elf | grep python | grep -v grep"
    username = "pi"
    password = "alex5"
    hostname = address

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.readlines()
        errors = stderr.readlines()

        # create single string from output
        outputStr = ""
        for line in output:
            outputStr = outputStr + line

        # create single string from errors
        errorStr = ""
        for line in errors:
            errorStr = errorStr + line

            printIfInteractive(f"\rssh response at {address}: \n{outputStr} \n{errorStr}")

    except Exception as e:
        pass

    try:
        client.close()

    except Exception as e:
        pass


# test address for HTTP responses
def testHTTP(address):

    success = False

    # now look for HTTP responses
    for port in portList:

        # build an URL string
        success = False

        url = f"http://{address}:{port}"
        try:
            printIfInteractive(f"\rTesting HTTP get for {url}              ", end="")
            response = requests.get(url, timeout=1)
            hostname = "unknown"
            try:
                hostname = socket.gethostbyaddr(address)[0]
            except Exception as e:
                pass

                printIfInteractive(f"\rReceived response at {url}: {response.status_code} hostname: {hostname}")
            success = True
        except Exception as e:
            pass

    return success


# main program function
def main() :

    # log start up message
    logging.info("***************************************************************")
    logging.info("networkscan Data Collector has started")
    logging.info("Working directory is %s", os.getcwd())

    try:
        hostname = socket.gethostname()
        externalip = get('https://api.ipify.org').text
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        localipaddress = s.getsockname()[0]
        logging.info("Hostname is %s", hostname)
        logging.info("Local IP is %s and external IP is %s", localipaddress, externalip)

    except Exception as e:
        logging.exception("Exception occurred")
        logging.error("Unable to get network information")

        printIfInteractive("Scanning subnet " + baseAddress)

    # create an address list and then iterate through each address and probe for network services
    addresses = createAddressList()
    for address in addresses:
        testPing(address)
        testSSH(address)
        testHTTP(address)

        printIfInteractive("Scan complete!                                          ")



# set up the logger
logging.basicConfig(filename="/var/log/networkscan/networkscan.log", format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


if __name__ == '__main__':

    try:
        main()

    except Exception as e:
        logging.exception("Exception occurred in main")

    logging.info("networkscan Data Collector has terminated")






