# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_mapbox_form.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_mapbox_form(object):
    def setupUi(self, hcmgis_mapbox_form):
        hcmgis_mapbox_form.setObjectName("hcmgis_mapbox_form")
        hcmgis_mapbox_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_mapbox_form.setEnabled(True)
        hcmgis_mapbox_form.resize(584, 266)
        hcmgis_mapbox_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_mapbox_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.LblMapboxStyle = QtWidgets.QLabel(hcmgis_mapbox_form)
        self.LblMapboxStyle.setObjectName("LblMapboxStyle")
        self.gridLayout.addWidget(self.LblMapboxStyle, 1, 0, 1, 1)
        self.radProvinces = QtWidgets.QRadioButton(hcmgis_mapbox_form)
        self.radProvinces.setChecked(True)
        self.radProvinces.setObjectName("radProvinces")
        self.gridLayout.addWidget(self.radProvinces, 0, 0, 1, 1)
        self.CboStyleType = QtWidgets.QComboBox(hcmgis_mapbox_form)
        self.CboStyleType.setObjectName("CboStyleType")
        self.CboStyleType.addItem("")
        self.CboStyleType.addItem("")
        self.gridLayout.addWidget(self.CboStyleType, 0, 1, 1, 3)
        self.LblSignUp = QtWidgets.QLabel(hcmgis_mapbox_form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.LblSignUp.setFont(font)
        self.LblSignUp.setObjectName("LblSignUp")
        self.gridLayout.addWidget(self.LblSignUp, 3, 0, 1, 4)
        self.CboMapboxStyle = QtWidgets.QComboBox(hcmgis_mapbox_form)
        self.CboMapboxStyle.setObjectName("CboMapboxStyle")
        self.CboMapboxStyle.addItem("")
        self.CboMapboxStyle.addItem("")
        self.CboMapboxStyle.addItem("")
        self.CboMapboxStyle.addItem("")
        self.CboMapboxStyle.addItem("")
        self.CboMapboxStyle.addItem("")
        self.gridLayout.addWidget(self.CboMapboxStyle, 1, 1, 1, 3)
        self.TxtStyleWMTS = QtWidgets.QTextEdit(hcmgis_mapbox_form)
        self.TxtStyleWMTS.setObjectName("TxtStyleWMTS")
        self.gridLayout.addWidget(self.TxtStyleWMTS, 4, 1, 1, 1)
        self.LblStyleWMTS = QtWidgets.QLabel(hcmgis_mapbox_form)
        self.LblStyleWMTS.setObjectName("LblStyleWMTS")
        self.gridLayout.addWidget(self.LblStyleWMTS, 4, 0, 1, 1)
        self.TxtAccessToken = QtWidgets.QLabel(hcmgis_mapbox_form)
        self.TxtAccessToken.setObjectName("TxtAccessToken")
        self.gridLayout.addWidget(self.TxtAccessToken, 2, 0, 1, 1)
        self.LinAccessToken = QtWidgets.QLineEdit(hcmgis_mapbox_form)
        self.LinAccessToken.setObjectName("LinAccessToken")
        self.gridLayout.addWidget(self.LinAccessToken, 2, 1, 1, 3)
        self.LblView = QtWidgets.QLabel(hcmgis_mapbox_form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.LblView.setFont(font)
        self.LblView.setObjectName("LblView")
        self.gridLayout.addWidget(self.LblView, 4, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_mapbox_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_mapbox_form)
        self.BtnApplyClose.accepted.connect(hcmgis_mapbox_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_mapbox_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_mapbox_form)

    def retranslateUi(self, hcmgis_mapbox_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_mapbox_form.setWindowTitle(_translate("hcmgis_mapbox_form", "Mapbox WMTS"))
        self.LblMapboxStyle.setText(_translate("hcmgis_mapbox_form", "Mapbox Style"))
        self.radProvinces.setText(_translate("hcmgis_mapbox_form", "Style Type"))
        self.CboStyleType.setItemText(0, _translate("hcmgis_mapbox_form", "Default Mapbox Style"))
        self.CboStyleType.setItemText(1, _translate("hcmgis_mapbox_form", "User\'s Custom Style"))
        self.LblSignUp.setText(_translate("hcmgis_mapbox_form", "Don\'t have Access Token? Click to sign up for a Mapbox Account!"))
        self.CboMapboxStyle.setItemText(0, _translate("hcmgis_mapbox_form", "streets-v11"))
        self.CboMapboxStyle.setItemText(1, _translate("hcmgis_mapbox_form", "outdoors-v11"))
        self.CboMapboxStyle.setItemText(2, _translate("hcmgis_mapbox_form", "light-v10"))
        self.CboMapboxStyle.setItemText(3, _translate("hcmgis_mapbox_form", "dark-v10"))
        self.CboMapboxStyle.setItemText(4, _translate("hcmgis_mapbox_form", "satellite-v9"))
        self.CboMapboxStyle.setItemText(5, _translate("hcmgis_mapbox_form", "satellite-streets-v11"))
        self.LblStyleWMTS.setText(_translate("hcmgis_mapbox_form", "Style WMTS"))
        self.TxtAccessToken.setText(_translate("hcmgis_mapbox_form", "Access Token"))
        self.LblView.setText(_translate("hcmgis_mapbox_form", "View on Mapbox"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_mapbox_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_mapbox_form()
    ui.setupUi(hcmgis_mapbox_form)
    hcmgis_mapbox_form.show()
    sys.exit(app.exec_())
