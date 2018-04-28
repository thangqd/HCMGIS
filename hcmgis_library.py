#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------
#    hcmgis_library - hcmgis operation functions
# --------------------------------------------------------

import io
import re
import csv
import sys
import time
import locale
import random
#import urllib2
import os.path
import operator
import tempfile
import xml.etree.ElementTree

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.gui import QgsMessageBar
#from processing.tools.vector import VectorWriter


# Used instead of "import math" so math functions can be used without "math." prefix
from math import *
global _Unicode, _TCVN3, _VNIWin, _KhongDau
_Unicode = [
u'â',u'Â',u'ă',u'Ă',u'đ',u'Đ',u'ê',u'Ê',u'ô',u'Ô',u'ơ',u'Ơ',u'ư',u'Ư',u'á',u'Á',u'à',u'À',u'ả',u'Ả',u'ã',u'Ã',u'ạ',u'Ạ',
u'ấ',u'Ấ',u'ầ',u'Ầ',u'ẩ',u'Ẩ',u'ẫ',u'Ẫ',u'ậ',u'Ậ',u'ắ',u'Ắ',u'ằ',u'Ằ',u'ẳ',u'Ẳ',u'ẵ',u'Ẵ',u'ặ',u'Ặ',
u'é',u'É',u'è',u'È',u'ẻ',u'Ẻ',u'ẽ',u'Ẽ',u'ẹ',u'Ẹ',u'ế',u'Ế',u'ề',u'Ề',u'ể',u'Ể',u'ễ',u'Ễ',u'ệ',u'Ệ',u'í',u'Í',u'ì',u'Ì',u'ỉ',u'Ỉ',u'ĩ',u'Ĩ',u'ị',u'Ị',    
u'ó',u'Ó',u'ò',u'Ò',u'ỏ',u'Ỏ',u'õ',u'Õ',u'ọ',u'Ọ',u'ố',u'Ố',u'ồ',u'Ồ',u'ổ',u'Ổ',u'ỗ',u'Ỗ',u'ộ',u'Ộ',u'ớ',u'Ớ',u'ờ',u'Ờ',u'ở',u'Ở',u'ỡ',u'Ỡ',u'ợ',u'Ợ',    
u'ú',u'Ú',u'ù',u'Ù',u'ủ',u'Ủ',u'ũ',u'Ũ',u'ụ',u'Ụ',u'ứ',u'Ứ',u'ừ',u'Ừ',u'ử',u'Ử',u'ữ',u'Ữ',u'ự',u'Ự',u'ỳ',u'Ỳ',u'ỷ',u'Ỷ',u'ỹ',u'Ỹ',u'ỵ',u'Ỵ',u'ý',u'Ý'    
]
_TCVN3 = [
u'©',u'¢',u'¨',u'¡',u'®',u'§',u'ª',u'£',u'«',u'¤',u'¬',u'¥',u'­',u'¦',u'¸',u'¸',u'µ',u'µ',u'¶',u'¶',u'·',u'·',u'¹',u'¹',
u'Ê',u'Ê',u'Ç',u'Ç',u'È',u'È',u'É',u'É',u'Ë',u'Ë',u'¾',u'¾',u'»',u'»',u'¼',u'¼',u'½',u'½',u'Æ',u'Æ',
u'Ð',u'Ð',u'Ì',u'Ì',u'Î',u'Î',u'Ï',u'Ï',u'Ñ',u'Ñ',u'Õ',u'Õ',u'Ò',u'Ò',u'Ó',u'Ó',u'Ô',u'Ô',u'Ö',u'Ö',u'Ý',u'Ý',u'×',u'×',u'Ø',u'Ø',u'Ü',u'Ü',u'Þ',u'Þ',    
u'ã',u'ã',u'ß',u'ß',u'á',u'á',u'â',u'â',u'ä',u'ä',u'è',u'è',u'å',u'å',u'æ',u'æ',u'ç',u'ç',u'é',u'é',u'í',u'í',u'ê',u'ê',u'ë',u'ë',u'ì',u'ì',u'î',u'î',    
u'ó',u'ó',u'ï',u'ï',u'ñ',u'ñ',u'ò',u'ò',u'ô',u'ô',u'ø',u'ø',u'õ',u'õ',u'ö',u'ö',u'÷',u'÷',u'ù',u'ù',u'ú',u'ú',u'û',u'û',u'ü',u'ü',u'þ',u'þ',u'ý',u'ý'     
]
_VNIWin = [
u'aâ',u'AÂ',u'aê',u'AÊ',u'ñ',u'Ñ',u'eâ',u'EÂ',u'oâ',u'OÂ',u'ô',u'Ô',u'ö',u'Ö',u'aù',u'AÙ',u'aø',u'AØ',u'aû',u'AÛ',u'aõ',u'AÕ',u'aï',u'AÏ',
u'aá',u'AÁ',u'aà',u'AÀ',u'aå',u'AÅ',u'aã',u'AÃ',u'aä',u'AÄ',u'aé',u'AÉ',u'aè',u'AÈ',u'aú',u'AÚ',u'aü',u'AÜ',u'aë',u'AË',
u'eù',u'EÙ',u'eø',u'EØ',u'eû',u'EÛ',u'eõ',u'EÕ',u'eï',u'EÏ',u'eá',u'EÁ',u'eà',u'EÀ',u'eå',u'EÅ',u'eã',u'EÃ',u'eä',u'EÄ',u'í',u'Í',u'ì',u'Ì',u'æ',u'Æ',u'ó',u'Ó',u'ò',u'Ò',    
u'où',u'OÙ',u'oø',u'OØ',u'oû',u'OÛ',u'oõ',u'OÕ',u'oï',u'OÏ',u'oá',u'OÁ',u'oà',u'OÀ',u'oå',u'OÅ',u'oã',u'OÃ',u'oä',u'OÄ',u'ôù',u'ÔÙ',u'ôø',u'ÔØ',u'ôû',u'ÔÛ',u'ôõ',u'ÔÕ',u'ôï',u'ÔÏ',    
u'uù',u'UÙ',u'uø',u'UØ',u'uû',u'UÛ',u'uõ',u'UÕ',u'uï',u'UÏ',u'öù',u'ÖÙ',u'öø',u'ÖØ',u'öû',u'ÖÛ',u'öõ',u'ÖÕ',u'öï',u'ÖÏ',u'yø',u'YØ',u'yû',u'YÛ',u'yõ',u'YÕ',u'î',u'Î',u'yù',u'YÙ'    
]
_KhongDau = [
u'a',u'A',u'a',u'A',u'd',u'D',u'e',u'E',u'o',u'O',u'o',u'O',u'u',u'U',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',
u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',
u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e','uE',u'e',u'E',u'e',u'E',u'e',u'E',u'i',u'I',u'i',u'I',u'i',u'I',u'i',u'I',u'i',u'I',
u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',
u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'y',u'Y',u'y',u'Y',u'y',u'Y',u'y',u'Y',u'y',u'Y'
]

