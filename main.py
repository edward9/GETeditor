# Name: Edward Takahashi
#
# file description:
#     This is a main file, containing codes for main GUI thread
#

import sys, socket

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

# for Gui
import MainWindow
import Close
import Tab
import Run
import ShareSetting, ShareRequest, ShareManager, ShareSubmit

# for peer/group Object
import Share

# for TCP server
import TcpServer

# for debugging
from debug import debug


__appname__ = "GETeditor"


class MainWin(QMainWindow, MainWindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)

        # data structure  ################################################
        self.new_count   = 0            # used to make a title for a new tab
        self.font        = self.font()  # font of this window
        self.acceptShare = False        # True if accept a share request
        self.password    = None         # None if no password is set
        
        # data for threading 
        self.tcpParentThreads = []      # used to avoid garbage collection
        self.tcpChildThreads  = []      # used to avoid garbage collection 
        
        # Network setting ################################################
        HOST, PORT = "", 0 # an arbitrary unused port
        
        # start up TCP server
        self.serverThread = TcpServer.ThreadServer(self, (HOST, PORT))
        self.serverThread.requestArrival.connect(self.ShareRequestArrival)
        self.serverThread.start()
        debug("Server loop running in thread: %s" % str(self.serverThread) )
        
        # obtain own public IP address
        ip, port = self.serverThread.server_address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 80))
        self.ip = s.getsockname()[0]
        self.port = port
        debug("IP: %s, port: %d" % (self.ip, self.port))
        
        # Network Construction ##########################################
        self.shareSettingLock     = QMutex()    # used for setting password and acceptShare
        self.childPeers           = []          # list of all child peers accepted
        self.childPeersNotInGroup = []          # list of child peers not in group
        self.peerGroups           = []          # list of groups created
        self.parentPeers          = []          # list of parent peers connected
        
        self.TabOnProcess         = {}          # used by FILE message,
                                                # keep track tabs on process of receiving file
        
        # Some other initialization #####################################
        self.NewAct()    # open a new tab
         
        # Signal connection #############################################
        # buttons 
        self.actionNew.triggered.connect(self.NewAct)
        self.actionOpen.triggered.connect(self.OpenAct)
        self.actionSave.triggered.connect(self.SaveAct)
        self.actionSave_As.triggered.connect(self.SaveAsAct)
        self.actionClose.triggered.connect(self.CloseAct)
        self.actionRedo.triggered.connect(self.RedoAct)
        self.actionUndo.triggered.connect(self.UndoAct)
        self.actionRun.triggered.connect(self.RunAct)        
        self.actionZoom_In.triggered.connect(self.ZoomInAct) 
        self.actionZoom_Out.triggered.connect(self.ZoomOutAct)
        self.actionShare.triggered.connect(self.ShareThisTab)
        self.actionRequestShare.triggered.connect(self.RequestShareAct)
        self.actionShareSetting.triggered.connect(self.ShareSettingAct)
        self.actionShareManager.triggered.connect(self.ShareManagerAct)
        
        # other signals
        self.tabWidget.tabCloseRequested.connect(self.TabCloseAct)
        self.tabWidget.currentChanged.connect(self.TabChange)
        self.runArguments.textChanged.connect(self.RunArgChanged)
        self.runCheck.stateChanged.connect(self.RunCheckChanged)
        
    ########################################################
    # Overloaded Event 
        
    def closeEvent(self, event):
        """ overload close event. Make sure to close every tab safely """
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(0)
            self.tabWidget.setCurrentWidget(tab)
            self._safeClose(tab)
            
        if self.tabWidget.count() > 0:
            event.ignore()
            
        # make sure to close all threads
        self.serverThread.shutdown()
        for thread in self.tcpParentThreads:
            thread.shutdown()
        for thread in self.tcpChildThreads:
            thread.shutdown()

            
    ########################################################
    # actions 
    # - methods used some bottun in toolbar/menubar is clicked
    
    def NewAct(self, isNew = True):
        """ Add a new tab to tabWidget.
            isNew is true if this tab was produced by New command """
        
        # Initialize a tab and add itd
        new_tab = Tab.MyTab(self)
        # set up signal for the new tab
        new_tab.filenameChanged.connect(self.ChangeTabTitle)
        new_tab.modStateChanged.connect(self.ModTabTitle)
        self.tabWidget.addTab(new_tab, "")

        if isNew:
            # if the new tab was made by New command,
            # title of the tab should be untitled text 
            self.new_count += 1
            new_tab.setFilename("Untitled Text " + str(self.new_count))
        
        # set the new tab to current tab, focus on its editing area 
        self.tabWidget.setCurrentWidget(new_tab)
        self.runArguments.setup(new_tab.getRunArg())
        new_tab.plainTextEdit.setFocus()
        return new_tab
    
    def OpenAct(self):
        """ Called when actionOpen was triggered.
            If a chosen file is not yet open, create a new tab and open in it,
            If the file is already open, set focus on the tab """
        dir = "."
        try:
            # Open a file dialog 
            fileObj  = QFileDialog.getOpenFileName(self, __appname__ + " Open File Dialog", dir=dir)
            filepath = fileObj[0]
            file     = open(filepath, "r")
            read     = file.read()
            file.close()
        except:
            # if user closed the file dialog without choosing a file, do nothing 
            return
        
        # check if the file is already Open
        tab = self._filepathToTab(filepath)
        if tab != None:
            # if it is already opened, then set focus on the tab
            self.tabWidget.setCurrentWidget(tab)
            tab.plainTextEdit.setFocus()
        else:
            # if not yet opened, open a new tab
            cur_tab =  self.tabWidget.currentWidget()
            
            if (cur_tab.isSaved() == False) or (cur_tab.getPath() != None):
                # Open a new tab and read otherwise
                cur_tab = self.NewAct(False)
                
            # update data member in tab
            cur_tab.setPath(filepath)
            cur_tab.setSaved()
            
            # update text editor window
            cur_tab.plainTextEdit.setPlainText(read)
        
    def SaveAct(self):
        """ save a file associated with the current tab. If the filepath of the tab is unknown, call SaveAsAct() """
        cur_tab =  self.tabWidget.currentWidget()
        if cur_tab.getPath() == None:
            # ask the file path for this tab by SaveAsAct()
            self.SaveAsAct()
        else:
            # get all text from editing area, then save.
            contents = cur_tab.plainTextEdit.toPlainText()        
            open(cur_tab.getPath(), mode="w").write(contents)
            cur_tab.setSaved()
            
    def SaveAsAct(self):
        """ save a file which is not associated with file path """
        dir = "."
        try:
            cur_tab =  self.tabWidget.currentWidget()
            fileobj = QFileDialog.getSaveFileName(self, __appname__, dir=dir)
            if fileobj[0] == '':
                raise NameError
            cur_tab.setPath(fileobj[0])
            
            # Once its file path is obtained, SaveAct() will take care the rest
            self.SaveAct()
        except:
            # If user closed the file dialog, then do nothing
            pass
        
    def CloseAct(self):
        """ close a current tab """
        self._safeClose(self.tabWidget.currentWidget())
                
    def RedoAct(self):
        """ Redo in the current file """
        cur_tab = self.tabWidget.currentWidget()
        cur_tab.plainTextEdit.redo()
    
    def UndoAct(self):
        """ Redo in the current file """
        cur_tab = self.tabWidget.currentWidget()
        cur_tab.plainTextEdit.undo()
        
    def RunAct(self):
        """ run .py file. If it is unsaved,then ask for save """
        cur_tab = self.tabWidget.currentWidget()
        
        if not cur_tab.isPythonMode():
            # this file is not .py file, give a warning and return
            QMessageBox.warning(self,__appname__, "Run is only valid for .py file.", QMessageBox.Ok)
        
        else:
            # Confirm to save all modified files before run
            confirm = Run.Run_Confirm()
            if confirm.setup(self.tabWidget):
                if confirm.exec_():
                    # save checked files
                    list = confirm.checkedTab()
                    for cur_tab in list:
                        contents = cur_tab.plainTextEdit.toPlainText()        
                        open(cur_tab.getPath(), mode="w").write(contents)
                        cur_tab.setSaved()
                else:
                    # cancel was pressed, return
                    return
                    
            # Run this file in new thread
            command = ['python', cur_tab.getPath()]
            if cur_tab.getRunCheck() == Qt.Checked:
                command.extend([cur_tab.getRunArg()])
            
            
            
            if cur_tab.run_thread == None:
                cur_tab.run_thread = Run.Run_Process(command,cur_tab)
            else:
                # give warning and ask if user want to terminate the thread
                ret = QMessageBox.question(self, "Another process is running", 
                                                "We need to close a currently running process before run another one. Do you want to continue?", 
                                                QMessageBox.Ok | QMessageBox.Cancel)
                if ret:
                    #cur_tab.run_thread.terminate()
                    cur_tab.run_thread = Run.Run_Process(command,cur_tab)
                else:
                    return
                    #Another process is 
            cur_tab.output = Run.Run_Output(self)
            cur_tab.output.setup(command)
            cur_tab.run_thread.updateOutput.connect(cur_tab.output.update)
            cur_tab.output.show()
            cur_tab.output.raise_()
            cur_tab.output.activateWindow()            
            cur_tab.run_thread.start()            
            
    def ZoomInAct(self):
        """ increment a fontsize """
        self.font.setPointSize(self.font.pointSize()+1)
        cur_tab = self.tabWidget.currentWidget()
        cur_tab.plainTextEdit.setFont(self.font)
        
    def ZoomOutAct(self):
        """ Decrement a fontsize """
        fontsize = self.font.pointSize()
        if fontsize<=1:
            return
        self.font.setPointSize(self.font.pointSize()-1)
        cur_tab = self.tabWidget.currentWidget()
        cur_tab.plainTextEdit.setFont(self.font)
    
    def ShareThisTab(self):
        """ Share this tab with selected group"""
        # Open a new dialog to let user select a group to share
        submit = ShareSubmit.ShareSubmit(self)
        if submit.exec_():
            for groupItem in submit.listWidget.selectedItems():
                # this group is selected, share a current tab with this group
                cur_tab = self.tabWidget.currentWidget()
                group = groupItem.getGroup()
                group.shareTab(cur_tab)

    def RequestShareAct(self):
        """ Send a REQUEST message in a new thread, try to establish a TCP connection with parent(host) """
        # Open a dialog askes IP addr/port/password of the parent
        request = ShareRequest.ShareRequest(self)
        if request.exec_():
            # create a new thread for a new TCP connection
            new_thread = ShareRequest.sendRequestThread(request)
            
            # record the new thread so that python won't garbage collect 
            self.tcpParentThreads.append(new_thread)
            
            # connect signals
            new_thread.socketFail.connect(self.FailRequestSocket)
            new_thread.connectionFail.connect(self.FailRequestConnection)
            new_thread.connectionSucceed.connect(self.SuccessRequest)
            new_thread.offerArrival.connect(self.HandleOffer)
            new_thread.handleFiledata.connect(self.HandleFiledata)
            new_thread.handlePermission.connect(self.HandlePermission)
            new_thread.handleStopSync.connect(self.HandleStopSyncFromParent)
            new_thread.removeChars.connect(self.RemoveCharsFromParent)
            new_thread.insertChars.connect(self.InsertCharsFromParent)
            new_thread.start()

    def ShareSettingAct(self):
        """ Open a setting window for sharing policy"""
        setting = ShareSetting.ShareSetting(self,self.acceptShare, self.password)
        if setting.exec_():
            self.shareSettingLock.lock()
            if setting.no_share_button.isChecked():
                # user does not share
                self.acceptShare = False
                self.password    = None
            elif setting.share_button.isChecked():
                # user accept child peer without password
                self.acceptShare = True
                self.password    = None
            else:
                # user accept child peer with password
                self.acceptShare = True
                self.password     = setting.password.text()
            self.shareSettingLock.unlock()
    
    def ShareManagerAct(self):
        """ Open a Share Manager to let user manage one's network """
        # open a manager dialog
        manager = ShareManager.ShareManager(self)
        if manager.exec_():
            for i in range(manager.tree.topLevelItemCount()):
                item = manager.tree.topLevelItem(i)
                if item.getType() == "Group":
                # item is a group
                
                    # for child peer in this group,
                    for j in range(item.childCount()):
                        # check if there is any new peer
                        child = item.child(j)
                        peer = child.getNetworkObj()
                        cur_group =  item.getNetworkObj()
                        peer.setGroup(cur_group)
                        
                        # Change permission if change was made
                        peer.setPermission(child.text(2))
                            
                            
                elif item.getType() == "Peer":
                    peer =  item.getNetworkObj()
                    
                    # set group of peer to None
                    peer.setGroup()
                    # Change permission if change was made
                    peer.setPermission(item.text(2))

                    
                else:
                    # this is a new group
                    new_group = Share.Group(item.text(0))
                    for j in range(item.childCount()):
                        peer = item.child(j).getNetworkObj()
                        peer.setGroup(new_group)
                        
                    self.peerGroups.append(new_group)
            for item in manager.removeditems:
                if item.getType() == "Peer":
                    # this child peer is removed
                    peer =  item.getNetworkObj()
                    peer.close()
                elif item.getType() == "Group":
                    # this group is removed
                    group = item.getNetworkObj()
                    # close all peers in the group
                    self.peerGroups.remove(group)
                    group.close()
        
        # debug statement
        debug("----------------------------------------------")
        debug("----Share-------------------------------------")
        debug("childPeers:")
        for peer in self.childPeers:
            debug(peer)
        debug("childPeersNotInGroup:")
        for peer in self.childPeersNotInGroup:
            debug(peer)
        debug("peerGroups:")
        for group in self.peerGroups:
            debug(group) 
        debug("----------------------------------------------")
        debug("----------------------------------------------")
    
    ########################################################
    # methods called by signal from Tab Widget
    #
    def ChangeTabTitle(self, tab):
        """ called when file name for the tab is changed """
        self.tabWidget.setTabText(self.tabWidget.indexOf(tab), tab.filename)
        
    def TabChange(self, index):
        """ Called when tab is switched. Update some information on GUI"""
        # If there is no tab, then ignore.  
        if index < 0:
            return
        cur_tab = self.tabWidget.currentWidget()
        # Update fonts
        cur_tab.plainTextEdit.setFont(self.font)        
        # Update arguments text box and checkbox for Run command
        self.runArguments.setup(cur_tab.getRunArg())
        self.runCheck.setCheckState(cur_tab.getRunCheck())
        # disable some actions if necessary
        if cur_tab.isSharedWithParent():
            self.actionUndo.setEnabled(False)
            self.actionRedo.setEnabled(False)
        else:
            self.actionUndo.setEnabled(True)
            self.actionRedo.setEnabled(True)
    
    def TabCloseAct(self,index):
        """ close a tab of index. This is called by signal tabCloseRequested """
        self._safeClose(self.tabWidget.widget(index))
        
    def RunArgChanged(self,arg):
        """ Save updated arguments in current tab object """
        self.tabWidget.currentWidget().setRunArg(arg)
    
    def RunCheckChanged(self,index):
        """ Save changed state of checkbox in current tab object """
        self.tabWidget.currentWidget().setRunCheck(self.runCheck.checkState())
        
    def ModTabTitle(self, tab):
        """ add '*' to indicate if the tab has been modified """
        if tab.isSaved():
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab), tab.filename)
        else:
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab), "*"+tab.filename)
    
    ########################################################
    # methods called by signal from Parent Peer (Host)
    #
    def FailRequestSocket(self, parentinfo):
        """ deliver connection fail message to user """
        text = "Fail to create a socket: %s, %d" % (parentinfo[0],parentinfo[1]) 
        QMessageBox.critical(self,"Socket Fail", text)
    
    def FailRequestConnection(self, parentinfo):
        """ deliver connection fail message to user """
        text = "Fail to connect with %s, port %d.\n" % (parentinfo[0],parentinfo[1])
        text += "Error Message: %s\n" % parentinfo[2]
        QMessageBox.critical(self,"Connection Fail", text)
    
    def SuccessRequest(self, parentinfo):
        """ deliver connection established message to user """
        parentinfo[2].setMainWin(self)
        self.parentPeers.append(parentinfo[2])
        text = "Your request is accepted: %s, %d." % (parentinfo[0],parentinfo[1]) 
        QMessageBox.information(self, "Request Accepted", text, QMessageBox.Ok)
        
    def HandleOffer(self, data):
        """ Handle OFFER message from parent """
        # ask user in a dialog whether accept the offer or not
        ret = QMessageBox.question(self, "Sharing Offer", 
                                        "Parent offer to share %s.\nDo you accept?" % data[1],
                                         QMessageBox.Yes, QMessageBox.No)
        if ret == QMessageBox.Yes:
            # if yes, send ACCEPT message to parent
            data[0].acceptOffer(data[1],data[2])
        else:
            # otherwise, send REFUSE message to parent
            data[0].refuseOffer(data[1],data[2])

    def HandleFiledata(self,data):
        """ Handle FILE message,
            if is possible that this data is only a part of file """
        peer = data[0]
        id   = data[1]
        text = data[2]
        
        if id in self.TabOnProcess:
            # if id in self.TabOnProcess, this is not first FILE message
            if text[-2:] == '\r\n':
                # "\r\n" suggests EOF
                self.TabOnProcess[id].plainTextEdit.appendPlainText(text[:-2])
                peer.doneFiledata(id)
                peer.addTab(self.TabOnProcess[id], id)
                self.TabOnProcess[id].setSharedWithParent(True)
                self.TabOnProcess[id].setSharingParent(peer)
                del self.TabOnProcess[id]

            else:
                self.TabOnProcess[id].plainTextEdit.appendPlainText(text)
        
        else:
            # open a new tab and sync its ID
            new_tab = self.NewAct()
            self.actionUndo.setDisabled(True)
            self.actionRedo.setDisabled(True)
            new_tab.setId(id)
            if peer.isReadOnly():
                new_tab.plainTextEdit.setReadOnly(True)
            
            if text[-2:] == "\r\n":
                # finished receiving a file, start sync
                new_tab.plainTextEdit.setPlainText(text[:-2])
                peer.doneFiledata(id)
                peer.addTab(new_tab, id)
                new_tab.setSharedWithParent(True)
                new_tab.setSharingParent(peer)
                
            else:
                # this FILE message does not contain file fully
                new_tab.plainTextEdit.setPlainText(text)
                self.TabOnProcess[id] = new_tab
                
    def HandlePermission(self, data):
        """ Handle Permission message from parent """
        peer       = data[0]
        permission = data[1]
        peer.recvPermission(permission)
            
    def HandleStopSyncFromParent(self, data):
        """ Handle STOPSYNC message from parent """
        peer = data[0]
        id   = data[1]
        peer.recvStopSync(id)
        
    def RemoveCharsFromParent(self, data):
        """ Handle REMOVE message from parent """
        peer   = data[0]
        id     = data[1]
        start  = data[2]
        length = data[3]
        
        tab = peer.IdToTab[id]
        tab.removeChars(int(start),int(length))
            
    def InsertCharsFromParent(self,data):
        """ Handle INSERT message from parent """
        peer   = data[0]
        id     = data[1]
        start  = data[2]
        text   = data[3]
        tab = peer.IdToTab[id]
        tab.insertText(int(start),text)
            
    ########################################################
    # methods called by signal from TCP server
    #                
    def ShareRequestArrival(self, info):
        """ Handle a REQUEST message arrived """
        new_thread = TcpServer.RequestHanderThread(self, info[0], info[1], info[2])
        self.tcpChildThreads.append(new_thread)
        
        # connect signals
        new_thread.connectionEstablished.connect(self.addChildPeer)
        new_thread.handleDone.connect(self.HandleDone)
        new_thread.sendFile.connect(self.sendFilePeer)
        new_thread.removeCharsParent.connect(self.RemoveCharsFromChild)
        new_thread.insertCharsParent.connect(self.InsertCharsFromChild)
        new_thread.handleStopSync.connect(self.HandleStopSyncFromChild)
        
        # process request
        new_thread.handleRequest()
        new_thread.start()

    
    ########################################################
    # methods called by signal from child peer(RequestHanderThread)
    #   
    
    def addChildPeer(self,info):
        """ record a newly connected child peer """
        info[0].setMainWin(self)
        self.childPeersNotInGroup.append(info[0])
        self.childPeers.append(info[0])
    
    def HandleDone(self, data):
        """ Handle DONE message """
        peer = data[0]
        id   = data[1]
        for tab in peer.group.tabs.keys():
            if id == tab.getId():
                # this tab is now shared with child peers 
                peer.group.tabs[tab].append(peer)
                peer.startSync()
                
    def sendFilePeer(self, data):
        """ send FILE message, where data[0] is peer and data[1] is tab to share"""
        data[0].sendFile(data[1])    
    
    def RemoveCharsFromChild(self, data):
        """ Handle REMOVE message from child peer (client) """
        peer   = data[0]
        id     = data[1]
        start  = data[2]
        length = data[3]
        
        for tab in peer.group.tabs.keys():
            if id == tab.getId():    
                tab.removeChars(int(start),int(length))
                for q in peer.group.tabs[tab]:
                    if peer != q:
                        q.sendRemove(id, start, length)
                return
        
    def InsertCharsFromChild(self, data):
        """ Handle INSERT message from child peer (client) """
        peer   = data[0]
        id     = data[1]
        start  = data[2]
        text   = data[3]
        for tab in peer.group.tabs.keys():
            if id == tab.getId():
                tab.insertText(int(start),text)
                for q in peer.group.tabs[tab]:
                    if peer != q:
                        q.sendInsert(id, start, text)
                return
            
    def HandleStopSyncFromChild(self, data):
        """ Handle STOPSYNC message from Children """
        peer = data[0]
        id   = data[1]
        peer.recvStopSync(id)
   
   
    ########################################################
    # Helper functions
    #      
    def _filepathToTab(self, filepath):
        """ helper function to obtain a tab from filepath """
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)
            if tab.getPath() == filepath:
                return tab
        return None
            
    def _safeClose(self,tab):
        """ Helper function which make sure if the tab is saved before closing it.
            If it is unsaved, then ask user for a decision """
        if tab.isSaved() == False:
            confirm = Close.Close_Confirm()
            ret = confirm.exec_()
            if ret == QMessageBox.Save:
                self.SaveAct()
            elif ret == QMessageBox.Discard:
                
                tab.close()
                self.tabWidget.removeTab(self.tabWidget.indexOf(tab))
                if self.tabWidget.count() <= 0:
                    self.close()
        else:
            tab.close()
            self.tabWidget.removeTab(self.tabWidget.indexOf(tab))
            if self.tabWidget.count() <= 0:
                self.close()


if __name__ == "__main__":
    

    mainApp = QApplication(sys.argv)
    mainWin = MainWin()
    mainWin.show()
    mainApp.exec_()

        




