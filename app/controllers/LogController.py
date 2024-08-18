from flask import Flask, jsonify, request
from database.connection import get_connection, close_connection

class LogController:
    def show(self):
        conn = get_connection()
        query = f"SELECT * FROM log ORDER BY created_at DESC"
        try:
            with conn.cursor() as cursor : 
                cursor.execute(query)
                harga = []

                for value in cursor.fetchall():
                    harga.append({
                        'id' : value[0],
                        'keterangan' : value[1],
                    })
                    pass
                return jsonify(harga)
        except Exception as e:
            return jsonify({
               'message' : e.args
            }), 500
        