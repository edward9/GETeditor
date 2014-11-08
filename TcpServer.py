# Name: Edward Takahashi
#
# file description:
#    provides code for TCP server which handles REQUEST message,
#    handshake, and TCP connection with child peer(client)
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

import socket, select, sys, errno, threading

# for peer objects
import Share

# for debugging
from debug import debug

def _eintrRetry(func, *args):
    """restart a system call interrupted by EINTR"""
    while True:
        try:
            return func(*args)
        except (OSError, select.error) as e:
            if e.args[0] != errno.EINTR:
                raise

class ThreadServer(QThread):
    """ thread for TCP server """
    timeout = None
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    daemon_threads = False
    poll_interval=0.5
    allow_reuse_address = False
    
    # signals
    requestArrival = Signal(tuple)
    
    def __init__(self, parent, server_address):
        super(ThreadServer, self).__init__()
        
        self.parent = parent
        self.server_address = server_address
        self.__isShutdown = threading.Event()
        self.__shutdownRequest = False
        
        self.socket = socket.socket(self.address_family,self.socket_type)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()
        self.socket.listen(self.request_queue_size)

    def run(self):
        """ called by start() """
        self.__isShutdown.clear()
        try:
            while not self.__shutdownRequest:
                r, w, e = _eintrRetry(select.select, [self], [], [], self.poll_interval)
                if self in r:
                    self._handleRequestNoblock()
        finally:
            self.__shutdownRequest = False
            self.__isShutdown.set()
            
    def fileno(self):
        return self.socket.fileno()
    
    def close(self):
        self.socket.close()
        
    def getRequest(self):
        return self.socket.accept()
    
    def shutdown(self):
        """Stops the loop in run()"""
        self.__shutdownRequest = True
        self.__isShutdown.wait()

    def handleRequest(self):
        """ Handle REQUEST """
        # Support people who used socket.settimeout() to escape
        # handle_request before self.timeout was available.
        timeout = self.socket.gettimeout()
        if timeout == None:
            timeout = self.timeout
        elif self.timeout != None:
            timeout = min(timeout, self.timeout)
        fd_sets = _eintr_retry(select.select, [self], [], [], timeout)
        
        if fd_sets[0]:
            self._handleRequestNoblock()

    def _handleRequestNoblock(self):
        try:
            request, client_address = self.getRequest()
        except socket.error:
            return

        try:
            self.processRequest(request, client_address)
        except:
            self.shutdownRequest(request)

    def processRequest(self, request, client_address):
        """ let main thread finish processing REQUEST"""
        self.requestArrival.emit((request,client_address,self))
        

    def shutdownRequest(self, request):
        """Called to shutdown and close an individual request."""
        try:
            request.shutdown(socket.SHUT_WR)
        except socket.error:
            pass 
        self.closeRequest(request)

    def closeRequest(self, request):
        """Called to clean up an individual request."""
        request.close()

    

class RequestHanderThread(QThread):
    connectionEstablished = Signal(tuple)
    recvFromChild = Signal(tuple)
    sendFile      = Signal(tuple)
    handleDone     = Signal(tuple)
    removeCharsParent = Signal(tuple)
    insertCharsParent = Signal(tuple)
    handleStopSync    = Signal(tuple)
    
    
    REQUESTLENGTH = 3
    peer = None
    def __init__(self, parent, request, client_address, server):
        super(RequestHanderThread,self).__init__(parent)
        self.parent = parent
        self.request = request
        self.client_address = client_address
        self.server = server
        
        # used for closing thread safely
        self.__isShutdown = threading.Event()
        self.__shutdownRequest = False
        
    def handleRequest(self):
        """ Handle REQUEST message, complete handshaking """
        success_flag = False
        response = None
        data = self.request.recv(128)
        data = data.split()
        if len(data) == self.REQUESTLENGTH and data[0] == "Request":
            self.parent.shareSettingLock.lock()

            if self.parent.acceptShare == False:
                response = "NO %s ParentNotSharing\r\n" % self.parent.ip
                
            elif data[2] == "None" and self.parent.password  == None:
                success_flag = True
            elif data[2] == self.parent.password:
                success_flag = True
            else:
                response = "NO %s WrongPassword\r\n" % self.parent.ip
            
            self.parent.shareSettingLock.unlock()    
            
        else:
            response = "NO %s BadFormat\r\n" % self.parent.ip
        
        if success_flag:
            self.request.sendall("OK %s None\r\n" % self.parent.ip)
            self.peer = Share.ChildPeer(self.request,self.client_address, data[1])
            self.connectionEstablished.emit((self.peer,))
        else:
            self.request.sendall(response)
       
    def run(self):
        """ accept message, until shutdown() is called """
        self.__isShutdown.clear()
        if self.peer == None:
            return
        data = ""
        try:
            self.request.settimeout(0.1)
            while not self.__shutdownRequest:
                try:
                    new_data = self.request.recv(4096)
                except:
                    continue
                new_data = new_data.decode('utf-8')
                ## debugging statement ################
                cur_thread = threading.current_thread()
                response = "{}: {}".format(cur_thread.name, new_data)
                debug("parent: %s" % response)
                ######################################
                if new_data == "":
                    debug("child: connection is broken")
                    break
                data += new_data
                
                # "\r\n" indicates the end of one message
                eof = data.find("\r\n")
                while eof >= 0:
                    if data[eof+2:eof+4] == "\r\n":
                        eof +=2
                    self.processData(data[:eof])
                    data = data[eof+2:]
                    eof = data.find("\r\n")
        finally:
            self.__shutdownRequest = False
            self.__isShutdown.set()
        
        self.server.shutdownRequest(self.request)
        
    def processData(self,data):
        """ process a message """
        if data.find(" ") <= 0:
            return
        keyword = data[:data.find(" ")]
        
        if keyword == "ACCEPT":
            # this is ACCEPT message
            offer = data.split("@")
            if len(offer) != 3:
                # never make here
                return
            self.sendFile.emit((self.peer, offer[2]))
            
        if keyword == "REFUSE":
            # this is REFUSE message
            pass
        
        if keyword == "DONE":
            # this is DONE message
            data = data.split()
            self.handleDone.emit((self.peer, data[1]))
            
        if keyword == "STOPSYNC":
            # this is STOPSYNC message
            data = data.split()
            self.handleStopSync.emit((self.peer, data[1], data[2]))
        
        if keyword == "REMOVE":
            # this is REMOVE message
            data = data.split("\@/")
            if len(data) == 4:
                self.removeCharsParent.emit((self.peer, data[1], data[2], data[3]))
            
        if keyword == "INSERT":
            # this is INSERT message
            data = data.split("\@/")
            if len(data) == 4:
                self.insertCharsParent.emit((self.peer, data[1], data[2], data[3]))
                
        if keyword == "CLOSE":
            # this is CLOSE message
            self.peer.recvClose()
            self.__shutdownRequest = True
                
    def shutdown(self):
        """Stops the loop in run()"""
        self.__shutdownRequest = True
        self.__isShutdown.wait()

        
        
        