#--------------------------------------------------------
#    Add basemap
# --------------------------------------------------------

def hcmgis_basemap(self, service_url, name):
	import requests
	import qgis.utils	
	service_uri = "type=xyz&zmin=0&zmax=22&url=http://"+requests.utils.quote(service_url)
	tms_layer = qgis.utils.iface.addRasterLayer(service_uri, name, "wms")
					
#--------------------------------------------------------
#    hcmgis_medialaxis - Create skeleton/ medial axis/ centerline of roads, rivers and similar linear structures
# --------------------------------------------------------

#for alg in QgsApplication.processingRegistry().algorithms(): print(alg.id())

def hcmgis_medialaxis(qgis, layer,selectedfield,density):		
	import processing
	## create skeleton/ media axis
	parameters1 = {'INPUT':layer,
					'OUTPUT':  "memory:polygon"}
	polygon = processing.run('qgis:saveselectedfeatures',parameters1)
	
	parameters2 = {'INPUT':polygon['OUTPUT'],
					'OUTPUT':  "memory:polyline"}
	polyline = processing.run('qgis:polygonstolines',parameters2)	
	
	parameters3 = {'INPUT': polyline['OUTPUT'],
					'DISTANCE' : density,
					'START_OFFSET' : 0, 
					'END_OFFSET' : 0,
					'OUTPUT' : "memory:points"} 
	#processing.runAndLoadResults('qgis:pointsalonglines', parameters3)
	points = processing.run('qgis:pointsalonglines', parameters3)	
	
	parameters4 = {'INPUT': points['OUTPUT'],
					 'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'} 
	voronoipolygon = processing.run('qgis:voronoipolygons', parameters4)	 
	
	parameters5 = {'INPUT': voronoipolygon['OUTPUT'],
					'OUTPUT' : 'memory:voronoipolyline'} 
	voronoipolyline = processing.run('qgis:polygonstolines',parameters5)
	
	
	parameters6 = {'INPUT': voronoipolyline['OUTPUT'],					
					'OUTPUT' : 'memory:explode'}
	explode = processing.run('qgis:explodelines',parameters6)
	
	parameters7 = {'INPUT': explode['OUTPUT'],
					'PREDICATE' : [6], # within					
					'INTERSECT': polygon['OUTPUT'],		
					'METHOD' : 0,
					'OUTPUT' : 'memory:candidate'}
	candidate= processing.run('qgis:selectbylocation',parameters7)
	
	
	parameters8 = {'INPUT':candidate['OUTPUT'],
					'OUTPUT':  'memory:medialaxis'}
	medialaxis = processing.run('qgis:saveselectedfeatures',parameters8)
	
	parameters9 = {'INPUT':medialaxis['OUTPUT'],
					'OUTPUT':  'memory:deleteduplicategeometries'}
	deleteduplicategeometries = processing.run('qgis:deleteduplicategeometries',parameters9)
	
	parameter10 =  {'INPUT':deleteduplicategeometries['OUTPUT'],
					'FIELD' : selectedfield,
					'OUTPUT':  "memory:medialaxis_dissolve"}
	medialaxis_dissolve = processing.run('qgis:dissolve',parameter10) 
	
	parameter11 = {'INPUT':medialaxis_dissolve['OUTPUT'],
					'METHOD' : 0,
					'TOLERANCE' : 1,
					'OUTPUT':  "memory:medialaxis"}
	processing.runAndLoadResults('qgis:simplifygeometries',parameter11) 
	
	#Calculate min/ max/ average width 
	# parameter12 =  {'INPUT': explode['OUTPUT'],	
					# 'OVERLAY': polygon['OUTPUT'], 
					# 'OUTPUT':  "memory:clip"}
	# clip = processing.runAndLoadResults('qgis:clip',parameter12) 
	
	# parameter13 = { 'INPUT' : clip['OUTPUT'], 
					# 'OUTPUT' : 'memory:' }
	# clip_clean = processing.runAndLoadResults('qgis:deleteduplicategeometries',parameter13) 

	
	# parameter14 = {'INPUT': clip_clean['OUTPUT'],
					# 'PREDICATE' : [4], # touch					
					# 'INTERSECT': medialaxis_collect['OUTPUT'],		
					# 'METHOD' : 0, 
					# 'OUTPUT' : 'memory:width'}
	# width_list= processing.run('qgis:selectbylocation',parameter14)
	
	# parameters15 = {'INPUT':width_list['OUTPUT'],
					# 'OUTPUT':  "memory:width_list"}
	# width_list = processing.runAndLoadResults('qgis:saveselectedfeatures',parameters15)

	################################################################
	#case 
	# when degrees(azimuth(end_point($geometry), start_point($geometry))) > 180 then degrees(azimuth(end_point($geometry), start_point($geometry))) - 180
	#else degrees(azimuth(end_point($geometry), start_point($geometry)))
	#end
	
	return

