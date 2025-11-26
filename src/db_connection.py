# db_connection.py
import mysql.connector

def get_conn():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='eventos_isw25',   # o el nombre que usaste
            user='root',
            password='mysqloscar12'   
        )
        if connection.is_connected():
            return connection
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None