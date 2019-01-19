#!/usr/bin/python3.6

# python program to scan network and find HTTP servers, pingable servers, ssh accessible servers
# source code at https://github.com/andreaslbauer/networkscan/blob/master/networkscan.py
# Force Jenkins build

import requests
import socket
import os
import paramiko

# port list and base address to scan
portList = ["5000", "8080", "8081", "8088", "80", "8089"]
baseAddress = "192.168.0."

# create list of addresses on 192.168.0 subnet
def createAddressList() :
    addresses = []
    for i in range(1, 255):
        addresses.append(baseAddress + str(i))

    #addresses = ["192.168.0.100", "192.168.0.133"]

    return addresses

# attempt to ping an address
def testPing(address):
    print(f"\rPinging {address}                                             ", end="")

    # first try to ping the address
    pingResponse = os.system("ping -c 2 -w 3 " + address + " > /dev/null 2>&1")
    if pingResponse == 0:
        hostname = "unknown"
        try:
            hostname = socket.gethostbyaddr(address)[0]
        except Exception as e:
            pass

        print(f"\rPing response from {address} hostname {hostname}: {pingResponse}")

# attempt ssh connection
def testSSH(address):
    print(f"\rTesting ssh for {address}                  ", end="")

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


        print(f"\rssh response at {address}: \n{outputStr} \n{errorStr}")

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
            print(f"\rTesting HTTP get for {url}              ", end="")
            response = requests.get(url, timeout=1)
            hostname = "unknown"
            try:
                hostname = socket.gethostbyaddr(address)[0]
            except Exception as e:
                pass

            print(f"\rReceived response at {url}: {response.status_code} hostname: {hostname}")
            success = True
        except Exception as e:
            pass

    return success


# main program function
def main() :
    print("Scanning subnet " + baseAddress)

    # create an address list and then iterate through each address and probe for network services
    addresses = createAddressList()
    for address in addresses:
        testPing(address)
        testSSH(address)
        testHTTP(address)


    print("Scan complete!                                          ")

# run the main function
main()






