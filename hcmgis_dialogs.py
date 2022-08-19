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
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from owslib.wfs import WebFeatureService
#from owslib.ogcapi import Features
from qgis.gui import QgsMessageBar
import qgis.utils
from glob import glob
import urllib, re, ssl
from time import sleep
from xml.etree.ElementTree import XML, fromstring
import webbrowser



try:
    from .hcmgis_library import *
except:
    from hcmgis_library import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from hcmgis_opendata_form import *
from hcmgis_geofabrik_form import *
from hcmgis_gadm_form import *
from hcmgis_microsoft_form import *
from hcmgis_global_microsoft_form import *

from hcmgis_font_convert_form import *
from hcmgis_split_field_form import *
from hcmgis_merge_field_form import *
from hcmgis_medialaxis_form import *
from hcmgis_centerline_form import *
from hcmgis_closestpair_form import *
from hcmgis_lec_form import *
from hcmgis_customprojections_form import *
from hcmgis_format_convert_form import *
from hcmgis_csv2shp_form import *
from hcmgis_txt2csv_form import *
from hcmgis_xls2csv_form import *
from hcmgis_mapbox_form import *
from hcmgis_split_polygon_form import *



# ------------------------------------------------------------------------------
#    hcmgis_dialog - base class for hcmgis dialogs containing utility functions
# ------------------------------------------------------------------------------
class hcmgis_dialog(QtWidgets.QDialog):
    def __init__(self, iface):
        QtWidgets.QDialog.__init__(self)
        self.iface = iface

    def hcmgis_initialize_spatial_output_file_widget(self, file_widget, name, ext = ".shp"):
        initial_file_name = self.hcmgis_temp_file_name(name, ext)
        file_widget.setFilePath(initial_file_name)
        file_widget.setStorageMode(QgsFileWidget.SaveFile)

        file_widget.setFilter("ESRI Shapefile (*.shp);;GeoJSON (*.geojson);;KML (*.kml);;" + \
            "Spatialite (*.sqlite);;GPKG (*.gpkg)")

    def hcmgis_temp_file_name(self, name, ext):
        project = QgsProject.instance()
        home_path = project.homePath()
        if not home_path:
            home_path = os.path.expanduser('~')
        for x in range(1, 10):
            file_name = home_path + "/" +name + str(x) + ext
            if not os.path.isfile(file_name):
                return file_name
        return home_path + "/"+ name + ext


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

    def hcmgis_fill_list_widget_with_vector_layers(self, list_widget):
        # Add layers not in the list
        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                found = False
                for index in range(list_widget.count()):
                    if list_widget.item(index).text() == layer.name():
                        found = True
                        break
                if not found:
                    list_widget.addItem(layer.name())

        # Remove layers no longer on the map
        removed = []
        for index in range(list_widget.count()):
            found = False
            for layer in self.iface.mapCanvas().layers():
                if layer.name() == list_widget.item(index).text():
                    found = True
                    break
            if not found:
                removed.append(index)

        removed.reverse()
        for index in removed:
            item = list_widget.takeItem(index)
            item = None
            # list_widget.removeItemWidget(list_widget.item(index))   
  
    def hcmgis_set_status_bar(self, status_bar, status_lable):
        status_bar.setMinimum(0)
        status_bar.setMaximum(100)
        status_bar.setValue(0)
        status_bar.setFormat("Ready")
        self.status_bar = status_bar
        self.status_lable = status_lable

    def hcmgis_status_callback(self, percent_complete, lable):
        try:           
            self.status_lable.setText(lable)    
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

    server_types = ['WFS'
                    #'ArcGIS Feature Server'
                ]
    arcgis_servers = []
    arcgis_urls = []
    wfs_servers = ['HCMGIS OpenData',
                'OpenDevelopment Mekong',
                'OpenDevelopment Cambodia',
                'OpenDevelopment Lao',
                'OpenDevelopment Myanmar',
                'OpenDevelopment Vietnam',
                'ISTI-CNR Pisa',
                'Stanford University',
                'CAEARTE-CONAE',
                # 'OpenAPI',
                'IBGE',
                'INDE',
                # 'ISRIC Data Hub',
                'World Food Programme',
                # 'PUMA - World Bank Group' ,
                ]

    wfs_urls = [
        'https://opendata.hcmgis.vn/geoserver',
        'https://data.opendevelopmentmekong.net/geoserver/ODMekong',
        'https://data.opendevelopmentmekong.net/geoserver/ODCambodia',
        'https://data.opendevelopmentmekong.net/geoserver/ODLao',
        'https://data.opendevelopmentmekong.net/geoserver/ODMyanmar',
        'https://data.opendevelopmentmekong.net/geoserver/ODVietnam',
        'http://geoserver.d4science.org:80/geoserver',
        'https://geowebservices.stanford.edu:443/geoserver',        
        'http://ambiente.caearte.conae.gov.ar/geoserver',
        # 'http://openapi.aurin.org.au/public',
        'https://geoservicos.ibge.gov.br/geoserver',
        'https://geoservicos.inde.gov.br/geoserver',
        # 'https://data.isric.org/geoserver',
        'https://geonode.wfp.org/geoserver',
        # 'https://puma.worldbank.org/geoserver'
         ]
    
    def hcmgis_fill_table_widget_with_csv(self,table_widget, csv_file, status_callback = None):	       
        data = []
        with open(csv_file, 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
            labels = data[0]
        del data[0]
        nb_row = len(data)
        nb_col = len(data[0])
        table_widget.setRowCount(nb_row)
        table_widget.setColumnCount(nb_col)
        table_widget.setHorizontalHeaderLabels(labels)
        for row in range (nb_row):
            for col in range(nb_col):
                item = QTableWidgetItem(str(data[row][col]))
                table_widget.setItem(row, col, item)

       
        return
 

    def hcmgis_fill_table_widget_with_wfs_layers0(self,table_widget, idx, TxtTitle, TxtAbstract, status_callback = None):	
        table_widget.setRowCount(0) 
        TxtTitle.clear()
        TxtAbstract.clear() 
        self.Filter.clear()            		       
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            #wfs = urllib.request.urlopen(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities',context=ssl._create_unverified_context())
            #wfs = urllib.request.urlopen(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities')
            #wfs = requests.get(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities',verify = False)
            uri = self.wfs_urls[idx] +'/wfs?version=2.0.0&request=GetCapabilities'
            # print (uri)
            wfs = requests.get(uri, stream=True, allow_redirects=True, verify = False)
            project = QgsProject.instance()
            home_path = project.homePath()
            if not home_path:
                home_path = os.path.expanduser('~')
            filename = home_path + "/"+ str(self.wfs_servers[idx])  + ".xml"   
            print (filename)
            if  (wfs.status_code == 200):               
                f = open(filename, 'wb')                           
                for chunk in wfs.iter_content(chunk_size = 1024):
                    if not chunk:
                        break
                    f.write(chunk)                                                            
                f.close()
                    
            if wfs is not None:              
                #data = wfs.read().decode('utf-8')
                #data = wfs.text
                getcapabilities = open(filename, 'r') 
                data = getcapabilities.read()
                getcapabilities.close()
                os.remove(filename)
                # print (data)
                server_title_regex = r'<ows:Title>(.+?)</ows:Title>|<ows:Title/>'
                #server_title_pattern = re.compile(server_title_regex)
                
                server_abstract_regex = r'<ows:Abstract>(.+?)</ows:Abstract>|<ows:Abstract/>'
                #server_abstract_pattern = re.compile(server_abstract_regex)
                
                server_title = re.findall(server_title_regex,data,re.DOTALL)
                server_abstract = re.findall(server_abstract_regex,data,re.DOTALL)

                layer_name_regex = r'<Name>(.+?)</Name>'
                #layer_name_pattern  = re.compile(layer_name_regex)

                layer_title_regex = r'<Title>(.+?)</Title>|<Title/>'
                #layer_title_pattern  = re.compile(layer_title_regex)

                layer_name = re.findall(layer_name_regex,data,re.DOTALL)
                layer_title = re.findall(layer_title_regex,data,re.DOTALL)
                if len(server_title)>0:
                    TxtTitle.insertPlainText(server_title[0])
                if len (server_abstract)>0:
                    TxtAbstract.insertPlainText(server_abstract[0].replace('&#13;','')) #delete unwanted character before \n
                
                #QMessageBox.information(None, "Congrats",u'GetCapabilities completed! Now wait for a minute to load WFS Layers')

                if layer_name is not None:
                    # print (layer_name)                
                    for i in range (len(layer_name)):                       
                        # # Feature count
                        # r = requests.get(self.wfs_urls[idx]+'/wfs', params={
                        # 'service': 'WFS',
                        # 'version': '1.1',
                        # 'request': 'GetFeature',
                        # 'resultType': 'hits',
                        # 'typename': layer_name[i]
                        # })
                        # myxml = fromstring(r.content)
                        # feature_count = myxml.attrib['numberOfFeatures']
                        table_widget.insertRow(i)
                        table_widget.setItem(i,0, QTableWidgetItem(layer_name[i]))
                        table_widget.setItem(i,1, QTableWidgetItem(layer_title[i]))
                        # table_widget.setItem(i,2, QTableWidgetItem(feature_count))

                        table_widget.item(i,0).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        table_widget.item(i,1).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        status_callback((i/len(layer_name))*100,None)
                
                        status_callback(((i+1)/len(layer_name))*100,None)
                    message = str(i+1) + " WFS layers loaded"
                    self.LblWFSLayers.setText(message)
                    MessageBar = qgis.utils.iface.messageBar()
                    MessageBar.pushMessage(message, 0, 2)
                    self.Filter.setEnabled(True)
                    self.Filter.setFocus(True)

                else: return
            else: return
        except Exception as e:
            QMessageBox.warning(None, "WFS ERROR",str(e))	
        return    		        
    
    def hcmgis_fill_table_widget_with_wfs_layers(self,table_widget, idx, TxtTitle, TxtAbstract, status_callback = None):	
        table_widget.clear()          
        table_widget.setRowCount(0) 
        TxtTitle.clear()
        TxtAbstract.clear()
        columns = ['Name', 'Title']            
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels(columns)       		       
        try:
            wfs = WebFeatureService(self.wfs_urls[idx] +'/wfs', version = '2.0.0')             
            if wfs is not None:              
                TxtTitle.insertPlainText(wfs.identification.title)
                TxtAbstract.insertPlainText(wfs.identification.abstract)
                layer_names = list(wfs.contents)
                if layer_names is not None: 
                    i = 0
                    for layer_name  in layer_names:  
                        table_widget.insertRow(i)
                        table_widget.setItem(i,0, QTableWidgetItem(layer_name))
                        table_widget.setItem(i,1, QTableWidgetItem(wfs[layer_name].title))
                        table_widget.item(i,0).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        table_widget.item(i,1).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        i+=1
                        status_callback((i/len(layer_names))*100,None)

                    message = str(i) + " WFS layers loaded"
                    MessageBar = qgis.utils.iface.messageBar()
                    MessageBar.pushMessage(message, 0, 2)  		
                else: return
            else: return
        except Exception as e:
            QMessageBox.warning(None, "WFS ERROR",str(e))	
            return  
        
# --------------------------------------------------------
#    HCMGIS Opendata
# --------------------------------------------------------

class hcmgis_opendata_dialog(hcmgis_dialog, Ui_hcmgis_opendata_form):	
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.Filter.setFocus(True)
        QWidget.setTabOrder(self.Filter, self.TblWFSLayers)      
        self.TblWFSLayers.doubleClicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)	

        project = QgsProject.instance()
        home_path = project.homePath()
        if not home_path:
            home_path = os.path.expanduser('~')
        self.LinOutputFolder.setText(home_path)                                             
        self.ChkSaveShapefile.stateChanged.connect(self.toggleouputfolder)
        
        columns = ['Name', 'Title']            
        self.TblWFSLayers.setColumnCount(len(columns))
        self.TblWFSLayers.setHorizontalHeaderLabels(columns) 
        self.TblWFSLayers.resizeColumnsToContents()
        self.TblWFSLayers.resizeRowsToContents()
        self.TblWFSLayers.horizontalHeader().setStretchLastSection(True)	
        self.TblWFSLayers.doubleClicked.connect(self.run)

        self.Filter.setEnabled(False)
        self.Filter.valueChanged.connect(self.updateWFSTable)


        # self.TblWFSLayers.setDragDropMode(QAbstractItemView.DragOnly)  
        # self.TblWFSLayers.setDragEnabled(True) 
        
        self.cboServerType.currentIndexChanged.connect(self.updateServer)
        self.cboServerType.addItems(self.server_types)        
        self.cboServerName.setCurrentIndex(0)


        self.cboServerName.setCurrentIndex(-1)
        self.cboServerName.currentIndexChanged.connect(self.readwfs)
        self.CboFormat.setEnabled(False)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	

        self.cboServerName.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboServerName.setMaxVisibleItems(10)
        self.cboServerName.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded) 
        
     
    def updateWFSTable(self):
        name = self.Filter.text().lower()
        if (name != '' and name is not None):    
            visible_row = 0
            for row in range(self.TblWFSLayers.rowCount()):
                item0 = self.TblWFSLayers.item(row, 0) # Layer Name
                item1 = self.TblWFSLayers.item(row, 1) # Layer Title
                # if the search is *not* in the item's text *do not hide* the row
                if (name not in item0.text().lower() and name not in item1.text().lower()):
                    match = True               
                else: 
                    match = False
                    visible_row += 1
                self.TblWFSLayers.setRowHidden(row, match )
            if visible_row < self.TblWFSLayers.rowCount():
                self.LblWFSLayers.setText(str(visible_row) + ' WFS Layers filterd')
        else:
            for row in range(self.TblWFSLayers.rowCount()):
                self.TblWFSLayers.setRowHidden(row, False )
            self.LblWFSLayers.setText(str(self.TblWFSLayers.rowCount()) + ' WFS Layers loaded')

    def updateServer(self):
        self.cboServerName.clear()
        self.TxtTitle.clear()
        self.TxtAbstract.clear()
        self.TblWFSLayers.setRowCount(0)
        self.LblWFSLayers.setText('WFS Layers')

        if self.cboServerType.currentIndex() == 0:             #'WFS'
            self.cboServerName.addItems(self.wfs_servers)
            self.cboServerName.setCurrentIndex(0)

    def readwfs(self):
        if (self.cboServerName.currentIndex()>-1):
            self.hcmgis_set_status_bar(self.status,self.LblStatus)	
            self.LblStatus.clear()
            self.LblWFSLayers.setText('WFS Layers')
            #self.hcmgis_fill_table_widget_with_wfs_layers(self.TblWFSLayers,self.cboServerName.currentIndex(), self.TxtTitle,self.TxtAbstract,self.hcmgis_status_callback)           
            self.hcmgis_fill_table_widget_with_wfs_layers0(self.TblWFSLayers,self.cboServerName.currentIndex(), self.TxtTitle,self.TxtAbstract,self.hcmgis_status_callback)

    def togglesave(self):
        self.ChkSaveShapefile.setChecked(self.CboFormat.currentIndex()>0)

    def browse_outfile(self):
        newname = QFileDialog.getExistingDirectory(None, "Output Folder",self.LinOutputFolder.displayText())
        if newname != None:
            self.LinOutputFolder.setText(newname)
                    
    def toggleouputfolder(self,state):
        if state > 0:
            self.LinOutputFolder.setEnabled(True)
            self.BtnOutputFolder.setEnabled(True)
            self.CboFormat.setEnabled(True)
        else:
            self.LinOutputFolder.setEnabled(False)
            self.BtnOutputFolder.setEnabled(False)	
            self.CboFormat.setEnabled(False)   
   
    def run(self):
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
        self.LblStatus.clear()
        idx = self.cboServerName.currentIndex()
        opendata_url =self.wfs_urls[idx]
        outdir = unicode(self.LinOutputFolder.displayText())
        wfs_format  = self.CboFormat.currentText().lower()
        ext = "." + wfs_format
        if (wfs_format == "json"):
            wfs_format = "application/json"
        elif (wfs_format == "shape-zip"):
            ext = ".zip"
        elif (wfs_format == "xls"):
            wfs_format = "excel"
        elif (wfs_format == "xlsx"):
            wfs_format = "excel2007"
        elif (wfs_format == "GML2" or wfs_format == "GML3" ):
            ext = '.gml'

        layernames = []	
        rows = []	
        for index in self.TblWFSLayers.selectedIndexes():
            if index.row() not in rows:
                rows.append(index.row())
        for row_index in rows:
            if (self.TblWFSLayers.item(row_index, 0) is not None):
                layernames.append(self.TblWFSLayers.item(row_index, 0).text())
        # print(rows)
        # print(layernames)
        ii = 0        
        if layernames is not None:
            for layer_name in layernames:
                uri = opendata_url + "/wfs?version=1.0.0&request=GetFeature&typename="+ str(layer_name)                       	
                #uri = opendata_url + "/ows?service=WFS&request=GetFeature&typename="+ str(layer_name)                       	
                if (not self.ChkSaveShapefile.isChecked()):
                    try:
                        success = qgis.utils.iface.addVectorLayer(uri, layer_name,"WFS")
                        if success:                           
                            ii+=1		
                            self.LblStatus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers loaded")	    			
                            percent_complete = ii/len(layernames)*100
                            self.status.setValue(percent_complete)
                            message = str(int(percent_complete)) + "%"
                            self.status.setFormat(message)                            
                    except Exception as e:                      
                        QMessageBox.critical(self.iface.mainWindow(), "WFS", e)                                                                  
                else:   
                    uri = opendata_url + "/wfs?version=1.0.0&request=GetFeature&typename="+ str(layer_name)   
                    #uri = opendata_url + "/ows?service=WFS&request=GetFeature&typename="+ str(layer_name)                       	                                       	                   
                    uri += '&outputFormat='
                    uri += wfs_format
                    try:
                        # filename = outdir + "/"+ str(layer_name).replace(":","_") + ext
                        # ssl._create_default_https_context = ssl._create_unverified_context
                        # #urllib.request.urlretrieve(uri,filename,context=ssl._create_unverified_context())
                        # urllib.request.urlretrieve(uri,filename)
                        # layer = QgsVectorLayer(filename, QFileInfo(filename).baseName(), 'ogr')
                        # layer.dataProvider().setEncoding(u'UTF-8')
                        # if (layer.isValid()):                     
                        #     QgsProject.instance().addMapLayer(layer)                         
                        #     ii+=1		
                        #     self.LblStatus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers saved and loaded")	
                        #     percent_complete = ii/len(layernames)*100
                        #     self.status.setValue(percent_complete)
                        #     message = str(int(percent_complete)) + "%"
                        #     self.status.setFormat(message)  
                        headers = ""
                        contents = requests.get(uri, headers=headers, stream=True, allow_redirects=True, verify = False)
                        filename = outdir + "/"+ str(layer_name).replace(":","_") + ext    
                        # total_size = int(len(contents.content))
                        # total_size_MB = round(total_size*10**(-6),2)
                        # chunk_size = int(total_size/100)                        
                        if  (contents.status_code == 200):
                            #print ('total_length MB:', total_size_MB)
                            #i = 0
                            f = open(filename, 'wb')                           
                            for chunk in contents.iter_content(chunk_size = 1024):
                                if not chunk:
                                    break
                                f.write(chunk)
                                # self.status.setValue(i)
                                # message = str(int(i)) + "%"
                                # self.status.setFormat(message) 
                                # self.iface.statusBarIface().showMessage(message)
                                # self.hcmgis_status_callback(i/1024, None)
                                # print (str(i))
                                #i+=1                                                      
                            f.close()
                            layer = QgsVectorLayer(filename, QFileInfo(filename).baseName(), 'ogr')
                            layer.dataProvider().setEncoding(u'UTF-8')
                            if (layer.isValid()):                     
                                QgsProject.instance().addMapLayer(layer)                         
                                ii+=1		
                                self.LblStatus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers saved and loaded")	
                                percent_complete = ii/len(layernames)*100
                                self.status.setValue(percent_complete)
                                message = str(int(percent_complete)) + "%"
                                self.status.setFormat(message)  
                    except Exception as e:
                        qgis.utils.iface.addVectorLayer(uri, str(layer_name),"WFS")    
                        QMessageBox.critical(self.iface.mainWindow(), "WFS", e)
            qgis.utils.iface.zoomToActiveLayer()
                                 
        return		


