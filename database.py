from config import DATABASE
import mysql.connector as db_driver


class Database:

    _connection = None

    def __init__(self):
        if not Database._connection:
            Database._connection = db_driver.connect(**DATABASE)

    @staticmethod
    def get_connection() -> db_driver.MySQLConnection:
        if not Database._connection:
            Database()
        return Database._connection

# have to use commit() on connection
