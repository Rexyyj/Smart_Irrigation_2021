from DB_management.mySQL_queries import insert_preliminary_test_data
from DB_management.db_connect import connect
from paho.mqtt import client as _mqtt_client
import json
import base64
import struct

# the things network MQTT integration credentials
broker = 'eu1.cloud.thethings.network'
port = 1883
end_dev_topic = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"
topic = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"
username = 'arduino-lora-test-rex@ttn'
password = 'NNSXS.AQKUJD6CGFB3HKLERXNMYVQBTN7VGXQXBLMABXQ.H2WWY5RFV5I5BPR4LJ3R7QVYD76HZYQOF72EL4LLXY7JWVR3HMSQ'
file_name = "./received.json"

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
        # transmitter_id = MQTT_payload_json["end_device_ids"]["device_id"]

        # payload (raw bits, needs decoding)
        payload_raw = MQTT_payload_json["uplink_message"]["frm_payload"]

        # # largest timestamp, assuming it marks when the packet arrived at the network server
        # rx_server_timestamp = MQTT_payload_json["received_at"]
        #
        # # 2nd largest timestamp, assuming it marks when the LoRa packet arrived at the gateway
        # rx_gateway_timestamp = MQTT_payload_json["uplink_message"]["received_at"]
        #
        # # these are the two lowest timestamp in the packet (and they are equal), assuming they mark tx time
        # tx_timestamp = MQTT_payload_json["uplink_message"]["settings"]["time"]
        # tx_timestamp2 = MQTT_payload_json["uplink_message"]["rx_metadata"][0]["time"]
        # tx_unix_timestamp = MQTT_payload_json["uplink_message"]["settings"]["timestamp"]
        # tx_unix_timestamp2 = MQTT_payload_json["uplink_message"]["rx_metadata"][0]["timestamp"]
        # NOTE: this isn't actually the unix timestamp

        rx_server_timestamp = None
        rx_gateway_timestamp = None
        tx_timestamp = None
        # search if timestamps are in the json packet, if a tmp is not found, NULL value will be inserted in the db
        if "received_at" in MQTT_payload_json:
            rx_server_timestamp = MQTT_payload_json["received_at"]
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

        decoded_data = self.decode_payload(payload_raw)
        if self.DEBUG:
            print(f"decoded payload: {decoded_data}, timestamps: tx: {tx_timestamp}, rx_gateway: {rx_gateway_timestamp}"
                  f", rx_server: {rx_server_timestamp}")

        # insert into database
        insert_preliminary_test_data(self.db_connection, tx_timestamp, rx_gateway_timestamp, rx_server_timestamp,
                                     decoded_data["device_ID"], decoded_data["data"])

    def subscribe(self, device_topics):
        self.MQTT_client.subscribe(device_topics)

    def decode_payload(self, raw_payload):
        # FOR NOW ONLY SUPPORTS SOIL AND TEMPERATURE SENSORS

        # decoded_data = {"dev_id": , "data": [["sensor_id", ], ["", ]]}
        decoded_data = {}

        # read the payload string into a base 64 byte array
        bytearray_raw = bytearray(base64.b64decode(raw_payload))
        decoded_data["device_ID"] = bytearray_raw[0]
        decoded_data["data"] = []
        n = 1
        while n < len(bytearray_raw):
            sensor_type = bytearray_raw[n]
            try:
                sensor_data = struct.unpack('<f', bytearray_raw[n+1:n+5])[0]  # little endian 4-byte float
            except:
                print(f"{len(bytearray_raw)}")
                raise ValueError("")
            decoded_data["data"].append([sensor_type, sensor_data])
            n += 5

        return decoded_data

    def start(self):
        # connect to broker
        self.MQTT_client.connect(self.broker, self.broker_port)
        # subscribe to topics
        for dev_topic in self.device_topics:
            self.subscribe(dev_topic)
        # start loop
        self.MQTT_client.loop_forever()

    def connect_to_db(self, DB_auth_usn, DB_auth_psw, DB_name):
        if self.DEBUG:
            print("connecting to DB")
        self.db_connection = connect(DB_auth_usn, DB_auth_psw, DB_name)
        if self.db_connection is None:
            raise Exception("ERROR:Could not connect to Database")
        if self.DEBUG:
            print("connection successful")


if __name__ == '__main__':
    topics = ["v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233246f04/up"]

    test_client = MQTTClient("test-213", broker, port, mqtt_auth=(username, password), device_topics=topics)
    test_client.connect_to_db(DB_usn, DB_psw, DB_name)
    test_client.start()
    test_client.subscribe(end_dev_topic)

