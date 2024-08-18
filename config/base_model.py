from database.connection import get_connection
from datetime import datetime
import psycopg2
import re

class Model:
    @classmethod
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()+'s';

    @classmethod
    def create(cls, data):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                keys = ','.join(data.keys())
                values = tuple(data.values())
                placeholders = ','.join(['%s'] * len(data))
                
                # Tambahkan created_at dan updated_at ke data jika tidak ada
                if 'created_at' not in data:
                    data['created_at'] = datetime.now()
                if 'updated_at' not in data:
                    data['updated_at'] = datetime.now()
                
                query = f"INSERT INTO {cls.__tablename__()} ({keys}, created_at, updated_at) VALUES ({placeholders}, %s, %s) RETURNING id"
                cursor.execute(query, values + (data['created_at'], data['updated_at']))
                
                new_id = cursor.fetchone()[0]
                conn.commit()
                return new_id;

        except psycopg2.Error as error:
            print(f"Error creating record: {error}")
            conn.rollback()
            return None

    @classmethod
    def delete(cls, model_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                query = f"DELETE FROM {cls.__tablename__()} WHERE id = %s"
                cursor.execute(query, (model_id,))
                conn.commit()
                print("Record deleted successfully.")
        except psycopg2.Error as error:
            print(f"Error deleting record: {error}")
            conn.rollback()

    @classmethod
    def truncate(cls):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                query = f"DELETE FROM {cls.__tablename__()}"
                cursor.execute(query)
                conn.commit()
        except psycopg2.Error as error:
            print(f"Error truncated record: {error}")
            conn.rollback()


        

