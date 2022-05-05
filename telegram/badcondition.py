import json
from DatabaseConnection import *
import time
import base64
import paho.mqtt.publish as publish


class badcondition():
    def __init__(self, conf, DBconf):
        conf = json.load(open(conf))
        self.broker = conf['broker']
        self.port = conf['port']
        self.topic = conf["alerttopic"]
        self.DBconf = DBconf

    def lowsoilmositure(self):
        myDB = DBConnector(self.DBconf)
        moisture = myDB.QueryMoisture()
        # Send command to telegram bot if the soil moisture is below threshold
        if moisture < 0.1:
            payload_msg = {"Alert!The soil moisture is below threshold!"}
            payload = json.dumps(payload_msg)
            publish.single(self.topic,
                           payload,
                           hostname=self.broker, port=self.port)


if __name__ == '__main__':
    TEST = badcondition("configuration.json", "DB_config.json")
    while True:
        # try:
            TEST.lowsoilmositure()
            TEST.sleep(3600)
        # except:
        #     print("Connection error")
