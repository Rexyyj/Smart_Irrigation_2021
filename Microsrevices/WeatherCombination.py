import json
from DatabaseConnection import *
import time
import base64
import paho.mqtt.publish as publish
from GetWeatherInfo import *
class DailyIrrigation():

    def __init__(self, MQTTconf,DBconf):
        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]
        self.DBconf = DBconf


    def CalculateDailyAmount(self):
        my_DB = DBConnector(self.DBconf)
        Today = datetime.now().date()
        Last_Day = Today - timedelta(days=1)
        LastDay = [Last_Day]
        DailyData = my_DB.QueryDailyData(LastDay)
        WF = WeatherInfo()

        #Combine weather forecast and calculate expected irrigation amount
        #IrriAmount = self.ET + self.residual - self.rain
        Requirement = DailyData["ET"] + DailyData["Residual"]
        ForecastRain =WF.getrain_today()
        IrriAmount = Requirement - ForecastRain

        #Send command to LoRa device
        IrriAmount_Str = str(IrriAmount)
        base64EncodedStr = base64.b64encode(IrriAmount_Str.encode('utf-8'))
        payload_raw = ""
        for i in base64EncodedStr:
            payload_raw+=chr(i)
        print(payload_raw)
        payload_dict = {"downlinks":[{"f_port": 15,"frm_payload":payload_raw,"priority": "NORMAL"}]}
        payload = json.dumps(payload_dict)
        print(payload)
        publish.single(self.topic,
                       payload,
                       hostname=self.broker, port=self.port,
                       auth={'username': self.clientID, 'password': self.Key})

        #Store data in database
        my_DB.CreateDailyData(Day=Today,need=Requirement,forecast=ForecastRain,irrigated=IrriAmount)


        return IrriAmount


if __name__ == '__main__':
    TEST = DailyIrrigation("MQTT.json","DB_config.json")
