#!/usr/bin/env python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------
#    hcmgisgis_dialogs - Dialog classes for hcmgis
#
#    begin                : 01/02/2018
#    copyright            : (c) 2018 by Quach Dong Thang
#    email                : quachdongthang@gmail.com
# --------------------------------------------------------
import csv
import math
import os.path
import operator
import sys

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .hcmgis_library import *

from qgis.gui import QgsMessageBar



sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")


from hcmgis_merge_form import *
from hcmgis_split_form import *
from hcmgis_checkvalidity_form import *
from hcmgis_fixgeometries_form import *
from hcmgis_reprojection_form import *

from hcmgis_font_convert_form import *
from hcmgis_split_field_form import *
from hcmgis_merge_field_form import *
from hcmgis_find_replace_form import *
from hcmgis_prefix_suffix_form import *
from hcmgis_medialaxis_form import *

global _Unicode, _TCVN3, _VNIWin, _KhongDau

# --------------------------------------------------------
#    hcmggis_merge - Merge layers to single shapefile
# --------------------------------------------------------
class hcmgis_medialaxis_dialog(QDialog, Ui_hcmgis_medialaxis_form):		
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
		self.CboField.setLayer (self.CboInput.currentLayer () )
		self.CboInput.activated.connect(self.update_field) 
		self.BtnOKCancel.accepted.connect(self.run)    
				
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )
	
				
	def run(self):             		
		layer = self.CboInput.currentLayer()
		selectedfield = self.CboField.currentText()
		density = self.spinBox.value()
		if layer.selectedFeatureCount()>0 and layer.selectedFeatureCount() <= 100:		
			message = hcmgis_medialaxis(self.iface,layer, selectedfield, density)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Skeleton/ Media Axis", message)						               
			else: return	
		else:
			#return u'Please select 1..100 features to create Skeleton/ Media Axis'		
			QMessageBox.information(None,  "Skeleton/ Media Axis",u'Please select 1..100 features to create Skeleton/ Media Axis!') 
		return
	
# --------------------------------------------------------
#    hcmggis_merge - Merge layers to single shapefile
# --------------------------------------------------------
class hcmgis_merge_dialog(QDialog, Ui_hcmgis_merge_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)

		self.browseoutfile.clicked.connect(self.browse_outfiles)
		self.buttonBox.accepted.connect(self.run)
		hcmgis_load_combo_box_with_vector_layers(self.iface, self.sourcelayers, True)
		self.sourcelayers.setDragDropMode(QAbstractItemView.InternalMove)
		self.outfilename.setText(hcmgis_temp_file_name("merge",".shp"))	

	def browse_outfiles(self):
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", 
		self.outfilename.displayText(), "Shapefile (*.shp)")
		if newname != None:
			self.outfilename.setText(newname)

	def run(self):
		layernames = []
		for x in range(0, self.sourcelayers.count()):
			if self.sourcelayers.item(x).isSelected():
				layernames.append(unicode(self.sourcelayers.item(x).text()))

		savename = unicode(self.outfilename.displayText()).strip()

		message = hcmgis_merge(self.iface, layernames, savename, 1)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Merge", message)

			

