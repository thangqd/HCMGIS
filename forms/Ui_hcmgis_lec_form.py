# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\KT_HCMGIS\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\HCMGIS\forms\hcmgis_lec_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_lec_form(object):
    def setupUi(self, hcmgis_lec_form):
        hcmgis_lec_form.setObjectName("hcmgis_lec_form")
        hcmgis_lec_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_lec_form.setEnabled(True)
        hcmgis_lec_form.resize(341, 145)
        hcmgis_lec_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_lec_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(175, 110, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblInput.setGeometry(QtCore.QRect(10, 7, 321, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_lec_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 321, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblOutput_3 = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblOutput_3.setGeometry(QtCore.QRect(10, 60, 321, 16))
        self.LblOutput_3.setObjectName("LblOutput_3")
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_lec_form)
        self.LinOutputFolder.setEnabled(True)
        self.LinOutputFolder.setGeometry(QtCore.QRect(10, 80, 241, 20))
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(False)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_lec_form)
        self.BtnOutputFolder.setEnabled(True)
        self.BtnOutputFolder.setGeometry(QtCore.QRect(260, 80, 71, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")

        self.retranslateUi(hcmgis_lec_form)
        self.BtnOKCancel.accepted.connect(hcmgis_lec_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_lec_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_lec_form)

    def retranslateUi(self, hcmgis_lec_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_lec_form.setWindowTitle(_translate("hcmgis_lec_form", "Largest Empty Circle"))
        self.LblInput.setText(_translate("hcmgis_lec_form", "Input Layer"))
        self.LblOutput_3.setText(_translate("hcmgis_lec_form", "Output Folder"))
        self.BtnOutputFolder.setText(_translate("hcmgis_lec_form", "Browse..."))

from qgis.gui import QgsMapLayerComboBox
