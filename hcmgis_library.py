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

import argparse
import json
import logging
import numbers
import sys

####################### arcgis2geojson

def pointsEqual(a, b):
    """
    checks if 2 [x, y] points are equal
    """
    for i in range(0, len(a)):
        if a[i] != b[i]:
            return False
    return True


def closeRing(coordinates):
    """
    checks if the first and last points of a ring are equal and closes the ring
    """
    if not pointsEqual(coordinates[0], coordinates[len(coordinates) - 1]):
        coordinates.append(coordinates[0])
    return coordinates


def ringIsClockwise(ringToTest):
    """
    determine if polygon ring coordinates are clockwise. clockwise signifies
    outer ring, counter-clockwise an inner ring or hole.
    """

    total = 0
    i = 0
    rLength = len(ringToTest)
    pt1 = ringToTest[i]
    pt2 = None
    for i in range(0, rLength - 1):
        pt2 = ringToTest[i + 1]
        total += (pt2[0] - pt1[0]) * (pt2[1] + pt1[1])
        pt1 = pt2

    return (total >= 0)


def vertexIntersectsVertex(a1, a2, b1, b2):
    uaT = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])
    ubT = (a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])
    uB = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])

    if uB != 0:
        ua = uaT / uB
        ub = ubT / uB

        if ua >= 0 and ua <= 1 and ub >= 0 and ub <= 1:
            return True

    return False


def arrayIntersectsArray(a, b):
    for i in range(0, len(a)-1):
        for j in range(0, len(b)-1):
            if vertexIntersectsVertex(a[i], a[i + 1], b[j], b[j + 1]):
                return True

    return False


def coordinatesContainPoint(coordinates, point):

    contains = False
    l = len(coordinates)
    i = -1
    j = l - 1
    while ((i + 1) < l):
        i = i + 1
        ci = coordinates[i]
        cj = coordinates[j]
        if ((ci[1] <= point[1] and point[1] < cj[1]) or (cj[1] <= point[1] and point[1] < ci[1])) and\
           (point[0] < (cj[0] - ci[0]) * (point[1] - ci[1]) / (cj[1] - ci[1]) + ci[0]):
            contains = not contains
        j = i
    return contains


def coordinatesContainCoordinates(outer, inner):
    intersects = arrayIntersectsArray(outer, inner)
    contains = coordinatesContainPoint(outer, inner[0])
    if not intersects and contains:
        return True
    return False


def convertRingsToGeoJSON(rings):
    """
    do any polygons in this array contain any other polygons in this array?
    used for checking for holes in arcgis rings
    """

    outerRings = []
    holes = []
    x = None  # iterator
    outerRing = None  # current outer ring being evaluated
    hole = None  # current hole being evaluated

    # for each ring
    for r in range(0, len(rings)):
        ring = closeRing(rings[r])
        if len(ring) < 4:
            continue

        # is this ring an outer ring? is it clockwise?
        if ringIsClockwise(ring):
            polygon = [ring[::-1]]
            outerRings.append(polygon)  # wind outer rings counterclockwise for RFC 7946 compliance
        else:
            holes.append(ring[::-1])  # wind inner rings clockwise for RFC 7946 compliance

    uncontainedHoles = []

    # while there are holes left...
    while len(holes):
        # pop a hole off out stack
        hole = holes.pop()

        # loop over all outer rings and see if they contain our hole.
        contained = False
        x = len(outerRings) - 1
        while (x >= 0):
            outerRing = outerRings[x][0]
            if coordinatesContainCoordinates(outerRing, hole):
                # the hole is contained push it into our polygon
                outerRings[x].append(hole)
                contained = True
                break
            x = x-1

        # ring is not contained in any outer ring
        # sometimes this happens https://github.com/Esri/esri-leaflet/issues/320
        if not contained:
            uncontainedHoles.append(hole)

    # if we couldn't match any holes using contains we can try intersects...
    while len(uncontainedHoles):
        # pop a hole off out stack
        hole = uncontainedHoles.pop()

        # loop over all outer rings and see if any intersect our hole.
        intersects = False
        x = len(outerRings) - 1
        while (x >= 0):
            outerRing = outerRings[x][0]
            if arrayIntersectsArray(outerRing, hole):
                # the hole is contained push it into our polygon
                outerRings[x].append(hole)
                intersects = True
                break
            x = x-1

        if not intersects:
            outerRings.append([hole[::-1]])

    if len(outerRings) == 1:
        return {
            'type': 'Polygon',
            'coordinates': outerRings[0]
        }
    else:
        return {
            'type': 'MultiPolygon',
            'coordinates': outerRings
        }


def getId(attributes, idAttribute=None):
    keys = [idAttribute, 'OBJECTID', 'FID'] if idAttribute else ['OBJECTID', 'FID']
    for key in keys:
        if key in attributes and (
                isinstance(attributes[key], numbers.Number) or
                isinstance(attributes[key], str)):
            return attributes[key]
    raise KeyError('No valid id attribute found')


def arcgis2geojson(arcgis, idAttribute=None):
    if isinstance(arcgis, str):
        return json.dumps(convert(json.loads(arcgis), idAttribute))
    else:
        return convert(arcgis, idAttribute)


