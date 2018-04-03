# -*- coding: utf-8 -*-
# --------------------------------------------------------
#    __init__ - HCMGIS init file
#
#    begin                : 01/02/2018
#    copyright            : 2018 by Quach Dong Thang
#    email                : quachdongthang@gmail.com
#   
# --------------------------------------------------------
def classFactory(iface):
	from .hcmgis_menu import hcmgis_menu
	return hcmgis_menu(iface)

