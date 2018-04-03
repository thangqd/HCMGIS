# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_split_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_split_form(object):
    def setupUi(self, hcmgis_split_form):
        hcmgis_split_form.setObjectName("hcmgis_split_form")
        hcmgis_split_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_split_form.setEnabled(True)
        hcmgis_split_form.resize(341, 188)
        hcmgis_split_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_split_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(175, 150, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_split_form)
        self.LblInput.setGeometry(QtCore.QRect(10, 7, 321, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_split_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 321, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_split_form)
        self.LblOutput_2.setGeometry(QtCore.QRect(10, 54, 321, 16))
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.CboField = QgsFieldComboBox(hcmgis_split_form)
        self.CboField.setGeometry(QtCore.QRect(10, 70, 321, 21))
        self.CboField.setObjectName("CboField")
        self.LblOutput_3 = QtWidgets.QLabel(hcmgis_split_form)
        self.LblOutput_3.setGeometry(QtCore.QRect(10, 100, 321, 16))
        self.LblOutput_3.setObjectName("LblOutput_3")
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_split_form)
        self.LinOutputFolder.setEnabled(True)
        self.LinOutputFolder.setGeometry(QtCore.QRect(10, 120, 241, 20))
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(False)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_split_form)
        self.BtnOutputFolder.setEnabled(True)
        self.BtnOutputFolder.setGeometry(QtCore.QRect(260, 120, 71, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")

        self.retranslateUi(hcmgis_split_form)
        self.BtnOKCancel.accepted.connect(hcmgis_split_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_split_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_split_form)

    def retranslateUi(self, hcmgis_split_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_split_form.setWindowTitle(_translate("hcmgis_split_form", "Split Layers"))
        self.LblInput.setText(_translate("hcmgis_split_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_split_form", "Unique field"))
        self.LblOutput_3.setText(_translate("hcmgis_split_form", "Output Folder"))
        self.BtnOutputFolder.setText(_translate("hcmgis_split_form", "Browse..."))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_split_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_split_form()
    ui.setupUi(hcmgis_split_form)
    hcmgis_split_form.show()
    sys.exit(app.exec_())