def convert(arcgis, idAttribute=None):
    """
    Convert an ArcGIS JSON object to a GeoJSON object
    """

    geojson = {}

    if 'features' in arcgis and arcgis['features']:
        geojson['type'] = 'FeatureCollection'
        geojson['features'] = []
        for feature in arcgis['features']:
            geojson['features'].append(convert(feature, idAttribute))

    if 'x' in arcgis and isinstance(arcgis['x'], numbers.Number) and\
            'y' in arcgis and isinstance(arcgis['y'], numbers.Number):
        geojson['type'] = 'Point'
        geojson['coordinates'] = [arcgis['x'], arcgis['y']]
        if 'z' in arcgis and isinstance(arcgis['z'], numbers.Number):
            geojson['coordinates'].append(arcgis['z'])

    if 'points' in arcgis:
        geojson['type'] = 'MultiPoint'
        geojson['coordinates'] = arcgis['points']

    if 'paths' in arcgis:
        if len(arcgis['paths']) == 1:
            geojson['type'] = 'LineString'
            geojson['coordinates'] = arcgis['paths'][0]
        else:
            geojson['type'] = 'MultiLineString'
            geojson['coordinates'] = arcgis['paths']

    if 'rings' in arcgis:
        geojson = convertRingsToGeoJSON(arcgis['rings'])

    if 'xmin' in arcgis and isinstance(arcgis['xmin'], numbers.Number) and\
            'ymin' in arcgis and isinstance(arcgis['ymin'], numbers.Number) and\
            'xmax' in arcgis and isinstance(arcgis['xmax'], numbers.Number) and\
            'ymax' in arcgis and isinstance(arcgis['ymax'], numbers.Number):
        geojson['type'] = 'Polygon'
        geojson['coordinates'] = [[
            [arcgis['xmax'], arcgis['ymax']],
            [arcgis['xmin'], arcgis['ymax']],
            [arcgis['xmin'], arcgis['ymin']],
            [arcgis['xmax'], arcgis['ymin']],
            [arcgis['xmax'], arcgis['ymax']]
        ]]

    if 'geometry' in arcgis or 'attributes' in arcgis:
        geojson['type'] = 'Feature'
        if 'geometry' in arcgis:
            geojson['geometry'] = convert(arcgis['geometry'])
        else:
            geojson['geometry'] = None

        if 'attributes' in arcgis:
            geojson['properties'] = arcgis['attributes']
            try:
                geojson['id'] = getId(arcgis['attributes'], idAttribute)
            except KeyError:
                # don't set an id
                pass
        else:
            geojson['properties'] = None

    if 'geometry' in geojson and not(geojson['geometry']):
        geojson['geometry'] = None

    if 'spatialReference' in arcgis and\
            'wkid' in arcgis['spatialReference'] and\
            arcgis['spatialReference']['wkid'] != 4326:
        logging.warning(
            'Object converted in non-standard crs - ' +\
            str(arcgis['spatialReference'])
        )

    return geojson


def main():
    parser = argparse.ArgumentParser(description='Convert ArcGIS JSON to GeoJSON')
    parser.add_argument(
        'file',
        nargs='?',
        help='Input file, if empty stdin is used',
        type=argparse.FileType('r'),
        default=sys.stdin
    )
    parser.add_argument(
        '--id',
        action='store',
        help='Attribute to use as feature ID',
        required=False,
        default=None
    )
    args = parser.parse_args()

    sys.stdout.write(arcgis2geojson(args.file.read(), idAttribute=args.id))
    return 0


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
	if not tms_layer.isValid():
  		print("Layer failed to load!")
	sources = []
	service_uri1 = "http://"+service_url
	sources.append(["connections-xyz",name,"","","",service_uri1,"","22","0"])
	for source in sources:
		connectionType = source[0]
		connectionName = source[1]
		QSettings().setValue("qgis/%s/%s/authcfg" % (connectionType, connectionName), source[2])
		QSettings().setValue("qgis/%s/%s/password" % (connectionType, connectionName), source[3])
		QSettings().setValue("qgis/%s/%s/referer" % (connectionType, connectionName), source[4])
		QSettings().setValue("qgis/%s/%s/url" % (connectionType, connectionName), source[5])
		QSettings().setValue("qgis/%s/%s/username" % (connectionType, connectionName), source[6])
		QSettings().setValue("qgis/%s/%s/zmax" % (connectionType, connectionName), source[7])
		QSettings().setValue("qgis/%s/%s/zmin" % (connectionType, connectionName), source[8])
	# Update GUI
	qgis.utils.iface.reloadConnections()


def hcmgis_vietbando(self, service_url, name):
	import qgis.utils
	sources = []
	service_url = "http://"+service_url
	sources.append(["connections-xyz",name,"","","",service_url,"","22","0"])
	for source in sources:
		connectionType = source[0]
		connectionName = source[1]
		QSettings().setValue("qgis/%s/%s/authcfg" % (connectionType, connectionName), source[2])
		QSettings().setValue("qgis/%s/%s/password" % (connectionType, connectionName), source[3])
		QSettings().setValue("qgis/%s/%s/referer" % (connectionType, connectionName), source[4])
		QSettings().setValue("qgis/%s/%s/url" % (connectionType, connectionName), source[5])
		QSettings().setValue("qgis/%s/%s/username" % (connectionType, connectionName), source[6])
		QSettings().setValue("qgis/%s/%s/zmax" % (connectionType, connectionName), source[7])
		QSettings().setValue("qgis/%s/%s/zmin" % (connectionType, connectionName), source[8])
	# Update GUI
	qgis.utils.iface.reloadConnections()	
					
#--------------------------------------------------------
#    hcmgis_medialaxis - Create skeleton/ medial axis/ centerline of roads, rivers and similar linear structures
# --------------------------------------------------------

#for alg in QgsApplication.processingRegistry().algorithms(): print(alg.id())

