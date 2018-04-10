# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_opendata_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_opendata_form(object):
    def setupUi(self, hcmgis_opendata_form):
        hcmgis_opendata_form.setObjectName("hcmgis_opendata_form")
        hcmgis_opendata_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_opendata_form.setEnabled(True)
        hcmgis_opendata_form.resize(411, 324)
        hcmgis_opendata_form.setMouseTracking(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(hcmgis_opendata_form)
        self.buttonBox.setGeometry(QtCore.QRect(240, 290, 160, 26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_4 = QtWidgets.QLabel(hcmgis_opendata_form)
        self.label_4.setGeometry(QtCore.QRect(12, 10, 141, 22))
        self.label_4.setObjectName("label_4")
        self.sourcelayers = QtWidgets.QListWidget(hcmgis_opendata_form)
        self.sourcelayers.setGeometry(QtCore.QRect(12, 30, 391, 201))
        self.sourcelayers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sourcelayers.setObjectName("sourcelayers")
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_opendata_form)
        self.LinOutputFolder.setEnabled(False)
        self.LinOutputFolder.setGeometry(QtCore.QRect(10, 260, 301, 20))
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(False)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_opendata_form)
        self.BtnOutputFolder.setEnabled(False)
        self.BtnOutputFolder.setGeometry(QtCore.QRect(330, 260, 71, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")
        self.ChkSaveShapefile = QtWidgets.QCheckBox(hcmgis_opendata_form)
        self.ChkSaveShapefile.setGeometry(QtCore.QRect(13, 240, 381, 17))
        self.ChkSaveShapefile.setObjectName("ChkSaveShapefile")

        self.retranslateUi(hcmgis_opendata_form)
        self.buttonBox.accepted.connect(hcmgis_opendata_form.accept)
        self.buttonBox.rejected.connect(hcmgis_opendata_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_opendata_form)
        hcmgis_opendata_form.setTabOrder(self.sourcelayers, self.buttonBox)

    def retranslateUi(self, hcmgis_opendata_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_opendata_form.setWindowTitle(_translate("hcmgis_opendata_form", "HCMGIS OpenData"))
        self.label_4.setText(_translate("hcmgis_opendata_form", "Select layers"))
        self.BtnOutputFolder.setText(_translate("hcmgis_opendata_form", "Browse..."))
        self.ChkSaveShapefile.setText(_translate("hcmgis_opendata_form", "Save layers to disk"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_opendata_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_opendata_form()
    ui.setupUi(hcmgis_opendata_form)
    hcmgis_opendata_form.show()
    sys.exit(app.exec_())

