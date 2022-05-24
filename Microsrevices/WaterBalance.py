from Et0 import *
from DatabaseConnection import *
from PreProcess import *
import logging
from daemonize import Daemonize
pid_monitor="./pid/water.pid"
LOG_FILENAME = './log/service3.log'

class WaterBalance:

    def __init__(self, DBconfig,logger, Fieldconf = "field.json"):
        self.DBconf = DBconfig
        fieldconf = json.load(open(Fieldconf))
        self.field = fieldconf["field"]
        self.lat = fieldconf["latitude"]
        self.alt = fieldconf["altitude"]
        self.logger = logger

    def Initialday(self):
        #Create data for the first day
        Today = datetime.now().date() # - timedelta(days=1)

        my_DB = DBConnector(self.DBconf)
        my_DB.CreateDailyData(Today, 0)


    def GetET(self):
        SensorData = ConvertSensorData(self.DBconf)
        my_DB = DBConnector(self.DBconf)

        # Compute weather of yesterday
        WY = SensorData.ComputeDailyWeather()

        # ET
        DATE = datetime.now().date() - timedelta(days=1)
        DOFY = DATE.timetuple().tm_yday
        ETmodel = ETmeasurement(Tmin=WY["Tmin"], Tmax=WY["Tmax"], RHmin=WY["RHmin"], RHmax=WY["RHmax"],
                                atm_pressure=WY["Pressure"], Rs=WY["Solar"], wind=WY["wind"],
                                day=DOFY, latitude=self.lat, altitude=self.alt)

        ETvalue = ETmodel.ET0()
        # Upload daily weather info and ET value
        my_DB.InsertDailyWeather(TMax=WY["Tmax"], TMin=WY["Tmin"], RH_Max=WY["RHmax"], RH_Min=WY["RHmin"],
                                 SolarRad_Total=WY["Solar"], Wind_Mean=WY["wind"], Air_Pressure=WY["Pressure"],ETo=ETvalue)

        return ETvalue


    def BalanceCalculation(self):
        my_DB = DBConnector(self.DBconf)
        SensorData = ConvertSensorData(self.DBconf)
        actual_rain = SensorData.GetRain()

        # Yeterday info
        Last_Day = datetime.now().date() - timedelta(days=1)

        ETvalue = self.GetET()
        my_DB.UpdateET(LastDay=Last_Day, ET=ETvalue)

        data_Y = my_DB.QueryDailyData(Last_Day)
        if self.field == "covered":
            residual = data_Y["Need"] - data_Y["Irrigated"] - actual_rain
        else:
            residual = data_Y["Need"] - data_Y["Irrigated"] - actual_rain
        my_DB.UpdateResidual(Last_Day, actual_rain, residual)

    def main(self):
        HOUR = 6
        Excuted = 0
        while True:
            self.logger.info("System checking...")
            hour = datetime.now().hour
            if hour == HOUR:
                if Excuted == 0:
                    Service3.BalanceCalculation()
                    Excuted = 1
                    self.logger.info("Working...")
                else:
                    pass
            else:
                Excuted = 0
            time.sleep(300)

if __name__ == '__main__':
    # TEST = ConvertSensorData("DB_config.json")
    # WY = TEST.ComputeDailyWeather()
    # DATE = datetime.now().date() - timedelta(days=2)
    # DOFY = DATE.timetuple().tm_yday
    # ETmodel = ETmeasurement(Tmin=WY["Tmin"], Tmax=WY["Tmax"], RHmin=WY["RHmin"], RHmax=WY["RHmax"],
    #                         atm_pressure=WY["Pressure"], Rs=WY["Solar"], wind=WY["wind"],
    #                         day=DOFY, latitude=45.07, altitude=300)
    # ETvalue = ETmodel.ET0()
    # TEST_DB = DBConnector("DB_config.json")
    # TEST_DB.UpdateET(LastDay=DATE, ET=ETvalue)
    # print(DATE)
    # print(ETvalue)


    # Configure logger
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILENAME, "w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    keep_fds = [fh.stream.fileno()]
    logger.info("Starting service...")



    Service3 = WaterBalance("/home/rex/Smart_Irrigation_2021/Microsrevices/DB_config.json",logger)


    daemon = Daemonize(app="SI_monitor", pid=pid_monitor, action=Service3.main,keep_fds=keep_fds,logger=logger)
    daemon.start()