def hcmgis_medialaxis(qgis, layer, selectedfield, density):		
	import processing
	## create skeleton/ media axis
	parameters1 = {'INPUT':layer,
					'OUTPUT':  "memory:polygon"}
	polygon = processing.run('qgis:saveselectedfeatures',parameters1)
	
	#densify by interval
	parameters2 = {'INPUT': polygon['OUTPUT'],
					'INTERVAL' : 1,
					'OUTPUT' : "memory:polygon_densify"} 
	polygon_densify = processing.run('qgis:densifygeometriesgivenaninterval', parameters2)
	
	# extract vertices
	parameters3 = {'INPUT': polygon_densify['OUTPUT'],					
					'OUTPUT' : "memory:points"} 
	points = processing.run('qgis:extractvertices', parameters3)	
	
	parameters4 = {'INPUT': points['OUTPUT'],
					 'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'} 
	voronoipolygon = processing.run('qgis:voronoipolygons', parameters4)	
	
	parameters5 = {'INPUT': voronoipolygon['OUTPUT'],
					'OUTPUT' : 'memory:voronoipolyline'} 
	voronoipolyline = processing.run('qgis:polygonstolines',parameters5)
	
	
	parameters6 = {'INPUT': voronoipolyline['OUTPUT'],					
					'OUTPUT' : 'memory:explode'}
	explode = processing.run('qgis:explodelines',parameters6)
	#processing.runAndLoadResults('qgis:explodelines',parameters6)
	
	parameters7 = {'INPUT': explode['OUTPUT'],
					'PREDICATE' : [6], # within					
					'INTERSECT': polygon['OUTPUT'],		
					'METHOD' : 0,
					'OUTPUT' : 'memory:candidate'}
	candidate= processing.run('qgis:selectbylocation',parameters7)
	
	
	parameters8 = {'INPUT':candidate['OUTPUT'],
					'OUTPUT':  'memory:medialaxis'}
	medialaxis = processing.run('qgis:saveselectedfeatures',parameters8)
	#processing.runAndLoadResults('qgis:saveselectedfeatures',parameters8)
	
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
	parameters1 = {'INPUT':layer,
					'OUTPUT':  "memory:polygon"}
	polygon = processing.run('qgis:saveselectedfeatures',parameters1)

	parameters1_1 = {'INPUT':polygon['OUTPUT'],
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
	
	#densify by interval
	parameters2 = {'INPUT': polygon['OUTPUT'],
					'INTERVAL' : 1,
					'OUTPUT' : "memory:polygon_densify"} 
	polygon_densify = processing.run('qgis:densifygeometriesgivenaninterval', parameters2)
	
	# extract vertices
	parameters3 = {'INPUT': polygon_densify['OUTPUT'],					
					'OUTPUT' : "memory:points"} 
	points = processing.run('qgis:extractvertices', parameters3)	

		
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
	if (not layer.wkbType()== QgsWkbTypes.Point):
		return 'Multipoint layer is not supported. Please convert to Point layer!'

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
					'COLUMN' : ['MEAN','STDDEV','MAX'],
	 				'OUTPUT':  'memory:closest'
					 }
	processing.runAndLoadResults('qgis:deletecolumn',parameters3_5)
	layer.removeSelection()	


	#Finding farthest pair of points
	parameters4 = {'INPUT': delaunay_polygon['OUTPUT'],								
					'OUTPUT' : 'memory:convexhull'}
	convexhull = processing.run('qgis:dissolve',parameters4)

	parameters5 = {'INPUT': layer,
					'PREDICATE' : [4],
					'INTERSECT' : convexhull['OUTPUT'],
					'METHOD' : 0,	# touch								
					'OUTPUT' : 'memory:convexhull_vertices'
					}
	processing.run('qgis:selectbylocation',parameters5)

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
	
	farthest_candidates = distance_matrix['OUTPUT']

	values = []
	idx = farthest_candidates.dataProvider().fieldNameIndex('MAX')

	for feat in farthest_candidates.getFeatures():
		attrs = feat.attributes()
		values.append(attrs[idx])

	max_value = str(round(max(values),1))
	selection2 = farthest_candidates.getFeatures(QgsFeatureRequest(QgsExpression('round("MAX",1)' + '=' + max_value)))
	ids = [s.id() for s in selection2]
	farthest_candidates.selectByIds(ids)

	parameters8 = {'INPUT':farthest_candidates,
	 				'OUTPUT':  'memory:farthest_points'
					 }
	farthest_points = processing.run('qgis:saveselectedfeatures',parameters8)

	
	parameters9 = {'INPUT': farthest_points['OUTPUT'],
					'COLUMN' : ['MEAN','STDDEV','MIN'],
	 				'OUTPUT':  'memory:farthest'
					 }
	processing.runAndLoadResults('qgis:deletecolumn',parameters9)


	layer.removeSelection()	
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

# --------------------------------------------------------
#    hcmgis_voronoi - Voronoi diagram creation
#    reference: mmqgis
# --------------------------------------------------------

