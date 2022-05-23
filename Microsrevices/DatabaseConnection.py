import mysql.connector
import json
from datetime import date, datetime, timedelta


class DBConnector:
    def __init__(self,ConfAddr):
        config = json.load(open(ConfAddr))
        self.my_db = mysql.connector.connect(**config)

    def ReloadConnection(self,ConfAddr):
        config = json.load(open(ConfAddr))
        self.my_db = mysql.connector.connect(**config)

    def InsertDailyWeather(self, TMax, TMin, RH_Max, RH_Min, SolarRad_Total, Wind_Mean, Air_Pressure, ETo):
        # DATE and DOFY could be removed
        DATE = datetime.now().date() - timedelta(days=1)
        DOFY = DATE.timetuple().tm_yday
        data_dailyweather = {
            'Date': DATE,
            'DOY': int(DOFY),
            'AirTempMax': float(TMax),
            'AirTempMin': float(TMin),
            'RHMax': int(RH_Max),
            'RHMin': int(RH_Min),
            'SolarRadTotal': float(SolarRad_Total),
            'WindMean': float(Wind_Mean),
            'AirPressure': float(Air_Pressure),
            'ETo': float(ETo)
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
        try:
            cursor.fetchall()
        except:
            pass
        cursor.close()
        return Result

    def QueryDailyData(self,LastDay):

        LastDay = [LastDay]
        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM DailyData_TEST "
                 "WHERE Date = %s")

        cursor.execute(query, LastDay)
        Result = cursor.fetchone()
        try:
            cursor.fetchall()
        except:
            pass
        cursor.close()
        return Result

    def CreateDailyData(self, date, day, irrigated=0, need=0, forecast=0):
        # Create new row
        #Day = datetime.now().date()
        new_dailyData = {"Date": date,
                         "ET": 0,
                         "Need": need,
                         "Forecast": forecast,
                         "Actual": 0,
                         "Residual": 0,
                         "Irrigated": irrigated,
                         "Day": day}
        cursor = self.my_db.cursor()
        add_dailyData = ("INSERT INTO DailyData_TEST "
                            "(Date, ET, Need, Forecast, Actual, Residual, Irrigated, Day) "
                            "VALUES (%(Date)s, %(ET)s, %(Need)s, %(Forecast)s, %(Actual)s, %(Residual)s, %(Irrigated)s, %(Day)s)")

        cursor.execute(add_dailyData, new_dailyData)
        self.my_db.commit()
        cursor.close()

    def UpdateResidual(self, LastDay, actual, residual):
        # Argument could be removed
        # Last_Day = datetime.now().date() - timedelta(days=1)
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                        "SET Actual = %s, Residual = %s"
                        "WHERE Date = %s")

        data = (actual, residual, LastDay)
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
        self.my_db.commit()
        cursor.close()

    def UpdateDailyData(self, irrigated, need, forecast, days):
        today = datetime.now().date()
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                        "SET Irrigated = %s, Forecast = %s, Need = %s, Day = %s"
                        " WHERE Date = %s")

        data = (irrigated, forecast, need, days, today)
        cursor.execute(update, data)
        self.my_db.commit()
        cursor.close()

    def UpdateET(self, LastDay, ET):
        # Argument could be removed
        # Last_Day = datetime.now().date() - timedelta(days=1)
        cursor = self.my_db.cursor()

        # prepare query and data
        update = ("UPDATE DailyData_TEST "
                  "SET ET = %s "
                  "WHERE Date = %s")

        data = (float(ET), LastDay)
        cursor.execute(update, data)
        self.my_db.commit()
        cursor.close()

    def QuerySensorData(self, sensor, hours=0):
        today = datetime.now().date()
        end = datetime.combine(today, datetime.min.time()) + timedelta(hours=hours)

        start = end - timedelta(days=1)

        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM single_value_sensor "
                 "WHERE sensor_type = %s AND Device_ID = %s AND tmp > %s AND tmp < %s "
                 "ORDER BY tmp DESC")
        # Weather Station device_id = 100
        cursor.execute(query, (sensor, "100", start, end))
        Result = cursor.fetchall()
        cursor.close()
        return Result

    def QueryMoisture(self):

        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time())
        end = start + timedelta(days=1)

        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM single_value_sensor "
                 "WHERE sensor_type = %s AND Device_ID = %s AND tmp > %s AND tmp < %s "
                 "ORDER BY tmp DESC")
        # sensor_type = 2, device_id = 1
        cursor.execute(query, ("2", "1", start, end))
        sensor_reading = []
        for n in range(3):
            try:
                result = cursor.fetchone()
                sensor_reading.append(result["sensor_reading"])
            except:
                pass
        moisture = sum(sensor_reading) / len(sensor_reading)
        try:
            cursor.fetchall()
        except:
            pass
        cursor.close()
        return moisture

    def QueryMoisture_multi(self,deviceID='3'):

        end = datetime.now()
        start = end - timedelta(days=1)

        cursor = self.my_db.cursor(dictionary=True)
        query = ("SELECT * FROM multi_value_sensor "
                 "WHERE sensor_type = %s AND Device_ID = %s AND tmp > %s AND tmp < %s "
                 "ORDER BY tmp DESC")
        # sensor_type = 2, device_id = 1
        cursor.execute(query, ("18", deviceID, start, end))
        layer1 = []
        layer2 = []
        for n in range(3):
            try:
                result = cursor.fetchone()
                layer1.append(result["layer1"])
                layer2.append(result["layer2"])
            except:
                pass
        moisture1 = sum(layer1) / len(layer1)
        moisture2 = sum(layer2) / len(layer2)
        try:
            cursor.fetchall()
        except:
            pass
        cursor.close()
        return (moisture1, moisture2)

    def QueryRain(self,hour=0):
        date = datetime.now().date() - timedelta(days=1)
        H = hour + 1
        start = datetime.combine(date, datetime.min.time()) + timedelta(hours=H, minutes=10)
        end = start + timedelta(minutes=30)

        cursor = self.my_db.cursor()
        query = ("SELECT sensor_reading FROM single_value_sensor "
                 "WHERE sensor_type = %s AND Device_ID = %s AND tmp > %s AND tmp < %s "
                 "ORDER BY tmp DESC")
        cursor.execute(query, ("6", "100", start, end))
        rain = cursor.fetchone()[0]
        try:
            cursor.fetchall()
        except:
            pass
        cursor.close()
        return rain

if __name__ == '__main__':
    TEST = DBConnector('DB_config.json')
    TEST.UpdateDailyData(1,2,3,1)
    pass




