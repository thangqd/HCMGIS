#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------
#    hcmgis_library - hcmgis operation functions
# --------------------------------------------------------

import io
import re
import csv
import sys
import locale
import random
import xlrd
import urllib
import argparse
import json
import logging
import numbers
import requests
import zipfile
import stat
import operator
import tempfile
import urllib.request
import os.path
import xml.etree.ElementTree

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.gui import QgsMessageBar
from math import *
# Used instead of "import math" so math functions can be used without "math." prefix
import qgis.utils
import processing   
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

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
# hcmgis_lec - Largest Empty Circle inside the convexhull of a point set based on Voronoi Diagram
# 	 
# --------------------------------------------------------

def hcmgis_lec(qgis, layer, selectedfield):	
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

#hcmgis_format_convert
def hcmgis_format_convert(input_file_name, output_file_name,ogr_driver_name):
    if  (input_file_name.endswith('.pbf') or input_file_name.endswith('.gpkg') or input_file_name.endswith('.dxf') or  input_file_name.endswith('.dgn')):
        try:
            ogr2ogr(["","-skipfailure","-f", ogr_driver_name,output_file_name, input_file_name])
            return None
        except:
            return "Failure creating output file"
    else:
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
    with open(input_txt_name, "r") as input_file:
        in_txt = csv.reader(input_file)
        with open(output_file_name, 'w', newline='') as output_file:
            out_csv = csv.writer(output_file)
            out_csv.writerows(in_txt)
    
    if status_callback:
        status_callback(100, None)

    return None

def hcmgis_xls2csv(input_xls_name, 	output_file_name, status_callback = None):  
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