class hcmgis_geofabrik_dialog(hcmgis_dialog, Ui_hcmgis_geofabrik_form):		
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)	
        
        self.cboRegion.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboCountry.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboCountry.setMaxVisibleItems(10)
        self.cboCountry.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.cboProvince.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboProvince.setMaxVisibleItems(10)
        self.cboProvince.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)


        project = QgsProject.instance()
        home_path = project.homePath()
        if not home_path:
            home_path = os.path.expanduser('~')
        self.LinOutputFolder.setText(home_path)    
        self.cboRegion.addItems(self.region)
        self.cboRegion.currentIndexChanged.connect(self.loadcountry)   
        self.cboRegion.setCurrentIndex(-1) 
        self.cboCountry.setCurrentIndex(-1) 
        self.cboCountry.setEnabled(False)
        self.cboCountry.currentIndexChanged.connect(self.loadprovince)
        self.cboProvince.setEnabled(False)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)		

    ##################### Region
    region = ['Africa','Antarctica','Asia','Australia and Oceania','Central America','Europe','North America','South America']
    region_name = []
    for reg in region:
        reg_name = reg.replace(' and ','-').replace(' ','-').lower()
        region_name.append(reg_name)
    
    ##################### Asia
    asia = ['Afghanistan','Armenia','Azerbaijan','Bangladesh','Bhutan','Cambodia','China','GCC States','India','Indonesia',\
                'Iran','Iraq','Israel and Palestine','Japan','Jordan','Kazakhstan','Kyrgyzstan','Laos','Lebanon','Malaysia, Singapore, and Brunei',\
                'Maldives','Mongolia','Myanmar','Nepal','North Korea','Pakistan','Philippines','Russian Federation','South Korea','Sri Lanka',\
                'Syria','Taiwan','Tajikistan','Thailand','Turkmenistan','Uzbekistan','Vietnam','Yemen']
    asia_name= []
    for country in asia:
        country_name = country.replace('Israel and Palestine','israel-and-palestine' ).replace('Malaysia, Singapore, and Brunei','malaysia-singapore-brunei').replace('Russian Federation','russia').replace(' ','-').lower()
        asia_name.append(country_name)
    
    japan_state = ['Chubu region','Chugoku region','Hokkaido','Kansai region','Kanto region','Kyushu','Shikoku','Tohoku region']
    japan_state_name= []
    for state in japan_state:
        state_name = state.replace(' region','').lower()
        japan_state_name.append(state_name)


    ##################### Africa
    africa =['Algeria','Angola','Benin','Botswana','Burkina Faso','Burundi','Cameroon','Canary Islands','Cape Verde','Central African Republic',\
            'Chad','Comores','Congo (Republic/Brazzaville)','Congo (Democratic Republic/Kinshasa)','Djibouti','Egypt','Equatorial Guinea','Eritrea','Ethiopia','Gabon',\
            'Ghana','Guinea','Guinea-Bissau','Ivory Coast','Kenya','Lesotho','Liberia','Libya','Madagascar','Malawi',\
            'Mali','Mauritania','Mauritius','Morocco','Mozambique','Namibia','Niger','Nigeria','Rwanda','Saint Helena, Ascension, and Tristan da Cunha',\
            'Sao Tome and Principe','Senegal and Gambia','Seychelles','Sierra Leone','Somalia','South Africa','South Sudan','Sudan','Swaziland',\
            'Tanzania','Togo','Tunisia','Uganda','Zambia','Zimbabwe',\
            'South Africa (includes Lesotho)'] #special region
    africa_name = []
    for country in africa:
        country_name = country.replace('Congo (Republic/Brazzaville)','congo-brazzaville').replace('Congo (Democratic Republic/Kinshasa)','congo-democratic-republic')\
        .replace('South Africa (includes Lesotho)','south-africa-and-lesotho').replace(' ','-').replace(',','').lower()
        africa_name.append(country_name)
        
    ##################### Australia
    australia = ['Australia','Cook Islands','Fiji','Kiribati','Marshall Islands','Micronesia','Nauru','New Caledonia','New Zealand','Niue',\
                'Palau','Papua New Guinea','Samoa','Solomon Islands','Tonga','Tuvalu','Vanuatu']
    australia_name = []
    for country in australia:
        country_name = country.replace(' ','-').lower()
        australia_name.append(country_name)

    ##################### Central America
    centralamerica= ['bahamas','Belize','Cuba','Guatemala','Haiti and Dominican Republic','Jamaica','Nicaragua']
    centralamerica_name = []
    for country in centralamerica:
        country_name = country.replace('Dominican Republic','domrep').replace(' ','-').lower()
        centralamerica_name.append(country_name)
    
    ##################### Europe
    europe= ['Albania','Andorra','Austria','Azores','Belarus','Belgium','Bosnia-Herzegovina','Bulgaria','Croatia','Cyprus',\
            'Czech Republic','Denmark','Estonia','Faroe Islands','Finland','France','Georgia (Eastern Europe)','Germany','Great Britain','Greece',\
            'Hungary','Iceland','Ireland and Northern Ireland','Isle of Man','Italy','Kosovo','Latvia','Liechtenstein','Lithuania','Luxembourg',\
            'Macedonia','Malta','Moldova','Monaco','Montenegro','Netherlands','Norway','Poland','Portugal','Romania',\
            'Russian Federation','Serbia','Slovakia','Slovenia','Spain','Sweden','Switzerland','Turkey','Ukraine (with Crimea)',\
            'Alps','Britain and Ireland','Germany, Austria, Switzerland']#special regions
    europe_name = []
    for country in europe:
        country_name = country.replace('Georgia (Eastern Europe)','georgia').replace('Ukraine (with Crimea)','ukraine').replace('Germany, Austria, Switzerland','dach').\
            replace('Russian Federation','russia').replace(' ','-').lower()
        europe_name.append(country_name)
    france_state = ['Alsace','Aquitaine','Auvergne','Basse-Normandie','Bourgogne','Bretagne','Centre','Champagne Ardenne','Corse','Franche Comte',\
                    'Guadeloupe','Guyane','Haute-Normandie','Ile-de-France','Languedoc-Roussillon','Limousin','Lorraine','Martinique','Mayotte','Midi-Pyrenees',\
                    'Nord-Pas-de-Calais','Pays de la Loire','Picardie','Poitou-Charentes','Provence Alpes-Cote-d''Azur','Reunion','Rhone-Alpes']
    france_state_name= []
    for state in france_state:
        state_name = state.replace(' ','-').lower()
        france_state_name.append(state_name)

    germany_state = ['Baden-Wurttemberg','Bayern','Berlin','Brandenburg (mit Berlin)','Bremen','Hamburg','Hessen','Mecklenburg-Vorpommern','Niedersachsen','Nordrhein-Westfalen',\
                    'Rheinland-Pfalz','Saarland','Sachsen','Sachsen-Anhalt','Schleswig-Holstein','Thuringen']
    germany_state_name= []
    for state in germany_state:
        state_name = state.replace('Brandenburg (mit Berlin)','brandenburg').lower()
        germany_state_name.append(state_name)
    
    great_britain_state = ['England','Scotland','Wales']
    great_britain_state_name = ['england','scotland','wales']	

    italy_state = ['Centro', 'Isole', 'Nord-Est', 'Nord-Ovest', 'Sud']
    italy_state_name =[]
    for state in italy_state:
        state_name = state.lower()
        italy_state_name.append(state_name)

    netherlands_state = ['Drenthe','Flevoland','Friesland','Gelderland','Groningen','Limburg','Noord-Brabant','Noord-Holland','Overijssel','Utrecht',\
                    'Zeeland','Zuid-Holland']
    netherlands_state_name= []
    for state in netherlands_state:
        state_name = state.lower()
        netherlands_state_name.append(state_name)
    

    poland_state =['Lower Silesian Voivodeship','Kuyavian-Pomeranian Voivodeship','Lodzkie Voivodeship','Lublin Voivodeship','Lubusz Voivodeship',\
        'Lesser Poland Voivodeship','Mazovian Voivodeship','Opole Voivodeship','Subcarpathian Voivodeship','Podlaskie Voivodeship',\
        'Pomeranian Voivodeship','Silesian Voivodeship','Swietokrzyskie Voivodeship','Warmian-Masurian Voivodeship','Greater Poland Voivodeship','West Pomeranian Voivodeship']
    poland_state_name= ['dolnoslaskie', 'kujawsko-pomorskie', 'lodzkie','lubelskie', 'lubuskie',\
                        'malopolskie', 'mazowieckie', 'opolskie','podkarpackie','podlaskie',\
                        'pomorskie', 'slaskie', 'swietokrzyskie', 'warminsko-mazurskie', 'wielkopolskie','zachodniopomorskie']
    

    russian_federation_state = ['Central Federal District','Crimean Federal District','Far Eastern Federal District','North Caucasus Federal District','Northwestern Federal District',\
            'Siberian Federal District','South Federal District','Ural Federal District','Volga Federal District','Kaliningrad']
    russian_federation_state_name = []
    for state in russian_federation_state:
        state_name = state.replace('Federal','fed').replace(' ','-').lower()
        russian_federation_state_name.append(state_name)
    
    ##################### North America
    northamerica= ['Canada','Greenland','Mexico','United States of America',\
        'US Midwest','US Northeast','US Pacific','US South','US West']# special regions of US
    northamerica_name = []
    for country in northamerica:
        country_name = country.replace('United States of America','us').replace(' ','-').lower()
        northamerica_name.append(country_name)
    us_state = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida',\
                'Georgia (US State)','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine',\
                'Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire',\
                'New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Puerto Rico',\
                'Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',\
                'Wisconsin','Wyoming']
    us_state_name = []
    for state in us_state:
        state_name = state.replace('Georgia (US State)','georgia').replace(' ','-').lower()
        us_state_name.append(state_name)

    canada_state = ['Alberta','British Columbia','Manitoba','New Brunswick','Newfoundland and Labrador','Northwest Territories','Nova Scotia','Nunavut','Ontario','Prince Edward Island',\
                    'Quebec','Saskatchewan','Yukon']
    canada_state_name = []
    for state in canada_state:
        state_name = state.replace(' ','-').lower()
        canada_state_name.append(state_name)
    
    ##################### South America
    southamerica= ['Argentina','Bolivia','Brazil','Chile','Colombia','Ecuador','Paraguay','Peru','Suriname','Uruguay','Venezuela']
    southamerica_name = []
    for country in southamerica:
        country_name = country.replace(' ','-').lower()
        southamerica_name.append(country_name)
    
    brazil_state = ['centro-oeste','nordeste','norte','sudeste','sul']
    brazil_state_name = brazil_state


    def browse_outfile(self):
        newname = QFileDialog.getExistingDirectory(None, "Output Folder",self.LinOutputFolder.displayText())

        if newname != None:
            self.LinOutputFolder.setText(newname)
                    
    def loadcountry(self):
        self.cboCountry.clear()
        self.cboCountry.setEnabled(True)
        if 	(self.cboRegion.currentText() == 'Asia'):
            self.cboCountry.addItems(self.asia)
        elif (self.cboRegion.currentText() == 'Africa'):
            self.cboCountry.addItems(self.africa)
            self.cboCountry.insertSeparator(len(self.africa)-1)
        elif (self.cboRegion.currentText() == 'Antarctica'):
            self.cboCountry.addItem('Antarctica')
        elif (self.cboRegion.currentText() == 'Australia and Oceania'):
            self.cboCountry.addItems(self.australia)
        elif (self.cboRegion.currentText() == 'Central America'):
            self.cboCountry.addItems(self.centralamerica)
        elif (self.cboRegion.currentText() == 'Europe'):
            self.cboCountry.addItems(self.europe)
            self.cboCountry.insertSeparator(len(self.europe)-3)
        elif (self.cboRegion.currentText() == 'North America'):
            self.cboCountry.addItems(self.northamerica)
            self.cboCountry.insertSeparator(len(self.northamerica)-5)
        elif (self.cboRegion.currentText() == 'South America'):
            self.cboCountry.addItems(self.southamerica)
    
    def loadprovince(self):
        self.cboProvince.clear()
        self.cboProvince.setEnabled(True)
        if 	(self.cboCountry.currentText() == 'United States of America'):
            self.cboProvince.addItems(self.us_state)
        elif (self.cboCountry.currentText() == 'Canada'):
            self.cboProvince.addItems(self.canada_state)
        elif (self.cboCountry.currentText() == 'Brazil'):
            self.cboProvince.addItems(self.brazil_state)
        elif (self.cboCountry.currentText() == 'France'):
            self.cboProvince.addItems(self.france_state)
        elif (self.cboCountry.currentText() == 'Germany'):
            self.cboProvince.addItems(self.germany_state)
        elif (self.cboCountry.currentText() == 'Great Britain'):
            self.cboProvince.addItems(self.great_britain_state)
        elif (self.cboCountry.currentText() == 'Italy'):
            self.cboProvince.addItems(self.italy_state)
        elif (self.cboCountry.currentText() == 'Netherlands'):
            self.cboProvince.addItems(self.netherlands_state)	
        elif (self.cboCountry.currentText() == 'Poland'):
            self.cboProvince.addItems(self.poland_state)
        elif (self.cboCountry.currentText() == 'Russian Federation'):
            self.cboProvince.addItems(self.russian_federation_state)	
        elif (self.cboCountry.currentText() == 'Japan'):
            self.cboProvince.addItems(self.japan_state)	
        self.cboProvince.setCurrentIndex(-1)
        
    
    def run(self):
        outdir = unicode(self.LinOutputFolder.displayText())
        if (self.cboProvince.currentIndex()<0):
            if (self.cboRegion.currentText() == 'Asia'):
                country_idx = self.asia.index(self.cboCountry.currentText())
                if self.cboCountry.currentText() == 'Russian Federation':
                    message = hcmgis_geofabrik('',self.asia_name[country_idx], outdir,self.hcmgis_status_callback)	
                else:
                    message = hcmgis_geofabrik('asia',self.asia_name[country_idx], outdir,self.hcmgis_status_callback)	
            elif (self.cboRegion.currentText() == 'Africa'):
                country_idx = self.africa.index(self.cboCountry.currentText())
                message = hcmgis_geofabrik('africa',self.africa_name[country_idx], outdir,self.hcmgis_status_callback)	
            elif (self.cboRegion.currentText() == 'Antarctica'):
                message = hcmgis_geofabrik('','antarctica', outdir)	
            elif (self.cboRegion.currentText() == 'Australia and Oceania'):
                country_idx = self.australia.index(self.cboCountry.currentText())
                message = hcmgis_geofabrik('australia-oceania',self.australia_name[country_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboRegion.currentText() == 'Central America'):
                country_idx = self.centralamerica.index(self.cboCountry.currentText())
                message = hcmgis_geofabrik('central-america',self.centralamerica_name[country_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboRegion.currentText() == 'Europe'):
                country_idx = self.europe.index(self.cboCountry.currentText())
                if self.cboCountry.currentText() == 'Russian Federation':
                    message = hcmgis_geofabrik('',self.europe_name[country_idx], outdir,self.hcmgis_status_callback)	
                else:
                    message = hcmgis_geofabrik('europe',self.europe_name[country_idx], outdir,self.hcmgis_status_callback)	
            elif (self.cboRegion.currentText() == 'North America'):
                country_idx = self.northamerica.index(self.cboCountry.currentText())
                message = hcmgis_geofabrik('north-america',self.northamerica_name[country_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboRegion.currentText() == 'South America'):
                country_idx = self.southamerica.index(self.cboCountry.currentText())
                message = hcmgis_geofabrik('south-america',self.southamerica_name[country_idx], outdir,self.hcmgis_status_callback)
        else:
            if (self.cboCountry.currentText() == 'Japan'):
                state_idx = self.japan_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('asia','japan',self.japan_state_name[state_idx], outdir,self.hcmgis_status_callback)	
            
            elif (self.cboCountry.currentText() == 'France'):
                state_idx = self.france_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','france',self.france_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Germany'):
                state_idx = self.germany_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','germany',self.germany_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Great Britain'):
                state_idx = self.great_britain_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','great-britain',self.great_britain_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Italy'):
                state_idx = self.italy_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','italy',self.italy_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Netherlands'):
                state_idx = self.netherlands_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','netherlands',self.netherlands_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Poland'):
                state_idx = self.poland_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('europe','poland',self.poland_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Russian Federation'):
                state_idx = self.russian_federation_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('','russia',self.russian_federation_state_name[state_idx], outdir,self.hcmgis_status_callback)
                    
            elif (self.cboCountry.currentText() == 'United States of America'):
                state_idx = self.us_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('north-america','us',self.us_state_name[state_idx], outdir,self.hcmgis_status_callback)
            elif (self.cboCountry.currentText() == 'Canada'):
                state_idx = self.canada_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('north-america','canada',self.canada_state_name[state_idx], outdir,self.hcmgis_status_callback)
            
            elif (self.cboCountry.currentText() == 'Brazil'):
                state_idx = self.brazil_state.index(self.cboProvince.currentText())
                message = hcmgis_geofabrik2('south-america','brazil',self.brazil_state_name[state_idx], outdir,self.hcmgis_status_callback)
        return		

########################################################
# GADM
#########################################################
class hcmgis_gadm_dialog(hcmgis_dialog, Ui_hcmgis_gadm_form):	
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)        
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)	
        project = QgsProject.instance()
        home_path = project.homePath()
        if not home_path:
            home_path = os.path.expanduser('~')
        self.LinOutputFolder.setText(home_path)    
        self.cboCountry.addItems(self.country)
        self.cboCountry.currentIndexChanged.connect(self.updateLOD)   
        self.cboCountry.setCurrentIndex(-1) 
        self.LinLOD.setText('')
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
        
        self.cboCountry.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboCountry.setMaxVisibleItems(10)
        self.cboCountry.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)         

    country = ['Afghanistan','Akrotiri and Dhekelia','Åland','Albania','Algeria','American Samoa','Andorra','Angola','Anguilla','Antarctica',\
            'Antigua and Barbuda','Argentina','Armenia','Aruba','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh',\
            'Barbados','Belarus','Belgium','Belize','Benin','Bermuda','Bhutan','Bolivia','Bonaire, Saint Eustatius and Saba','Bosnia and Herzegovina',\
            'Botswana','Bouvet Island','Brazil','British Indian Ocean Territory','British Virgin Islands','Brunei','Bulgaria','Burkina Faso','Burundi','Cambodia',\
            'Cameroon','Canada','Cape Verde','Caspian Sea','Cayman Islands','Central African Republic','Chad','Chile','China','Christmas Island',\
            'Clipperton Island','Cocos Islands','Colombia','Comoros','Cook Islands','Costa Rica','Côte d''Ivoire','Croatia','Cuba','Curaçao',\
            'Cyprus','Czech Republic','Democratic Republic of the Congo','Denmark','Djibouti','Dominica','Dominican Republic','East Timor','Ecuador','Egypt',\
            'El Salvador','Equatorial Guinea','Eritrea','Estonia','Ethiopia','Falkland Islands','Faroe Islands','Fiji','Finland','France',\
            'French Guiana','French Polynesia','French Southern Territories','Gabon','Gambia','Georgia','Germany','Ghana','Gibraltar','Greece',\
            'Greenland','Grenada','Guadeloupe','Guam','Guatemala','Guernsey','Guinea','Guinea-Bissau','Guyana',\
            'Haiti','Heard Island and McDonald Islands','Honduras','Hong Kong','Hungary','Iceland','India','Indonesia','Iran','Iraq','Ireland',\
            'Isle of Man','Israel','Italy','Jamaica','Japan','Jersey','Jordan','Kazakhstan','Kenya','Kiribati',\
            'Kosovo','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein',\
            'Lithuania','Luxembourg','Macao','Macedonia','Madagascar','Malawi','Malaysia','Maldives','Mali','Malta',\
            'Marshall Islands','Martinique','Mauritania','Mauritius','Mayotte','Mexico','Micronesia','Moldova','Monaco','Mongolia',\
            'Montenegro','Montserrat','Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','New Caledonia',\
            'New Zealand','Nicaragua','Niger','Nigeria','Niue','Norfolk Island','North Korea','Northern Cyprus','Northern Mariana Islands','Norway',\
            'Oman','Pakistan','Palau','Palestina','Panama','Papua New Guinea','Paracel Islands','Paraguay','Peru','Philippines',\
            'Pitcairn Islands','Poland','Portugal','Puerto Rico','Qatar','Republic of Congo','Reunion','Romania','Russia','Rwanda',\
            'Saint-Barthélemy','Saint-Martin','Saint Helena','Saint Kitts and Nevis','Saint Lucia','Saint Pierre and Miquelon','Saint Vincent and the Grenadines','Samoa','San Marino','Sao Tome and Principe',\
            'Saudi Arabia','Senegal','Serbia','Seychelles','Sierra Leone','Singapore','Sint Maarten','Slovakia','Slovenia','Solomon Islands',\
            'Somalia','South Africa','South Georgia and the South Sandwich Islands','South Korea','South Sudan','Spain','Spratly islands','Sri Lanka','Sudan','Suriname',\
            'Svalbard and Jan Mayen','Swaziland','Sweden','Switzerland','Syria','Taiwan','Tajikistan','Tanzania','Thailand','Togo',\
            'Tokelau','Tonga','Trinidad and Tobago','Tunisia','Turkey','Turkmenistan','Turks and Caicos Islands','Tuvalu','Uganda','Ukraine',\
            'United Arab Emirates','United Kingdom','United States','United States Minor Outlying Islands','Uruguay','Uzbekistan','Vanuatu','Vatican City','Venezuela','Vietnam',\
            'Virgin Islands, U.S.','Wallis and Futuna','Western Sahara','Yemen','Zambia','Zimbabwe']
    country_short = ['AFG','XAD','ALA','ALB','DZA','ASM','AND','AGO','AIA','ATA',\
                    'ATG','ARG','ARM','ABW','AUS','AUT','AZE','BHS','BHR','BGD',\
                    'BRB','BLR','BEL','BLZ','BEN','BMU','BTN','BOL','BES','BIH',\
                    'BWA','BVT','BRA','IOT','VGB','BRN','BGR','BFA','BDI','KHM',\
                    'CMR','CAN','CPV','XCA','CYM','CAF','TCD','CHL','CHN','CXR',\
                    'XCL','CCK','COL','COM','COK','CRI','CIV','HRV','CUB','CUW',\
                    'CYP','CZE','COD','DNK','DJI','DMA','DOM','TLS','ECU','EGY',\
                    'SLV','GNQ','ERI','EST','ETH','FLK','FRO','FJI','FIN','FRA',\
                    'GUF','PYF','ATF','GAB','GMB','GEO','DEU','GHA','GIB','GRC',\
                    'GRL','GRD','GLP','GUM','GTM','GGY','GIN','GNB','GUY','HTI',\
                    'HMD','HND','HKG','HUN','ISL','IND','IDN','IRN','IRQ','IRL',\
                    'IMN','ISR','ITA','JAM','JPN','JEY','JOR','KAZ','KEN','KIR',\
                    'XKO','KWT','KGZ','LAO','LVA','LBN','LSO','LBR','LBY','LIE',\
                    'LTU','LUX','MAC','MKD','MDG','MWI','MYS','MDV','MLI','MLT',\
                    'MHL','MTQ','MRT','MUS','MYT','MEX','FSM','MDA','MCO','MNG',\
                    'MNE','MSR','MAR','MOZ','MMR','NAM','NRU','NPL','NLD','NCL',\
                    'NZL','NIC','NER','NGA','NIU','NFK','PRK','XNC','MNP','NOR',\
                    'OMN','PAK','PLW','PSE','PAN','PNG','XPI','PRY','PER','PHL',\
                    'PCN','POL','PRT','PRI','QAT','COG','REU','ROU','RUS','RWA',\
                    'BLM','MAF','SHN','KNA','LCA','SPM','VCT','WSM','SMR','STP',\
                    'SAU','SEN','SRB','SYC','SLE','SGP','SXM','SVK','SVN','SLB',\
                    'SOM','ZAF','SGS','KOR','SSD','ESP','XSP','LKA','SDN','SUR',\
                    'SJM','SWZ','SWE','CHE','SYR','TWN','TJK','TZA','THA','TGO',\
                    'TKL','TON','TTO','TUN','TUR','TKM','TCA','TUV','UGA','UKR',\
                    'ARE','GBR','USA','UMI','URY','UZB','VUT','VAT','VEN','VNM',\
                    'VIR','WLF','ESH','YEM','ZMB','ZWE']
    lod = [3,2,2,4,3,4,2,4,1,1,2,3,2,1,3,4,3,2,2,5,2,3,5,2,3,2,3,4,2,4,3,1,4,1,2,3,3,4,5,5,4,4,2,1,2,3,4,4,4,1,1,1,3,2,1,3,5,3,3,1,2,3,4,3,3,2,3,4,4,\
            3,3,3,3,4,4,1,3,3,5,6,3,2,2,3,3,3,5,3,1,4,2,2,3,2,3,2,4,3,3,5,1,3,2,3,3,4,5,3,3,2,3,2,4,2,3,2,3,3,4,1,3,2,3,3,3,4,2,4,2,2,3,5,3,2,5,4,3,1,5,3,\
            1,3,3,2,2,3,2,2,1,3,2,2,5,4,4,3,2,5,3,3,3,3,4,3,1,1,3,2,2,3,3,4,2,3,4,3,1,3,4,4,1,4,4,2,2,3,3,3,4,6,1,1,3,2,2,2,2,3,2,3,2,5,3,2,4,2,1,3,3,3,3,\
            5,1,3,4,5,1,3,4,3,2,3,3,4,3,3,4,4,4,3,2,2,2,3,3,2,2,2,5,3,4,4,3,2,3,3,3,1,3,4,3,3,2,3,3,3]


    def browse_outfile(self):
        newname = QFileDialog.getExistingDirectory(None, "Output Folder",self.LinOutputFolder.displayText())

        if newname != None:
            self.LinOutputFolder.setText(newname)
                    
    def updateLOD(self):
        idx = self.cboCountry.currentIndex()
        self.LinLOD.setText(str(self.lod[idx]))
    
    def run(self):
        outdir = unicode(self.LinOutputFolder.displayText())
        idx = self.cboCountry.currentIndex()
        hcmgis_gadm(self.country[idx],self.country_short[idx], outdir,self.hcmgis_status_callback)				
        return		

