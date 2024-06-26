# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_merge_field_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_merge_field_form(object):
    def setupUi(self, hcmgis_merge_field_form):
        hcmgis_merge_field_form.setObjectName("hcmgis_merge_field_form")
        hcmgis_merge_field_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_merge_field_form.setEnabled(True)
        hcmgis_merge_field_form.resize(523, 484)
        hcmgis_merge_field_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_merge_field_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_merge_field_form)
        self.CboInput.setShowCrs(True)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblOutput_2 = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblOutput_2.setObjectName("LblOutput_2")
        self.verticalLayout.addWidget(self.LblOutput_2)
        self.ListFields = QtWidgets.QListWidget(hcmgis_merge_field_form)
        self.ListFields.setAcceptDrops(False)
        self.ListFields.setDragEnabled(False)
        self.ListFields.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ListFields.setAlternatingRowColors(True)
        self.ListFields.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ListFields.setViewMode(QtWidgets.QListView.ListMode)
        self.ListFields.setSelectionRectVisible(True)
        self.ListFields.setObjectName("ListFields")
        self.verticalLayout.addWidget(self.ListFields)
        self.LblChar = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblChar.setObjectName("LblChar")
        self.verticalLayout.addWidget(self.LblChar)
        self.CboChar = QtWidgets.QComboBox(hcmgis_merge_field_form)
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
        self.verticalLayout.addWidget(self.CboChar)
        self.LblStatus = QtWidgets.QLabel(hcmgis_merge_field_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.verticalLayout.addWidget(self.LblStatus)
        self.status = QtWidgets.QProgressBar(hcmgis_merge_field_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_merge_field_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_merge_field_form)
        self.BtnApplyClose.accepted.connect(hcmgis_merge_field_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_merge_field_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_merge_field_form)

    def retranslateUi(self, hcmgis_merge_field_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_merge_field_form.setWindowTitle(_translate("hcmgis_merge_field_form", "Merge Fields"))
        self.LblInput.setText(_translate("hcmgis_merge_field_form", "Input Layer"))
        self.LblOutput_2.setText(_translate("hcmgis_merge_field_form", "Fields (selected order = merged field order)"))
        self.ListFields.setToolTip(_translate("hcmgis_merge_field_form", "Drad & Drop để thay đổi thứ tự trường dữ liệu"))
        self.ListFields.setSortingEnabled(True)
        self.LblChar.setText(_translate("hcmgis_merge_field_form", "Linking characters"))
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
from qgsmaplayercombobox import QgsMapLayerComboBox


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_merge_field_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_merge_field_form()
    ui.setupUi(hcmgis_merge_field_form)
    hcmgis_merge_field_form.show()
    sys.exit(app.exec_())
