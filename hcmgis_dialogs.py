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
from hcmgis_customprojections_form import *
from hcmgis_csv2shp_form import *

global _Unicode, _TCVN3, _VNIWin, _KhongDau
# --------------------------------------------------------
#    HCMGIS Opendata
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
		try:
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
			else: return				
		except Exception:
			QMessageBox.warning(None, "WFS ERROR",u'OpenData Reading Error')			
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

# --------------------------------------------------------
#    VN-2000 Projections
# --------------------------------------------------------
class hcmgis_customprojections_dialog(QDialog, Ui_hcmgis_customprojections_form):		

	def __init__(self, iface):		
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)
		#self.BtnOKCancel.accepted.connect(self.run)
		self.cboProvinces.setCurrentIndex(-1)
		self.cboKTT.setCurrentIndex(-1)
		self.cboZone.setCurrentIndex(0)
		self.cboKTT.setEnabled(False)
		self.cboZone.setEnabled(False)
		
		self.rad3do.toggled.connect(self.togglerad3do)
		self.radcustom.toggled.connect(self.toggleradcustom)
		self.cboZone.currentIndexChanged.connect(self.zonechange)
	
		self.cboProvinces.currentIndexChanged.connect(self.update_proj)
		self.cboFormat.currentIndexChanged.connect(self.update_proj)
		self.cboParameters.currentIndexChanged.connect(self.update_proj)
		self.cboKTT.currentTextChanged.connect(self.update_proj)



	def update_proj(self):		
		self.txtProjections.clear()
		provinces = ['Lai Châu','Sơn La','Kiên Giang','Cà Mau','Lào Cai','Yên Bái','Nghệ An',
				'Phú Thọ','An Giang', 'Thanh Hoá', 'Vĩnh Phúc', 'Hà Tây', 'Đồng Tháp','Cần Thơ',
				'Bạc Liêu','Hà Nội','Ninh Bình','Hà Nam','Hà Giang','Hải Dương','Hà Tĩnh','Bắc Ninh','Hưng Yên',
				'Thái Bình','Nam Định','Tây Ninh','Vĩnh Long','Sóc Trăng','Trà Vinh',
				'Cao Bằng','Long An','Tiền Giang','Bến Tre','Hải Phòng','TP.HCM','Bình Dương','Tuyên Quang','Hoà Bình',
				'Quảng Bình','Quảng Trị','Bình Phước','Bắc Kạn','Thái Nguyên','Bắc Giang','Thừa Thiên - Huế','Lạng Sơn',
				'Kon Tum','Quảng Ninh','Đồng Nai','Bà Rịa - Vũng Tàu', 'Quảng Nam','Lâm Đồng','Đà Nẵng',
				'Quảng Ngãi','Ninh Thuận','Khánh Hoà','Bình Định','Đắc Lắc','Phú Yên','Gia Lai','Bình Thuận']		
		ktt = [103,104,104.5, 104.5, 104.75, 104.75, 104.75,
		104.75, 104.75, 105,  105, 105, 105, 105,
		105,105,105, 105,105.5,105.5,105.5,105.5,105.5,105.5,
		105.5,105.5,105.5,105.5,105.5,105.5,
		105.75, 105.75, 105.75, 105.75, 105.75, 105.75, 105.75, 106, 106,
		106, 106.25,106.25,106.5, 106.5, 107, 107,107.25,
		107.5, 107.75, 107.75,107.75,107.75,107.75,107.75,
		108, 108.25, 108.25,108.25,108.5,108.5,108.5,108.5]
		parameters = self.cboParameters.currentText()

		if self.rad3do.isChecked():
			i = self.cboProvinces.currentIndex()
			self.cboKTT.setCurrentText(str(ktt[i]))
			self.cboZone.setCurrentIndex(0)
			self.cboZone.setEnabled(False)
			self.cboKTT.setEnabled(False)
			k = 0.9999
			self.txtProjections.setText(self.hcmgis_projections_generate(parameters, ktt[i],k))
		
		elif self.radcustom.isChecked():
			if ((self.cboKTT.currentText() is not None) and  (self.cboKTT.currentText().strip() != '') and (self.cboKTT.currentIndex() != -1)):
				ktt = self.cboKTT.currentText().strip()
				if self.cboZone.currentIndex() == 0 :
					k = 0.9999
				else: k = 0.9996
				self.txtProjections.setText(self.hcmgis_projections_generate(parameters,ktt,k))
	
	
	def hcmgis_projections_generate(self,parameters,ktt,scale_factor):	
		projections_text =''
		ktt = self.cboKTT.currentText().strip()
		try:
			srid = int(float(self.cboKTT.currentText().strip())*100)
		except:
			srid = 10500
		
		if self.cboZone.currentIndex() == 0 :
			k = 0.9999
		else: k = 0.9996	
		
		#Proj.4
		if self.cboFormat.currentIndex() == 0: 
			projections_text = '+proj=tmerc +lat_0=0 +lon_0='
			projections_text+= str(ktt)
			projections_text+=' +k='
			projections_text+= str(k)
			projections_text+= ' +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84='
			projections_text+= parameters
			projections_text+= ' +units=m +no_defs'
		
		#ESRI WKT
		#PROJCS["VN_2000_UTM_zone_48N",GEOGCS["GCS_VN-2000",DATUM["D_Vietnam_2000",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]
		elif self.cboFormat.currentIndex() == 1:			
			projections_text = 'PROJCS['
			projections_text += '"VN-2000 / '+  str(srid) +'"'
			projections_text += ',GEOGCS["GCS_VN-2000",DATUM["D_Vietnam_2000",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
			projections_text += ktt + ']'
			projections_text +=',PARAMETER["scale_factor",'
			projections_text += str(k) +']'
			projections_text +=',PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'			
		
		#PostGIS
		#INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 3405, 'EPSG', 3405, '+proj=utm +zone=48 +ellps=WGS84 +towgs84=-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188 +units=m +no_defs ', 'PROJCS["VN-2000 / UTM zone 48N",GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","3405"]]');
		elif self.cboFormat.currentIndex() == 2:		
			projections_text = 'INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values('
			projections_text += str(srid) 
			projections_text += ',\'' 
			projections_text +=	'HCMGIS'
			projections_text += '\',' 
			projections_text += str(srid)
			projections_text += ',\''
			projections_text += '+proj=utm +ellps=WGS84 +towgs84='
			projections_text +=	parameters 
			projections_text += ' +units=m +no_defs'
			projections_text += '\''
			projections_text += ',\''
			projections_text += 'PROJCS["'
			projections_text += 'VN-2000 / ' + str(srid) + '"'
			projections_text += ',GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[-191.9044129,-39.30318279,-111.45032835,-0.00928836, 0.01975479, -0.004274, 0.252906278],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
			projections_text +=str(ktt)
			projections_text +='],PARAMETER["scale_factor",'
			projections_text +=str(k)
			projections_text +='],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG",'
			projections_text += '"'
			projections_text += str(srid)
			projections_text += '"'
			projections_text += ']]'
			projections_text +='\''
			projections_text +=');'

		#GeoServer:
		#3405=PROJCS["VN-2000 / UTM zone 48N",GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","3405"]]
		elif self.cboFormat.currentIndex() == 3:			
			projections_text = str(srid)
			projections_text += '=PROJCS['
			projections_text +='"'
			projections_text += 'VN-2000 / '+str(srid)
			projections_text +='"'
			projections_text += ',GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84['
			projections_text += parameters
			projections_text += '],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
			projections_text +=str(ktt)
			projections_text +='],PARAMETER["scale_factor",'
			projections_text +=str(k)
			projections_text +='],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG",'
			projections_text +=  '"'
			projections_text +=  str(srid)
			projections_text +=  '"'
			projections_text +=']]'
		
		return projections_text

	def zonechange(self):
		self.txtProjections.clear()
		
		listKTT6do = ['105','111','117']
		listKTT3do = ['102', '103', '104','104.5', '104.75', '105','105.5', '105.75','106', '106.25', '106.5',
		'107','107.25','107.5','107.75','108','108.25','108.5', '111','114', '117']

		if (self.cboZone.currentIndex() == 1):
			self.cboKTT.clear()
			self.cboKTT.addItems(listKTT6do)
			self.cboKTT.setCurrentIndex(-1)
	
		elif (self.cboZone.currentIndex() == 0):
			self.cboKTT.clear()
			self.cboKTT.addItems(listKTT3do)
			self.cboKTT.setCurrentIndex(-1)
         	
	def togglerad3do(self):
		self.txtProjections.clear()
		self.cboKTT.clear()
		if self.rad3do.isChecked():
			self.cboProvinces.setCurrentIndex(-1)
			self.cboKTT.setCurrentIndex(-1)
			self.cboZone.setCurrentIndex(-1)
			self.cboProvinces.setEnabled(True)
			self.cboKTT.setEnabled(False)
			self.cboZone.setEnabled(False)
		
	def toggleradcustom(self):
		self.txtProjections.clear()
		self.cboKTT.clear()
		if self.radcustom.isChecked():			
			self.cboProvinces.setCurrentIndex(-1)
			self.cboKTT.setCurrentIndex(-1)
			self.cboZone.setCurrentIndex(-1)
			self.cboProvinces.setEnabled(False)
			self.cboKTT.setEnabled(True)
			self.cboZone.setEnabled(True)

			
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
		self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
		self.CboField.setLayer (self.CboInput.currentLayer () )	
		self.CboInput.activated.connect(self.update_field)         
		self.BtnOKCancel.accepted.connect(self.run) 
          
	
	def update_field(self):
		self.CboField.setLayer (self.CboInput.currentLayer () )	

	def run(self):             		
		layer = self.CboInput.currentLayer()
		selectedfield = self.CboField.currentText()
		if layer is None:
			return u'No selected point layer!'		
		else:
			message = hcmgis_lec(self.iface,layer, selectedfield)
			if message != None:
				QMessageBox.critical(self.iface.mainWindow(), "Largest Empty Circle", message)						               
			else: return		
		return
	
