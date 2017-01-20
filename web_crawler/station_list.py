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
	STATION_DATA_URL = "https://eau.ec.gc.ca/report/real_time_e.html"
	HISTORICAL_STATION_DATA = "https://eau.ec.gc.ca/report/historical_e.html"
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

	def getRequestDict(self, stationNumber=None, dataType='Real-Time'):
		delta = datetime.datetime(2017, 1, 19) - datetime.datetime(2015, 7, 19)

		if dataType != 'Real-Time':
			returnDict = {
				'stn': stationNumber,
				'dataType': dataType,
				'mode': 'Table',
				'y1Max': 1, 'y1Min': 1,
				'results_type': 'historical',
				'type': "h2oArc"
			}
		else:
			returnDict = {
				'endDate': datetime.datetime.now().strftime('%Y-%m-%d'),
				'startDate': (datetime.datetime.now() - delta).strftime('%Y-%m-%d'),
				'stn': stationNumber,
				'dataType': dataType,
				'mode': 'Table',
				'y1Max': 1, 'y1Min': 1
			}
		return returnDict

	def getStationData(self, stationNumber: str):
		self.station_list[stationNumber]['web_site_info'] = self.getStationInformation(stationNumber)
		try:
			self.station_list[stationNumber]['real_time_data'] = self.getStationRealTimeData(stationNumber)
		except AttributeError:
			self.station_list[stationNumber]['real_time_data'] = {}
		self.station_list[stationNumber]['historical_data'] = self.getStationHistoricalData(stationNumber)

	def getRealTimeAvaibleParameters(self, stationNumber: str):
		parameters = {}

		r = requests.get(self.STATION_DATA_URL, params={'stn': stationNumber}, cookies={'disclaimer': 'agree'},
						 verify=False)

		webSiteContent = bs4.BeautifulSoup(r.text, "html.parser")

		for ele in webSiteContent.find_all('select'):
			if ele.get('id') == 'selectTypey1':
				for option in ele.find_all('option'):
					parameters[option.string] = option.attrs['value']
		return parameters

	def getStationInformation(self, stationNumber: str):

		r = requests.get(self.STATION_DATA_URL,
						 params={'stn': stationNumber},
						 cookies={'disclaimer': 'agree'},
						 verify=False)
		stationDataInWebSite = bs4.BeautifulSoup(r.text, "html.parser")
		try:
			stationDataInWebSite.find('div', {'class': 'metadata'}) \
				.find_all('div', {'class': 'col-md-6 col-sm-6 col-xs-6'})
		except AttributeError:
			r = requests.get(self.HISTORICAL_STATION_DATA,
							 params={'stn': stationNumber},
							 cookies={'disclaimer': 'agree'},
							 verify=False)
			stationDataInWebSite = bs4.BeautifulSoup(r.text, "html.parser")

		station_information = {}
		currentWebID = ""
		for ele in stationDataInWebSite.find('div', {'class': 'metadata'}) \
				.find_all('div', {'class': 'col-md-6 col-sm-6 col-xs-6'}):
			try:
				# get the row id
				currentWebID = ele['id']
			except KeyError:
				# if no ID on the row, take the data
				if ele['aria-labelledby'] == currentWebID:
					# transform location data from deg, min,sec to deg
					if len(ele.contents) > 2:
						station_information[currentWebID] = float(ele.contents[0]) + \
															float(ele.contents[2].string) / 60 + \
															float(ele.contents[4].string) / 3600
					else:
						station_information[currentWebID] = ele.contents[0].string
		return station_information

	def getStationRealTimeData(self, stationNumber: str):
		stationData = {}
		# get avaible parameters for the station
		stationParameters = self.getRealTimeAvaibleParameters(stationNumber)
		# iterate for each station
		for params in stationParameters:
			stationData[params] = {}
			newDict = self.getRequestDict(stationNumber)
			newDict['prm1'] = stationParameters[params]
			print('fetching ' + params)
			# Make the request with the station parameter
			r = requests.get(self.STATION_DATA_URL, params=newDict, cookies={'disclaimer': 'agree'},
							 verify=False)

			stationDataInWebSite = bs4.BeautifulSoup(r.text, "html.parser")

			# get the table header
			stationData[params]['header'] = []
			for ele in stationDataInWebSite.find('table').find('thead').find('tr').find_all('th'):
				stationData[params]['header'].append(ele.contents[0].string.replace('\t', '').replace('\n', ''))
			# Get the data
			stationData[params]['data'] = []
			for data in stationDataInWebSite.find('table').find('tbody').find_all('tr'):
				stationData[params]['data'].append([rowData
													for dat in data.find_all('td')
													for rowData in dat])
		return stationData

	def getHistoricalAvaibleParameters(self, stationNumber: str):
		parameters = []

		r = requests.get(self.HISTORICAL_STATION_DATA,
						 params={'stn': stationNumber}, cookies={'disclaimer': 'agree'},
						 verify=False)
		webSiteContent = bs4.BeautifulSoup(r.text, "html.parser")

		for ele in webSiteContent.find_all('select'):
			if ele.get('id') == 'selectDataType':
				for option in ele.find_all('option'):
					parameters.append(option.attrs['value'])
		return parameters

	def getHistoricalAvaibleYearForParameter(self, stationNumber: str):
		"""
		Method that return a dict with

		:param stationNumber:
		:return: dict(PARAM) = [LIST_OF_YEARS_FOR_PARAM]
		"""
		historic_params = self.getHistoricalAvaibleParameters(stationNumber)
		returnDict = {}
		for params in historic_params:
			r = requests.get(self.HISTORICAL_STATION_DATA,
							 params={
								 'stn': stationNumber,
								 'parameterType': params
							 },
							 cookies={'disclaimer': 'agree'},
							 verify=False)
			webSiteContent = bs4.BeautifulSoup(r.text, "html.parser")
			returnDict[params] = []
			for ele in webSiteContent.find_all('select'):
				if ele.get('id') == 'selectYear':
					for option in ele.find_all('option'):
						returnDict[params].append(option.attrs['value'])
		return returnDict

	def extractHistoricalData(self, webSiteContent: bs4.BeautifulSoup):
		"""
		this method is executed for each year for each parameter
		:param webSiteContent:
		:return:
		"""
		# gettings parameter unit
		unit = ""
		for s in webSiteContent \
				.find('main') \
				.find('h2') \
				.find('abbr').contents:
			unit += s.string

		# Fetching parameters legend
		parameter_legend = {}
		for item in webSiteContent \
				.find('main') \
				.find('ul', {'class': 'legend'}) \
				.find_all('li'):
			params_list = item.string.split(' = ')
			parameter_legend[params_list[0]] = params_list[1]

		# extract data
		dict_historic_data = {}
		year = int(webSiteContent.find('main').find('h2').contents[0][:4])
		dict_historic_data[year] = {}
		dict_historic_data[year]['unit'] = unit
		# make empty list for each month
		for mth in range(1, 13):
			dict_historic_data[year][mth] = []
		# fetch data
		for ele in webSiteContent.find('table').find('tbody').find_all('tr'):
			day = int(ele.find('th').string.replace('\n', '').replace('\t', ''))
			for month, value in enumerate(ele.find_all('td')):
				date = ""
				try:
					# get date first. If the day don't exist, GoTo ValueError ==> pass
					date = datetime.date(year, month + 1, day)
					# if the cell have a legend
					if search(r'[A-Z]', value.string):
						dict_historic_data[year][month + 1].append(
							[date.strftime('%Y-%m-%d'),
							 split(r' *', value.string)[0], parameter_legend[split(r' *', value.string)[1]]])
					else:
						dict_historic_data[year][month + 1].append(
							[date.strftime('%Y-%m-%d'), value.string.replace(' ', '')])
				except ValueError:
					pass

		return dict_historic_data

	def getStationHistoricalData(self, stationNumber: str):
		historical_dict = self.getHistoricalAvaibleYearForParameter(stationNumber)
		historical_data = {}
		for parameter in historical_dict:
			historical_data[parameter] = {}
			newDict = self.getRequestDict(stationNumber, 'Daily')
			newDict.update({'parameterType': parameter})
			print('FETCHING PARAMETER ' + parameter)

			for year in historical_dict[parameter]:
				newDict.update({'year': year})
				print('FETCHING YEAR ' + str(year))

				r = requests.get(self.HISTORICAL_STATION_DATA,
								 params=newDict, cookies={'disclaimer': 'agree'},
								 verify=False)
				webSiteContent = bs4.BeautifulSoup(r.text, "html.parser")
				print(r.url)
				historical_data[parameter].update(self.extractHistoricalData(webSiteContent))
		print('END OF FETCHING')
		return historical_data

	@property
	def station_list(self):
		return self._webSiteContent['station_list']

	@property
	def province_list(self):
		return self._webSiteContent['province_list']

	@property
	def webSiteContent(self):
		return self._webSiteContent


if __name__ == '__main__':
	webStation = StationList()
	webStation.getStationsForProvince('Quebec')
	webStation.getStationData('02PJ035')

	print(webStation.station_list['02PJ035']['historical_data']['Flow'][1977][5])
