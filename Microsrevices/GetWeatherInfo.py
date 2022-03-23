import requests
from datetime import datetime
import json

class WeatherInfo():

    def __init__(self,ConfAddr='Weatherservice.json'):
        conf = json.load(open(ConfAddr))
        self.Key = conf['APIkey']
        self.ServiceName = conf['Weatherservice']
        self.Lat = conf['Latitude']
        self.Lon = conf['Longitude']
        self.weather = {}

    def getweather(self):
        if self.ServiceName == 'openweathermap':
            latitude = '&lat=' + str(self.Lat)
            longitude = '&lon=' + str(self.Lon)
            auth = '&appid=' + self.Key
            uri =  'https://api.openweathermap.org/data/2.5/onecall?exclude=current,minutely,hourly&units=metric'
            URL = uri + latitude + longitude + auth
            reply = requests.get(URL).text
            self.weather = json.loads(reply)
        return self.weather

    def getrain_today(self):
        self.getweather()
        rain = 0
        tomorrow = self.weather['daily'][0]
        try:
            rain = tomorrow['rain']
        except:
            pass
        return rain


if __name__ == '__main__':
    TEST = WeatherInfo()
    print(TEST.getrain_today())
    pass