def hcmgis_geofabrik(region, country, outdir,status_callback = None):
    #temp_dir = tempfile.mkdtemp()
    download_url_shp = r'https://download.geofabrik.de/' + region + '/'+ country+ '-latest-free.shp.zip'	
    #print (download_url_shp)
    zip_filename_shp = outdir + '\\'+ country +  '-latest-free.shp.zip'
    #unzip_folder_shp = zip_filename_shp.replace('.zip','')
    unzip_folder_shp = zip_filename_shp.split('.')[-1]
    #print (zip_filename_shp)
    download_url_pbf = r'https://download.geofabrik.de/' + region + '/'+ country+ '-latest.osm.pbf'	
    filename_pbf = outdir + '\\'+ country +  '-latest.osm.pbf'
    #print (download_url_pbf)    
    headers = ""
    zip = requests.get(download_url_shp, headers=headers, stream=True, allow_redirects=True)    
    total_size = int(zip.headers.get('content-length'))
    total_size_MB = round(total_size*10**(-6),2)
    chunk_size = int(total_size/100)
    
    if  (zip.status_code == 200):
        print ('total_length MB:', total_size_MB)
        confirmed = QMessageBox.question(None, "Attention",'Estimated Shapefile size: ' +str(total_size_MB) + ' MB. Downloading may take time. Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            i = 0
            f = open(zip_filename_shp, 'wb')
            for chunk in zip.iter_content(chunk_size = chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                if status_callback: 
                    status_callback(i,None)
                i+=1
               
            f.close()
            print (unzip_folder_shp)
            QMessageBox.information(None, "Congrats",u'Download completed! Now wait for a minute to extract zip files and load into QGIS')
            if status_callback: 
                status_callback(0,None)
            if not os.path.exists (unzip_folder_shp):
                os.mkdir(unzip_folder_shp)
            
            with zipfile.ZipFile(zip_filename_shp) as zip_ref:
                zip_ref.extractall(unzip_folder_shp)	
            #os.chdir(zip_folder)
            wholelist = os.listdir(unzip_folder_shp)
            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.addGroup(country)
            i = 0
            for file in wholelist:
                if ".shp" in file:
                    if "xml" not in file:
                        fileroute=unzip_folder_shp+'\\'+file
                        filename = QgsVectorLayer(fileroute,file[:-4],"ogr")
                        QgsProject.instance().addMapLayer(filename,False)
                        shapeGroup.insertChildNode(1,QgsLayerTreeLayer(filename))
                percen_complete = i/len(wholelist)*100                
                if status_callback: 
                    status_callback(i,None)
                i+=1
            status_callback(100,None)            
            QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')
    else:
        zip = requests.get(download_url_pbf, headers=headers, stream=True, allow_redirects=True)    
        total_size = int(zip.headers.get('content-length'))
        total_size_MB = round(total_size*10**(-6),2)
        chunk_size = int(total_size/100)       
        confirmed = QMessageBox.question(None, "Attention",'Estimated OSM ppf size: ' +str(total_size_MB) + ' MB. Downloading may take time. Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            i = 0
            f = open(filename_pbf, 'wb')
            for chunk in zip.iter_content(chunk_size = chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                if status_callback: 
                    status_callback(i,None)
                i+=1
            f.close()
            #print (unzip_folder_shp)
            QMessageBox.information(None, "Congrats",u'Download completed! Now wait for a minute to convert pbf to GeoPackage and load into QGIS')
            if status_callback: 
                status_callback(0,None)
            filename_gpkg = filename_pbf[:-4]+'.gpkg'
            ogr2ogr(["","-f", "GPKG",filename_gpkg, filename_pbf])
            #from qgis.core import QgsVectorLayer, QgsProject

            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.addGroup(country)
            layer = QgsVectorLayer(filename_gpkg,"gpkg","ogr")
            subLayers =layer.dataProvider().subLayers()
            i = 0
            for subLayer in subLayers:
                name = subLayer.split('!!::!!')[1]
                uri = "%s|layername=%s" % (filename_gpkg, name,)
                # Create layer
                if name != 'other_relations':
                    sub_vlayer = QgsVectorLayer(uri, name, 'ogr')
                    # Add layer to map
                    QgsProject.instance().addMapLayer(sub_vlayer,False)
                    shapeGroup.insertChildNode(1,QgsLayerTreeLayer(sub_vlayer))
                percen_complete = i/len(subLayers)*100                
                if status_callback: 
                    status_callback(i,None)
                i+=1
            status_callback(100,None)  
            QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')
  
def hcmgis_geofabrik2(region, country,state, outdir,status_callback = None):
    #temp_dir = tempfile.mkdtemp()
    download_url_shp = r'https://download.geofabrik.de/' + region + '/'+ country+ '/' + state + '-latest-free.shp.zip'	
    print (download_url_shp)
    zip_filename_shp = outdir + '\\'+ country + '-'+ state + '-latest-free.shp.zip'
    unzip_folder_shp = zip_filename_shp.replace('.zip','')

    download_url_pbf = r'https://download.geofabrik.de/' + region + '/'+ country+ '/' + state+'-latest.osm.pbf'	
    print (download_url_pbf)
    filename_pbf = outdir + '\\'+ country + '-'+ state + '-latest.osm.pbf'   
    headers = ""
    zip = requests.get(download_url_shp, headers=headers, stream=True, allow_redirects=True)    
    total_size = int(zip.headers.get('content-length'))
    total_size_MB = round(total_size*10**(-6),2)
    chunk_size = int(total_size/100)    
    if  (zip.status_code == 200):
        print ('total_length MB:', total_size_MB)
        confirmed = QMessageBox.question(None, "Attention",'Estimated Shapefile size: ' +str(total_size_MB) + ' MB. Downloading may take time. Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            i = 0
            f = open(zip_filename_shp, 'wb')
            for chunk in zip.iter_content(chunk_size = chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                if status_callback: 
                    status_callback(i,None)
                i+=1               
            f.close()
            print (unzip_folder_shp)
            QMessageBox.information(None, "Congrats",u'Download completed! Now wait for a minute to extract zip files and load into QGIS')
            if status_callback: 
                status_callback(0,None)
            if not os.path.exists (unzip_folder_shp):
                os.mkdir(unzip_folder_shp)
            
            with zipfile.ZipFile(zip_filename_shp) as zip_ref:
                zip_ref.extractall(unzip_folder_shp)	
            #os.chdir(zip_folder)
            wholelist = os.listdir(unzip_folder_shp)
            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.addGroup(country+'_'+state)
            i = 0
            for file in wholelist:
                if ".shp" in file:
                    if "xml" not in file:
                        fileroute=unzip_folder_shp+'\\'+file
                        filename = QgsVectorLayer(fileroute,file[:-4],"ogr")
                        QgsProject.instance().addMapLayer(filename,False)
                        shapeGroup.insertChildNode(1,QgsLayerTreeLayer(filename))
                percen_complete = i/len(wholelist)*100                
                if status_callback: 
                    status_callback(i,None)
                i+=1
            status_callback(100,None)            
            QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')    
    else:
        zip = requests.get(download_url_pbf, headers=headers, stream=True, allow_redirects=True)    
        total_size = int(zip.headers.get('content-length'))
        total_size_MB = round(total_size*10**(-6),2)
        chunk_size = int(total_size/100)        
        confirmed = QMessageBox.question(None, "Attention",'Estimated OSM ppf size: ' +str(total_size_MB) + ' MB. Downloading may take time. Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            i = 0
            f = open(filename_pbf, 'wb')
            for chunk in zip.iter_content(chunk_size = chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                if status_callback: 
                    status_callback(i,None)
                i+=1
            f.close()
            #print (unzip_folder_shp)
            QMessageBox.information(None, "Congrats",u'Download completed! Now wait for a minute to convert pbf to GeoPackage and load into QGIS')
            if status_callback: 
                status_callback(0,None)
            filename_gpkg = filename_pbf[:-4]+'.gpkg'
            ogr2ogr(["","-f", "GPKG",filename_gpkg, filename_pbf])
            #from qgis.core import QgsVectorLayer, QgsProject

            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.addGroup(country+'_'+state)
            layer = QgsVectorLayer(filename_gpkg,"gpkg","ogr")
            subLayers =layer.dataProvider().subLayers()
            i = 0
            for subLayer in subLayers:
                name = subLayer.split('!!::!!')[1]
                uri = "%s|layername=%s" % (filename_gpkg, name,)
                # Create layer
                if name != 'other_relations':
                    sub_vlayer = QgsVectorLayer(uri, name, 'ogr')
                    # Add layer to map
                    QgsProject.instance().addMapLayer(sub_vlayer,False)
                    shapeGroup.insertChildNode(1,QgsLayerTreeLayer(sub_vlayer))
                percen_complete = i/len(subLayers)*100                
                if status_callback: 
                    status_callback(i,None)
                i+=1
            if status_callback: 
                status_callback(100,None) 
            QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')

def hcmgis_gadm(country, country_short, outdir,status_callback = None):  
    pre = 'https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_'
    suf = '_shp.zip'
    download_url_shp = pre + country_short + suf
    zip_filename_shp = outdir + '\\'+ country_short +  suf
    unzip_folder_shp = zip_filename_shp.replace('.zip','')
    
    headers = ""
    zip = requests.get(download_url_shp, headers=headers, stream=True, allow_redirects=True)    
    total_size = int(zip.headers.get('content-length'))
    total_size_MB = round(total_size*10**(-6),2)
    chunk_size = int(total_size/100)    
    if  (zip.status_code == 200):
        print ('total_length MB:', total_size_MB)
        confirmed = QMessageBox.question(None, "Attention",'Estimated Shapefile size: ' +str(total_size_MB) + ' MB. Downloading may take time. Are you sure?', QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            i = 0
            f = open(zip_filename_shp, 'wb')
            for chunk in zip.iter_content(chunk_size = chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                if status_callback: 
                    status_callback(i,None)
                i+=1               
            f.close()        
            QMessageBox.information(None, "Congrats",u'Download completed! Now wait for a minute to extract zip files and load into QGIS')
            status_callback(0,None)
            if not os.path.exists (unzip_folder_shp):
                os.mkdir(unzip_folder_shp)
            
            with zipfile.ZipFile(zip_filename_shp) as zip_ref:
                zip_ref.extractall(unzip_folder_shp)
            #os.chdir(zip_folder)
            wholelist = os.listdir(unzip_folder_shp)
            root = QgsProject.instance().layerTreeRoot()
            shapeGroup = root.addGroup(country)
            i = 0
            for file in wholelist:
                if ".shp" in file:
                    if "xml" not in file:
                        fileroute=unzip_folder_shp+'\\'+file
                        filename = QgsVectorLayer(fileroute,file[:-4],"ogr")
                        QgsProject.instance().addMapLayer(filename,False)
                        shapeGroup.insertChildNode(1,QgsLayerTreeLayer(filename))
                percen_complete = i/len(wholelist)*100                
                status_callback(i,None)
                i+=1
            status_callback(100,None)            
            QMessageBox.information(None, "Congrats",u'Done. Thank you for your patience!')
    else:
        QMessageBox.warning(None, "Attention",u'Link not found!')
    return


#################
#ogr2ogr
##################

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*****************************************************************************
# $Id$
#
# Project:  OpenGIS Simple Features Reference Implementation
# Purpose:  Python port of a simple client for translating between formats.
# Author:   Even Rouault, <even dot rouault at mines dash paris dot org>
#
# Port from ogr2ogr.cpp whose author is Frank Warmerdam
#
#*****************************************************************************
# Copyright (c) 2010-2013, Even Rouault <even dot rouault at mines-paris dot org>
# Copyright (c) 1999, Frank Warmerdam
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#**************************************************************************

# Note : this is the most direct port of ogr2ogr.cpp possible
# It could be made much more Python'ish !


###############################################################################

class ScaledProgressObject:
    def __init__(self, min, max, cbk, cbk_data = None):
        self.min = min
        self.max = max
        self.cbk = cbk
        self.cbk_data = cbk_data

###############################################################################

def ScaledProgressFunc(pct, msg, data):
    if data.cbk is None:
        return True
    return data.cbk(data.min + pct * (data.max - data.min), msg, data.cbk_data)

###############################################################################

def EQUAL(a, b):
    return a.lower() == b.lower()

###############################################################################
# Redefinition of GDALTermProgress, so that autotest/pyscripts/test_ogr2ogr_py.py
# can check that the progress bar is displayed

nLastTick = -1

def TermProgress( dfComplete, pszMessage, pProgressArg ):

    global nLastTick
    nThisTick = (int) (dfComplete * 40.0)

    if nThisTick < 0:
        nThisTick = 0
    if nThisTick > 40:
        nThisTick = 40

    # Have we started a new progress run?
    if nThisTick < nLastTick and nLastTick >= 39:
        nLastTick = -1

    if nThisTick <= nLastTick:
        return True

    while nThisTick > nLastTick:
        nLastTick = nLastTick + 1
        if (nLastTick % 4) == 0:
            sys.stdout.write('%d' % ((nLastTick / 4) * 10))
        else:
            sys.stdout.write('.')

    if nThisTick == 40:
        print(" - done." )
    else:
        sys.stdout.flush()

    return True

class TargetLayerInfo:
    def __init__(self):
        self.poDstLayer = None
        self.poCT = None
        #self.papszTransformOptions = None
        self.panMap = None
        self.iSrcZField = None

class AssociatedLayers:
    def __init__(self):
        self.poSrcLayer = None
        self.psInfo = None

#**********************************************************************
#                                main()
#**********************************************************************

bSkipFailures = False
nGroupTransactions = 200
bPreserveFID = False
nFIDToFetch = ogr.NullFID

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

GeomOperation = Enum(["NONE", "SEGMENTIZE", "SIMPLIFY_PRESERVE_TOPOLOGY"])

def ogr2ogr(args = None, progress_func = TermProgress, progress_data = None):

    global bSkipFailures
    global nGroupTransactions
    global bPreserveFID
    global nFIDToFetch

    pszFormat = "ESRI Shapefile"
    pszDataSource = None
    pszDestDataSource = None
    papszLayers = []
    papszDSCO = []
    papszLCO = []
    bTransform = False
    bAppend = False
    bUpdate = False
    bOverwrite = False
    pszOutputSRSDef = None
    pszSourceSRSDef = None
    poOutputSRS = None
    bNullifyOutputSRS = False
    poSourceSRS = None
    pszNewLayerName = None
    pszWHERE = None
    poSpatialFilter = None
    pszSelect = None
    papszSelFields = None
    pszSQLStatement = None
    eGType = -2
    bPromoteToMulti = False
    eGeomOp = GeomOperation.NONE
    dfGeomOpParam = 0
    papszFieldTypesToString = []
    bDisplayProgress = False
    pfnProgress = None
    pProgressArg = None
    bClipSrc = False
    bWrapDateline = False
    poClipSrc = None
    pszClipSrcDS = None
    pszClipSrcSQL = None
    pszClipSrcLayer = None
    pszClipSrcWhere = None
    poClipDst = None
    pszClipDstDS = None
    pszClipDstSQL = None
    pszClipDstLayer = None
    pszClipDstWhere = None
    #pszSrcEncoding = None
    #pszDstEncoding = None
    bWrapDateline = False
    bExplodeCollections = False
    pszZField = None
    nCoordDim = -1

    if args is None:
        args = sys.argv

    args = ogr.GeneralCmdLineProcessor( args )

# --------------------------------------------------------------------
#      Processing command line arguments.
# --------------------------------------------------------------------
    if args is None:
        return False

    nArgc = len(args)

    iArg = 1
    while iArg < nArgc:
        if EQUAL(args[iArg],"-f") and iArg < nArgc-1:
            iArg = iArg + 1
            pszFormat = args[iArg]

        elif EQUAL(args[iArg],"-dsco") and iArg < nArgc-1:
            iArg = iArg + 1
            papszDSCO.append(args[iArg] )

        elif EQUAL(args[iArg],"-lco") and iArg < nArgc-1:
            iArg = iArg + 1
            papszLCO.append(args[iArg] )

        elif EQUAL(args[iArg],"-preserve_fid"):
            bPreserveFID = True

        elif len(args[iArg]) >= 5 and EQUAL(args[iArg][0:5], "-skip"):
            bSkipFailures = True
            nGroupTransactions = 1 # #2409

        elif EQUAL(args[iArg],"-append"):
            bAppend = True
            bUpdate = True

        elif EQUAL(args[iArg],"-overwrite"):
            bOverwrite = True
            bUpdate = True

        elif EQUAL(args[iArg],"-update"):
            bUpdate = True

        elif EQUAL(args[iArg],"-fid") and iArg < nArgc-1:
            iArg = iArg + 1
            nFIDToFetch = int(args[iArg])

        elif EQUAL(args[iArg],"-sql") and iArg < nArgc-1:
            iArg = iArg + 1
            pszSQLStatement = args[iArg]

        elif EQUAL(args[iArg],"-nln") and iArg < nArgc-1:
            iArg = iArg + 1
            pszNewLayerName = args[iArg]

        elif EQUAL(args[iArg],"-nlt") and iArg < nArgc-1:

            if EQUAL(args[iArg+1],"NONE"):
                eGType = ogr.wkbNone
            elif EQUAL(args[iArg+1],"GEOMETRY"):
                eGType = ogr.wkbUnknown
            elif EQUAL(args[iArg+1],"PROMOTE_TO_MULTI"):
                bPromoteToMulti = True
            elif EQUAL(args[iArg+1],"POINT"):
                eGType = ogr.wkbPoint
            elif EQUAL(args[iArg+1],"LINESTRING"):
                eGType = ogr.wkbLineString
            elif EQUAL(args[iArg+1],"POLYGON"):
                eGType = ogr.wkbPolygon
            elif EQUAL(args[iArg+1],"GEOMETRYCOLLECTION"):
                eGType = ogr.wkbGeometryCollection
            elif EQUAL(args[iArg+1],"MULTIPOINT"):
                eGType = ogr.wkbMultiPoint
            elif EQUAL(args[iArg+1],"MULTILINESTRING"):
                eGType = ogr.wkbMultiLineString
            elif EQUAL(args[iArg+1],"MULTIPOLYGON"):
                eGType = ogr.wkbMultiPolygon
            elif EQUAL(args[iArg+1],"GEOMETRY25D"):
                eGType = ogr.wkbUnknown | ogr.wkb25DBit
            elif EQUAL(args[iArg+1],"POINT25D"):
                eGType = ogr.wkbPoint25D
            elif EQUAL(args[iArg+1],"LINESTRING25D"):
                eGType = ogr.wkbLineString25D
            elif EQUAL(args[iArg+1],"POLYGON25D"):
                eGType = ogr.wkbPolygon25D
            elif EQUAL(args[iArg+1],"GEOMETRYCOLLECTION25D"):
                eGType = ogr.wkbGeometryCollection25D
            elif EQUAL(args[iArg+1],"MULTIPOINT25D"):
                eGType = ogr.wkbMultiPoint25D
            elif EQUAL(args[iArg+1],"MULTILINESTRING25D"):
                eGType = ogr.wkbMultiLineString25D
            elif EQUAL(args[iArg+1],"MULTIPOLYGON25D"):
                eGType = ogr.wkbMultiPolygon25D
            else:
                print("-nlt %s: type not recognised." % args[iArg+1])
                return False

            iArg = iArg + 1

        elif EQUAL(args[iArg],"-dim") and iArg < nArgc-1:

            nCoordDim = int(args[iArg+1])
            if nCoordDim != 2 and nCoordDim != 3:
                print("-dim %s: value not handled." % args[iArg+1])
                return False
            iArg = iArg + 1

        elif (EQUAL(args[iArg],"-tg") or \
                EQUAL(args[iArg],"-gt")) and iArg < nArgc-1:
            iArg = iArg + 1
            nGroupTransactions = int(args[iArg])

        elif EQUAL(args[iArg],"-s_srs") and iArg < nArgc-1:
            iArg = iArg + 1
            pszSourceSRSDef = args[iArg]

        elif EQUAL(args[iArg],"-a_srs") and iArg < nArgc-1:
            iArg = iArg + 1
            pszOutputSRSDef = args[iArg]
            if EQUAL(pszOutputSRSDef, "NULL") or \
               EQUAL(pszOutputSRSDef, "NONE"):
                pszOutputSRSDef = None
                bNullifyOutputSRS = True

        elif EQUAL(args[iArg],"-t_srs") and iArg < nArgc-1:
            iArg = iArg + 1
            pszOutputSRSDef = args[iArg]
            bTransform = True

        elif EQUAL(args[iArg],"-spat") and iArg + 4 < nArgc:
            oRing = ogr.Geometry(ogr.wkbLinearRing)

            oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )
            oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+4]) )
            oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+4]) )
            oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+2]) )
            oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )

            poSpatialFilter = ogr.Geometry(ogr.wkbPolygon)
            poSpatialFilter.AddGeometry(oRing)
            iArg = iArg + 4

        elif EQUAL(args[iArg],"-where") and iArg < nArgc-1:
            iArg = iArg + 1
            pszWHERE = args[iArg]

        elif EQUAL(args[iArg],"-select") and iArg < nArgc-1:
            iArg = iArg + 1
            pszSelect = args[iArg]
            if pszSelect.find(',') != -1:
                papszSelFields = pszSelect.split(',')
            else:
                papszSelFields = pszSelect.split(' ')
            if papszSelFields[0] == '':
                papszSelFields = []

        elif EQUAL(args[iArg],"-simplify") and iArg < nArgc-1:
            iArg = iArg + 1
            eGeomOp = GeomOperation.SIMPLIFY_PRESERVE_TOPOLOGY
            dfGeomOpParam = float(args[iArg])

        elif EQUAL(args[iArg],"-segmentize") and iArg < nArgc-1:
            iArg = iArg + 1
            eGeomOp = GeomOperation.SEGMENTIZE
            dfGeomOpParam = float(args[iArg])

        elif EQUAL(args[iArg],"-fieldTypeToString") and iArg < nArgc-1:
            iArg = iArg + 1
            pszFieldTypeToString = args[iArg]
            if pszFieldTypeToString.find(',') != -1:
                tokens = pszFieldTypeToString.split(',')
            else:
                tokens = pszFieldTypeToString.split(' ')

            for token in tokens:
                if EQUAL(token,"Integer") or \
                    EQUAL(token,"Real") or \
                    EQUAL(token,"String") or \
                    EQUAL(token,"Date") or \
                    EQUAL(token,"Time") or \
                    EQUAL(token,"DateTime") or \
                    EQUAL(token,"Binary") or \
                    EQUAL(token,"IntegerList") or \
                    EQUAL(token,"RealList") or \
                    EQUAL(token,"StringList"):

                    papszFieldTypesToString.append(token)

                elif EQUAL(token,"All"):
                    papszFieldTypesToString = [ 'All' ]
                    break

                else:
                    print("Unhandled type for fieldtypeasstring option : %s " % token)
                    return Usage()

        elif EQUAL(args[iArg],"-progress"):
            bDisplayProgress = True

        #elif EQUAL(args[iArg],"-wrapdateline") )
        #{
        #    bWrapDateline = True;
        #}
        #
        elif EQUAL(args[iArg],"-clipsrc") and iArg < nArgc-1:

            bClipSrc = True
            if IsNumber(args[iArg+1]) and iArg < nArgc - 4:
                oRing = ogr.Geometry(ogr.wkbLinearRing)

                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )
                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+4]) )
                oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+4]) )
                oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+2]) )
                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )

                poClipSrc = ogr.Geometry(ogr.wkbPolygon)
                poClipSrc.AddGeometry(oRing)
                iArg = iArg + 4

            elif (len(args[iArg+1]) >= 7 and EQUAL(args[iArg+1][0:7],"POLYGON") ) or \
                  (len(args[iArg+1]) >= 12 and EQUAL(args[iArg+1][0:12],"MULTIPOLYGON") ) :
                poClipSrc = ogr.CreateGeometryFromWkt(args[iArg+1])
                if poClipSrc is None:
                    print("FAILURE: Invalid geometry. Must be a valid POLYGON or MULTIPOLYGON WKT\n")
                    return Usage()

                iArg = iArg + 1

            elif EQUAL(args[iArg+1],"spat_extent"):
                iArg = iArg + 1

            else:
                pszClipSrcDS = args[iArg+1]
                iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipsrcsql") and iArg < nArgc-1:
            pszClipSrcSQL = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipsrclayer") and iArg < nArgc-1:
            pszClipSrcLayer = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipsrcwhere") and iArg < nArgc-1:
            pszClipSrcWhere = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipdst") and iArg < nArgc-1:

            if IsNumber(args[iArg+1]) and iArg < nArgc - 4:
                oRing = ogr.Geometry(ogr.wkbLinearRing)

                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )
                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+4]) )
                oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+4]) )
                oRing.AddPoint_2D( float(args[iArg+3]), float(args[iArg+2]) )
                oRing.AddPoint_2D( float(args[iArg+1]), float(args[iArg+2]) )

                poClipDst = ogr.Geometry(ogr.wkbPolygon)
                poClipDst.AddGeometry(oRing)
                iArg = iArg + 4

            elif (len(args[iArg+1]) >= 7 and EQUAL(args[iArg+1][0:7],"POLYGON") ) or \
                  (len(args[iArg+1]) >= 12 and EQUAL(args[iArg+1][0:12],"MULTIPOLYGON") ) :
                poClipDst = ogr.CreateGeometryFromWkt(args[iArg+1])
                if poClipDst is None:
                    print("FAILURE: Invalid geometry. Must be a valid POLYGON or MULTIPOLYGON WKT\n")
                    return Usage()

                iArg = iArg + 1

            elif EQUAL(args[iArg+1],"spat_extent"):
                iArg = iArg + 1

            else:
                pszClipDstDS = args[iArg+1]
                iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipdstsql") and iArg < nArgc-1:
            pszClipDstSQL = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipdstlayer") and iArg < nArgc-1:
            pszClipDstLayer = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-clipdstwhere") and iArg < nArgc-1:
            pszClipDstWhere = args[iArg+1]
            iArg = iArg + 1

        elif EQUAL(args[iArg],"-explodecollections"):
            bExplodeCollections = True

        elif EQUAL(args[iArg],"-zfield") and iArg < nArgc-1:
            pszZField = args[iArg+1]
            iArg = iArg + 1

        elif args[iArg][0] == '-':
            return Usage()

        elif pszDestDataSource is None:
            pszDestDataSource = args[iArg]
        elif pszDataSource is None:
            pszDataSource = args[iArg]
        else:
            papszLayers.append (args[iArg] )

        iArg = iArg + 1

    if pszDataSource is None:
        return Usage()

    if bPreserveFID and bExplodeCollections:
        print("FAILURE: cannot use -preserve_fid and -explodecollections at the same time\n\n")
        return Usage()

    if bClipSrc and pszClipSrcDS is not None:
        poClipSrc = LoadGeometry(pszClipSrcDS, pszClipSrcSQL, pszClipSrcLayer, pszClipSrcWhere)
        if poClipSrc is None:
            print("FAILURE: cannot load source clip geometry\n" )
            return Usage()

    elif bClipSrc and poClipSrc is None:
        if poSpatialFilter is not None:
            poClipSrc = poSpatialFilter.Clone()
        if poClipSrc is None:
            print("FAILURE: -clipsrc must be used with -spat option or a\n" + \
                  "bounding box, WKT string or datasource must be specified\n")
            return Usage()

    if pszClipDstDS is not None:
        poClipDst = LoadGeometry(pszClipDstDS, pszClipDstSQL, pszClipDstLayer, pszClipDstWhere)
        if poClipDst is None:
            print("FAILURE: cannot load dest clip geometry\n" )
            return Usage()

