# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_closestpair_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_closestpair_form(object):
    def setupUi(self, hcmgis_closestpair_form):
        hcmgis_closestpair_form.setObjectName("hcmgis_closestpair_form")
        hcmgis_closestpair_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_closestpair_form.setEnabled(True)
        hcmgis_closestpair_form.resize(422, 319)
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
        self.LblOutput = QtWidgets.QLabel(hcmgis_closestpair_form)
        self.LblOutput.setObjectName("LblOutput")
        self.verticalLayout.addWidget(self.LblOutput)
        self.closest = QgsFileWidget(hcmgis_closestpair_form)
        self.closest.setObjectName("closest")
        self.verticalLayout.addWidget(self.closest)
        self.label = QtWidgets.QLabel(hcmgis_closestpair_form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.farthest = QgsFileWidget(hcmgis_closestpair_form)
        self.farthest.setObjectName("farthest")
        self.verticalLayout.addWidget(self.farthest)
        self.LblStatus = QtWidgets.QLabel(hcmgis_closestpair_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.verticalLayout.addWidget(self.LblStatus)
        self.status = QtWidgets.QProgressBar(hcmgis_closestpair_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
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
        self.LblOutput.setText(_translate("hcmgis_closestpair_form", "Closest pair of point"))
        self.label.setText(_translate("hcmgis_closestpair_form", "Farthest pair of point"))

from qgsfieldcombobox import QgsFieldComboBox
from qgsfilewidget import QgsFileWidget
from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_closestpair_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_closestpair_form()
    ui.setupUi(hcmgis_closestpair_form)
    hcmgis_closestpair_form.show()
    sys.exit(app.exec_())

