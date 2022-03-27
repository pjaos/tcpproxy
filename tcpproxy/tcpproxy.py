#!/usr/bin/env python3

import os
import sys
import argparse
import socket

from   time import sleep, time
from   subprocess import Popen, PIPE
from   threading import Thread

from   p3lib.uio import UIO
from   p3lib.helper import logTraceBack, getHomePath, saveDict, getDict
from   p3lib.boot_manager import BootManager

class ProxyConfig(object):
    """@brief Responsible for managing the persistent proxy configuration."""
    
    CONFIG_FILE = os.path.join( getHomePath(), ".tcpproxy.cfg" )
    BIND_ALL_ADDRESS = "0.0.0.0/32"
    
    def __init__(self, uio):
        """@brief Constructor
           @param uio A UIO instance handling user input and output (E.G stdin/stdout or a GUI)."""
        self._uio = uio
        try:
            self._singleProxyList = getDict(ProxyConfig.CONFIG_FILE, jsonFmt=True)
        except:
            self._singleProxyList = []

    def _debug(self, msg):
        self._uio.debug(msg)

    def _info(self, msg):
        self._uio.info(msg)

    def _error(self, msg):
        self._uio.error(msg)

    def _isDebugEnabled(self):
        """@brief Determinme if debugging is enabled.
           @return True if debugging is enabled."""
        return self._uio.isDebugEnabled()

    def runCmd(self, cmd):
        """@brief Run a system command.
           @param The command to execute.
           @return A tuple containing
                   0: return code
                   1: A list of stdout lines of text
                   2: A list of stderr lines of text"""
        self._debug("cmd: {}".format(cmd))
        if not isinstance(cmd, list):
            cmd = cmd.split()
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        stdOutLines = out.decode("utf-8").split("\n")
        stdErrLines = err.decode("utf-8").split("\n")
        if self._isDebugEnabled():
            for l in stdOutLines:
                self._debug("stdout: {}".format(l))
            for l in stdErrLines:
                self._debug("stderr: {}".format(l))
        return (proc.returncode, stdOutLines, stdErrLines)

    def _getNetAddrList(self):
        """@brief Get the list of network interface addresses on the computer.
           @return A list of network interface addresses on the local computer.
                   Each IP address will include /subnet mask size."""
        cmd = "/sbin/ip a"
        rc, lines, _ = self.runCmd(cmd)
        if rc:
            raise Exception("{} command returned an error.".format(cmd))
        interfaceList = []
        for line in lines:
            line=line.strip()
            elems = line.split()
            if len(elems) > 0 and elems[0] == 'inet':
                if len(elems) > 1:
                    interfaceList.append(elems[1])

        interfaceList.append(ProxyConfig.BIND_ALL_ADDRESS)
        return interfaceList

    def _showProxyDict(self):
        """@brief Display the configured proxy connections."""
        col0Title = "ID"
        col1Title = "Bind Address"
        col2Title = "Listen Port"
        col3Title = "Destination Address"
        col4Title = "Destination Port"
        titleHeaderLine = "| {: <3} | {: <12} | {: <11} | {: <19} | {: <16} |".format(col0Title, col1Title, col2Title, col3Title, col4Title)
        horSepLine = "*"*len(titleHeaderLine)
        self._info(horSepLine)
        self._info(titleHeaderLine)
        self._info(horSepLine)
        
        id = 1
        for attrList in self._singleProxyList:
            rowLine = "| {: <3} | {: <12} | {: <11} | {: <19} | {: <16} !".format(id, attrList[0], attrList[1], attrList[2], attrList[3])
            self._info(rowLine)
            id = id + 1
            
        self._info(horSepLine)

    def _getAddress(self, prompt, defaultAddress):
        """@brief Allow the user to enter an address.
           @param prompt The user prompt.
           @param defaultAddress The address to return if the user just presses the Enter key.
           @return The address."""
        response = self._uio.getInput(prompt)
        response = response.lower()
        if response == 'q':
            return None
        
        elif len(response) == 0:
            return defaultAddress
        
        else:
            return response
                       
    def _getLocalBindAddress(self, defaultAddress=BIND_ALL_ADDRESS):
        """@brief Get the local interface IP to bind to.
           @param defaultAddress The default IP address."""
        localBindAddress = None
        while True:
            netAddrList = self._getNetAddrList()
            self._uio.info("Local network interface address list")
            for netAddr in netAddrList:
                self._uio.info(netAddr)
            self._info("Press enter to set the local bind address to {}".format(defaultAddress))
            response = self._getAddress("Enter the local network interface address to bind to from the above list or 'q' to quit.", defaultAddress=defaultAddress)
            if response is None:
                return None

            elif response in netAddrList:
                localBindAddress = response
                break

            else:
                self._uio.error("{} is not a local interface address.".format(response))

        return localBindAddress

    def _getPort(self, prompt, defaultPort=None):
        """@brief Get a port number.
           @param prompt The prompt to present to the user.
           @param defaultPort The port to select if the user does not enter a port."""
        port = -1
        while True:
            response = self._uio.getInput(prompt)
            if len(response) == 0 and defaultPort != None:
                port = defaultPort
                break
            else:
                
                try:
                    port = int(response)
                    break
                except ValueError:
                    self._error("{} is an invalid port (1-65535 are valid).".format(response))

        return port

    def _addProxy(self):
        """@brief Add to the proxy configuration."""
        localBindAddress = self._getLocalBindAddress()
        listenPort = self._getPort("Enter the local listen port")
        destAddr = self._uio.getInput("Enter the destination address")
        destPort = self._getPort("Enter the destination port")
        attrList = (localBindAddress, listenPort, destAddr, destPort)
        self._singleProxyList.append(attrList)
       
    def _editProxy(self):
        """@brief Edit to the proxy configuration."""
        id = self._uio.getIntInput("Enter the ID of the row to edit")
        if id > 0 and id <= len(self._singleProxyList):
            row = self._singleProxyList[id-1]
            bindAddress = row[0]
            listenPort = row[1]
            destAddress = row[2]
            destPort = row[3]
            bindAddress = self._getLocalBindAddress(defaultAddress=bindAddress)
                       
            listenPort = self._getPort("Enter the local listen port (Enter={})".format(listenPort), defaultPort=listenPort)
            self._getAddress("Enter the destination address (Enter={})".format(destAddress), defaultAddress=destAddress )
            destPort = self._getPort("Enter the destination port (Enter={})".format(destPort), defaultPort=destPort)
            self._singleProxyList[id-1] = [bindAddress, listenPort, destAddress, destPort]

    def _deleteProxy(self):
        """@brief Delete to the proxy configuration."""
        id = self._uio.getIntInput("Enter the ID of the row to delete")
        if id > 0 and id <= len(self._singleProxyList):
            del self._singleProxyList[id-1 ]
            self._info("Removed row {}".format(id))

    def _save(self):
        """@brief Save the config to the default config file."""
        saveDict(self._singleProxyList, ProxyConfig.CONFIG_FILE, jsonFmt=True)
        self._info("Saved configuration.")
        
    def getProxyAttrList(self):
        """@return A list of elements, each of which defines a list of attributes for a single proxy server."""
        return self._singleProxyList

    def config(self):
        """@brief Allow user to change the persistent proxy configuration."""
        while True:
            self._showProxyDict()
            response = self._uio.getInput("A: Add, E: Edit, D: Delete, S: Save or Q: to quit.")
            response = response.lower()
            if response == 'a':
                self._addProxy()

            elif response == 'e':
                self._editProxy()

            elif response == 'd':
                self._deleteProxy()

            elif response == 's':
                self._save()

            elif response == 'q':
                break

