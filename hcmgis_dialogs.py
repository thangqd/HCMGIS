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

from hcmgis_opendata_form import *
from hcmgis_merge_form import *
from hcmgis_split_form import *

from hcmgis_font_convert_form import *
from hcmgis_split_field_form import *
from hcmgis_merge_field_form import *
from hcmgis_medialaxis_form import *
from hcmgis_centerline_form import *
from hcmgis_closestpair_form import *
from hcmgis_lec_form import *


global _Unicode, _TCVN3, _VNIWin, _KhongDau

# --------------------------------------------------------
#    hcmggis_merge - Merge layers to single shapefile
# --------------------------------------------------------
class hcmgis_opendata_dialog(QDialog, Ui_hcmgis_opendata_form):	
	def __init__(self, iface):		
		from owslib.wfs import WebFeatureService                
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		self.buttonBox.accepted.connect(self.run)
		self.BtnOutputFolder.clicked.connect(self.browse_outfile)	
		self.LinOutputFolder.setText(os.getcwd())                                             
		self.ChkSaveShapefile.stateChanged.connect(self.toggleCheckBox)
		self.readwfs()
		
	def browse_outfile(self):
		newname = QFileDialog.getExistingDirectory(None, "Output Shapefiles",self.LinOutputFolder.displayText())

		if newname != None:
			self.LinOutputFolder.setText(newname)
                	
	def toggleCheckBox(self,state):
		if state > 0:
			self.LinOutputFolder.setEnabled(True)
			self.BtnOutputFolder.setEnabled(True)
		else:
			self.LinOutputFolder.setEnabled(False)
			self.BtnOutputFolder.setEnabled(False)	   
	
	def readwfs(self):
		opendata_url = "https://opendata.hcmgis.vn/geoserver/ows?"
		import qgis.utils
		from owslib.wfs import WebFeatureService
		from PyQt5.QtWidgets import QProgressBar
		from qgis.gui import QgsMessageBar

		progressMessageBar = qgis.utils.iface.messageBar()
		progress = QProgressBar()
		#Maximum is set to 100, making it easy to work with percentage of completion
		progress.setMaximum(100) 
		#pass the progress bar to the message Bar
		progressMessageBar.pushWidget(progress)                
		# try:
		self.sourcelayers.clear()			
		wfs = WebFeatureService(url=opendata_url, version='1.0.0')
		if wfs.contents is not None:
			count =  len (list(wfs.contents))
			ii = 0
			for i in list(wfs.contents):  
				self.sourcelayers.addItem(i)                         
				ii+=1
				percent = (ii/float(count)) * 100
				progress.setValue(percent)                
			# except Exception:
				# QMessageBox.warning(None, "WFS ERROR",u'OpenData Reading Error') 
		else: return				
		qgis.utils.iface.messageBar().clearWidgets()  
	
	def run(self):
		#from qgis.core import *
		import qgis.utils
		from owslib.wfs import WebFeatureService
		from PyQt5.QtWidgets import QProgressBar

		from qgis.gui import QgsMessageBar
		opendata_url = "https://opendata.hcmgis.vn/geoserver/ows?"


		outdir = unicode(self.LinOutputFolder.displayText())
		layernames = []		
		
		for x in range(0, self.sourcelayers.count()):
			if self.sourcelayers.item(x).isSelected():
				layernames.append(unicode(self.sourcelayers.item(x).text()))
		for i in layernames:            
			#uri = opendata_url + "service=WFS&version=1.0.0&request=GetFeature&srsname=EPSG:4326&typename="+ str(i)
			uri = opendata_url + "service=WFS&version=1.0.0&request=GetFeature&srsname=EPSG:4326&typename="+ str(i)				  
			if (not self.ChkSaveShapefile.isChecked()):
				qgis.utils.iface.addVectorLayer(uri, str(i),"WFS")
			else:                      
				if (not os.path.isdir(outdir)):
					QMessageBox.critical(self.iface.mainWindow(), "WFS", u"Invalid Output Folder: " + unicode(outdir))
					return
				else:		  
					try:
						layer = QgsVectorLayer( uri, str(i), "WFS" )
						filename = outdir + "\\"+ str(i).replace(":","_") + ".shp"                                        
						#QgsVectorFileWriter.writeAsVectorFormat( layer,filename,"UTF-8",QgsCoordinateReferenceSystem(4326),"ESRI Shapefile" )	
						QgsVectorFileWriter.writeAsVectorFormat( layer,filename,"UTF-8",layer.crs(),"ESRI Shapefile" )						
						qgis.utils.iface.addVectorLayer(filename, str(i).replace(":","_"), "ogr")						
					except:
						#if (error != QgsVectorFileWriter.NoError):
						QMessageBox.critical(self.iface.mainWindow(), "WFS", u"Shapfiles Saving Error")
						qgis.utils.iface.addVectorLayer(uri, str(i),"WFS")
		
		MessageBar = qgis.utils.iface.messageBar()
		MessageBar.pushMessage(u"Complete Downloading " + unicode(len(layernames)) +u" OpenData Layers", 0, 3)        
		return			

		
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
		if layer is None:
			return u'No selected layers!'  
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

