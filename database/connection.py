# db_connection.py

import psycopg2
from psycopg2 import sql
from config.database import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Inisialisasi variabel global untuk koneksi
global_connection = None

def get_connection():
    global global_connection
    if global_connection is None:
        try:
            global_connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Database connection established.")
        except Exception as error:
            print(f"Error connecting to the database: {error}")
            global_connection = None
    return global_connection

def close_connection():
    global global_connection
    if global_connection:
        global_connection.close()
        global_connection = None
        print("Database connection closed.")
