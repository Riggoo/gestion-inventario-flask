import sqlite3
import os

def obtener_conexion():
    # Se crea un archivo de base de datos local dentro del servidor
    base_datos = "inventario_produccion.db"
    
    try:
        # Conectamos y configuramos para que devuelva diccionarios (igual que hacía PyMySQL)
        conexion = sqlite3.connect(base_datos)
        conexion.row_factory = sqlite3.Row
        
        cursor = conexion.cursor()
        
        # 1. Creamos la tabla de usuarios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT NOT NULL UNIQUE,
                contrasena_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'empleado',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Creamos la tabla de productos si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock_actual INTEGER NOT NULL DEFAULT 0
            );
        """)
        
        conexion.commit()
        return conexion
    except Exception as e:
        print(f"Error en la base de datos: {e}")
        return None