#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

import bs4
import datetime
import requests
from re import search, split
from web_crawler.abstractstation import AbstractWeatherStation

WEATHER_STATION_DATA_URL = "http://climate.weather.gc.ca/climate_data/daily_data_e.html"


dict = """
hlyRange:%7C
dlyRange:1998-02-01%7C2007-11-30
mlyRange:1998-04-01%7C2007-11-01
StationID:10700
Prov:AB
urlExtension:_e.html
searchType:stnProv
optLimit:yearRange
StartYear:1840
EndYear:2017
selRowPerPage:100
Line:0
Month:11
Day:23
lstProvince:
timeframe:2
Year:2007
"""