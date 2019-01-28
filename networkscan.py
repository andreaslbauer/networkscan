#!/usr/bin/python3.6

# python program to scan network and find HTTP servers, pingable servers, ssh accessible servers
# source code at https://github.com/andreaslbauer/networkscan/blob/master/networkscan.py
# Force Jenkins build

import requests
import os
import paramiko
import socket
from requests import get
import datetime

# logging facility: https://realpython.com/python-logging/
import logging

# for couch db
import pycouchdb

# port list and base address to scan
portList = ["5000", "8080", "8081", "8088", "80", "8089", "8100", "5984"]
baseAddress = ["192.168.0.", "192.168.1."]
interactive = None

# our couch DB access
couchDBServerUrl = "http://192.168.0.150:5984/"
couchDBServer = None
couchDB = None

# read ssh username and password from file
sshUsername = ""
sshPassword = ""

def readSSHUsernamePassword() :
    file = open("username.txt", "r")
    line = file.readline()
    splitLine = line.split()
    global sshUsername
    sshUsername = splitLine[0]
    global sshPassword
    sshPassword = splitLine[1]


# print but only if interactive flag is "on"
def printIfInteractive (*args, **kwargs):
    if interactive:
        print(*args, **kwargs)

# create list of addresses on 192.168.0 subnet
def createAddressList() :
    addresses = []
    for base in baseAddress:
        for i in range(1, 255):
            addresses.append(base + str(i))

    #addresses = ["192.168.0.100", "192.168.0.133", "192.168.0.1", "192.168.0.150", "127.0.0.1"]

    return addresses

# clsas networkProber to check network properties for an address and record findings in class data members
class networkProber :

    # constructor; it initializes all data members per passed parameters
    def __init__ (self, ipAddress):
        self.ipAddress = ipAddress
        self._id = ipAddress
        self.pingResponseString = ""
        self.hostname = ""
        self.hostFound = None

    # attempt to ping an address
    def testPing(self):
        address = self.ipAddress
        printIfInteractive(f"\rPinging {address}                                             ", end="")

        # first try to ping the address
        pingResponse = os.system("ping -c 2 -w 3 " + address + " > /dev/null 2>&1")
        self.pingResponseString = pingResponse
        if pingResponse == 0:
            hostname = "unknown"
            try:
                hostname = socket.gethostbyaddr(address)[0]
                self.hostname = hostname

            except Exception as e:
                pass

            finally:
                printIfInteractive(f"\rPing response from {address} hostname {hostname}: {pingResponse}")
                #logging.info("Hostname is %s", hostname)
                logging.info(f"Ping response from {address} hostname {hostname}: {pingResponse}")
                self.hostFound = 1

    def sendCmdssh(self, ipAddress, username, password, cmd):

        sshResponse = ""

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=ipAddress, username=username, password=password)
            stdin, stdout, stderr = client.exec_command(cmd)

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

            printIfInteractive(f"\rssh response at {ipAddress} for command {cmd}: \n{outputStr} \n{cmd}")
            sshResponse = outputStr

        except Exception as e:
            pass

        try:
            client.close()

        except Exception as e:
            pass

        return sshResponse


    # attempt ssh connection
    def testSSH(self):
        address = self.ipAddress
        printIfInteractive(f"\rTesting ssh for {address}                  ", end="")

        username = sshUsername
        password = sshPassword

        self.sshResponse_uname = self.sendCmdssh(address, username, password, "uname -a")
        self.sshResponse_uptime = self.sendCmdssh(address, username, password, "uptime")
        self.sshResponse_ps_docker = self.sendCmdssh(address, username, password, "ps -elf | grep docker | grep -v grep")
        self.sshResponse_ps_motion = self.sendCmdssh(address, username, password, "ps -elf | grep motion | grep -v grep")
        self.sshResponse_docker_ps = self.sendCmdssh(address, username, password, "docker ps")
        self.sshResponse_df = self.sendCmdssh(address, username, password, "df -h")
        self.memTotal = self.sendCmdssh(address, username, password, "cat /proc/meminfo | grep MemTotal")


    # test address for HTTP responses
    def testHTTP(self):
        address = self.ipAddress

        success = False
        ports = []

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
                self.hostFound = 1
                ports.append(str(port))
            except Exception as e:
                pass

        self.httpPorts = ports
        return success

    def probe(self):
        self.testPing()
        self.testSSH()
        self.testHTTP()

        now = datetime.datetime.now()
        nowDateTime = str(now)
        self.lastUpdated = nowDateTime
        self.firstSeen = nowDateTime

        if self.hostFound :
            # if couch DB instance is initialized save the document
            if (couchDB != None) :
                try:
                    doc = None
                    try:
                        doc = couchDB.get(self.ipAddress)
                        self._rev = doc["_rev"]
                        self.firstSeen = doc['firstSeen']
                    except:
                        pass

                except pycouchdb.exceptions.Conflict as e:
                    pass

                doc = couchDB.save(self.__dict__)
                logging.info("Stored record %s", doc)

    def toJSON(self):
        return self.__dict__


# main program function
def main() :

    # log start up message
    logging.info("***************************************************************")
    logging.info("networkscan Data Collector has started")
    logging.info("Working directory is %s", os.getcwd())

    couchDBServer = pycouchdb.Server(couchDBServerUrl)
    logging.info("CouchDB Server is %s", couchDBServerUrl)
    logging.info("CouchDB Server version is %s", couchDBServer.info()['version'])

    # initialize global variable couch DB
    global couchDB
    couchDB = couchDBServer.database("networkscan")

    readSSHUsernamePassword()

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
        prober = networkProber(address)
        prober.probe()

    printIfInteractive("Scan complete!                                          ")



# set up the logger
logging.basicConfig(filename="/var/log/networkscan/networkscan.log", format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


if __name__ == '__main__':

    #try:
    main()

    #except Exception as e:
        #logging.exception("Exception occurred in main")

    logging.info("networkscan Data Collector has terminated")