class TCPProxyServer(Thread):

    def set(self, uio, attrList, backLog=5):
        """@brief Constructor.
           @param attrList  A list of the attributes
                  0 = The bind address
                  1 = The port to listen on
                  2 = The destintaion address
                  3 = The destination port.
           @param backLog The number of client connections to handle simultainiously."""
        self._uio = uio
        self._attrList = attrList
        self._bindAddress = self._attrList[0]
        if self._bindAddress.find("/") > 0:
            self._bindAddress = self._bindAddress.split("/")[0]
        self._listenPort  = self._attrList[1]
        self._destAddress = self._attrList[2]
        if self._destAddress.find("/") > 0:
            self._destAddress = self._destAddress.split("/")[0]
        self._destPort    = self._attrList[3]        
        self._running = False
        self._backLog = backLog

    def _debug(self, msg):
        self._uio.debug(msg)

    def _info(self, msg):
        self._uio.info(msg)

    def _error(self, msg):
        self._uio.error(msg)
    
    def shutDown(self):
        """@brief Shutdown the server."""
        self._running = False

    def run(self):
        self.serveConnection()
        
    def serveConnection(self):
        self._running = True        
        listenPort=self._attrList[1]
        self._debug("Started server: Listen on TCP/IP port {}:{} and forward to {}:{}".format(self._bindAddress, self._listenPort, self._destAddress, self._destPort) )
        try:
          try:
            dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            dock_socket.bind((self._bindAddress, self._listenPort))
            while self._running:
              dock_socket.listen(self._backLog)
              while self._running:
                  client_socket = dock_socket.accept()[0]
                  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                  self._handle_socket(client_socket, server_socket)

          except:
            self._uio.errorException()
            #If we can't connect to the host or the connection dies wait a while
            #rather than spinning as fast as possible.
            sleep(0.25)
        finally:
          self._debug("Shutdown server listening on {}:{}".format(self._bindAddress, self._listenPort) )

    def _handle_socket(self, client_socket, server_socket):
      server_socket.connect((self._destAddress, self._destPort))
      threadA = Thread(target=self._forward, args=(client_socket, server_socket))
      threadA.start()

      threadB = Thread(target=self._forward, args=(server_socket, client_socket))
      threadB.start()
     
      self._info("Connected {}:{} to {}:{}".format(self._bindAddress, self._listenPort, self._destAddress, self._destPort))
      
    def _forward(self, source, destination, rxBufferSize=65536):
        """@brief Forward the source socket data to the destination socket.
           @param source Src socket.
           @param destination Destination socket."""
        data = None
        try:
            while self._running:
              data = source.recv(rxBufferSize)
              if data:
                  destination.sendall(data)
        except:
            self._info("Disconnected")