def hcmgis_voronoi_diagram(qgis, sourcelayer, savename, addlayer):
	layer = hcmgis_find_layer(sourcelayer)
	if layer == None:
		return "Layer " + sourcename + " not found"
	
	if len(savename) <= 0:
		return "No output filename given"

	if QFile(savename).exists():
		if not QgsVectorFileWriter.deleteShapeFile(savename):
			return "Failure deleting existing shapefile: " + savename

	outfile = QgsVectorFileWriter(savename, "utf-8", layer.fields(), 
			QgsWkbTypes.Polygon, layer.crs(), "ESRI Shapefile")

	if (outfile.hasError() != QgsVectorFileWriter.NoError):
		return "Failure creating output shapefile: " + unicode(outfile.errorMessage())

	points = []
	xmin = 0
	xmax = 0
	ymin = 0
	ymax = 0

	for feature in layer.getFeatures():
		# Re-read by feature ID because nextFeature() doesn't always seem to read attributes
		# layer.featureAtId(feature.id(), feature)
		geometry = feature.geometry()
		hcmgis_status_message(qgis, "Reading feature " + unicode(feature.id()))
		# print str(feature.id()) + ": " + str(geometry.wkbType())
		if geometry.wkbType() == QgsWkbTypes.Point:
			points.append( (geometry.asPoint().x(), geometry.asPoint().y(), feature.attributes()) )
			if (len(points) <= 1) or (xmin > geometry.asPoint().x()):
				xmin = geometry.asPoint().x()
			if (len(points) <= 1) or (xmax < geometry.asPoint().x()):
				xmax = geometry.asPoint().x()
			if (len(points) <= 1) or (ymin > geometry.asPoint().y()):
				ymin = geometry.asPoint().y()
			if (len(points) <= 1) or (ymax < geometry.asPoint().y()):
				ymax = geometry.asPoint().y()

	if (len(points) < 3):
		return "Too few points to create diagram"

	for point_number, center in enumerate(points):
	# for center in [ points[17] ]:
		# print "\nCenter, " + str(center[0]) + ", " + str(center[1])
		if (point_number % 20) == 0:
			#hcmgis_status_message(qgis, "Processing point " + \
			#	unicode(center[0]) + ", " + unicode(center[1]))
			hcmgis_status_message(qgis, "Processing point " + unicode(point_number) + " of " + unicode(len(points)))

		# Borders are tangents to midpoints between all neighbors
		tangents = []
		for neighbor in points:
			border = hcmgis_voronoi_line((center[0] + neighbor[0]) / 2.0, (center[1] + neighbor[1]) / 2.0)
			if ((neighbor[0] != center[0]) or (neighbor[1] != center[1])):
				tangents.append(border)

		# Add edge intersections to clip to extent of points
		offset = (xmax - xmin) * 0.01
		tangents.append(hcmgis_voronoi_line(xmax + offset, center[1]))
		tangents.append(hcmgis_voronoi_line(center[0], ymax + offset))
		tangents.append(hcmgis_voronoi_line(xmin - offset, center[1]))
		tangents.append(hcmgis_voronoi_line(center[0], ymin - offset))
		#print "Extent x = " + str(xmax) + " -> " + str(xmin) + ", y = " + str(ymax) + " -> " + str(ymin)

		# Find vector distance and angle to border from center point
		for scan in range(0, len(tangents)):
			run = tangents[scan].x - center[0]
			rise = tangents[scan].y - center[1]
			tangents[scan].distance = sqrt((run * run) + (rise * rise))
			if (tangents[scan].distance <= 0):
				tangents[scan].angle = 0
			elif (tangents[scan].y >= center[1]):
				tangents[scan].angle = acos(run / tangents[scan].distance)
			elif (tangents[scan].y < center[1]):
				tangents[scan].angle = (2 * pi) - acos(run / tangents[scan].distance)
			elif (tangents[scan].x > center[0]):
				tangents[scan].angle = pi / 2.0
			else:
				tangents[scan].angle = 3 * pi / 4

			#print "  Tangent, " + str(tangents[scan].x) + ", " + str(tangents[scan].y) + \
			#	", angle " + str(tangents[scan].angle * 180 / pi) + ", distance " + \
			#	str(tangents[scan].distance)


		# Find the closest line - guaranteed to be a border
		closest = -1
		for scan in range(0, len(tangents)):
			if ((closest == -1) or (tangents[scan].distance < tangents[closest].distance)):
				closest = scan

		# Use closest as the first border
		border = hcmgis_voronoi_line(tangents[closest].x, tangents[closest].y)
		border.angle = tangents[closest].angle
		border.distance = tangents[closest].distance
		borders = [ border ]

		#print "  Border 0) " + str(closest) + " of " + str(len(tangents)) + ", " \
		#	+ str(border.x) + ", " + str(border.y) \
		#	+ ", (angle " + str(border.angle * 180 / pi) + ", distance " \
		#	+ str(border.distance) + ")"

		# Work around the tangents in a CCW circle
		circling = 1
		while circling:
			next = -1
			scan = 0
			while (scan < len(tangents)):
				anglebetween = tangents[scan].angle - borders[len(borders) - 1].angle
				if (anglebetween < 0):
					anglebetween += (2 * pi)
				elif (anglebetween > (2 * pi)):
					anglebetween -= (2 * pi)

				#print "    Scanning " + str(scan) + " of " + str(len(borders)) + \
				#	", " + str(tangents[scan].x) + ", " + str(tangents[scan].y) + \
				#	", angle " + str(tangents[scan].angle * 180 / pi) + \
				#	", anglebetween " + str(anglebetween * 180 / pi)

				# If border intersects to the left
				if (anglebetween < pi) and (anglebetween > 0):
					# A typo here with a reversed slash cost 8/13/2009 debugging
					tangents[scan].iangle = atan2( (tangents[scan].distance / 
						borders[len(borders) - 1].distance) \
						- cos(anglebetween), sin(anglebetween))
					tangents[scan].idistance = borders[len(borders) - 1].distance \
						/ cos(tangents[scan].iangle)

					tangents[scan].iangle += borders[len(borders) - 1].angle

					# If the rightmost intersection so far, it's a candidate for next border
					if (next < 0) or (tangents[scan].iangle < tangents[next].iangle):
						# print "      Take idistance " + str(tangents[scan].idistance)
						next = scan

				scan += 1

			# iangle/distance are for intersection of border with next border
			borders[len(borders) - 1].iangle = tangents[next].iangle
			borders[len(borders) - 1].idistance = tangents[next].idistance

			# Stop circling if back to the beginning
			if (borders[0].x == tangents[next].x) and (borders[0].y == tangents[next].y):
				circling = 0

			else:
				# Add the next border
				border = hcmgis_voronoi_line(tangents[next].x, tangents[next].y)
				border.angle = tangents[next].angle
				border.distance = tangents[next].distance
				border.iangle = tangents[next].iangle
				border.idistance = tangents[next].idistance
				borders.append(border)
				#print "  Border " + str(len(borders) - 1) + \
				#	") " + str(next) + ", " + str(border.x) + \
				#	", " + str(border.y) + ", angle " + str(border.angle * 180 / pi) +\
				#	", iangle " + str(border.iangle * 180 / pi) +\
				#	", idistance " + str(border.idistance) + "\n"

			# Remove the border from the list so not repeated
			tangents.pop(next)
			if (len(tangents) <= 0):
				circling = 0

		polygon = []
		if len(borders) >= 3:
			for border in borders:
				ix = center[0] + (border.idistance * cos(border.iangle))
				iy = center[1] + (border.idistance * sin(border.iangle))
				#print "  Node, " + str(ix) + ", " + str(iy) + \
				#	", angle " + str(border.angle * 180 / pi) + \
				#	", iangle " + str(border.iangle * 180 / pi) + \
				#	", idistance " + str(border.idistance) + ", from " \
				#	+ str(border.x) + ", " + str(border.y)
				polygon.append(QgsPointXY(ix, iy))

			#print "Polygon " + unicode(point_number)
			#for x in range(0, len(polygon)):
			#	print "  Point " + unicode(polygon[x].x()) + ", " + unicode(polygon[x].y())

			# Remove duplicate nodes
			# Compare as strings (unicode) to avoid odd precision discrepancies
			# that sometimes cause duplicate points to be unrecognized
			dup = 0
			while (dup < (len(polygon) - 1)):
				if (unicode(polygon[dup].x()) == unicode(polygon[dup + 1].x())) and \
				   (unicode(polygon[dup].y()) == unicode(polygon[dup + 1].y())):
					polygon.pop(dup)
					# print "  Removed duplicate node " + unicode(dup) + \
					#	" in polygon " + unicode(point_number)
				else:
					# print "  " + unicode(polygon[dup].x()) + ", " + \
					#	unicode(polygon[dup].y()) + " != " + \
					#	unicode(polygon[dup + 1].x()) + ", " + \
					#	unicode(polygon[dup + 1].y())
					dup = dup + 1

			# attributes = { 0:QVariant(center[0]), 1:QVariant(center[1]) }

		if len(polygon) >= 3:
			geometry = QgsGeometry.fromPolygonXY([ polygon ])
			feature = QgsFeature()
			feature.setGeometry(geometry)
			feature.setAttributes(center[2])
			outfile.addFeature(feature)
				
	del outfile

	if addlayer:
		qgis.addVectorLayer(savename, os.path.basename(savename), "ogr")

	hcmgis_completion_message(qgis, "Created " + unicode(len(points)) + " polygon Voronoi diagram")

	return None

