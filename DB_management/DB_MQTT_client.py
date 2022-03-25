import time

from DB_management.mySQL_queries import insert_preliminary_test_data, connect, insert_sensor_data
from paho.mqtt import client as _mqtt_client
from payload_decoding import decode_LoRa_sensors, parse_plug_n_sense_str
import json
import base64
import struct
from datetime import datetime
import time

# the things network MQTT integration credentials
broker = 'eu1.cloud.thethings.network'
port = 1883
end_dev_topic = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"
topic = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"
username = 'arduino-lora-test-rex@ttn'
password = 'NNSXS.AQKUJD6CGFB3HKLERXNMYVQBTN7VGXQXBLMABXQ.H2WWY5RFV5I5BPR4LJ3R7QVYD76HZYQOF72EL4LLXY7JWVR3HMSQ'
file_name = "./received.json"

topic2 = "v3/arduino-lora-test-rex@ttn/devices/eui-70b3d57ed004e263/up"  # plug&sense
topic3 = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"
topic4 = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a32371b8001/up"

# mySQL DB credentials
DB_name = "local_db"
DB_usn = "root"
DB_psw = "4Wza^d7LwYP~={RB"


class MQTTClient:

    DEBUG = True

    def __init__(self, client_id, mqtt_broker, mqtt_broker_port, device_topics, mqtt_auth=None):
        self.MQTT_client = _mqtt_client.Client(client_id)
        self.client_id = client_id
        self.broker = mqtt_broker
        self.broker_port = mqtt_broker_port
        self.device_topics = device_topics
        self.db_connection = None

        # set authentication if provided
        if mqtt_auth is not None:
            self.MQTT_client.username_pw_set(mqtt_auth[0], mqtt_auth[1])

        # set callbacks
        self.MQTT_client.on_connect = self.on_connect
        self.MQTT_client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT broker connection successful")
        else:
            print("Failed to connect to MQTT broker, return code %d\n", rc)

    def on_message(self, paho_mqtt, userdata, msg):
        if self.DEBUG:
            print(f"received payload, topic: {msg.topic}")
        MQTT_payload_raw = msg.payload
        MQTT_payload_json = json.loads(MQTT_payload_raw)

        # # id of the transmitter
        transmitter_id = MQTT_payload_json["end_device_ids"]["device_id"]

        # payload (raw bits, needs decoding)
        rx_server_timestamp = None
        rx_gateway_timestamp = None
        tx_timestamp = None
        if "uplink_message" in MQTT_payload_json:
            if "frm_payload" in MQTT_payload_json["uplink_message"]:
                payload_raw = MQTT_payload_json["uplink_message"]["frm_payload"]
            # search if timestamps are in the json packet, if a tmp is not found, NULL value will be inserted in the db
            if "received_at" in MQTT_payload_json:
                tx_timestamp = MQTT_payload_json["received_at"]
            if "uplink_message" in MQTT_payload_json:
                if "received_at" in MQTT_payload_json["uplink_message"]:
                    rx_gateway_timestamp = MQTT_payload_json["uplink_message"]["received_at"]
                if "settings" in MQTT_payload_json["uplink_message"]:
                    if "time" in MQTT_payload_json["uplink_message"]["settings"]:
                        tx_timestamp = MQTT_payload_json["uplink_message"]["settings"]["time"]
                if tx_timestamp is None:
                    if "rx_metadata" in MQTT_payload_json["uplink_message"]:
                        if type(MQTT_payload_json["uplink_message"]["rx_metadata"]) is list:
                            for el in MQTT_payload_json["uplink_message"]["rx_metadata"]:
                                if "time" in el:
                                    tx_timestamp = el["time"]
                                    break
        elif "data" in MQTT_payload_json:
            # ALTERNATE PACKET FORMAT
            payload_raw = MQTT_payload_json["data"]["raw_payload"]
            tx_timestamp = MQTT_payload_json["data"]["received_at"]
        else:
            # INVALID MY THINGS NETWORK PACKET
            return
        # largest timestamp, assuming it marks when the packet arrived at the network server
        # rx_server_timestamp = MQTT_payload_json["received_at"]

        # 2nd largest timestamp, assuming it marks when the LoRa packet arrived at the gateway
        # rx_gateway_timestamp = MQTT_payload_json["uplink_message"]["received_at"]

        # these are the two lowest timestamp in the packet (and they are equal), assuming they mark tx time
        # tx_timestamp = MQTT_payload_json["uplink_message"]["settings"]["time"]
        # tx_timestamp2 = MQTT_payload_json["uplink_message"]["rx_metadata"][0]["time"]
        # tx_unix_timestamp = MQTT_payload_json["uplink_message"]["settings"]["timestamp"]
        # tx_unix_timestamp2 = MQTT_payload_json["uplink_message"]["rx_metadata"][0]["timestamp"]
        # NOTE: this isn't actually the unix timestamp

        # TODO: THIS IS A TEMPORARY SOLUTION FOR PACKETS FROM PLUG&SENSE, UPDATE WHEN THEIR FORMAT IS STANDARDIZED
        try:
            global topic2
            STRING_PAYLOAD_TOPIC = topic2
            if msg.topic == STRING_PAYLOAD_TOPIC:
                decoded_data = {}
                decoded_data["device_ID"] = 100  # set manually
                decoded_data["data"] = parse_plug_n_sense_str(payload_raw)
            else:
                decoded_data = self.decode_payload(payload_raw)
                """
                dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
                sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
                """

            if self.DEBUG:
                print(f"decoded payload: {decoded_data}, timestamps: tx: {tx_timestamp}")
            # insert into database
            if decoded_data["data"] is None:
                # invalid data
                return None
            if tx_timestamp is None:
                if rx_gateway_timestamp is None:
                    if rx_server_timestamp is None:
                        tmp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        tmp = rx_gateway_timestamp
                else:
                    tmp = rx_gateway_timestamp
            else:
                tmp = tx_timestamp
            try:
                tmp = datetime.strptime(tmp.split(".")[0], "%Y-%m-%dT%H:%M:%S")
            except:
                print("PROBLEM PARSING STRING: ", tmp)
                tmp = datetime.fromtimestamp(time.time())
            device_ID = decoded_data["device_ID"]
            for sensor_pair in decoded_data["data"]:
                # insert db entry
                data_dict = {"sensor_type": "single", "sensor_data": {"device_ID": device_ID,
                                                                            "sensor_type": sensor_pair[0],
                                                                            "rx_timestamp": tmp,
                                                                            "sensor_reading": sensor_pair[1]}}
                insert_sensor_data(self.db_connection, data_dict)
                """
                data_dict: dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
                sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
                """
                # dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
                # sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
                # insert_preliminary_test_data(self.db_connection, tx_timestamp, rx_gateway_timestamp, rx_server_timestamp,
                #                              decoded_data["device_ID"], decoded_data["data"])
        except:
            print("inconsistent packet")
            with open("err_packt_log.json", "a") as fp:
                fp.write(MQTT_payload_raw+"\n")

    def subscribe(self, device_topics):
        self.MQTT_client.subscribe(device_topics)

    def decode_payload(self, raw_payload):
        # SUPPORTS SINGLE, MULTI-LAYER, BOOLEAN SENSORS, PUMP STATUS SENSORS

        # decoded_data = {"dev_id": , "data": [["sensor_id", ], ["", ]]}
        decoded_data = {}

        # read the payload string into a base 64 byte array
        bytearray_raw = bytearray(base64.b64decode(raw_payload))
        decoded_data["device_ID"] = bytearray_raw[0]  # first byte is the device id
        # print(bytearray_raw[0], bytearray_raw[1])
        # print("id: ", decoded_data["device_ID"])
        decoded_data["data"] = []
        decoded_data["data"] = decode_LoRa_sensors(bytearray_raw[1:])
        # decoded_data["data"] = [[sensor_type, sensor_data],[sensor_type, sensor_data],..] -> each list element is a
        # sensor reading (multi, single or bool)

        return decoded_data

    def start(self):
        # connect to broker
        self.MQTT_client.connect(self.broker, self.broker_port)
        # subscribe to topics
        for dev_topic in self.device_topics:
            self.subscribe(dev_topic)
        # start loop
        self.MQTT_client.loop_forever()

    def connect_to_db(self, DB_auth_usn, DB_auth_psw, DB_name, DB_host, DB_port):
        if self.DEBUG:
            print("connecting to DB")
        self.db_connection = connect(DB_auth_usn, DB_auth_psw, DB_name, DB_host, DB_port)
        if self.db_connection is None:
            raise Exception("ERROR:Could not connect to Database")
        if self.DEBUG:
            print("connection successful")

    def store_LoRa_packet(self):
        """
        dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
        sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
        :return:
        """


if __name__ == '__main__':
    topics = [topic2, topic3, topic4]
    DB_usn = "root"
    DB_psw = "Qwertykk.22!"
    DB_name = "new_db"
    DB_host = "80.210.98.95"
    DB_port = 6606
    test_client = MQTTClient("test-213", broker, port, mqtt_auth=(username, password), device_topics=topics)
    test_client.connect_to_db(DB_usn, DB_psw, DB_name, DB_host, DB_port)
    test_client.start()
    # test_client.subscribe(end_dev_topic)
    test_client.subscribe(topic2)
    test_client.subscribe(topic3)
    test_client.subscribe(topic4)

