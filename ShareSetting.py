try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

import ShareSettingUI



class ShareSetting(QDialog, ShareSettingUI.Ui_Dialog):
    def __init__(self, parent=None, accept_share=None, password=None):
        super(ShareSetting, self).__init__(parent)
        self.setupUi(self)
        self.ipText.setText(  "Your IP Address: %s" % parent.ip)
        self.portText.setText("Your port number: %d" % parent.port)
        if accept_share == True:
            if password == None:
                self.share_button.toggle()
            else:
                self.share_pass_button.toggle()
                self.password.setEnabled(True)
        else:
            self.no_share_button.toggle()
        
        self.password.setup(password)        
        
        self.share_pass_button.toggled.connect(self.EnablePassword)
        
        
    def EnablePassword(self, clicked):
        if clicked == True:
            self.password.setEnabled(True)
        else:
            self.password.setEnabled(False)
            
            