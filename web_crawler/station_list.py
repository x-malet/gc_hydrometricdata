#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-19'
__description__ = " "
__version__ = '1.0'

import datetime
from urllib import request

import bs4
import requests
import time


class StationList(object):
    STATION_LIST_BY_PROVINCE = "https://eau.ec.gc.ca/search/real_time_results_e.html?search_type=province&province={}"
    PROVINCE_LIST_URL = "https://eau.ec.gc.ca/search/real_time_e.html"
    STATION_DATA_URL = "https://eau.ec.gc.ca/report/real_time_e.html?mode=Table&type=&startDate={start_date}&endDate={today}&stn={stn}&dataType=Real-Time"
    HYSTORICAL_STATION_DATA = "https://eau.ec.gc.ca/report/historical_f.html?stn={}&mode=Table&type=h2oArc&results_type=historical&dataType=Daily&parameterType=Level&year={}&y1Max=1&y1Min=1"
    HISTORICAL_STATION_LIST = "https://eau.ec.gc.ca/search/historical_results_f.html?search_type=province&province={}&start_year=1850&end_year=2017&minimum_years="

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

    def getStationListByProvince(self, provinceName):
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

    def getStationData(self, stationNumber):
        try:
            delta = datetime.datetime(2017, 1, 19) - datetime.datetime(2015, 7, 19)

            dict_url = {'today': datetime.datetime.now().strftime('%Y-%m-%d'),
                        'start_date': (datetime.datetime.now() - delta).strftime('%Y-%m-%d'),
                        'stn': self.station_list[stationNumber]['Station Number']}

            url = self.STATION_DATA_URL.format(**dict_url)
            r = requests.get(url, cookies={'disclaimer': 'agree'}, verify=False)
            html_page = r.text
            stationDataInWebSite = bs4.BeautifulSoup(html_page, "html.parser")

            self.station_list[stationNumber]['web_site_info'] = self.getStationInformation(stationDataInWebSite)
            self.station_list[stationNumber]['real_time_data'] = self.getStationRealTimeData(stationDataInWebSite)

        except KeyError as e:
            print(e)
            raise KeyError('Bad Station Number input')

    def getStationInformation(self, webSiteContent: bs4.BeautifulSoup):
        station_information = {}
        currentWebID = ""
        for ele in webSiteContent.find('div', {'class': 'metadata'}) \
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

    def getStationRealTimeData(self, webSiteContent):

        stationData = {}
        stationData['header'] = []
        stationData['station_data'] = []
        webSite = webSiteContent
        for ele in webSite.find('table').find('thead').find('tr').find_all('th'):
            stationData['header'].append(ele.contents[0].string.replace('\t', '').replace('\n', ''))

        for data in webSite.find('table').find('tbody').find_all('tr'):
            stationData['station_data'].append([rowData
                                                for dat in data.find_all('td')
                                                for rowData in dat])
        return stationData

    def getStationHistoricalData(self):
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


if __name__ == '__main__':
    webStation = StationList()
    webStation.getStationListByProvince('New Brunswick')
    webStation.getStationData('01AP003')

    print(len(webStation.station_list['01AP003']['real_time_data']['station_data']))
