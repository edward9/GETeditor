# Name: Edward Takahashi
#
# file description:
#    For GUI that is evoked by actionShare action
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

# for GUI
import ShareSubmitUI

class GroupItem(QListWidgetItem):
    """ class for item used by ShreSubmit. Overload from QListWidgetItem"""
    icon = QIcon()
    def __init__(self, group, view,):
        self.icon.addPixmap(QPixmap(":/icons/users32.png"), QIcon.Normal, QIcon.Off)
        super(GroupItem, self).__init__(self.icon, group.getName(),view)
        self.group = group
        
    def getGroup(self):
        return self.group

class ShareSubmit(QDialog, ShareSubmitUI.Ui_Dialog):
    """ Dialog for letting user select group to submit """
    def __init__(self, parent):
        super(ShareSubmit, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent
        for group in self.parent.peerGroups:
            GroupItem(group, self.listWidget)