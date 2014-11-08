# Name: Edward Takahashi
#
# file description:
#    provide MyTab class which inherits QWidget. This tab GUI widget is a container for MyEditor class.
#    Also MyTab class manages peers sharing the content of MyEditor and send update to other peers.
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")
import SyntaxHighlighter
import Editor
import random

class MyTab(QWidget):
    """  This tab GUI widget is a container for MyEditor class.
         manages peers sharing the content of MyEditor and send update to other peers. """
    counter = 0
    
    # signals
    filenameChanged = Signal(QWidget)
    modStateChanged = Signal(QWidget)
    
    def __init__(self, parent=None):
        super(MyTab, self).__init__(parent)
        
        MyTab.counter += 1
        self.setObjectName("tab"+ self.strCounter())
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plainTextEdit = Editor.MyEditor(self)

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        
        self.horizontalLayout.addWidget(self.plainTextEdit)
        
        # other data setup
        self.syntaxHighlighter = SyntaxHighlighter.PythonSH(self)
        self.flagSaved         = True   # true if the content of editor is saved
        self.filepath          = None   # contains filepath of editor. None if not saved in any filesystem 
        self.filename          = None   # name of file
        self.filetype          = None   # type of file (.py or None)
        # used for run action
        self.runArgument       = "Type some arguments here" 
        self.runCheck          = Qt.Unchecked   
        self.run_thread        = None
        self.output            = None
        
        # used to manage peers sharing this tab
        self.sharedWithChild   = False  # sharing this tab with others as parent
        self.sharingGroups     = []     # list of Group obj sharing 
        self.sharedWithParent  = False  # this tab is shared from parent
        self.sharingParent     = None   # ParentPeer obj who shared this tab
        
        # used to identify tab among mutiple users
        self.id                = str(random.random())
        
        # connecting signal
        self.plainTextEdit.modificationChanged.connect(self.setUnsaved)        
        self.test = True
        self.plainTextEdit.document().contentsChange.connect(self.ContentChange)
    
    
    
        
    ########################################################
    # Method for communication between peers 
    
    def ContentChange(self, start, removed, added):
        """ send messages to peers what changed in the content """
        if self.sharedWithChild:
            for group in self.sharingGroups:
                for peer in group.tabs[self]:
                    peer.sendUpdate(self,start,removed,added)
            
        
    def removeChars(self, start, length):
        """ remove 'length' letters from cursor point start """
        cursor = QTextCursor(self.plainTextEdit.document())
        cursor.setPosition(start)
        for i in range(length):
            self.ignore_flag = True
            cursor.deleteChar()
            
            
    def insertText(self, start, text):
        """ insert text from cursor point start """
        cursor = QTextCursor(self.plainTextEdit.document())
        cursor.setPosition(start)
        self.ignore_flag = True
        cursor.insertText(text)
        
    def addSharingGroups(self, group):
        """ append group to sharingGroups """
        self.sharingGroups.append(group)
        
    def removeShareingGroups(self, group):
        """ remove group from sharingGroups """
        self.sharingGroups.remove(group)
        if self.sharingGroups == []:
            self.sharedWithChild = False
    
    def close(self):
        """ When closing a tab, we need to let host/client know to stop sync """
        for group in self.sharingGroups:
            # for the group shared
            group.removeSharedTab(self)
        if self.sharingParent != None:
            # for the parent sharing this tab
            self.sharingParent.sendStopSync(self.id)
        super(MyTab, self).close()   
    
    ########################################################
    # Get methods      
        
    def strCounter(self):
        return str(MyTab.counter)
    
    def isSaved(self):
        return self.flagSaved
    
    def isPythonMode(self):
        if self.filetype == "py":
            return True
        return False
    
    def isSharedWithParent(self):
        return self.sharedWithParent
    
    def getId(self):
        return str(self.id)
    
    def getPath(self):
        return self.filepath
    
    def getFilename(self):
        return self.filename

    def getRunArg(self):
        return self.runArgument
        
    def getRunCheck(self):
        return self.runCheck
        
    ########################################################
    # Set methods      
    
    def setRunArg(self, text):
        self.runArgument = text
        
    def setRunCheck(self, state):
        self.runCheck    = state
        
    def setId(self, id):
        self.id = str(id)
    
    def setPath(self,path):
        self.filetype = path[path.rfind('.')+1:]    
        self.filepath = path
        if self.isPythonMode():
            self.syntaxHighlighter.setDocument(self.plainTextEdit.document())
        else:
            self.syntaxHighlighter.setDocument(None)
        self.setFilename(self._pathTofilename(path))
        
    def setFilename(self, name):
        self.filename = name
        self.filenameChanged.emit(self)
    
    def setUnsaved(self, modified = True):
        if modified:
            self.flagSaved = False
            self.modStateChanged.emit(self)
        else:
            self.setSaved()
    
    def setSaved(self):
        self.flagSaved = True
        self.plainTextEdit.document().setModified(False)
        self.modStateChanged.emit(self)
    
    def setSharedWithChild(self, y):
        self.sharedWithChild = y
        
    def setSharedWithParent(self, y):
        if y:
            self.plainTextEdit.setUndoRedoEnabled(False)
            self.plainTextEdit.setAcceptDrops(False)
        else:
            self.plainTextEdit.setUndoRedoEnabled(True)
            self.plainTextEdit.setAcceptDrops(True)
        self.sharedWithParent = y
    
    def setSharingParent(self, parent):
        self.sharingParent = parent
    
    
    ########################################################
    # Helper methods  
    def _pathTofilename(self, path):
        return path[path.rfind('/')+1:]