# --------------------------------------------------------------------
#      Open data source.
# --------------------------------------------------------------------
    poDS = ogr.Open( pszDataSource, False )

# --------------------------------------------------------------------
#      Report failure
# --------------------------------------------------------------------
    if poDS is None:
        print("FAILURE:\n" + \
                "Unable to open datasource `%s' with the following drivers." % pszDataSource)

        for iDriver in range(ogr.GetDriverCount()):
            print("  ->  " + ogr.GetDriver(iDriver).GetName() )

        return False

# --------------------------------------------------------------------
#      Try opening the output datasource as an existing, writable
# --------------------------------------------------------------------
    poODS = None
    poDriver = None

    if bUpdate:
        poODS = ogr.Open( pszDestDataSource, True )
        if poODS is None:

            if bOverwrite or bAppend:
                poODS = ogr.Open( pszDestDataSource, False )
                if poODS is None:
                    # the datasource doesn't exist at all
                    bUpdate = False
                else:
                    poODS.delete()
                    poODS = None

            if bUpdate:
                print("FAILURE:\n" +
                        "Unable to open existing output datasource `%s'." % pszDestDataSource)
                return False

        elif len(papszDSCO) > 0:
            print("WARNING: Datasource creation options ignored since an existing datasource\n" + \
                    "         being updated." )

        if poODS is not None:
            poDriver = poODS.GetDriver()

