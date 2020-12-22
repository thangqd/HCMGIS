# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_medialaxis_form.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_medialaxis_form(object):
    def setupUi(self, hcmgis_medialaxis_form):
        hcmgis_medialaxis_form.setObjectName("hcmgis_medialaxis_form")
        hcmgis_medialaxis_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_medialaxis_form.setEnabled(True)
        hcmgis_medialaxis_form.resize(479, 343)
        hcmgis_medialaxis_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_medialaxis_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.status = QtWidgets.QProgressBar(hcmgis_medialaxis_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.gridLayout.addWidget(self.status, 11, 0, 1, 2)
        self.LblOutput = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblOutput.setObjectName("LblOutput")
        self.gridLayout.addWidget(self.LblOutput, 7, 0, 1, 2)
        self.LblInput_2 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_2.setObjectName("LblInput_2")
        self.gridLayout.addWidget(self.LblInput_2, 4, 0, 1, 2)
        self.label = QtWidgets.QLabel(hcmgis_medialaxis_form)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 6, 0, 1, 2)
        self.LblStatus = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.gridLayout.addWidget(self.LblStatus, 10, 0, 1, 2)
        self.LblInput = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput.setObjectName("LblInput")
        self.gridLayout.addWidget(self.LblInput, 0, 0, 1, 2)
        self.LblInput_3 = QtWidgets.QLabel(hcmgis_medialaxis_form)
        self.LblInput_3.setObjectName("LblInput_3")
        self.gridLayout.addWidget(self.LblInput_3, 2, 0, 1, 2)
        self.CboInput = QgsMapLayerComboBox(hcmgis_medialaxis_form)
        self.CboInput.setObjectName("CboInput")
        self.gridLayout.addWidget(self.CboInput, 1, 0, 1, 2)
        self.spinBox = QtWidgets.QSpinBox(hcmgis_medialaxis_form)
        self.spinBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.spinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(10)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 5, 0, 1, 2)
        self.CboField = QgsFieldComboBox(hcmgis_medialaxis_form)
        self.CboField.setObjectName("CboField")
        self.gridLayout.addWidget(self.CboField, 3, 0, 1, 2)
        self.output_file_name = QgsFileWidget(hcmgis_medialaxis_form)
        self.output_file_name.setObjectName("output_file_name")
        self.gridLayout.addWidget(self.output_file_name, 8, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_medialaxis_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_medialaxis_form)
        self.BtnApplyClose.accepted.connect(hcmgis_medialaxis_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_medialaxis_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_medialaxis_form)

    def retranslateUi(self, hcmgis_medialaxis_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_medialaxis_form.setWindowTitle(_translate("hcmgis_medialaxis_form", "Skeleton/Medial Axis"))
        self.LblOutput.setText(_translate("hcmgis_medialaxis_form", "Output"))
        self.LblInput_2.setText(_translate("hcmgis_medialaxis_form", "Density (m)"))
        self.label.setText(_translate("hcmgis_medialaxis_form", "(Notice: Output should be refined after running)"))
        self.LblInput.setText(_translate("hcmgis_medialaxis_form", "Input Polygon (1..100 selected features limit!) - Layer must be in Projected CRS"))
        self.LblInput_3.setText(_translate("hcmgis_medialaxis_form", "Unique field"))
from qgsfieldcombobox import QgsFieldComboBox
from qgsfilewidget import QgsFileWidget
from qgsmaplayercombobox import QgsMapLayerComboBox


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_medialaxis_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_medialaxis_form()
    ui.setupUi(hcmgis_medialaxis_form)
    hcmgis_medialaxis_form.show()
    sys.exit(app.exec_())
