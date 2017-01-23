#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

from abc import ABCMeta, abstractmethod
from urllib import request

import bs4, datetime, requests

PROVINCE_LIST = "https://eau.ec.gc.ca/search/real_time_e.html"
REAL_TIME_STATION_LIST = "https://eau.ec.gc.ca/search/real_time_results_e.html"
HISTORICAL_STATION_LIST = "https://eau.ec.gc.ca/search/historical_results_e.html"

HISTORICAL_DATA_KEY = 'historic_data'
REAL_TIME_DATA_KEY = 'real_time_data'




class StationList(metaclass=ABCMeta):
    def __init__(self, province=None, mainURL=''):
        self.mainURL = mainURL
        self.province = province
        self.dict_url = {}  # dict that have to be completed before running getStationList
        self._webSiteContent = {}
        self._getProvinceList()

    def _getProvinceList(self):
        provinceInWebSite = bs4.BeautifulSoup(request.urlopen(PROVINCE_LIST), "html.parser").find(
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


class HistoricalStationList(StationList):
    def __init__(self, province=None):
        super().__init__(province, HISTORICAL_STATION_LIST)
        self.dict_url = {
            'search_type': 'province',
            'province': self.province_list[self.province],
            'start_year': '1850',
            'end_year': datetime.date.today().year,
            'minimum_years': ''
        }
        self.getStationList()

    def getStationList(self):
        super(HistoricalStationList, self).getStationList()


class RealTimeStationList(StationList):
    def __init__(self, province=None):
        super().__init__(province, REAL_TIME_STATION_LIST)
        self.dict_url = {
            'search_type': 'province',
            'province': self.province_list[self.province],
        }

        self.getStationList()

    def getStationList(self):
        super(RealTimeStationList, self).getStationList()


