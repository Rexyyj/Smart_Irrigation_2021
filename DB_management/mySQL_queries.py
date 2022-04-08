import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import time
from datetime import datetime
import json
# APIs to access the DB
DEBUG = True
DATE_FORMAT_STR = "%Y-%m-%d %H:%M:%S"  # ex: 2022-03-18 16:17:05


# instantiate the DB connector
def connect(usn, psw, db, host=None, port=None):
    # %% Connect to database, raise error if any
    try:
        if host is None:
            # connect to localhost
            mydb = mysql.connector.connect(user=usn,
                                           password=psw,
                                           database=db)
        else:
            if port is None:
                mydb = mysql.connector.connect(user=usn,
                                               password=psw,
                                               host=host,
                                               database=db)
            else:
                mydb = mysql.connector.connect(user=usn,
                                               password=psw,
                                               host=host,
                                               database=db,
                                               port=port)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    return mydb


# query to insert data for preliminary test
def insert_preliminary_test_data(db_conn, tx_tmp, rx_gateway_tmp, rx_server_tmp, dev_id, data_list):
    """

    :param db_conn: an instance of MySQLConnection
    :param tx_tmp:
    :param rx_gateway_tmp:
    :param rx_server_tmp:
    :param dev_id:
    :param data_list:
    :return:
    """
    db_cursor = db_conn.cursor()
    for reading in data_list:
        # reading should have format [sensor_type, sensor_reading]
        query = (
            "INSERT INTO preliminary_test(device_ID, sensor_type, tx_timestamp, rx_gateway_timestamp, rx_server_timestamp, sensor_reading) VALUES (%s, %s, %s, %s, %s, %s);"
        )
        data = (dev_id, reading[0], tx_tmp, rx_gateway_tmp, rx_server_tmp, reading[1])
        try:
            db_cursor.execute(query, data)
        except:
            print(f"Error handling query: {query}, data: {data}")
            raise Exception
    # result = db_cursor.fetchall()
    # print("result: ", result)
    db_conn.commit()
    # close cursor
    db_cursor.close()

# ----------------------------------------------------------------------------------------------------------------------
# DATA QUERIES
# ----------------------------------------------------------------------------------------------------------------------
# soil weather station
#


def get_most_recent(db_conn, table, field_id, sensor_type):
    """

    :param db_conn: instance of mySQLconnection (returned by connect() function)
    :param table: the db table to query (single_value_sensor, multi_value_sensor, bool_value_sensor)
    :param field_id: id of the field to query
    :param sensor_type: id of the sensor type, if left empty all readings of a specific field id will be retrieved
    :return:
    """
    global DATE_FORMAT_STR
    # TODO: get list of device id in field
    db_cursor = db_conn.cursor()

    query = "SELECT device_id FROM device_list " \
            "WHERE field_id = %s;"
    values = (field_id,)
    try:
        db_cursor.execute(query, values)
    except:
        print(f"Error handling query: {query}")
        raise Exception
    result = db_cursor.fetchall()
    dev_id_list = []
    for el in result:
        dev_id_list.append(el[0])
    result = []
    # print("id list: ", dev_id_list)
    most_recent_tmp = datetime.fromtimestamp(0)
    for device_id in dev_id_list:
        tmp_query = f"SELECT MAX(tmp) FROM {table} " \
                    f"WHERE device_ID = %s AND " \
                    f"sensor_type = %s;"
        values = (device_id, sensor_type)
        try:
            db_cursor.execute(tmp_query, values)
        except:
            print(f"Error handling query: {query}")
            raise Exception
        result = db_cursor.fetchall()[0][0]
        if result is not None:
            if result > most_recent_tmp:
                most_recent_tmp = result
        # most_recent_tmp = db_cursor.fetchall()[0]
        # db_cursor = db_conn.cursor()
        # if sensor_type is None:
        #     query = f'SELECT * FROM {table} ' \
        #             f'WHERE device_id = %s AND ' \
        #             f'tmp BETWEEN %s AND %s;'
        #     values = (device_id, d1, d2)
        # else:
        #     query = f'SELECT * FROM {table} ' \
        #             f'WHERE sensor_type = %s AND ' \
        #                 f'device_id = %s AND' \
        #             f'tmp BETWEEN %s AND %s;'
        #     values = (sensor_type, device_id, d1, d2)
        # try:
        #     print("sending query: ", query, "; values: ", values)
        #     db_cursor.execute(query, values)
        # except:
        #     print(f"Error handling query: {query}")
        #     raise Exception
        # query_result = db_cursor.fetchall()
        # print(query_result)
        # result.append(db_cursor.fetchall())
        # print("result: ", result)
        # db_conn.commit()
    # close cursor
    query = f"SELECT * FROM {table} " \
            f"WHERE tmp = %s AND sensor_type = %s;"
    values = (most_recent_tmp, sensor_type)
    try:
        db_cursor.execute(query, values)
    except:
        print(f"Error handling query: {query}")
        raise Exception
    result = db_cursor.fetchall()
    db_cursor.close()
    return result


