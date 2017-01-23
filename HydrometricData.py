#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'xmalet'
__date__ = '2017-01-23'
__description__ = " "
__version__ = '1.0'

from web_crawler.station import Station
from web_crawler.station_list import *

HISTORICAL_STATION_DATA = "https://eau.ec.gc.ca/report/historical_e.html"
REAL_TIME_STATION_DATA_URL = "https://eau.ec.gc.ca/report/real_time_e.html"

class HydrometricDataInterface(object):
    def __init__(self):
        self._historic_station = None
        self._real_time_station = None
        self._stationData = {}

    def getStationsForProvince(self, provinceName: str):
        self._historic_station = HistoricalStationList(provinceName)
        self._real_time_station = RealTimeStationList(provinceName)

    def _extractStationData(self, stationNumber: str):
        if self.isStationPresent(stationNumber):
            self._stationData[stationNumber] = {}
            if stationNumber in self.getStationInBoth():
                print('station have historic and real-time data')
                self._stationData[stationNumber][HISTORICAL_DATA_KEY] = HistoricalStation(stationNumber)
                self._stationData[stationNumber][REAL_TIME_DATA_KEY] = RealTimeStation(stationNumber)
            else:
                if stationNumber in self.historicStationList:
                    print('station have historic data only')

                    self._stationData[stationNumber][HISTORICAL_DATA_KEY] = HistoricalStation(stationNumber)
                elif stationNumber in self.realTimeStationList:
                    print('station have real-time data only')

                    self._stationData[stationNumber][REAL_TIME_DATA_KEY] = RealTimeStation(stationNumber)
        else:
            raise AttributeError('Station not in the station list')

    def isStationPresent(self, stationNumber) -> bool:
        return stationNumber in self.allStationList

    @property
    def historicStationList(self) -> dict:
        return self._historic_station.station_list

    @property
    def realTimeStationList(self) -> dict:
        return self._real_time_station.station_list

    def getStationInBoth(self) -> list:
        return sorted([station for station in self.historicStationList if station in self.realTimeStationList])

    @property
    def allStationList(self) -> list:
        historicStation = [station for station in self.historicStationList]
        realTimeStation = [station for station in self.realTimeStationList if station not in self.historicStationList]
        return historicStation + realTimeStation

    def getStationData(self, stationNumber) -> dict:
        if stationNumber not in self._stationData.keys():
            self._extractStationData(stationNumber)

        return self._stationData[stationNumber]

    def _getDataTypeForStation(self, stationNumber, dataType) -> Station:
        if dataType in self.getStationData(stationNumber).keys():
            return self.getStationData(stationNumber)[dataType]
        else:
            raise KeyError("Station doesn't have the requested data")

    def getHistoricalDataForStation(self, stationNumber) -> Station:
        return self._getDataTypeForStation(stationNumber, HISTORICAL_DATA_KEY)

    def getRealTimeDataForStation(self, stationNumber) -> Station:
        return self._getDataTypeForStation(stationNumber, REAL_TIME_DATA_KEY)

    def getStationInfo(self, stationNumber) -> dict:
        if self.isStationPresent(stationNumber):
            if stationNumber in self.historicStationList:
                return self.getHistoricalDataForStation(stationNumber).stationInformation
            else:
                return self.getRealTimeDataForStation(stationNumber).stationInformation
        else:
            raise AttributeError('Station not in the station list')

    def getStationCoordinates(self, stationNumber) -> tuple:
        if self.isStationPresent(stationNumber):
            if stationNumber in self.historicStationList:
                return self.getHistoricalDataForStation(stationNumber).coordinates
            else:
                return self.getRealTimeDataForStation(stationNumber).coordinates
        else:
            raise AttributeError('Station not in the station list')


if __name__ == '__main__':
    from web_crawler.station import *

    webStation = HydrometricDataInterface()
    webStation.getStationsForProvince('Quebec')

    for station in webStation.historicStationList.items():
        print(station)
