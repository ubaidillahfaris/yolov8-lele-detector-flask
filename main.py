from flask import Flask,send_from_directory, jsonify, request
from controller.VideoProcessingController import VideoProcessingController
from datetime import datetime, timedelta
from database.connection import get_connection, close_connection
from app.controllers.PerhitunganLele_controller import PerhitunganleleController
from app.controllers.ProsesDetecting_controller import ProsesdetectingController
from app.controllers.HargaController_controller import Hargacontroller
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
FILE_DIR = os.path.join(os.getcwd(), 'assets')

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message': 'Success'})

@app.route('/perhitungan/create', methods=['GET'])
def create():
    return PerhitunganleleController().store()

@app.route('/perhitungan/truncate', methods=['GET'])
def delete():
    return PerhitunganleleController().delete()

@app.route('/perhitungan/show', methods=['GET'])
def show():
    return PerhitunganleleController().show(request)

@app.route('/harga/show',methods=['GET'])
def show_harga():
    return Hargacontroller().show(request)

@app.route('/harga/update/<id>',methods=['PUT'])
def update_harga(id):
    return Hargacontroller().update(request, id)


@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    try:
        if os.path.isfile(os.path.join(FILE_DIR, f"videos/{filename}")):
            return send_from_directory(FILE_DIR, f"videos/{filename}", mimetype='video/mp4')
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        raise e

@app.route('/process_video', methods=['POST'])
def process_video():
    # cek require param
    if 'file' not in request.files:
        return jsonify({'error': 'No video file found in request'}), 400
    param = request
    # processing video
    ProsesdetectingController().proses(param)
    return jsonify({
        'message': 'Video processing started',
    })


def main():
    conn = get_connection()
    if conn:
        try:
            # Lakukan operasi database di sini
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            print(f"App ready to use :)")
        except Exception as error:
            print(f"Cannot use app")

if __name__ == "__main__":
    main()
    from waitress import serve
    serve(app, host=os.getenv('APP_HOST','127.0.0.1'), port=os.getenv('APP_PORT',8000))