def hcmgis_centerline(qgis,layer,density,chksurround,distance):		
	import processing
	convexhull	= None
	## extract gaps of polygon
	# fix geometries
	parameters1_1 = {'INPUT':layer,
				'OUTPUT': 'memory:fix'}
	fix = processing.run('qgis:fixgeometries',parameters1_1)	
	
	# aggregate polygons	
	parameters1_2 = {'INPUT':fix['OUTPUT'],
					'GROUP_BY' : 'NULL',
					'AGGREGATES' : [],
					'OUTPUT':  'memory:aggregate'}
	#aggregate = processing.runAndLoadResults('qgis:aggregate',parameters1_2)
	aggregate = processing.run('qgis:aggregate',parameters1_2)
	
	# delete holes in aggregated polygons	
	parameter1_3 = {'INPUT':aggregate['OUTPUT'],
					'MIN_AREA' : 0,
					'OUTPUT':  "memory:deleteholes"}
	deleteholes = processing.run('qgis:deleteholes',parameter1_3) 
		
	# simplify geometries
	parameter1_4 = {'INPUT':deleteholes['OUTPUT'],
					'METHOD' : 0,
					'TOLERANCE' : 1,
					'OUTPUT':  "memory:simplify"}
	simplify = processing.run('qgis:simplifygeometries',parameter1_4) 	
	
	
	#create convexhull
	parameters1_5 = {'INPUT':simplify['OUTPUT'],					
					'OUTPUT':  "memory:convexhull"}
	convexhull = processing.run('qgis:convexhull',parameters1_5)
	
	if chksurround:
		parameters1_6 = {'INPUT':convexhull['OUTPUT'],
					'DISTANCE' : distance,
					'SEGMENTS' : 5,
					'END_CAP_STYLE' : 0, 
					'JOIN_STYLE' : 0, 
					'MITER_LIMIT' : 2, 
					'DISSOLVE' : False, 
					'OUTPUT':  "memory:convexhull"}
		convexhull = processing.run('qgis:buffer',parameters1_6)
	
	
	parameters1_7 = {'INPUT': convexhull['OUTPUT'],
					'OVERLAY' : simplify['OUTPUT'],
					'OUTPUT' : 'memory:polygon'} 					
	polygon = processing.run('qgis:symmetricaldifference',parameters1_7)	
	

	## create centerline
	parameters2 = {'INPUT':polygon['OUTPUT'],
					'OUTPUT':  "memory:polyline"}
	polyline = processing.run('qgis:polygonstolines',parameters2)	
	
	parameters3 = {'INPUT': polyline['OUTPUT'],
					'DISTANCE' : density,
					'START_OFFSET' : 0, 
					'END_OFFSET' : 0,
					'OUTPUT' : "memory:points"} 
	points = processing.run('qgis:pointsalonglines', parameters3)	
	
	parameters4 = {'INPUT': points['OUTPUT'],
					 'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'} 
	voronoipolygon = processing.run('qgis:voronoipolygons', parameters4)	 
	
	parameters5 = {'INPUT': voronoipolygon['OUTPUT'],
					'OUTPUT' : 'memory:voronoipolyline'} 
	voronoipolyline = processing.run('qgis:polygonstolines',parameters5)
	
	
	parameters6 = {'INPUT': voronoipolyline['OUTPUT'],					
					'OUTPUT' : 'memory:explode'}
	explode = processing.run('qgis:explodelines',parameters6)
	
	parameters7 = {'INPUT': explode['OUTPUT'],
					'PREDICATE' : [6], # within					
					'INTERSECT': polygon['OUTPUT'],		
					'METHOD' : 0,
					'OUTPUT' : 'memory:candidate'}
	candidate= processing.run('qgis:selectbylocation',parameters7)
	
	
	parameters8 = {'INPUT':candidate['OUTPUT'],
					'OUTPUT':  "memory:medialaxis"}
	medialaxis = processing.run('qgis:saveselectedfeatures',parameters8)
	
	parameters9 = {'INPUT':medialaxis['OUTPUT'],
					'OUTPUT':  'memory:deleteduplicategeometries'}
	deleteduplicategeometries = processing.run('qgis:deleteduplicategeometries',parameters9)
	
	parameter10 =  {'INPUT':deleteduplicategeometries['OUTPUT'],
					'OUTPUT':  "memory:medialaxis_dissolve"}
	medialaxis_dissolve = processing.run('qgis:dissolve',parameter10) 
	
	parameter11 = {'INPUT':medialaxis_dissolve['OUTPUT'],
					'METHOD' : 0,
					'TOLERANCE' : 1,
					'OUTPUT':  "memory:centerline"}
	processing.runAndLoadResults('qgis:simplifygeometries',parameter11)  	
	
	return

