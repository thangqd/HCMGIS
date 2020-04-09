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
from owslib.wfs import WebFeatureService
#from owslib.ogcapi import Features
from qgis.gui import QgsMessageBar
import qgis.utils
from glob import glob
import urllib, re, ssl
from PyQt5 import QtCore

try:
    from .hcmgis_library import *
except:
    from hcmgis_library import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from hcmgis_opendata_form import *
from hcmgis_geofabrik_form import *
from hcmgis_gadm_form import *
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
from hcmgis_format_convert_form import *
from hcmgis_csv2shp_form import *
from hcmgis_txt2csv_form import *
from hcmgis_xls2csv_form import *

# ------------------------------------------------------------------------------
#    hcmgis_dialog - base class for hcmgis dialogs containing utility functions
# ------------------------------------------------------------------------------
class hcmgis_dialog(QtWidgets.QDialog):
    def __init__(self, iface):
        QtWidgets.QDialog.__init__(self)
        self.iface = iface

    def hcmgis_find_layer_by_data_source(self, file_name):
        if not file_name:
            return None

        # URI notation used by the API to distinguish layers within files that contain multiple layers
        # Simple formats like shapefile and GeoJSON still have these in the mapLayers() list
        if not file_name.find("|") >= 0:
            file_name = file_name + "|layerid=0"

        for layer_name, layer in QgsProject.instance().mapLayers().items():
            if layer.dataProvider() and (file_name == layer.dataProvider().dataSourceUri()):
                return layer

        return None

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

    def hcmgis_temp_file_name(self, temp, suffix):
        preferred = os.getcwd() +"/" + temp + suffix
        if not os.path.isfile(preferred):
            return preferred

        for x in range(2, 10):
            name = os.getcwd() + temp + unicode(x) + suffix
            if not os.path.isfile(name):
                return name

        return preferred


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
    server_types = ['WFS',
                    'ArcGIS Feature Server'
                ]
    arcgis_servers = []
    arcgis_urls = []
    wfs_servers = ['HCMGIS OpenData',
                  'OpenDevelopmetMekong',
                  'OpenDevelopmetCambodia',
                  'OpenDevelopmentLao',
                  'OpenDevelopmentMyanmar',
                  'OpenDevelopmentVietnam',
                  'ISRIC Data Hub',
                  'World Food Programme',
                  'PUMA - World Bank Group'
                ]

    wfs_urls = [
        'https://opendata.hcmgis.vn/geoserver',
        'https://data.opendevelopmentmekong.net/geoserver/ODMekong',
        'https://data.opendevelopmentmekong.net/geoserver/ODCambodia',
        'https://data.opendevelopmentmekong.net/geoserver/ODLao',
        'https://data.opendevelopmentmekong.net/geoserver/ODMyanmar',
        'https://data.opendevelopmentmekong.net/geoserver/ODVietnam',
        'https://data.isric.org/geoserver',
        'https://geonode.wfp.org/geoserver',
        'https://puma.worldbank.org/geoserver'
#         'http://webgis.regione.sardegna.it/geoservers',
#         ''

# http://geomap.reteunitaria.piemonte.it/ws/gsareprot/rp-01/areeprotwfs/wfs_gsareprot_1?service=WFS&request=getCapabilities 

# http://demo.opengeo.org/geoserver/wfs?service=wfs&version=1.1.0&request=getCapabilities

# http://mrdata.usgs.gov/services/mt?request=getcapabilities&service=WFS&version=1.0.0&

# http://mrdata.usgs.gov/services/tx?request=getcapabilities&service=WFS&version=1.0.0&

# http://mrdata.usgs.gov/services/mrds?request=getcapabilities&service=WFS&version=1.0.0

# http://sdi.geoportal.gov.pl/wfs_prg/wfservice.aspx?REQUEST=GetCapabilities&SERVICE=WFS&VERSION=1.1.0
        ]
  
    def hcmgis_fill_table_widget_with_wfs_layers0(self,table_widget, idx, TxtTitle, TxtAbstract, status_callback = None):	
        table_widget.setRowCount(0) 
        TxtTitle.clear()
        TxtAbstract.clear()             		       
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            #wfs = urllib.request.urlopen(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities',context=ssl._create_unverified_context())
            #wfs = urllib.request.urlopen(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities')
            wfs = requests.get(self.wfs_urls[idx] +'/ows?service=wfs&version=2.0.0&request=GetCapabilities',verify = False)
           
            if wfs is not None:              
                #data = wfs.read().decode('utf-8')
                data = wfs.text
                #print (data)
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
                print(server_title)   
                print(server_abstract)   
                #print(layer_name)   
                #print(layer_title)       

                if layer_name is not None: 
                    if len(server_title)>0:
                        TxtTitle.insertPlainText(server_title[0])
                    if len (server_abstract)>0:
                        TxtAbstract.insertPlainText(server_abstract[0].replace('&#13;','')) #delete unwanted character before \n
                    #layer_name.remove(layer_name[0])
                    #layer_title.remove(layer_title[0])
                    for i in range (len(layer_name)):  
                        table_widget.insertRow(i)
                        table_widget.setItem(i,0, QTableWidgetItem(layer_name[i]))
                        table_widget.setItem(i,1, QTableWidgetItem(layer_title[i]))
                        table_widget.item(i,0).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        table_widget.item(i,1).setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                        status_callback((i/len(layer_name))*100,None)
                   
                    status_callback(((i+1)/len(layer_name))*100,None)
                    message = str(i+1) + " WFS layers loaded"
                    MessageBar = qgis.utils.iface.messageBar()
                    MessageBar.pushMessage(message, 0, 3)  		
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
        self.TblWFSLayers.doubleClicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)	
        self.LinOutputFolder.setText(os.getcwd())                                             
        self.ChkSaveShapefile.stateChanged.connect(self.toggleouputfolder)
        
        columns = ['Name', 'Title']            
        self.TblWFSLayers.setColumnCount(len(columns))
        self.TblWFSLayers.setHorizontalHeaderLabels(columns) 
        self.TblWFSLayers.resizeColumnsToContents()
        self.TblWFSLayers.resizeRowsToContents()
        self.TblWFSLayers.horizontalHeader().setStretchLastSection(True)	
        # self.TblWFSLayers.setDragDropMode(QAbstractItemView.DragOnly)  
        # self.TblWFSLayers.setDragEnabled(True) 
        
        self.cboServerType.currentIndexChanged.connect(self.updateServer)
        self.cboServerType.addItems(self.server_types)        
        self.cboServerName.setCurrentIndex(0)


        self.cboServerName.setCurrentIndex(-1)
        self.cboServerName.currentIndexChanged.connect(self.readwfs)
        self.CboFormat.setEnabled(False)
        self.hcmgis_set_status_bar(self.status)	
        
     

    def updateServer(self):
        self.cboServerName.clear()
        self.TxtTitle.clear()
        self.TxtAbstract.clear()
        self.TblWFSLayers.setRowCount(0)

        if self.cboServerType.currentIndex() == 0:             #'WFS'
            self.cboServerName.addItems(self.wfs_servers)
            self.cboServerName.setCurrentIndex(0)

    def readwfs(self):
        if (self.cboServerName.currentIndex()>-1):
            self.hcmgis_set_status_bar(self.status)	
            self.LblSattus.clear()
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
        self.hcmgis_set_status_bar(self.status)	
        self.LblSattus.clear()
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
        print(rows)
        print(layernames)
        ii = 0        
        if layernames is not None:
            for layer_name in layernames:
                uri = opendata_url + "/ows?service=WFS&version=1.0.0&request=GetFeature&typename="+ str(layer_name)                       	
                #uri = opendata_url + "/ows?service=WFS&request=GetFeature&typename="+ str(layer_name)                       	
                if (not self.ChkSaveShapefile.isChecked()):
                    try:
                        success = qgis.utils.iface.addVectorLayer(uri, layer_name,"WFS")
                        if success:                           
                            ii+=1		
                            self.LblSattus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers loaded")	    			
                            percent_complete = ii/len(layernames)*100
                            self.status.setValue(percent_complete)
                            message = str(int(percent_complete)) + "%"
                            self.status.setFormat(message)
                    except Exception as e:                      
                        QMessageBox.critical(self.iface.mainWindow(), "WFS", e)                                          
                else:   
                    uri = opendata_url + "/ows?service=WFS&version=1.0.0&request=GetFeature&typename="+ str(layer_name)   
                    #uri = opendata_url + "/ows?service=WFS&request=GetFeature&typename="+ str(layer_name)                       	                                       	                   
                    uri += '&outputFormat='
                    uri += wfs_format
                    try:
                        # filename = outdir + "\\"+ str(layer_name).replace(":","_") + ext
                        # ssl._create_default_https_context = ssl._create_unverified_context
                        # #urllib.request.urlretrieve(uri,filename,context=ssl._create_unverified_context())
                        # urllib.request.urlretrieve(uri,filename)
                        # layer = QgsVectorLayer(filename, QFileInfo(filename).baseName(), 'ogr')
                        # layer.dataProvider().setEncoding(u'UTF-8')
                        # if (layer.isValid()):                     
                        #     QgsProject.instance().addMapLayer(layer)                         
                        #     ii+=1		
                        #     self.LblSattus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers saved and loaded")	
                        #     percent_complete = ii/len(layernames)*100
                        #     self.status.setValue(percent_complete)
                        #     message = str(int(percent_complete)) + "%"
                        #     self.status.setFormat(message)  
                        headers = ""
                        contents = requests.get(uri, headers=headers, stream=True, allow_redirects=True, verify = False)
                        filename = outdir + "\\"+ str(layer_name).replace(":","_") + ext    
                        #total_size = int(len(contents.content))
                        #total_size_MB = round(total_size*10**(-6),2)
                        #chunk_size = int(total_size/100)                        
                        if  (contents.status_code == 200):
                            #print ('total_length MB:', total_size_MB)
                            i = 0
                            f = open(filename, 'wb')                           
                            for chunk in contents.iter_content(chunk_size = 1024):
                                if not chunk:
                                    break
                                f.write(chunk)
                                # self.status.setValue(i)
                                # message = str(int(i)) + "%"
                                # self.status.setFormat(message) 
                                # self.iface.statusBarIface().showMessage(message)
                                #self.hcmgis_status_callback(i/1024, None)
                                #print (str(i))
                                i+=1                                                      
                            f.close()
                            layer = QgsVectorLayer(filename, QFileInfo(filename).baseName(), 'ogr')
                            layer.dataProvider().setEncoding(u'UTF-8')
                            if (layer.isValid()):                     
                                QgsProject.instance().addMapLayer(layer)                         
                                ii+=1		
                                self.LblSattus.setText (str(ii)+"/ "+ str(len(layernames)) + " layers saved and loaded")	
                                percent_complete = ii/len(layernames)*100
                                self.status.setValue(percent_complete)
                                message = str(int(percent_complete)) + "%"
                                self.status.setFormat(message)  
                    except Exception as e:
                        qgis.utils.iface.addVectorLayer(uri, str(layer_name),"WFS")    
                        QMessageBox.critical(self.iface.mainWindow(), "WFS", e)
                                 
        return		


