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
        hcmgis_opendata_form.resize(557, 464)
        hcmgis_opendata_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_opendata_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(hcmgis_opendata_form)
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.sourcelayers = QtWidgets.QListWidget(hcmgis_opendata_form)
        self.sourcelayers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sourcelayers.setObjectName("sourcelayers")
        self.verticalLayout.addWidget(self.sourcelayers)
        self.ChkSaveShapefile = QtWidgets.QCheckBox(hcmgis_opendata_form)
        self.ChkSaveShapefile.setObjectName("ChkSaveShapefile")
        self.verticalLayout.addWidget(self.ChkSaveShapefile)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_opendata_form)
        self.BtnOutputFolder.setEnabled(False)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")
        self.gridLayout.addWidget(self.BtnOutputFolder, 0, 1, 1, 1)
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_opendata_form)
        self.LinOutputFolder.setEnabled(False)
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(False)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.gridLayout.addWidget(self.LinOutputFolder, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_opendata_form)
        self.BtnApplyClose.setOrientation(QtCore.Qt.Horizontal)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_opendata_form)
        self.BtnApplyClose.accepted.connect(hcmgis_opendata_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_opendata_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_opendata_form)
        hcmgis_opendata_form.setTabOrder(self.sourcelayers, self.BtnApplyClose)

    def retranslateUi(self, hcmgis_opendata_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_opendata_form.setWindowTitle(_translate("hcmgis_opendata_form", "HCMGIS OpenData"))
        self.label_4.setText(_translate("hcmgis_opendata_form", "Select layers"))
        self.ChkSaveShapefile.setText(_translate("hcmgis_opendata_form", "Save layers to disk"))
        self.BtnOutputFolder.setText(_translate("hcmgis_opendata_form", "Browse..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_opendata_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_opendata_form()
    ui.setupUi(hcmgis_opendata_form)
    hcmgis_opendata_form.show()
    sys.exit(app.exec_())

