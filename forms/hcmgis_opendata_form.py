# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hcmgis_opendata_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_hcmgis_opendata_form(object):
    def setupUi(self, hcmgis_opendata_form):
        hcmgis_opendata_form.setObjectName("hcmgis_opendata_form")
        hcmgis_opendata_form.setWindowModality(QtCore.Qt.NonModal)
        hcmgis_opendata_form.setEnabled(True)
        hcmgis_opendata_form.resize(593, 619)
        hcmgis_opendata_form.setMouseTracking(False)
        self.gridLayout_2 = QtWidgets.QGridLayout(hcmgis_opendata_form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.BtnApplyClose = QtWidgets.QDialogButtonBox(hcmgis_opendata_form)
        self.BtnApplyClose.setOrientation(QtCore.Qt.Horizontal)
        self.BtnApplyClose.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.BtnApplyClose.setObjectName("BtnApplyClose")
        self.gridLayout_2.addWidget(self.BtnApplyClose, 10, 0, 1, 2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.cboFormat = QtWidgets.QComboBox(hcmgis_opendata_form)
        self.cboFormat.setEnabled(False)
        self.cboFormat.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cboFormat.setObjectName("cboFormat")
        self.gridLayout.addWidget(self.cboFormat, 14, 2, 1, 1)
        self.LblTitle = QtWidgets.QLabel(hcmgis_opendata_form)
        self.LblTitle.setObjectName("LblTitle")
        self.gridLayout.addWidget(self.LblTitle, 5, 0, 1, 1)
        self.BtnOutputFolder = QtWidgets.QPushButton(hcmgis_opendata_form)
        self.BtnOutputFolder.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BtnOutputFolder.sizePolicy().hasHeightForWidth())
        self.BtnOutputFolder.setSizePolicy(sizePolicy)
        self.BtnOutputFolder.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.BtnOutputFolder.setFont(font)
        self.BtnOutputFolder.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.BtnOutputFolder.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.BtnOutputFolder.setObjectName("BtnOutputFolder")
        self.gridLayout.addWidget(self.BtnOutputFolder, 13, 2, 1, 1)
        self.cboServerType = QtWidgets.QComboBox(hcmgis_opendata_form)
        self.cboServerType.setObjectName("cboServerType")
        self.gridLayout.addWidget(self.cboServerType, 0, 1, 1, 2)
        self.LblWFSLayers = QtWidgets.QLabel(hcmgis_opendata_form)
        self.LblWFSLayers.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LblWFSLayers.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.LblWFSLayers.setObjectName("LblWFSLayers")
        self.gridLayout.addWidget(self.LblWFSLayers, 7, 0, 1, 3)
        self.TblWFSLayers = QtWidgets.QTableWidget(hcmgis_opendata_form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TblWFSLayers.sizePolicy().hasHeightForWidth())
        self.TblWFSLayers.setSizePolicy(sizePolicy)
        self.TblWFSLayers.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.TblWFSLayers.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.TblWFSLayers.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.TblWFSLayers.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.TblWFSLayers.setObjectName("TblWFSLayers")
        self.TblWFSLayers.setColumnCount(2)
        self.TblWFSLayers.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TblWFSLayers.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TblWFSLayers.setHorizontalHeaderItem(1, item)
        self.TblWFSLayers.horizontalHeader().setCascadingSectionResizes(False)
        self.TblWFSLayers.horizontalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.TblWFSLayers, 11, 0, 1, 3)
        self.LblServerType = QtWidgets.QLabel(hcmgis_opendata_form)
        self.LblServerType.setObjectName("LblServerType")
        self.gridLayout.addWidget(self.LblServerType, 0, 0, 1, 1)
        self.LblStatus = QtWidgets.QLabel(hcmgis_opendata_form)
        self.LblStatus.setText("")
        self.LblStatus.setObjectName("LblStatus")
        self.gridLayout.addWidget(self.LblStatus, 15, 0, 1, 3)
        self.TxtAbstract = QtWidgets.QPlainTextEdit(hcmgis_opendata_form)
        self.TxtAbstract.setMaximumSize(QtCore.QSize(16777215, 80))
        self.TxtAbstract.setFocusPolicy(QtCore.Qt.NoFocus)
        self.TxtAbstract.setReadOnly(True)
        self.TxtAbstract.setObjectName("TxtAbstract")
        self.gridLayout.addWidget(self.TxtAbstract, 6, 1, 1, 2)
        self.LblFormat = QtWidgets.QLabel(hcmgis_opendata_form)
        self.LblFormat.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.LblFormat.setObjectName("LblFormat")
        self.gridLayout.addWidget(self.LblFormat, 14, 0, 1, 2)
        self.TxtTitle = QtWidgets.QPlainTextEdit(hcmgis_opendata_form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TxtTitle.sizePolicy().hasHeightForWidth())
        self.TxtTitle.setSizePolicy(sizePolicy)
        self.TxtTitle.setMaximumSize(QtCore.QSize(16777215, 80))
        self.TxtTitle.setFocusPolicy(QtCore.Qt.NoFocus)
        self.TxtTitle.setReadOnly(True)
        self.TxtTitle.setObjectName("TxtTitle")
        self.gridLayout.addWidget(self.TxtTitle, 6, 0, 1, 1)
        self.Filter = QgsFilterLineEdit(hcmgis_opendata_form)
        self.Filter.setToolTip("")
        self.Filter.setShowSearchIcon(True)
        self.Filter.setShowSpinner(False)
        self.Filter.setProperty("qgisRelation", "")
        self.Filter.setObjectName("Filter")
        self.gridLayout.addWidget(self.Filter, 8, 0, 1, 3)
        self.label = QtWidgets.QLabel(hcmgis_opendata_form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.ChkSaveShapefile = QtWidgets.QCheckBox(hcmgis_opendata_form)
        self.ChkSaveShapefile.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.ChkSaveShapefile.setObjectName("ChkSaveShapefile")
        self.gridLayout.addWidget(self.ChkSaveShapefile, 12, 0, 1, 2)
        self.lblAbstract = QtWidgets.QLabel(hcmgis_opendata_form)
        self.lblAbstract.setObjectName("lblAbstract")
        self.gridLayout.addWidget(self.lblAbstract, 5, 1, 1, 2)
        self.LinOutputFolder = QtWidgets.QLineEdit(hcmgis_opendata_form)
        self.LinOutputFolder.setEnabled(False)
        self.LinOutputFolder.setMouseTracking(True)
        self.LinOutputFolder.setFocusPolicy(QtCore.Qt.NoFocus)
        self.LinOutputFolder.setAcceptDrops(False)
        self.LinOutputFolder.setText("")
        self.LinOutputFolder.setReadOnly(True)
        self.LinOutputFolder.setObjectName("LinOutputFolder")
        self.gridLayout.addWidget(self.LinOutputFolder, 13, 0, 1, 2)
        self.cboServerName = QtWidgets.QComboBox(hcmgis_opendata_form)
        self.cboServerName.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.cboServerName.setObjectName("cboServerName")
        self.gridLayout.addWidget(self.cboServerName, 1, 1, 1, 2)
        self.status = QtWidgets.QProgressBar(hcmgis_opendata_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.gridLayout.addWidget(self.status, 16, 0, 1, 3)
        self.TxtURL = QtWidgets.QLineEdit(hcmgis_opendata_form)
        self.TxtURL.setReadOnly(False)
        self.TxtURL.setObjectName("TxtURL")
        self.gridLayout.addWidget(self.TxtURL, 4, 0, 1, 2)
        self.BtnConnect = QtWidgets.QPushButton(hcmgis_opendata_form)
        self.BtnConnect.setObjectName("BtnConnect")
        self.gridLayout.addWidget(self.BtnConnect, 4, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(hcmgis_opendata_form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 3)
        self.gridLayout_2.addLayout(self.gridLayout, 9, 0, 1, 2)

        self.retranslateUi(hcmgis_opendata_form)
        self.BtnApplyClose.accepted.connect(hcmgis_opendata_form.accept)
        self.BtnApplyClose.rejected.connect(hcmgis_opendata_form.reject)
        QtCore.QMetaObject.connectSlotsByName(hcmgis_opendata_form)

    def retranslateUi(self, hcmgis_opendata_form):
        _translate = QtCore.QCoreApplication.translate
        hcmgis_opendata_form.setWindowTitle(_translate("hcmgis_opendata_form", "Download OpenData"))
        self.LblTitle.setText(_translate("hcmgis_opendata_form", "Title"))
        self.BtnOutputFolder.setText(_translate("hcmgis_opendata_form", "Browse..."))
        self.LblWFSLayers.setText(_translate("hcmgis_opendata_form", "WFS layers"))
        self.TblWFSLayers.setToolTip(_translate("hcmgis_opendata_form", "Double Click to add selected Layers"))
        self.TblWFSLayers.setSortingEnabled(True)
        item = self.TblWFSLayers.horizontalHeaderItem(0)
        item.setText(_translate("hcmgis_opendata_form", "Name"))
        item = self.TblWFSLayers.horizontalHeaderItem(1)
        item.setText(_translate("hcmgis_opendata_form", "Title"))
        self.LblServerType.setText(_translate("hcmgis_opendata_form", "Service Type"))
        self.LblFormat.setText(_translate("hcmgis_opendata_form", "Format"))
        self.Filter.setPlaceholderText(_translate("hcmgis_opendata_form", "Search"))
        self.label.setText(_translate("hcmgis_opendata_form", "Service Provider"))
        self.ChkSaveShapefile.setText(_translate("hcmgis_opendata_form", "Save layers to disk"))
        self.lblAbstract.setText(_translate("hcmgis_opendata_form", "Abstract"))
        self.BtnConnect.setText(_translate("hcmgis_opendata_form", "Connect"))
        self.label_2.setText(_translate("hcmgis_opendata_form", "Server URL:"))
from qgsfilterlineedit import QgsFilterLineEdit


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    hcmgis_opendata_form = QtWidgets.QDialog()
    ui = Ui_hcmgis_opendata_form()
    ui.setupUi(hcmgis_opendata_form)
    hcmgis_opendata_form.show()
    sys.exit(app.exec_())