def get_sensor_data(db_conn, table, field_id, period, sensor_type = None, unix_tmp = False):
    """

    :param db_conn: instance of mySQLconnection (returned by connect() function)
    :param table: the db table to query (single_value_sensor, multi_value_sensor, bool_value_sensor)
    :param sensor_type: id of the sensor type, if left empty all readings of a specific field id will be retrieved
    :param field_id: id of the field to query
    :param period: list of format [d1, d2]; where d1 and d2 are datetime objects that delimitate the chosen period
    :param unix_tmp: flag to specify if timestamp in payload is a unix tmp
    :return:
    """
    global DATE_FORMAT_STR
    # TODO: get list of device id in field
    db_cursor = db_conn.cursor()

    query = "SELECT device_id FROM device_list " \
            "WHERE field_id = %s;"
    values = (field_id,)
    try:
        db_cursor.execute(query, values)
    except:
        print(f"Error handling query: {query}")
        raise Exception
    result = db_cursor.fetchall()
    dev_id_list = []
    for el in result:
        dev_id_list.append(el[0])
    result = []
    for device_id in dev_id_list:
        print(device_id)
        d1 = period[0]
        d2 = period[1]
        if unix_tmp:
            # convert into datetime str
            d1 = datetime.fromtimestamp(d1).strftime(DATE_FORMAT_STR)
            d2 = datetime.fromtimestamp(d2).strftime(DATE_FORMAT_STR)

        db_cursor = db_conn.cursor()
        if sensor_type is None:
            query = f'SELECT * FROM {table} ' \
                    f'WHERE device_id = %s AND ' \
                    f'tmp BETWEEN %s AND %s;'
            values = (device_id, d1, d2)
        else:
            query = f'SELECT * FROM {table} ' \
                    f'WHERE sensor_type = %s AND ' \
                    f'device_id = %s AND' \
                    f'tmp BETWEEN %s AND %s;'
            values = (sensor_type, device_id, d1, d2)
        try:
            print("sending query: ", query, "; values: ", values)
            db_cursor.execute(query, values)
        except:
            print(f"Error handling query: {query}")
            raise Exception
        query_result = db_cursor.fetchall()
        print(query_result)
        result.append(db_cursor.fetchall())
        # print("result: ", result)
        # db_conn.commit()
    # close cursor
    db_cursor.close()
    return result


# ----------------------------------------------------------------------------------------------------------------------
# DATA INSERTION
# ----------------------------------------------------------------------------------------------------------------------

