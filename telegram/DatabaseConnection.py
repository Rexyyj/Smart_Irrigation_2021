import mysql.connector
import json
from datetime import date, datetime, timedelta



import pandas as pd
from numpy import log as ln


class DBConnector():
    def __init__(self,ConfAddr):
        config = json.load(open(ConfAddr))
        self.my_db = mysql.connector.connect(**config)

    def ReloadConnection(self,ConfAddr):
        config = json.load(open(ConfAddr))
        self.my_db = mysql.connector.connect(**config)

    def InsertDailyWeather(self, DATE, DOFY, TMax, TMin, RH_Max, RH_Min, SolarRad_Total, Wind_Mean, Air_Pressure):
        # DATE and DOFY could be removed
        #DATE = datetime.now().date() - timedelta(days=1)
        #DOFY = DATE.timetuple().tm_yday
        data_dailyweather = {
            'Date': DATE,
            'DOY': int(DOFY),
            'AirTempMax': float(TMax),
            'AirTempMin': float(TMin),
            'RHMax': int(RH_Max),
            'RHMin': int(RH_Min),
            'SolarRadTotal': float(SolarRad_Total),
            'WindMean': float(Wind_Mean),
            'AirPressure': float(Air_Pressure)
        }
        add_dailyweather = ("INSERT INTO DailyWeather_TEST "
                            "(Date, DOY, AirTempMax, AirTempMin, RHMax, RHMin, SolarRadTotal, WindMean, AirPressure) "
                            "VALUES (%(Date)s, %(DOY)s, %(AirTempMax)s, %(AirTempMin)s, %(RHMax)s, %(RHMin)s, %(SolarRadTotal)s, %(WindMean)s, %(AirPressure)s)")

        cursor = self.my_db.cursor()
        cursor.execute(add_dailyweather, data_dailyweather)
        self.my_db.commit()
        cursor.close()

    def QueryDailyWeather(self):
        Last_Day = datetime.now().date() - timedelta(days=1)
        LastDay = [Last_Day]
        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM DailyWeather_TEST "
                 "WHERE Date = %s")

        cursor.execute(query, LastDay)
        Result = cursor.fetchone()
        cursor.close()
        return Result

    def QueryDailyData(self,LastDay):

        #Argument could be removed
        # Last_Day = datetime.now().date() - timedelta(days=1)
        # LastDay = [Last_Day]
        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM DailyData_TEST "
                 "WHERE Date = %s")

        cursor.execute(query, LastDay)
        Result = cursor.fetchone()
        cursor.close()
        return Result

    def CreateDailyData(self,Day,need,forecast,irrigated):
        # Argument should be removed
        # Day = datetime.now().date()
        new_dailyData = {"Date": Day,
                         "ET": 0,
                         "Need": need,
                         "Forecast": forecast,
                         "Actual": 0,
                         "Residual": 0,
                         "Irrigated": irrigated}
        cursor = self.my_db.cursor()
        add_dailyData = ("INSERT INTO DailyData_TEST "
                            "(Date, ET, Need, Forecast, Actual, Residual, Irrigated) "
                            "VALUES (%(Date)s, %(ET)s, %(Need)s, %(Forecast)s, %(Actual)s, %(Residual)s, %(Irrigated)s)")

        cursor.execute(add_dailyData, new_dailyData)
        self.my_db.commit()
        cursor.close()

    def UpdateDailyData(self,LastDay,actual,residual):
        # Argument could be removed
        # Last_Day = datetime.now().date() - timedelta(days=1)
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                        "SET ET = %s, Actual = %s, Residual = %s"
                        "WHERE Date = %s")

        data = (actual,residual,LastDay)
        cursor.execute(update, data)
        cursor.close()

    def UpdateIrrigation(self,Amount):
        today = datetime.now().date()
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                        "SET Irrigated = %s"
                        "WHERE Date = %s")

        data = (Amount, today)
        cursor.execute(update, data)
        cursor.close()

    def UpdateET(self,LastDay,ET):
        # Argument could be removed
        # Last_Day = datetime.now().date() - timedelta(days=1)
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                  "SET ET = %s "
                  "WHERE Date = %s")

        data = (ET, LastDay)
        cursor.execute(update, data)
        cursor.close()

    # def QuerySensorData(self,sensorID,start,end):
    #     cursor = self.my_db.cursor(dictionary=True)
    #     query = ("SELECT * FROM DailyWeather_TEST "
    #              "WHERE Date = %s")
    #
    #     cursor.execute(query, LastDay)
    #     Result = cursor.fetchone()
    #     cursor.close()
    #     return Result

    def QueryMoisture(self):
        Today = datetime.now().date() - timedelta(days=30)    # for test - timedelta(days=5)
        start = datetime.combine(Today, datetime.min.time())
        end = start + timedelta(days=30)


        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM single_value_sensor "
                 "WHERE sensor_type = %s AND tmp > %s AND tmp < %s "
                 "ORDER BY tmp DESC")

        cursor.execute(query, ("2", start, end))
        Result = cursor.fetchone()["sensor_reading"]
        #cursor.close()
        return Result

if __name__ == '__main__':
    myDB = DBConnector('DB_config.json')
    D = [date(2021, 1, 1)]
    Result = myDB.QueryMoisture()
    print(Result)



    pass




