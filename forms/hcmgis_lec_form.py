# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_lec_form.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_lec_form(object):
    def setupUi(self, hcmgis_lec_form):
        hcmgis_lec_form.setObjectName("hcmgis_lec_form")
        hcmgis_lec_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_lec_form.setEnabled(True)
        hcmgis_lec_form.resize(487, 325)
        hcmgis_lec_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_lec_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.gridLayout.addWidget(self.LblOutput_2, 2, 0, 1, 2)
        self.status = QtWidgets.QProgressBar(hcmgis_lec_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.gridLayout.addWidget(self.status, 10, 0, 1, 2)
        self.LblInput = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblInput.setObjectName("LblInput")
        self.gridLayout.addWidget(self.LblInput, 0, 0, 1, 2)
        self.CboField = QgsFieldComboBox(hcmgis_lec_form)
        self.CboField.setObjectName("CboField")
        self.gridLayout.addWidget(self.CboField, 3, 0, 1, 2)
        self.LblStatus = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.gridLayout.addWidget(self.LblStatus, 8, 0, 1, 2)
        self.LblOutput = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblOutput.setObjectName("LblOutput")
        self.gridLayout.addWidget(self.LblOutput, 4, 0, 1, 2)
        self.CboInput = QgsMapLayerComboBox(hcmgis_lec_form)
        self.CboInput.setObjectName("CboInput")
        self.gridLayout.addWidget(self.CboInput, 1, 0, 1, 2)
        self.output_file_name = QgsFileWidget(hcmgis_lec_form)
        self.output_file_name.setObjectName("output_file_name")
        self.gridLayout.addWidget(self.output_file_name, 5, 0, 1, 1)
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
        self.LblOutput.setText(_translate("hcmgis_lec_form", "Output"))
from qgsfieldcombobox import QgsFieldComboBox
from qgsfilewidget import QgsFileWidget
from qgsmaplayercombobox import QgsMapLayerComboBox


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_lec_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_lec_form()
    ui.setupUi(hcmgis_lec_form)
    hcmgis_lec_form.show()
    sys.exit(app.exec_())
