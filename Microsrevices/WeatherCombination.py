from DatabaseConnection import *
import time
import base64
import paho.mqtt.publish as publish
from GetWeatherInfo import WeatherInfo

class DailyIrrigation:

    def __init__(self, MQTTconf, DBconf, Fieldconf='field.json'):
        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]
        self.DBconf = DBconf
        fieldconf = json.load(open(Fieldconf))
        self.field = fieldconf['field']
        self.cropInfo = json.load(open('crops.json'))[fieldconf['crop']]


    def DailyAmount(self, area=10.0):
        my_DB = DBConnector(self.DBconf)
        Today = datetime.now().date()
        Last_Day = Today - timedelta(days=1)
        DailyData = my_DB.QueryDailyData(Last_Day)
        WF = WeatherInfo()
        num_of_days = DailyData["Day"] + 1
        # get crop coefficient
        if num_of_days <= self.cropInfo["stage"][0]:
            Kc = self.cropInfo["value"]['ini']
            phase = "initial"
        elif num_of_days > self.cropInfo["stage"][1]:
            Kc = self.cropInfo["value"]['end']
            phase = "final"
        else:
            Kc = self.cropInfo["value"]['mid']
            phase = "middle"
        print("The plant has grown for ",num_of_days, " days, in the ", phase, " phase, Kc value is", Kc)
        # Combine weather forecast and calculate expected irrigation amount
        # IrriAmount = self.ET + self.residual - self.rain


        Requirement = DailyData["ET"] * Kc + DailyData["Residual"]

        ForecastRain =WF.getrain_today()
        if self.field == "covered":
            IrriAmount = Requirement
        else:
            IrriAmount = Requirement - ForecastRain
            if Requirement < 0:
                Requirement =0
        # Send command to LoRa device
        IrriAmount_Str = str(int(IrriAmount*area*0.1))
        print("Daily irrigation of", Today, " Amount is ", IrriAmount_Str, " mL")
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

        # Store data in database
        data = my_DB.QueryDailyData(Today)
        if data is None:
            my_DB.CreateDailyData(date=Today, need=Requirement, forecast=ForecastRain, irrigated=IrriAmount, day=num_of_days)
        else:
            Excuted = IrriAmount + data['Irrigated']
            my_DB.UpdateDailyData(Excuted, Requirement, ForecastRain, num_of_days)
            print("Daily data updated")

        return IrriAmount


if __name__ == '__main__':
    AREA = 15*15*3.15*2

    Service1 = DailyIrrigation("MQTT.json", "DB_config.json")
    HOUR = 8
    Irrigated = 0
    while True:
        hour = datetime.now().hour
        if hour == HOUR:
            if Irrigated == 0:
                Service1.DailyAmount(area = AREA)
                Irrigated = 1
            else:
                pass
        else:
            Irrigated = 0
        time.sleep(300)