def hcmgis_endpoint(start, distance, degrees):
	# Assumes points are WGS 84 lat/long, distance in meters,
	# bearing in degrees with north = 0, east = 90, west = -90
	# Uses the haversine formula for calculation:
	# http://www.movable-type.co.uk/scripts/latlong.html
	radius = 6378137.0 # meters

	start_lon = start.x() * pi / 180
	start_lat = start.y() * pi / 180
	bearing = degrees * pi / 180

	end_lat = asin((sin(start_lat) * cos(distance / radius)) +
		(cos(start_lat) * sin(distance / radius) * cos(bearing)))
	end_lon = start_lon + atan2( \
		sin(bearing) * sin(distance / radius) * cos(start_lat),
		cos(distance / radius) - (sin(start_lat) * sin(end_lat)))

	return QgsPointXY(end_lon * 180 / pi, end_lat * 180 / pi)


# --------------------------------------------------------
# hcmgis_lec - Largest Empty Circle inside the convexhull of a point set based on Voronoi Diagram
# 	 
# --------------------------------------------------------

def hcmgis_lec(qgis, layer, selectedfield):	
	import processing
	if layer is None:
		return u'No selected point layer!'  
	if (not layer.wkbType()== QgsWkbTypes.Point):
		return 'Multipoint layer is not supported. Please convert to Point layer!'	
	parameters1 = {'INPUT': layer,
				  'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'
				  } 
	voronoipolygon = processing.run('qgis:voronoipolygons', parameters1)
	#processing.runAndLoadResults('qgis:voronoipolygons', parameters1)

	#parameters2 = {'INPUT': layer,
	#				'OUTPUT' : 'memory:convexhull'} 
	#convexhull = processing.run('qgis:convexhull', parameters2)	

	parameters2 = {'INPUT': layer,
				'FIELD' : None,
				 'TYPE' : 3,
					'OUTPUT' : 'memory:convexhull'} 
	convexhull = processing.run('qgis:minimumboundinggeometry', parameters2)	

	parameter2_1 =  {'INPUT': convexhull['OUTPUT'],					 
				  'OUTPUT':  "memory:convexhull_vertices"}
	convexhull_vertices = processing.run('qgis:extractvertices',parameter2_1) 
 


	parameter3 =  {'INPUT': voronoipolygon['OUTPUT'],	
				   'OVERLAY': convexhull['OUTPUT'], 
				  'OUTPUT':  "memory:voronoi_clip"}
	voronoi_clip = processing.run('qgis:clip',parameter3) 

	parameter4 =  {'INPUT': voronoi_clip['OUTPUT'],					 
				  'OUTPUT':  "memory:voronoi_vertices"}
	voronoi_vertices = processing.run('qgis:extractvertices',parameter4) 

	parameter5 =  {'INPUT': voronoi_vertices['OUTPUT'],					 
				  'OUTPUT':  "memory:voronoi_vertices_clean"}
	voronoi_vertices_clean = processing.run('qgis:deleteduplicategeometries',parameter5) 

	parameter6 =  {'INPUT': voronoi_vertices_clean['OUTPUT'],
					'OVERLAY': 	convexhull_vertices['OUTPUT'],				 
				   'OUTPUT':  "memory:candidates"}
	candidates = processing.run('qgis:difference',parameter6) 

	parameter7 =  {'INPUT': candidates['OUTPUT'],
					'FIELD': selectedfield,
					'HUBS' : layer,
					'UNIT' : 0,
				   'OUTPUT':  "memory:distances"}
	max_distances = processing.run('qgis:distancetonearesthubpoints',parameter7) 
	
	values = []
	centers = max_distances['OUTPUT']
	idx =  centers.dataProvider().fieldNameIndex("HubDist")
	for feat in centers.getFeatures():
		attrs = feat.attributes()
		values.append(attrs[idx])
	
	maxvalue = max(values)
	maxvaluestr = str(max(values))	
	
	selection = centers.getFeatures(QgsFeatureRequest(QgsExpression('"HubDist"' + '=' + maxvaluestr)))
	ids = [s.id() for s in selection]
	centers.selectByIds(ids)

	parameters8 = {'INPUT':centers,
					'OUTPUT':  "memory:center"}
	center = processing.runAndLoadResults('qgis:saveselectedfeatures',parameters8)
	
	radius_attribute = None
	radius_unit = 'Meters'
	edge_attribute = 'Rounded'
	edge_count = 64
	hcmgis_buffers_radius = maxvalue
	rotation_attribute = None
	hcmgis_buffers_rotation = 0
	#savename = "E:/circle.shp"
	selectedonly = False
	#center_layer = center['OUTPUT']	
	# try:
	# 	hcmgis_buffers(qgis, center_layer, radius_attribute, hcmgis_buffers_radius, radius_unit, 
	# 		edge_attribute, edge_count, rotation_attribute, hcmgis_buffers_rotation,
	# 		savename, selectedonly, True)
	# 	#hcmgis_buffer_point(point, hcmgis_buffers_radius,edge_count,hcmgis_buffers_rotation)
	# except Exception:
	# 	return	