class hcmgis_geofabrik_dialog(hcmgis_dialog, Ui_hcmgis_geofabrik_form):		
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.BtnOutputFolder.clicked.connect(self.browse_outfile)	
        self.LinOutputFolder.setText(os.getcwd())    
        self.cboRegion.addItems(self.region)
        self.cboRegion.currentIndexChanged.connect(self.loadcountry)   
        self.cboRegion.setCurrentIndex(-1) 
        self.cboCountry.setCurrentIndex(-1) 
        self.cboCountry.setEnabled(False)
        self.cboCountry.currentIndexChanged.connect(self.loadprovince)
        self.cboProvince.setEnabled(False)
        self.hcmgis_set_status_bar(self.status)		

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
                message = hcmgis_geofabrik2('south-america',self.southamerica_name[country_idx], outdir,self.hcmgis_status_callback)
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
        self.LinOutputFolder.setText(os.getcwd())    
        self.cboCountry.addItems(self.country)
        self.cboCountry.currentIndexChanged.connect(self.updateLOD)   
        self.cboCountry.setCurrentIndex(-1) 
        self.LinLOD.setText('')
        self.hcmgis_set_status_bar(self.status)		
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
# 		#self.BtnOKCancel.accepted.connect(self.run)
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
    epsg_code = [9205, 9205, 
                9206, 
                9207, 9207, 
                9208, 9208, 9208, 9208, 9208, 
                5897, 5897, 5897, 5897, 5897, 5897, 5897, 5897, 5897, 
                9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 9209, 	
                9210, 9210, 9210, 9210, 9210, 9210, 9210,			
                9211, 9211, 9211, 
                9212, 9212, 
                9213, 9213, 
                9214, 9214, 
                9215,
                9216,
                5899, 5899, 5899, 5899, 5899, 5899,
                5898, 
                9217, 9217, 9217,			
                9218, 9218, 9218, 9218, 9218
                ]
    
    def __init__(self, iface):		
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.cboProvinces.setCurrentIndex(-1)
        self.cboEPSG.setCurrentIndex(-1)	
        self.cboProvinces.checked = True
        self.cboEPSG.checked = False
        self.cboEPSG.setEnabled(False)

        self.TxtEPSGInfo.clear()
        self.lnEPSG.clear()
        self.lnZone.clear()

        self.radProvinces.toggled.connect(self.togglerad)
        self.radEPSG.toggled.connect(self.togglerad)
        self.cboEPSG.currentIndexChanged.connect(self.EPSGChange)
        self.cboProvinces.currentIndexChanged.connect(self.ProvincesChange)
        self.cboProvinces.clear()
        self.cboProvinces.addItems(self.provinces)        
   
    def ProvincesChange(self):
        self.lnEPSG.clear()
        self.lnZone.clear()
        i = self.cboProvinces.currentIndex()
        self.lnZone.setText(str(self.zone[i]))
        self.lnEPSG.setText(str(self.epsg_code[i]))
        

    def EPSGChange(self):
        self.LblEPSGInfo.clear()
        EPSGCode = int(self.cboEPSG.currentText().strip())
        i = self.epsg_code.index(EPSGCode) 
        EPSGInfoText = 'Zone name: ' + str (self.zone[i]) 
        
        indices = [i for i, x in enumerate(self.epsg_code) if x == EPSGCode]
        provinces_list = ''
        for indice in indices:
            provinces_list+= str(self.provinces[indice]) + ', '

        ProvincesText = '. Provinces: ' + provinces_list 

        if ProvincesText.endswith(', '):     						
            ProvincesText = ProvincesText[:-(len(', '))] + '.'
        self.TxtEPSGInfo.setText(EPSGInfoText + ProvincesText)

        
    def togglerad(self):
        if self.radProvinces.isChecked():
            self.cboEPSG.setEnabled(False)
            self.TxtEPSGInfo.setEnabled(False)
            self.cboProvinces.setEnabled(True)
            self.lnEPSG.setEnabled(True)	
            self.lnZone.setEnabled(True)
            
        elif self.radEPSG.isChecked():
            self.cboProvinces.setEnabled(False)
            self.lnEPSG.setEnabled(False)	
            self.lnZone.setEnabled(False)	
            self.cboEPSG.setEnabled(True)
            self.TxtEPSGInfo.setEnabled(True)

                        
