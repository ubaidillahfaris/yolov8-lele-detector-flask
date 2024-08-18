from flask import Flask, jsonify, request
from models.PerhitunganLele import PerhitunganLele
from database.connection import get_connection,close_connection


class PerhitunganleleController:
    def index(self):
        pass

    def showYolo(self, request):
        # init database connection
        conn = get_connection()

        # get parameter
        param = request.args
        tanggal = param.get('tanggal', None)
        try:
            table_value = []
            with conn.cursor() as cursor:
                query = f"select * from perhitungan_leles pl order by pl.created_at desc"
                
                if tanggal:
                    query += f" WHERE tanggal = %s"
                    cursor.execute(query, (tanggal,))
                    perhitungan_leles = cursor.fetchall()
                else:
                    cursor.execute(query)
                    perhitungan_leles = cursor.fetchall()

                for row in perhitungan_leles:
                    table_value.append({
                        'id' : row[0],
                        'tanggal' : row[1],
                        'grade' : row[2],
                        'jumlah' : row[3],
                        'total_harga' : row[4],
                        'video_url' : f"{request.host_url}videos/{row[5]}",
                        'created_at' : row[6],
                    })
                
                if table_value != []:
                    return jsonify(table_value)
                else:
                    return jsonify({
                        'data' : None
                    })
        except Exception as e:
            return jsonify({
                'message' : 'Error',
                'detail' : e.args
            }) , 400

    def showKnn(self, request):
        # init database connection
        conn = get_connection()

        # get parameter
        param = request.args
        tanggal = param.get('tanggal', None)
        try:
            table_value = []
            with conn.cursor() as cursor:
                query = f"select plk.id, plk.tanggal , plk.grade , pl.jumlah , pl.harga, plk.file_path , plk.created_at , plk.updated_at  from perhitungan_lele_knns plk  join perhitungan_leles pl on pl.id = plk.id_perhitungan_yolo  order by plk.created_at desc"
                
                if tanggal:
                    query += f" WHERE tanggal = %s"
                    cursor.execute(query, (tanggal,))
                    perhitungan_leles = cursor.fetchall()
                else:
                    cursor.execute(query)
                    perhitungan_leles = cursor.fetchall()

                for row in perhitungan_leles:
                    table_value.append({
                        'id' : row[0],
                        'tanggal' : row[1],
                        'grade' : row[2],
                        'jumlah' : row[3],
                        'total_harga' : row[4],
                        'video_url' : f"{request.host_url}videos/{row[5]}",
                        'created_at' : row[6],
                    })
                
                if table_value != []:
                    return jsonify(table_value)
                else:
                    return jsonify({
                        'data' : None
                    })
        except Exception as e:
            return jsonify({
                'message' : 'Error',
                'detail' : e.args
            }) , 400

    def store(self):
        try:
            
            for value in range(1,100000):
                PerhitunganLele().save({
                    'tanggal' : '2024-06-01',
                    'jumlah' : value,
                })
                pass
            return jsonify({
                    'message' : 'Perhitungan Controller'
            })
        except Exception as e:
            raise e

    def update(self, id):
        # Code to update a record by ID
        pass

    def delete(self, id):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM perhitungan_leles WHERE id = %s;", (id,))
            conn.commit()
            close_connection()

            return jsonify({
                    'message' : 'Data perhitungan lele dihapus'
            })
        except Exception as e:
            raise e
