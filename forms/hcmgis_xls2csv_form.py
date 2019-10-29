# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_xls2csv_form.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_xls2csv_form(object):
    def setupUi(self, hcmgis_xls2csv_form):
        hcmgis_xls2csv_form.setObjectName("hcmgis_xls2csv_form")
        hcmgis_xls2csv_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_xls2csv_form.setEnabled(True)
        hcmgis_xls2csv_form.resize(513, 465)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        hcmgis_xls2csv_form.setFont(font)
        hcmgis_xls2csv_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_xls2csv_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(hcmgis_xls2csv_form)
        self.label_2.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.BtnInputFolder = QtWidgets.QPushButton(hcmgis_xls2csv_form)
        self.BtnInputFolder.setEnabled(True)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnInputFolder.setFont(font)
        self.BtnInputFolder.setObjectName("BtnInputFolder")
        self.gridLayout_3.addWidget(self.BtnInputFolder, 0, 1, 1, 1)
        self.LinInputFolder = QtWidgets.QLineEdit(hcmgis_xls2csv_form)
        self.LinInputFolder.setEnabled(True)
        self.LinInputFolder.setMouseTracking(True)
        self.LinInputFolder.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinInputFolder.setAcceptDrops(False)
        self.LinInputFolder.setText("")
        self.LinInputFolder.setReadOnly(False)
        self.LinInputFolder.setObjectName("LinInputFolder")
        self.gridLayout_3.addWidget(self.LinInputFolder, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.LblXLS = QtWidgets.QLabel(hcmgis_xls2csv_form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.LblXLS.setFont(font)
        self.LblXLS.setText("")
        self.LblXLS.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.LblXLS.setObjectName("LblXLS")
        self.verticalLayout.addWidget(self.LblXLS)
        self.lsXLS = QtWidgets.QListWidget(hcmgis_xls2csv_form)
        self.lsXLS.setObjectName("lsXLS")
        self.verticalLayout.addWidget(self.lsXLS)
        self.lblStatus = QtWidgets.QLabel(hcmgis_xls2csv_form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblStatus.setFont(font)
        self.lblStatus.setText("")
        self.lblStatus.setObjectName("lblStatus")
        self.verticalLayout.addWidget(self.lblStatus)
        self.status = QtWidgets.QProgressBar(hcmgis_xls2csv_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.label = QtWidgets.QLabel(hcmgis_xls2csv_form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.txtError = QtWidgets.QTextEdit(hcmgis_xls2csv_form)
        self.txtError.setObjectName("txtError")
        self.verticalLayout.addWidget(self.txtError)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_xls2csv_form)
        self.BtnOKCancel.setOrientation(QtCore.Qt.Horizontal)
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnOKCancel.setCenterButtons(False)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.verticalLayout.addWidget(self.BtnOKCancel)

        self.retranslateUi(hcmgis_xls2csv_form)
        self.BtnOKCancel.accepted.connect(hcmgis_xls2csv_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_xls2csv_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_xls2csv_form)

    def retranslateUi(self, hcmgis_xls2csv_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_xls2csv_form.setWindowTitle(_translate("hcmgis_xls2csv_form", "Batch Convert XLSX to CSV"))
        self.label_2.setText(_translate("hcmgis_xls2csv_form", "Input XLSX Folder"))
        self.BtnInputFolder.setText(_translate("hcmgis_xls2csv_form", "Browse..."))
        self.label.setText(_translate("hcmgis_xls2csv_form", "Errors Log"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_xls2csv_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_xls2csv_form()
    ui.setupUi(hcmgis_xls2csv_form)
    hcmgis_xls2csv_form.show()
    sys.exit(app.exec_())
