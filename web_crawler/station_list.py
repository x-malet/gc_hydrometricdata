#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

import datetime
from urllib import request
from abc import ABCMeta, abstractmethod
import bs4
import requests, urllib3
import time
from collections import OrderedDict

STATION_LIST_BY_PROVINCE = "https://eau.ec.gc.ca/search/real_time_results_e.html"
PROVINCE_LIST_URL = "https://eau.ec.gc.ca/search/real_time_e.html"
HISTORICAL_STATION_LIST = "https://eau.ec.gc.ca/search/historical_results_e.html"


class HydrometricData(object):
	def __init__(self):
		pass

	def getStationsForProvince(self, provinceName: str):
		self._getRealTimeStationListByProvince(provinceName)
		self._getHistoricStationsListByProvince(provinceName)

	def getStationData(self, stationNumber: str):
		pass


class StationList(metaclass=ABCMeta):
	def __init__(self, province=None, mainURL=''):
		self.mainURL = mainURL
		self.province = province
		self.dict_url = {}
		self._webSiteContent = {}
		self.station_list = {}
		self._getProvinceList()

	def _getProvinceList(self):
		provinceInWebSite = bs4.BeautifulSoup(request.urlopen(PROVINCE_LIST_URL), "html.parser").find(
			id='province')
		self._webSiteContent['province_list'] = {}
		for values in provinceInWebSite.contents:
			if values != '\n':
				self._webSiteContent['province_list'][values.string] = values['value']

	@abstractmethod
	def getStationList(self):
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
		self.station_list = {}
		for row in stationInWebSite.find('table').tbody.find_all('tr'):
			# First value is ignored again
			rowData = [v.string for v in row.contents if v != '\n'][1:]
			self.station_list[rowData[stationNumberIndex]] = rowData[stationNameIndex]

	@property
	def province_list(self):
		return self._webSiteContent['province_list']

	@property
	def webSiteContent(self):
		return self._webSiteContent


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
		super().__init__(province, STATION_LIST_BY_PROVINCE)
		self.dict_url = {
			'search_type': 'province',
			'province': self.province_list[self.province],
		}

		self.getStationList()

	def getStationList(self):
		super(RealTimeStationList, self).getStationList()


if __name__ == '__main__':
	from web_crawler.station import *

	webStation = HistoricalStationList('Quebec')
	print(webStation.station_list)
	for station in webStation.station_list:
		hist_station = HistoricalStation(station)
		print(station)
		print(hist_station.stationInformation['longitude'])
		print(hist_station.stationInformation['latitude'])
