from flask import Flask, jsonify, request
from database.connection import get_connection
from models.harga import Harga
class Hargacontroller:
    def index(self):
        # Code to fetch all records
        pass

    def show(self, id):
        conn = get_connection()
        query = f"SELECT * FROM hargas"

        try:
            with conn.cursor() as cursor : 
                cursor.execute(query)
                harga = []

                for value in cursor.fetchall():
                    harga.append({
                        'id' : value[0],
                        'grade' : value[1],
                        'harga' : value[2],
                    })
                    pass
                return jsonify(harga)
        except Exception as e:
           return jsonify({
               'message' : e.args
           }), 500
    
    def store(self):
        # Code to store a new record
        pass

    def update(self,request, id):
        data = request.form
        conn = get_connection()
        try:
            values = (data.get('grade',None),data.get('harga',None),id)
            update_query = f"""UPDATE hargas
                SET grade = %s, harga = %s
                WHERE id = %s
            """
            with conn.cursor() as cursor : 
                cursor.execute(update_query, values)

            conn.commit()


            return jsonify({
               'message' : 'Behasil memperbarui harga'
           })
        except Exception as e:
            return jsonify({
               'message' : e.args
           }), 500
    def delete(self, id):
        # Code to delete a record by ID
        pass
