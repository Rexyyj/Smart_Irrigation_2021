
# APIs to access the DB


# query to insert data for preliminary test
def insert_preliminary_test_data(db_conn, tx_tmp, rx_gateway_tmp, rx_server_tmp, dev_id, data_list):
    # db_conn must be an instance of MySQLConnection
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
