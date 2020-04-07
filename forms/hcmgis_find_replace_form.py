# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_find_replace_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_find_replace_form(object):
    def setupUi(self, hcmgis_find_replace_form):
        hcmgis_find_replace_form.setObjectName("hcmgis_find_replace_form")
        hcmgis_find_replace_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_find_replace_form.setEnabled(True)
        hcmgis_find_replace_form.resize(341, 235)
        hcmgis_find_replace_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_find_replace_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_find_replace_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.verticalLayout.addWidget(self.LblOutput_2)
        self.CboField = QgsFieldComboBox(hcmgis_find_replace_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.LblChar = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblChar.setObjectName("LblChar")
        self.gridLayout.addWidget(self.LblChar, 0, 0, 1, 1)
        self.LblChar_2 = QtWidgets.QLabel(hcmgis_find_replace_form)
        self.LblChar_2.setObjectName("LblChar_2")
        self.gridLayout.addWidget(self.LblChar_2, 0, 1, 1, 1)
        self.LinFind = QtWidgets.QLineEdit(hcmgis_find_replace_form)
        self.LinFind.setObjectName("LinFind")
        self.gridLayout.addWidget(self.LinFind, 1, 0, 1, 1)
        self.LinReplace = QtWidgets.QLineEdit(hcmgis_find_replace_form)
        self.LinReplace.setObjectName("LinReplace")
        self.gridLayout.addWidget(self.LinReplace, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.ChkSelectedFeaturesOnly = QtWidgets.QCheckBox(hcmgis_find_replace_form)
        self.ChkSelectedFeaturesOnly.setObjectName("ChkSelectedFeaturesOnly")
        self.verticalLayout.addWidget(self.ChkSelectedFeaturesOnly)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_find_replace_form)
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.verticalLayout.addWidget(self.BtnOKCancel)

        self.retranslateUi(hcmgis_find_replace_form)
        self.BtnOKCancel.accepted.connect(hcmgis_find_replace_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_find_replace_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_find_replace_form)

    def retranslateUi(self, hcmgis_find_replace_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_find_replace_form.setWindowTitle(_translate("hcmgis_find_replace_form", "Find and Replace"))
        self.LblInput.setText(_translate("hcmgis_find_replace_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_find_replace_form", "Field"))
        self.LblChar.setText(_translate("hcmgis_find_replace_form", "Find"))
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