# --------------------------------------------------------
#    hcmgis_buffers - Create buffers around shapes
# --------------------------------------------------------
def hcmgis_buffer_point(point, meters, edges, rotation_degrees):
	if (meters <= 0) or (edges < 3):
		return None

	# Points are treated separately from other geometries so that discrete
	# edges can be supplied for non-circular buffers that are not supported
	# by the QgsGeometry.buffer() function

	wgs84 = QgsCoordinateReferenceSystem()
	wgs84.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")

	# print "Point " + unicode(point.x()) + ", " + unicode(point.y()) + " meters " + unicode(meters)

	polyline = []
	for edge in range(0, edges + 1):
		degrees = ((float(edge) * 360.0 / float(edges)) + rotation_degrees) % 360
		polyline.append(hcmgis_endpoint(QgsPointXY(point), meters, degrees))

	return QgsGeometry.fromPolygonXY([polyline])


def hcmgis_buffers(qgis, layer, radius_attribute, radius, radius_unit, edge_attribute, edge_count, 
	rotation_attribute, rotation_degrees, savename, selectedonly, addlayer):
	# Create the output file
	if QFile(savename).exists():
		if not QgsVectorFileWriter.deleteShapeFile(savename):
			return "Failure deleting existing shapefile: " + savename
 
	wgs84 = QgsCoordinateReferenceSystem()
	wgs84.createFromProj4("+proj=longlat +datum=WGS84 +no_defs")
	transform = QgsCoordinateTransform(layer.crs(), wgs84, QgsProject.instance())
	# print layer.crs().toProj4() + " -> " + wgs84.toProj4()
	
	outfile = QgsVectorFileWriter(savename, "utf-8", layer.fields(), QgsWkbTypes.Polygon, wgs84, "ESRI Shapefile")

	if (outfile.hasError() != QgsVectorFileWriter.NoError):
		return "Failure creating output shapefile: " + unicode(outfile.errorMessage())

	# Create buffers for each feature
	buffercount = 0
	featurecount = layer.featureCount()
	if selectedonly:
		feature_list = layer.selectedFeatures()
	else:
		feature_list = layer.getFeatures()

	for feature_index, feature in enumerate(feature_list):
		#hcmgis_status_message(qgis, "Writing feature " + \
			#unicode(feature.id()) + " of " + unicode(featurecount))

		geometry = feature.geometry()
		geometry.transform(transform) # Needs to be WGS 84 to use Haversine distance calculation
		# print "Transform " + unicode(x) + ": " + unicode(geometry.centroid().asPoint().x())

		if (geometry.wkbType() in [QgsWkbTypes.Point, QgsWkbTypes.Point25D, QgsWkbTypes.MultiPoint, QgsWkbTypes.MultiPoint25D]):

			#newgeometry = hcmgis_buffer_point(geometry.asPoint(), feature_radius, feature_edges, feature_rotation)
			newgeometry = hcmgis_buffer_point(geometry.asPoint(), radius, edge_count, 0)

		if newgeometry == None:
			return "Failure converting geometry for feature " + unicode(buffercount)

		else:
			newfeature = QgsFeature()
			newfeature.setGeometry(newgeometry)
			newfeature.setAttributes(feature.attributes())
			outfile.addFeature(newfeature)
	
		buffercount = buffercount + 1

	del outfile

	if addlayer:
		vlayer = qgis.addVectorLayer(savename, os.path.basename(savename), "ogr")
		
	#hcmgis_completion_message(qgis, unicode(buffercount) + " buffers created for " + \
		#unicode(featurecount) + " features")

	return None

