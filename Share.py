# Name: Edward Takahashi
#
# file description:
#    Defines Peer classes, ChildPeer and ParentPeer, which encapsulates peer's information,
#    and provides useful method for communicating with peers.
#    Also defines Group classes, which encapsulates the data about group and
#    provides methods to manage a group
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")


import sys

# for debugging
from debug import debug


class BasePeer(object):
    """ base class for ChildPeer and ParentPeer class """
    # permission
    READANDWRITE = 0
    READONLY = 1
    def __init__(self, socket, address, username):
        self.socket = socket                # peer's socket
        self.ip = address[0]                # peer's IP address
        self.port = address[1]              # peer's port number
        self.username = username            # peer's username
        self.mainwin = None                 # main windows GUI
        self.group   = None                 # group which peer belongs
        self.tabs = []                      # tabs peer's sharing with
        self.permission = self.READANDWRITE # permission. default is Read and write
        
    ########################################################
    # Get methods      
        
    def isReadOnly(self):
        return self.permission == self.READONLY
    
    def isReadWrite(self):
        return self.permission == self.READANDWRITE
    
    def getAddress(self):
        return self.address
    
    def getPermission(self):
        if self.permission == self.READONLY:
            return "ReadOnly"
        return "Read/Write"
    
    def getUsername(self):
        return self.username
    
    def getType(self):
        return "Peer"
    
    def __str__(self):
        txt = "---------------------------------------\n"
        txt += "socket:\t%s\n" % str(self.socket)
        txt += "IP Addr:\t%s\n" % self.ip
        txt += "Port num:\t%d\n" % self.port
        txt += "Username:\t%s\n" % self.username
        txt += "Permission:\t%d\n" % self.permission
        return txt
    
    ########################################################
    # Set methods      
    
    def setMainWin(self, mainwin):
        self.mainwin = mainwin
        
    def setPermission(self, permission):
        """ set permission. if change was made, send PERMISSION message"""
        if permission == self.getPermission():
            return
        if permission == "ReadOnly":
            self.permission = self.READONLY
            self.sendPermission()
        else:
            self.permission = self.READANDWRITE
            self.sendPermission()
    
    ########################################################
    # methods used to communicate to peer 
        
    def send(self,text):
        debug("send: %s" % text)
        totalsent = 0
        length    = len(text)
        while totalsent < length:
            sent = self.socket.send((text[totalsent:]).encode("utf-8"))
            if sent == 0:
                # socket connection is broken
                # take off from belonged group
                debug("Socket Sent Error")
                return
            totalsent += sent

        
    def sendUpdate(self, tab, start, removed, added):
        if removed > 0:
            self.sendRemove(tab.getId(), str(start), str(removed))
        elif added > 0:
            cursor = QTextCursor(tab.plainTextEdit.document())
            cursor.setPosition(start)
            text = ""
            for i in range(added):
                text += tab.plainTextEdit.document().characterAt(start+i)
            self.sendInsert(tab.getId(), str(start), text)
            
            
    def sendRemove(self, id, start, length):
        self.send("REMOVE \@/%s\@/%s\@/%s\r\n" % (id, start, length))
            
    def sendInsert(self, id, start, text):
        self.send("INSERT \@/%s\@/%s\@/%s\r\n" % (id, start, text))
        
    def sendStopSync(self, id):
        self.send("STOPSYNC %s None\r\n" % id)
        
    def close(self):
        """ close connection with peer """
        debug("Peer closed")
        self.send("CLOSE %s %s\r\n" % (self.username, self.ip))
        self.socket.close()
        
        