class hcmgis_checkvalidity_dialog(QDialog, Ui_hcmgis_checkvalidity_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
		self.BtnOKCancel.accepted.connect(self.run)

	def run(self):
		layer = self.CboInput.currentLayer()
		message = hcmgis_checkvalidity(self.iface, layer)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Check Validity", message)

			
class hcmgis_fixgeometries_dialog(QDialog, Ui_hcmgis_fixgeometries_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
		self.BtnOutput.clicked.connect(self.browse_outfiles)
		self.BtnOKCancel.accepted.connect(self.run)
		self.LinOutput.setText(hcmgis_temp_file_name("fixgeometries",".shp"))	

	def browse_outfiles(self):
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", 
		self.LinOutput.displayText(), "Shapefile (*.shp)")
		if newname != None:
			self.LinOutput.setText(newname)

	def run(self):
		layer = self.CboInput.currentLayer()
		savename = unicode(self.LinOutput.displayText()).strip()

		message = hcmgis_fixgeometries(self.iface, layer, savename)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Fix Geometries", message)

class hcmgis_reprojection_dialog(QDialog, Ui_hcmgis_reprojection_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
		self.BtnOutput.clicked.connect(self.browse_outfiles)
		self.BtnOKCancel.accepted.connect(self.run)
		self.LinOutput.setText(hcmgis_temp_file_name("reproject",".shp"))	
		self.crs.setCrs(QgsCoordinateReferenceSystem(4326))


	def browse_outfiles(self):
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", 
		self.LinOutput.displayText(), "Shapefile (*.shp)")
		if newname != None:
			self.LinOutput.setText(newname)

	def run(self):
		layer = self.CboInput.currentLayer()
		savename = unicode(self.LinOutput.displayText()).strip()
		destcrs = self.crs.crs()
		message = hcmgis_reprojection(self.iface, layer,destcrs, savename)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Reprojection", message)
			
			
class hcmgis_split_dialog(QDialog, Ui_hcmgis_split_form):	
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)	
		self.CboField.setLayer (self.CboInput.currentLayer () )
		self.CboInput.activated.connect(self.update_field)                
		self.BtnOKCancel.accepted.connect(self.run)
		self.LinOutputFolder.setText(os.getcwd())                                             
		self.BtnOutputFolder.clicked.connect(self.browse_outfiles)
	
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )	
	def browse_outfiles(self):
		newname = QFileDialog.getExistingDirectory(None, "Output Shapefile", self.LinOutputFolder.displayText())
		if newname != None:
			self.LinOutputFolder.setText(newname)
						
	def run(self):             		
		layer = self.CboInput.currentLayer()
		selectedfield = self.CboField.currentText()
		outdir = unicode(self.LinOutputFolder.displayText())
		if layer is None:
			return u'No selected layer!'
		elif selectedfield is None:
			return u'No selected field!'
		elif (not os.path.isdir(outdir)):
			return u'Không tồn tại đường dẫn!'
		else:
			message = hcmgis_split(self.iface,layer,selectedfield,outdir)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Split Layer", message)						               
			else: return		
		return


class hcmgis_font_convert_dialog(QDialog, Ui_hcmgis_font_convert_form):	
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
		self.ListFields.clear()
		self.update_fields()
		self.BtnBrowseOutput.clicked.connect(self.browse_outfiles)
		
		self.BtnOKCancel.accepted.connect(self.run)
		self.LinOutput.setText(hcmgis_temp_file_name("convert_font",".shp"))	
	
		self.CboInput.activated.connect(self.update_fields)
		
	def update_fields(self):               
		self.ListFields.clear()
		layer = self.CboInput.currentLayer()
		if layer != None and layer.type()  == QgsMapLayer.VectorLayer:                        
			for field in layer.fields():
				if field.type() in [QVariant.String]:
					self.ListFields.addItem(field.name()) # lists layer fields
			
               
	def browse_outfiles(self):
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", self.LinOutput.displayText(), "Shapefile (*.shp)")
		if newname != None:
			self.LinOutput.setText(newname)
				
	def run(self):             		
		input_layer = self.CboInput.currentLayer()
		output_layer = unicode(self.LinOutput.displayText()).strip()			
		sE = GetEncodeIndex(self.CboSourceFont.currentText())
		dE = GetEncodeIndex(self.CboDestFont.currentText())
		caseI = GetCaseIndex(self.CboOption.currentText())
		selectedfields = []
		selectedfeatureonly = self.ChkSelectedFeaturesOnly.isChecked()
		for i in list(self.ListFields.selectedItems()):
			selectedfields.append(str(i.text()))
		if len(selectedfields) > 0:
			message = hcmgis_convertfont(self.iface,input_layer, selectedfields, output_layer, sE, dE, caseI,selectedfeatureonly) 
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Convert Font", message)						               
		else: return

#---------------------------
# Split Fields
#----------------------------				
class hcmgis_split_field_dialog(QDialog, Ui_hcmgis_split_field_form):	
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)			
		self.CboField.setLayer (self.CboInput.currentLayer () )
		self.CboInput.activated.connect(self.update_field)                
		self.BtnOKCancel.accepted.connect(self.run)    
				
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )
			
	def run(self):             		
		layer = self.CboInput.currentLayer()
		char = self.CboChar.currentText()
		selectedfield = self.CboField.currentText()
		selectedfeatureonly = self.ChkSelectedFeaturesOnly.isChecked()
		message = hcmgis_split_field(self.iface,layer, selectedfield, char,selectedfeatureonly)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Split Fields", message)						               
		else: return		
		return

