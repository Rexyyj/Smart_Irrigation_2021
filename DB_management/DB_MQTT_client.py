import time
import traceback
import sys
from mySQL_queries import insert_preliminary_test_data, connect, insert_sensor_data
from paho.mqtt import client as _mqtt_client
from payload_decoding import decode_LoRa_sensors, parse_plug_n_sense_str
import json
import base64
import struct
from datetime import datetime
import time

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def get_sensor_type(sensor_id):
    multi_layer_sensors = [17, 18]
    single_layer_sensors = [1, 2, 3, 4, 5, 6, 7]
    bool_sensors = []
    pump_message = [257]

    if sensor_id in single_layer_sensors:
        return "single"
    if sensor_id in bool_sensors:
        return "bool"
    if sensor_id in multi_layer_sensors:
        return "multi"

    return None  # unrecognized ID


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
        try:
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
                MQTT_payload_data = MQTT_payload_json
            elif "data" in MQTT_payload_json:
                MQTT_payload_data = MQTT_payload_json["data"]
            else:
                print("INVALID MY THINGS NETWORK PACKET")
                with open("err_packt_log.json", "a") as fp:
                    fp.write(str(MQTT_payload_json)+"\n")
                # TODO: STORE BAD PACKET
                return

            if "frm_payload" in MQTT_payload_data["uplink_message"]:
                payload_raw = MQTT_payload_data["uplink_message"]["frm_payload"]
                # search if timestamps are in the json packet, if a tmp is not found, NULL value will be inserted in the db
                if "received_at" in MQTT_payload_data:
                    tx_timestamp = MQTT_payload_data["received_at"]
                if "uplink_message" in MQTT_payload_data:
                    if "received_at" in MQTT_payload_data["uplink_message"]:
                        rx_gateway_timestamp = MQTT_payload_data["uplink_message"]["received_at"]
                    if "settings" in MQTT_payload_data["uplink_message"]:
                        if "time" in MQTT_payload_data["uplink_message"]["settings"]:
                            tx_timestamp = MQTT_payload_data["uplink_message"]["settings"]["time"]
                    if tx_timestamp is None:
                        if "rx_metadata" in MQTT_payload_data["uplink_message"]:
                            if type(MQTT_payload_data["uplink_message"]["rx_metadata"]) is list:
                                for el in MQTT_payload_data["uplink_message"]["rx_metadata"]:
                                    if "time" in el:
                                        tx_timestamp = el["time"]
                                        break

            elif "raw_payload" in MQTT_payload_data:
                # ALTERNATE PACKET FORMAT
                if "received_at" in MQTT_payload_data:
                    tx_timestamp = MQTT_payload_data["data"]["received_at"]
                else:
                    print("ERROR: could not find timestamp for 'raw_payload '")
                    with open("err_packt_log.json", "a") as fp:
                        fp.write(str(MQTT_payload_json)+"\n")
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
    
            try:
                # TODO: THIS IS A TEMPORARY SOLUTION FOR PACKETS FROM PLUG&SENSE
                #  UPDATE WHEN THEIR FORMAT IS STANDARDIZED
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
                try:
                    # INSERT INTO DB
                    for sensor_pair in decoded_data["data"]:
                        if self.DEBUG:
                            print("inserting sensor data in DB")
                        # insert single db entry
                        sensor_type_id = int(sensor_pair[0])
                        sensor_value = sensor_pair[1]
                        data_dict = {"sensor_type": get_sensor_type(sensor_type_id), "sensor_data": {"device_ID": device_ID,
                                                                                    "sensor_type": sensor_type_id,
                                                                                    "rx_timestamp": tmp,
                                                                                    "sensor_reading": sensor_value}}
                        insert_sensor_data(self.db_connection, data_dict, DEBUG=self.DEBUG)
                        """
                        data_dict: dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
                        sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
                        """
                        # dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
                        # sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
                        # insert_preliminary_test_data(self.db_connection, tx_timestamp, rx_gateway_timestamp, rx_server_timestamp,
                        #                              decoded_data["device_ID"], decoded_data["data"])
                except Exception as e:
                    print("Printing only the traceback above the current stack frame")
                    print("".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
                    print("Printing the full traceback as if we had not caught it here...")
                    print(format_exception(e))

            except:
                print("inconsistent packet")
                with open("err_packt_log.json", "a") as fp:
                    fp.write(str(MQTT_payload_raw)+"\n")
        except:
            print("ERROR")

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

    config_file = "config.json"

    with open(config_file, "r") as fp:
        config = json.load(fp)
    print(config)
    broker = config["broker"]
    port = config["port"]
    username = config["username"]
    password = config["password"]

    topic2 = config["topic2"]
    topic3 = config["topic3"]
    topic4 = config["topic4"]
    topic_multi = "v3/arduino-lora-test-rex@ttn/devices/eui-a8610a3233206504/up"
    DB_usn = config["DB_usn"]
    DB_psw = config["DB_psw"]
    DB_name = config["DB_name"]
    DB_host = config["DB_host"]
    DB_port = config["DB_port"]
    topics = [topic2, topic3, topic4, topic_multi]
    test_client = MQTTClient("test-213", broker, port, mqtt_auth=(username, password), device_topics=topics)
    test_client.connect_to_db(DB_usn, DB_psw, DB_name, DB_host, DB_port)
    test_client.start()  # start the MQTT client and subscribe to gven topics