################################################################
# Finding closest/ Farthest pair of Points
################################################################
def hcmgis_closestpair(qgis,layer,field):		
	import processing
	if layer is None:
		return 'No selected layer!'
	if ((field is None) or (field == '')):
		return 'Please select an unique field!'	
		
	parameters1 = {'INPUT':layer,
					'OUTPUT':  "memory:delaunay_polygon"}
	delaunay_polygon = processing.run('qgis:delaunaytriangulation',parameters1)

	parameters2 = {'INPUT':delaunay_polygon['OUTPUT'],
					'OUTPUT':  "memory:delaunay_polyline"}
	delaunay_polyline = processing.run('qgis:polygonstolines',parameters2)	

	parameters3 = {'INPUT': delaunay_polyline['OUTPUT'],					
					'OUTPUT' : 'memory:delaunay_explode'}
	delaunay_explode = processing.run('qgis:explodelines',parameters3)

	lengths = []
	closest_candidates = delaunay_explode['OUTPUT']
	# calculate length in meters
	for feature in closest_candidates.getFeatures():
		length = feature.geometry().length() 		
		lengths.append(length)
	
	minlength = str(min(lengths))	

	selection = closest_candidates.getFeatures(QgsFeatureRequest(QgsExpression('$length'  + '=' + minlength)))
	ids = [s.id() for s in selection]
	closest_candidates.selectByIds(ids)
	
	parameters3_1 = {'INPUT':closest_candidates,
	 				'OUTPUT':  'memory:min_delaunay'
					 }
	min_delaunay = processing.run('qgis:saveselectedfeatures',parameters3_1)

	parameters3_2 = {'INPUT': layer,
					'PREDICATE' : [4],#touch
					'INTERSECT' : min_delaunay['OUTPUT'],
					'METHOD' : 0,									
					'OUTPUT' : 'memory:closest'
					}
	
	closest = processing.run('qgis:selectbylocation',parameters3_2)
	
	parameters3_3 = {'INPUT': closest['OUTPUT'],
	 				'OUTPUT':  'memory:closest'
					 }
	closest_points = processing.run('qgis:saveselectedfeatures',parameters3_3)
	
	parameters3_4 = {'INPUT':closest_points['OUTPUT'],
					'INPUT_FIELD' : field,
					 'TARGET' : closest_points['OUTPUT'],
					 'TARGET_FIELD' : field,
					 'MATRIX_TYPE' : 2,
					 'NEAREST_POINTS' : 0,
					 'OUTPUT':  'memory:closest_points'
					}
	closest_points = processing.run('qgis:distancematrix',parameters3_4)
	
	parameters3_5 = {'INPUT':closest_points['OUTPUT'],
					'COLUMN' : ['MEAN','STDDEV','MIN'],
	 				'OUTPUT':  'memory:closest_points'
					 }
	processing.runAndLoadResults('qgis:deletecolumn',parameters3_5)


	#Finding farthest pair of points
	parameters4 = {'INPUT': delaunay_polygon['OUTPUT'],								
					'OUTPUT' : 'memory:convexhull'}
	convexhull = processing.run('qgis:dissolve',parameters4)

	parameters5 = {'INPUT': layer,
					'PREDICATE' : [4],
					'INTERSECT' : convexhull['OUTPUT'],
					'METHOD' : 0,									
					'OUTPUT' : 'memory:convexhull_vertices'
					}
	
	convexhull_vertices = processing.run('qgis:selectbylocation',parameters5)

	parameters6 = {'INPUT':layer,
					'OUTPUT':  "memory:farthest_candidates"}
	farthest_candidates = processing.run('qgis:saveselectedfeatures',parameters6)
	

	parameters7 = {'INPUT':farthest_candidates['OUTPUT'],
					'INPUT_FIELD' : field,
					 'TARGET' : farthest_candidates['OUTPUT'],
					 'TARGET_FIELD' : field,
					 'MATRIX_TYPE' : 2,
					 'NEAREST_POINTS' : 0,
					 'OUTPUT':  'memory:distance_matrix'
					}
	distance_matrix = processing.run('qgis:distancematrix',parameters7)
	

	max_distance = distance_matrix['OUTPUT']
	values = []
	idx =  max_distance.dataProvider().fieldNameIndex("MAX")
	for feat in max_distance.getFeatures():
		attrs = feat.attributes()
		values.append(attrs[idx])
	
	maxvalue = str(max(values))	
	selection = max_distance.getFeatures(QgsFeatureRequest(QgsExpression('"MAX"' + '=' + maxvalue)))
	ids = [s.id() for s in selection]
	max_distance.selectByIds(ids)
	
	parameters8 = {'INPUT':max_distance,
	 				'OUTPUT':  'memory:farthest'
					 }
	farthest = processing.run('qgis:saveselectedfeatures',parameters8)

	parameters9 = {'INPUT':farthest['OUTPUT'],
					'COLUMN' : ['MEAN','STDDEV','MIN'],
	 				'OUTPUT':  'memory:farthest_points'
					 }
	processing.runAndLoadResults('qgis:deletecolumn',parameters9)

	return


# --------------------------------------------------------
#    hcmgis_merge - Merge layers to single shapefile
#	 Reference: mmqgis
# --------------------------------------------------------

def hcmgis_merge(qgis, layernames, savename, addlayer):
	layers = []
	field_list = []
	totalfeaturecount = 0

	for x in range(0, len(layernames)):
		layername = layernames[x]
		layer = hcmgis_find_layer(layername)
		if layer == None:
			return "Layer " + layername + " not found"

		# Verify that all layers are the same type (point, polygon, etc)
		if (len(layers) > 0):
			if (layer.wkbType() != layers[0].wkbType()):
				return "Merged layers must all be same type of geometry (" + \
					hcmgis_wkbtype_to_text(layer.wkbType()) + " != " + \
					hcmgis_wkbtype_to_text(layers[0].wkbType()) + ")"

		layers.append(layer)
		totalfeaturecount += layer.featureCount()

		# Add any fields not in the composite field list
		for sindex, sfield in enumerate(layer.fields()):
			found = None
			for dindex, dfield in enumerate(field_list):
				if (dfield.name().upper() == sfield.name().upper()):
					found = dfield
					if (dfield.type() != sfield.type()):
						# print "Mismatch", dfield.typeName(), sfield.typeName(), layername
						field_list[dindex].setType(QVariant.String)
						field_list[dindex].setTypeName("String")
						field_list[dindex].setLength(254)
						field_list[dindex].setPrecision(0)
					break

					#	return unicode(sfield.name()) + " attribute type " + \
					#		unicode(sfield.typeName()) + " in layer " +\
					#		unicode(layer.name()) + " does not match type " +\
					#		unicode(dfield.typeName()) + " in other layers"

			if not found:
				field_list.append(QgsField(sfield))

	# Convert field list to structure.
	# Have to do this as a list because fields in structure cannot be 
	# modified after appending, and conflicting types need to be converted to string

	fields = QgsFields()
	for field in field_list:
		fields.append(field)
		# print field.name(), field.typeName()
			
	if (len(layers) <= 0):
		return "No layers given to merge"

	# Create the output shapefile
	if len(savename) <= 0:
		return "No output filename given"

	if QFile(savename).exists():
		if not QgsVectorFileWriter.deleteShapeFile(savename):
			return "Failure deleting existing shapefile: " + savename

	outfile = QgsVectorFileWriter(savename, "utf-8", fields, layers[0].wkbType(), layers[0].crs(), "ESRI Shapefile")

	if (outfile.hasError() != QgsVectorFileWriter.NoError):
		return "Failure creating output shapefile: " + unicode(outfile.errorMessage())

	# Copy layer features to output file
	featurecount = 0
	for layer in layers:
		# print "Layer", unicode(featurecount)
		for feature in layer.getFeatures():
			sattributes = feature.attributes()
			dattributes = []
			for dindex, dfield in enumerate(fields):
				# dattribute = QVariant(dfield.type())
				# print str(dindex) + ": " + str(dfield.type())

				if (dfield.type() in [QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong]):
					dattribute = 0

				elif (dfield.type() == QVariant.Double):
					dattribute = 0.0

				else:
					dattribute = ""

				for sindex, sfield in enumerate(layer.fields()):
					if (sfield.name().upper() == dfield.name().upper()):
						if (sfield.type() == dfield.type()):
							dattribute = sattributes[sindex]

						elif (dfield.type() == QVariant.String):
							dattribute = unicode(sattributes[sindex])

						else:
							return "Attribute " + unicode(sfield.name()) + \
								" type mismatch " + sfield.typeName() + \
								" != " + dfield.typeName()
						break

				dattributes.append(dattribute)

			#for dindex, dfield in dattributes.items():
			#	print layer.name() + " (" + str(dindex) + ") " + str(dfield.toString())

			feature.setAttributes(dattributes)
			outfile.addFeature(feature)
			featurecount += 1
			if (featurecount % 50) == 0:
				hcmgis_status_message(qgis, "Writing feature " + \
					unicode(featurecount) + " of " + unicode(totalfeaturecount))

	del outfile

	# Add the merged layer to the project
	if addlayer:
		qgis.addVectorLayer(savename, os.path.basename(savename), "ogr")

	hcmgis_completion_message(qgis, unicode(featurecount) + " records exported")

	return None