class ParentPeer(BasePeer):
    """ Parent Peer class, used to interact with parent"""
    def __init__(self, socket, address):
        super(ParentPeer,self).__init__(socket,address,"parent")
        self.IdToTab = {} # map ID to Tab
    
       
    def addTab(self,tab,id):
        self.tabs.append(tab)
        self.IdToTab[id] = tab

    ########################################################
    # methods used to communicate with parent peer 
    
    def send(self,text):
        """ send text to parent peer"""
        debug("send: %s" % text)
        totalsent = 0
        length    = len(text)
        while totalsent < length:
            sent = self.socket.send((text[totalsent:]).encode("utf-8"))
            debug("sent: %d" % sent)
            if sent == 0:
                # socket connection is broken
                # take off from belonged group
                debug("Socket Sent Error")
                self__clean()
                return
            totalsent += sent
    
    def acceptOffer(self,file,path):
        """ send ACCEPT message """
        self.send("ACCEPT @%s@%s\r\n" % (file, path))
    
    def refuseOffer(self,file,path):
        """ send REFUSE message """
        self.send("REFUSE @%s@%s\r\n" % (file, path))
        
    def doneFiledata(self, id):
        """ send DONE message """
        self.send("DONE %s NONE\r\n" % id)
        
    def recvPermission(self, permission):
        """ change permission """
        if permission == "ReadOnly":
            self.permission = self.READONLY
            for tab in self.tabs:
                tab.plainTextEdit.setReadOnly(True)
        else:
            self.permission = self.READANDWRITE
            for tab in self.tabs:
                tab.plainTextEdit.setReadOnly(False)
    
    def recvStopSync(self,id):
        """ stop sync """
        if id in self.IdToTab:
            tab = self.IdToTab[id]
        if tab in self.tabs:
            tab.setSharingParent(None)
            tab.setSharedWithParent(False)        
            del self.IdToTab[tab.getId()]
            self.tabs.remove(tab)
            
    def recvClose(self):
        """ clean up to close socket"""
        self.__clean()
        
    ########################################################
    # helper function
    
    def __clean(self):
        """ helper funciton to clean up """
        for tab in self.tabs:
            tab.setSharedWithParent(False)
            tab.setSharingParent(None)
        self.socket.close()
    
    ########################################################
    # used for debugging
    def __str__(self):
        txt = super(ParentPeer, self).__str__()
        txt += "Tabs:\t%s\n" % self.tabs
            
    
           