################################
# Microsoft Building Footprints - Releases
##################################
class hcmgis_microsoft_dialog(hcmgis_dialog, Ui_hcmgis_microsoft_form):	
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)        
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)       

        project = QgsProject.instance()
        home_path = project.homePath()
        if not home_path:
            home_path = os.path.expanduser('~')
        self.LinOutputFolder.setText(home_path)    
        self.cboCountry.addItems(self.country)
        self.cboCountry.currentIndexChanged.connect(self.loadprovince)   
        self.cboCountry.setCurrentIndex(-1) 
        self.cboProvince.setCurrentIndex(-1) 
        self.cboProvince.setEnabled(False)
        self.cboProvince.currentIndexChanged.connect(self.updateinfo)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	   
        self.LblHyperlink.setOpenExternalLinks(True)

        self.cboProvince.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboProvince.setMaxVisibleItems(10)
        self.cboProvince.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)	     
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        #locale.getlocale()
        locale.resetlocale()

    country = ['Australia','Canada', 'United States of America', 'South America', 'Uganda', 'Tanzania', 'Nigeria', 'Kenya', 'Indonesia', 'Philippines', 'Malaysia']    
    us_states = ['Alabama','Alaska','Arizona','Arkansas','California',\
                'Colorado','Connecticut','Delaware','District of Columbia','Florida',\
                'Georgia','Hawaii','Idaho','Illinois','Indiana',\
                'Iowa','Kansas','Kentucky','Louisiana','Maine',\
                'Maryland','Massachusetts','Michigan','Minnesota','Mississippi',\
                'Missouri','Montana','Nebraska','Nevada','New Hampshire',\
                'New Jersey','New Mexico','New York','North Carolina','North Dakota',\
                'Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island',\
                'South Carolina','South Dakota','Tennessee','Texas','Utah',\
                'Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']    
    us_buildings= [2455168,111042,2738732,1571198,11542912,\
                   2185953,1215624,357534,77851,7263195,\
                   3981792,252908,942132,5194010,3739648,\
                   207904,1614406,2447682,2173567,758999,\
                   1657199,2114602,4982783,2914616,1507496,\
                   3190076,773119,1187234,1006278,577936,\
                   2550308,1037096,4972497,4678064,568213,\
                   5544032,2159894,1873786,4965213,392581,\
                   2299671,661311,3212306,10678921,1081586,\
                   351266,3079351,3128258,1055625,3173347,386518]
    us_size= [672.58 ,30.00,806.59 ,425.40 ,3350,619.88 ,324.20 ,94.00 ,22.52 ,2000,\
              1000,64.72 ,259.43 ,1350,920.20 ,517.95 ,428.38 ,663.98 ,600.69 ,187.84 ,\
              410.84 ,566.87 ,1240,762.08 ,394.08 ,840.28 ,200.45 ,302.72 ,296.10 ,146.40 ,\
              681.55 ,291.54 ,1250,1220,143.54 ,1420,582.14 ,545.94 ,1230,105.21 ,\
              612.67 ,166.31 ,890.22 ,2830,306.98 ,87.92 ,797.04 ,884.38 ,260.33 ,817.06 ,99.32 ]
    
    canada_states = ['Alberta',	'British Columbia',	'Manitoba',	'New Brunswick', 'Newfoundland And Labrador','Northwest Territories',\
        	        'Nova Scotia',	'Nunavut',	'Ontario',	'Prince Edward Island',	'Quebec','Saskatchewan','Yukon Territory']
    canada_buildings = [1777439,1359628,632982,350989,255568,13161,\
                        402358,2875,3781847,76590,2495801,681553,11395]
    canada_size = [389,301,135,71,51,3,\
                   81,1,808,16,512,146,3]  

    south_america_states = ['Argentina','Bolivia','Brazil','Chile','Colombia',\
                'Ecuador','Guyana','Paraguay','Peru','Uruguay', 'Venezuela',\
                'Whole Continent']    
    south_america_buildings= [3427787,1015151, 18711536, 2208744, 6083821,\
                   3674190,3339,990756,1710431, 2656, 6572969,\
                    44495865
                   ]
    south_america_size= [323,82, 1600, 187, 482, \
                        287, 0.236, 73, 144, 0.2, 497,\
                        15000]    
    
    us_states_code = [x.replace(" ", "") for x in us_states]
    canada_states_code = [x.replace(" ", "") for x in canada_states]
    south_america_states_code = [x.replace(" ", "") for x in south_america_states]


    def browse_outfile(self):
        newname = QFileDialog.getExistingDirectory(None, "Output Folder",self.LinOutputFolder.displayText())
        if newname != None:
            self.LinOutputFolder.setText(newname)
                    
    def loadprovince(self):
        self.cboProvince.clear()
        self.LblHyperlink.clear()
        self.cboProvince.setEnabled(True)  
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)      
        if 	(self.cboCountry.currentText() == 'United States of America'):
            self.cboProvince.addItems(self.us_states)
        elif (self.cboCountry.currentText() == 'Canada'):
            self.cboProvince.addItems(self.canada_states)
        elif (self.cboCountry.currentText() == 'South America'):
            self.cboProvince.addItems(self.south_america_states)

        if (self.cboCountry.currentText() == 'Australia'):
            self.LinBuidings.setText(locale.format_string("%d", 11334866, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 6410, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+'<a href=https://usbuildingdata.blob.core.windows.net/australia-buildings/Australia_2020-06-21.geojson.zip>Australia Building Footprints</a>' +' instead!')

        elif (self.cboCountry.currentText() == 'Uganda'):
            self.LinBuidings.setText(locale.format_string("%d", 6928078, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 1139, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+'<a href=https://usbuildingdata.blob.core.windows.net/tanzania-uganda-buildings/Uganda_2019-09-16.zip>Uganda Building Footprints</a>' +' instead!')

        elif (self.cboCountry.currentText() == 'Tanzania'):
            self.LinBuidings.setText(locale.format_string("%d", 11014267, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 2202, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://usbuildingdata.blob.core.windows.net/tanzania-uganda-buildings/Tanzania_2019-09-16.zip>Tanzania Building Footprints</a>' +' instead!')
        
        elif (self.cboCountry.currentText() == 'Nigeria'):
            self.LinBuidings.setText(locale.format_string("%d", 35767509, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 2300, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://minedbuildings.blob.core.windows.net/africa/nigeria.geojsonl.zip>Nigeria Building Footprints</a>' +' instead!')
        
        elif (self.cboCountry.currentText() == 'Kenya'):
            self.LinBuidings.setText(locale.format_string("%d", 14748685, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 984, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://minedbuildings.blob.core.windows.net/africa/kenya.geojsonl.zip>Kenya Building Footprints</a>' +' instead!')
        
        elif (self.cboCountry.currentText() == 'Indonesia'):
            self.LinBuidings.setText(locale.format_string("%d", 63947880, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 4400, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://minedbuildings.blob.core.windows.net/southeast-asia/indonesia.geojsonl.zip>Indonesia Building Footprints</a>' +' instead!')

        elif (self.cboCountry.currentText() == 'Philippines'):
            self.LinBuidings.setText(locale.format_string("%d", 17421764, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 1100, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://minedbuildings.blob.core.windows.net/southeast-asia/philippines.geojsonl.zip>Philippines Building Footprints</a>' +' instead!')

        elif (self.cboCountry.currentText() == 'Malaysia'):
            self.LinBuidings.setText(locale.format_string("%d", 7283908, grouping=True))
            self.LinSize.setText(locale.format_string("%d", 548, grouping=True))
            self.LblHyperlink.setText('File size is too big. Please download directly at '+ '<a href=https://minedbuildings.blob.core.windows.net/southeast-asia/malaysia.geojsonl.zip>Malaysia Building Footprints</a>' +' instead!')

     
        self.cboProvince.setCurrentIndex(-1)

    def updateinfo(self):
        self.LinBuidings.clear()
        self.LinSize.clear()
        self.LblHyperlink.clear()        
        province_index = self.cboProvince.currentIndex()          
        if (province_index >=0):      
            self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(True)     
            if (self.cboCountry.currentText() == 'United States of America'):                
                self.LinBuidings.setText(locale.format_string("%d", self.us_buildings[province_index], grouping=True))
                self.LinSize.setText(locale.format_string("%.2f", self.us_size[province_index], grouping=True))
                if (self.us_size[province_index]>=500):
                    link_message = 'File size is too big. Please download directly at '+ '<a href='+ 'https://usbuildingdata.blob.core.windows.net/usbuildings-v1-1/'+str(self.us_states_code[province_index])+'.zip>'+str (self.cboProvince.currentText()) +' Building Footprints</a>' +' instead!'
                    self.LblHyperlink.setText(link_message)
                    self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)               
            elif (self.cboCountry.currentText() == 'Canada'):
                self.LinBuidings.setText(locale.format_string("%d", self.canada_buildings[province_index], grouping=True))
                self.LinSize.setText(locale.format_string("%.2f", self.canada_size[province_index], grouping=True))
                if (self.canada_size[province_index]>=500):
                    link_message = 'File size is too big. Please download directly at '+ '<a href='+ 'https://usbuildingdata.blob.core.windows.net/canadian-buildings-v2/'+str(self.canada_states_code[province_index])+'.zip>'+str (self.cboProvince.currentText()) +' Building Footprints</a>' +' instead!'
                    self.LblHyperlink.setText(link_message)
                    self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)

            elif (self.cboCountry.currentText() == 'South America'):
                self.LinBuidings.setText(locale.format_string("%d", self.south_america_buildings[province_index], grouping=True))
                self.LinSize.setText(locale.format_string("%.2f", self.south_america_size[province_index], grouping=True))
                if (self.south_america_size[province_index]>=500):
                    if (self.cboProvince.currentText() != 'Whole Continent'):
                        link_message = 'File size is too big. Please download directly at '+ '<a href='+ 'https://minedbuildings.blob.core.windows.net/southamerica/'+str(self.south_america_states_code[province_index])+'geojsonl.zip>'+str (self.cboProvince.currentText()) +' Building Footprints</a>' +' instead!'
                    else:
                        link_message = 'File size is too big. Please download directly at '+ '<a href='+ 'https://minedbuildings.blob.core.windows.net/southamerica/SouthAmericaPolygons.zip>'+' South America Building Footprints</a>' +' instead!'    
                    self.LblHyperlink.setText(link_message)
                    self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)                    

        else:   self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).setEnabled(False)    
           
    def run(self):
        outdir = unicode(self.LinOutputFolder.displayText())
        country_idx = self.cboCountry.currentIndex()
        province_idx = self.cboProvince.currentIndex()
        if (self.country[country_idx] == 'United States of America'):
            hcmgis_microsoft(self.country[country_idx],self.us_states_code[province_idx], outdir,self.hcmgis_status_callback)				
        elif  (self.country[country_idx] == 'Canada'):
            hcmgis_microsoft(self.country[country_idx],self.canada_states_code[province_idx], outdir,self.hcmgis_status_callback)
        elif  (self.country[country_idx] == 'South America'):
            hcmgis_microsoft(self.country[country_idx],self.south_america_states_code[province_idx], outdir,self.hcmgis_status_callback)	
        else: 	hcmgis_microsoft(self.country[country_idx],None, outdir,self.hcmgis_status_callback)
        return		

################################
# Global Microsoft Building Footprints
##################################
class hcmgis_global_microsoft_dialog(hcmgis_dialog, Ui_hcmgis_global_microsoft_form):	
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.Filter.setFocus(True)
        QWidget.setTabOrder(self.Filter, self.TblCountries)

        self.readcsv()
        self.TblCountries.resizeColumnsToContents()
        self.TblCountries.resizeRowsToContents()
        self.TblCountries.horizontalHeader().setStretchLastSection(True)
        self.TblCountries.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.Filter.valueChanged.connect(self.updateCountriesTable)
        self.TblCountries.itemDoubleClicked.connect(self.run)    

           
    def updateCountriesTable(self):
        name = self.Filter.text().lower()
        if (name != '' and name is not None):    
            visible_row = 0
            for row in range(self.TblCountries.rowCount()):
                item = self.TblCountries.item(row, 0) # Country Name
                # if the search is *not* in the item's text *do not hide* the row
                if (name not in item.text().lower()):
                    match = True               
                else: 
                    match = False
                    visible_row += 1
                self.TblCountries.setRowHidden(row, match )
        else:
            for row in range(self.TblCountries.rowCount()):
                self.TblCountries.setRowHidden(row, False )

    def readcsv(self):
        csv_file = os.path.dirname(__file__) + "/buildingfootprints.csv"
        #self.hcmgis_fill_table_widget_with_wfs_layers(self.TblWFSLayers,self.cboServerName.currentIndex(), self.TxtTitle,self.TxtAbstract,self.hcmgis_status_callback)           
        self.hcmgis_fill_table_widget_with_csv(self.TblCountries,csv_file,self.hcmgis_status_callback)
       

    def run(self):  
        row=self.TblCountries.currentRow() 
        value=self.TblCountries.item(row,3).text().strip() 
        print(value) 
        if value.startswith("http://") or value.startswith("https://"):
            webbrowser.open(value)  
        return		

# --------------------------------------------------------
#    VN-2000 Projections
# --------------------------------------------------------

# class hcmgis_customprojections_dialog(hcmgis_dialog, Ui_hcmgis_customprojections_form):		
# 	provinces = ['Lai Châu', 'Điện Biên',
# 				'Sơn La',
# 				'Kiên Giang', 'Cà Mau',
# 				'Lào Cai', 'Yên Bái', 'Nghệ An', 'Phú Thọ', 'An Giang',
# 				'Thanh Hoá', 'Vĩnh Phúc', 'Đồng Tháp','Cần Thơ', 'Hậu Giang', 'Bạc Liêu', 'Hà Nội', 'Ninh Bình', 'Hà Nam',
# 				'Hà Giang', 'Hải Dương', 'Hà Tĩnh', 'Bắc Ninh', 'Hưng Yên', 'Thái Bình', 'Nam Định', 'Tây Ninh', 'Vĩnh Long', 'Sóc Trăng', 'Trà Vinh', 
# 				'Cao Bằng','Long An','Tiền Giang','Bến Tre','Hải Phòng','TP.HCM','Bình Dương',
# 				'Tuyên Quang', 'Hoà Bình', 'Quảng Bình',
# 				'Quảng Trị', 'Bình Phước',
# 				'Bắc Kạn','Thái Nguyên',
# 				'Bắc Giang','Thừa Thiên - Huế',
# 				'Lạng Sơn',
# 				'Kon Tum',
# 				'Quảng Ninh','Đồng Nai','Bà Rịa - Vũng Tàu', 'Quảng Nam','Lâm Đồng','Đà Nẵng',
# 				'Quảng Ngãi',
# 				'Ninh Thuận','Khánh Hoà','Bình Định',
# 				'Đắk Lắk', 'Đắk Nông', 'Phú Yên','Gia Lai','Bình Thuận']
# 	ktt = [	103,103,
# 			104,
# 			104.5, 104.5, 
# 			104.75, 104.75, 104.75, 104.75, 104.75, 
# 			105, 105, 105, 105, 105, 105, 105, 105, 105,  
# 			105.5, 105.5, 105.5, 105.5, 105.5, 105.5, 105.5, 105.5, 105.5, 105.5, 105.5,
# 			105.75, 105.75, 105.75, 105.75, 105.75, 105.75, 105.75, 
# 			106, 106, 106, 
# 			106.25,106.25,
# 			106.5, 106.5, 
# 			107, 107,
# 			107.25,
# 			107.5, 		
# 			107.75, 107.75, 107.75, 107.75, 107.75, 107.75,	
# 			108, 
# 			108.25, 108.25, 108.25, 
# 			108.5, 108.5, 108.5, 108.5,108.5]
# 	epsg_code = [9205, 9205, 
# 				9206, 
# 				9207, 9207, 
# 				9208, 9208, 9208, 9208, 9208, 
# 				5897, 5897, 5897, 5897, 5897, 5897, 5897, 5897, 5897, 
# 				9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 	
# 				9210, 9210, 9210, 9210, 9210, 9210, 9210,			
# 				9211, 9211, 9211, 
# 				9212, 9212, 
# 				9213, 9213, 
# 				9214, 9214, 
# 				9215,
# 				9216,
# 				5899, 5899, 5899, 5899, 5899, 5899,
# 				5898, 
# 				9217, 9217, 9217,			
# 				9218, 9218, 9218, 9218, 9218
# 				]
# 	def __init__(self, iface):		
# 		hcmgis_dialog.__init__(self, iface)
# 		
# 		self.setupUi(self)
# 		#self.BtnApplyClose.accepted.connect(self.run)
# 		self.cboProvinces.setCurrentIndex(-1)
# 		self.cboKTT.setCurrentIndex(-1)
# 		self.cboZone.setCurrentIndex(0)
# 		self.cboKTT.setEnabled(False)
# 		self.cboZone.setEnabled(False)
        
# 		self.rad3do.toggled.connect(self.togglerad3do)
# 		self.radcustom.toggled.connect(self.toggleradcustom)
# 		self.cboZone.currentIndexChanged.connect(self.zonechange)
    
# 		self.cboProvinces.currentIndexChanged.connect(self.update_proj)
# 		self.cboFormat.currentIndexChanged.connect(self.update_proj)
# 		self.cboParameters.currentIndexChanged.connect(self.update_proj)
# 		self.cboKTT.currentTextChanged.connect(self.update_proj)
# 		self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)

# 	def update_proj(self):		
# 		self.txtProjections.clear()		
# 		parameters = self.cboParameters.currentText()
# 		format_id = self.cboFormat.currentIndex()

# 		if self.rad3do.isChecked():
# 			i = self.cboProvinces.currentIndex()
# 			self.cboKTT.setCurrentText(str(self.ktt[i]))
# 			self.cboZone.setCurrentIndex(0)
# 			self.cboZone.setEnabled(False)
# 			self.cboKTT.setEnabled(False)
# 			k = 0.9999
# 			self.txtProjections.setText(self.hcmgis_projections_generate(parameters, self.ktt[i],k,format_id))
        
# 		elif self.radcustom.isChecked():
# 			if ((self.cboKTT.currentText() is not None) and  (self.cboKTT.currentText().strip() != '') and (self.cboKTT.currentIndex() != -1)):
# 				ktt = self.cboKTT.currentText().strip()
# 				if self.cboZone.currentIndex() == 0 :
# 					k = 0.9999
# 				else: k = 0.9996
# 				self.txtProjections.setText(self.hcmgis_projections_generate(parameters,ktt,k,format_id))
    
# 	def QGIS_WKT(self):		
# 		parameters = self.cboParameters.currentText()
# 		QGIS_WKT_text = ''
# 		if self.rad3do.isChecked():
# 			i = self.cboProvinces.currentIndex()
# 			self.cboKTT.setCurrentText(str(self.ktt[i]))
# 			self.cboZone.setCurrentIndex(0)
# 			self.cboZone.setEnabled(False)
# 			self.cboKTT.setEnabled(False)
# 			k = 0.9999
# 			QGIS_WKT_text = self.hcmgis_projections_generate(parameters, self.ktt[i],k,0)
        
# 		elif self.radcustom.isChecked():
# 			if ((self.cboKTT.currentText() is not None) and  (self.cboKTT.currentText().strip() != '') and (self.cboKTT.currentIndex() != -1)):
# 				ktt = self.cboKTT.currentText().strip()
# 				if self.cboZone.currentIndex() == 0 :
# 					k = 0.9999
# 				else: k = 0.9996
# 				QGIS_WKT_text = self.hcmgis_projections_generate(parameters,ktt,k,0)
# 		return QGIS_WKT_text

# 	def ProJ_4(self):		
# 		parameters = self.cboParameters.currentText()
# 		ProJ_4_text = ''
# 		if self.rad3do.isChecked():
# 			i = self.cboProvinces.currentIndex()
# 			self.cboKTT.setCurrentText(str(self.ktt[i]))
# 			self.cboZone.setCurrentIndex(0)
# 			self.cboZone.setEnabled(False)
# 			self.cboKTT.setEnabled(False)
# 			k = 0.9999
# 			ProJ_4_text = self.hcmgis_projections_generate(parameters, self.ktt[i],k,1)
        
# 		elif self.radcustom.isChecked():
# 			if ((self.cboKTT.currentText() is not None) and  (self.cboKTT.currentText().strip() != '') and (self.cboKTT.currentIndex() != -1)):
# 				ktt = self.cboKTT.currentText().strip()
# 				if self.cboZone.currentIndex() == 0 :
# 					k = 0.9999
# 				else: k = 0.9996
# 				ProJ_4_text = self.hcmgis_projections_generate(parameters,ktt,k,1)
# 		return ProJ_4_text
    
# 	def run(self):
# 		import sqlite3
# 		from qgis.core import QgsApplication
# 		import random
# 		db = sqlite3.connect(QgsApplication.qgisUserDatabaseFilePath())		
# 		i = self.cboProvinces.currentIndex()
# 		ProJ_4_text = self.ProJ_4()
# 		QGIS_WKT_text = self.QGIS_WKT()

# 		if ((self.rad3do.isChecked()) and (self.cboProvinces.currentIndex() != -1)):			
# 			cursor = db.cursor()
# 			sql = "INSERT OR REPLACE INTO [tbl_srs] VALUES (:srs_id,:desciprtion,'tmerc','WGS84',:ProJ_4_text,NULL,NULL,NULL,0,0,NULL)"
# 			srs_id = 20000 + self.cboProvinces.currentIndex()
# 			desc = "VN_2000_" +  self.provinces[i].replace(" ", "_")+ "_3deg"				
# 			# parameters = "+proj=tmerc +lat_0=0 +lon_0="
# 			# parameters += str(self.ktt[i]) 
# 			# parameters += " +k=0.9999 +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84="
# 			# parameters +=  str(self.cboParameters.currentText())
# 			# parameters += " +units=m +no_defs"
# 			# #parameters = self.txtProjections.toPlainText()
# 			cursor.execute(sql, {'srs_id': srs_id, 'desciprtion': desc, 'ProJ_4_text': ProJ_4_text, })
# 			# Commit changes
# 			db.commit()
             
# 		elif ((self.radcustom.isChecked()) and (self.cboZone.currentIndex() != -1) and (self.cboKTT.currentText() is not None)):
# 			cursor = db.cursor()
# 			sql = "INSERT OR REPLACE INTO [tbl_srs] VALUES (:srs_id,:desciprtion,'tmerc','WGS84',:ProJ_4_text,NULL,NULL,NULL,0,0,:QGIS_WKT_text)"
# 			srs_id = 30000 + random.randint(0,1000)
# 			desc = "VN_2000_" + self.cboKTT.currentText() + "_"+self.cboZone.currentText()		
# 			# parameters = "+proj=tmerc +lat_0=0 +lon_0="
# 			# parameters += str(self.cboKTT.currentText()) 
# 			# k = 0
# 			# if (self.cboZone.currentIndex() == 1): #"6 degree"
# 			# 	k = 0.9996
# 			# elif(self.cboZone.currentIndex() == 0): 	k = 0.9999
# 			# parameters += " +k=" + str(k)
# 			# parameters += " +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84="
# 			# parameters +=  str(self.cboParameters.currentText())
# 			# parameters += " +units=m +no_defs"
# 			#parameters = self.txtProjections.toPlainText()
# 			#cursor.execute(sql, {'srs_id': srs_id, 'desciprtion': desc, 'parameters': parameters })					
# 			cursor.execute(sql, {'srs_id': srs_id, 'desciprtion': desc, 'ProJ_4_text': ProJ_4_text, 'QGIS_WKT_text': QGIS_WKT_text })
# 			# Commit changes
# 			db.commit()
# 		db.close() 
# 		return

    # def hcmgis_projections_generate(self,parameters,ktt,scale_factor, format_id):	
    # 	projections_text =''
    # 	parameters_list = parameters.split(",")		
    # 	ktt = self.cboKTT.currentText().strip()
    # 	try:
    # 		srid = int(float(self.cboKTT.currentText().strip())*100)
    # 	except:
    # 		srid = 10500
        
    # 	if self.cboZone.currentIndex() == 0 :
    # 		k = 0.9999
    # 	else: k = 0.9996	
        
    # 	#QGIS WKT		
    # 	#self.cboFormat.currentIndex()
    # 	if  format_id == 0:	
    # 		projections_text += 'BOUNDCRS[SOURCECRS[PROJCS["VN-2000 / '+  str(srid) +'",'
    # 		projections_text += 'BASEGEOGCRS["VN-2000",DATUM["Vietnam 2000",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4756]],CONVERSION["unnamed",METHOD["Transverse Mercator",ID["EPSG",9807]],'
    # 		projections_text += 'PARAMETER["Latitude of natural origin",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",'
    # 		projections_text +=  ktt
    # 		projections_text += ',ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["Scale factor at natural origin",0.9999,SCALEUNIT["unity",1],ID["EPSG",8805]],'
    # 		projections_text += 'PARAMETER["False easting",500000,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],'
    # 		projections_text += 'AXIS["easting",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["northing",north,ORDER[2],LENGTHUNIT["metre",1]],ID["EPSG",10545]]],'
    # 		projections_text += 'TARGETCRS[GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],'
    # 		projections_text += 'ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]]],'
    # 		projections_text += 'ABRIDGEDTRANSFORMATION["Transformation from VN-2000 to WGS84",METHOD["Position Vector transformation (geog2D domain)",ID["EPSG",9606]]'
    # 		projections_text += ',PARAMETER["X-axis translation",'
    # 		projections_text += str(parameters_list[0]) + ',ID["EPSG",8605]],'
    # 		projections_text += 'PARAMETER["Y-axis translation",'
    # 		projections_text += str(parameters_list[1]) + ',ID["EPSG",8606]],'
    # 		projections_text += 'PARAMETER["Z-axis translation",'
    # 		projections_text += str(parameters_list[2]) +',ID["EPSG",8607]],'
    # 		projections_text += 'PARAMETER["X-axis rotation",'
    # 		projections_text += str(parameters_list[3]) +',ID["EPSG",8608]],'
    # 		projections_text += 'PARAMETER["Y-axis rotation",'
    # 		projections_text += str(parameters_list[4]) +',ID["EPSG",8609]],'
    # 		projections_text += 'PARAMETER["Z-axis rotation",'
    # 		projections_text += str(parameters_list[5]) +',ID["EPSG",8610]],'
    # 		projections_text += 'PARAMETER["Scale difference",'
    # 		#projections_text += str(parameters_list[6])+ ',ID["EPSG",8611]]]]'
    # 		projections_text += str(1.00000025290628)+ ',ID["EPSG",8611]]]]'


    # 	#Proj.4
    # 	elif format_id == 1: 
    # 		projections_text = '+proj=tmerc +lat_0=0 +lon_0='
    # 		projections_text+= str(ktt)
    # 		projections_text+=' +k='
    # 		projections_text+= str(k)
    # 		projections_text+= ' +x_0=500000 +y_0=0 +ellps=WGS84 +towgs84='
    # 		projections_text+= parameters
    # 		projections_text+= ' +units=m +no_defs'
    
    # 	#ESRI WKT
    # 	#PROJCS["VN_2000_UTM_zone_48N",GEOGCS["GCS_VN-2000",DATUM["D_Vietnam_2000",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]
    # 	elif format_id == 2:			
    # 		projections_text = 'PROJCS['
    # 		projections_text += '"VN-2000 / '+  str(srid) +'"'
    # 		projections_text += ',GEOGCS["GCS_VN-2000",DATUM["D_Vietnam_2000",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
    # 		projections_text += ktt + ']'
    # 		projections_text +=',PARAMETER["scale_factor",'
    # 		projections_text += str(k) +']'
    # 		projections_text +=',PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'			
        
    # 	#PostGIS
    # 	#INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 3405, 'EPSG', 3405, '+proj=utm +zone=48 +ellps=WGS84 +towgs84=-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188 +units=m +no_defs ', 'PROJCS["VN-2000 / UTM zone 48N",GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","3405"]]');
    # 	elif format_id == 3:		
    # 		projections_text = 'INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values('
    # 		projections_text += str(srid) 
    # 		projections_text += ',\'' 
    # 		projections_text +=	'HCMGIS'
    # 		projections_text += '\',' 
    # 		projections_text += str(srid)
    # 		projections_text += ',\''
    # 		projections_text += '+proj=utm +ellps=WGS84 +towgs84='
    # 		projections_text +=	parameters 
    # 		projections_text += ' +units=m +no_defs'
    # 		projections_text += '\''
    # 		projections_text += ',\''
    # 		projections_text += 'PROJCS["'
    # 		projections_text += 'VN-2000 / ' + str(srid) + '"'
    # 		projections_text += ',GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
    # 		projections_text += 'TOWGS84['
    # 		projections_text += parameters
    # 		projections_text += '],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
    # 		projections_text += str(ktt)
    # 		projections_text += '],PARAMETER["scale_factor",'
    # 		projections_text += str(k)
    # 		projections_text += '],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG",'
    # 		projections_text += '"'
    # 		projections_text += str(srid)
    # 		projections_text += '"'
    # 		projections_text += ']]'
    # 		projections_text += '\''
    # 		projections_text += ');'

    # 	#GeoServer:
    # 	#3405=PROJCS["VN-2000 / UTM zone 48N",GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[-192.873,-39.382,-111.202,-0.00205,-0.0005,0.00335,0.0188],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","3405"]]
    # 	elif format_id == 4:			
    # 		projections_text = str(srid)
    # 		projections_text += '=PROJCS['
    # 		projections_text += '"'
    # 		projections_text += 'VN-2000 / '+str(srid)
    # 		projections_text += '"'
    # 		projections_text += ',GEOGCS["VN-2000",DATUM["Vietnam_2000",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84['
    # 		projections_text += parameters
    # 		projections_text += '],AUTHORITY["EPSG","6756"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4756"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",'
    # 		projections_text += str(ktt)
    # 		projections_text += '],PARAMETER["scale_factor",'
    # 		projections_text += str(k)
    # 		projections_text += '],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG",'
    # 		projections_text +=  '"'
    # 		projections_text += str(srid)
    # 		projections_text += '"'
    # 		projections_text += ']]'
        
    # 	return projections_text

    # def zonechange(self):
    # 	self.txtProjections.clear()
        
    # 	listKTT6do = ['105','111','117']
    # 	listKTT3do = ['102', '103', '104','104.5', '104.75', '105','105.5', '105.75','106', '106.25', '106.5',
    # 	'107','107.25','107.5','107.75','108','108.25','108.5', '111','114', '117']

    # 	if (self.cboZone.currentIndex() == 1):
    # 		self.cboKTT.clear()
    # 		self.cboKTT.addItems(listKTT6do)
    # 		self.cboKTT.setCurrentIndex(-1)
    
    # 	elif (self.cboZone.currentIndex() == 0):
    # 		self.cboKTT.clear()
    # 		self.cboKTT.addItems(listKTT3do)
    # 		self.cboKTT.setCurrentIndex(-1)
             
    # def togglerad3do(self):
    # 	self.txtProjections.clear()
    # 	self.cboKTT.clear()
    # 	if self.rad3do.isChecked():
    # 		self.cboProvinces.setCurrentIndex(-1)
    # 		self.cboKTT.setCurrentIndex(-1)
    # 		self.cboZone.setCurrentIndex(-1)
    # 		self.cboProvinces.setEnabled(True)
    # 		self.cboKTT.setEnabled(False)
    # 		self.cboZone.setEnabled(False)
        
    # def toggleradcustom(self):
    # 	self.txtProjections.clear()
    # 	self.cboKTT.clear()
    # 	if self.radcustom.isChecked():			
    # 		self.cboProvinces.setCurrentIndex(-1)
    # 		self.cboKTT.setCurrentIndex(-1)
    # 		self.cboZone.setCurrentIndex(-1)
    # 		self.cboProvinces.setEnabled(False)
    # 		self.cboKTT.setEnabled(True)
    # 		self.cboZone.setEnabled(True)
    
class hcmgis_customprojections_dialog(hcmgis_dialog, Ui_hcmgis_customprojections_form):	
    provinces = ['Lai Châu', 'Điện Biên',
                'Sơn La',
                'Kiên Giang', 'Cà Mau',
                'Lào Cai', 'Yên Bái', 'Nghệ An', 'Phú Thọ', 'An Giang',
                'Thanh Hoá', 'Vĩnh Phúc', 'Đồng Tháp','Cần Thơ', 'Hậu Giang', 'Bạc Liêu', 'Hà Nội', 'Ninh Bình', 'Hà Nam',
                'Hà Giang', 'Hải Dương', 'Hà Tĩnh', 'Bắc Ninh', 'Hưng Yên', 'Thái Bình', 'Nam Định', 'Tây Ninh', 'Vĩnh Long', 'Sóc Trăng', 'Trà Vinh', 
                'Cao Bằng','Long An','Tiền Giang','Bến Tre','Hải Phòng','TP.HCM','Bình Dương',
                'Tuyên Quang', 'Hoà Bình', 'Quảng Bình',
                'Quảng Trị', 'Bình Phước',
                'Bắc Kạn','Thái Nguyên',
                'Bắc Giang','Thừa Thiên - Huế',
                'Lạng Sơn',
                'Kon Tum',
                'Quảng Ninh','Đồng Nai','Bà Rịa - Vũng Tàu', 'Quảng Nam','Lâm Đồng','Đà Nẵng',
                'Quảng Ngãi',
                'Ninh Thuận','Khánh Hoà','Bình Định',
                'Đắk Lắk', 'Đắk Nông', 'Phú Yên','Gia Lai','Bình Thuận']
    
    zone = ['VN-2000 / TM-3 103-00','VN-2000 / TM-3 103-00', 
            'VN-2000 / TM-3 104-00',
            'VN-2000 / TM-3 104-30','VN-2000 / TM-3 104-30',
            'VN-2000 / TM-3 104-45','VN-2000 / TM-3 104-45','VN-2000 / TM-3 104-45','VN-2000 / TM-3 104-45','VN-2000 / TM-3 104-45',
            'VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00','VN-2000 / TM-3 105-00',
            'VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30','VN-2000 / TM-3 105-30',
            'VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45','VN-2000 / TM-3 105-45',
            'VN-2000 / TM-3 106-00','VN-2000 / TM-3 106-00','VN-2000 / TM-3 106-00',
            'VN-2000 / TM-3 106-15', 'VN-2000 / TM-3 106-15', 
            'VN-2000 / TM-3 106-30', 'VN-2000 / TM-3 106-30', 
            'VN-2000 / TM-3 107-00', 'VN-2000 / TM-3 107-00', 
            'VN-2000 / TM-3 107-15',
            'VN-2000 / TM-3 107-30', 
            'VN-2000 / TM-3 107-45', 'VN-2000 / TM-3 107-45', 'VN-2000 / TM-3 107-45', 'VN-2000 / TM-3 107-45', 'VN-2000 / TM-3 107-45', 'VN-2000 / TM-3 107-45', 
            'VN-2000 / TM-3 zone 491',			
            'VN-2000 / TM-3 108-15','VN-2000 / TM-3 108-15','VN-2000 / TM-3 108-15',
            'VN-2000 / TM-3 108-30','VN-2000 / TM-3 108-30','VN-2000 / TM-3 108-30','VN-2000 / TM-3 108-30','VN-2000 / TM-3 108-30'
            ]
    epsg_code = ['9205', '9205', 
                '9206', 
                '9207', '9207', 
                '9208', '9208', '9208', '9208', '9208', 
                '5897', '5897', '5897', '5897', '5897', '5897', '5897', '5897','5897', 
                '9209', '9209', '9209', '9209', '9209', '9209', '9209', '9209', '9209', '9209', '9209', 	
                '9210', '9210', '9210', '9210', '9210', '9210', '9210',			
                '9211', '9211', '9211', 
                '9212', '9212', 
                '9213', '9213', 
                '9214', '9214', 
                '9215',
                '9216',
                '5899', '5899', '5899', '5899', '5899', '5899',
                '5898', 
                '9217', '9217', '9217',			
                '9218', '9218', '9218', '9218', '9218'
                ]
    
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.cboProvinces.addItems(self.provinces) 
        self.cboProvinces.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboProvinces.setMaxVisibleItems(21)
        self.cboProvinces.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.cboEPSG.setStyleSheet("QComboBox {combobox-popup: 0; }") # To enable the setMaxVisibleItems        
        self.cboEPSG.setMaxVisibleItems(21)
        self.cboEPSG.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)



        
        self.cboProvinces.setCurrentIndex(-1)
        self.cboEPSG.setCurrentIndex(-1)	
        self.cboProvinces.checked = True
        self.cboEPSG.checked = False
        self.cboEPSG.setEnabled(False)
        self.TxtEPSGInfo.setReadOnly(True)     
        self.TxtEPSGInfo.clear()

        self.radEPSG.toggled.connect(self.togglerad)
        self.cboEPSG.currentIndexChanged.connect(self.EPSGChange)
        self.radProvinces.toggled.connect(self.togglerad)
        self.cboProvinces.currentIndexChanged.connect(self.ProvincesChange)
       
   
    def ProvincesChange(self):
        self.TxtEPSGInfo.clear()
        if self.cboProvinces.currentIndex() != -1:  
            i = self.cboProvinces.currentIndex()
            EPSGCode = self.epsg_code[i] 
            EPSGInfoZoneName = '- Zone name: ' + self.zone[i] 
            EPSGInfoEPSGCode = '\n- EPSG Code: ' + EPSGCode            
            indices = [i for i, x in enumerate(self.epsg_code) if x == EPSGCode]
            provinces_list = ''
            for indice in indices:
                provinces_list+= str(self.provinces[indice]) + ', '

            ProvincesText = '\n- Provinces: ' + provinces_list 

            if ProvincesText.endswith(', '):     						
                ProvincesText = ProvincesText[:-(len(', '))] + '.'
            self.TxtEPSGInfo.setText(EPSGInfoZoneName + EPSGInfoEPSGCode +ProvincesText)        

    def EPSGChange(self):
        self.TxtEPSGInfo.clear()
        if self.cboEPSG.currentIndex() != -1:            
            EPSGCode = self.cboEPSG.currentText().strip()  
            i = self.epsg_code.index(EPSGCode) 
            EPSGInfoZoneName = '- Zone name: ' + self.zone[i] 
            EPSGInfoEPSGCode = '\n- EPSG Code: ' + EPSGCode            
            
            indices = [i for i, x in enumerate(self.epsg_code) if x == EPSGCode]
            provinces_list = ''
            for indice in indices:
                provinces_list+= str(self.provinces[indice]) + ', '

            ProvincesText = '\n- Provinces: ' + provinces_list 

            if ProvincesText.endswith(', '):     						
                ProvincesText = ProvincesText[:-(len(', '))] + '.'
            self.TxtEPSGInfo.setText(EPSGInfoZoneName + EPSGInfoEPSGCode +ProvincesText)

        
    def togglerad(self):
        if self.radProvinces.isChecked():
            self.cboEPSG.setEnabled(False)
            self.cboEPSG.setCurrentIndex(-1)
            self.cboProvinces.setEnabled(True)
            self.TxtEPSGInfo.clear()
            
        elif self.radEPSG.isChecked():
            self.cboProvinces.setEnabled(False)
            self.cboProvinces.setCurrentIndex(-1)
            self.cboEPSG.setEnabled(True)
            self.TxtEPSGInfo.clear()

#   Split Polygons into (almost) equal parts       
class hcmgis_split_polygon_dialog(hcmgis_dialog, Ui_hcmgis_spit_polygon_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)		
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.hcmgis_initialize_spatial_output_file_widget(self.output_file_name,'split')    
   
              
    def run(self):             		
        layer = self.CboInput.currentLayer()
        if layer is None:
            return u'No selected Layer!'  
        parts = self.spParts.value()
        randompoints = self.spRandomPoints.value()
        output = str(self.output_file_name.filePath())
        split_layers = []        

        if layer.selectedFeatureCount()>0:	
            for feat in layer.selectedFeatures():
                # mem_layer = QgsVectorLayer(layer, QFileInfo(layer).baseName(), 'ogr')
                mem_layer = QgsVectorLayer('Polygon','polygon','memory')
                mem_layer.dataProvider().setEncoding(u'UTF-8')
                mem_layer_data = mem_layer.dataProvider()
                attr = layer.dataProvider().fields().toList()
                mem_layer_data.addAttributes(attr)
                mem_layer.updateFields()
                mem_layer.startEditing()
                mem_layer.addFeature(feat)
                mem_layer.commitChanges()
                # QgsProject.instance().addMapLayer(mem_layer)                 
                message = hcmgis_split_polygon(mem_layer,parts,randompoints,self.hcmgis_status_callback)
                if message != None:
                    QMessageBox.critical(self.iface.mainWindow(), "Split Polygons", message)						               
                else: 
                    self.LblStatus.setText('Completed! ')  
        else:
            #return u'Please select at least 1 feature to Split Polygon	
            for feat in layer.getFeatures():
                # mem_layer = QgsVectorLayer(layer, QFileInfo(layer).baseName(), 'ogr')
                mem_layer = QgsVectorLayer('Polygon','polygon','memory')
                mem_layer.dataProvider().setEncoding(u'UTF-8')
                mem_layer_data = mem_layer.dataProvider()
                attr = layer.dataProvider().fields().toList()
                mem_layer_data.addAttributes(attr)
                mem_layer.updateFields()
                mem_layer.startEditing()
                mem_layer.addFeature(feat)
                mem_layer.commitChanges()
                # QgsProject.instance().addMapLayer(mem_layer) 
                message = hcmgis_split_polygon(mem_layer,parts,randompoints,self.hcmgis_status_callback)
                if message != None:
                    QMessageBox.critical(self.iface.mainWindow(), "Split Polygons", message)						               
                else: 
                    self.LblStatus.setText('Completed! ')         

        #  layer list in the group
        layers =  QgsProject.instance().mapLayersByName('Intersection')

        parameters = {'LAYERS': layers,                
                     'OUTPUT' : output} 
        points = processing.runAndLoadResults('qgis:mergevectorlayers', parameters)  
       
        for layer in QgsProject.instance().mapLayers().values():            
            if layer.name() == 'Intersection': 
               QgsProject.instance().removeMapLayers([layer.id()])
        return


class hcmgis_medialaxis_dialog(hcmgis_dialog, Ui_hcmgis_medialaxis_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
        self.CboField.setLayer (self.CboInput.currentLayer())
        self.CboInput.activated.connect(self.update_field) 
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
        self.hcmgis_initialize_spatial_output_file_widget(self.output_file_name,'skeleton')

               
    def update_field(self):
        self.CboField.setLayer(self.CboInput.currentLayer () )
        
        if (self.CboField.count()>0):
            self.CboField.setCurrentIndex(0)
    
                
    def run(self):             	
        self.LblStatus.clear()	
        layer = self.CboInput.currentLayer()
        if layer is None:
            return u'No selected Layer!'  
        field = self.CboField.currentText()
        density = self.spinBox.value()
        output = str(self.output_file_name.filePath())
        if layer.selectedFeatureCount() in range (1,3000):
            message = hcmgis_medialaxis(layer,field, density,output,self.hcmgis_status_callback)
            if message != None:
                QMessageBox.critical(self.iface.mainWindow(), "Skeleton/ Media Axis", message)	
            else: 
                self.LblStatus.setText('Completed ' + str(layer.selectedFeatureCount()) + ' features')          
        else:
            #return u'Please select 1..100 features to create Skeleton/ Media Axis'		
            QMessageBox.information(None,  "Skeleton/ Media Axis",u'Please select 1..100 features to create Skeleton/ Media Axis!') 
        return

class hcmgis_centerline_dialog(hcmgis_dialog, Ui_hcmgis_centerline_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.chksurround.checked = False
        self.lblsurround.setEnabled(False)
        self.distance.setEnabled(False)			
        self.chksurround.stateChanged.connect(self.toggleSurround)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.hcmgis_initialize_spatial_output_file_widget(self.output_file_name,'centerline')

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
            return u'No selected Layer!'  
        density = self.spinBox.value()
        chksurround = self.chksurround.isChecked() 
        distance = self.distance.value()
        output = str(self.output_file_name.filePath())
        if layer.selectedFeatureCount()>0:		
            message = hcmgis_centerline(layer,density,chksurround,distance,output,self.hcmgis_status_callback)
            if message != None:
                QMessageBox.critical(self.iface.mainWindow(), "Centerline in Polygon's Gaps", message)						               
            else: 
                self.LblStatus.setText('Completed! ')  	
        else:
            #return u'Please select at least 1 feature to create centerline		
            QMessageBox.information(None,  "Centerline",u'Please select at least 1 feature to create Centerline!') 
        return
        
# --------------------------------------------------------
#   Finding closest pair of Points
# --------------------------------------------------------			
class hcmgis_closestpair_dialog(hcmgis_dialog, Ui_hcmgis_closestpair_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.CboField.setLayer (self.CboInput.currentLayer () )		
        self.CboInput.activated.connect(self.update_field)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)           
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
        self.hcmgis_initialize_spatial_output_file_widget(self.closest,'closest')
        self.hcmgis_initialize_spatial_output_file_widget(self.farthest,'farthest')


    def update_field(self):
        self.CboField.setLayer (self.CboInput.currentLayer () )	
        if (self.CboField.count()>0):
            self.CboField.setCurrentIndex(0)
        
    def run(self):             		
        layer = self.CboInput.currentLayer()
        field = self.CboField.currentText()
        closest = str(self.closest.filePath())
        farthest = str(self.farthest.filePath())

        #message = hcmgis_closestpair(self.iface,layer,field,self.hcmgis_status_callback)
        message = hcmgis_closest_farthest(layer,field,closest,farthest,self.hcmgis_status_callback)
        if message != None:
            QMessageBox.critical(self.iface.mainWindow(), "Closest/ farthest pair of Points", message)						               
        else: self.LblStatus.setText('Completed! ')  			
        return

# --------------------------------------------------------
#   Finding largest empty circle
# --------------------------------------------------------			
class hcmgis_lec_dialog(hcmgis_dialog, Ui_hcmgis_lec_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.CboField.setLayer (self.CboInput.currentLayer () )	
        self.CboInput.activated.connect(self.update_field)         
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
        self.hcmgis_initialize_spatial_output_file_widget(self.output_file_name,'lec')

    def update_field(self):
        self.CboField.setLayer (self.CboInput.currentLayer () )	
        if (self.CboField.count()>0):
            self.CboField.setCurrentIndex(0)
    
    def run(self):             		
        layer = self.CboInput.currentLayer()
        field = self.CboField.currentText()
        if layer is None:
            return u'No selected point layer!'		
        else:
            output = str(self.output_file_name.filePath())	
            message = hcmgis_lec(layer,field, output ,self.hcmgis_status_callback)
            if message != None:
                QMessageBox.critical(self.iface.mainWindow(), "Largest Empty Circle", message)						               
            else: self.LblStatus.setText('Completed! ')  		
        return
    
class hcmgis_font_convert_dialog(hcmgis_dialog, Ui_hcmgis_font_convert_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	 
        self.hcmgis_initialize_spatial_output_file_widget(self.output_file_name,'fontconvert')              
         
                
    def run(self):             		
        input_layer = self.CboInput.currentLayer()
        output_layer = str(self.output_file_name.filePath())				
        sE = GetEncodeIndex(self.CboSourceFont.currentText())
        dE = GetEncodeIndex(self.CboDestFont.currentText())
        caseI = GetCaseIndex(self.CboOption.currentText())                
        message = hcmgis_convertfont(input_layer,sE, dE, caseI,output_layer,self.hcmgis_status_callback) 
        if message != None:
            QMessageBox.critical(self.iface.mainWindow(), "Convert Font", message)						               
        else: self.LblStatus.setText('Completed! ')  

#---------------------------
# Split Fields
#----------------------------				
class hcmgis_split_field_dialog(hcmgis_dialog, Ui_hcmgis_split_field_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)			
        self.CboField.setLayer (self.CboInput.currentLayer () )
        self.CboInput.activated.connect(self.update_field)                
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
                
    def update_field(self):
        self.CboField.setLayer(self.CboInput.currentLayer () )        
        if (self.CboField.count()>0):
            self.CboField.setCurrentIndex(0)
             
    def run(self):             		
        layer = self.CboInput.currentLayer()
        char = self.CboChar.currentText()
        field = self.CboField.currentText()
        message = hcmgis_split_field(layer, field, char,self.hcmgis_status_callback)
        if message != None:
            QMessageBox.critical(self.iface.mainWindow(), "Split Fields", message)						               
        else: self.LblStatus.setText('Completed! ')  		
        return

#------------------------------
# Merge Fields
#------------------------------			
class hcmgis_merge_field_dialog(hcmgis_dialog, Ui_hcmgis_merge_field_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.update_fields()
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)	
        self.CboInput.activated.connect(self.update_fields)
        self.hcmgis_set_status_bar(self.status,self.LblStatus)	
                
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
        for i in list(self.ListFields.selectedItems()):
            selectedfields.append(str(i.text()))
        if len(selectedfields) > 0:
            message = hcmgis_merge_field(layer, selectedfields, char,self.hcmgis_status_callback)
            if message != None:
                QMessageBox.critical(self.iface.mainWindow(), "Merge Fields", message)						               
            else: self.LblStatus.setText('Completed! ')  
        return

# Format Convert
class hcmgis_format_convert_dialog(hcmgis_dialog, Ui_hcmgis_format_convert_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)	
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.lsFiles.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_files)		                           
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.cboInputFormat.currentIndexChanged.connect(self.update_files) 
        self.cboOutputFormat.clear()
        self.cboOutputFormat.addItems(self.out_put_format)  
        self.cboOutputFormat.currentIndexChanged.connect(self.update_status)      
    #out_put_format = ['AmigoCloud','BNA','Carto','Cloudant','CouchDB','CSV','DB2ODBC','DGN','DXF','ElasticSearch','ESRI Shapefile',\
    #				'Geoconcept','GeoJSON','GeoJSONSeq','GeoRSS','GFT','GML','GPKG','GPSBabel','GPSTrackMaker','GPX','Interlis 1',\
    #				'Interlis 2','JML','KML','LIBKML','MapInfo File','MBTiles','Memory','MSSQLSpatial','MVT','MySQL','netCDF','NGW',\
    #				'OCI','ODBC','ODS','OGR_GMT','PCIDSK','PDF','PDS4','PGDUMP','PostgreSQL','S57','Selafin','SQLite','TIGER','VDV','WAsP','XLSX']
    out_put_format=['CSV','ESRI Shapefile','GeoJSON','GML','GPKG']
    out_put_ext = ['csv','shp','geojson','gml','gpkg']

    def update_status(self):
        self.lsFiles.setCurrentRow(0)
        self.LblStatus.clear()
        self.txtError.clear()
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        
    def update_files(self):
        if self.LinInputFolder.displayText() != None:
            self.lsFiles.clear() 			
            PATH = self.LinInputFolder.displayText()
            EXT = "*." + self.cboInputFormat.currentText()
            all_files = [file
                        for path, subdir, files in os.walk(PATH)
                        for file in glob(os.path.join(path, EXT))]
            self.lsFiles.addItems(all_files)
            self.lblFiles.setText (str(self.lsFiles.count()) + " files loaded")
            self.lsFiles.setCurrentRow(0)
            self.LblStatus.clear()
            self.txtError.clear()
            self.hcmgis_set_status_bar(self.status,self.LblStatus)


    def read_files(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None and os.path.basename(newname)!='' : #prevent choose the whole Disk like C:\:
            self.LinInputFolder.setText(newname)	
            self.lsFiles.clear()		
            PATH = newname
            EXT = "*." + self.cboInputFormat.currentText()
            all_files = [file
                        for path, subdir, files in os.walk(PATH)
                        for file in glob(os.path.join(path, EXT))]
            self.lsFiles.addItems(all_files)
            self.lblFiles.setText (str(self.lsFiles.count()) + " files loaded")
            self.lsFiles.setCurrentRow(0)
            self.LblStatus.clear()
            self.txtError.clear()
            self.hcmgis_set_status_bar(self.status,self.LblStatus)
        else:            
            QMessageBox.warning(None, "Choose Folder", 'Please choose a folder, not a disk like C:/')
        
    def run(self):      
        item_count = 0
        error_count = 0
        items = []
        for index in range(self.lsFiles.count()):
            items.append(self.lsFiles.item(index))
        self.txtError.clear()
        self.lsFiles.blockSignals(True)
        self.LinInputFolder.setEnabled(False)
        self.BtnInputFolder.setEnabled(False)
        self.cboInputFormat.setEnabled(False)
        self.cboOutputFormat.setEnabled(False)		
        self.status_bar.setEnabled(False)			
    
        for item in items:
            self.lsFiles.setCurrentRow(item_count)	
            ogr_driver_name = str(self.cboOutputFormat.currentText())	
            input_file_name = item.text()
            temp_file_name = item.text()
            input_ext = "." + str(self.cboInputFormat.currentText()).lower()
            idx = self.cboOutputFormat.currentIndex()
            output_ext = "." + self.out_put_ext[idx]
            output_file_name = temp_file_name.replace(input_ext, output_ext, 1)		
            message = hcmgis_format_convert(input_file_name, output_file_name,ogr_driver_name)
            if message:
                #QMessageBox.critical(self.iface.mainWindow(), "Vector Format Convert", message)
                error_count+=1
                self.txtError.append(str(error_count)+ ". "+ input_file_name + ": " + message)
                continue
            else:
                item_count +=1
                self.LblStatus.setText (str(item_count)+"/ "+ str(self.lsFiles.count()) + " files converted")	
                percent_complete = item_count/self.lsFiles.count()*100
                self.status_bar.setValue(percent_complete)
                message = str(int(percent_complete)) + "%"
                self.status_bar.setFormat(message)
        
        self.lsFiles.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)
        self.cboInputFormat.setEnabled(True)
        self.cboOutputFormat.setEnabled(True)	
        self.status_bar.setEnabled(True)	
    

# csv2shp
class hcmgis_csv2shp_dialog(hcmgis_dialog, Ui_hcmgis_csv2shp_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Close).setAutoDefault(False)	
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.lsCSV.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_csv)			
        self.lsCSV.currentRowChanged.connect(self.set_field_names)                             
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)

    def set_field_names(self):
        try: 
            header = self.hcmgis_read_csv_header(self.lsCSV.currentItem().text())
        except:
            return
        if not header:
            return
        self.longitude_field.clear()
        self.latitude_field.clear()		
        self.longitude_field.addItems(header)
        self.latitude_field.addItems(header)

        for index, field in enumerate(header):
            #if (field.lower().find("x") >= 0):
            if (field.lower().startswith("x") ):
                self.longitude_field.setCurrentIndex(index)

            elif (field.lower().startswith("y") ):
                self.latitude_field.setCurrentIndex(index)

            elif (field.lower().startswith('lon')):
                self.longitude_field.setCurrentIndex(index)

            elif (field.lower().startswith('lat')):
                self.latitude_field.setCurrentIndex(index)

    def read_csv(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None and os.path.basename(newname)!='' : #prevent choose the whole Disk like C:\
            self.LinInputFolder.setText(newname)	
            self.lsCSV.clear() 				
            PATH = newname
            EXT = "*.csv"
            all_csv_files = [file
                        for path, subdir, files in os.walk(PATH)
                        for file in glob(os.path.join(path, EXT))]
            self.lsCSV.addItems(all_csv_files)
            self.lblCSV.setText (str(self.lsCSV.count()) + " files loaded")
            self.lsCSV.setCurrentRow(0)
            self.LblStatus.clear()
            self.hcmgis_set_status_bar(self.status,self.LblStatus)
        else:
            QMessageBox.warning(None, "Choose Folder", 'Please choose a folder, not a disk like C:/')

        
    def run(self):             		
        item_count = 0
        error_count = 0
        items = []
        for index in range(self.lsCSV.count()):
            items.append(self.lsCSV.item(index))
        self.txtError.clear()
        self.lsCSV.blockSignals(True)
        self.LinInputFolder.setEnabled(False)
        self.BtnInputFolder.setEnabled(False)
        self.longitude_field.setEnabled(False)
        self.latitude_field.setEnabled(False)		
        self.status_bar.setEnabled(False)			
    
        for item in items:
            self.lsCSV.setCurrentRow(item_count)		
            input_csv_name = item.text()
            longitude_field = str(self.longitude_field.currentText())
            latitude_field = str(self.latitude_field.currentText())

            temp_file_name = item.text()
            output_file_name = temp_file_name.replace(".csv", ".geojson", 1)

            message = hcmgis_csv2shp(input_csv_name,  latitude_field, longitude_field, \
                output_file_name, self.hcmgis_status_callback)
            if message:
                #QMessageBox.critical(self.iface.mainWindow(), "CSV Point Convert", message)
                error_count+=1
                self.txtError.append(str(error_count)+ ". "+ input_csv_name + ": " + message)
                continue
            else:
                item_count +=1
                self.LblStatus.setText (str(item_count)+"/ "+ str(self.lsCSV.count()) + " files converted")	
        
        self.lsCSV.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)
        self.longitude_field.setEnabled(True)
        self.latitude_field.setEnabled(True)	
        self.status_bar.setEnabled(True)


# txt2csv
class hcmgis_txt2csv_dialog(hcmgis_dialog, Ui_hcmgis_txt2csv_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.lsTXT.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_txt)			
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        
    def read_txt(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None and os.path.basename(newname)!='' : #prevent choose the whole Disk like C:\:
            self.LinInputFolder.setText(newname)	
            self.lsTXT.clear()		
            PATH = newname
            EXT = "*.txt"
            all_txt_files = [file
                        for path, subdir, files in os.walk(PATH)
                        for file in glob(os.path.join(path, EXT))]
            self.lsTXT.addItems(all_txt_files)
            self.lblTXT.setText (str(self.lsTXT.count()) + " files loaded")
            self.lsTXT.setCurrentRow(0)
            self.LblStatus.clear()
            self.hcmgis_set_status_bar(self.status,self.LblStatus)
        else:
            QMessageBox.warning(None, "Choose Folder", 'Please choose a folder, not a disk like C:/')
        
    def run(self):             		
        item_count = 0
        error_count = 0
        items = []
        for index in range(self.lsTXT.count()):
            items.append(self.lsTXT.item(index))
        self.txtError.clear()
        self.lsTXT.blockSignals(True)
        self.LinInputFolder.setEnabled(False)
        self.BtnInputFolder.setEnabled(False)
    
        self.status_bar.setEnabled(False)			
    
        for item in items:
            self.lsTXT.setCurrentRow(item_count)		
            input_txt_name = item.text()

            temp_file_name = item.text()
            output_file_name = temp_file_name.replace(".txt", ".csv", 1)

            message = hcmgis_txt2csv(input_txt_name, output_file_name, self.hcmgis_status_callback)
            if message:
                #QMessageBox.critical(self.iface.mainWindow(), "CSV Point Convert", message)
                error_count+=1
                self.txtError.append(str(error_count)+ ". "+ input_txt_name + ": " + message)
                continue
            else:
                item_count +=1
                self.LblStatus.setText (str(item_count)+"/ "+ str(self.lsTXT.count()) + " files converted")	
        
        self.lsTXT.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)	
        self.status_bar.setEnabled(True)	

# xls2csv
class hcmgis_xls2csv_dialog(hcmgis_dialog, Ui_hcmgis_xls2csv_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.hcmgis_set_status_bar(self.status,self.LblStatus)
        self.lsXLS.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_xls)			
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)	
        
    def read_xls(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None and os.path.basename(newname)!='' : #prevent choose the whole Disk like C:\: 
            self.LinInputFolder.setText(newname)	
            self.lsXLS.clear()			
            PATH = newname
            EXT = "*.xlsx"
            all_txt_files = [file
                        for path, subdir, files in os.walk(PATH)
                        for file in glob(os.path.join(path, EXT))]
            self.lsXLS.addItems(all_txt_files)
            self.LblXLS.setText(str(self.lsXLS.count()) + " files loaded")
            self.lsXLS.setCurrentRow(0)
            self.LblStatus.clear()
            self.hcmgis_set_status_bar(self.status,self.LblStatus)
        else:
            QMessageBox.warning(None, "Choose Folder", 'Please choose a folder, not a disk like C:/')
        
        
    def run(self):             		
        item_count = 0
        error_count = 0
        items = []
        for index in range(self.lsXLS.count()):
            items.append(self.lsXLS.item(index))
        self.txtError.clear()
        self.lsXLS.blockSignals(True)
        self.LinInputFolder.setEnabled(False)
        self.BtnInputFolder.setEnabled(False)
    
        self.status_bar.setEnabled(False)			
    
        for item in items:
            self.lsXLS.setCurrentRow(item_count)		
            input_xls_name = item.text()
            temp_file_name = item.text()
            output_file_name = temp_file_name.replace(".xlsx", ".csv", 1)
            message = hcmgis_xls2csv(input_xls_name, output_file_name, self.hcmgis_status_callback)
            if message:
                #QMessageBox.critical(self.iface.mainWindow(), "CSV Point Convert", message)
                error_count+=1
                self.txtError.append(str(error_count)+ ". "+ input_xls_name + ": " + message)
                continue
            else:
                item_count +=1
                self.LblStatus.setText (str(item_count)+"/ "+ str(self.lsXLS.count()) + " files converted")	
        
        self.lsXLS.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)	
        self.status_bar.setEnabled(True)

class hcmgis_mapbox_dialog(hcmgis_dialog, Ui_hcmgis_mapbox_form):	
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)    
        self.CboStyleType.currentIndexChanged.connect(self.StyleTypeChange)
        self.CboMapboxStyle.currentIndexChanged.connect(self.MapboxStyleChange)
        self.LblView.openExternalLinks()
        self.CboMapboxStyle.setCurrentIndex(-1)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)            
        self.LinAccessToken.setText('pk.eyJ1IjoidGhhbmdxZCIsImEiOiJucHFlNFVvIn0.j5yb-N8ZR3d4SJAYZz-TZA')   
        self.TxtStyleWMTS.clear()
       
    def StyleTypeChange(self):
        self.TxtStyleWMTS.clear()
        if (self.CboStyleType.currentIndex() == 0 ): #Mapbox default Style
            self.CboMapboxStyle.setEnabled(True)
            self.TxtStyleWMTS.setReadOnly(True)
        else: 
            self.CboMapboxStyle.setCurrentIndex(-1)
            self.CboMapboxStyle.setEnabled(False)
            self.TxtStyleWMTS.setReadOnly(False)

    def MapboxStyleChange(self):
        self.TxtStyleWMTS.clear()
        if self.CboStyleType.currentIndex() == 0: #Mapbox default Style
            ViewURL = 'https://api.mapbox.com/styles/v1/mapbox/' + self.CboMapboxStyle.currentText()
            ViewURL += '.html?fresh=true&title=copy&access_token='+ self.LinAccessToken.text()      
     
            StyleWMTS = 'https://api.mapbox.com/styles/v1/mapbox/' + self.CboMapboxStyle.currentText()
            StyleWMTS += '/wmts?service=WMTS&request=GetCapabilities&access_token='+ self.LinAccessToken.text()   
            self.TxtStyleWMTS.setPlainText(StyleWMTS)
        else:
            if (self.TxtStyleWMTS.toPlainText() != None):
                StyleWMTS =  self.TxtStyleWMTS.toPlainText()
                ViewURL = StyleWMTS.replace('/wms?','.html?fresh=true&title=view')
   
        
    def run(self):
        hcmgis_mapbox(self.TxtStyleWMTS.toPlainText())	
        return		


 