def hcmgis_split(qgis, layer,selectedfield, outdir):	
	import processing
	if layer is None:
		return u'No selected layers!'  
	parameters = {'INPUT':layer,
				'FIELD': selectedfield,
				'OUTPUT': outdir
			  }
	processing.run('qgis:splitvectorlayer',parameters)	

def hcmgis_fixgeometries(qgis, input, output):		
	import qgis.utils
	import processing
	if input is None:
		return u'No selected layers!'  
	parameters = {'INPUT':input,
				'OUTPUT': output
			  }
	processing.runAndLoadResults('qgis:fixgeometries',parameters)	

def hcmgis_checkvalidity(qgis, input):			
	import qgis.utils
	import processing
	if input is None:
		return u'No selected layers!'  
	parameters = { 'INPUT_LAYER' : input, 
	'METHOD' : 2, 
	'VALID_OUTPUT' : 'memory:', 
	'INVALID_OUTPUT' : 'memory:', 
	'ERROR_OUTPUT' : 'memory:' }		
	processing.runAndLoadResults('qgis:checkvalidity',parameters)	
	
def hcmgis_reprojection(qgis, input, destcrs, output):		
	import qgis.utils
	import processing
	if input is None:
		return u'No selected layers!'  
	parameters = {'INPUT':input,
				'TARGET_CRS': str(destcrs),
				#'OUTPUT': "memory:"
				'OUTPUT': output
			  }
	processing.runAndLoadResults('qgis:reprojectlayer',parameters)	
		

def hcmgis_merge_field(qgis, layer, selectedfields, char,selectedfeatureonly):			
	if layer is None:
		return u'No selected layers!'  
	if (char == u'Space'):
		char = " "
	elif (char == "Tab"):
		char = "\t"
	if (len(selectedfields) <= 0):
		return u'No selected fields!'
	char = unicode (char)
	# need to create a data provider
	layer.dataProvider().addAttributes([QgsField("merge",  QVariant.String)]) # define/add field data type
	layer.updateFields() # tell the vector layer to fetch changes from the provider
	progressMessageBar = qgis.messageBar()
	progress = QProgressBar()
	#Maximum is set to 100, making it easy to work with percentage of completion
	progress.setMaximum(100) 
	#pass the progress bar to the message Bar
	progressMessageBar.pushWidget(progress)
        
	fieldnumber = 0
	for i in layer.fields():
			fieldnumber += 1      
	featurecount = 0           
        
	layer.startEditing()
	if selectedfeatureonly:
		totalfeaturecount = layer.selectedFeatureCount()
		for feature in  layer.SelectedFeatures():  
			count = 0
			merge_value = ""                
			for j in selectedfields:                                       
				if (feature[layer.dataProvider().fieldNameIndex(j)]):# is not NULL
					if (count == len(selectedfields)-1):# last slected field
						merge_value += unicode(feature[layer.dataProvider().fieldNameIndex(j)]) 
					else:
						merge_value += unicode(feature[layer.dataProvider().fieldNameIndex(j)]) + char
					layer.changeAttributeValue(feature.id(), fieldnumber-1, merge_value)
				count +=1
			featurecount += 1              
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)
	else:
			totalfeaturecount = layer.featureCount()
			for feature in  layer.getFeatures():  
				count = 0
				merge_value = ""                
				for j in selectedfields:                                       
					if (feature[layer.dataProvider().fieldNameIndex(j)]):# is not NULL
						if (count == len(selectedfields)-1):# last slected field
							merge_value += unicode(feature[layer.dataProvider().fieldNameIndex(j)]) 
						else:
							merge_value += unicode(feature[layer.dataProvider().fieldNameIndex(j)]) + char
						layer.changeAttributeValue(feature.id(), fieldnumber-1, merge_value)
					count +=1
				featurecount += 1              
				percent = (featurecount/float(totalfeaturecount)) * 100
				progress.setValue(percent)     
	layer.commitChanges()
	#hcmgis_completion_message(qgis, unicode(featurecount) + " records updated")
	qgis.messageBar().clearWidgets() 	
	return None