class hcmgis_medialaxis_dialog(hcmgis_dialog, Ui_hcmgis_medialaxis_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
        self.CboField.setLayer (self.CboInput.currentLayer () )
        self.CboInput.activated.connect(self.update_field) 
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)

                
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

class hcmgis_centerline_dialog(hcmgis_dialog, Ui_hcmgis_centerline_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.PolygonLayer)	
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
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
class hcmgis_closestpair_dialog(hcmgis_dialog, Ui_hcmgis_closestpair_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.CboField.setLayer (self.CboInput.currentLayer () )		
        self.CboInput.activated.connect(self.update_field)
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)           
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
class hcmgis_lec_dialog(hcmgis_dialog, Ui_hcmgis_lec_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.CboField.setLayer (self.CboInput.currentLayer () )	
        self.CboInput.activated.connect(self.update_field)         
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
          
    
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
class hcmgis_merge_dialog(hcmgis_dialog, Ui_hcmgis_merge_form):
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.browseoutfile.clicked.connect(self.browse_outfiles)		
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.hcmgis_fill_list_widget_with_vector_layers(self.sourcelayers)
        self.sourcelayers.setDragDropMode(QAbstractItemView.InternalMove)
        self.outfilename.setText(self.hcmgis_temp_file_name("merge",".shp"))	

    
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

            

class hcmgis_split_dialog(hcmgis_dialog, Ui_hcmgis_split_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)	
        self.CboField.setLayer (self.CboInput.currentLayer () )
        self.CboInput.activated.connect(self.update_field)                
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
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


class hcmgis_font_convert_dialog(hcmgis_dialog, Ui_hcmgis_font_convert_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)		
        self.ListFields.clear()
        self.update_fields()
        self.BtnBrowseOutput.clicked.connect(self.browse_outfiles)
        
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        self.LinOutput.setText(self.hcmgis_temp_file_name("convert_font",".shp"))	
    
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
class hcmgis_split_field_dialog(hcmgis_dialog, Ui_hcmgis_split_field_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)			
        self.CboField.setLayer (self.CboInput.currentLayer () )
        self.CboInput.activated.connect(self.update_field)                
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
    
                
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
class hcmgis_merge_field_dialog(hcmgis_dialog, Ui_hcmgis_merge_field_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)
        self.CboInput.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.update_fields()
        self.BtnApplyClose.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)	
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

