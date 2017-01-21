#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

import datetime
from urllib import request

import bs4
from re import search, split
import requests, urllib3
import time


class StationList(object):
	STATION_LIST_BY_PROVINCE = "https://eau.ec.gc.ca/search/real_time_results_e.html?search_type=province&province={}"
	PROVINCE_LIST_URL = "https://eau.ec.gc.ca/search/real_time_e.html"
	HISTORICAL_STATION_LIST = "https://eau.ec.gc.ca/search/historical_results_e.html?search_type=province&province={}&start_year=1850&end_year=2017&minimum_years="

	def __init__(self):
		self._webSiteContent = {}
		self._getProvinceList()

	def _getProvinceList(self):
		provinceInWebSite = bs4.BeautifulSoup(request.urlopen(self.PROVINCE_LIST_URL), "html.parser").find(
			id='province')
		self._webSiteContent['province_list'] = {}
		for values in provinceInWebSite.contents:
			if values != '\n':
				self._webSiteContent['province_list'][values.string] = values['value']

	def getStationsForProvince(self, provinceName: str):
		self._getRealTimeStationListByProvince(provinceName)
		self._getHistoricStationsListByProvince(provinceName)

	def _getRealTimeStationListByProvince(self, provinceName: str):
		self._webSiteContent['station_list'] = {}

		stationInWebSite = bs4.BeautifulSoup(
			request.urlopen(
				self.STATION_LIST_BY_PROVINCE.format(self._webSiteContent['province_list'][provinceName])),
			"html.parser")

		# Making the header. first value is set ignored because it's a check box
		tableHeader = [v.string for v in stationInWebSite.find('table').thead.tr.contents if (v != '\n')][1:]
		stationNumberIndex = tableHeader.index('Station Number')
		for data in stationInWebSite.find('table').tbody.find_all('tr'):
			# First value is ignored again
			rowData = [v.string for v in data.contents if v != '\n'][1:]
			# Station number used as a key
			self._webSiteContent['station_list'][rowData[stationNumberIndex]] = {}
			# Adding data to the dict
			for index, value in enumerate(rowData):
				self._webSiteContent['station_list'][rowData[stationNumberIndex]][tableHeader[index]] = value

	def _getHistoricStationsListByProvince(self, provinceName: str):
		stationInWebSite = bs4.BeautifulSoup(
			request.urlopen(
				self.HISTORICAL_STATION_LIST.format(self._webSiteContent['province_list'][provinceName])),
			"html.parser")
		# Making the header. first value is set ignored because it's a check box
		tableHeader = [v.string for v in stationInWebSite.find('table').thead.tr.contents if (v != '\n')][1:]
		stationNumberIndex = tableHeader.index('Station Number')
		for data in stationInWebSite.find('table').tbody.find_all('tr'):
			# First value is ignored again
			rowData = [v.string for v in data.contents if v != '\n'][1:]
			# Station number used as a key
			if rowData[stationNumberIndex] not in self.station_list.keys():
				self._webSiteContent['station_list'][rowData[stationNumberIndex]] = {}
			# Adding data to the dict
			for index, value in enumerate(rowData):
				self._webSiteContent['station_list'][rowData[stationNumberIndex]][tableHeader[index]] = value



	def getStationData(self, stationNumber: str):
		pass
	@property
	def station_list(self):
		return self._webSiteContent['station_list']

	@property
	def province_list(self):
		return self._webSiteContent['province_list']

	@property
	def webSiteContent(self):
		return self._webSiteContent

class HistoricalStationList(object):
	pass


if __name__ == '__main__':
	webStation = StationList()
	webStation.getStationsForProvince('Quebec')
	webStation.getStationData('02PJ035')

	print(webStation.station_list['02PJ035']['historical_data']['Flow'][1977][5])