class ChildPeer(BasePeer):
    """ Child Peer class, used to interact with child peer """
    def __init__(self, socket, address, username):
        super(ChildPeer,self).__init__(socket,address,username)
        self.group = None
        self.isSyncing = False
    
    ########################################################
    # methods used to communicate with child peer 
    
    def send(self,text):
        """ send text to child peer """
        debug("send: %s" % text)
        totalsent = 0
        length    = len(text)
        while totalsent < length:
            sent = self.socket.send((text[totalsent:]).encode("utf-8"))
            if sent == 0:
                # socket connection is broken
                # take off from belonged group
                debug("Socket Sent Error")
                if self.group != None:
                    self.__clean()
                return
            totalsent += sent
    
    def offerShare(self,tab):
        """ send OFFER message """
        self.send("OFFER @%s@%s\r\n" % (tab.getFilename(), tab.getId()))
        
    def sendFile(self, id):
        """ send a file contained in tab with 'id' """
        # find the target tab
        for tab in self.group.tabs.keys():
            if id == tab.getId():
                # send text in this tab
                line = "FILE "+ tab.getId() + " "
                text = tab.plainTextEdit.toPlainText() + "\r\n" 
                while True:
                    text = line + text
                    length = min( len(text),4094)
                    self.send(text[:length]+"\r\n")
                    if length == len(text):
                        return
                    text = text[4094:]
                return
            
    def stopSync(self):
        """ Send STOPSYNC message to this child peer, stop syncing"""
        if self.isSyncing != True:
            return
        for tab in self.group.tabs:
            if self in self.group.tabs[tab]:
                self.stopSyncTab(tab)
        self.isSyncing = False
        
    def stopSyncTab(self,tab):
        """ stop syncing this tab """
        if self.isSyncing != True:
            return
        self.sendStopSync(tab.getId())
        self.group.tabs[tab].remove(self)
        
    def recvStopSync(self, id):
        """ handle STOPSYNC message """
        for tab in self.group.tabs.keys():
            if id == tab.getId():
                self.group.tabs[tab].remove(self)
        
    def startSync(self):
        """ set isSyncing true """
        if self.group == None:
            return
        self.isSyncing = True
    
    def sendPermission(self):
        self.send("PERMISSION %s None\r\n" % self.getPermission())

    def close(self):
        debug("Peer closed")
        self.send("CLOSE %s %s\r\n" % (self.username, self.ip))
        self.__clean()
        self.socket.close()
    
    def recvClose(self):
        self.__clean()
        self.socket.close()
    
    ########################################################
    # Get methods 
    
    def getGroup(self):
        return self.group
    
    def getLabel(self):
        ret = [self.username,self.ip]
        if self.permission == self.READANDWRITE:
            ret.append("Read/Write")
        else:
            ret.append("ReadOnly")
        return ret    
    
    def __str__(self):
        txt = super(ChildPeer, self).__str__()
        if self.group == None:
            txt += "Group:\t%s\n" % self.group
        else:
            txt += "Group:\t%s\n" % self.group.getName()
        txt += "isSynced:\t%s\n" % str(self.isSyncing)
        return txt
    
    def isSynced(self):
        return self.isSyncing
    
    ########################################################
    # Set methods 
    
    def setGroup(self,group = None):
        """add this peer to group,
           if group is None, then take out this peer from self.group"""
        if group == self.group:
            # no need to change anything
            return
        elif self.group == None:
            group.addPeer(self)
            self.group = group
            self.mainwin.childPeersNotInGroup.remove(self)
            
        else:
            # this peer is removed from group
            if self.isSyncing:
                # if peer is already synced with other group,
                # then send a stop sync message
                self.stopSync()
            self.group.removePeer(self) 
            self.group = group
            if group == None:
                self.mainwin.childPeersNotInGroup.append(self)
            else:
                self.group.addPeer(self)
    
    
    ########################################################
    # helper funciton 
    
    def __clean(self):
        self.setGroup()
        self.mainwin.childPeersNotInGroup.remove(self)
        self.mainwin.childPeers.remove(self)
    
        
class Group():
    """ Group class, used to manage group """
    ALLREADONLY = False
    def __init__(self, name, peers = []):
        self.name = name
        self.peers = peers
        self.tabs = {}
        
    ########################################################
    # methods for managing group 
    def addPeer(self,peer):
        self.peers.append(peer)
        peer.startSync()
        
    def addPeers(self, peers):
        for peer in peers:
            self.addPeer(peer)
        
    def removePeer(self, peer):
        self.peers.remove(peer)
    
    def offerShareAll(self,tab):
        """ offer to share tab to all peers """
        for peer in self.peers:
            peer.offerShare(tab)            
    
    def removeSharedTab(self,tab):
        """ stop sync 'tab' with peers in a group"""
        if tab in self.tabs:
            for peer in self.tabs[tab]:
                peer.stopSyncTab(tab)
    
    def shareTab(self,tab):
        """ start sync 'tab' with peers """
        if tab in self.tabs:
            return
        self.tabs[tab] = []
        tab.setSharedWithChild(True)
        tab.addSharingGroups(self)
        self.offerShareAll(tab)
        
    def close(self):
        for peer in self.peers:
            peer.close()
        for tab in self.tabs:
            tab.removeShareingGroups(group)    
    
    ########################################################
    # get methods
    def getPeers(self):
        return self.peers
    
    def getLabel(self):
        return [self.name, "",""]
    
    def getType(self):
        return "Group"
    
    def getName(self):
        return self.name
    
    def __str__(self):
        txt = "===Group==========================\n"
        txt += "Name:\t%s\n" % self.name
        txt += "peers:\n"
        for peer in self.peers:
            txt += str(peer)
        txt += "Tabs:\t%s\n" % self.tabs
        return txt    
    
            
    
    
    
    