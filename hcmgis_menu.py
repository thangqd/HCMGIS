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
from functools import partial


# ---------------------------------------------
class hcmgis_menu ():
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
        self.basemap_menu = QMenu(u'Basemaps')		
        self.hcmgis_add_submenu(self.basemap_menu)

        ##https://mc.bbbike.org/mc/?num=2&mt0=mapnik&mt1=watercolor
        #https://gitlab.com/GIS-projects/Belgium-XYZ-tiles/tree/b538df2c2de0d16937641742f25e4709ca94e42e
        
        #############
        #Google Maps
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlemaps.png")
        self.googlemaps_action = QAction(icon, u'Google Maps', self.iface.mainWindow())
        self.googlemaps_action.triggered.connect(lambda: hcmgis_basemap('Google Maps'))		
        self.basemap_menu.addAction(self.googlemaps_action)
        
        #Google Satellite
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlemaps.png")
        self.googlesatellite_action = QAction(icon, u'Google Satellite', self.iface.mainWindow())
        self.googlesatellite_action.triggered.connect(lambda: hcmgis_basemap('Google Satellite'))		
        self.basemap_menu.addAction(self.googlesatellite_action)

        #Google Satellite Hybrid
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlemaps.png")
        self.hcmgis_googlesatellitehybrid_action = QAction(icon, u'Google Satellite Hybrid', self.iface.mainWindow())
        self.hcmgis_googlesatellitehybrid_action.triggered.connect(lambda: hcmgis_basemap('Google Satellite Hybrid'))		
        self.basemap_menu.addAction(self.hcmgis_googlesatellitehybrid_action)

                
        #Google Terrain
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlemaps.png")
        # self.hcmgis_googleterrain_action = QAction(icon, u'Google Terrain', self.iface.mainWindow())
        # self.hcmgis_googleterrain_action.triggered.connect(lambda: hcmgis_basemap('Google Terrain'))		
        # self.basemap_menu.addAction(self.hcmgis_googleterrain_action)

        #Google Terrain Hybrid
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_googlemaps.png")
        self.hcmgis_googleterrainhybrid_action = QAction(icon, u'Google Terrain Hybrid', self.iface.mainWindow())
        self.hcmgis_googleterrainhybrid_action.triggered.connect(lambda: hcmgis_basemap('Google Terrain Hybrid'))		
        self.basemap_menu.addAction(self.hcmgis_googleterrainhybrid_action)

        
        #############
        #Bing Virtual Earth
        #############
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_bing.png")
        self.bingaerial_action = QAction(icon, u'Bing Virtual Earth', self.iface.mainWindow())
        self.bingaerial_action.triggered.connect(lambda: hcmgis_basemap('Bing Virtual Earth'))	
        self.basemap_menu.addAction(self.bingaerial_action)
 

        #Carto Antique
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")
        self.cartoantique_action = QAction(icon, u'Carto Antique', self.iface.mainWindow())
        self.cartoantique_action.triggered.connect(lambda: hcmgis_basemap('Carto Antique'))		
        self.basemap_menu.addAction(self.cartoantique_action)

        #Carto Dark
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")
        self.cartodark_action = QAction(icon, u'Carto Dark', self.iface.mainWindow())
        self.cartodark_action.triggered.connect(lambda: hcmgis_basemap('Carto Dark'))		
        self.basemap_menu.addAction(self.cartodark_action)

        #Carto Eco
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")
        self.cartoeco_action = QAction(icon, u'Carto Eco', self.iface.mainWindow())
        self.cartoeco_action.triggered.connect(lambda: hcmgis_basemap('Carto Eco'))		
        self.basemap_menu.addAction(self.cartoeco_action)

        #Carto Light
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")
        self.cartolight_action = QAction(icon, u'Carto Light', self.iface.mainWindow())
        self.cartolight_action.triggered.connect(lambda: hcmgis_basemap('Carto Light'))		
        self.basemap_menu.addAction(self.cartolight_action)

        
        #########################		
        # ESRI https://gitlab.com/GIS-projects/Belgium-XYZ-tiles/tree/b538df2c2de0d16937641742f25e4709ca94e42e
        #####################
        #Esri Boundaries and Places 
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        # self.esriboundary_action = QAction(icon, u'Esri Boundaries and Places', self.iface.mainWindow())
        # self.esriboundary_action.triggered.connect(lambda: hcmgis_basemap('Esri Boundaries and Places'))		
        # self.basemap_menu.addAction(self.esriboundary_action)

        #Esri Dark Gray 
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esridarkgray_action = QAction(icon, u'Esri Dark Gray', self.iface.mainWindow())
        self.esridarkgray_action.triggered.connect(lambda: hcmgis_basemap('Esri Dark Gray'))		
        self.basemap_menu.addAction(self.esridarkgray_action)

        #Esri DeLorme World Base Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esridelorme_action = QAction(icon, u'ESri DeLorme', self.iface.mainWindow())
        self.esridelorme_action.triggered.connect(lambda: hcmgis_basemap('ESri DeLorme'))		
        self.basemap_menu.addAction(self.esridelorme_action)

        #Esri Imagery 
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esriimagery_action = QAction(icon, u'Esri Imagery', self.iface.mainWindow())
        self.esriimagery_action.triggered.connect(lambda: hcmgis_basemap('Esri Imagery'))		
        self.basemap_menu.addAction(self.esriimagery_action)
    
        #Esri Light Gray 
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esrilightgray_action = QAction(icon, u'Esri Light Gray', self.iface.mainWindow())
        self.esrilightgray_action.triggered.connect(lambda: hcmgis_basemap('Esri Light Gray'))		
        self.basemap_menu.addAction(self.esrilightgray_action)

        #Esri National Geographic World Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esrinational_action = QAction(icon, u'Esri National Geographic', self.iface.mainWindow())
        self.esrinational_action.triggered.connect(lambda: hcmgis_basemap('Esri National Geographic'))		
        self.basemap_menu.addAction(self.esrinational_action)

        #Esri Ocean Basemap
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esriocean_action = QAction(icon, u'Esri Ocean', self.iface.mainWindow())
        self.esriocean_action.triggered.connect(lambda: hcmgis_basemap('Esri Ocean'))		
        self.basemap_menu.addAction(self.esriocean_action)

        #Esri Physical Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esriphysical_action = QAction(icon, u'Esri Physical', self.iface.mainWindow())
        self.esriphysical_action.triggered.connect(lambda: hcmgis_basemap('Esri Physical'))		
        self.basemap_menu.addAction(self.esriphysical_action)

        #Esri Shaded Relief
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esrishaded_action = QAction(icon, u'Esri Shaded Relief', self.iface.mainWindow())
        self.esrishaded_action.triggered.connect(lambda: hcmgis_basemap('Esri Shaded Relief'))		
        self.basemap_menu.addAction(self.esrishaded_action)

        #Esri Street Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esristreet_action = QAction(icon, u'Esri Street', self.iface.mainWindow())
        self.esristreet_action.triggered.connect(lambda: hcmgis_basemap('Esri Street'))		
        self.basemap_menu.addAction(self.esristreet_action)

        #Esri Terrain Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esriterrain_action = QAction(icon, u'Esri Terrain', self.iface.mainWindow())
        self.esriterrain_action.triggered.connect(lambda: hcmgis_basemap('Esri Terrain'))		
        self.basemap_menu.addAction(self.esriterrain_action)
        
        #Esri World Topo Map
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        self.esritopo_action = QAction(icon, u'Esri Topographic', self.iface.mainWindow())
        self.esritopo_action.triggered.connect(lambda: hcmgis_basemap('Esri Topographic'))		
        self.basemap_menu.addAction(self.esritopo_action)

        # """ #Esri World Transportation
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        # self.esritransport_action = QAction(icon, u'Esri Transport', self.iface.mainWindow())
        # self.esritransport_action.triggered.connect(self.esritransport_call)		
        # self.basemap_menu.addAction(self.esritransport_action)
        #  """
        
        ##############################
        # F4map - 2D
        #############################
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_f4map.png")
        self.f4map_action = QAction(icon, u'F4 Map - 2D', self.iface.mainWindow())
        self.f4map_action.triggered.connect(lambda: hcmgis_basemap('F4 Map - 2D'))		
        self.basemap_menu.addAction(self.f4map_action)

        ##############################
        # Mapbox
        #############################
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_mapbox.png")
        # self.mapbox_action = QAction(icon, u'Mapbox', self.iface.mainWindow())
        # self.mapbox_action.triggered.connect(self.mapbox)		
        # self.basemap_menu.addAction(self.mapbox_action)

        ##############################
        # OpenTopoMap
        #############################
        # """ icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opentopomap.png")
        # self.opentopomap_action = QAction(icon, u'OpenTopoMap', self.iface.mainWindow())
        # self.opentopomap_action.triggered.connect(self.opentopomap_call)		
        # self.basemap_menu.addAction(self.opentopomap_action) """
        

        
        #Stamen Toner
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamentoner_action = QAction(icon, u'Stamen Toner', self.iface.mainWindow())
        self.stamentoner_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner'))		
        self.basemap_menu.addAction(self.stamentoner_action)

        # Stamen Toner Background
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamentonerbkg_action = QAction(icon, u'Stamen Toner Background', self.iface.mainWindow())
        self.stamentonerbkg_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Background'))		
        self.basemap_menu.addAction(self.stamentonerbkg_action)

        # Stamen Toner Hybrid
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamentonerhybrid_action = QAction(icon, u'Stamen Toner Hybrid', self.iface.mainWindow())
        self.stamentonerhybrid_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Hybrid'))		
        self.basemap_menu.addAction(self.stamentonerhybrid_action)

        # Stamen Toner Lite
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamentonerlite_action = QAction(icon, u'Stamen Toner Lite', self.iface.mainWindow())
        self.stamentonerlite_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Lite'))		
        self.basemap_menu.addAction(self.stamentonerlite_action)
        
        # Stamen Terrain
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamenterrain_action = QAction(icon, u'Stamen Terrain', self.iface.mainWindow())
        self.stamenterrain_action.triggered.connect(lambda: hcmgis_basemap('Stamen Terrain'))		
        self.basemap_menu.addAction(self.stamenterrain_action)

        # Stamen Terrain Background
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamenterrainbkg_action = QAction(icon, u'Stamen Terrain Background', self.iface.mainWindow())
        self.stamenterrainbkg_action.triggered.connect(lambda: hcmgis_basemap('Stamen Terrain Background'))		
        self.basemap_menu.addAction(self.stamenterrainbkg_action)
        
        # Stamen Watercolor
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        self.stamenwatercolor_action = QAction(icon, u'Stamen Watercolor', self.iface.mainWindow())
        self.stamenwatercolor_action.triggered.connect(lambda: hcmgis_basemap('Stamen Watercolor'))		
        self.basemap_menu.addAction(self.stamenwatercolor_action)
                
        # Wikimedia Maps
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_wikimedia.png")
        self.wikimedia_action = QAction(icon, u'Wikimedia Maps', self.iface.mainWindow())
        self.wikimedia_action.triggered.connect(lambda: hcmgis_basemap('Wikimedia Maps'))		
        self.basemap_menu.addAction(self.wikimedia_action)
    # """ 
    # 	# Strava Run
    # 	icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_strava.png")
    # 	self.stravarun_action = QAction(icon, u'Strava Run', self.iface.mainWindow())
    # 	self.stravarun_action.triggered.connect(self.stravarun_call)		
    # 	self.basemap_menu.addAction(self.stravarun_action)

    # 	# Strava All
    # 	icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_strava.png")
    # 	self.stravaall_action = QAction(icon, u'Strava All', self.iface.mainWindow())
    # 	self.stravaall_action.triggered.connect(self.stravaall_call)		
    # 	self.basemap_menu.addAction(self.stravaall_action) """	

    # """ # Wikimedia Hike Bike
    # 	icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_wikimedia.png")
    # 	self.wikimediahikebike_action = QAction(icon, u'Wikimedia Hike Bike', self.iface.mainWindow())
    # 	self.wikimediahikebike_action.triggered.connect(self.wikimediahikebike_call)		
    # 	self.basemap_menu.addAction(self.wikimediahikebike_action)
    # 	 """

        #Vietnam OSM Mapss
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_becamaps.png")
        self.hcmgis_osm_action = QAction(icon, u'Vietnam OSM BecaMaps', self.iface.mainWindow())
        self.hcmgis_osm_action.triggered.connect(lambda: hcmgis_basemap('Vietnam OSM BecaMaps'))		
        self.basemap_menu.addAction(self.hcmgis_osm_action)

        #Viet Ban do
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vbd.png")
        self.hcmgis_vbd_action = QAction(icon, u'Vietbando Maps', self.iface.mainWindow())
        self.hcmgis_vbd_action.triggered.connect(lambda: hcmgis_basemap('Vietbando Maps'))	
        self.basemap_menu.addAction(self.hcmgis_vbd_action)


        
        # Batch Converter Submenu
        self.batch_converter_menu = QMenu(u'Batch Converter')	
        self.hcmgis_add_submenu(self.batch_converter_menu)

        # Vector Format Converter
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_converter.png")
        self.formatconvert_action = QAction(icon, u'Vector Format Converter', self.iface.mainWindow())
        self.formatconvert_action.triggered.connect(self.formatconvert)
        self.batch_converter_menu.addAction(self.formatconvert_action)

        # CSV point to Shapefile
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_csv.png")
        self.csv2shp_action = QAction(icon, u'CSV to Point', self.iface.mainWindow())
        self.csv2shp_action.triggered.connect(self.csv2shp)
        self.batch_converter_menu.addAction(self.csv2shp_action)

        # TXT to CSV
        #icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
        #self.txt2csv_action = QAction(icon, u'TXT to CSV', self.iface.mainWindow())
        #self.txt2csv_action.triggered.connect(self.txt2csv)
        #self.batch_converter_menu.addAction(self.txt2csv_action)

        
        # # XLS to CSV
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
        # self.xls2csv_action = QAction(icon, u'XLSX to CSV', self.iface.mainWindow())
        # self.xls2csv_action.triggered.connect(self.xls2csv)
        # self.batch_converter_menu.addAction(self.xls2csv_action)

        #HCMGIS OpenData submenu
        # self.covid19_menu = QMenu(u'Download COVID-19 Data')		
        # self.hcmgis_add_submenu(self.covid19_menu)	
        
        # #Global CoVID-19 live update
        # self.hcmgis_add_submenu(self.covid19_menu)
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_covid19.png")
        # self.covid19_action = QAction(icon, u'Global COVID-19 Live Update - Johns Hopkins CSSE', self.iface.mainWindow())
        # self.covid19_action.triggered.connect(lambda:hcmgis_covid19())		
        # self.covid19_menu.addAction(self.covid19_action)

        
        # #Global CoVID-19 Timeseries 
        # self.hcmgis_add_submenu(self.covid19_menu)
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_covid19.png")
        # self.covid19_timeseries_action = QAction(icon, u'Global COVID-19 Time Series - Johns Hopkins CSSE', self.iface.mainWindow())
        # self.covid19_timeseries_action.triggered.connect(lambda:hcmgis_covid19_timeseries())		
        # self.covid19_menu.addAction(self.covid19_timeseries_action)

        
        # #Global CoVID-19 Vaccination Timeseries
        # self.hcmgis_add_submenu(self.covid19_menu)
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_covid19_vaccine.png")
        # self.covid19_vaccination_timeseries_action = QAction(icon, u'Global CoVID-19 Vaccination Timeseries - Johns Hopkins GovEx', self.iface.mainWindow())
        # self.covid19_vaccination_timeseries_action.triggered.connect(lambda:hcmgis_covid19_vaccination_timeseries())		
        # self.covid19_menu.addAction(self.covid19_vaccination_timeseries_action)


        # #Vietnam CoVID-19 live update 
        # self.hcmgis_add_submenu(self.covid19_menu)
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
        # self.covid19_vietnam_action = QAction(icon, u'Vietnam COVID-19 Live Update - HCMGIS OpenData', self.iface.mainWindow())
        # self.covid19_vietnam_action.triggered.connect(lambda:hcmgis_covid19_vietnam())		
        # self.covid19_menu.addAction(self.covid19_vietnam_action)




        #HCMGIS OpenData submenu
        self.opendata_menu = QMenu(u'Download OpenData')		
        self.hcmgis_add_submenu(self.opendata_menu)	

        #OSM Data from Geofabrik 
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_geofabrik.png")
        self.geofabrik_action = QAction(icon, u'OSM Data by Country from Geofabrik', self.iface.mainWindow())
        self.geofabrik_action.triggered.connect(self.geofabrik)		
        self.opendata_menu.addAction(self.geofabrik_action)

        #Global Administrative Areas by Country from GADM
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_gadm.png")
        self.gadm_action = QAction(icon, u'Global Administrative Areas by Country from GADM', self.iface.mainWindow())
        self.gadm_action.triggered.connect(self.gadm)		
        self.opendata_menu.addAction(self.gadm_action)

        #Building Footprints from Microsoft
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_bing.png")
        self.microsoft_action = QAction(icon, u'Building Footprints from Microsoft', self.iface.mainWindow())
        self.microsoft_action.triggered.connect(self.microsoft)		
        self.opendata_menu.addAction(self.microsoft_action)

        #HCMGIS OpenData
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_opendata.png")
        self.opendata_action = QAction(icon, u'HCMGIS OpenData and more...', self.iface.mainWindow())
        self.opendata_action.triggered.connect(self.opendata)		
        self.opendata_menu.addAction(self.opendata_action)


        
        # VN-2000 Projections submenu
        self.projections_menu = QMenu(u'VN-2000/TM-3')		
        self.hcmgis_add_submenu(self.projections_menu)
        
        # VN-2000 Projections
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_projections.png")
        self.projections_action = QAction(icon, u'EPSG Code for VN-2000/TM-3', self.iface.mainWindow())
        self.projections_action.triggered.connect(self.projections)		
        self.projections_menu.addAction(self.projections_action)

        
        # Geoprocessing submenu
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

        
        # Largest Empty Circle Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_lec.png")
        self.lec_action = QAction(icon, u"Largest Empty Circle", self.iface.mainWindow())
        self.lec_action.triggered.connect(self.lec)
        self.geoprocessing_menu.addAction(self.lec_action)
        

            
        # Calculate Attribute submenu
        self.tool_menu = QMenu(u'Calculate Field')	
        self.hcmgis_add_submenu(self.tool_menu)
                
        
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

        # FontConverter Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_font_converter.png")
        self.fontconverter_action = QAction(icon, u'Vietnamese Font Converter', self.iface.mainWindow())
        self.fontconverter_action.triggered.connect(self.fontconverter)
        #QObject.connect(self.fontconverter_action, SIGNAL("triggered()"), self.fontconverter)
        self.tool_menu.addAction(self.fontconverter_action)	

        
        
    def unload(self):
        if self.hcmgis_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.hcmgis_menu.menuAction())
        else:
            self.iface.removePluginMenu("&hcmgis", self.basemap_menu.menuAction())
            self.iface.removePluginMenu("&hcmgis", self.batch_converter_menu.menuAction())
            self.iface.removePluginMenu("&hcmgis", self.covid19_menu.menuAction())						
            self.iface.removePluginMenu("&hcmgis", self.opendata_menu.menuAction())
            self.iface.removePluginMenu("&hcmgis", self.projections_menu.menuAction())			
            self.iface.removePluginMenu("&hcmgis", self.geoprocessing_menu.menuAction())
            self.iface.removePluginMenu("&hcmgis", self.tool_menu.menuAction())
            
         
    
    ##########################	
    def opendata(self):
        dialog = hcmgis_opendata_dialog(self.iface)
        dialog.exec_()
    
    # def opendevelopmentmekong(self):
    # 	dialog = hcmgis_opendevelopmentmekong_dialog(self.iface)
    # 	dialog.exec_()
    
    def geofabrik(self):
        dialog = hcmgis_geofabrik_dialog(self.iface)
        dialog.exec_()
    
    def gadm(self):
        dialog = hcmgis_gadm_dialog(self.iface)
        dialog.exec_()    

    
    def microsoft(self):
        dialog = hcmgis_microsoft_dialog(self.iface)
        dialog.exec_()    
        
            
    def projections(self):
        dialog = hcmgis_customprojections_dialog(self.iface)
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
    
    def lec(self):
        dialog = hcmgis_lec_dialog(self.iface)
        dialog.exec_()
            
        
    def merge(self):
        dialog = hcmgis_merge_dialog(self.iface)
        dialog.exec_()
    
    def split(self):
        dialog = hcmgis_split_dialog(self.iface)
        dialog.exec_()
    
    def fontconverter(self):
        dialog = hcmgis_font_convert_dialog(self.iface)
        dialog.exec_()	
    
    def formatconvert(self):
        dialog = hcmgis_format_convert_dialog(self.iface)
        dialog.exec_()

    def csv2shp(self):
        dialog = hcmgis_csv2shp_dialog(self.iface)
        dialog.exec_()
    
    def txt2csv(self):
        dialog = hcmgis_txt2csv_dialog(self.iface)
        dialog.exec_()
    
    # def xls2csv(self):
    #     dialog = hcmgis_xls2csv_dialog(self.iface)
    #     dialog.exec_()
            
    def mapbox(self):
        dialog = hcmgis_mapbox_dialog(self.iface)
        dialog.exec_()