# inserts all the data included in a single LoRa payload
def insert_sensor_data(db_conn, data_dict, unix_tmp = False):
    """

    :param unix_tmp: flag to specify if timestamp in payload is a unix tmp
    :param db_conn:
    :param data_dict: dictionary with struct: {"sensor_type": str, "sensor_data": sensor_dict};
    sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading,}
    :return:
    """

    global DATE_FORMAT_STR
    db_cursor = db_conn.cursor()
    dev_id = data_dict["sensor_data"]["device_ID"]
    sensor_type_id = data_dict["sensor_data"]["sensor_type"]
    tx_timestamp = data_dict["sensor_data"]["rx_timestamp"]

    if unix_tmp:
        # convert into datetime str
        tx_timestamp = datetime.fromtimestamp(tx_timestamp).strftime(DATE_FORMAT_STR)
    else:
        # assumed datetime obj
        tx_timestamp = tx_timestamp.strftime(DATE_FORMAT_STR)
    if data_dict["sensor_type"] is "single":

        sensor_reading = data_dict["sensor_data"]["sensor_reading"]

        query = (
            "INSERT INTO single_value_sensor(device_ID, sensor_type, tmp, filtered, sensor_reading) VALUES ("
            "%s, %s, %s, %s, %s); "
        )
        data = (dev_id, sensor_type_id, tx_timestamp, 0, sensor_reading)

    elif data_dict["sensor_type"] is "bool":
        sensor_reading = data_dict["sensor_data"]["sensor_reading"]

        query = (
            "INSERT INTO bool_value_sensor(device_ID, sensor_type, tx_timestamp, filtered, sensor_reading) VALUES ("
            "%s, %s, %s, %s, %s); "
        )
        data = (dev_id, sensor_type_id, tx_timestamp, 0, sensor_reading)

    elif data_dict["sensor_type"] is "multi":
        sensor_reading = data_dict["sensor_data"]["sensor_reading"] # should be a list

        query = (
            "INSERT INTO bool_value_sensor(device_ID, sensor_type, tx_timestamp, filtered, layer1, layer2, layer3"
            "layer4) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        )
        data = (dev_id, sensor_type_id, tx_timestamp, 0, sensor_reading[0], sensor_reading[1], sensor_reading[2],
                sensor_reading[3])

    else:
        print("error: invalid sensor typology: ", data_dict["sensor_typology"])
        return 0

    try:
        db_cursor.execute(query, data)
    except:
        print(f"Error handling query: {query}, data: {data}")
        raise Exception

    db_conn.commit()
    # close cursor
    db_cursor.close()
    return 1


def insert_ET_value(db_conn, data_dict, unix_tmp = False):
    """

    :param unix_tmp: flag to specify if timestamp in payload is a unix tmp
    :param db_conn:
    :param data_dict: dictionary of format {"field_id", "Et0_value", "tmp"}
    :return:
    """

    global DATE_FORMAT_STR
    db_cursor = db_conn.cursor()
    field_id = data_dict["field_id"]
    residual = data_dict["residual"]
    Et0_value = data_dict["Et0_value"]
    tmp = data_dict["tmp"]
    if unix_tmp:
        tmp_datetime = datetime.fromtimestamp(tmp).strftime(DATE_FORMAT_STR)
        query = (
            "INSERT INTO ET_values(field_id, ET0_value, residual, tmp) VALUES (%s, %s, %s, %s);"
        )
        data = (field_id, Et0_value, residual, tmp_datetime)
    else:
        query = (
            "INSERT INTO ET_values(field_id, ET0_value, residual, tmp) VALUES (%s, %s, %s, %s);"
        )
        data = (field_id, Et0_value, residual, tmp)

    try:
        if DEBUG:
            print("sending query: ", query)
        db_cursor.execute(query, data)
    except:
        print(f"Error handling query: {query}, data: {data}")
        raise Exception

    db_conn.commit()
    # close cursor
    db_cursor.close()
    return 1


if __name__ == "__main__":
    config_file = "config.json"

    with open(config_file, "r") as fp:
        config = json.load(fp)
    # print("current config: ", config)
    broker = config["broker"]
    port = config["port"]
    username = config["username"]
    password = config["password"]

    topic2 = config["topic2"]
    topic3 = config["topic3"]
    topic4 = config["topic4"]
    DB_usn = config["DB_usn"]
    DB_psw = config["DB_psw"]
    DB_name = config["DB_name"]
    DB_host = config["DB_host"]
    DB_port = config["DB_port"]
    db_connection = connect(DB_usn, DB_psw, DB_name, DB_host, DB_port)
    db_cursor = db_connection.cursor()

    d1 = datetime(2022, 3, 25)
    d2 = datetime(2022, 3, 26)
    query_period = [d1, d2]
    # results = get_sensor_data(db_connection, "single_value_sensor", 0, query_period)
    result = get_most_recent(db_connection, "single_value_sensor", 0, 1)
    print(result)
    # print(results)

