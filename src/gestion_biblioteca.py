import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "biblioteca_db"

def create_database(cursor):
    """Crea la base de datos si no existe."""
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        print(f"Base de datos '{DB_NAME}' creada o ya existente.")
    except Error as e:
        print(f"Error al crear la base de datos: {e}")

def create_tables(conn):
    """Crea las tablas 'libros' y 'usuarios' en la base de datos."""
    cursor = conn.cursor()
    try:
        # Creación de la tabla 'libros'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(100) NOT NULL UNIQUE,
                autor VARCHAR(100) NOT NULL,
                disponible BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB;
        """)
        print("Tabla 'libros' creada o ya existente.")

        # Creación de la tabla 'usuarios'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB;
        """)
        print("Tabla 'usuarios' creada o ya existente.")
        conn.commit()
    except Error as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        cursor.close()

def insert_initial_data(conn):
    """Inserta datos iniciales en las tablas 'libros' y 'usuarios'."""
    cursor = conn.cursor()
    try:
        # Datos para libros
        libros = [
            ('Cien años de soledad', 'Gabriel García Márquez', True),
            ('El señor de los anillos', 'J.R.R. Tolkien', True),
            ('1984', 'George Orwell', False),
            ('Un mundo feliz', 'Aldous Huxley', True),
            ('Don Quijote de la Mancha', 'Miguel de Cervantes', True)
        ]
        cursor.executemany("INSERT INTO libros (titulo, autor, disponible) VALUES (%s, %s, %s)", libros)
        print(f"Insertados {cursor.rowcount} registros en la tabla 'libros'.")

        # Datos para usuarios
        usuarios = [
            ('Juan Perez',),
            ('Ana Garcia',),
            ('Carlos Sanchez',),
            ('Laura Martinez',),
            ('Pedro Rodriguez',)
        ]
        cursor.executemany("INSERT INTO usuarios (nombre) VALUES (%s)", usuarios)
        print(f"Insertados {cursor.rowcount} registros en la tabla 'usuarios'.")
        
        conn.commit()
    except Error as e:
        print(f"Error al insertar datos: {e}")
        conn.rollback() # Revertir cambios si hay un error
    finally:
        cursor.close()

def show_data(conn):
    """Muestra los datos de las tablas."""
    cursor = conn.cursor()
    print("\n--- Datos en 'libros' ---")
    cursor.execute("SELECT id, titulo, autor, disponible FROM libros")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Título: {row[1]}, Autor: {row[2]}, Disponible: {'Sí' if row[3] else 'No'}")

    print("\n--- Datos en 'usuarios' ---")
    cursor.execute("SELECT id, nombre FROM usuarios")
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nombre: {row[1]}")
    
    cursor.close()

def main():
    """Función principal para configurar y poblar la base de datos de la biblioteca."""
    conn = None
    try:
        # 1. Conexión inicial sin base de datos para crearla
        conn_init = mysql.connector.connect(
            host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD")
        )
        cursor_init = conn_init.cursor()
        create_database(cursor_init) # 2. Crea y verifica la BD
        cursor_init.close()
        conn_init.close()

        # Conexión a la base de datos 'biblioteca_db'
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=DB_NAME
        )
        
        create_tables(conn) # 3. Creación de tablas
        insert_initial_data(conn) # 4. Inserción de datos
        show_data(conn) # Verificación final

    except Error as e:
        print(f"Error en la operación principal: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("\nConexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()