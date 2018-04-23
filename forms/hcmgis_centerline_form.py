# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_centerline_form.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_centerline_form(object):
    def setupUi(self, hcmgis_centerline_form):
        hcmgis_centerline_form.setObjectName("hcmgis_centerline_form")
        hcmgis_centerline_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_centerline_form.setEnabled(True)
        hcmgis_centerline_form.resize(352, 264)
        hcmgis_centerline_form.setMouseTracking(False)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_centerline_form)
        self.BtnOKCancel.setGeometry(QtCore.QRect(190, 230, 156, 31))
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.LblInput = QtWidgets.QLabel(hcmgis_centerline_form)
        self.LblInput.setGeometry(QtCore.QRect(10, 7, 331, 16))
        self.LblInput.setObjectName("LblInput")
        self.CboInput = QgsMapLayerComboBox(hcmgis_centerline_form)
        self.CboInput.setGeometry(QtCore.QRect(10, 24, 331, 21))
        self.CboInput.setObjectName("CboInput")
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_centerline_form)
        self.LblInput_2.setGeometry(QtCore.QRect(10, 56, 331, 16))
        self.LblInput_2.setObjectName("LblInput_2")
        self.spinBox = QtWidgets.QSpinBox(hcmgis_centerline_form)
        self.spinBox.setGeometry(QtCore.QRect(10, 73, 331, 22))
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10)
        self.spinBox.setObjectName("spinBox")
        self.label = QtWidgets.QLabel(hcmgis_centerline_form)
        self.label.setGeometry(QtCore.QRect(10, 190, 331, 16))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.chksurround = QtWidgets.QCheckBox(hcmgis_centerline_form)
        self.chksurround.setGeometry(QtCore.QRect(10, 110, 331, 20))
        self.chksurround.setChecked(False)
        self.chksurround.setObjectName("chksurround")
        self.lblsurround = QtWidgets.QLabel(hcmgis_centerline_form)
        self.lblsurround.setGeometry(QtCore.QRect(10, 138, 331, 16))
        self.lblsurround.setObjectName("lblsurround")
        self.distance = QtWidgets.QSpinBox(hcmgis_centerline_form)
        self.distance.setGeometry(QtCore.QRect(10, 160, 331, 22))
        self.distance.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.distance.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.distance.setMinimum(1)
        self.distance.setMaximum(1000)
        self.distance.setProperty("value", 2)
        self.distance.setObjectName("distance")

        self.retranslateUi(hcmgis_centerline_form)
        self.BtnOKCancel.accepted.connect(hcmgis_centerline_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_centerline_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_centerline_form)

    def retranslateUi(self, hcmgis_centerline_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_centerline_form.setWindowTitle(_translate("hcmgis_centerline_form", "Centerline in the gaps between polygons"))
        self.LblInput.setText(_translate("hcmgis_centerline_form", "Input Polygon (Ex: Block of Buildings)"))
        self.LblInput_2.setText(_translate("hcmgis_centerline_form", "Density (m)"))
        self.label.setText(_translate("hcmgis_centerline_form", "(Notice: Output should be refined after running)"))
        self.chksurround.setText(_translate("hcmgis_centerline_form", "Also create line surround the polygon"))
        self.lblsurround.setText(_translate("hcmgis_centerline_form", "Distance to the bounding box of polygon (m)"))

from qgis.gui import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_centerline_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_centerline_form()
    ui.setupUi(hcmgis_centerline_form)
    hcmgis_centerline_form.show()
    sys.exit(app.exec_())

