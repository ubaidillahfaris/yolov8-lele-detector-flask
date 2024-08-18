import cv2
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import torch
import os
import numpy as np 
from models.PerhitunganLele import PerhitunganLele
from models.harga import Harga
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
from collections import defaultdict
from database.connection import get_connection, close_connection
from collections import OrderedDict

class ProsesdetectingController:

    def __init__(self):
        self.next_object_id = 0
        self.tracked_objects = []
        self.label_counts = defaultdict(int)
        self.label_groups = defaultdict(dict)
        self.max_distance = 170 
       
    def proses(self, video_path):
       try:
            conn = get_connection()
            today = datetime.now()
            d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")

            model = YOLO("model/Lele/best.pt")

            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"Using device: {device}")
            model.to(device)

            cap = cv2.VideoCapture(video_path)
            assert cap.isOpened(), f"Error reading video file {video_path}"

            w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
            print(f"Video properties - Width: {w}, Height: {h}, FPS: {fps}")

            line_points = [(20, 600), (1080, 600)]

            save_video_dir = 'assets/videos'
            os.makedirs(save_video_dir, exist_ok=True)
            output_path = os.path.join(save_video_dir, f"{d_m_y_h_m}_object_counting_output.mp4")
            video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            # assert video_writer.isOpened(), f"Error opening video writer for {output_path}"

            counter = object_counter.ObjectCounter(
                view_img=True, 
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

                
                tracks = model.track(im0, persist=True, conf=0.1, verbose=True, device=device)
                
                im0 = counter.start_counting(im0, tracks)
                print(counter.class_wise_count)
                
                video_writer.write(im0)

            data_dict = counter.class_wise_count
            
            id_list = [];

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

                    idTemp = PerhitunganLele.create({
                        'grade': grade,
                        'tanggal': datetime.now(),
                        'jumlah': out - in_val,
                        'harga': total_price,
                        'lele_in' : in_val,
                        'lele_out' : out,
                        'file_path': f"{d_m_y_h_m}_object_counting_output.mp4",
                    })
                    
                    id_list.append({'id': idTemp, 'grade': grade})

            cap.release()
            video_writer.release()
            cv2.destroyAllWindows()
            return id_list
       
       
       except Exception as e:
        raise e;

    def prosesKnn(self, video_path, idList):
        print('proses KNN')
        try:
            today = datetime.now()
            d_m_y_h_m = today.strftime("%d_%m_%Y_%H_%M")

            model = YOLO("model/Lele/best.pt")

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

            line_y = 600
            line_points = [(20, line_y), (1080, line_y)]
            # Inisialisasi count
            total_ikan_masuk = 0
            total_ikan_keluar = 0

            # Instance tracker
            fish_tracker = FishTracker()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                results = model(frame)
                centroids = []

                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        w = x2 - x1
                        h = y2 - y1
                        confidence = box.conf.cpu().numpy()[0]

                        # Predict the label using KNN
                        pred_label = knn.predict([[w, h]])[0]

                        # Calculate the centroid manually
                        centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
                        centroids.append(centroid)

                # Update tracked objects based on centroids
                tracked_objects = fish_tracker.update(centroids)

                # Clear all previous bounding boxes
                for object_id, centroid in tracked_objects.items():
                    xx1, yy1, xx2, yy2 = centroid[0] - 20, centroid[1] - 20, centroid[0] + 20, centroid[1] + 20

                    # Detect crossing and track object if not already tracked
                    if fish_tracker.check_line_crossing(yy1, yy2, line_y):
                        if object_id not in self.tracked_objects:
                            self.tracked_objects.append(object_id)

                            # Determine if the object is entering or exiting
                            if yy1 > line_y and yy2 >= line_y:
                                movement_text = "Ikan Masuk"
                                total_ikan_masuk += 1
                            else:
                                movement_text = ""

                            # Add the movement text to the frame
                            if movement_text:
                                cv2.putText(frame, f"{movement_text}, yy1: {yy1} - yy2 {yy2}", (xx1, yy1 - 30), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # Handle cases where objects start below the line
                    elif yy1 > line_y and object_id not in self.tracked_objects:
                        self.tracked_objects.append(object_id)
                        movement_text = "Ikan Masuk"
                        total_ikan_masuk += 1

                        # Add the movement text to the frame
                        cv2.putText(frame, f"{movement_text}, yy1: {yy1} - yy2 {yy2}", (xx1, yy1 - 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                    # Draw bounding box and label
                    cv2.rectangle(frame, (xx1, yy1), (xx2, yy2), (0, 255, 0), 2)
                    label_text = f"Label: {pred_label}, Conf: {confidence:.2f}, Label-id: {object_id}"
                    cv2.putText(frame, label_text, (xx1, yy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Draw the line for detecting entry and exit
                cv2.line(frame, line_points[0], line_points[1], (0, 0, 255), 2)

                # Display the count of fish entering and exiting
                cv2.putText(frame, f"Total Ikan Masuk: {total_ikan_masuk}", (frame.shape[1] - 250, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Total Ikan Keluar: {total_ikan_keluar}", (frame.shape[1] - 250, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                out.write(frame)


            cap.release()
            out.release()

            output = [{"label": label, "total": len(group_info['objects'])} for label, groups in self.label_groups.items() for group_info in groups.values()]

            label_groups = defaultdict(list)
            for item in output:

                label = f"lele{item['label']}"
                total = item['total']
                label_groups[label].append(total)

            label_counts = {}
            for label, totals in label_groups.items():
                label_counts[label] = len(totals)

            conn = get_connection()
            if conn is None:
                print("Failed to connect to the database.")
                return

            cursor = conn.cursor()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for label, jumlah in label_counts.items():
                grade_id = None
                for value in idList:
                    if value['grade'] == label:
                        grade_id = value['id']
                        break

                if grade_id is not None:
                    cursor.execute("""
                        INSERT INTO perhitungan_lele_knns (tanggal, grade, jumlah, file_path, created_at, updated_at, id_perhitungan_yolo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (timestamp, label, jumlah, f"{d_m_y_h_m}_knn_object_counting_output.mp4", timestamp, timestamp, grade_id))

            
            conn.commit()
            close_connection()
            print("Data berhasil disimpan ke database.")

        except Exception as e:
            print(f"Error during video processing: {e}")


class FishTracker:
    def __init__(self, max_distance=50):
        self.next_object_id = 0
        self.tracked_objects = {}
        self.max_distance = max_distance  # Maximum distance to consider the same object

    def register(self, centroid):
        self.tracked_objects[self.next_object_id] = centroid
        self.next_object_id += 1
    
    def check_line_crossing(self, y1, y2, line_y):
        return (y1 < line_y and y2 >= line_y)
    
    def update(self, centroids):
        if len(self.tracked_objects) == 0:
            # Register all centroids as new objects
            for centroid in centroids:
                self.register(centroid)
        else:
            object_ids = list(self.tracked_objects.keys())
            object_centroids = list(self.tracked_objects.values())

            # Compute distance matrix
            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - centroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                object_id = object_ids[row]
                self.tracked_objects[object_id] = centroids[col]

                used_rows.add(row)
                used_cols.add(col)

            # Register new centroids as new objects
            for col in set(range(len(centroids))).difference(used_cols):
                self.register(centroids[col])

        return self.tracked_objects