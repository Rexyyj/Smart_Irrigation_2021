'''Microservice 2: monitoring real-time soil moisture'''
import json
import base64
from DatabaseConnection import *
import paho.mqtt.publish as publish

class Monitoring():

    def __init__(self,DBconfig,MQTTconf, MonitorConf = "MonitorConf.json"):

        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]

        self.DBconfig = DBconfig
        self.conf = json.load(open(MonitorConf))


    def Check(self):
        threshold = self.conf['threshold']
        my_DB = DBConnector(self.DBconfig)
        moisture = my_DB.QueryMoisture()
        if moisture <= threshold:
            #   Execute Irrigation
            IrriAmount_Str = str(self.conf['irrigation_EM'])
            base64EncodedStr = base64.b64encode(IrriAmount_Str.encode('utf-8'))
            payload_raw = ""
            for i in base64EncodedStr:
                payload_raw += chr(i)
            print(payload_raw)
            payload_dict = {"downlinks": [{"f_port": 15, "frm_payload": payload_raw, "priority": "NORMAL"}]}
            payload = json.dumps(payload_dict)
            print(payload)
            publish.single(self.topic,
                           payload,
                           hostname=self.broker, port=self.port,
                           auth={'username': self.clientID, 'password': self.Key})


            #   Update Irrigated amount
            data = my_DB.QueryDailyData(datetime.now().date())
            excuted = data['Irrigated']
            excuted += self.conf['irrigation_EM']
            my_DB.UpdateIrrigation(excuted)



        else:
            pass

if __name__ == '__main__':
    pass
