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
        hcmgis_split_form.resize(522, 214)
        hcmgis_split_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_split_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_split_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_split_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_split_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.verticalLayout.addWidget(self.LblOutput_2)
        self.CboField = QgsFieldComboBox(hcmgis_split_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.LblOutput_3 = QtWidgets.QLabel(hcmgis_split_form)
        self.LblOutput_3.setObjectName("LblOutput_3")
        self.verticalLayout.addWidget(self.LblOutput_3)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_split_form)
        self.LinOutputFolder.setEnabled(True)
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(False)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.gridLayout.addWidget(self.LinOutputFolder, 0, 0, 1, 1)
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_split_form)
        self.BtnOutputFolder.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")
        self.gridLayout.addWidget(self.BtnOutputFolder, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_split_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_split_form)
        self.BtnApplyClose.accepted.connect(hcmgis_split_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_split_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_split_form)

    def retranslateUi(self, hcmgis_split_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_split_form.setWindowTitle(_translate("hcmgis_split_form", "Split Layers"))
        self.LblInput.setText(_translate("hcmgis_split_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_split_form", "Unique field"))
        self.LblOutput_3.setText(_translate("hcmgis_split_form", "Output Folder"))
        self.BtnOutputFolder.setText(_translate("hcmgis_split_form", "Browse..."))

from qgsfieldcombobox import QgsFieldComboBox
from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_split_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_split_form()
    ui.setupUi(hcmgis_split_form)
    hcmgis_split_form.show()
    sys.exit(app.exec_())

