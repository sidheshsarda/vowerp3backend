import mysql.connector
from config import Config

def get_db_connection():
    """
    Establish a database connection using configuration from Config.
    Returns a MySQL connection object.
    """
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        raise e
