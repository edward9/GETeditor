# Name: Edward Takahashi
#
# file description:
#    provides GUI for close confirmation
#

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")


class Close_Confirm(QMessageBox):
    """ MessageBox GUI ask for confirmation to close """
    def __init__(self, parent = None):
        super(Close_Confirm, self).__init__(parent)
        
        self.setText("This file has been modified.")
        self.setInformativeText("Do you want to save your changes?")
        self.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        self.setDefaultButton(QMessageBox.Save)
        self.setIcon(QMessageBox.Warning)

        
