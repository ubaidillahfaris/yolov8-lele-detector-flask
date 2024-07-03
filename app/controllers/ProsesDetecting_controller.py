from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2
import torch
import os
import numpy as np 
from models.PerhitunganLele import PerhitunganLele
from models.harga import Harga
from database.connection import get_connection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import joblib
# from sklearn.neighbors import KNeighborsClassifier
# import sklearn.metrics

class ProsesdetectingController:
    def proses(self, video_path):
       try:
            conn = get_connection()
            # set date now
            today = datetime.now()
            d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")

            # file model lele
            model = YOLO("model/Lele/best.pt")
            # ====================

            # Ensure the model is using the GPU
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"Using device: {device}")
            model.to(device)

            # Open the video file
            cap = cv2.VideoCapture(video_path)
            assert cap.isOpened(), f"Error reading video file {video_path}"

            # Get video properties
            w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
            print(f"Video properties - Width: {w}, Height: {h}, FPS: {fps}")

            # Define line points
            line_points = [(20, 600), (1080, 600)]

            # Video writer
            save_video_dir = 'assets/videos'
            os.makedirs(save_video_dir, exist_ok=True)
            output_path = os.path.join(save_video_dir, f"{d_m_y_h_m}_object_counting_output.mp4")
            video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            assert video_writer.isOpened(), f"Error opening video writer for {output_path}"

            # Initialize Object Counter with desired settings
            counter = object_counter.ObjectCounter(
                view_img=True,  # Change to True if you want to view the frames while processing
                reg_pts=line_points,
                classes_names=model.names,
                draw_tracks=False,
                line_thickness=2,
            )
           
            while cap.isOpened():
                success, im0 = cap.read()
                if not success:
                    print("Video frame is empty or video processing has been successfully completed.")
                    break

                # Perform prediction with the model on the current frame
                tracks = model.track(im0, persist=True, conf=0.1, verbose=True, device=device)
                # Count objects and draw bounding boxes
                im0 = counter.start_counting(im0, tracks)
                print(counter.class_wise_count)
                
                video_writer.write(im0)

            data_dict = counter.class_wise_count

            for grade, values in data_dict.items():
                total_price = 0
                out = values['OUT']
                in_val = values['IN']

                if out > 0:
                    with conn.cursor() as cursor:
                        query = f"SELECT * FROM hargas WHERE grade = %s"
                        cursor.execute(query, (grade,))
                        harga = cursor.fetchone()
                        if harga and len(harga) > 2:
                            total_price = harga[2] * (out - in_val)

                    PerhitunganLele.create({
                        'grade': grade,
                        'tanggal': datetime.now(),
                        'jumlah': out - in_val,
                        'harga' : total_price,
                        'file_path' : f"videos/{d_m_y_h_m}_object_counting_output.mp4",
                    })

            # Release video resources
            cap.release()
            video_writer.release()
            cv2.destroyAllWindows()
            pass
       except Exception as e:
        raise e;

    def prosesKnn(self, video_path):
        try:
            # set date now
            today = datetime.now()
            d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")

            
            # file model lele
            model = YOLO("model/Lele/best.pt")

            # Memuat model KNN yang telah dilatih sebelumnya
            knn = joblib.load('model/Lele/knn_model.pkl')
            
            
            save_video_dir = 'assets/videos'
            os.makedirs(save_video_dir, exist_ok=True)
            output_video_path = os.path.join(save_video_dir, f"{d_m_y_h_m}_knn_object_counting_output.mp4")

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Error: Tidak bisa memuat video.")
                return

            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"FPS pada video: {fps}")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model(frame)

                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        w = x2 - x1
                        h = y2 - y1
                        confidence = box.conf.cpu().numpy()[0]

                        pred_label = knn.predict([[w, h]])[0]

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label_text = f"Label: {pred_label}, Conf: {confidence:.2f}"
                        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                out.write(frame)

            cap.release()
            out.release()
        except Exception as e:
            print("ERROR::")
            raise e