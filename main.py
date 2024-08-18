from flask import Flask,send_from_directory, jsonify, request, render_template
from controller.VideoProcessingController import VideoProcessingController
from datetime import datetime, timedelta
from database.connection import get_connection, close_connection
from app.controllers.PerhitunganLele_controller import PerhitunganleleController
from app.controllers.ProsesDetecting_controller import ProsesdetectingController
from app.controllers.HargaController_controller import Hargacontroller
from app.controllers.LogController import LogController
import threading
import time
import os


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

@app.route('/perhitungan/show/yolo', methods=['GET'])
def showYolo():
    return PerhitunganleleController().showYolo(request)

@app.route('/perhitungan/show/knn', methods=['GET'])
def showKnn():
    return PerhitunganleleController().showKnn(request)

@app.route('/perhitungan/delete/<id>', methods=['DELETE'])
def delete_riwayat(id):
    return PerhitunganleleController().delete(id)




@app.route('/harga/show',methods=['GET'])
def show_harga():
    return Hargacontroller().show(request)

@app.route('/harga/update/<id>',methods=['PUT'])
def update_harga(id):
    return Hargacontroller().update(request, id)

@app.route('/harga/create',methods=['POST'])
def create_harga():
    return Hargacontroller().store(request)

@app.route('/harga/delete/<id>',methods=['DELETE'])
def delete_harga(id):
    return Hargacontroller().delete(id)

@app.route('/log/show',methods=['GET'])
def show_log():
    return LogController().show()


@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    try:
        if os.path.isfile(os.path.join(FILE_DIR, f"videos/{filename}")):
            return send_from_directory(FILE_DIR, f"videos/{filename}", mimetype='video/mp4')
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        raise e



def add_job_to_queue(file_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO job_queue (file_path) VALUES (%s) RETURNING id;", (file_path,))
    job_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    close_connection()
    return job_id

def get_next_job():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM job_queue WHERE status = 'pending' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;")
    job = cur.fetchone()
    if job:
        job_id = job[0]
        cur.execute("UPDATE job_queue SET status = 'processing' WHERE id = %s;", (job_id,))
        conn.commit()
        cur.close()
        close_connection()
        return job_id
    cur.close()
    close_connection()
    return None

def process_job(job_id):
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now()
    d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")
    cur.execute("SELECT file_path FROM job_queue WHERE id = %s;", (job_id,))
    job = cur.fetchone()
    if job:
        file_path = job[0]
        try:
            # Lakukan pemrosesan video di sini
            getId = ProsesdetectingController().proses(file_path)
            ProsesdetectingController().prosesKnn(file_path, getId)
            cur.execute("DELETE FROM job_queue WHERE id = %s;", (job_id,))


            # insert log
           
            query = f"INSERT INTO log (keterangan, created_at, updated_at) VALUES (%s, %s, %s)"
            cur.execute(query, (f"Berhasil memproses data pada tanggal {today}",today,today))

            # cur.execute(query, (f"Gagal memproses data pada tanggal {today}",today,today),)
            conn.commit()
            cur.close()
            close_connection()
            return;
        except Exception as e:
            print("Error during video processing:", e)

    cur.execute(query, (f"Gagal memproses data pada tanggal {today}",today,today),)
    conn.commit()
    cur.close()
    close_connection()
    return;

def worker():
    conn = get_connection()  # Open the database connection outside the loop
    while True:
        job_id = get_next_job()
        if job_id:
            process_job(job_id)
        time.sleep(20)  # Add a 1-second delay between each iteration of the loop
    close_connection()

@app.route('/process_video', methods=['POST'])
def process_video():
    # cek require param
  
    if 'file' not in request.files:
        return jsonify({'error': 'No video file found in request'}), 400
    
    print(request.files);
    today = datetime.now()
    d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")

    # Simpan file sementara
    video_file = request.files['file']
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)
    video_path = os.path.join(upload_dir, f"{d_m_y_h_m}_{video_file.filename}")
    video_file.save(video_path)
    
    # Mulai threading untuk pemrosesan video
    job_id = add_job_to_queue(video_path)
    print(f"Job {job_id} added to queue path {video_path}")

    return jsonify({
        'message': 'Video processing job added to queue',
    })


def main():
    worker_thread = threading.Thread(target=worker)
    worker_thread.start()

if __name__ == "__main__":
    main()
    from waitress import serve
    serve(app, host='192.168.18.228', port=os.getenv('APP_PORT',8000), threads=4)
