#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------
#    hcmgis_menu - QGIS plugins menu class
##  --------------------------------------------------------

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from .hcmgis_dialogs import *
from .hcmgis_library import *
# ---------------------------------------------

class hcmgis_menu:
	def __init__(self, iface):
		self.iface = iface
		self.hcmgis_menu = None

	def hcmgis_add_submenu(self, submenu):
		if self.hcmgis_menu != None:
			self.hcmgis_menu.addMenu(submenu)
		else:
			self.iface.addPluginToMenu("&hcmgis", submenu.menuAction())

	def initGui(self):
		# Uncomment the following two lines to have hcmgis accessible from a top-level menu
		self.hcmgis_menu = QMenu(QCoreApplication.translate("hcmgis", "HCMGIS"))
		self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.hcmgis_menu)
		
		# OpenData_basemap submenu
		self.basemap_menu = QMenu(u'BaseMap')		
		self.hcmgis_add_submenu(self.basemap_menu)
		
		#HCMGIS Aerial Image
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
		self.hcmgisaerial_action = QAction(icon, u'HCMGIS Arerial Images', self.iface.mainWindow())
		self.hcmgisaerial_action.triggered.connect(self.hcmgisaerial_call)		
		self.basemap_menu.addAction(self.hcmgisaerial_action)
		
		#OSM Stamen Watercolor
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamenwatercolor.png")
		self.stamenwatercolor_action = QAction(icon, u'OSM Stamen Watercolor', self.iface.mainWindow())
		self.stamenwatercolor_action.triggered.connect(self.stamenwatercolor_call)		
		self.basemap_menu.addAction(self.stamenwatercolor_action)
		
		#OSM Stamen Toner
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamentoner.png")
		self.stamentoner_action = QAction(icon, u'OSM Stamen Toner', self.iface.mainWindow())
		self.stamentoner_action.triggered.connect(self.stamentoner_call)		
		self.basemap_menu.addAction(self.stamentoner_action)
		
		#OSM Stamen Terrain
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamenterrain.png")
		self.stamenterrain_action = QAction(icon, u'OSM Stamen Terrain', self.iface.mainWindow())
		self.stamenterrain_action.triggered.connect(self.stamenterrain_call)		
		self.basemap_menu.addAction(self.stamenterrain_action)
		
		
		#OSM Carto Light
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_cartolight.png")
		self.cartolight_action = QAction(icon, u'Carto Light', self.iface.mainWindow())
		self.cartolight_action.triggered.connect(self.cartolight_call)		
		self.basemap_menu.addAction(self.cartolight_action)
		
		
		#OSM Carto Dark
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_cartodark.png")
		self.cartodark_action = QAction(icon, u'Carto Dark', self.iface.mainWindow())
		self.cartodark_action.triggered.connect(self.cartodark_call)		
		self.basemap_menu.addAction(self.cartodark_action)
		
		#Google Satellite
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlesatellite.png")
		self.googlesatellite_action = QAction(icon, u'Google Satellite', self.iface.mainWindow())
		self.googlesatellite_action.triggered.connect(self.googlesatellite_call)		
		self.basemap_menu.addAction(self.googlesatellite_action)
		
		#Google Streets
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlestreets.png")
		self.googlestreets_action = QAction(icon, u'Google Streets', self.iface.mainWindow())
		self.googlestreets_action.triggered.connect(self.googlestreets_call)		
		self.basemap_menu.addAction(self.googlestreets_action)
		
		#Google Hybrid
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlehybrid.png")
		self.hcmgis_googlehybrid_action = QAction(icon, u'Google Hybrid', self.iface.mainWindow())
		self.hcmgis_googlehybrid_action.triggered.connect(self.googlehybrid_call)		
		self.basemap_menu.addAction(self.hcmgis_googlehybrid_action)
		
		#Google Physical
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlephysical.png")
		self.hcmgis_googlephysical_action = QAction(icon, u'Google Physical', self.iface.mainWindow())
		self.hcmgis_googlephysical_action.triggered.connect(self.googlephysical_call)		
		self.basemap_menu.addAction(self.hcmgis_googlephysical_action)
		
		#HCMGIS OpenData submenu
		self.opendata_menu = QMenu(u'HCMGIS OpenData')		
		self.hcmgis_add_submenu(self.opendata_menu)
		
		#HCMGIS OpenData
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
		self.opendata_action = QAction(icon, u'Download Free and Open GeoData', self.iface.mainWindow())
		self.opendata_action.triggered.connect(self.opendata)		
		self.opendata_menu.addAction(self.opendata_action)
		
		# Merge_Split submenu
		self.geoprocessing_menu = QMenu(u'Geometry Processing')		
		self.hcmgis_add_submenu(self.geoprocessing_menu)
		
		# MediAxis Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_skeleton.png")
		self.medialaxis_action = QAction(icon, u'Skeleton/ Medial Axis', self.iface.mainWindow())
		self.medialaxis_action.triggered.connect(self.medialaxis)
		self.geoprocessing_menu.addAction(self.medialaxis_action)
		
		# Centerline Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_centerline.png")
		self.centerline_action = QAction(icon, u"Centerline in Polygons' Gaps", self.iface.mainWindow())
		self.centerline_action.triggered.connect(self.centerline)
		self.geoprocessing_menu.addAction(self.centerline_action)

		# Closest pair of Points Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_closestpair.png")
		self.closestpair_action = QAction(icon, u"Closest/ farthest pair of Points", self.iface.mainWindow())
		self.closestpair_action.triggered.connect(self.closestpair)
		self.geoprocessing_menu.addAction(self.closestpair_action)
		

		#Merge
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_merge.png")
		self.merge_action = QAction(icon, u'Merge Layers', self.iface.mainWindow())
		self.merge_action.triggered.connect(self.merge)		
		self.geoprocessing_menu.addAction(self.merge_action)
		
		#Splits
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_split.png")
		self.split_action = QAction(icon, u'Split Layer', self.iface.mainWindow())
		self.split_action.triggered.connect(self.split)
		self.geoprocessing_menu.addAction(self.split_action)
		
		#CheckValidity
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_checkvalidity.png")
		self.checkvalidity_action = QAction(icon, u'Check Validity', self.iface.mainWindow())
		self.checkvalidity_action.triggered.connect(self.checkvalidity)
		self.geoprocessing_menu.addAction(self.checkvalidity_action)
		
		#Fixgeometries
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_fixgeometries.png")
		self.fixgeometries_action = QAction(icon, u'Fix Geometries', self.iface.mainWindow())
		self.fixgeometries_action.triggered.connect(self.fixgeometries)
		self.geoprocessing_menu.addAction(self.fixgeometries_action)
		
		# Reproject Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_reproject.png")
		self.reproject_action = QAction(icon, u'CRS Transformation', self.iface.mainWindow())
		self.reproject_action.triggered.connect(self.reproject)
		self.geoprocessing_menu.addAction(self.reproject_action)
		
		
		
				
		# Tool Submenu
		self.tool_menu = QMenu(u'Calculate Field')	
		self.hcmgis_add_submenu(self.tool_menu)
				
		# FontConverter Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_font_converter.png")
		self.fontconverter_action = QAction(icon, u'Vietnamese Font Converter', self.iface.mainWindow())
		self.fontconverter_action.triggered.connect(self.fontconverter)
		#QObject.connect(self.fontconverter_action, SIGNAL("triggered()"), self.fontconverter)
		self.tool_menu.addAction(self.fontconverter_action)
		
		# Merge Field Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_merge_field.png")
		self.mergefield_action = QAction(icon, u'Merge Fields', self.iface.mainWindow())
		self.mergefield_action.triggered.connect(self.mergefield)
		#QObject.connect(self.mergefield_action, SIGNAL("triggered()"), self.mergefield)
		self.tool_menu.addAction(self.mergefield_action)
		
		# Split Field Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_split_field.png")
		self.splitfield_action = QAction(icon, u'Split Field', self.iface.mainWindow())
		self.splitfield_action.triggered.connect(self.splitfield)
		#QObject.connect(self.splitfield_action, SIGNAL("triggered()"), self.splitfield)
		self.tool_menu.addAction(self.splitfield_action)

		# Find and Replace Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_find_replace.png")
		self.find_replace_action = QAction(icon, u'Find and Replace', self.iface.mainWindow())
		self.find_replace_action.triggered.connect(self.find_replace)
		#QObject.connect(self.find_replace_action, SIGNAL("triggered()"), self.find_replace)
		self.tool_menu.addAction(self.find_replace_action)

		# Prefix/ Suffix Submenu
		icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_prefix_suffix.png")
		self.prefix_suffix_action = QAction(icon, u'Add Prefix/ Suffix', self.iface.mainWindow())
		self.prefix_suffix_action.triggered.connect(self.prefix_suffix)
		#QObject.connect(self.prefix_suffix_action, SIGNAL("triggered()"), self.prefix_suffix)
		self.tool_menu.addAction(self.prefix_suffix_action)
		
		
	def unload(self):
		if self.hcmgis_menu != None:
			self.iface.mainWindow().menuBar().removeAction(self.hcmgis_menu.menuAction())
		else:
			self.iface.removePluginMenu("&hcmgis", self.basemap_menu.menuAction())
			self.iface.removePluginMenu("&hcmgis", self.openddata_menu.menuAction())
			self.iface.removePluginMenu("&hcmgis", self.geoprocessing_menu.menuAction())
			self.iface.removePluginMenu("&hcmgis", self.tool_menu.menuAction())

	def hcmgisaerial_call(self):
		service_url = "trueortho.hcmgis.vn/basemap/cache_lidar/{z}/{x}/{y}.jpg" 
		name = "HCMGIS Aerial Images"
		hcmgis_basemap(self.iface,service_url, name)
			
	def stamenwatercolor_call(self):
		service_url = "c.tile.stamen.com/watercolor/{z}/{x}/{y}.jpg" 
		name = "OSM Stamen Watercolor"
		hcmgis_basemap(self.iface,service_url, name)
	
	def stamentoner_call(self):
		service_url ="a.tile.stamen.com/toner-background/{z}/{x}/{y}.png"
		name = "OSM Stamen Toner"
		hcmgis_basemap(self.iface,service_url, name)
	
	def stamenterrain_call(self):
		service_url ="a.tile.stamen.com/terrain-background/{z}/{x}/{y}.png" 
		name = "OSM Stamen Terrain"
		hcmgis_basemap(self.iface,service_url, name)
	
	def cartolight_call(self):
		service_url ="a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png" 
		name = "OSM Carto Light"
		hcmgis_basemap(self.iface,service_url, name)
		
	def cartodark_call(self):
		service_url ="a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png" 
		name = "OSM Carto Dark"
		hcmgis_basemap(self.iface,service_url, name)
		
	def googlesatellite_call(self):
		service_url ="mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" 
		name = "Google Satellite"
		hcmgis_basemap(self.iface,service_url, name)
	
	def googlestreets_call(self):
		service_url ="mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
		name = "Google Streets"
		hcmgis_basemap(self.iface,service_url, name)
	
	def googlehybrid_call(self):
		service_url ="mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
		name = "Google Hybrid"
		hcmgis_basemap(self.iface,service_url, name)
	
	def googlephysical_call(self):
		service_url ="mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}" 
		name = "Google Physical"
		hcmgis_basemap(self.iface,service_url, name)
		
	def opendata(self):
		dialog = hcmgis_opendata_dialog(self.iface)
		dialog.exec_()
	
	def prefix_suffix(self):
		dialog = hcmgis_prefix_suffix_dialog(self.iface)
		dialog.exec_()
		
	def find_replace(self):
		dialog = hcmgis_find_replace_dialog(self.iface)
		dialog.exec_()
		
		
	def mergefield(self):
		dialog = hcmgis_merge_field_dialog(self.iface)
		dialog.exec_()
		
	def splitfield(self):
		dialog = hcmgis_split_field_dialog(self.iface)
		dialog.exec_()
		
			
	def medialaxis(self):
		dialog = hcmgis_medialaxis_dialog(self.iface)
		dialog.exec_()
	
	def centerline(self):
		dialog = hcmgis_centerline_dialog(self.iface)
		dialog.exec_()
	
	def closestpair(self):
		dialog = hcmgis_closestpair_dialog(self.iface)
		dialog.exec_()
		
		
	def merge(self):
		dialog = hcmgis_merge_dialog(self.iface)
		dialog.exec_()
	
	def split(self):
		dialog = hcmgis_split_dialog(self.iface)
		dialog.exec_()
	
	def checkvalidity(self):
		dialog = hcmgis_checkvalidity_dialog(self.iface)
		dialog.exec_()
		
	def fixgeometries(self):
		dialog = hcmgis_fixgeometries_dialog(self.iface)
		dialog.exec_()
	
	def fontconverter(self):
		dialog = hcmgis_font_convert_dialog(self.iface)
		dialog.exec_()
	
	def reproject(self):
		dialog = hcmgis_reprojection_dialog(self.iface)
		dialog.exec_()

	
		

