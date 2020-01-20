# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_medialaxis_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_medialaxis_form(object):
    def setupUi(self, hcmgis_medialaxis_form):
        hcmgis_medialaxis_form.setObjectName("hcmgis_medialaxis_form")
        hcmgis_medialaxis_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_medialaxis_form.setEnabled(True)
        hcmgis_medialaxis_form.resize(461, 229)
        hcmgis_medialaxis_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_medialaxis_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_medialaxis_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblInput_3 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_3.setObjectName("LblInput_3")
        self.verticalLayout.addWidget(self.LblInput_3)
        self.CboField = QgsFieldComboBox(hcmgis_medialaxis_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_2.setObjectName("LblInput_2")
        self.verticalLayout.addWidget(self.LblInput_2)
        self.spinBox = QtWidgets.QSpinBox(hcmgis_medialaxis_form)
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10)
        self.spinBox.setObjectName("spinBox")
        self.verticalLayout.addWidget(self.spinBox)
        self.label = QtWidgets.QLabel(hcmgis_medialaxis_form)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_medialaxis_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_medialaxis_form)
        self.BtnApplyClose.accepted.connect(hcmgis_medialaxis_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_medialaxis_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_medialaxis_form)

    def retranslateUi(self, hcmgis_medialaxis_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_medialaxis_form.setWindowTitle(_translate("hcmgis_medialaxis_form", "Skeleton/Medial Axis"))
        self.LblInput.setText(_translate("hcmgis_medialaxis_form", "Input Polygon (1..100 selected features limit!)"))
        self.LblInput_3.setText(_translate("hcmgis_medialaxis_form", "Unique field (when selected features > 1)"))
        self.LblInput_2.setText(_translate("hcmgis_medialaxis_form", "Density (m)"))
        self.label.setText(_translate("hcmgis_medialaxis_form", "(Notice: Output should be refined after running)"))

from qgsfieldcombobox import QgsFieldComboBox
from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_medialaxis_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_medialaxis_form()
    ui.setupUi(hcmgis_medialaxis_form)
    hcmgis_medialaxis_form.show()
    sys.exit(app.exec_())

