import base64
import struct


# TEMPORARY SOLUTION FOR PLUG & SENSE DATA
def parse_plug_n_sense_str(raw_payload):
    bytearray_raw = bytearray(base64.b64decode(raw_payload))
    # "sensor_id1=v1/sensor_id2=v2/...//"
    payload_str = bytearray_raw.decode()
    payload_str = payload_str.split("/")
    data = []
    for value_pair in payload_str:
        value_pair_array = value_pair.split("=")
        if len(value_pair_array) == 2:
            try:
                # valid format
                sensor_id = int(value_pair_array[0])
                value = float(value_pair_array[1].replace(",", ".").replace(" ", "")) # change , to . and remove blank spaces
                data.append([sensor_id, value])
            except:
                print(f"error decoding plug&sense payload string: {value_pair}")

    return data


# payload_bytes should be a byte array containing only the sensor data payload
# (structure: sensor_type--data--sensor_type--data etc.)
def decode_LoRa_sensors(payload_bytes):
    n = 0
    data = []
    while n < len(payload_bytes):
        sensor_type = 256*int(payload_bytes[n]) + int(payload_bytes[n+1])  # sensor id is a 2-byte value
        n += 2

        # boolean sensor
        if sensor_type == 9999:  # TODO: UPDATE WHEN SENSOR ID HAS BEEN SET
            # single byte (bool value)
            sensor_data = struct.unpack('<f', payload_bytes[n])[0]
            n += 1

        # multi-later sensor
        elif sensor_type == 11 or sensor_type == 12:
            try:
                # three little endian 4-byte float in succession
                sensor_data = [struct.unpack('<f', payload_bytes[n+k:n+k+4])[0] for k in range(0, 12, 4)]
            except:
                print("ERROR with multilayer status message, msg payload: ", payload_bytes[n:])
                return None
            n += 12

        elif 1 <= sensor_type <= 10:  # single value sensor
            try:
                sensor_data = struct.unpack('<f', payload_bytes[n:n+4])[0]  # little endian 4-byte float
            except:
                # print(f"{len(payload_bytes)}")
                print(f"ERROR: payload data, sensor id ({sensor_type}): ", payload_bytes)
                sensor_data = None
            # raise ValueError("")
            n += 4

        elif sensor_type == 257:  # pump status message
            try:
                sensor_data = int(payload_bytes[n:].decode())
                data.append([sensor_type, sensor_data])
                # pump status messages are always on their own
                return data

            except:
                print("ERROR with pump status msg: ", payload_bytes[n:])
                return None

        # single float sensor
        else:
            print(f"UNRECOGNIZED SENSOR ID: {sensor_type}, payload: {payload_bytes}")
            sensor_data = None
            data.append([sensor_type, sensor_data])
            # raise ValueError("")
            n += 4

        data.append([sensor_type, sensor_data])

    return data


if __name__ == "__main__":

    test = '//1=21,479/2=21/3=4,340/5=0,  0/6=0,  0/7=0,  0'
    data = parse_plug_n_sense_str(test, test)
    print("end: ", data)