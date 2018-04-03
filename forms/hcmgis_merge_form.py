# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_merge_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_merge_form(object):
    def setupUi(self, hcmgis_merge_form):
        hcmgis_merge_form.setObjectName("hcmgis_merge_form")
        hcmgis_merge_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_merge_form.setEnabled(True)
        hcmgis_merge_form.resize(372, 288)
        hcmgis_merge_form.setMouseTracking(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(hcmgis_merge_form)
        self.buttonBox.setGeometry(QtCore.QRect(205, 262, 160, 26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(hcmgis_merge_form)
        self.label.setGeometry(QtCore.QRect(10, 213, 121, 22))
        self.label.setObjectName("label")
        self.outfilename = QtWidgets.QLineEdit(hcmgis_merge_form)
        self.outfilename.setGeometry(QtCore.QRect(10, 233, 271, 21))
        self.outfilename.setText("")
        self.outfilename.setReadOnly(False)
        self.outfilename.setObjectName("outfilename")
        self.browseoutfile = QtWidgets.QPushButton(hcmgis_merge_form)
        self.browseoutfile.setGeometry(QtCore.QRect(283, 230, 81, 26))
        self.browseoutfile.setObjectName("browseoutfile")
        self.label_4 = QtWidgets.QLabel(hcmgis_merge_form)
        self.label_4.setGeometry(QtCore.QRect(12, 4, 351, 22))
        self.label_4.setObjectName("label_4")
        self.sourcelayers = QtWidgets.QListWidget(hcmgis_merge_form)
        self.sourcelayers.setGeometry(QtCore.QRect(12, 26, 351, 181))
        self.sourcelayers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sourcelayers.setObjectName("sourcelayers")

        self.retranslateUi(hcmgis_merge_form)
        self.buttonBox.accepted.connect(hcmgis_merge_form.accept)
        self.buttonBox.rejected.connect(hcmgis_merge_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_merge_form)
        hcmgis_merge_form.setTabOrder(self.sourcelayers, self.outfilename)
        hcmgis_merge_form.setTabOrder(self.outfilename, self.browseoutfile)
        hcmgis_merge_form.setTabOrder(self.browseoutfile, self.buttonBox)

    def retranslateUi(self, hcmgis_merge_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_merge_form.setWindowTitle(_translate("hcmgis_merge_form", "Merge Layers"))
        self.label.setText(_translate("hcmgis_merge_form", "Output Shapefile"))
        self.browseoutfile.setText(_translate("hcmgis_merge_form", "Browse..."))
        self.label_4.setText(_translate("hcmgis_merge_form", "Select Layers to be merged"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_merge_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_merge_form()
    ui.setupUi(hcmgis_merge_form)
    hcmgis_merge_form.show()
    sys.exit(app.exec_())

