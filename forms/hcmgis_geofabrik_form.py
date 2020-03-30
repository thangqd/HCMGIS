# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_geofabrik_form.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_geofabrik_form(object):
    def setupUi(self, hcmgis_geofabrik_form):
        hcmgis_geofabrik_form.setObjectName("hcmgis_geofabrik_form")
        hcmgis_geofabrik_form.setWindowModality(QtCore.Qt.ApplicationModal)
        hcmgis_geofabrik_form.setEnabled(True)
        hcmgis_geofabrik_form.resize(521, 266)
        hcmgis_geofabrik_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(hcmgis_geofabrik_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(hcmgis_geofabrik_form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(hcmgis_geofabrik_form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 6, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(hcmgis_geofabrik_form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.cboRegion = QtWidgets.QComboBox(hcmgis_geofabrik_form)
        self.cboRegion.setObjectName("cboRegion")
        self.gridLayout.addWidget(self.cboRegion, 3, 1, 1, 1)
        self.cboCountry = QtWidgets.QComboBox(hcmgis_geofabrik_form)
        self.cboCountry.setObjectName("cboCountry")
        self.gridLayout.addWidget(self.cboCountry, 6, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(hcmgis_geofabrik_form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 1)
        self.cboProvince = QtWidgets.QComboBox(hcmgis_geofabrik_form)
        self.cboProvince.setObjectName("cboProvince")
        self.gridLayout.addWidget(self.cboProvince, 7, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_geofabrik_form)
        self.LinOutputFolder.setReadOnly(True)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.gridLayout_2.addWidget(self.LinOutputFolder, 1, 0, 1, 1)
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_geofabrik_form)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")
        self.gridLayout_2.addWidget(self.BtnOutputFolder, 1, 1, 1, 1)
        self.Label = QtWidgets.QLabel(hcmgis_geofabrik_form)
        self.Label.setObjectName("Label")
        self.gridLayout_2.addWidget(self.Label, 0, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_geofabrik_form)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.verticalLayout.addWidget(self.BtnApplyClose)

        self.retranslateUi(hcmgis_geofabrik_form)
        self.BtnApplyClose.accepted.connect(hcmgis_geofabrik_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_geofabrik_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_geofabrik_form)

    def retranslateUi(self, hcmgis_geofabrik_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_geofabrik_form.setWindowTitle(_translate("hcmgis_geofabrik_form", "Download OSM Data by Country"))
        self.label.setText(_translate("hcmgis_geofabrik_form", "Download OSM Data by Country from Geofabrik"))
        self.label_3.setText(_translate("hcmgis_geofabrik_form", "Select Country"))
        self.label_2.setText(_translate("hcmgis_geofabrik_form", "Select Region"))
        self.label_4.setText(_translate("hcmgis_geofabrik_form", "Slect State/ Province"))
        self.BtnOutputFolder.setText(_translate("hcmgis_geofabrik_form", "Browse..."))
        self.Label.setText(_translate("hcmgis_geofabrik_form", "Select folder to save shapefile"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_geofabrik_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_geofabrik_form()
    ui.setupUi(hcmgis_geofabrik_form)
    hcmgis_geofabrik_form.show()
    sys.exit(app.exec_())
