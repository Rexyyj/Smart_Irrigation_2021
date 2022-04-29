import time
import telepot
from telepot import Bot
from telepot.loop import MessageLoop
from MyMQTT import *
import datetime
import json

class Telegrambot():

    def __init__(self, confAddr):
        try:
            self.conf = json.load(open(confAddr))
        except:
            print("Configuration file not found")
            exit()
        self.token = self.conf["token"]
        self.bot = telepot.Bot(self.token)
        self.serviceId = self.conf["serviceId"]
        self.alertTopic=self.conf["alerttopic"]
        self.client = MyMQTT(
            self.serviceId, self.conf["broker"], int(self.conf["port"]), self)
        self.__message = {"start": ""}


    def start(self):
        self.client.start()
        self.client.mySubscribe(self.alertTopic)
        MessageLoop(self.bot, self.msg_handler).run_as_thread()

    def stop(self):
        self.workingStatus = False
        self.client.stop()

    def initial_message(self):
        self.bot.sendMessage(
            text='Welcome to the Smart_irrigation!')

    def notify(self, topic, msg):
        msg = json.loads(msg)
        info = "Attention please!The soil moisture is below 10%! Please irrigate from user interface."
        print(msg)
        self.bot.sendMessage(info)


if __name__ == "__main__":
    configFile = input("Enter the location of configuration file: ")
    if len(configFile) == 0:
        configFile = "./configuration.json"
    telegrambot = Telegrambot(configFile)
    telegrambot.start()
    print('waiting ...')
    while (True):
        if input() == 'q':
            break

    telegrambot.stop()
