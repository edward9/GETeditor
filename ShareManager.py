# Name: Edward Takahashi
#
# file description:
#    Provides GUI for managing child peers
#
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

# for GUI
import ShareManagerUI

# for peer obj
import Share

class MyTreeWidgetItem(QTreeWidgetItem):
    """ item object used for ShareManager GUI"""
    def __init__(self, parent, labels, networkobj = None):
        super(MyTreeWidgetItem, self).__init__(parent, labels)
        self.networkobj = networkobj
    def getType(self):
        if self.networkobj == None:
            return "None"
        return self.networkobj.getType()
    def getNetworkObj(self):
        return self.networkobj
    

class ShareManager(QDialog, ShareManagerUI.Ui_ShareManager):
    """ GUI dialog for managing peers """
    new_group_counter = 1
    FLAG_BASE  = Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
    FLAG_PEER  = FLAG_BASE | Qt.ItemIsDragEnabled
    FLAG_GROUP =  FLAG_BASE | Qt.ItemIsEditable | Qt.ItemIsDropEnabled

    def __init__(self, parent=None):
        super(ShareManager, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        
        # add peers and groups for Tree View Widget
        for group in self.parent.peerGroups:
            item = MyTreeWidgetItem(self.tree, group.getLabel(),group)
            # show indicator as expandable
            item.setChildIndicatorPolicy(MyTreeWidgetItem.ShowIndicator)
            # group should be editable, dragenabled, dropenabled.
            item.setFlags(self.FLAG_GROUP)
            
            for peer in group.getPeers():
                child = MyTreeWidgetItem(item,peer.getLabel(),peer)                
                child.setFlags(self.FLAG_PEER)
            
        for peer in self.parent.childPeersNotInGroup:
            item = MyTreeWidgetItem(self.tree,peer.getLabel(),peer)
            item.setFlags(self.FLAG_PEER)

        # data
        self.removeditems = []
        
        # signals
        self.newgroupBottun.clicked.connect(self.newgroupAct)
        self.readonlyBottun.clicked.connect(self.readonlyAct)
        self.readwriteBottun.clicked.connect(self.readwriteAct)
        self.removeBottun.clicked.connect(self.removeAct)
        
    def newgroupAct(self):
        new_group = MyTreeWidgetItem(self.tree, ["Group"+ str(ShareManager.new_group_counter),"",""])
        ShareManager.new_group_counter += 1
        new_group.setChildIndicatorPolicy(MyTreeWidgetItem.ShowIndicator)
        new_group.setFlags(self.FLAG_GROUP)
        self.tree.addTopLevelItem(new_group)
        
    def readonlyAct(self):
        for item in self.tree.selectedItems():
            if item.getType() == "Peer":
                item.setText(2,"ReadOnly")
            
    def readwriteAct(self):
        for item in self.tree.selectedItems():
            if item.getType() == "Peer":
                item.setText(2,"Read/Write")
            
    def removeAct(self):
        root = self.tree.invisibleRootItem()
        for item in self.tree.selectedItems():
            if item.parent() == None or not self.tree.isItemSelected(item.parent()):
                self.removeditems.append(item)
            (item.parent() or root).removeChild(item)
            
    def getRemovedItems(self):
        return self.removeditems
    
    
        
        