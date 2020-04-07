# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_checkvalidity_form.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hcmgis_checkvalidity_form(object):
    def setupUi(self, hcmgis_checkvalidity_form):
        hcmgis_checkvalidity_form.setObjectName("hcmgis_checkvalidity_form")
        hcmgis_checkvalidity_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_checkvalidity_form.setEnabled(True)
        hcmgis_checkvalidity_form.resize(341, 118)
        hcmgis_checkvalidity_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_checkvalidity_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LblInput = QtWidgets.QLabel(hcmgis_checkvalidity_form)
        self.LblInput.setObjectName("LblInput")
        self.verticalLayout.addWidget(self.LblInput)
        self.CboInput = QgsMapLayerComboBox(hcmgis_checkvalidity_form)
        self.CboInput.setObjectName("CboInput")
        self.verticalLayout.addWidget(self.CboInput)
        self.BtnOKCancel = QtWidgets.QDialogButtonBox(hcmgis_checkvalidity_form)
        self.BtnOKCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BtnOKCancel.setObjectName("BtnOKCancel")
        self.verticalLayout.addWidget(self.BtnOKCancel)

        self.retranslateUi(hcmgis_checkvalidity_form)
        self.BtnOKCancel.accepted.connect(hcmgis_checkvalidity_form.accept)
        self.BtnOKCancel.rejected.connect(hcmgis_checkvalidity_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_checkvalidity_form)

    def retranslateUi(self, hcmgis_checkvalidity_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_checkvalidity_form.setWindowTitle(_translate("hcmgis_checkvalidity_form", "Check Validity"))
        self.LblInput.setText(_translate("hcmgis_checkvalidity_form", "Input Layer"))

from qgis.gui import QgsMapLayerComboBox

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_checkvalidity_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_checkvalidity_form()
    ui.setupUi(hcmgis_checkvalidity_form)
    hcmgis_checkvalidity_form.show()
    sys.exit(app.exec_())

