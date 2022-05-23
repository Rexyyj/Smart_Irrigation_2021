'''Microservice 2: monitoring real-time soil moisture'''
import json
import base64
import time
from DatabaseConnection import *
import paho.mqtt.publish as publish
import logging
LOG_FILENAME = './log/service2.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, datefmt='"%Y-%m-%d %H:%M:%S"')
class Monitoring:

    def __init__(self, DBconfig, MQTTconf, MonitorConf = "MonitorConf.json"):
        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]

        self.DBconfig = DBconfig
        self.conf = json.load(open(MonitorConf))


    def Check(self, area = 10.0):
        threshold = self.conf['threshold']
        my_DB = DBConnector(self.DBconfig)
        moisture = 6
        moisture2 = 6
        try:
            moisture = my_DB.QueryMoisture()
        except Exception as e:
            logging.info("Error with reading moisture from single layer")
            logging.exception(e)
        try:
            moisture2 = my_DB.QueryMoisture_multi()[1]
        except:
            logging.info("Error with reading moisture from single layer")
            logging.exception(e)

        if moisture <= threshold or moisture2 <= threshold:
            #   Execute Irrigation
            IrriAmount_Str = str(int(self.conf['irrigation_EM']*area*0.1))
            irri_info = "Emergency irrigation of " + str(datetime.now()) + " Amount is " + IrriAmount_Str, " mL"
            logging.info(irri_info)
            base64EncodedStr = base64.b64encode(IrriAmount_Str.encode('utf-8'))
            payload_raw = ""
            for i in base64EncodedStr:
                payload_raw += chr(i)
            payload_dict = {"downlinks": [{"f_port": 15, "frm_payload": payload_raw, "priority": "NORMAL"}]}
            payload = json.dumps(payload_dict)
            publish.single(self.topic,
                           payload,
                           hostname=self.broker, port=self.port,
                           auth={'username': self.clientID, 'password': self.Key})


            # Update Irrigated amount
            today = datetime.now().date()
            data = my_DB.QueryDailyData(today)
            if data != None:
                excuted = data['Irrigated']
                excuted += self.conf['irrigation_EM']
                my_DB.UpdateIrrigation(excuted)
                logging.info("Irrigation finished, update amount in database")
            else:
                excuted = self.conf['irrigation_EM']
                yesterday = my_DB.QueryDailyData(today-timedelta(days=1))
                days = yesterday['Day'] + 1
                my_DB.CreateDailyData(date=today,irrigated=excuted,day=days)
                logging.info("Irrigation finished, no data in database, create a new record")

        else:
            pass

if __name__ == '__main__':
    Service2 = Monitoring("DB_config.json", "MQTT.json")
    AREA = 15*15*3.15*2
    while True:
        try:
            Service2.Check(area=AREA)
        except Exception as e:
            logging.exception(e)
        time.sleep(3600)