# --------------------------------------------------------------------
#      Find the output driver.
# --------------------------------------------------------------------
    if not bUpdate:
        poDriver = ogr.GetDriverByName(pszFormat)
        if poDriver is None:
            print("Unable to find driver `%s'." % pszFormat)
            print( "The following drivers are available:" )

            for iDriver in range(ogr.GetDriverCount()):
                print("  ->  %s" % ogr.GetDriver(iDriver).GetName() )

            return False

        if poDriver.TestCapability( ogr.ODrCCreateDataSource ) == False:
            print( "%s driver does not support data source creation." % pszFormat)
            return False

# --------------------------------------------------------------------
#      Special case to improve user experience when translating
#      a datasource with multiple layers into a shapefile. If the
#      user gives a target datasource with .shp and it does not exist,
#      the shapefile driver will try to create a file, but this is not
#      appropriate because here we have several layers, so create
#      a directory instead.
# --------------------------------------------------------------------
        if EQUAL(poDriver.GetName(), "ESRI Shapefile") and \
           pszSQLStatement is None and \
           (len(papszLayers) > 1 or \
            (len(papszLayers) == 0 and poDS.GetLayerCount() > 1)) and \
            pszNewLayerName is None and \
            EQUAL(os.path.splitext(pszDestDataSource)[1], ".SHP") :

            try:
                os.stat(pszDestDataSource)
            except:
                try:
                    # decimal 493 = octal 0755. Python 3 needs 0o755, but
                    # this syntax is only supported by Python >= 2.6
                    os.mkdir(pszDestDataSource, 493)
                except:
                    print("Failed to create directory %s\n"
                          "for shapefile datastore.\n" % pszDestDataSource )
                    return False

# --------------------------------------------------------------------
#      Create the output data source.
# --------------------------------------------------------------------
        poODS = poDriver.CreateDataSource( pszDestDataSource, options = papszDSCO )
        if poODS is None:
            print( "%s driver failed to create %s" % (pszFormat, pszDestDataSource ))
            return False

# --------------------------------------------------------------------
#      Parse the output SRS definition if possible.
# --------------------------------------------------------------------
    if pszOutputSRSDef is not None:
        poOutputSRS = osr.SpatialReference()
        if poOutputSRS.SetFromUserInput( pszOutputSRSDef ) != 0:
            print( "Failed to process SRS definition: %s" % pszOutputSRSDef )
            return False

# --------------------------------------------------------------------
#      Parse the source SRS definition if possible.
# --------------------------------------------------------------------
    if pszSourceSRSDef is not None:
        poSourceSRS = osr.SpatialReference()
        if poSourceSRS.SetFromUserInput( pszSourceSRSDef ) != 0:
            print( "Failed to process SRS definition: %s" % pszSourceSRSDef )
            return False

# --------------------------------------------------------------------
#      For OSM file.
# --------------------------------------------------------------------
    bSrcIsOSM = poDS.GetDriver() is not None and \
                             poDS.GetDriver().GetName() == "OSM"
    nSrcFileSize = 0
    if bSrcIsOSM and poDS.GetName() != "/vsistdin/":
        sStat = gdal.VSIStatL(poDS.GetName())
        if sStat is not None:
            nSrcFileSize = sStat.size

# --------------------------------------------------------------------
#      Special case for -sql clause.  No source layers required.
# --------------------------------------------------------------------
    if pszSQLStatement is not None:
        if pszWHERE is not None:
            print( "-where clause ignored in combination with -sql." )
        if len(papszLayers) > 0:
            print( "layer names ignored in combination with -sql." )

        poResultSet = poDS.ExecuteSQL( pszSQLStatement, poSpatialFilter, \
                                        None )

        if poResultSet is not None:
            nCountLayerFeatures = 0
            if bDisplayProgress:
                if bSrcIsOSM:
                    pfnProgress = progress_func
                    pProgressArg = progress_data

                elif not poResultSet.TestCapability(ogr.OLCFastFeatureCount):
                    print( "Progress turned off as fast feature count is not available.")
                    bDisplayProgress = False

                else:
                    nCountLayerFeatures = poResultSet.GetFeatureCount()
                    pfnProgress = progress_func
                    pProgressArg = progress_data

# --------------------------------------------------------------------
#      Special case to improve user experience when translating into
#      single file shapefile and source has only one layer, and that
#      the layer name isn't specified
# --------------------------------------------------------------------
            if EQUAL(poDriver.GetName(), "ESRI Shapefile") and \
                pszNewLayerName is None:
                try:
                    mode = os.stat(pszDestDataSource).st_mode
                    if (mode & stat.S_IFDIR) == 0:
                        pszNewLayerName = os.path.splitext(os.path.basename(pszDestDataSource))[0]
                except:
                    pass


            psInfo = SetupTargetLayer(  poDS, \
                                        poResultSet,
                                        poODS, \
                                        papszLCO, \
                                        pszNewLayerName, \
                                        bTransform, \
                                        poOutputSRS, \
                                        bNullifyOutputSRS, \
                                        poSourceSRS, \
                                        papszSelFields, \
                                        bAppend, eGType, bPromoteToMulti, nCoordDim, bOverwrite, \
                                        papszFieldTypesToString, \
                                        bWrapDateline, \
                                        bExplodeCollections, \
                                        pszZField, \
                                        pszWHERE )

            poResultSet.ResetReading()

            if psInfo is None or not TranslateLayer( psInfo, poDS, poResultSet, poODS, \
                                poOutputSRS, bNullifyOutputSRS, \
                                eGType, bPromoteToMulti, nCoordDim, \
                                eGeomOp, dfGeomOpParam, \
                                nCountLayerFeatures, \
                                poClipSrc, poClipDst, \
                                bExplodeCollections, \
                                nSrcFileSize, None, \
                                pfnProgress, pProgressArg ):
                print(
                        "Terminating translation prematurely after failed\n" + \
                        "translation from sql statement." )

                return False

            poDS.ReleaseResultSet( poResultSet )


