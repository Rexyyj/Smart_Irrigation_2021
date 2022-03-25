import cherrypy
import time
import json
import os
from DB_management.mySQL_queries import insert_sensor_data, connect
import cherrypy_cors


class DB_REST_interface(object):
    exposed = True

    def __init__(self):
        pass

    @cherrypy.tools.accept(media='application/json')
    def GET(self, *uri):
        global db_conn
        deviceID = uri[0]
        cmd = uri[1]

    def POST(self, *uri, **params):
        global db_conn
        # transmit sensor data to database
        # {"sensor_type": str, "sensor_data": sensor_dict};
        # sensor_dict: {"device_ID", sensor_type, rx_timestamp, sensor_reading}
        insert_sensor_data()


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
    DB_name = "new_db"
    DB_usn = "root"
    DB_psw = "4Wza^d7LwYP~={RB"

    # CONNECT TO DATABASE
    db_conn = connect(DB_usn, DB_psw, DB_name)

    catalog_ip = "smart-pot-catalog.herokuapp.com"
    catalog_port = ""

    # myIP = "127.0.0.1"
    # myPort = "8080"
    myIP = "0.0.0.0"
    myPort = os.getenv('PORT')

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
    cherrypy.config.update({"server.socket_host": str(myIP), "server.socket_port": int(myPort)})
    cherrypy.engine.start()
    cherrypy.engine.block()
