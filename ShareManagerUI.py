# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ShareManager.ui'
#
# Created: Mon Apr 29 02:50:17 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ShareManager(object):
    def setupUi(self, ShareManager):
        ShareManager.setObjectName("ShareManager")
        ShareManager.resize(607, 563)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/users32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ShareManager.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(ShareManager)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(ShareManager)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 1)
        self.removeBottun = QtGui.QPushButton(ShareManager)
        self.removeBottun.setObjectName("removeBottun")
        self.gridLayout.addWidget(self.removeBottun, 3, 1, 1, 1)
        self.readonlyBottun = QtGui.QPushButton(ShareManager)
        self.readonlyBottun.setObjectName("readonlyBottun")
        self.gridLayout.addWidget(self.readonlyBottun, 2, 1, 1, 1)
        self.readwriteBottun = QtGui.QPushButton(ShareManager)
        self.readwriteBottun.setObjectName("readwriteBottun")
        self.gridLayout.addWidget(self.readwriteBottun, 1, 1, 1, 1)
        self.newgroupBottun = QtGui.QPushButton(ShareManager)
        self.newgroupBottun.setObjectName("newgroupBottun")
        self.gridLayout.addWidget(self.newgroupBottun, 0, 1, 1, 1)
        self.tree = QtGui.QTreeWidget(ShareManager)
        self.tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tree.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree.setObjectName("tree")
        self.tree.header().setVisible(True)
        self.tree.header().setCascadingSectionResizes(False)
        self.tree.header().setHighlightSections(False)
        self.tree.header().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tree, 0, 0, 5, 1)

        self.retranslateUi(ShareManager)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ShareManager.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ShareManager.reject)
        QtCore.QMetaObject.connectSlotsByName(ShareManager)
        ShareManager.setTabOrder(self.tree, self.newgroupBottun)
        ShareManager.setTabOrder(self.newgroupBottun, self.readwriteBottun)
        ShareManager.setTabOrder(self.readwriteBottun, self.readonlyBottun)
        ShareManager.setTabOrder(self.readonlyBottun, self.removeBottun)
        ShareManager.setTabOrder(self.removeBottun, self.buttonBox)

    def retranslateUi(self, ShareManager):
        ShareManager.setWindowTitle(QtGui.QApplication.translate("ShareManager", "ShareManager", None, QtGui.QApplication.UnicodeUTF8))
        self.removeBottun.setText(QtGui.QApplication.translate("ShareManager", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.readonlyBottun.setText(QtGui.QApplication.translate("ShareManager", "Read Only", None, QtGui.QApplication.UnicodeUTF8))
        self.readwriteBottun.setText(QtGui.QApplication.translate("ShareManager", "Read/Write", None, QtGui.QApplication.UnicodeUTF8))
        self.newgroupBottun.setText(QtGui.QApplication.translate("ShareManager", "New Group", None, QtGui.QApplication.UnicodeUTF8))
        self.tree.headerItem().setText(0, QtGui.QApplication.translate("ShareManager", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.tree.headerItem().setText(1, QtGui.QApplication.translate("ShareManager", "IP Address", None, QtGui.QApplication.UnicodeUTF8))
        self.tree.headerItem().setText(2, QtGui.QApplication.translate("ShareManager", "Permission", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
