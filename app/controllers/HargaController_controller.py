from flask import Flask, jsonify, request
from database.connection import get_connection, close_connection
from models.harga import Harga
class Hargacontroller:
    def index(self):
        # Code to fetch all records
        pass

    def show(self, id):
        conn = get_connection()
        query = f"SELECT * FROM hargas ORDER BY grade ASC"

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
    
    def store(self, request):
        data = request.form
        conn = get_connection()
        try:
            values = (data.get('grade',None),data.get('harga',None))
            create = f"""INSERT INTO hargas (grade, harga, age)
                VALUES (%s, %s, 1); 
            """
            with conn.cursor() as cursor : 
                cursor.execute(create, values)
            conn.commit()
            close_connection()

            return jsonify({
               'message' : 'Behasil menyimpan data harga'
           })
        except Exception as e:
            return jsonify({
                'message' : e.args
            }), 500

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
            close_connection()
            return jsonify({
               'message' : 'Behasil memperbarui harga'
           })
        except Exception as e:
            return jsonify({
               'message' : e.args
           }), 500
   
    def delete(self, id):
        conn = get_connection()

        try:
            delete_query = f"""delete from hargas where id = %s """

            with conn.cursor() as cursor : 
                cursor.execute(delete_query, (id,))

            conn.commit()
            close_connection()
            return jsonify({
                'message' : 'Behasil menghapus harga'
            })

        except Exception as e:
            return jsonify({
               'message' : e.args
           }), 500