#hcmgis_format_convert
def hcmgis_format_convert(input_file_name, output_file_name,ogr_driver_name):
	# Parameter error checks and conversions
	import processing
	input_file = QgsVectorLayer(input_file_name)	
	if input_file.featureCount() <= 0:
		return "Invalid Vector file"
	error, error_string = QgsVectorFileWriter.writeAsVectorFormat(input_file, output_file_name, input_file.dataProvider().encoding(), input_file.crs(),ogr_driver_name, False)
	if error != QgsVectorFileWriter.NoError:
		return "Failure creating output file: " + str(error_string)
	return None
# ----------------------------------------------------------------
#    hcmgis_point_import_from_csv - point import from CSV
# ----------------------------------------------------------------

def hcmgis_csv2shp(input_csv_name, latitude_field, longitude_field, \
		output_file_name, status_callback = None):

	# Parameter error checks and conversions
	input_csv = QgsVectorLayer(input_csv_name)
	if input_csv.featureCount() <= 0:
		return "Invalid CSV point file"

	latitude_index = input_csv.fields().indexFromName(latitude_field)
	if latitude_index < 0:
		return "Invalid latitude field"

	longitude_index = input_csv.fields().indexFromName(longitude_field)
	if longitude_index < 0:
		return "Invalid longitude field"

	wkb_type = QgsWkbTypes.Point

	# Create the output shapefile

	fields = QgsFields()	
	for field in input_csv.fields():
		fields.append(field)

	# Assume WGS 84?
	crs = QgsCoordinateReferenceSystem()
	crs.createFromSrid(4326) # WGS 84

	if not output_file_name:
		return "No output file name given"

	file_formats = { ".shp":"ESRI Shapefile"}

	if os.path.splitext(output_file_name)[1] not in file_formats:
		return "Unsupported output file format: " + str(output_file_name)

	output_file_format = file_formats[os.path.splitext(output_file_name)[1]]

	outfile = QgsVectorFileWriter(output_file_name, "utf-8", fields, wkb_type, crs, output_file_format)

	if (outfile.hasError() != QgsVectorFileWriter.NoError):
		return "Failure creating output file: " + str(outfile.errorMessage())

	shape_count = 0
	current_shape_id = False

	for row_number, row in enumerate(input_csv.getFeatures()):
		if status_callback and ((row_number % 10) == 0):
			if status_callback(100 * row_number / input_csv.featureCount(), 
					"Point " + str(row_number) + " of " + str(input_csv.featureCount())):
				return "Canceled at point " + str(row_number)

		if (latitude_index >= len(row.attributes())) or (latitude_index >= len(row.attributes())):
			return "Node file missing lat/long at row " + str(row_number + 1)
	
		point = QgsPointXY(float(row.attributes()[longitude_index]), float(row.attributes()[latitude_index]))

		# Each node is a separate feature in a point file
		
		newfeature = QgsFeature()
		newfeature.setAttributes(row.attributes())
		geometry = QgsGeometry.fromPointXY(point)
		newfeature.setGeometry(geometry)
		outfile.addFeature(newfeature)
		shape_count += 1
		continue		
		
	del outfile

	if status_callback:
		#status_callback(100, str(shape_count) + " shapes, " + str(input_csv.featureCount()) + " nodes")
		status_callback(100, None)

	return None

def hcmgis_txt2csv(input_txt_name, output_file_name, status_callback = None):
	import csv
	import os
	with open(input_txt_name, "r") as input_file:
		in_txt = csv.reader(input_file)
		with open(output_file_name, 'w', newline='') as output_file:
			out_csv = csv.writer(output_file)
			out_csv.writerows(in_txt)
	
	if status_callback:
		status_callback(100, None)

	return None

def hcmgis_xls2csv(input_xls_name, 	output_file_name, status_callback = None):
	import csv
	import os
	import xlrd
	temp_outfile_name = output_file_name.replace(".csv","", 1)

	#Non_empty sheets	
	with xlrd.open_workbook(input_xls_name) as wb:
		non_empty_sheets = []
		for sheet_name in wb.sheet_names():
			if (wb.sheet_by_name(sheet_name).nrows > 0 or wb.sheet_by_name(sheet_name).ncols > 0): # check none empty sheets
				non_empty_sheets.append(sheet_name)
		if (len(non_empty_sheets) == 1):
			sh = wb.sheet_by_index(0)
			with  open(output_file_name, 'w', newline="") as f:
				c = csv.writer(f)
				for r in range(sh.nrows):
					c.writerow(sh.row_values(r))
		else:
			for sheet_name in non_empty_sheets:
				if (wb.sheet_by_name(sheet_name).nrows > 0 or wb.sheet_by_name(sheet_name).ncols > 0): # check none empty sheets
					sh  = wb.sheet_by_name(sheet_name) 
					sheet_csv = temp_outfile_name + '_'+ sheet_name + '.csv'
					with  open(sheet_csv, 'w', newline="") as f:
						c = csv.writer(f)
						for r in range(sh.nrows):
							c.writerow(sh.row_values(r))
	if status_callback:
		status_callback(100, None)
	return None

