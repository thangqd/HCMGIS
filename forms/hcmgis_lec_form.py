# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_lec_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_lec_form(object):
    def setupUi(self, hcmgis_lec_form):
        hcmgis_lec_form.setObjectName("hcmgis_lec_form")
        hcmgis_lec_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_lec_form.setEnabled(True)
        hcmgis_lec_form.resize(487, 340)
        hcmgis_lec_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_lec_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.status = QtWidgets.QProgressBar(hcmgis_lec_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.gridLayout.addWidget(self.status, 10, 0, 1, 2)
        self.CboField = QgsFieldComboBox(hcmgis_lec_form)
        self.CboField.setObjectName("CboField")
        self.gridLayout.addWidget(self.CboField, 3, 0, 1, 2)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.gridLayout.addWidget(self.LblOutput_2, 2, 0, 1, 2)
        self.CboInput = QgsMapLayerComboBox(hcmgis_lec_form)
        self.CboInput.setObjectName("CboInput")
        self.gridLayout.addWidget(self.CboInput, 1, 0, 1, 2)
        self.LblInput = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblInput.setObjectName("LblInput")
        self.gridLayout.addWidget(self.LblInput, 0, 0, 1, 2)
        self.LinOutput = QtWidgets.QLineEdit(hcmgis_lec_form)
        self.LinOutput.setReadOnly(True)
        self.LinOutput.setObjectName("LinOutput")
        self.gridLayout.addWidget(self.LinOutput, 7, 0, 1, 1)
        self.BtnBrowseOutput = QtWidgets.QPushButton(hcmgis_lec_form)
        self.BtnBrowseOutput.setObjectName("BtnBrowseOutput")
        self.gridLayout.addWidget(self.BtnBrowseOutput, 7, 1, 1, 1)
        self.LblStatus = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.gridLayout.addWidget(self.LblStatus, 8, 0, 1, 2)
        self.lblOutput = QtWidgets.QLabel(hcmgis_lec_form)
        self.lblOutput.setObjectName("lblOutput")
        self.gridLayout.addWidget(self.lblOutput, 4, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_lec_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_lec_form)
        self.BtnApplyClose.accepted.connect(hcmgis_lec_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_lec_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_lec_form)

    def retranslateUi(self, hcmgis_lec_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_lec_form.setWindowTitle(_translate("hcmgis_lec_form", "Largest Empty Circle"))
        self.LblOutput_2.setText(_translate("hcmgis_lec_form", "Unique field"))
        self.LblInput.setText(_translate("hcmgis_lec_form", "Input Point Layer"))
        self.BtnBrowseOutput.setText(_translate("hcmgis_lec_form", "..."))
        self.lblOutput.setText(_translate("hcmgis_lec_form", "Output"))

from qgsfieldcombobox import QgsFieldComboBox
from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_lec_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_lec_form()
    ui.setupUi(hcmgis_lec_form)
    hcmgis_lec_form.show()
    sys.exit(app.exec_())

