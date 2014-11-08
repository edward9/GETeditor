# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'share_setting.ui'
#
# Created: Mon Apr 29 03:19:44 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class PasswordLine(QtGui.QLineEdit):
    def __init__(self, parent=None):
        super(PasswordLine,self).__init__(parent)
        self.__mousePress = False

    def setup(self,text):
        if text != None:
            self.setEchoMode(QtGui.QLineEdit.Password)
            self.setText(text)
        else:
            self.setText("set a password")
        self.__mousePress = False        
    
    def focusInEvent(self, e):
        super(PasswordLine, self).focusInEvent(e)
        self.selectAll()
        self.setEchoMode(QtGui.QLineEdit.Password)
        self.__mousePress = True
        
    def mousePressEvent(self, e):
        super(PasswordLine, self).mousePressEvent(e)
        if self.__mousePress:
            self.selectAll()
            self.__mousePress = False


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(298, 208)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ipText = QtGui.QLabel(Dialog)
        self.ipText.setObjectName("ipText")
        self.verticalLayout.addWidget(self.ipText)
        self.portText = QtGui.QLabel(Dialog)
        self.portText.setObjectName("portText")
        self.verticalLayout.addWidget(self.portText)
        self.no_share_button = QtGui.QRadioButton(Dialog)
        self.no_share_button.setObjectName("no_share_button")
        self.verticalLayout.addWidget(self.no_share_button)
        self.share_button = QtGui.QRadioButton(Dialog)
        self.share_button.setObjectName("share_button")
        self.verticalLayout.addWidget(self.share_button)
        self.share_pass_button = QtGui.QRadioButton(Dialog)
        self.share_pass_button.setObjectName("share_pass_button")
        self.verticalLayout.addWidget(self.share_pass_button)
        self.password = PasswordLine(Dialog)
        self.password.setEnabled(False)
        self.password.setMaxLength(32)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName("password")
        self.verticalLayout.addWidget(self.password)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Share setting", None, QtGui.QApplication.UnicodeUTF8))
        self.ipText.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.portText.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.no_share_button.setText(QtGui.QApplication.translate("Dialog", "Don\'t share files", None, QtGui.QApplication.UnicodeUTF8))
        self.share_button.setText(QtGui.QApplication.translate("Dialog", "Share files without password", None, QtGui.QApplication.UnicodeUTF8))
        self.share_pass_button.setText(QtGui.QApplication.translate("Dialog", "Share files with password", None, QtGui.QApplication.UnicodeUTF8))