# --------------------------------------------------------
#   hcmggis_merge - Merge layers to single shapefile
#	Reference: hcmgis
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

# csv2shp
class hcmgis_csv2shp_dialog(QDialog, Ui_hcmgis_csv2shp_form):		
	def __init__(self, iface):
		QDialog.__init__(self)
		self.iface = iface
		self.setupUi(self)	
		self.hcmgis_set_status_bar(self.status)

		self.BtnInputFolder.clicked.connect(self.read_csv)	
		#self.LinOutputFolder.setText(os.getcwd())   
		self.lsCSV.clear() 
		self.lsCSV.currentRowChanged.connect(self.set_field_names)                             
		self.BtnOKCancel.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)

	def set_field_names(self):
		header = self.hcmgis_read_csv_header(self.lsCSV.currentItem().text())
		if not header:
			return
		self.longitude_field.clear()
		self.latitude_field.clear()		
		self.longitude_field.addItems(header)
		self.latitude_field.addItems(header)

		for index, field in enumerate(header):
			if (field.lower().find("x") >= 0):
				self.longitude_field.setCurrentIndex(index)

			elif (field.lower().find("y") >= 0):
				self.latitude_field.setCurrentIndex(index)

			elif (field.lower().find('lon') >= 0):
				self.longitude_field.setCurrentIndex(index)

			elif (field.lower().find('lat') >= 0):
				self.latitude_field.setCurrentIndex(index)

	def hcmgis_read_csv_header(self, input_csv_name):
	# This may take awhile with large CSV files
		input_csv = QgsVectorLayer(input_csv_name)
		field_names = []
		if (not input_csv) or (input_csv.featureCount() <= 0) or (len(input_csv.fields()) <= 0):
			return field_names
		for field in input_csv.fields():
			field_names.append(field.name())
		return field_names

	def hcmgis_direct_read_csv_header(self, filename):
		try:
			infile = open(filename, 'r', encoding='utf-8')
		except Exception as e:
			return	"Failure opening " + filename + ": " + str(e)

		try:
			dialect = csv.Sniffer().sniff(infile.read(8192))
		except Exception as e:
			return "Bad CSV file " + filename + ": " + str(e) + "(verify that your delimiters are consistent)"

		infile.seek(0)
		reader = csv.reader(infile, dialect)
		header = next(reader)
			
		del reader
		infile.close()
		del infile

		if len(header) <= 0:
			return filename + " does not appear to be a CSV file"

		return header

	def hcmgis_set_status_bar(self, status_bar):
		status_bar.setMinimum(0)
		status_bar.setMaximum(100)
		status_bar.setValue(0)
		status_bar.setFormat("Ready")
		self.status_bar = status_bar

	def hcmgis_status_callback(self, percent_complete, message):
		try:
			if not message:
				message = str(int(percent_complete)) + "%"

			self.status_bar.setFormat(message)

			if percent_complete < 0:
				self.status_bar.setValue(0)
			elif percent_complete > 100:
				self.status_bar.setValue(100)
			else:
				self.status_bar.setValue(percent_complete)

			self.iface.statusBarIface().showMessage(message)

			# print("status_callback(" + message + ")")
		except:
			print(message)

		# add handling of "Close" button
		return 0
		
	def read_csv(self):
		newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
		self.lsCSV.clear() 
		if newname != None:
			self.LinInputFolder.setText(newname)		
		import os
		from glob import glob
		PATH = newname
		EXT = "*.csv"
		all_csv_files = [file
                 for path, subdir, files in os.walk(PATH)
                 for file in glob(os.path.join(path, EXT))]
		self.lsCSV.addItems(all_csv_files)
		self.lblCSV.setText (str(self.lsCSV.count()) + " files loaded")
		self.lsCSV.setCurrentRow(0)
				
		
	def run(self):             		
		item_count = 0
		items = []
		for index in range(self.lsCSV.count()):
			items.append(self.lsCSV.item(index))

		for item in items:
			self.lsCSV.setCurrentRow(item_count);		
			item_count +=1
			input_csv_name = item.text()
			longitude_field = str(self.longitude_field.currentText())
			latitude_field = str(self.latitude_field.currentText())

			temp_file_name = item.text()
			output_file_name = temp_file_name.replace(".csv", ".shp", 1)

			message = hcmgis_csv2shp(input_csv_name,  latitude_field, longitude_field, \
				output_file_name, self.hcmgis_status_callback)
			if message:
				QMessageBox.critical(self.iface.mainWindow(), "CSV Point Convert", message)
			
			self.lblStatus.setText (str(item_count)+"/ "+ str(self.lsCSV.count()) + " files converted")	

		#elif self.hcmgis_find_layer_by_data_source(output_file_name):
		#	self.iface.mapCanvas().refreshAllLayers()

		#else:
		#	self.iface.addVectorLayer(output_file_name, "", "ogr")
		
def hcmgis_load_combo_box_with_vector_layers(qgis, combo_box, set_selected):
	
	combo_box.clear()

	for legend in QgsProject.instance().layerTreeRoot().findLayers():
		layer = QgsProject.instance().mapLayer(legend.layerId())
		if layer.type() == QgsMapLayer.VectorLayer:
			combo_box.addItem(layer.name())
	
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
	preferred = os.getcwd() +"/" + temp + suffix
	if not os.path.isfile(preferred):
		return preferred

	for x in range(2, 10):
		name = os.getcwd() + temp + unicode(x) + suffix
		if not os.path.isfile(name):
			return name

	return preferred