# --------------------------------------------------------------------
#      Special case for layer interleaving mode.
# --------------------------------------------------------------------
    elif bSrcIsOSM and gdal.GetConfigOption("OGR_INTERLEAVED_READING", None) is None:

        gdal.SetConfigOption("OGR_INTERLEAVED_READING", "YES")

        #if (bSplitListFields)
        #{
        #    fprintf( stderr, "FAILURE: -splitlistfields not supported in this mode\n" );
        #    exit( 1 );
        #}

        nSrcLayerCount = poDS.GetLayerCount()
        pasAssocLayers = [ AssociatedLayers() for i in range(nSrcLayerCount) ]

# --------------------------------------------------------------------
#      Special case to improve user experience when translating into
#      single file shapefile and source has only one layer, and that
#      the layer name isn't specified
# --------------------------------------------------------------------

        if EQUAL(poDriver.GetName(), "ESRI Shapefile") and \
           (len(papszLayers) == 1 or nSrcLayerCount == 1) and pszNewLayerName is None:
            try:
                mode = os.stat(pszDestDataSource).st_mode
                if (mode & stat.S_IFDIR) == 0:
                    pszNewLayerName = os.path.splitext(os.path.basename(pszDestDataSource))[0]
            except:
                pass

        if bDisplayProgress and bSrcIsOSM:
            pfnProgress = progress_func
            pProgressArg = progress_data

# --------------------------------------------------------------------
#      If no target layer specified, use all source layers.
# --------------------------------------------------------------------
        if len(papszLayers) == 0:
            papszLayers = [ None for i in range(nSrcLayerCount) ]
            for iLayer in range(nSrcLayerCount):
                poLayer = poDS.GetLayer(iLayer)
                if poLayer is None:
                    print("FAILURE: Couldn't fetch advertised layer %d!" % iLayer)
                    return False

                papszLayers[iLayer] = poLayer.GetName()
        else:
            if bSrcIsOSM:
                osInterestLayers = "SET interest_layers ="
                for iLayer in range(len(papszLayers)):
                    if iLayer != 0:
                        osInterestLayers = osInterestLayers + ","
                    osInterestLayers = osInterestLayers + papszLayers[iLayer]

                poDS.ExecuteSQL(osInterestLayers, None, None)

# --------------------------------------------------------------------
#      First pass to set filters and create target layers.
# --------------------------------------------------------------------
        for iLayer in range(nSrcLayerCount):
            poLayer = poDS.GetLayer(iLayer)
            if poLayer is None:
                print("FAILURE: Couldn't fetch advertised layer %d!" % iLayer)
                return False

            pasAssocLayers[iLayer].poSrcLayer = poLayer

            if CSLFindString(papszLayers, poLayer.GetName()) >= 0:
                if pszWHERE is not None:
                    if poLayer.SetAttributeFilter( pszWHERE ) != 0:
                        print("FAILURE: SetAttributeFilter(%s) on layer '%s' failed.\n" % (pszWHERE, poLayer.GetName()) )
                        if not bSkipFailures:
                            return False

                if poSpatialFilter is not None:
                    poLayer.SetSpatialFilter( poSpatialFilter )

                psInfo = SetupTargetLayer( poDS, \
                                           poLayer, \
                                           poODS, \
                                           papszLCO, \
                                           pszNewLayerName, \
                                           bTransform, \
                                           poOutputSRS, \
                                           bNullifyOutputSRS, \
                                           poSourceSRS, \
                                           papszSelFields, \
                                           bAppend, eGType, bPromoteToMulti, nCoordDim, bOverwrite, \
                                           papszFieldTypesToString, \
                                           bWrapDateline, \
                                           bExplodeCollections, \
                                           pszZField, \
                                           pszWHERE )

                if psInfo is None and not bSkipFailures:
                    return False

                pasAssocLayers[iLayer].psInfo = psInfo
            else:
                pasAssocLayers[iLayer].psInfo = None

# --------------------------------------------------------------------
#      Second pass to process features in a interleaved layer mode.
# --------------------------------------------------------------------
        bHasLayersNonEmpty = True
        while bHasLayersNonEmpty:
            bHasLayersNonEmpty = False

            for iLayer in range(nSrcLayerCount):
                poLayer = pasAssocLayers[iLayer].poSrcLayer
                psInfo = pasAssocLayers[iLayer].psInfo
                anReadFeatureCount = [0]

                if psInfo is not None:
                    if not TranslateLayer(psInfo, poDS, poLayer, poODS, \
                                        poOutputSRS, bNullifyOutputSRS,  \
                                        eGType, bPromoteToMulti, nCoordDim, \
                                        eGeomOp, dfGeomOpParam,  \
                                        0,  \
                                        poClipSrc, poClipDst,  \
                                        bExplodeCollections,  \
                                        nSrcFileSize,  \
                                        anReadFeatureCount, \
                                        pfnProgress, pProgressArg ) \
                        and not bSkipFailures:
                        print(
                                "Terminating translation prematurely after failed\n" + \
                                "translation of layer " + poLayer.GetName() + " (use -skipfailures to skip errors)")

                        return False
                else:
                    # No matching target layer : just consumes the features

                    poFeature = poLayer.GetNextFeature()
                    while poFeature is not None:
                        anReadFeatureCount[0] = anReadFeatureCount[0] + 1
                        poFeature = poLayer.GetNextFeature()

                if anReadFeatureCount[0] != 0:
                    bHasLayersNonEmpty = True

    else:

        nLayerCount = 0
        papoLayers = []

# --------------------------------------------------------------------
#      Process each data source layer.
# --------------------------------------------------------------------
        if len(papszLayers) == 0:
            nLayerCount = poDS.GetLayerCount()
            papoLayers = [None for i in range(nLayerCount)]
            iLayer = 0

            for iLayer in range(nLayerCount):
                poLayer = poDS.GetLayer(iLayer)

                if poLayer is None:
                    print("FAILURE: Couldn't fetch advertised layer %d!" % iLayer)
                    return False

                papoLayers[iLayer] = poLayer
                iLayer = iLayer + 1

# --------------------------------------------------------------------
#      Process specified data source layers.
# --------------------------------------------------------------------
        else:
            nLayerCount = len(papszLayers)
            papoLayers = [None for i in range(nLayerCount)]
            iLayer = 0

            for layername in papszLayers:
                poLayer = poDS.GetLayerByName(layername)

                if poLayer is None:
                    print("FAILURE: Couldn't fetch advertised layer %s!" % layername)
                    return False

                papoLayers[iLayer] = poLayer
                iLayer = iLayer + 1

        panLayerCountFeatures = [0 for i in range(nLayerCount)]
        nCountLayersFeatures = 0
        nAccCountFeatures = 0

        # First pass to apply filters and count all features if necessary
        for iLayer in range(nLayerCount):
            poLayer = papoLayers[iLayer]

            if pszWHERE is not None:
                if poLayer.SetAttributeFilter( pszWHERE ) != 0:
                    print("FAILURE: SetAttributeFilter(%s) failed." % pszWHERE)
                    if not bSkipFailures:
                        return False

            if poSpatialFilter is not None:
                poLayer.SetSpatialFilter( poSpatialFilter )

            if bDisplayProgress and not bSrcIsOSM:
                if not poLayer.TestCapability(ogr.OLCFastFeatureCount):
                    print("Progress turned off as fast feature count is not available.")
                    bDisplayProgress = False
                else:
                    panLayerCountFeatures[iLayer] = poLayer.GetFeatureCount()
                    nCountLayersFeatures += panLayerCountFeatures[iLayer]

        # Second pass to do the real job
        for iLayer in range(nLayerCount):
            poLayer = papoLayers[iLayer]

            if bDisplayProgress:
                if bSrcIsOSM:
                    pfnProgress = progress_func
                    pProgressArg = progress_data
                else:
                    pfnProgress = ScaledProgressFunc
                    pProgressArg = ( \
                            nAccCountFeatures * 1.0 / nCountLayersFeatures, \
                            (nAccCountFeatures + panLayerCountFeatures[iLayer]) * 1.0 / nCountLayersFeatures, \
                            progress_func, progress_data)

            nAccCountFeatures += panLayerCountFeatures[iLayer]

# --------------------------------------------------------------------
#      Special case to improve user experience when translating into
#      single file shapefile and source has only one layer, and that
#      the layer name isn't specified
# --------------------------------------------------------------------
            if EQUAL(poDriver.GetName(), "ESRI Shapefile") and \
                nLayerCount == 1 and pszNewLayerName is None:
                try:
                    mode = os.stat(pszDestDataSource).st_mode
                    if (mode & stat.S_IFDIR) == 0:
                        pszNewLayerName = os.path.splitext(os.path.basename(pszDestDataSource))[0]
                except:
                    pass


            psInfo = SetupTargetLayer( poDS, \
                                       poLayer, \
                                       poODS, \
                                       papszLCO, \
                                       pszNewLayerName, \
                                       bTransform, \
                                       poOutputSRS, \
                                       bNullifyOutputSRS, \
                                       poSourceSRS, \
                                       papszSelFields, \
                                       bAppend, eGType, bPromoteToMulti, nCoordDim, bOverwrite, \
                                       papszFieldTypesToString, \
                                       bWrapDateline, \
                                       bExplodeCollections, \
                                       pszZField, \
                                       pszWHERE )

            poLayer.ResetReading()

            if (psInfo is None or \
                not TranslateLayer( psInfo, poDS, poLayer, poODS, \
                                    poOutputSRS, bNullifyOutputSRS, \
                                    eGType, bPromoteToMulti, nCoordDim, \
                                    eGeomOp, dfGeomOpParam, \
                                    panLayerCountFeatures[iLayer], \
                                    poClipSrc, poClipDst, \
                                    bExplodeCollections, \
                                    nSrcFileSize, None, \
                                    pfnProgress, pProgressArg )) \
                and not bSkipFailures:
                print(
                        "Terminating translation prematurely after failed\n" + \
                        "translation of layer " + poLayer.GetLayerDefn().GetName() + " (use -skipfailures to skip errors)")

                return False