def hcmgis_split_field(qgis, layer, selectedfield, char, selectedfeatureonly):            
	if layer is None:
		return u'No selected layer!'
	if ( layer.isEditable == False): return u'Layer is read only!' 

	char = unicode(char)
	if (char == u'Space'):
		char = " "
	elif (char == "Tab"):
		char = "\t"
	if (len(selectedfield) <= 0):
		return u'No selected field!'        	        
	
	top_occurence = hcmgis_top_occurence(layer, selectedfield,char,selectedfeatureonly)    
	
	if (top_occurence == 0):
		return u'Field ' + selectedfield + u' does not contain any split characters!'

			  
	for i in range(0, top_occurence+1):
		layer.dataProvider().addAttributes([QgsField("split",  QVariant.String)]) # define/add field data type
	layer.updateFields()

	featurecount = 0
	fieldnumber = 0
	
	for i in layer.fields():
		fieldnumber += 1
			
	progressMessageBar = qgis.messageBar()
	progress = QProgressBar()
	#Maximum is set to 100, making it easy to work with percentage of completion
	progress.setMaximum(100) 
	#pass the progress bar to the message Bar
	progressMessageBar.pushWidget(progress)        
				  
	layer.startEditing()
	if selectedfeatureonly:
		totalfeaturecount = layer.selectedFeatureCount()
		for feature in  layer.SelectedFeatures():                    
			fieldupdatenumber = unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).count(char)+1
			for i in range (fieldupdatenumber):
				if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL                                                         
					layer.changeAttributeValue(feature.id(), (fieldnumber-1) - top_occurence + i, unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).split(char)[i])                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)
	else:
		totalfeaturecount = layer.featureCount()
		for feature in layer.getFeatures():                   
			fieldupdatenumber = unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).count(char)+1
			for i in range (fieldupdatenumber):
				if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL
					layer.changeAttributeValue(feature.id(), (fieldnumber-1) - top_occurence + i, unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).split(char)[i])                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)              
	layer.commitChanges()        
	#hcmgis_completion_message(qgis, unicode(featurecount) + " records updated")

			
	qgis.messageBar().clearWidgets() 	
	return None

def hcmgis_find_replace(qgis, layer, selectedfield, find, replace, selectedfeatureonly):
	if layer is None:
		return u'No selected layer!'           
   
	if (len(selectedfield) <= 0):
		return u'No selected field!'        	                        
	find = unicode(find)
	replace = unicode(replace)      


	layer.dataProvider().addAttributes([QgsField("find_replace",  QVariant.String)]) # define/add field data type
	layer.updateFields()

	progressMessageBar = qgis.messageBar()
	progress = QProgressBar()
	#Maximum is set to 100, making it easy to work with percentage of completion
	progress.setMaximum(100) 
	#pass the progress bar to the message Bar
	progressMessageBar.pushWidget(progress)
		
	featurecount = 0
	fieldnumber = 0
   
	for i in layer.fields():
                fieldnumber += 1

   
	layer.startEditing()
	if selectedfeatureonly:
		totalfeaturecount = layer.selectedFeatureCount()
		for feature in  layer.SelectedFeatures():
			if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).replace(find ,replace))                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)                   
	else:
		totalfeaturecount = layer.featureCount()
		for feature in layer.getFeatures():
			if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).replace(find ,replace))                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)        
	layer.commitChanges()        
	#hcmgis_completion_message(qgis, unicode(featurecount) + " records updated")
	qgis.messageBar().clearWidgets() 	
	return None

def hcmgis_prefix_suffix(qgis, layer, selectedfield, prefix, charprefix, suffix, charsuffix, selectedfeatureonly):
	from PyQt5.QtWidgets import QProgressBar

	if layer is None:
		return u'No selected layer!'                  
	if (len(selectedfield) <= 0):
		return u'No selected field!'        
	
	if ( layer.isEditable == False): return u'Layer is read only!' 
	
	prefix = unicode(prefix)
	charprefix = unicode(charprefix)
	suffix = unicode(suffix)
	charsuffix = unicode(charsuffix)
	if (charprefix == u'Space'):
		charprefix = " "
	elif (charprefix == "Tab"):
		charprefix = "\t"

	if (charsuffix == u'Space'):
		charsuffix = " "
	elif (charsuffix == "Tab"):
		charsuffix = "\t"
							   
	try:
		layer.dataProvider().addAttributes([QgsField("pre_suf",  QVariant.String)]) # define/add field data type
		layer.updateFields()
	except: return u'Layer is read only!' 
	#layer.commitChanges()        


	progressMessageBar = qgis.messageBar()
	progress = QProgressBar()
	#Maximum is set to 100, making it easy to work with percentage of completion
	progress.setMaximum(100) 
	#pass the progress bar to the message Bar
	progressMessageBar.pushWidget(progress)
	
	featurecount = 0
	fieldnumber = 0
	totalfeaturecount = 0
	
	for i in layer.fields():
		fieldnumber += 1              
		  
	layer.startEditing()
	if selectedfeatureonly:
		totalfeaturecount = layer.selectedFeatureCount()
		for feature in  layer.SelectedFeatures():                        
			if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), (prefix + charprefix + unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)])+ charsuffix + suffix))
			else:                      
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), (prefix + charprefix + charsuffix + suffix))                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)
	else:
		totalfeaturecount = layer.featureCount()
		for feature in  layer.getFeatures():
			if (feature[layer.dataProvider().fieldNameIndex(selectedfield)]):# is not NULL
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), (prefix + charprefix + unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)])+ charsuffix + suffix))
			else:                      
				layer.changeAttributeValue(feature.id(), (fieldnumber-1), (prefix + charprefix + charsuffix + suffix))                                        
			featurecount += 1
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)
	layer.commitChanges()        
	#hcmgis_completion_message(qgis, unicode(featurecount) + " records updated")
	qgis.messageBar().clearWidgets() 	
	return None

##################################
#Font Converter
##################################
	
