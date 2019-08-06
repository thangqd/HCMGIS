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
        hcmgis_merge_form.resize(360, 229)
        hcmgis_merge_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_merge_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtWidgets.QLabel(hcmgis_merge_form)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.sourcelayers = QtWidgets.QListWidget(hcmgis_merge_form)
        self.sourcelayers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sourcelayers.setObjectName("sourcelayers")
        self.verticalLayout.addWidget(self.sourcelayers)
        self.label = QtWidgets.QLabel(hcmgis_merge_form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.outfilename = QtWidgets.QLineEdit(hcmgis_merge_form)
        self.outfilename.setText("")
        self.outfilename.setReadOnly(False)
        self.outfilename.setObjectName("outfilename")
        self.gridLayout.addWidget(self.outfilename, 0, 0, 1, 1)
        self.browseoutfile = QtWidgets.QPushButton(hcmgis_merge_form)
        self.browseoutfile.setObjectName("browseoutfile")
        self.gridLayout.addWidget(self.browseoutfile, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(hcmgis_merge_form)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

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
        self.label_4.setText(_translate("hcmgis_merge_form", "Select Layers to be merged"))
        self.label.setText(_translate("hcmgis_merge_form", "Output Shapefile"))
        self.browseoutfile.setText(_translate("hcmgis_merge_form", "Browse..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_merge_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_merge_form()
    ui.setupUi(hcmgis_merge_form)
    hcmgis_merge_form.show()
    sys.exit(app.exec_())

