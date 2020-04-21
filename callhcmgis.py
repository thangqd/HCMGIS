from qgis.core import QgsApplication, QgsProcessingFeedback
from qgis.analysis import QgsNativeAlgorithms
QgsApplication.setPrefixPath(r'C:\OSGeo4W64\apps\qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()
import sys
## Add the path to processing so we can import it next
sys.path.append(r'C:\OSGeo4W64\apps\qgis\python\plugins')
sys.path.append("C:\\Users\DELLG7\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\HCMGIS") # Location of HCMGIS Plugin on your computer

## Imports usually should be at the top of a script but this unconventional
## order is necessary here because QGIS has to be initialized first
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

from hcmgis_library import *

#######################################
## in QGIS Pyghon Console: just type from HCMGIS.hcmgis_library import * without any imports above
#from HCMGIS.hcmgis_library import *

## in your PyGIS code, just copy hcmgis_library.py to your folder
## or adding through sys.path.append("C:\\Users\DELLG7\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\HCMGIS") # Location of HCMGIS Plugin on your computer
# an then import by "from hcmgis_library import".
#######################################

#########################################################
## HCMGIS function without any parameters
#hcmgis_basemap_load()
## Add dozens of beautiful basemaps to XYZ Tiles of QGIS, ready for use

#hcmgis_covid19()
## Download Global COVID-19 live update

#hcmgis_covid19_timeseries()
## Download Global COVID-19 Timeseries

#hcmgis_covid19_vietnam()
## Download Vietnam COVID-19 live update in Polygon

########################################################
## HCMGIS function with parameters
## PLEASE DON'T MIND the parameter 'status_callback = None' in these functions because it is writen for HCMGIS Plugin
## with GUI interaction and also for running in Python console

## Create Medial Axis/ Skeleton from Road in Polygon
#input = "D:\\osm\\road.shp"
#output = "D:\\osm\\skeleton.shp"
#hcmgis_medialaxis(input, 'OBJECTID', 1,output,status_callback = None)
## hcmgis_medialaxis(layer, field, density,output,status_callback = None):
## field: unique field of inputlayer
## density (float value): densify geometries with given an interval (in this case the density is 1 meter). Smaller density value returns smoother centerline but slower

## Create Centerline from Bulding block
input = "D:\\osm\\block.shp" # your polygon input
output = "D:\\osm\\centerline.shp" #  your centerline output in .sqlite, .shp, .geojson, .gpkg,  or kml
hcmgis_centerline(input, 1, True, 2,output,status_callback = None)
##hcmgis_centerline(layer,density,chksurround,distance,output,status_callback = None):
##density (float value): densify geometries with given an interval (in this case the density is 1 meter). Smaller density value returns smoother centerline but slower
##chksurround: if chksurround is True, then the function will also create a surrounding 'centerline' with a "distance" to the bounding box of building block

## Closest/ farthest pair of points
#input = "D:\\osm\\points.shp"
#closest = "D:\\osm\\closest.shp"
#farthest = "D:\\osm\\farthest.shp"
#hcmgis_closest_farthest(input,'fid', closest, farthest, status_callback = None)
## hcmgis_closest_farthest(layer,field,closest,farthest,status_callback = None): "field": the unique field of input layer

## Largest Empty Circle
#input = "D:\\osm\\points.shp"
#output = "D:\\osm\lec.shp"
#hcmgis_lec(input,'fid', output, status_callback = None)
## hcmgis_lec(layer,field,output,status_callback = None): "field": the unique field of input layer