def hcmgis_convertfont(qgis,input_layer, selectedfields, output_layer, sE, dE, caseI,selectedfeatureonly):      
	if input_layer is None:
		return u'No selected layer!'
	if selectedfields is None:
		return u'No selected fields!'
	if output_layer is None:
		return u'Không xác định được đường dẫn lưu kết quả'
	
	#shapeWriter = VectorWriter(output_layer, "UTF-8", input_layer.dataProvider().fields(),input_layer.dataProvider().geometryType(), input_layer.crs())               
	shapeWriter = QgsVectorFileWriter(output_layer, "UTF-8", input_layer.dataProvider().fields(),input_layer.wkbType(), input_layer.crs(),"ESRI Shapefile")   
	
	progressMessageBar = qgis.messageBar()
	progress = QProgressBar()
	#Maximum is set to 100, making it easy to work with percentage of completion
	progress.setMaximum(100) 
	#pass the progress bar to the message Bar
	progressMessageBar.pushWidget(progress)
   
	featurecount = 0               
   
	if selectedfeatureonly:
		totalfeaturecount = input_layer.selectedFeatureCount()
		for feat in  input_layer.SelectedFeatures():
			for tf in selectedfields:
				oldValue = feat[tf]
				if oldValue != None:
					if sE == _VNIWin:
						# Convert VNI-Win to Unicode
						newValue = ConvertVNIWindows(oldValue)
						# if targerEncode is not Unicode -> Convert to other options
						if dE != _Unicode:
							newValue = Convert(newValue,_Unicode,dE)
					else:
						newValue = Convert(oldValue,sE,dE)
					# Character Case-setting                                
					if caseI !=  "none":
						newValue = ChangeCase(newValue, caseI)
							   
					# update new value
					feat[tf] = newValue						
				else: pass									                        
			shapeWriter.addFeature(feat)
			featurecount += 1		                                              
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)                              
			if (((featurecount % 50) == 0) or (featurecount == totalfeaturecount)):
				hcmgis_status_message(qgis, "Writing feature " + unicode(featurecount) + " of " + unicode(totalfeaturecount))
		del shapeWriter
		layer = QgsVectorLayer(output_layer, QFileInfo(output_layer).baseName(), 'ogr')
		layer.setProviderEncoding(u'System')
		layer.dataProvider().setEncoding(u'UTF-8')
		if layer.isValid():
			QgsProject.instance().addMapLayer(layer)   
		#hcmgis_completion_message(qgis, unicode(featurecount) + " records font converted")
		qgis.messageBar().clearWidgets()
	else:
		totalfeaturecount = input_layer.featureCount()
		for feat in  input_layer.getFeatures():
			for tf in selectedfields:
				oldValue = feat[tf]
				if oldValue != None:
					if sE == _VNIWin:
						# Convert VNI-Win to Unicode
						newValue = ConvertVNIWindows(oldValue)
						# if targerEncode is not Unicode -> Convert to other options
						if dE !=  _Unicode:
							newValue = Convert(newValue,_Unicode,dE)
					else:
						newValue = Convert(oldValue,sE,dE)
					# Character Case-setting                                
					if caseI !=  "none":
						newValue = ChangeCase(newValue, caseI)
						   
					# update new value
					feat[tf] = newValue						
				else: pass									                        
			shapeWriter.addFeature(feat)
			featurecount += 1		                                              
			percent = (featurecount/float(totalfeaturecount)) * 100
			progress.setValue(percent)                              
			if (((featurecount % 50) == 0) or (featurecount == totalfeaturecount)):
				hcmgis_status_message(qgis, "Writing feature " + unicode(featurecount) + " of " + unicode(totalfeaturecount))
		del shapeWriter
		layer = QgsVectorLayer(output_layer, QFileInfo(output_layer).baseName(), 'ogr')
		layer.setProviderEncoding(u'System')
		layer.dataProvider().setEncoding(u'UTF-8')
		if layer.isValid():
			QgsProject.instance().addMapLayer(layer)   
		#hcmgis_completion_message(qgis, unicode(featurecount) + " records font converted")
		qgis.messageBar().clearWidgets() 
	return None
                
def Convert(txt,s,d):    
	result = u''
	for c in txt:
		if c in s:
			idx = s.index(c)
			if idx >= 0:
				c = d[idx]
		result += c
	return result

