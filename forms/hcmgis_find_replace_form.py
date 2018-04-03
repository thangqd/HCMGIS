# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_find_replace_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_find_replace_form(object):
    def setupUi(self, hcmgis_find_replace_form):
        hcmgis_find_replace_form.setObjectName("hcmgis_find_replace_form")
        hcmgis_find_replace_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_find_replace_form.setEnabled(True)
        hcmgis_find_replace_form.resize(341, 228)
        hcmgis_find_replace_form.setMouseTracking(False)
        self.LblChar = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblChar.setGeometry(QtCore.QRect(10, 110, 151, 16))
        self.LblChar.setObjectName("LblChar")
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_find_replace_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(175, 189, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblInput.setGeometry(QtCore.QRect(11, 11, 321, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_find_replace_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 30, 321, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblOutput_2.setGeometry(QtCore.QRect(10, 63, 321, 16))
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.CboField = QgsFieldComboBox(hcmgis_find_replace_form)
        self.CboField.setGeometry(QtCore.QRect(10, 80, 321, 21))
        self.CboField.setObjectName("CboField")
        self.LinFind = QtWidgets.QLineEdit(hcmgis_find_replace_form)
        self.LinFind.setGeometry(QtCore.QRect(10, 130, 151, 20))
        self.LinFind.setObjectName("LinFind")
        self.LblChar_2 = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblChar_2.setGeometry(QtCore.QRect(180, 110, 151, 20))
        self.LblChar_2.setObjectName("LblChar_2")
        self.LinReplace = QtWidgets.QLineEdit(hcmgis_find_replace_form)
        self.LinReplace.setGeometry(QtCore.QRect(180, 130, 151, 20))
        self.LinReplace.setObjectName("LinReplace")
        self.ChkSelectedFeaturesOnly = QtWidgets.QCheckBox(hcmgis_find_replace_form)
        self.ChkSelectedFeaturesOnly.setGeometry(QtCore.QRect(10, 165, 321, 17))
        self.ChkSelectedFeaturesOnly.setObjectName("ChkSelectedFeaturesOnly")

        self.retranslateUi(hcmgis_find_replace_form)
        self.BtnOKCancel.accepted.connect(hcmgis_find_replace_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_find_replace_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_find_replace_form)

    def retranslateUi(self, hcmgis_find_replace_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_find_replace_form.setWindowTitle(_translate("hcmgis_find_replace_form", "Find and Replace"))
        self.LblChar.setText(_translate("hcmgis_find_replace_form", "Find"))
        self.LblInput.setText(_translate("hcmgis_find_replace_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_find_replace_form", "Field"))
        self.LblChar_2.setText(_translate("hcmgis_find_replace_form", "Replace"))
        self.ChkSelectedFeaturesOnly.setText(_translate("hcmgis_find_replace_form", "Selected features only"))

from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_find_replace_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_find_replace_form()
    ui.setupUi(hcmgis_find_replace_form)
    hcmgis_find_replace_form.show()
    sys.exit(app.exec_())

