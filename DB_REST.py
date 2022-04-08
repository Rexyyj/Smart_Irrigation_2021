import cherrypy
import time
import json
import os
from DB_management.mySQL_queries import insert_sensor_data, connect, get_sensor_data, get_most_recent
from datetime import datetime
import cherrypy_cors


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return (str(z))
        else:
            return super().default(z)


class DB_REST_interface(object):
    exposed = True

    def __init__(self):
        pass

    @cherrypy.tools.accept(media='application/json')
    def GET(self, *uri):
        global db_conn
        if len(uri) != 0:
            req = uri[0]

            if req == "sensor_data_most_recent":
                # req url : /sensor_data_most_recent/field_id/sensor_id
                # ex: /sensor_data_most_recent/0/6
                try:
                    field_id = uri[1]
                    sensor_id = uri[2]
                except:
                    print("ERROR: invalid url format")
                    return
                try:
                    sensor_id = int(sensor_id)
                except:
                    print("ERROR: provided sensor_id is not an int")
                    return

                sensor_data = get_most_recent(db_conn, "single_value_sensor", field_id, sensor_id)
                return json.dumps(sensor_data, cls=DateTimeEncoder)

            else:
                return "invalid url"
            # data body of the request
            # input_json = cherrypy.request.body.read()
            # try:
            #     input_dict = json.loads(input_json)
            #     print(input_dict)
            # except:
            #     print("ERROR: invalid json in request body: ", input_json)
        #     return

    def POST(self, *uri, **params):
        global db_conn
        # transmit sensor data to database
        # {"sensor_type": str, "sensor_data": sensor_dict};
        # sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading}
        # insert_sensor_data()
        pass


if __name__ == '__main__':
    # retrieve topic data from the home catalog
    # file = open("configFile.json", "r")
    # jsonString = file.read()
    # file.close()
    # data = json.loads(jsonString)
    # catalog_ip = data["resourceCatalog"]["ip"]
    # catalog_port = data["resourceCatalog"]["port"]
    # myIP = data["manualMode"]["ip"]
    # myPort = data["manualMode"]["port"]

    # DATABASE CREDENTIALS
    # TODO: GET THEM FROM config.json
    config_file = "config.json"
    with open(config_file, "r") as fp:
        config = json.load(fp)

    DB_usn = config["DB_usn"]
    DB_psw = config["DB_psw"]
    DB_name = config["DB_name"]
    DB_host = config["DB_host"]
    DB_port = config["DB_port"]

    # CONNECT TO DATABASE
    db_conn = connect(DB_usn, DB_psw, DB_name, DB_host, DB_port)
    if db_conn is None:
        raise Exception("ERROR: could not connect to db")

    # web server port
    myIP = "127.0.0.1"
    myPort = os.getenv('PORT')

    # results = get_sensor_data(db_connection, "single_value_sensor", 0, query_period)

    def CORS():
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True,
            'tools.CORS.on': True,
            'tools.response_headers.on': True
        }
    }
    cherrypy.tree.mount(DB_REST_interface(), '/', conf)
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    # cherrypy.config.update({"server.socket_host": str(myIP), "server.socket_port": int(myPort)})
    cherrypy.engine.start()
    cherrypy.engine.block()
