# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'share_request.ui'
#
# Created: Sat Apr 27 16:05:53 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class IpLine(QtGui.QLineEdit):
    def __init__(self, parent=None):
        super(IpLine,self).__init__(parent)
        self.__mousePress = False

    def focusInEvent(self, e):
        super(IpLine, self).focusInEvent(e)
        self.home(False)
        self.__mousePress = True
        
    def mousePressEvent(self, e):
        super(IpLine, self).mousePressEvent(e)
        if self.__mousePress:
            self.home(False)
            self.__mousePress = False


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(359, 226)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.parentpasswordLabel = QtGui.QLabel(Dialog)
        self.parentpasswordLabel.setObjectName("parentpasswordLabel")
        self.gridLayout.addWidget(self.parentpasswordLabel, 3, 0, 1, 1)
        self.usernameLabel = QtGui.QLabel(Dialog)
        self.usernameLabel.setObjectName("usernameLabel")
        self.gridLayout.addWidget(self.usernameLabel, 0, 0, 1, 1)
        self.parentport = QtGui.QSpinBox(Dialog)
        self.parentport.setMaximum(65535)
        self.parentport.setObjectName("parentport")
        self.gridLayout.addWidget(self.parentport, 2, 1, 1, 3)
        self.parentportLabel = QtGui.QLabel(Dialog)
        self.parentportLabel.setObjectName("parentportLabel")
        self.gridLayout.addWidget(self.parentportLabel, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.parentpassword = QtGui.QLineEdit(Dialog)
        self.parentpassword.setMaxLength(32)
        self.parentpassword.setObjectName("parentpassword")
        self.gridLayout.addWidget(self.parentpassword, 3, 1, 1, 3)
        self.parentipLabel = QtGui.QLabel(Dialog)
        self.parentipLabel.setObjectName("parentipLabel")
        self.gridLayout.addWidget(self.parentipLabel, 1, 0, 1, 1)
        self.username = QtGui.QLineEdit(Dialog)
        self.username.setMaxLength(32)
        self.username.setObjectName("username")
        self.gridLayout.addWidget(self.username, 0, 1, 1, 3)
        self.parentip = IpLine(Dialog)
        self.parentip.setObjectName("parentip")
        self.gridLayout.addWidget(self.parentip, 1, 1, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.username, self.parentip)
        Dialog.setTabOrder(self.parentip, self.parentport)
        Dialog.setTabOrder(self.parentport, self.parentpassword)
        Dialog.setTabOrder(self.parentpassword, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.parentpasswordLabel.setText(QtGui.QApplication.translate("Dialog", "Parent\'s Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.usernameLabel.setText(QtGui.QApplication.translate("Dialog", "Your User Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.parentportLabel.setText(QtGui.QApplication.translate("Dialog", "Parent\'s Port number:", None, QtGui.QApplication.UnicodeUTF8))
        self.parentipLabel.setText(QtGui.QApplication.translate("Dialog", "Parent\'s  IP Address:", None, QtGui.QApplication.UnicodeUTF8))
        self.parentip.setInputMask(QtGui.QApplication.translate("Dialog", "000.000.000.000; ", None, QtGui.QApplication.UnicodeUTF8))