# --------------------------------------------------------------------
#      Close down.
# --------------------------------------------------------------------
    # We must explicitly destroy the output dataset in order the file
    # to be properly closed !
    poODS.Destroy()
    poDS.Destroy()

    return True

#**********************************************************************
#                               Usage()
#**********************************************************************

def Usage():

    print( "Usage: ogr2ogr [--help-general] [-skipfailures] [-append] [-update] [-gt n]\n" + \
            "               [-select field_list] [-where restricted_where] \n" + \
            "               [-progress] [-sql <sql statement>] \n" + \
            "               [-spat xmin ymin xmax ymax] [-preserve_fid] [-fid FID]\n" + \
            "               [-a_srs srs_def] [-t_srs srs_def] [-s_srs srs_def]\n" + \
            "               [-f format_name] [-overwrite] [[-dsco NAME=VALUE] ...]\n" + \
            "               [-simplify tolerance]\n" + \
            #// "               [-segmentize max_dist] [-fieldTypeToString All|(type1[,type2]*)]\n" + \
            "               [-fieldTypeToString All|(type1[,type2]*)] [-explodecollections] \n" + \
            "               dst_datasource_name src_datasource_name\n" + \
            "               [-lco NAME=VALUE] [-nln name] [-nlt type] [-dim 2|3] [layer [layer ...]]\n" + \
            "\n" + \
            " -f format_name: output file format name, possible values are:")

    for iDriver in range(ogr.GetDriverCount()):
        poDriver = ogr.GetDriver(iDriver)

        if poDriver.TestCapability( ogr.ODrCCreateDataSource ):
            print( "     -f \"" + poDriver.GetName() + "\"" )

    print( " -append: Append to existing layer instead of creating new if it exists\n" + \
            " -overwrite: delete the output layer and recreate it empty\n" + \
            " -update: Open existing output datasource in update mode\n" + \
            " -progress: Display progress on terminal. Only works if input layers have the \"fast feature count\" capability\n" + \
            " -select field_list: Comma-delimited list of fields from input layer to\n" + \
            "                     copy to the new layer (defaults to all)\n" + \
            " -where restricted_where: Attribute query (like SQL WHERE)\n" + \
            " -sql statement: Execute given SQL statement and save result.\n" + \
            " -skipfailures: skip features or layers that fail to convert\n" + \
            " -gt n: group n features per transaction (default 200)\n" + \
            " -spat xmin ymin xmax ymax: spatial query extents\n" + \
            " -simplify tolerance: distance tolerance for simplification.\n" + \
            #//" -segmentize max_dist: maximum distance between 2 nodes.\n" + \
            #//"                       Used to create intermediate points\n" + \
            " -dsco NAME=VALUE: Dataset creation option (format specific)\n" + \
            " -lco  NAME=VALUE: Layer creation option (format specific)\n" + \
            " -nln name: Assign an alternate name to the new layer\n" + \
            " -nlt type: Force a geometry type for new layer.  One of NONE, GEOMETRY,\n" + \
            "      POINT, LINESTRING, POLYGON, GEOMETRYCOLLECTION, MULTIPOINT,\n" + \
            "      MULTIPOLYGON, or MULTILINESTRING.  Add \"25D\" for 3D layers.\n" + \
            "      Default is type of source layer.\n" + \
            " -dim dimension: Force the coordinate dimension to the specified value.\n" + \
            " -fieldTypeToString type1,...: Converts fields of specified types to\n" + \
            "      fields of type string in the new layer. Valid types are : \n" + \
            "      Integer, Real, String, Date, Time, DateTime, Binary, IntegerList, RealList,\n" + \
            "      StringList. Special value All can be used to convert all fields to strings.")

    print(" -a_srs srs_def: Assign an output SRS\n"
        " -t_srs srs_def: Reproject/transform to this SRS on output\n"
        " -s_srs srs_def: Override source SRS\n"
        "\n"
        " Srs_def can be a full WKT definition (hard to escape properly),\n"
        " or a well known definition (i.e. EPSG:4326) or a file with a WKT\n"
        " definition." )

    return False

def CSLFindString(v, mystr):
    i = 0
    for strIter in v:
        if EQUAL(strIter, mystr):
            return i
        i = i + 1
    return -1

def IsNumber( pszStr):
    try:
        (float)(pszStr)
        return True
    except:
        return False

def LoadGeometry( pszDS, pszSQL, pszLyr, pszWhere):
    poGeom = None

    poDS = ogr.Open( pszDS, False )
    if poDS is None:
        return None

    if pszSQL is not None:
        poLyr = poDS.ExecuteSQL( pszSQL, None, None )
    elif pszLyr is not None:
        poLyr = poDS.GetLayerByName(pszLyr)
    else:
        poLyr = poDS.GetLayer(0)

    if poLyr is None:
        print("Failed to identify source layer from datasource.")
        poDS.Destroy()
        return None

    if pszWhere is not None:
        poLyr.SetAttributeFilter(pszWhere)

    poFeat = poLyr.GetNextFeature()
    while poFeat is not None:
        poSrcGeom = poFeat.GetGeometryRef()
        if poSrcGeom is not None:
            eType = wkbFlatten(poSrcGeom.GetGeometryType())

            if poGeom is None:
                poGeom = ogr.Geometry( ogr.wkbMultiPolygon )

            if eType == ogr.wkbPolygon:
                poGeom.AddGeometry( poSrcGeom )
            elif eType == ogr.wkbMultiPolygon:
                for iGeom in range(poSrcGeom.GetGeometryCount()):
                    poGeom.AddGeometry(poSrcGeom.GetGeometryRef(iGeom) )

            else:
                print("ERROR: Geometry not of polygon type." )
                if pszSQL is not None:
                    poDS.ReleaseResultSet( poLyr )
                poDS.Destroy()
                return None

        poFeat = poLyr.GetNextFeature()

    if pszSQL is not None:
        poDS.ReleaseResultSet( poLyr )
    poDS.Destroy()

    return poGeom


def wkbFlatten(x):
    return x & (~ogr.wkb25DBit)

#**********************************************************************
#                               SetZ()
#**********************************************************************

def SetZ (poGeom, dfZ ):

    if poGeom is None:
        return

    eGType = wkbFlatten(poGeom.GetGeometryType())
    if eGType == ogr.wkbPoint:
        poGeom.SetPoint(0, poGeom.GetX(), poGeom.GetY(), dfZ)

    elif eGType == ogr.wkbLineString or \
         eGType == ogr.wkbLinearRing:
        for i in range(poGeom.GetPointCount()):
            poGeom.SetPoint(i, poGeom.GetX(i), poGeom.GetY(i), dfZ)

    elif eGType == ogr.wkbPolygon or \
         eGType == ogr.wkbMultiPoint or \
         eGType == ogr.wkbMultiLineString or \
         eGType == ogr.wkbMultiPolygon or \
         eGType == ogr.wkbGeometryCollection:
        for i in range(poGeom.GetGeometryCount()):
            SetZ(poGeom.GetGeometryRef(i), dfZ)

#**********************************************************************
#                         SetupTargetLayer()
#**********************************************************************

def SetupTargetLayer( poSrcDS, poSrcLayer, poDstDS, papszLCO, pszNewLayerName, \
                    bTransform,  poOutputSRS, bNullifyOutputSRS, poSourceSRS, papszSelFields, \
                    bAppend, eGType, bPromoteToMulti, nCoordDim, bOverwrite, \
                    papszFieldTypesToString, bWrapDateline, \
                    bExplodeCollections, pszZField, pszWHERE) :

    if pszNewLayerName is None:
        pszNewLayerName = poSrcLayer.GetLayerDefn().GetName()

# --------------------------------------------------------------------
#      Setup coordinate transformation if we need it.
# --------------------------------------------------------------------
    poCT = None

    if bTransform:
        if poSourceSRS is None:
            poSourceSRS = poSrcLayer.GetSpatialRef()

        if poSourceSRS is None:
            print("Can't transform coordinates, source layer has no\n" + \
                    "coordinate system.  Use -s_srs to set one." )
            return None

        poCT = osr.CoordinateTransformation( poSourceSRS, poOutputSRS )
        if gdal.GetLastErrorMsg().find( 'Unable to load PROJ.4 library' ) != -1:
            poCT = None

        if poCT is None:
            pszWKT = None

            print("Failed to create coordinate transformation between the\n" + \
                "following coordinate systems.  This may be because they\n" + \
                "are not transformable, or because projection services\n" + \
                "(PROJ.4 DLL/.so) could not be loaded." )

            pszWKT = poSourceSRS.ExportToPrettyWkt( 0 )
            print( "Source:\n" + pszWKT )

            pszWKT = poOutputSRS.ExportToPrettyWkt( 0 )
            print( "Target:\n" + pszWKT )
            return None