#------------------------------
# Merge Fields
#------------------------------			
class hcmgis_merge_field_dialog(QDialog, Ui_hcmgis_merge_field_form):	
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
		self.update_fields()
		self.BtnOKCancel.accepted.connect(self.run)	
		self.CboInput.activated.connect(self.update_fields)

	def update_fields(self):
		self.ListFields.clear()
		if self.CboInput.currentLayer() != None:                        
			layer = self.CboInput.currentLayer ()  # gets selected layer              
			for field in layer.fields():                               
				self.ListFields.addItem(field.name()) # lists layer fields             
				
	def run(self):             				
		layer = self.CboInput.currentLayer()
		char = self.CboChar.currentText()
		selectedfields = []
		selectedfeatureonly = self.ChkSelectedFeaturesOnly.isChecked()
		for i in list(self.ListFields.selectedItems()):
			selectedfields.append(str(i.text()))
		if len(selectedfields) > 0:
			message = hcmgis_merge_field(self.iface,layer, selectedfields, char,selectedfeatureonly)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Merge Fields", message)						               
		else: return
		return

		
# --------------------------------------------------------
#    hcmggis_find_replace - Find and Replace
# --------------------------------------------------------
class hcmgis_find_replace_dialog(QDialog, Ui_hcmgis_find_replace_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
		self.CboField.setLayer (self.CboInput.currentLayer () )
		self.BtnOKCancel.accepted.connect(self.run)
		self.CboInput.activated.connect(self.update_field)                
			
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )
				
	def run(self):             		
		layer = self.CboInput.currentLayer()
		find = self.LinFind.text()
		replace = self.LinReplace.text()
		selectedfield = self.CboField.currentText()
		selectedfeatureonly = self.ChkSelectedFeaturesOnly.isChecked()
		message = hcmgis_find_replace(self.iface,layer, selectedfield, find, replace,selectedfeatureonly)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Find and Replace", message)						               
		else: return		
		return
# --------------------------------------------------------
#    hcmggis_prefix_suffix - Prefix/ Suffix
# --------------------------------------------------------
class hcmgis_prefix_suffix_dialog(QDialog, Ui_hcmgis_prefix_suffix_form):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
		self.CboField.setLayer (self.CboInput.currentLayer () )
		self.BtnOKCancel.accepted.connect(self.run)              
		self.CboInput.activated.connect(self.update_field)                
			
	def update_field(self):                
		self.CboField.setLayer (self.CboInput.currentLayer () )
				
	def run(self):             		
		layer = self.CboInput.currentLayer()		
		selectedfield = self.CboField.currentText()
		prefix = self.LinPrefix.text()
		suffix = self.LinSuffix.text()
		charprefix = self.CboCharPrefix.currentText()
		charsuffix = self.CboCharSuffix.currentText()
		selectedfeatureonly = self.ChkSelectedFeaturesOnly.isChecked()
		message = hcmgis_prefix_suffix(self.iface,layer, selectedfield, prefix, charprefix, suffix, charsuffix, selectedfeatureonly)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Append prefix/ suffix", message)						               
		else: return		
		return	




def hcmgis_load_combo_box_with_vector_layers(qgis, combo_box, set_selected):
	
	combo_box.clear()

	for legend in QgsProject.instance().layerTreeRoot().findLayers():
		layer = QgsProject.instance().mapLayer(legend.layerId())
		if layer.type() == QgsMapLayer.VectorLayer:
			combo_box.addItem(layer.name())

	#for name, layer in QgsProject.instance().mapLayers().items():
	#	if layer.type() == QgsMapLayer.VectorLayer:
	#		combo_box.addItem(layer.name())


	# set_selected can be boolean "True" to use current selection in layer pane...

	if (type(set_selected) == bool):
		# for index, layer in enumerate(qgis.legendInterface().selectedLayers()):
		for index, layer in enumerate(qgis.layerTreeView().selectedLayers()):
			if (type(combo_box) == QComboBox):
				combo_index = combo_box.findText(layer.name())
				if combo_index >= 0:
					combo_box.setCurrentIndex(combo_index)
					break;

			elif (type(combo_box) == QListWidget):
				for item in combo_box.findItems(layer.name(), Qt.MatchExactly):
					item.setSelected(1)

	# ...or set_selected can be the name of a layer to select
	else:
		if (type(combo_box) == QComboBox):
			combo_index = combo_box.findText(set_selected)
			if combo_index >= 0:
				combo_box.setCurrentIndex(combo_index)
				return;

		elif (type(combo_box) == QListWidget):
			for item in combo_box.findItems(set_selected):
				combo_box.setCurrentItem(item)

	

def hcmgis_temp_file_name(temp, suffix):
	preferred = os.getcwd() + temp + suffix
	if not os.path.isfile(preferred):
		return preferred

	for x in range(2, 10):
		name = os.getcwd() + temp + unicode(x) + suffix
		if not os.path.isfile(name):
			return name

	return preferred
