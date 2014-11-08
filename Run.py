import subprocess
from PySide import QtCore, QtGui

from RunUI import *

class Run_Confirm(QtGui.QDialog, Ui_Dialog_Confirm):
    """ Dialog GUI which ask to save unsaved file before Run command """ 
    def __init__(self, parent=None):
        super(Run_Confirm, self).__init__(parent)
        self.setupUi(self)
        self.unsaved_list = []
        
        self.pushButton.clicked.connect(self.SelectAllAct)
        self.pushButton_2.clicked.connect(self.DeselectAllAct)
        
    def setup(self, tabWidget):
        not_empty = False
        for i in range(tabWidget.count()):
            tab = tabWidget.widget(i)
            if not tab.isSaved() and tab.isPythonMode():
                self.unsaved_list.append(tab)
                item = QtGui.QListWidgetItem(tab.getFilename(), self.listWidget, QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Checked)
                not_empty = True
        return not_empty        
                 
    def SelectAllAct(self):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(QtCore.Qt.Checked)
            
    def DeselectAllAct(self):
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)
            
    def checkedTab(self):
        tabs = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                tabs.append(self.unsaved_list[i])
        
        return tabs
    
    
class Run_Output(QtGui.QDialog, Ui_Dialog_Output):
    """ Dialog GUI displays output of run """
    def __init__(self, parent=None):
        super(Run_Output, self).__init__(parent)
        self.setupUi(self)
        
    def setup(self, command):
        self.setWindowTitle("Output- "+ command[1])
        firstline = ">" + " ".join(command) + "\n"
        self.textBrowser.setPlainText(firstline)
        
    def update(self, output):
        self.textBrowser.append(output)

class Run_Argument(QtGui.QLineEdit):
    """ textline located in toolbar for passing an argument for run command"""
    def __init__(self, parent=None):
        super(Run_Argument,self).__init__(parent)
        self.__mousePress = False

    def setup(self,text="Type some arguments here"):
        self.setText(text)
        self.__mousePress = False        
    
    def focusInEvent(self, e):
        super(Run_Argument, self).focusInEvent(e)
        self.selectAll()
        self.__mousePress = True
        
    def mousePressEvent(self, e):
        super(Run_Argument, self).mousePressEvent(e)
        if self.__mousePress:
            self.selectAll()
            self.__mousePress = False

class Run_Process(QtCore.QThread):
    """ Thread runs python program """
    updateOutput = QtCore.Signal(str)
    def __init__(self, command, parent = None):
        super(Run_Process, self).__init__(parent)
        self.command = command

    def run(self):
        proc   = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = proc.communicate()[0]
        self.updateOutput.emit(stdout)
               
    

           