# --------------------------------------------------------------------
#      Get other info.
# --------------------------------------------------------------------
    poSrcFDefn = poSrcLayer.GetLayerDefn()

    if poOutputSRS is None and not bNullifyOutputSRS:
        poOutputSRS = poSrcLayer.GetSpatialRef()

# --------------------------------------------------------------------
#      Find the layer.
# --------------------------------------------------------------------

    # GetLayerByName() can instantiate layers that would have been
    # 'hidden' otherwise, for example, non-spatial tables in a
    # PostGIS-enabled database, so this apparently useless command is
    # not useless. (#4012)
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    poDstLayer = poDstDS.GetLayerByName(pszNewLayerName)
    gdal.PopErrorHandler()
    gdal.ErrorReset()

    iLayer = -1
    if poDstLayer is not None:
        nLayerCount = poDstDS.GetLayerCount()
        for iLayer in range(nLayerCount):
            poLayer = poDstDS.GetLayer(iLayer)
            # The .cpp version compares on pointers directly, but we cannot
            # do this with swig object, so just compare the names.
            if poLayer is not None \
                and poLayer.GetName() == poDstLayer.GetName():
                break

        if (iLayer == nLayerCount):
            # Shouldn't happen with an ideal driver
            poDstLayer = None

# --------------------------------------------------------------------
#      If the user requested overwrite, and we have the layer in
#      question we need to delete it now so it will get recreated
#      (overwritten).
# --------------------------------------------------------------------
    if poDstLayer is not None and bOverwrite:
        if poDstDS.DeleteLayer( iLayer ) != 0:
            print("DeleteLayer() failed when overwrite requested." )
            return None

        poDstLayer = None

# --------------------------------------------------------------------
#      If the layer does not exist, then create it.
# --------------------------------------------------------------------
    if poDstLayer is None:
        if eGType == -2:
            eGType = poSrcFDefn.GetGeomType()

            n25DBit = eGType & ogr.wkb25DBit
            if bPromoteToMulti:
                if wkbFlatten(eGType) == ogr.wkbLineString:
                    eGType = ogr.wkbMultiLineString | n25DBit
                elif wkbFlatten(eGType) == ogr.wkbPolygon:
                    eGType = ogr.wkbMultiPolygon | n25DBit

            if bExplodeCollections:
                if wkbFlatten(eGType) == ogr.wkbMultiPoint:
                    eGType = ogr.wkbPoint | n25DBit
                elif wkbFlatten(eGType) == ogr.wkbMultiLineString:
                    eGType = ogr.wkbLineString | n25DBit
                elif wkbFlatten(eGType) == ogr.wkbMultiPolygon:
                    eGType = ogr.wkbPolygon | n25DBit
                elif wkbFlatten(eGType) == ogr.wkbGeometryCollection:
                    eGType = ogr.wkbUnknown | n25DBit

            if pszZField is not None:
                eGType = eGType | ogr.wkb25DBit

        if nCoordDim == 2:
            eGType = eGType & ~ogr.wkb25DBit
        elif nCoordDim == 3:
            eGType = eGType | ogr.wkb25DBit

        if poDstDS.TestCapability( ogr.ODsCCreateLayer ) == False:
            print("Layer " + pszNewLayerName + "not found, and CreateLayer not supported by driver.")
            return None

        gdal.ErrorReset()

        poDstLayer = poDstDS.CreateLayer( pszNewLayerName, poOutputSRS, \
                                            eGType, papszLCO )

        if poDstLayer is None:
            return None

        bAppend = False

# --------------------------------------------------------------------
#      Otherwise we will append to it, if append was requested.
# --------------------------------------------------------------------
    elif not bAppend:
        print("FAILED: Layer " + pszNewLayerName + "already exists, and -append not specified.\n" + \
                            "        Consider using -append, or -overwrite.")
        return None
    else:
        if len(papszLCO) > 0:
            print("WARNING: Layer creation options ignored since an existing layer is\n" + \
                    "         being appended to." )

# --------------------------------------------------------------------
#      Add fields.  Default to copy all field.
#      If only a subset of all fields requested, then output only
#      the selected fields, and in the order that they were
#      selected.
# --------------------------------------------------------------------

    # Initialize the index-to-index map to -1's
    nSrcFieldCount = poSrcFDefn.GetFieldCount()
    panMap = [ -1 for i in range(nSrcFieldCount) ]

    poDstFDefn = poDstLayer.GetLayerDefn()

    if papszSelFields is not None and not bAppend:

        nDstFieldCount = 0
        if poDstFDefn is not None:
            nDstFieldCount = poDstFDefn.GetFieldCount()

        for iField in range(len(papszSelFields)):

            iSrcField = poSrcFDefn.GetFieldIndex(papszSelFields[iField])
            if iSrcField >= 0:
                poSrcFieldDefn = poSrcFDefn.GetFieldDefn(iSrcField)
                oFieldDefn = ogr.FieldDefn( poSrcFieldDefn.GetNameRef(),
                                            poSrcFieldDefn.GetType() )
                oFieldDefn.SetWidth( poSrcFieldDefn.GetWidth() )
                oFieldDefn.SetPrecision( poSrcFieldDefn.GetPrecision() )

                if papszFieldTypesToString is not None and \
                    (CSLFindString(papszFieldTypesToString, "All") != -1 or \
                    CSLFindString(papszFieldTypesToString, \
                                ogr.GetFieldTypeName(poSrcFieldDefn.GetType())) != -1):

                    oFieldDefn.SetType(ogr.OFTString)

                # The field may have been already created at layer creation
                iDstField = -1
                if poDstFDefn is not None:
                    iDstField = poDstFDefn.GetFieldIndex(oFieldDefn.GetNameRef())
                if iDstField >= 0:
                    panMap[iSrcField] = iDstField
                elif poDstLayer.CreateField( oFieldDefn ) == 0:
                    # now that we've created a field, GetLayerDefn() won't return NULL
                    if poDstFDefn is None:
                        poDstFDefn = poDstLayer.GetLayerDefn()

                    # Sanity check : if it fails, the driver is buggy
                    if poDstFDefn is not None and \
                        poDstFDefn.GetFieldCount() != nDstFieldCount + 1:
                        print("The output driver has claimed to have added the %s field, but it did not!" %  oFieldDefn.GetNameRef() )
                    else:
                        panMap[iSrcField] = nDstFieldCount
                        nDstFieldCount = nDstFieldCount + 1

            else:
                print("Field '" + papszSelFields[iField] + "' not found in source layer.")
                if not bSkipFailures:
                    return None

        # --------------------------------------------------------------------
        # Use SetIgnoredFields() on source layer if available
        # --------------------------------------------------------------------

        # Here we differ from the ogr2ogr.cpp implementation since the OGRFeatureQuery
        # isn't mapped to swig. So in that case just don't use SetIgnoredFields()
        # to avoid issue raised in #4015
        if poSrcLayer.TestCapability(ogr.OLCIgnoreFields) and pszWHERE is None:
            papszIgnoredFields = []
            for iSrcField in range(nSrcFieldCount):
                pszFieldName = poSrcFDefn.GetFieldDefn(iSrcField).GetNameRef()
                bFieldRequested = False
                for iField in range(len(papszSelFields)):
                    if EQUAL(pszFieldName, papszSelFields[iField]):
                        bFieldRequested = True
                        break

                if pszZField is not None and EQUAL(pszFieldName, pszZField):
                    bFieldRequested = True

                # If source field not requested, add it to ignored files list
                if not bFieldRequested:
                    papszIgnoredFields.append(pszFieldName)

            poSrcLayer.SetIgnoredFields(papszIgnoredFields)

    elif not bAppend:

        nDstFieldCount = 0
        if poDstFDefn is not None:
            nDstFieldCount = poDstFDefn.GetFieldCount()

        for iField in range(nSrcFieldCount):

            poSrcFieldDefn = poSrcFDefn.GetFieldDefn(iField)
            oFieldDefn = ogr.FieldDefn( poSrcFieldDefn.GetNameRef(),
                                        poSrcFieldDefn.GetType() )
            oFieldDefn.SetWidth( poSrcFieldDefn.GetWidth() )
            oFieldDefn.SetPrecision( poSrcFieldDefn.GetPrecision() )

            if papszFieldTypesToString is not None and \
                (CSLFindString(papszFieldTypesToString, "All") != -1 or \
                CSLFindString(papszFieldTypesToString, \
                            ogr.GetFieldTypeName(poSrcFieldDefn.GetType())) != -1):

                oFieldDefn.SetType(ogr.OFTString)

            # The field may have been already created at layer creation
            iDstField = -1
            if poDstFDefn is not None:
                 iDstField = poDstFDefn.GetFieldIndex(oFieldDefn.GetNameRef())
            if iDstField >= 0:
                panMap[iField] = iDstField
            elif poDstLayer.CreateField( oFieldDefn ) == 0:
                # now that we've created a field, GetLayerDefn() won't return NULL
                if poDstFDefn is None:
                    poDstFDefn = poDstLayer.GetLayerDefn()

                # Sanity check : if it fails, the driver is buggy
                if poDstFDefn is not None and \
                    poDstFDefn.GetFieldCount() != nDstFieldCount + 1:
                    print("The output driver has claimed to have added the %s field, but it did not!" %  oFieldDefn.GetNameRef() )
                else:
                    panMap[iField] = nDstFieldCount
                    nDstFieldCount = nDstFieldCount + 1

    else:
        # For an existing layer, build the map by fetching the index in the destination
        # layer for each source field
        if poDstFDefn is None:
            print( "poDstFDefn == NULL.\n" )
            return None

        for iField in range(nSrcFieldCount):
            poSrcFieldDefn = poSrcFDefn.GetFieldDefn(iField)
            iDstField = poDstFDefn.GetFieldIndex(poSrcFieldDefn.GetNameRef())
            if iDstField >= 0:
                panMap[iField] = iDstField

    iSrcZField = -1
    if pszZField is not None:
        iSrcZField = poSrcFDefn.GetFieldIndex(pszZField)

    psInfo = TargetLayerInfo()
    psInfo.poDstLayer = poDstLayer
    psInfo.poCT = poCT
    #psInfo.papszTransformOptions = papszTransformOptions
    psInfo.panMap = panMap
    psInfo.iSrcZField = iSrcZField

    return psInfo

