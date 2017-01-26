#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

from abc import ABCMeta, abstractmethod
from urllib import request

import bs4
import datetime
import requests

HYDROMETRIC_PROVINCE_LIST = "https://eau.ec.gc.ca/search/real_time_e.html"
REAL_TIME_STATION_LIST_URL = "https://eau.ec.gc.ca/search/real_time_results_e.html"
HISTORICAL_STATION_LIST_URL = "https://eau.ec.gc.ca/search/historical_results_e.html"

HISTORICAL_DATA_KEY = 'historic_data'
REAL_TIME_DATA_KEY = 'real_time_data'

WEATHER_STATION_LIST_URL = "http://climate.weather.gc.ca/historical_data/search_historic_data_stations_e.html"
WEATHER_STATION_PROVINCE_LIST = "http://climate.weather.gc.ca/historical_data/search_historic_data_e.html"


class StationList(metaclass=ABCMeta):
    def __init__(self, province=None, mainURL=''):
        self.mainURL = mainURL
        self.province = province
        self.dict_url = {}  # dict that have to be completed before running getStationList
        self._webSiteContent = {}
        self._getProvinceList()

    def _getProvinceList(self):
        provinceInWebSite = bs4.BeautifulSoup(request.urlopen(HYDROMETRIC_PROVINCE_LIST), "html.parser").find(
            id='province')
        self._webSiteContent['province_list'] = {}
        for values in provinceInWebSite.contents:
            if values != '\n':
                self._webSiteContent['province_list'][values.string] = values['value']

    @abstractmethod
    def getStationList(self):
        assert self.dict_url != {}, 'The dict have to be completed before running this method'

        req = requests.get(self.mainURL,
                           params=self.dict_url,
                           cookies={'disclaimer': 'agree'},
                           verify=False)

        stationInWebSite = bs4.BeautifulSoup(
            req.text, "html.parser")

        # Making the header. first value is set ignored because it's a check box
        tableHeader = [v.string for v in stationInWebSite.find('table').thead.tr.contents if (v != '\n')][1:]
        stationNumberIndex = tableHeader.index('Station Number')
        stationNameIndex = tableHeader.index('Station Name')
        self._webSiteContent['station_list'] = {}

        for row in stationInWebSite.find('table').tbody.find_all('tr'):
            # First value is ignored again
            rowData = [v.string for v in row.contents if v != '\n'][1:]
            self._webSiteContent['station_list'][rowData[stationNumberIndex]] = rowData[stationNameIndex]

    @property
    def province_list(self):
        return self._webSiteContent['province_list']

    @property
    def webSiteContent(self):
        return self._webSiteContent

    @property
    def station_list(self):
        return self._webSiteContent['station_list']


class HistoricalHydrometricStationList(StationList):
    def __init__(self, province=None):
        super().__init__(province, HISTORICAL_STATION_LIST_URL)
        self.dict_url = {
            'search_type': 'province',
            'province': self.province_list[self.province],
            'start_year': '1850',
            'end_year': datetime.date.today().year,
            'minimum_years': ''
        }
        self.getStationList()

    def getStationList(self):
        super(HistoricalHydrometricStationList, self).getStationList()


class RealTimeHydrometricStationList(StationList):
    def __init__(self, province=None):
        super().__init__(province, REAL_TIME_STATION_LIST_URL)
        self.dict_url = {
            'search_type': 'province',
            'province': self.province_list[self.province],
        }

        self.getStationList()

    def getStationList(self):
        super(RealTimeHydrometricStationList, self).getStationList()


class WeatherStationList(StationList):
    def __init__(self, province=None):
        super().__init__(province, WEATHER_STATION_LIST_URL)

    def _getProvinceList(self):
        r = requests.get(WEATHER_STATION_PROVINCE_LIST)
        print(r.url)
        provinceInWebSite = bs4.BeautifulSoup(request.urlopen(WEATHER_STATION_PROVINCE_LIST), "html.parser").find(
            id='province')

        self._webSiteContent['province_list'] = {}
        for value in provinceInWebSite.find('select', {'id': 'lstProvince'}):
            if isinstance(value, bs4.element.Tag):
                if value.string != 'All':
                    self._webSiteContent['province_list'][value.string] = value['value']

    def makeRequestDictForProximitySearch(self, xdeg, xmin, xsec, ydeg, ymin, ysec, radius):
        self.dict_url = {
            'searchType': "stnProx",
            'timeframe': '1',
            'txtRadius': str(radius),
            'selCity': '',
            'selPark': '',
            'optProxType': "custom",
            'txtCentralLatDeg': str(xdeg),
            'txtCentralLatMin': str(xmin),
            'txtCentralLatSec': str(xsec),
            'txtCentralLongDeg': str(ydeg),
            'txtCentralLongMin': str(ymin),
            'txtCentralLongSec': str(ysec),
            'optLimit': "yearRange",
            'StartYear': '1840',
            'EndYear': str(datetime.datetime.now().year),
            'Year': str(datetime.datetime.now().year),
            'Month': str(datetime.datetime.now().month),
            'Day': str(datetime.datetime.now().day),
            'selRowPerPage': 100
        }

    def makeRequestDictForProvinceSearch(self, provinceName):

        self.dict_url = {
            'searchType': "stnProx",
            'timeframe': '1',
            'lstProvince': self.province_list[self.province],
            'optLimit': "yearRange",
            'StartYear': '1840',
            'EndYear': str(datetime.datetime.now().year),
            'Year': str(datetime.datetime.now().year),
            'Month': str(datetime.datetime.now().month),
            'Day': str(datetime.datetime.now().day)
        }

    def getStationList(self):
        pass


if __name__ == '__main__':
    # wstl = WeatherStationList('Quebec')
    # print(wstl.province_list)
    r = requests.get("http://climate.weather.gc.ca/historical_data/search_historic_data_stations_e.html?searchType=stnProv&lstProvince=QC&StartYear=1840&EndYear=2017&Year=2017&Month=1&Day=24")
    bsFile = bs4.BeautifulSoup(r.text, 'html.parser')
    for tag in bsFile.find('form',{'action':'/climate_data/interform_e.html'}).find_all('input'):
        # print(tag)
        if 'name' in tag.attrs and tag['name'] == 'StationID':
            print(tag, tag['value'])