# Format Convert
class hcmgis_format_convert_dialog(hcmgis_dialog, Ui_hcmgis_format_convert_form):	
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)	
        self.setupUi(self)	
        self.hcmgis_set_status_bar(self.status)
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
        self.lblStatus.clear()
        self.txtError.clear()
        self.hcmgis_set_status_bar(self.status)
        
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
            self.lblStatus.clear()
            self.txtError.clear()
            self.hcmgis_set_status_bar(self.status)


    def read_files(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None:
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
            self.lblStatus.clear()
            self.txtError.clear()
            self.hcmgis_set_status_bar(self.status)
    
        
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
                self.lblStatus.setText (str(item_count)+"/ "+ str(self.lsFiles.count()) + " files converted")	
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
        self.hcmgis_set_status_bar(self.status)
        self.lsCSV.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_csv)			
        self.lsCSV.currentRowChanged.connect(self.set_field_names)                             
        self.BtnOKCancel.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)

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
            if (field.lower().find("x") >= 0):
                self.longitude_field.setCurrentIndex(index)

            elif (field.lower().find("y") >= 0):
                self.latitude_field.setCurrentIndex(index)

            elif (field.lower().find('lon') >= 0):
                self.longitude_field.setCurrentIndex(index)

            elif (field.lower().find('lat') >= 0):
                self.latitude_field.setCurrentIndex(index)

    def read_csv(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None:
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
            self.lblStatus.clear()
            self.hcmgis_set_status_bar(self.status)
    
        
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
            output_file_name = temp_file_name.replace(".csv", ".shp", 1)

            message = hcmgis_csv2shp(input_csv_name,  latitude_field, longitude_field, \
                output_file_name, self.hcmgis_status_callback)
            if message:
                #QMessageBox.critical(self.iface.mainWindow(), "CSV Point Convert", message)
                error_count+=1
                self.txtError.append(str(error_count)+ ". "+ input_csv_name + ": " + message)
                continue
            else:
                item_count +=1
                self.lblStatus.setText (str(item_count)+"/ "+ str(self.lsCSV.count()) + " files converted")	
        
        self.lsCSV.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)
        self.longitude_field.setEnabled(True)
        self.latitude_field.setEnabled(True)	
        self.status_bar.setEnabled(True)			

        #elif self.hcmgis_find_layer_by_data_source(output_file_name):
        #	self.iface.mapCanvas().refreshAllLayers()

        #else:
        #	self.iface.addVectorLayer(output_file_name, "", "ogr")

