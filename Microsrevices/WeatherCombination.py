from DatabaseConnection import *
import time
import base64
import paho.mqtt.publish as publish
from GetWeatherInfo import WeatherInfo

import logging
from daemonize import Daemonize
pid_weather="./pid/weather.pid"
LOG_FILENAME = './log/service1.log'

class DailyIrrigation:

    def __init__(self, MQTTconf, DBconf,area,logger, Fieldconf='field.json'):
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
        self.area=area
        self.logger=logger


    def DailyAmount(self):
        my_DB = DBConnector(self.DBconf)
        Today = datetime.now().date()
        Last_Day = Today - timedelta(days=1)
        DailyData = my_DB.QueryDailyData(Last_Day)
        WF = WeatherInfo()
        num_of_days = DailyData["Day"] + 1
        # get crop coefficient
        if num_of_days <= self.cropInfo["stage"][0]:
            # In the initial phase, the Kc value increase linearly
            Kc_ini = self.cropInfo["value"]['ini']
            Kc_mid = self.cropInfo["value"]['mid']
            Kc = Kc_ini + (Kc_mid-Kc_ini) / self.cropInfo["stage"][0] * num_of_days
            phase = "initial"
        elif num_of_days > self.cropInfo["stage"][1]:
            Kc = self.cropInfo["value"]['end']
            phase = "final"
        else:
            Kc = self.cropInfo["value"]['mid']
            phase = "middle"
        log_info= "Plant has grown for " + str(num_of_days) + " days, in " + phase + " phase, Kc value is"+str(Kc)
        self.logger.info(log_info)
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
        IrriAmount_Str = str(int(IrriAmount*self.area*0.1))
        irri_info = "Daily irrigation of" + str(Today) + " Amount is " + IrriAmount_Str + " mL"
        self.logger.info(irri_info)
        base64EncodedStr = base64.b64encode(IrriAmount_Str.encode('utf-8'))
        payload_raw = ""
        for i in base64EncodedStr:
            payload_raw+=chr(i)
        payload_dict = {"downlinks":[{"f_port": 15,"frm_payload":payload_raw,"priority": "NORMAL"}]}
        payload = json.dumps(payload_dict)
        publish.single(self.topic,
                       payload,
                       hostname=self.broker, port=self.port,
                       auth={'username': self.clientID, 'password': self.Key})

        # Store data in database
        data = my_DB.QueryDailyData(Today)
        if data is None:
            my_DB.CreateDailyData(date=Today, need=Requirement, forecast=ForecastRain, irrigated=IrriAmount, day=num_of_days)
            update_info = "Daily data for" + str(Today) + " created"
            self.logger.info(update_info)
        else:
            Excuted = IrriAmount + data['Irrigated']
            my_DB.UpdateDailyData(Excuted, Requirement, ForecastRain, num_of_days)
            update_info = "Daily data for" + str(Today) + " updated"
            self.logger.info(update_info)

        return IrriAmount


    def main(self):
        HOUR = 8
        Irrigated = 0
        while True:
            hour = datetime.now().hour
            self.logger.info("System checking...")
            if hour == HOUR:
                if Irrigated == 0:
                    try:
                        Service1.DailyAmount()
                        Irrigated = 1
                        self.logger.info("Working...")
                    except Exception as e:
                        self.logger.exception(e)
                else:
                    pass
            else:
                Irrigated = 0
            time.sleep(300)



if __name__ == '__main__':
    
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


    AREA = 15*15*3.15*2
    Service1 = DailyIrrigation("MQTT.json", "/home/rex/Smart_Irrigation_2021/Microsrevices/DB_config.json",AREA,logger)

    daemon = Daemonize(app="SI_weather", pid=pid_weather, action=Service1.main,keep_fds=keep_fds,logger=logger)
    daemon.start()
