# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_merge_field_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_merge_field_form(object):
    def setupUi(self, hcmgis_merge_field_form):
        hcmgis_merge_field_form.setObjectName("hcmgis_merge_field_form")
        hcmgis_merge_field_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_merge_field_form.setEnabled(True)
        hcmgis_merge_field_form.resize(340, 307)
        hcmgis_merge_field_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_merge_field_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(174, 259, 156, 51))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblInput.setGeometry(QtCore.QRect(11, 8, 321, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_merge_field_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 321, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblOutput_2.setGeometry(QtCore.QRect(10, 54, 321, 16))
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.ListFields = QtWidgets.QListWidget(hcmgis_merge_field_form)
        self.ListFields.setGeometry(QtCore.QRect(10, 70, 321, 111))
        self.ListFields.setAcceptDrops(False)
        self.ListFields.setDragEnabled(False)
        self.ListFields.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ListFields.setAlternatingRowColors(True)
        self.ListFields.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ListFields.setViewMode(QtWidgets.QListView.ListMode)
        self.ListFields.setSelectionRectVisible(True)
        self.ListFields.setObjectName("ListFields")
        self.CboChar = QtWidgets.QComboBox(hcmgis_merge_field_form)
        self.CboChar.setGeometry(QtCore.QRect(10, 210, 321, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.CboChar.setFont(font)
        self.CboChar.setEditable(True)
        self.CboChar.setObjectName("CboChar")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.CboChar.addItem("")
        self.LblChar = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblChar.setGeometry(QtCore.QRect(10, 192, 321, 16))
        self.LblChar.setObjectName("LblChar")
        self.ChkSelectedFeaturesOnly = QtWidgets.QCheckBox(hcmgis_merge_field_form)
        self.ChkSelectedFeaturesOnly.setGeometry(QtCore.QRect(10, 247, 151, 17))
        self.ChkSelectedFeaturesOnly.setObjectName("ChkSelectedFeaturesOnly")

        self.retranslateUi(hcmgis_merge_field_form)
        self.BtnOKCancel.accepted.connect(hcmgis_merge_field_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_merge_field_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_merge_field_form)

    def retranslateUi(self, hcmgis_merge_field_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_merge_field_form.setWindowTitle(_translate("hcmgis_merge_field_form", "Merge Fields"))
        self.LblInput.setText(_translate("hcmgis_merge_field_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_merge_field_form", "Fields (selected order = merged field order)"))
        self.ListFields.setToolTip(_translate("hcmgis_merge_field_form", "Drad & Drop để thay đổi thứ tự trường dữ liệu"))
        self.ListFields.setSortingEnabled(True)
        self.CboChar.setItemText(0, _translate("hcmgis_merge_field_form", "Space"))
        self.CboChar.setItemText(1, _translate("hcmgis_merge_field_form", ","))
        self.CboChar.setItemText(2, _translate("hcmgis_merge_field_form", "_"))
        self.CboChar.setItemText(3, _translate("hcmgis_merge_field_form", "-"))
        self.CboChar.setItemText(4, _translate("hcmgis_merge_field_form", "/"))
        self.CboChar.setItemText(5, _translate("hcmgis_merge_field_form", "|"))
        self.CboChar.setItemText(6, _translate("hcmgis_merge_field_form", "\\"))
        self.CboChar.setItemText(7, _translate("hcmgis_merge_field_form", "."))
        self.CboChar.setItemText(8, _translate("hcmgis_merge_field_form", ":"))
        self.CboChar.setItemText(9, _translate("hcmgis_merge_field_form", ";"))
        self.CboChar.setItemText(10, _translate("hcmgis_merge_field_form", "&"))
        self.LblChar.setText(_translate("hcmgis_merge_field_form", "Linking characters"))
        self.ChkSelectedFeaturesOnly.setText(_translate("hcmgis_merge_field_form", "Selected features only"))

from qgis.gui import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_merge_field_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_merge_field_form()
    ui.setupUi(hcmgis_merge_field_form)
    hcmgis_merge_field_form.show()
    sys.exit(app.exec_())