class TCPProxy(object):

    def __init__(self, uio, options):
        """@brief Constructor
           @param uio A UIO instance handling user input and output (E.G stdin/stdout or a GUI)
           @param options An instance of the OptionParser command line options."""
        self._uio = uio
        self._options = options
        self._proxyConfig = ProxyConfig(uio)

    def serve(self):
        """@brief Server all TCP connections."""
        proxyAttrList = self._proxyConfig.getProxyAttrList()
        for singleProxyAttr in proxyAttrList:
            self._uio.info("Forwarding {}:{} to {}:{}".format(singleProxyAttr[0],
                                                              singleProxyAttr[1],
                                                              singleProxyAttr[2],
                                                              singleProxyAttr[3]))
            tcpProxyServer = TCPProxyServer()
            tcpProxyServer.set(self._uio, singleProxyAttr)
            tcpProxyServer.start()
        # We rely on the TCP threads not being daemon threads to keep running as the main thread will exit from here
            
    def config(self):
        """@brief Allow user to change the persistent proxy configuration."""
        self._proxyConfig.config()

    def enableAutoStart(self):
        """@brief Enable this program to auto start when the computer on which it is installed starts."""
        bootManager = BootManager()
        if not self._options.user:
            raise Exception("--user not set.")

        argString = ""
        if self._options.debug:
            argString = argString + " --debug"

        bootManager.add(user=self._options.user, argString=argString, enableSyslog=True)
        self._uio.info("Enabled auto start")
        
    def disableAutoStart(self):
        """@brief Enable this program to auto start when the computer on which it is installed starts."""
        bootManager = BootManager()
        bootManager.remove()
        self._uio.info("Disabled auto start")

    def checkAutoStartStatus(self):
        """@brief Check the status of a process previously set to auto start."""
        bootManager = BootManager()
        lines = bootManager.getStatus()
        if lines and len(lines) > 0:
            for line in lines:
                self._uio.info(line)
                
def main():
    """@brief Program entry point"""
    uio = UIO()

    try:
        parser = argparse.ArgumentParser(description="This program provides a simple proxy server.\n",
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-c", "--config",             help="Configure the TCP proxy server.", action='store_true')
        parser.add_argument("-u", "--user",               help="Set the user for auto start.")
        parser.add_argument("-e", "--enable_auto_start",  help="Enable auto start this program when this computer starts.", action="store_true", default=False)
        parser.add_argument("-d", "--disable_auto_start", help="Disable auto start this program when this computer starts.", action="store_true", default=False)
        parser.add_argument("-s", "--check_status",       help="Check the status of an auto started tcpproxy instance.", action="store_true", default=False)
        parser.add_argument("--debug",                    help="Enable debugging.", action='store_true')

        options = parser.parse_args()

        uio.enableDebug(options.debug)
        tcpProxy = TCPProxy(uio, options)

        if options.config:
            tcpProxy.config()

        elif options.enable_auto_start:
            tcpProxy.enableAutoStart()

        elif options.disable_auto_start:
            tcpProxy.disableAutoStart()

        elif options.check_status:
            tcpProxy.checkAutoStartStatus()
            
        else:
            tcpProxy.serve()

    #If the program throws a system exit exception
    except SystemExit:
        pass
    #Don't print error information if CTRL C pressed
    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logTraceBack(uio)

        if options.debug:
            raise
        else:
            uio.error(str(ex))

if __name__== '__main__':
    main()