def ConvertVNIWindows(txt):
	_VniWindows2= [
			u'aâ',u'AÂ',u'aê',u'AÊ',u'eâ',u'EÂ',u'ô',u'Ô',u'aù',u'AÙ',u'aø',u'AØ',u'aû',u'AÛ',u'aõ',u'AÕ',u'aï',u'AÏ',
			u'aá',u'AÁ',u'aà',u'AÀ',u'aå',u'AÅ',u'aã',u'AÃ',u'aä',u'AÄ',u'aé',u'AÉ',u'aè',u'AÈ',u'aú',u'AÚ',u'aü',u'AÜ',u'aë',u'AË',
			u'eù',u'EÙ',u'eø',u'EØ',u'eû',u'EÛ',u'eõ',u'EÕ',u'eï',u'EÏ',u'eá',u'EÁ',u'eà',u'EÀ',u'eå',u'EÅ',u'eã',u'EÃ',u'eä',u'EÄ',u'ó',u'Ó',u'ò',u'Ò',    
			u'oû',u'OÛ',u'oõ',u'OÕ',u'oï',u'OÏ',u'oá',u'OÁ',u'oà',u'OÀ',u'oå',u'OÅ',u'oã',u'OÃ',u'oä',u'OÄ',u'ôù',u'ÔÙ',u'ôø',u'ÔØ',u'ôû',u'ÔÛ',u'ôõ',u'ÔÕ',u'ôï',u'ÔÏ',    
			u'uù',u'UÙ',u'uø',u'UØ',u'uû',u'UÛ',u'uõ',u'UÕ',u'uï',u'UÏ',u'öù',u'ÖÙ',u'öø',u'ÖØ',u'öû',u'ÖÛ',u'öõ',u'ÖÕ',u'öï',u'ÖÏ',u'yø',u'YØ',u'yû',u'YÛ',u'yõ',u'YÕ',u'yù',u'YÙ',
			u'où',u'OÙ',u'oø',u'OØ',u'oâ',u'OÂ'
	]
	_VniWindows1= [    
			u'ñ',u'Ñ',u'í',u'Í',u'ì',u'Ì',u'æ',u'Æ',u'ö',u'Ö',u'î',u'Î'    
	]
	_Unicode2= [
			u'â',u'Â',u'ă',u'Ă',u'ê',u'Ê',u'ơ',u'Ơ',u'á',u'Á',u'à',u'À',u'ả',u'Ả',u'ã',u'Ã',u'ạ',u'Ạ',
			u'ấ',u'Ấ',u'ầ',u'Ầ',u'ẩ',u'Ẩ',u'ẫ',u'Ẫ',u'ậ',u'Ậ',u'ắ',u'Ắ',u'ằ',u'Ằ',u'ẳ',u'Ẳ',u'ẵ',u'Ẵ',u'ặ',u'Ặ',
			u'é',u'É',u'è',u'È',u'ẻ',u'Ẻ',u'ẽ',u'Ẽ',u'ẹ',u'Ẹ',u'ế',u'Ế',u'ề',u'Ề',u'ể',u'Ể',u'ễ',u'Ễ',u'ệ',u'Ệ',u'ĩ',u'Ĩ',u'ị',u'Ị',    
			u'ỏ',u'Ỏ',u'õ',u'Õ',u'ọ',u'Ọ',u'ố',u'Ố',u'ồ',u'Ồ',u'ổ',u'Ổ',u'ỗ',u'Ỗ',u'ộ',u'Ộ',u'ớ',u'Ớ',u'ờ',u'Ờ',u'ở',u'Ở',u'ỡ',u'Ỡ',u'ợ',u'Ợ',    
			u'ú',u'Ú',u'ù',u'Ù',u'ủ',u'Ủ',u'ũ',u'Ũ',u'ụ',u'Ụ',u'ứ',u'Ứ',u'ừ',u'Ừ',u'ử',u'Ử',u'ữ',u'Ữ',u'ự',u'Ự',u'ỳ',u'Ỳ',u'ỷ',u'Ỷ',u'ỹ',u'Ỹ',u'ý',u'Ý',
			u'ó#',u'Ó#',u'ò#',u'Ò#',u'ô#',u'Ô#'
			]
	_Unicode1= [   
			u'đ',u'Đ',u'í',u'Í',u'ì',u'Ì',u'ỉ',u'Ỉ',u'ư',u'Ư',u'ỵ',u'Ỵ'      
	]           

	for j in range (0,len(txt)-1):
		c = txt[j:j+2]     
		if c in _VniWindows2:      
			idx = _VniWindows2.index(c)
			if idx >= 0:
				c = _Unicode2[idx]                
			txt = txt.replace(txt[j:j+2],c)

	for j in range (0,len(txt)):
		c = txt[j:j+1]
		if c in _VniWindows1:      
			idx = _VniWindows1.index(c)
			if idx >= 0:
				c = _Unicode1[idx]                
			txt = txt.replace(txt[j:j+1],c)	
				

	for i in range (0,len(txt)):       
		c = txt[i:i+1]  
		if c == u'ó'and txt[i+1:i+2] != u'#':
			c= u'ĩ'
			txt = txt[:i] + c + txt[i+1:]
		elif c== u'Ó'and txt[i+1:i+2] != u'#':
			c= u'Ĩ'
			txt = txt[:i] + c + txt[i+1:]
		elif c== u'ò'and txt[i+1:i+2] != u'#':
			c= u'ị'
			txt = txt[:i] + c + txt[i+1:]
		elif c== u'Ò'and txt[i+1:i+2] != u'#':
			c= u'Ị'
			txt = txt[:i] + c + txt[i+1:]
		elif c== u'ô'and txt[i+1:i+2] != u'#':
			c= u'ơ'
			txt = txt[:i] + c + txt[i+1:]
		elif c== u'Ô'and txt[i+1:i+2] != u'#':
			c= u'Ơ'
			txt = txt[:i] + c + txt[i+1:]

	txt = txt.replace(u'ó#',u'ó')
	txt = txt.replace(u'Ó#',u'Ó')
	txt = txt.replace(u'ò#',u'ò')
	txt = txt.replace(u'Ò#',u'Ò')
	txt = txt.replace(u'ô#',u'ô')
	txt = txt.replace(u'Ô#',u'Ô')
	return txt

def GetEncodeIndex(encodeTxt):
	return{
		"Unicode" : _Unicode,
		"TCVN3" : _TCVN3,
		"VNI-Windows": _VNIWin,
		"ANSI (Khong dau)" : _KhongDau,
	}.get(encodeTxt,_Unicode)

def GetCaseIndex(cText):
	return{
		u'UPPER CASE (IN HOA)' : "upper",
		u'lower case (in thường)' : "lower",
		u'Capitalize (Hoa đầu câu)' : "capitalize",
		u'Title (Hoa Mỗi từ)' : "title",
	}.get(cText, "none")
        
def ChangeCase(str, caseIndex):
	result = u''
	# Character Case-setting
	if caseIndex == "upper":
		result = str.upper()
	elif caseIndex == "lower":
		result = str.lower()
	elif caseIndex == "capitalize":
		result = str.capitalize()
	elif caseIndex == "title":
		result = str.title()
	return result

def hcmgis_top_occurence(layer, selectedfield, char, selectedfeatureonly):	
	max = 0
	if selectedfeatureonly:
		for feature in layer.SelectedFeatures():
			fieldvalue = unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).strip()
			occurence = fieldvalue.count(char)
			if (occurence > max):
				max = occurence
	else:
		for feature in layer.getFeatures():
			fieldvalue = unicode(feature[layer.dataProvider().fieldNameIndex(selectedfield)]).strip()
			occurence = fieldvalue.count(char)
			if (occurence > max):
				max = occurence
	return max

	
def hcmgis_wkbtype_to_text(wkbtype):
	text = QgsWkbTypes.displayString(wkbtype)
	if text:
		return text
	else:
		return "Unknown WKB " + unicode(wkbtype)

def hcmgis_find_layer(layer_name):

	if not layer_name:
		return None

	layers = QgsProject.instance().mapLayersByName(layer_name)
	if (len(layers) >= 1):
		return layers[0]


def hcmgis_status_message(qgis, message):
	qgis.statusBarIface().showMessage(message)



def hcmgis_completion_message(qgis, message):
	hcmgis_status_message(qgis, message)