#**********************************************************************
#                           TranslateLayer()
#**********************************************************************

def TranslateLayer( psInfo, poSrcDS, poSrcLayer, poDstDS,  \
                    poOutputSRS, bNullifyOutputSRS, \
                    eGType, bPromoteToMulti, nCoordDim, eGeomOp, dfGeomOpParam, \
                    nCountLayerFeatures, \
                    poClipSrc, poClipDst, bExplodeCollections, nSrcFileSize, \
                    pnReadFeatureCount, pfnProgress, pProgressArg) :

    bForceToPolygon = False
    bForceToMultiPolygon = False
    bForceToMultiLineString = False

    poDstLayer = psInfo.poDstLayer
    #papszTransformOptions = psInfo.papszTransformOptions
    poCT = psInfo.poCT
    panMap = psInfo.panMap
    iSrcZField = psInfo.iSrcZField

    if poOutputSRS is None and not bNullifyOutputSRS:
        poOutputSRS = poSrcLayer.GetSpatialRef()

    if wkbFlatten(eGType) == ogr.wkbPolygon:
        bForceToPolygon = True
    elif wkbFlatten(eGType) == ogr.wkbMultiPolygon:
        bForceToMultiPolygon = True
    elif wkbFlatten(eGType) == ogr.wkbMultiLineString:
        bForceToMultiLineString = True

# --------------------------------------------------------------------
#      Transfer features.
# --------------------------------------------------------------------
    nFeaturesInTransaction = 0
    nCount = 0

    if nGroupTransactions > 0:
        poDstLayer.StartTransaction()

    while True:
        poDstFeature = None

        if nFIDToFetch != ogr.NullFID:

            #// Only fetch feature on first pass.
            if nFeaturesInTransaction == 0:
                poFeature = poSrcLayer.GetFeature(nFIDToFetch)
            else:
                poFeature = None

        else:
            poFeature = poSrcLayer.GetNextFeature()

        if poFeature is None:
            break

        nParts = 0
        nIters = 1
        if bExplodeCollections:
            poSrcGeometry = poFeature.GetGeometryRef()
            if poSrcGeometry is not None:
                eSrcType = wkbFlatten(poSrcGeometry.GetGeometryType())
                if eSrcType == ogr.wkbMultiPoint or \
                   eSrcType == ogr.wkbMultiLineString or \
                   eSrcType == ogr.wkbMultiPolygon or \
                   eSrcType == ogr.wkbGeometryCollection:
                        nParts = poSrcGeometry.GetGeometryCount()
                        nIters = nParts
                        if nIters == 0:
                            nIters = 1

        for iPart in range(nIters):
            nFeaturesInTransaction = nFeaturesInTransaction + 1
            if nFeaturesInTransaction == nGroupTransactions:
                poDstLayer.CommitTransaction()
                poDstLayer.StartTransaction()
                nFeaturesInTransaction = 0

            gdal.ErrorReset()
            poDstFeature = ogr.Feature( poDstLayer.GetLayerDefn() )

            if poDstFeature.SetFromWithMap( poFeature, 1, panMap ) != 0:

                if nGroupTransactions > 0:
                    poDstLayer.CommitTransaction()

                print("Unable to translate feature %d from layer %s" % (poFeature.GetFID() , poSrcLayer.GetName() ))

                return False

            if bPreserveFID:
                poDstFeature.SetFID( poFeature.GetFID() )

            poDstGeometry = poDstFeature.GetGeometryRef()
            if poDstGeometry is not None:

                if nParts > 0:
                    # For -explodecollections, extract the iPart(th) of the geometry
                    poPart = poDstGeometry.GetGeometryRef(iPart).Clone()
                    poDstFeature.SetGeometryDirectly(poPart)
                    poDstGeometry = poPart

                if iSrcZField != -1:
                    SetZ(poDstGeometry, poFeature.GetFieldAsDouble(iSrcZField))
                    # This will correct the coordinate dimension to 3
                    poDupGeometry = poDstGeometry.Clone()
                    poDstFeature.SetGeometryDirectly(poDupGeometry)
                    poDstGeometry = poDupGeometry


                if nCoordDim == 2 or nCoordDim == 3:
                    poDstGeometry.SetCoordinateDimension( nCoordDim )

                if eGeomOp == GeomOperation.SEGMENTIZE:
                    pass
                    #if (poDstFeature.GetGeometryRef() is not None and dfGeomOpParam > 0)
                    #    poDstFeature.GetGeometryRef().segmentize(dfGeomOpParam);
                elif eGeomOp == GeomOperation.SIMPLIFY_PRESERVE_TOPOLOGY and dfGeomOpParam > 0:
                    poNewGeom = poDstGeometry.SimplifyPreserveTopology(dfGeomOpParam)
                    if poNewGeom is not None:
                        poDstFeature.SetGeometryDirectly(poNewGeom)
                        poDstGeometry = poNewGeom

                if poClipSrc is not None:
                    poClipped = poDstGeometry.Intersection(poClipSrc)
                    if poClipped is None or poClipped.IsEmpty():
                        # Report progress
                        nCount = nCount +1
                        if pfnProgress is not None:
                            pfnProgress(nCount * 1.0 / nCountLayerFeatures, "", pProgressArg)
                        continue

                    poDstFeature.SetGeometryDirectly(poClipped)
                    poDstGeometry = poClipped

                if poCT is not None:
                    eErr = poDstGeometry.Transform( poCT )
                    if eErr != 0:
                        if nGroupTransactions > 0:
                            poDstLayer.CommitTransaction()

                        print("Failed to reproject feature %d (geometry probably out of source or destination SRS)." % poFeature.GetFID())
                        if not bSkipFailures:
                            return False

                elif poOutputSRS is not None:
                    poDstGeometry.AssignSpatialReference(poOutputSRS)

                if poClipDst is not None:
                    poClipped = poDstGeometry.Intersection(poClipDst)
                    if poClipped is None or poClipped.IsEmpty():
                        continue

                    poDstFeature.SetGeometryDirectly(poClipped)
                    poDstGeometry = poClipped

                if bForceToPolygon:
                    poDstFeature.SetGeometryDirectly(ogr.ForceToPolygon(poDstGeometry))

                elif bForceToMultiPolygon or \
                        (bPromoteToMulti and wkbFlatten(poDstGeometry.GetGeometryType()) == ogr.wkbPolygon):
                    poDstFeature.SetGeometryDirectly(ogr.ForceToMultiPolygon(poDstGeometry))

                elif bForceToMultiLineString or \
                        (bPromoteToMulti and wkbFlatten(poDstGeometry.GetGeometryType()) == ogr.wkbLineString):
                    poDstFeature.SetGeometryDirectly(ogr.ForceToMultiLineString(poDstGeometry))

            gdal.ErrorReset()
            if poDstLayer.CreateFeature( poDstFeature ) != 0 and not bSkipFailures:
                if nGroupTransactions > 0:
                    poDstLayer.RollbackTransaction()

                return False

        # Report progress
        nCount = nCount  + 1
        if pfnProgress is not None:
            if nSrcFileSize != 0:
                if (nCount % 1000) == 0:
                    poFCLayer = poSrcDS.ExecuteSQL("GetBytesRead()", None, None)
                    if poFCLayer is not None:
                        poFeat = poFCLayer.GetNextFeature()
                        if poFeat is not None:
                            pszReadSize = poFeat.GetFieldAsString(0)
                            nReadSize = int(pszReadSize)
                            pfnProgress(nReadSize * 1.0 / nSrcFileSize, "", pProgressArg)
                    poSrcDS.ReleaseResultSet(poFCLayer)
            else:
                pfnProgress(nCount * 1.0 / nCountLayerFeatures, "", pProgressArg)

        if pnReadFeatureCount is not None:
            pnReadFeatureCount[0] = nCount

    if nGroupTransactions > 0:
        poDstLayer.CommitTransaction()

    return True

# if __name__ == '__main__':
#     version_num = int(gdal.VersionInfo('VERSION_NUM'))
#     if version_num < 1800: # because of ogr.GetFieldTypeName
#         print('ERROR: Python bindings of GDAL 1.8.0 or later required')
#         sys.exit(1)

#     if not main(sys.argv):
#         sys.exit(1)
#     else:
#         sys.exit(0)
