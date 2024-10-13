#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------
#    hcmgis_menu - QGIS plugins menu class
#
#    begin                : 01/02/2018
#    copyright            : (c) 2018 by Quach Dong Thang
#    email                : quachdongthang@gmail.com
# --------------------------------------------------------

"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License v3.0.            *
 *                                                                         *
 ***************************************************************************/
 """

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

    def hcmgis_add_submenu2(self, submenu, icon):
        if self.hcmgis_menu != None:
            submenu.setIcon(QIcon(icon))
            self.hcmgis_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&hcmgis", submenu.menuAction())

    def hcmgis_add_submenu3(self, submenu, icon):
        if self.basemap_menu != None:
            submenu.setIcon(QIcon(icon))
            self.basemap_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&basemap", submenu.menuAction())

    def initGui(self):
        # Uncomment the following two lines to have hcmgis accessible from a top-level menu
        self.hcmgis_menu = QMenu(QCoreApplication.translate("hcmgis", "HCMGIS"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.hcmgis_menu)

        # OpenData_basemap submenu
        self.basemap_menu = QMenu(u'Basemaps')
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_basemaps.png")
        self.hcmgis_add_submenu2(self.basemap_menu, icon)

        ############################################
        # Add Vector Tile Basemaps
        ############################################
        # Adding "Vector tiles" submenu under "Basemaps"
        self.vectortiles_menu = QMenu(u'Vector tiles')
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vectortiles.png")
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vgrid.png")
        self.hcmgis_add_submenu3(self.vectortiles_menu,icon)

        ############################################
        # ESRI Vector Tiles
        ############################################

        # ESRI Colored Pencil action under "Vector tiles" submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esricoloredpencile_action = QAction(icon, u'ESRI Colored Pencil', self.iface.mainWindow())
        self.esricoloredpencile_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Colored Pencil'))
        self.vectortiles_menu.addAction(self.esricoloredpencile_action)
        
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esridark_action = QAction(icon, u'ESRI Dark', self.iface.mainWindow())
        self.esridark_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Dark'))
        self.vectortiles_menu.addAction(self.esridark_action)

        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esrimodenantique_action = QAction(icon, u'ESRI Modern Antique', self.iface.mainWindow())
        self.esrimodenantique_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Modern Antique'))
        self.vectortiles_menu.addAction(self.esrimodenantique_action)

        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esrinova_action = QAction(icon, u'ESRI Nova', self.iface.mainWindow())
        self.esrinova_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Nova'))
        self.vectortiles_menu.addAction(self.esrinova_action)

        # ESRI Night
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esrinight_action = QAction(icon, u'ESRI Night', self.iface.mainWindow())
        self.esrinight_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Night'))
        self.vectortiles_menu.addAction(self.esrinight_action)

        #ESRI Topo
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esritopo_action = QAction(icon, u'ESRI Topo', self.iface.mainWindow())
        self.esritopo_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI Topo'))
        self.vectortiles_menu.addAction(self.esritopo_action)

        #ESRI OSM Standard
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esriosmstandard_action = QAction(icon, u'ESRI OSM Standard', self.iface.mainWindow())
        self.esriosmstandard_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI OSM Standard'))
        self.vectortiles_menu.addAction(self.esriosmstandard_action)
        
        #ESRI OSM Street
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esriosmstreet_action = QAction(icon, u'ESRI OSM Street', self.iface.mainWindow())
        self.esriosmstreet_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI OSM Street'))
        self.vectortiles_menu.addAction(self.esriosmstreet_action)

        #ESRI OSM Light Grey
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esriosmlightgrey_action = QAction(icon, u'ESRI OSM Light Grey', self.iface.mainWindow())
        self.esriosmlightgrey_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI OSM Light Grey'))
        self.vectortiles_menu.addAction(self.esriosmlightgrey_action)

         #ESRI OSM Dark Grey
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esriosmdarkgrey_action = QAction(icon, u'ESRI OSM Dark Grey', self.iface.mainWindow())
        self.esriosmdarkgrey_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI OSM Dark Grey'))
        self.vectortiles_menu.addAction(self.esriosmdarkgrey_action)

        #ESRI OSM Dark Grey
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")  
        self.esriosmdarkgrey_action = QAction(icon, u'ESRI OSM Dark Grey', self.iface.mainWindow())
        self.esriosmdarkgrey_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('ESRI OSM Dark Grey'))
        self.vectortiles_menu.addAction(self.esriosmdarkgrey_action)
        
        self.vectortiles_menu.addSeparator()
        ############################################
        # Carto
        ############################################
        'Carto Basic',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.Cartobasic_action  = QAction(icon, u'Carto Basic', self.iface.mainWindow())
        self.Cartobasic_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Basic'))
        self.vectortiles_menu.addAction(self.Cartobasic_action)

        'Carto Dark',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.cartodark_action = QAction(icon, u'Carto Dark', self.iface.mainWindow())
        self.cartodark_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Dark'))
        self.vectortiles_menu.addAction(self.cartodark_action)
        
        'Carto Fiord',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.cartofiord_action = QAction(icon, u'Carto Fiord', self.iface.mainWindow())
        self.cartofiord_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Fiord'))
        self.vectortiles_menu.addAction(self.cartofiord_action)

        'Carto Liberty',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.cartoliberty_action = QAction(icon, u'Carto Liberty', self.iface.mainWindow())
        self.cartoliberty_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Liberty'))
        self.vectortiles_menu.addAction(self.cartoliberty_action)

        'Carto Positron',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.cartopositron_action = QAction(icon, u'Carto Positron', self.iface.mainWindow())
        self.cartopositron_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Positron'))
        self.vectortiles_menu.addAction(self.cartopositron_action)

        'Carto Toner',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_carto.png")  
        self.cartoner_action = QAction(icon, u'Carto Toner', self.iface.mainWindow())
        self.cartoner_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Carto Toner'))
        self.vectortiles_menu.addAction(self.cartoner_action)

        self.vectortiles_menu.addSeparator()
        ############################################
        # Versatiles
        ############################################
        'Versatiles Colorful',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_versatiles.png")  
        self.versatilescolorful_action = QAction(icon, u'Versatiles Colorful', self.iface.mainWindow())
        self.versatilescolorful_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Versatiles Colorful'))
        self.vectortiles_menu.addAction(self.versatilescolorful_action)
                
        'Versatiles Eclipse',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_versatiles.png")  
        self.versatileseclipse_action = QAction(icon, u'Versatiles Eclipse', self.iface.mainWindow())
        self.versatileseclipse_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Versatiles Eclipse'))
        self.vectortiles_menu.addAction(self.versatileseclipse_action)
                
        'Versatiles Neutrino',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_versatiles.png")  
        self.versatilesneutrino_action = QAction(icon, u'Versatiles Neutrino', self.iface.mainWindow())
        self.versatilesneutrino_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Versatiles Neutrino'))
        self.vectortiles_menu.addAction(self.versatilesneutrino_action)


        self.vectortiles_menu.addSeparator()
        ############################################
        # Vgrid
        ###########################################
        'Vgrid Bright',
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vgrid.png")  
        self.vgridbright_action = QAction(icon, u'Vgrid Bright', self.iface.mainWindow())
        self.vgridbright_action.triggered.connect(lambda: hcmgis_vectortiles_basemap('Vgrid Bright'))
        self.vectortiles_menu.addAction(self.vgridbright_action)

        ##https://mc.bbbike.org/mc/?num=2&mt0=mapnik&mt1=watercolor
        #https://gitlab.com/GIS-projects/Belgium-XYZ-tiles/tree/b538df2c2de0d16937641742f25e4709ca94e42e
        
        ############################################
        # Add Raster Tile Basemaps
        ############################################

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


        self.basemap_menu.addSeparator()
        #############
        #Bing Virtual Earth
        #############
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_bing.png")
        self.bingaerial_action = QAction(icon, u'Bing Virtual Earth', self.iface.mainWindow())
        self.bingaerial_action.triggered.connect(lambda: hcmgis_basemap('Bing Virtual Earth'))
        self.basemap_menu.addAction(self.bingaerial_action)

        self.basemap_menu.addSeparator()
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

        self.basemap_menu.addSeparator()
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
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        # self.esridelorme_action = QAction(icon, u'ESri DeLorme', self.iface.mainWindow())
        # self.esridelorme_action.triggered.connect(lambda: hcmgis_basemap('ESri DeLorme'))
        # self.basemap_menu.addAction(self.esridelorme_action)

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
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_esri.png")
        # self.esriocean_action = QAction(icon, u'Esri Ocean', self.iface.mainWindow())
        # self.esriocean_action.triggered.connect(lambda: hcmgis_basemap('Esri Ocean'))
        # self.basemap_menu.addAction(self.esriocean_action)

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

        self.basemap_menu.addSeparator()
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


        # self.basemap_menu.addSeparator()
        # #Stamen Toner
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamentoner_action = QAction(icon, u'Stamen Toner', self.iface.mainWindow())
        # self.stamentoner_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner'))		
        # self.basemap_menu.addAction(self.stamentoner_action)

        # # Stamen Toner Background
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamentonerbkg_action = QAction(icon, u'Stamen Toner Background', self.iface.mainWindow())
        # self.stamentonerbkg_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Background'))		
        # self.basemap_menu.addAction(self.stamentonerbkg_action)

        # # Stamen Toner Hybrid
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamentonerhybrid_action = QAction(icon, u'Stamen Toner Hybrid', self.iface.mainWindow())
        # self.stamentonerhybrid_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Hybrid'))		
        # self.basemap_menu.addAction(self.stamentonerhybrid_action)

        # # Stamen Toner Lite
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamentonerlite_action = QAction(icon, u'Stamen Toner Lite', self.iface.mainWindow())
        # self.stamentonerlite_action.triggered.connect(lambda: hcmgis_basemap('Stamen Toner Lite'))		
        # self.basemap_menu.addAction(self.stamentonerlite_action)
        
        # # Stamen Terrain
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamenterrain_action = QAction(icon, u'Stamen Terrain', self.iface.mainWindow())
        # self.stamenterrain_action.triggered.connect(lambda: hcmgis_basemap('Stamen Terrain'))		
        # self.basemap_menu.addAction(self.stamenterrain_action)

        # # Stamen Terrain Background
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamenterrainbkg_action = QAction(icon, u'Stamen Terrain Background', self.iface.mainWindow())
        # self.stamenterrainbkg_action.triggered.connect(lambda: hcmgis_basemap('Stamen Terrain Background'))		
        # self.basemap_menu.addAction(self.stamenterrainbkg_action)
        
        # # Stamen Watercolor
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_stamen.png")
        # self.stamenwatercolor_action = QAction(icon, u'Stamen Watercolor', self.iface.mainWindow())
        # self.stamenwatercolor_action.triggered.connect(lambda: hcmgis_basemap('Stamen Watercolor'))		
        # self.basemap_menu.addAction(self.stamenwatercolor_action)
        
        # self.basemap_menu.addSeparator()        
        # # NASA
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_nasa_black.png")
        # self.nasa_black_action = QAction(icon, u'NASA Black Marble', self.iface.mainWindow())
        # self.nasa_black_action.triggered.connect(lambda: hcmgis_basemap('NASA Black Marble'))		
        # self.basemap_menu.addAction(self.nasa_black_action)


        # self.basemap_menu.addSeparator()
        # # Wikimedia Maps
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_wikimedia.png")
        # self.wikimedia_action = QAction(icon, u'Wikimedia Maps', self.iface.mainWindow())
        # self.wikimedia_action.triggered.connect(lambda: hcmgis_basemap('Wikimedia Maps'))
        # self.basemap_menu.addAction(self.wikimedia_action)
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
        self.basemap_menu.addSeparator()
        #Viet Ban do
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vbd.png")
        self.hcmgis_vbd_action = QAction(icon, u'Vietbando Maps', self.iface.mainWindow())
        self.hcmgis_vbd_action.triggered.connect(lambda: hcmgis_basemap('Vietbando Maps'))
        self.basemap_menu.addAction(self.hcmgis_vbd_action)
       
        #BecaGIS Maps
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_becamaps.png")
        self.hcmgis_osm_action = QAction(icon, u'BecaGIS Maps', self.iface.mainWindow())
        self.hcmgis_osm_action.triggered.connect(lambda: hcmgis_basemap('BecaGIS Maps'))		
        self.basemap_menu.addAction(self.hcmgis_osm_action)

        #HCMC OneMap
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_dxcenter.png")
        self.hcmgis_osm_action = QAction(icon, u'HCMC OneMap', self.iface.mainWindow())
        self.hcmgis_osm_action.triggered.connect(lambda: hcmgis_basemap('HCMC OneMap'))		
        self.basemap_menu.addAction(self.hcmgis_osm_action)

        self.basemap_menu.addSeparator()
        ##############################
        # F4map - 2D
        #############################
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_vgrid.png")
        self.f4map_action = QAction(icon, u'Vgrid', self.iface.mainWindow())
        self.f4map_action.triggered.connect(lambda: hcmgis_basemap('Vgrid'))
        self.basemap_menu.addAction(self.f4map_action)




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
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_open.png")
        self.opendata_menu = QMenu(u'Download OpenData')
        self.hcmgis_add_submenu2(self.opendata_menu, icon)


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

        #Global Administrative Areas by Country from Who's On First (WOF)
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_wof.png")
        self.wof_action = QAction(icon, u'Global Administrative Areas by Country from WOF', self.iface.mainWindow())
        self.wof_action.triggered.connect(self.wof)
        self.opendata_menu.addAction(self.wof_action)

        #Building Footprints from Microsoft
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_bing.png")
        self.microsoft_action = QAction(icon, u'Microsoft Building Footprints - Releases', self.iface.mainWindow())
        self.microsoft_action.triggered.connect(self.microsoft)
        self.opendata_menu.addAction(self.microsoft_action)

        #Building Footprints from Microsoft
        self.hcmgis_add_submenu(self.opendata_menu)
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_bing.png")
        self.global_microsoft_action = QAction(icon, u'Microsoft Building Footprints - Global', self.iface.mainWindow())
        self.global_microsoft_action.triggered.connect(self.global_microsoft)
        self.opendata_menu.addAction(self.global_microsoft_action)

        #HCMGIS OpenData
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_basemaps.png")
        self.opendata_action = QAction(icon, u'BecaGIS OpenData and more...', self.iface.mainWindow())
        self.opendata_action.triggered.connect(self.opendata)
        self.opendata_menu.addAction(self.opendata_action)


        # Batch Converter Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_batchconverter.png")
        self.batch_converter_menu = QMenu(u'Batch Converter')
        self.hcmgis_add_submenu2(self.batch_converter_menu, icon)


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


        # VN-2000 Projections submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_projections.png")
        self.projections_menu = QMenu(u'VN-2000/TM-3')
        self.hcmgis_add_submenu2(self.projections_menu, icon)


        # VN-2000 Projections
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_projections.png")
        self.projections_action = QAction(icon, u'EPSG Code for VN-2000/TM-3', self.iface.mainWindow())
        self.projections_action.triggered.connect(self.projections)
        self.projections_menu.addAction(self.projections_action)


        # Geoprocessing submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_geoprocess.png")
        # self.geoprocessing_menu = QMenu(u'Geometry Processing')
        # self.hcmgis_add_submenu2(self.geoprocessing_menu, icon)

        # # Split Polygon Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_split_polygon.png")
        # self.split_polygon_action = QAction(icon, u'Split Polygons by Voronoi Diagram', self.iface.mainWindow())
        # self.split_polygon_action.triggered.connect(self.splitpolygon)
        # self.geoprocessing_menu.addAction(self.split_polygon_action)

        # Media Axis Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_skeleton.png")
        # self.medialaxis_action = QAction(icon, u'Skeleton/ Medial Axis', self.iface.mainWindow())
        # self.medialaxis_action.triggered.connect(self.medialaxis)
        # self.geoprocessing_menu.addAction(self.medialaxis_action)

        # # Centerline Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_centerline.png")
        # self.centerline_action = QAction(icon, u"Centerline in Polygons' Gaps", self.iface.mainWindow())
        # self.centerline_action.triggered.connect(self.centerline)
        # self.geoprocessing_menu.addAction(self.centerline_action)

        # Closest pair of Points Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_closestpair.png")
        # self.closestpair_action = QAction(icon, u"Closest/ farthest pair of Points", self.iface.mainWindow())
        # self.closestpair_action.triggered.connect(self.closestpair)
        # self.geoprocessing_menu.addAction(self.closestpair_action)


        # Largest Empty Circle Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_lec.png")
        # self.lec_action = QAction(icon, u"Largest Empty Circle", self.iface.mainWindow())
        # self.lec_action.triggered.connect(self.lec)
        # self.geoprocessing_menu.addAction(self.lec_action)



        # Calculate Attribute submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/hcmgis_calculator.png")
        self.tool_menu = QMenu(u'Calculate Field')
        self.hcmgis_add_submenu2(self.tool_menu, icon)



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

    def wof(self):
        dialog = hcmgis_wof_dialog(self.iface)
        dialog.exec_()

    def microsoft(self):
        dialog = hcmgis_microsoft_dialog(self.iface)
        dialog.exec_()

    def global_microsoft(self):
        dialog = hcmgis_global_microsoft_dialog(self.iface)
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

    # def splitpolygon(self):
    #     dialog = hcmgis_split_polygon_dialog(self.iface)
    #     dialog.exec_()

    # def medialaxis(self):
    #     dialog = hcmgis_medialaxis_dialog(self.iface)
    #     dialog.exec_()

    # def centerline(self):
    #     dialog = hcmgis_centerline_dialog(self.iface)
    #     dialog.exec_()

    # def closestpair(self):
    #     dialog = hcmgis_closestpair_dialog(self.iface)
    #     dialog.exec_()

    # def lec(self):
    #     dialog = hcmgis_lec_dialog(self.iface)
    #     dialog.exec_()


    # def merge(self):
    #     dialog = hcmgis_merge_dialog(self.iface)
    #     dialog.exec_()

    # def split(self):
    #     dialog = hcmgis_split_dialog(self.iface)
    #     dialog.exec_()

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

