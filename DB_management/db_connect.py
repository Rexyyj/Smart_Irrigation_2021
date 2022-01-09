import mysql.connector
from mysql.connector import errorcode


def connect(usn, psw, db, host=None):
    # %% Connect to database, raise error if any
    try:
        if host is None:
            # connect to localhost
            mydb = mysql.connector.connect(user=usn,
                                           password=psw,
                                           database=db)
        else:
            mydb = mysql.connector.connect(user=usn,
                                           password=psw,
                                           host=host,
                                           database=db)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    return mydb
