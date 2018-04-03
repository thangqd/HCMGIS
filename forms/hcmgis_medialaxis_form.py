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
        hcmgis_medialaxis_form.resize(352, 231)
        hcmgis_medialaxis_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_medialaxis_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(190, 197, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput.setGeometry(QtCore.QRect(10, 7, 331, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_medialaxis_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 331, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_2.setGeometry(QtCore.QRect(10, 113, 331, 16))
        self.LblInput_2.setObjectName("LblInput_2")
        self.spinBox = QtWidgets.QSpinBox(hcmgis_medialaxis_form)
        self.spinBox.setGeometry(QtCore.QRect(10, 130, 331, 22))
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10)
        self.spinBox.setObjectName("spinBox")
        self.CboField = QgsFieldComboBox(hcmgis_medialaxis_form)
        self.CboField.setGeometry(QtCore.QRect(10, 80, 331, 21))
        self.CboField.setObjectName("CboField")
        self.LblInput_3 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_3.setGeometry(QtCore.QRect(10, 61, 321, 16))
        self.LblInput_3.setObjectName("LblInput_3")
        self.label = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.label.setGeometry(QtCore.QRect(10, 167, 331, 16))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(hcmgis_medialaxis_form)
        self.BtnOKCancel.accepted.connect(hcmgis_medialaxis_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_medialaxis_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_medialaxis_form)

    def retranslateUi(self, hcmgis_medialaxis_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_medialaxis_form.setWindowTitle(_translate("hcmgis_medialaxis_form", "Skeleton/Medial Axis"))
        self.LblInput.setText(_translate("hcmgis_medialaxis_form", "Input Polygon (1..100 selected features limit!)"))
        self.LblInput_2.setText(_translate("hcmgis_medialaxis_form", "Density (m)"))
        self.LblInput_3.setText(_translate("hcmgis_medialaxis_form", "Unique field (when selected features > 1)"))
        self.label.setText(_translate("hcmgis_medialaxis_form", "(Notice: Output should be refined after running)"))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_medialaxis_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_medialaxis_form()
    ui.setupUi(hcmgis_medialaxis_form)
    hcmgis_medialaxis_form.show()
    sys.exit(app.exec_())

