'''Microservice 2: monitoring real-time soil moisture'''
import json
import base64
import time
from DatabaseConnection import *
import paho.mqtt.publish as publish
import logging
from daemonize import Daemonize
pid_monitor="./pid/monitor.pid"
LOG_FILENAME = './log/service2.log'
# logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
class Monitoring:

    def __init__(self, DBconfig, MQTTconf,area,logger,MonitorConf = "MonitorConf.json"):
        MQTTconf = json.load(open(MQTTconf))
        self.broker = MQTTconf['broker']
        self.port = MQTTconf['port']
        self.topic = MQTTconf["Daily"]
        self.clientID = MQTTconf["Username"]
        self.Key = MQTTconf["APIKey"]

        self.DBconfig = DBconfig
        self.conf = json.load(open(MonitorConf))
        self.area = area
        self.logger =logger
       
        ## logger
        #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        #self.logger = logging.getLogger(__name__)
        #fh = logging.FileHandler(LOG_FILENAME, "w")
        #fh.setLevel(logging.DEBUG)
        #logger.addHandler(fh)
        #self.keep_fds = [fh.stream.fileno()]
        


    def Check(self):
        logger= self.logger
        threshold = self.conf['threshold']
        my_DB = DBConnector(self.DBconfig)
        moisture = 6
        moisture2 = 6
        try:
            moisture = my_DB.QueryMoisture()
        except Exception as e:
            logger.info("Error with reading moisture from single layer")
            logger.exception(e)
        try:
            moisture2 = my_DB.QueryMoisture_multi()[1]
        except:
            logger.info("Error with reading moisture from single layer")
            logger.exception(e)

        if moisture <= threshold or moisture2 <= threshold:
            #   Execute Irrigation
            IrriAmount_Str = str(int(self.conf['irrigation_EM']*self.area*0.1))
            irri_info = "Emergency irrigation of " + str(datetime.now()) + " Amount is " + IrriAmount_Str, " mL"
            logger.info(irri_info)
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
                logger.info("Irrigation finished, update amount in database")
            else:
                excuted = self.conf['irrigation_EM']
                yesterday = my_DB.QueryDailyData(today-timedelta(days=1))
                days = yesterday['Day'] + 1
                my_DB.CreateDailyData(date=today,irrigated=excuted,day=days)
                logger.info("Irrigation finished, no data in database, create a new record")

        else:
            pass

    def main(self):
        while True:
            try:
                self.Check()
                self.logger.info("Working...")
            except Exception as e:
                self.logger.exception(e)
            time.sleep(3600)


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
    Service2 = Monitoring("/home/rex/Smart_Irrigation_2021/Microsrevices/DB_config.json", "MQTT.json",AREA,logger)

    daemon = Daemonize(app="SI_monitor", pid=pid_monitor, action=Service2.main,keep_fds=keep_fds,logger=logger)
    daemon.start()
