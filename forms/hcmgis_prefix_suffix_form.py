# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_prefix_suffix_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_prefix_suffix_form(object):
    def setupUi(self, hcmgis_prefix_suffix_form):
        hcmgis_prefix_suffix_form.setObjectName("hcmgis_prefix_suffix_form")
        hcmgis_prefix_suffix_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_prefix_suffix_form.setEnabled(True)
        hcmgis_prefix_suffix_form.resize(343, 287)
        hcmgis_prefix_suffix_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_prefix_suffix_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_prefix_suffix_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.verticalLayout.addWidget(self.LblOutput_2)
        self.CboField = QgsFieldComboBox(hcmgis_prefix_suffix_form)
        self.CboField.setObjectName("CboField")
        self.verticalLayout.addWidget(self.CboField)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.LblChar = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblChar.setObjectName("LblChar")
        self.gridLayout.addWidget(self.LblChar, 0, 0, 1, 1)
        self.LblChar_3 = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblChar_3.setObjectName("LblChar_3")
        self.gridLayout.addWidget(self.LblChar_3, 0, 1, 1, 1)
        self.LinPrefix = QtWidgets.QLineEdit(hcmgis_prefix_suffix_form)
        self.LinPrefix.setObjectName("LinPrefix")
        self.gridLayout.addWidget(self.LinPrefix, 1, 0, 1, 1)
        self.CboCharPrefix = QtWidgets.QComboBox(hcmgis_prefix_suffix_form)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CboCharPrefix.setFont(font)
        self.CboCharPrefix.setEditable(True)
        self.CboCharPrefix.setObjectName("CboCharPrefix")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.CboCharPrefix.addItem("")
        self.gridLayout.addWidget(self.CboCharPrefix, 1, 1, 1, 1)
        self.LblChar_2 = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblChar_2.setObjectName("LblChar_2")
        self.gridLayout.addWidget(self.LblChar_2, 2, 0, 1, 1)
        self.LblChar_4 = QtWidgets.QLabel(hcmgis_prefix_suffix_form)
        self.LblChar_4.setObjectName("LblChar_4")
        self.gridLayout.addWidget(self.LblChar_4, 2, 1, 1, 1)
        self.LinSuffix = QtWidgets.QLineEdit(hcmgis_prefix_suffix_form)
        self.LinSuffix.setObjectName("LinSuffix")
        self.gridLayout.addWidget(self.LinSuffix, 3, 0, 1, 1)
        self.CboCharSuffix = QtWidgets.QComboBox(hcmgis_prefix_suffix_form)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CboCharSuffix.setFont(font)
        self.CboCharSuffix.setEditable(True)
        self.CboCharSuffix.setObjectName("CboCharSuffix")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.CboCharSuffix.addItem("")
        self.gridLayout.addWidget(self.CboCharSuffix, 3, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.ChkSelectedFeaturesOnly = QtWidgets.QCheckBox(hcmgis_prefix_suffix_form)
        self.ChkSelectedFeaturesOnly.setObjectName("ChkSelectedFeaturesOnly")
        self.verticalLayout.addWidget(self.ChkSelectedFeaturesOnly)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_prefix_suffix_form)
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.verticalLayout.addWidget(self.BtnOKCancel)

        self.retranslateUi(hcmgis_prefix_suffix_form)
        self.BtnOKCancel.accepted.connect(hcmgis_prefix_suffix_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_prefix_suffix_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_prefix_suffix_form)

    def retranslateUi(self, hcmgis_prefix_suffix_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_prefix_suffix_form.setWindowTitle(_translate("hcmgis_prefix_suffix_form", "Add Prefix/ Suffix"))
        self.LblInput.setText(_translate("hcmgis_prefix_suffix_form", "Imput Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_prefix_suffix_form", "Field"))
        self.LblChar.setText(_translate("hcmgis_prefix_suffix_form", "Prefix"))
        self.LblChar_3.setText(_translate("hcmgis_prefix_suffix_form", "Linking Characters"))
        self.CboCharPrefix.setItemText(0, _translate("hcmgis_prefix_suffix_form", "Space"))
        self.CboCharPrefix.setItemText(1, _translate("hcmgis_prefix_suffix_form", "Tab"))
        self.CboCharPrefix.setItemText(2, _translate("hcmgis_prefix_suffix_form", ","))
        self.CboCharPrefix.setItemText(3, _translate("hcmgis_prefix_suffix_form", "_"))
        self.CboCharPrefix.setItemText(4, _translate("hcmgis_prefix_suffix_form", "-"))
        self.CboCharPrefix.setItemText(5, _translate("hcmgis_prefix_suffix_form", "/"))
        self.CboCharPrefix.setItemText(6, _translate("hcmgis_prefix_suffix_form", "|"))
        self.CboCharPrefix.setItemText(7, _translate("hcmgis_prefix_suffix_form", "\\"))
        self.CboCharPrefix.setItemText(8, _translate("hcmgis_prefix_suffix_form", "."))
        self.CboCharPrefix.setItemText(9, _translate("hcmgis_prefix_suffix_form", ":"))
        self.CboCharPrefix.setItemText(10, _translate("hcmgis_prefix_suffix_form", ";"))
        self.CboCharPrefix.setItemText(11, _translate("hcmgis_prefix_suffix_form", "~"))
        self.CboCharPrefix.setItemText(12, _translate("hcmgis_prefix_suffix_form", "`"))
        self.CboCharPrefix.setItemText(13, _translate("hcmgis_prefix_suffix_form", "!"))
        self.CboCharPrefix.setItemText(14, _translate("hcmgis_prefix_suffix_form", "@"))
        self.CboCharPrefix.setItemText(15, _translate("hcmgis_prefix_suffix_form", "#"))
        self.CboCharPrefix.setItemText(16, _translate("hcmgis_prefix_suffix_form", "$"))
        self.CboCharPrefix.setItemText(17, _translate("hcmgis_prefix_suffix_form", "%"))
        self.CboCharPrefix.setItemText(18, _translate("hcmgis_prefix_suffix_form", "&"))
        self.CboCharPrefix.setItemText(19, _translate("hcmgis_prefix_suffix_form", "*"))
        self.CboCharPrefix.setItemText(20, _translate("hcmgis_prefix_suffix_form", "("))
        self.CboCharPrefix.setItemText(21, _translate("hcmgis_prefix_suffix_form", ")"))
        self.CboCharPrefix.setItemText(22, _translate("hcmgis_prefix_suffix_form", "{"))
        self.CboCharPrefix.setItemText(23, _translate("hcmgis_prefix_suffix_form", "}"))
        self.CboCharPrefix.setItemText(24, _translate("hcmgis_prefix_suffix_form", "["))
        self.CboCharPrefix.setItemText(25, _translate("hcmgis_prefix_suffix_form", "]"))
        self.CboCharPrefix.setItemText(26, _translate("hcmgis_prefix_suffix_form", "\'"))
        self.CboCharPrefix.setItemText(27, _translate("hcmgis_prefix_suffix_form", "\""))
        self.CboCharPrefix.setItemText(28, _translate("hcmgis_prefix_suffix_form", "<"))
        self.CboCharPrefix.setItemText(29, _translate("hcmgis_prefix_suffix_form", ">"))
        self.LblChar_2.setText(_translate("hcmgis_prefix_suffix_form", "Suffix"))
        self.LblChar_4.setText(_translate("hcmgis_prefix_suffix_form", "Linking Characters"))
        self.CboCharSuffix.setItemText(0, _translate("hcmgis_prefix_suffix_form", "Space"))
        self.CboCharSuffix.setItemText(1, _translate("hcmgis_prefix_suffix_form", "Tab"))
        self.CboCharSuffix.setItemText(2, _translate("hcmgis_prefix_suffix_form", ","))
        self.CboCharSuffix.setItemText(3, _translate("hcmgis_prefix_suffix_form", "_"))
        self.CboCharSuffix.setItemText(4, _translate("hcmgis_prefix_suffix_form", "-"))
        self.CboCharSuffix.setItemText(5, _translate("hcmgis_prefix_suffix_form", "/"))
        self.CboCharSuffix.setItemText(6, _translate("hcmgis_prefix_suffix_form", "|"))
        self.CboCharSuffix.setItemText(7, _translate("hcmgis_prefix_suffix_form", "\\"))
        self.CboCharSuffix.setItemText(8, _translate("hcmgis_prefix_suffix_form", "."))
        self.CboCharSuffix.setItemText(9, _translate("hcmgis_prefix_suffix_form", ":"))
        self.CboCharSuffix.setItemText(10, _translate("hcmgis_prefix_suffix_form", ";"))
        self.CboCharSuffix.setItemText(11, _translate("hcmgis_prefix_suffix_form", "~"))
        self.CboCharSuffix.setItemText(12, _translate("hcmgis_prefix_suffix_form", "`"))
        self.CboCharSuffix.setItemText(13, _translate("hcmgis_prefix_suffix_form", "!"))
        self.CboCharSuffix.setItemText(14, _translate("hcmgis_prefix_suffix_form", "@"))
        self.CboCharSuffix.setItemText(15, _translate("hcmgis_prefix_suffix_form", "#"))
        self.CboCharSuffix.setItemText(16, _translate("hcmgis_prefix_suffix_form", "$"))
        self.CboCharSuffix.setItemText(17, _translate("hcmgis_prefix_suffix_form", "%"))
        self.CboCharSuffix.setItemText(18, _translate("hcmgis_prefix_suffix_form", "&"))
        self.CboCharSuffix.setItemText(19, _translate("hcmgis_prefix_suffix_form", "*"))
        self.CboCharSuffix.setItemText(20, _translate("hcmgis_prefix_suffix_form", "("))
        self.CboCharSuffix.setItemText(21, _translate("hcmgis_prefix_suffix_form", ")"))
        self.CboCharSuffix.setItemText(22, _translate("hcmgis_prefix_suffix_form", "{"))
        self.CboCharSuffix.setItemText(23, _translate("hcmgis_prefix_suffix_form", "}"))
        self.CboCharSuffix.setItemText(24, _translate("hcmgis_prefix_suffix_form", "["))
        self.CboCharSuffix.setItemText(25, _translate("hcmgis_prefix_suffix_form", "]"))
        self.CboCharSuffix.setItemText(26, _translate("hcmgis_prefix_suffix_form", "\'"))
        self.CboCharSuffix.setItemText(27, _translate("hcmgis_prefix_suffix_form", "\""))
        self.CboCharSuffix.setItemText(28, _translate("hcmgis_prefix_suffix_form", "<"))
        self.CboCharSuffix.setItemText(29, _translate("hcmgis_prefix_suffix_form", ">"))
        self.ChkSelectedFeaturesOnly.setText(_translate("hcmgis_prefix_suffix_form", "Selected features only"))
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_prefix_suffix_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_prefix_suffix_form()
    ui.setupUi(hcmgis_prefix_suffix_form)
    hcmgis_prefix_suffix_form.show()
    sys.exit(app.exec_())
