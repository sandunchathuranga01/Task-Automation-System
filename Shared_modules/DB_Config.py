import mysql.connector
from mysql.connector import Error
from log_script import logger

# Function to create and return a database connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port='3305',
            user='root',
            password='sandun123',
            database='vms_project'
        )
        if connection.is_connected():

            logger.info("Connection to MySQL DB successful")
            return connection
        else:
            return None
    except Error as e:
        logger.error(f"The error '{e}' occurred while trying to connect to the database")
        return None


