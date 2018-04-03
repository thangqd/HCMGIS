# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_reprojection_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_reprojection_form(object):
    def setupUi(self, hcmgis_reprojection_form):
        hcmgis_reprojection_form.setObjectName("hcmgis_reprojection_form")
        hcmgis_reprojection_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_reprojection_form.setEnabled(True)
        hcmgis_reprojection_form.resize(341, 194)
        hcmgis_reprojection_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_reprojection_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(175, 160, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_reprojection_form)
        self.LblInput.setGeometry(QtCore.QRect(10, 7, 321, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_reprojection_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 321, 21))
        self.CboInput.setShowCrs(True)
        self.CboInput.setObjectName("CboInput")
        self.LblOutput_3 = QtWidgets.QLabel(hcmgis_reprojection_form)
        self.LblOutput_3.setGeometry(QtCore.QRect(10, 112, 321, 16))
        self.LblOutput_3.setObjectName("LblOutput_3")
        self.LinOutput = QtWidgets.QLineEdit(hcmgis_reprojection_form)
        self.LinOutput.setEnabled(True)
        self.LinOutput.setGeometry(QtCore.QRect(10, 130, 241, 20))
        self.LinOutput.setMouseTracking(True)
        self.LinOutput.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.LinOutput.setAcceptDrops(False)
        self.LinOutput.setText("")
        self.LinOutput.setReadOnly(False)
        self.LinOutput.setObjectName("LinOutput")
        self.BtnOutput = QtWidgets.QPushButton(hcmgis_reprojection_form)
        self.BtnOutput.setEnabled(True)
        self.BtnOutput.setGeometry(QtCore.QRect(260, 130, 71, 21))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutput.setFont(font)
        self.BtnOutput.setObjectName("BtnOutput")
        self.LblOutput_4 = QtWidgets.QLabel(hcmgis_reprojection_form)
        self.LblOutput_4.setGeometry(QtCore.QRect(10, 55, 321, 16))
        self.LblOutput_4.setObjectName("LblOutput_4")
        self.crs = QgsProjectionSelectionWidget(hcmgis_reprojection_form)
        self.crs.setGeometry(QtCore.QRect(10, 73, 321, 27))
        self.crs.setObjectName("crs")

        self.retranslateUi(hcmgis_reprojection_form)
        self.BtnOKCancel.accepted.connect(hcmgis_reprojection_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_reprojection_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_reprojection_form)

    def retranslateUi(self, hcmgis_reprojection_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_reprojection_form.setWindowTitle(_translate("hcmgis_reprojection_form", "Layer Reprojection"))
        self.LblInput.setText(_translate("hcmgis_reprojection_form", "Input Layer"))
        self.LblOutput_3.setText(_translate("hcmgis_reprojection_form", "Output Shapefile"))
        self.BtnOutput.setText(_translate("hcmgis_reprojection_form", "Browse..."))
        self.LblOutput_4.setText(_translate("hcmgis_reprojection_form", "Target CRS"))

from qgis.gui import QgsMapLayerComboBox, QgsProjectionSelectionWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_reprojection_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_reprojection_form()
    ui.setupUi(hcmgis_reprojection_form)
    hcmgis_reprojection_form.show()
    sys.exit(app.exec_())

