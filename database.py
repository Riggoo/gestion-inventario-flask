import os
import pymysql
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def obtener_conexion():
    """Establece una conexión segura con la base de datos MySQL."""
    try:
        conexion = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor 
        )
        return conexion
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    