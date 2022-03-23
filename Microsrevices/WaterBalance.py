from Et0 import *
from DatabaseConnection import *


class WaterBalance():

    def __init__(self,DBconfig):
        self.DBconf = DBconfig
        self.lat = 45.07
        self.alt = 300

    def BalanceCalculation(self,actual):
        My_DB = DBConnector(self.DBconf)

        # Weather of yesterday
        WY = My_DB.QueryDailyWeather()

        #ET
        ETmodel = measurement(Tmin = WY["AirTempMin"], Tmax=WY["AirTempMax"], RHmin=WY["RHMin"], RHmax=WY["RHMax"], atm_pressure=WY["AirPressure"], Rs=WY["SolarRadTotal"], wind=WY["WindMean"], day=WY["DOY"], latitude=self.lat, altitude=self.alt)
        ETvalue = ETmodel.ET0()

        # Yeterday info
        Last_Day = datetime.now().date() - timedelta(days=1)
        LastDay = [Last_Day]
        data_Y = My_DB.QueryDailyData(LastDay)
        residual = data_Y["Need"] - data_Y["Irrigated"] - actual
        My_DB.UpdateDailyData(LastDay, actual, residual)



if __name__ == '__main__':
    pass