class hcmgis_centerline_dialog(QDialog, Ui_hcmgis_centerline_form):		
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
		self.BtnOKCancel.accepted.connect(self.run) 
		self.chksurround.checked = False
		self.lblsurround.setEnabled(False)
		self.distance.setEnabled(False)			
		self.chksurround.stateChanged.connect(self.toggleSurround)
		
	def toggleSurround(self,state):
		if state > 0:
			self.lblsurround.setEnabled(True)
			self.distance.setEnabled(True)
		else:
			self.lblsurround.setEnabled(False)
			self.distance.setEnabled(False)	
			
	def run(self):             		
		layer = self.CboInput.currentLayer()
		if layer is None:
			return u'No selected layers!'  
		density = self.spinBox.value()
		chksurround = self.chksurround.isChecked() 
		distance = self.distance.value()
		if layer.selectedFeatureCount()>0:		
			message = hcmgis_centerline(self.iface,layer,density,chksurround,distance)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Centerline in Polygon's Gaps", message)						               
			else: return	
		else:
			#return u'Please select at least 1 feature to create centerline		
			QMessageBox.information(None,  "Centerline",u'Please select at least 1 feature to create Centerline!') 
		return
		
# --------------------------------------------------------
#   Finding closest pair of Points
# --------------------------------------------------------			
class hcmgis_closestpair_dialog(QDialog, Ui_hcmgis_closestpair_form):		
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
		self.CboField.setLayer (self.CboInput.currentLayer () )		
		self.CboInput.activated.connect(self.update_field)
		self.BtnOKCancel.accepted.connect(self.run) 
           
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )	
		
	def run(self):             		
		layer = self.CboInput.currentLayer()
		field = self.CboField.currentText()
		message = hcmgis_closestpair(self.iface,layer,field)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Closest/ farthest pair of Points", message)						               
		else: return			
		return

# --------------------------------------------------------
#   Finding largest empty circle
# --------------------------------------------------------			
class hcmgis_lec_dialog(QDialog, Ui_hcmgis_lec_form):		
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.browseoutfile.clicked.connect(self.browse_outfiles)
		self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
		self.CboInput.activated.connect(self.update_field)         
		self.BtnOKCancel.accepted.connect(self.run) 
		self.outfilename.setText(hcmgis_temp_file_name("circle",".shp"))	
          
	
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )	

	def browse_outfiles(self):
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", 
			self.outfilename.displayText(), "Shapefile (*.shp)")

		if newname and newname[0]:
			self.outfilename.setText(newname[0])

	def run(self):             		
		layer = self.CboInput.currentLayer()
		selectedfield = self.CboField.currentText()
		savename = unicode(self.outfilename.displayText()).strip()

		if layer is None:
			return u'No selected point layer!'		
		else:
			message = hcmgis_lec(self.iface,layer, selectedfield, savename)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Largest Empty Circle", message)						               
			else: return		
		return
	
# --------------------------------------------------------
#   hcmggis_merge - Merge layers to single shapefile
#	Reference: mmqgis
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

		if newname and newname[0]:
			self.outfilename.setText(newname[0])
			
	def run(self):
		layernames = []
		for x in range(0, self.sourcelayers.count()):
			if self.sourcelayers.item(x).isSelected():
				layernames.append(unicode(self.sourcelayers.item(x).text()))

		savename = unicode(self.outfilename.displayText()).strip()

		message = hcmgis_merge(self.iface, layernames, savename, 1)
		if message != None:
			QMessageBox.critical(self.iface.mainWindow(), "Merge", message)

			

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
		elif ((selectedfield is None) or (selectedfield == '')):
			return u'No selected field!'
		elif (not os.path.isdir(outdir)):
			return u'Invalid Folder!'
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
		newname = QFileDialog.getSaveFileName(None, "Output Shapefile", 
			self.LinOutput.displayText(), "Shapefile (*.shp)")

		if newname and newname[0]:
			self.LinOutput.setText(newname[0])	
				
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