# txt2csv
class hcmgis_txt2csv_dialog(hcmgis_dialog, Ui_hcmgis_txt2csv_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.hcmgis_set_status_bar(self.status)
        self.lsTXT.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_txt)			
        self.BtnOKCancel.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)
        
    def read_txt(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None:
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
            self.lblStatus.clear()
            self.hcmgis_set_status_bar(self.status)
    
        
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
            self.lsTXT.setCurrentRow(item_count);		
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
                self.lblStatus.setText (str(item_count)+"/ "+ str(self.lsTXT.count()) + " files converted")	
        
        self.lsTXT.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)	
        self.status_bar.setEnabled(True)	

# xls2csv
class hcmgis_xls2csv_dialog(hcmgis_dialog, Ui_hcmgis_xls2csv_form):		
    def __init__(self, iface):
        hcmgis_dialog.__init__(self, iface)		
        self.setupUi(self)	
        self.hcmgis_set_status_bar(self.status)
        self.lsXLS.clear() 
        self.txtError.clear()
        self.BtnInputFolder.clicked.connect(self.read_xls)			
        self.BtnOKCancel.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.run)	
        
    def read_xls(self):
        newname = QFileDialog.getExistingDirectory(None, "Input Folder",self.LinInputFolder.displayText())
        if newname != None:
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
            self.lblStatus.clear()
            self.hcmgis_set_status_bar(self.status)
    
        
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
                self.lblStatus.setText (str(item_count)+"/ "+ str(self.lsXLS.count()) + " files converted")	
        
        self.lsXLS.blockSignals(False)
        self.LinInputFolder.setEnabled(True)
        self.BtnInputFolder.setEnabled(True)	
        self.status_bar.setEnabled(True)			
        

            
