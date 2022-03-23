import json
#import context
import time
import base64
import paho.mqtt.publish as publish

class DailyAmount():

    def __init__(self, MQTTconf):
        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        #self.clientID = "DailyInitial" #Can be other config
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]





        # self.ET = ET   # ET value of yesterday
        # self.residual = Residual
        # self.rain = Rain

    def CalculateDailyAmount(self, ET, Residual, Rain):

        #IrriAmount = self.ET + self.residual - self.rain
        IrriAmount = ET + Residual - Rain
        IrriAmount_Str = str(IrriAmount)
        base64EncodedStr = base64.b64encode(IrriAmount_Str.encode('utf-8'))
        #MQTTclient = MyMQTT(self.clientID,self.broker,self.port)
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



        return IrriAmount


if __name__ == '__main__':
    TEST = DailyAmount("MQTT.json")
    # while True:

    TEST.CalculateDailyAmount(20, -1, 9)
    time.sleep(20)