def hcmgis_geofabrik(region, country, outdir):
	import os
	import urllib
	import zipfile
	import tempfile
	import urllib.request
	temp_dir = tempfile.mkdtemp()
	download_url_shp = r'https://download.geofabrik.de/' + region + '/'+ country+ '-latest-free.shp.zip'	
	zip_filename_shp = outdir + '\\'+ country +  '-latest-free.shp.zip'
	unzip_folder_shp = zip_filename_shp.replace('.zip','')
	
	download_url_pbf = r'https://download.geofabrik.de/' + region + '/'+ country+ '-latest.osm.pbf'	
	filename_pbf = outdir + '\\'+ country +  '-latest.osm.pbf'
	
	LinkFound = True
	try:
		urllib.request.urlopen(download_url_shp)
	except:
		LinkFound = False
	
	if  LinkFound:
		filesizeinMB = round(int(urllib.request.urlopen(download_url_shp).info()['Content-Length'])*10**(-6),2)
		QMessageBox.information(None, "Attention",'Estimated Shapefile size: ' + str(filesizeinMB) + ' MB. '+ 'Downloading may take time. Please be patient!')
		zip, headers = urllib.request.urlretrieve(download_url_shp, zip_filename_shp)
		if not os.path.exists (unzip_folder_shp):
			os.mkdir(unzip_folder_shp)
		with zipfile.ZipFile(zip, 'r') as zip_ref:
			zip_ref.extractall(unzip_folder_shp)		
		#os.chdir(zip_folder)
		wholelist = os.listdir(unzip_folder_shp)
		root = QgsProject.instance().layerTreeRoot()
		shapeGroup = root.addGroup(country)
		for file in wholelist:
			if ".shp" in file:
				if "xml" not in file:
					fileroute=unzip_folder_shp+'\\'+file
					filename = QgsVectorLayer(fileroute,file[:-4],"ogr")
					QgsProject.instance().addMapLayer(filename,False)
					shapeGroup.insertChildNode(1,QgsLayerTreeLayer(filename))
	else:
		filesizeinMB = round(int(urllib.request.urlopen(download_url_pbf).info()['Content-Length'])*10**(-6),2)
		QMessageBox.information(None, "Attention",'Estimated OSM pbf file size: ' + str(filesizeinMB) + ' MB. '+ 'Downloading may take time. Please be patient!')
		pbf, headers =  urllib.request.urlretrieve(download_url_pbf, filename_pbf)		 
		QMessageBox.information(None, "Attention",u'Data in OSM PBF format. Please manually add it to QGIS!')
	QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')
	# with zipfile.ZipFile(zip) as zf:
	#     files = zf.namelist()
	#     for filename in files:
	#         #if 'roads' in filename:
	# 		file_path = os.path.join(os.getcwd(), filename)
	# 		f = open(file_path, 'wb')
	# 		f.write(zf.read(filename))
	# 		f.close()
	# 		if filename == 'gis_osm_roads_free_1.shp':
	# 			roads_shp_path = file_path	
	# print ('Downloaded file to %s' % roads_shp_path)	
def hcmgis_gadm(country, country_short, outdir):
	import os
	import urllib
	import zipfile
	import tempfile
	import urllib.request
	pre = 'https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_'
	suf = '_shp.zip'
	download_url_shp = pre + country_short + suf
	zip_filename_shp = outdir + '\\'+ country_short +  suf
	unzip_folder_shp = zip_filename_shp.replace('.zip','')
	LinkFound = True
	try:
		urllib.request.urlopen(download_url_shp)
	except:
		LinkFound = False
	
	if  LinkFound:
		filesizeinMB = round(int(urllib.request.urlopen(download_url_shp).info()['Content-Length'])*10**(-6),2)
		QMessageBox.information(None, "Attention",'Estimated Shapefile size: ' + str(filesizeinMB) + ' MB. '+ 'Downloading may take time. Please be patient!')
		zip, headers = urllib.request.urlretrieve(download_url_shp, zip_filename_shp)
		if not os.path.exists (unzip_folder_shp):
			os.mkdir(unzip_folder_shp)
		with zipfile.ZipFile(zip, 'r') as zip_ref:
			zip_ref.extractall(unzip_folder_shp)		
		#os.chdir(zip_folder)
		wholelist = os.listdir(unzip_folder_shp)
		root = QgsProject.instance().layerTreeRoot()
		shapeGroup = root.addGroup(country)
		for file in wholelist:
			if ".shp" in file:
				if "xml" not in file:
					fileroute=unzip_folder_shp+'\\'+file
					filename = QgsVectorLayer(fileroute,file[:-4],"ogr")
					QgsProject.instance().addMapLayer(filename,False)
					shapeGroup.insertChildNode(1,QgsLayerTreeLayer(filename))
	else:
		QMessageBox.information(None, "Attention",u'Link not found!')
		return
	QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')
