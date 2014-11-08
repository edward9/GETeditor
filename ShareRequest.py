# Name: Edward Takahashi
#
# file description:
#    This file provides a dialog GUI used for requesting file share.
#    Also provides code for thread which submit REQUEST message, handshake,
#    and connection between parent peer(host)

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

import sys ,socket, threading

# for debugging
from debug import debug

# for GUI
import ShareRequestUI

# for peer/group Object
import Share

class ShareRequest(QDialog, ShareRequestUI.Ui_Dialog):
    """ Dialog for requesting share """
    def __init__(self, parent=None, accept_share=None, password=None):
        super(ShareRequest, self).__init__(parent)
        self.setupUi(self)
        
    def getParentInfo(self):
        """ return string of typed IP address and port """ 
        return self.parentip.text(), int(self.parentport.text())
    
    def getParentPassword(self):
        """ return string of typed password """ 
        return self.parentpassword.text()
    
    def getUsername(self):
        """ return typed username """
        return self.username.text()
    
    def requestMessage(self):
        """ generate REQUEST message """
        msg = "Request " + self.username.text()
        password = self.getParentPassword()
        if password == "":
            password = "None"
        return msg + " " + password
        
class sendRequestThread(QThread):
    """ Thread used to TCP connection to Parent Peer (host) """
    
    # signals to communicate main thread
    socketFail        = Signal(tuple)
    connectionFail    = Signal(tuple)
    connectionSucceed = Signal(tuple)
    offerArrival      = Signal(tuple)
    handleFiledata    = Signal(tuple)
    handlePermission  = Signal(tuple)
    handleStopSync    = Signal(tuple)
    removeChars       = Signal(tuple)
    insertChars       = Signal(tuple)
    
    def __init__(self,req):
        super(sendRequestThread, self).__init__()
        self.request = req    # socket requested
        self.peer    = None   # peer object
        
        # used for shutdown from the loop in run()
        self.__isShutdown = threading.Event()
        self.__shutdownRequest = False
        
    def run(self):
        """ called by start(), deal with handshake, then keep TCP connection """ 
        self.__isShutdown.clear()
        ip, port = self.request.getParentInfo()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            self.socketFail.emit((ip,port))
            return
        try:
            sock.settimeout(10)
            sock.connect((ip,port))
        except:
            # connection fail
            sock.close()
            self.connectionFail.emit((ip,port,"Cannot connect"))
            return
        try:
            sock.sendall(self.request.requestMessage())
            response = sock.recv(1024)
            debug("Received: {}".format(response))
        except:
            # received no response for 10 seconds
            sock.close()
            self.connectionFail.emit((ip,port,"No response from parent"))
            return
        
        try:
            response_list = response.split()
            if len(response_list) == 3 and response_list[0] == "NO":
                self.connectionFail.emit((ip,port,response_list[2]))
                return
            elif len(response_list) ==3 and response_list[0] != "OK":
                self.connectionFail.emit((ip,port,"Error occurred in Parent's side"))
                return
            elif len(response_list) !=3:
                self.connectionFail.emit((ip,port,"Error occurred in Parent's side"))
                return
            
            # connection is successfully established
            # create a peer object and send it to mainWin
            self.peer = Share.ParentPeer(sock,(ip,port))
            self.connectionSucceed.emit((ip,port,self.peer))
            
            data = ""
            try:
                sock.settimeout(0.1)
                while not self.__shutdownRequest:
                    try:
                        new_data = sock.recv(4096)
                    except:
                        continue
                    new_data = new_data.decode("utf-8")
                    debug("child recv: %s" % new_data)
                    if new_data == "":
                        debug("child: connection is broken")
                        break
                    data += new_data
                    
                    # parse by "\r\n" which indicates end of one message
                    eof = data.find("\r\n")
                    while eof >= 0:
                        if data[eof+2:eof+4] == "\r\n":
                            eof +=2
                        # process the message
                        self.processData(data[:eof])
                        data = data[eof+2:]
                        eof = data.find("\r\n")
            finally:
                self.__shutdownRequest = False
                self.__isShutdown.set()
        finally:
            try:
                sock.close()
            except:
                pass
            
    def processData(self,data):
        """ process a message """
        if data.find(" ") <= 0:
            return
        keyword = data[:data.find(" ")] # first word of the message
        
        if keyword == "OFFER":
            # this is OFEER message
            offer = data.split("@")
            if len(offer) != 3:
                # never make here
                return
            self.offerArrival.emit((self.peer, offer[1], offer[2]))
            
        if keyword == "FILE":
            # this is FILE message
            try:
                data = data[data.find(" ")+1:]
                first_space = data.find(" ")
                id = data[:first_space]
                text = data[first_space+1:]
                self.handleFiledata.emit((self.peer, id, text))
                
            except Exception as e:
                debug(e)
        if keyword == "PERMISSION":
            # this is PERMISSION message
            data = data.split()
            self.handlePermission.emit((self.peer, data[1]))
        
        if keyword == "STOPSYNC":
            # this is STOPSYNC message
            data = data.split()
            self.handleStopSync.emit((self.peer, data[1], data[2]))
                
        if keyword == "REMOVE":
            # this is REMOVE message
            data = data.split("\@/")
            if len(data) == 4:
                self.removeChars.emit((self.peer, data[1], data[2], data[3]))
            
        if keyword == "INSERT":
            # this is INSERT message
            data = data.split("\@/")
            if len(data) == 4:
                self.insertChars.emit((self.peer, data[1], data[2], data[3]))
                
        if keyword == "CLOSE":
            # this is CLOSE message
            self.peer.recvClose()
            self.__shutdownRequest = True
    
    def shutdown(self):
        """Stops the loop in run()"""
        self.__shutdownRequest = True
        self.__isShutdown.wait()
