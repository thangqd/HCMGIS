# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_lec_form.ui'
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
        hcmgis_lec_form.resize(338, 154)
        hcmgis_lec_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_lec_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_lec_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_lec_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.verticalLayout.addWidget(self.LblOutput_2)
        self.CboField = QgsFieldComboBox(hcmgis_lec_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_lec_form)
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.verticalLayout.addWidget(self.BtnOKCancel)

        self.retranslateUi(hcmgis_lec_form)
        self.BtnOKCancel.accepted.connect(hcmgis_lec_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_lec_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_lec_form)

    def retranslateUi(self, hcmgis_lec_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_lec_form.setWindowTitle(_translate("hcmgis_lec_form", "Largest Empty Circle"))
        self.LblInput.setText(_translate("hcmgis_lec_form", "Input Point Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_lec_form", "Unique field"))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_lec_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_lec_form()
    ui.setupUi(hcmgis_lec_form)
    hcmgis_lec_form.show()
    sys.exit(app.exec_())

