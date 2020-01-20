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
        hcmgis_centerline_form.resize(467, 256)
        hcmgis_centerline_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_centerline_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_centerline_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_centerline_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_centerline_form)
        self.LblInput_2.setObjectName("LblInput_2")
        self.verticalLayout.addWidget(self.LblInput_2)
        self.spinBox = QtWidgets.QSpinBox(hcmgis_centerline_form)
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10)
        self.spinBox.setObjectName("spinBox")
        self.verticalLayout.addWidget(self.spinBox)
        self.chksurround = QtWidgets.QCheckBox(hcmgis_centerline_form)
        self.chksurround.setChecked(False)
        self.chksurround.setObjectName("chksurround")
        self.verticalLayout.addWidget(self.chksurround)
        self.lblsurround = QtWidgets.QLabel(hcmgis_centerline_form)
        self.lblsurround.setObjectName("lblsurround")
        self.verticalLayout.addWidget(self.lblsurround)
        self.distance = QtWidgets.QSpinBox(hcmgis_centerline_form)
        self.distance.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.distance.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.distance.setMinimum(1)
        self.distance.setMaximum(1000)
        self.distance.setProperty("value", 2)
        self.distance.setObjectName("distance")
        self.verticalLayout.addWidget(self.distance)
        self.label = QtWidgets.QLabel(hcmgis_centerline_form)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_centerline_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_centerline_form)
        self.BtnApplyClose.accepted.connect(hcmgis_centerline_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_centerline_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_centerline_form)

    def retranslateUi(self, hcmgis_centerline_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_centerline_form.setWindowTitle(_translate("hcmgis_centerline_form", "Centerline in the gaps between polygons"))
        self.LblInput.setText(_translate("hcmgis_centerline_form", "Input Polygon (Ex: Block of Buildings)"))
        self.LblInput_2.setText(_translate("hcmgis_centerline_form", "Density (m)"))
        self.chksurround.setText(_translate("hcmgis_centerline_form", "Also create line surround the polygon"))
        self.lblsurround.setText(_translate("hcmgis_centerline_form", "Distance to the bounding box of polygon (m)"))
        self.label.setText(_translate("hcmgis_centerline_form", "(Notice: Output should be refined after running)"))

from qgsmaplayercombobox import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_centerline_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_centerline_form()
    ui.setupUi(hcmgis_centerline_form)
    hcmgis_centerline_form.show()
    sys.exit(app.exec_())

