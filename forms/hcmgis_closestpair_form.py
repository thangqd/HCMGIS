# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_closestpair_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_closestpair_form(object):
    def setupUi(self, hcmgis_closestpair_form):
        hcmgis_closestpair_form.setObjectName("hcmgis_closestpair_form")
        hcmgis_closestpair_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_closestpair_form.setEnabled(True)
        hcmgis_closestpair_form.resize(450, 154)
        hcmgis_closestpair_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_closestpair_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_closestpair_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_closestpair_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_closestpair_form)
        self.LblInput_2.setObjectName("LblInput_2")
        self.verticalLayout.addWidget(self.LblInput_2)
        self.CboField = QgsFieldComboBox(hcmgis_closestpair_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_closestpair_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_closestpair_form)
        self.BtnApplyClose.accepted.connect(hcmgis_closestpair_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_closestpair_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_closestpair_form)

    def retranslateUi(self, hcmgis_closestpair_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_closestpair_form.setWindowTitle(_translate("hcmgis_closestpair_form", "Closest/farthest pair of Points"))
        self.LblInput.setText(_translate("hcmgis_closestpair_form", "Input Point Layer"))
        self.LblInput_2.setText(_translate("hcmgis_closestpair_form", "Unique Field"))

from qgsfieldcombobox import QgsFieldComboBox
from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_closestpair_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_closestpair_form()
    ui.setupUi(hcmgis_closestpair_form)
    hcmgis_closestpair_form.show()
    sys.exit(app.exec_())

