from DatabaseConnection import *
import numpy as np

class ConvertSensorData:

    def __init__(self,DBconfig):
        self.My_DB = DBConnector(DBconfig)
        self.date = datetime.now().date()


    def GetTemperature(self):
        measurements = self.My_DB.QuerySensorData("8")
        list_values = []
        for value in measurements:
            list_values.append(value["sensor_reading"])
        Tmax = max(list_values)
        Tmin = min(list_values)
        return Tmax, Tmin

    def GetHumidity(self):
        measurements = self.My_DB.QuerySensorData("9")
        list_values = []
        for value in measurements:
            list_values.append(value["sensor_reading"])
        RHmax = max(list_values)
        RHmin = min(list_values)
        return RHmax, RHmin

    def GetWind(self):
        measurements = self.My_DB.QuerySensorData("5")
        list_values = []
        for value in measurements:
            list_values.append(value["sensor_reading"])
        wind = np.mean(list_values)
        # convert km/h to m/s
        wind = wind*5/18
        # need calibrate height
        return wind

    def Getpressure(self):
        measurements = self.My_DB.QuerySensorData("3")
        list_values = []
        for value in measurements:
            list_values.append(value["sensor_reading"])
        pressure = np.mean(list_values)
        return pressure

    def Getradiation(self,interval=300):
        measurements = self.My_DB.QuerySensorData("7")
        Radiation = 0
        for value in measurements:
            # umol to W
            W = value["sensor_reading"]/4.6
            Radiation += W*interval
        Rs = Radiation * 1.0E-6
        return Rs

    def ComputeDailyWeather(self):
        tem = self.GetTemperature()
        RH = self.GetHumidity()
        dict_daily = {
            "Tmax": tem[0],
            "Tmin": tem[1],
            "RHmax": RH[0],
            "RHmin": RH[1],
            "Solar": self.Getradiation(),
            "Pressure": self.Getpressure(),
            "wind": self.GetWind()
        }
        return dict_daily

    def GetRain(self):
        rain = 0
        for h in range(24):
            try:
                measurement = self.My_DB.QueryRain(hour=h)
                rain += measurement
            except:
                pass
        return rain


if __name__ == '__main__':
    TEST = ConvertSensorData("DB_config.json")
    X = TEST.GetTemperature()#ComputeDailyWeather()
    print(X)
    pass