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
            assert video_writer.isOpened(), f"Error opening video writer for {output_path}"

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

            cap.release()
            video_writer.release()
            cv2.destroyAllWindows()
            pass
       except Exception as e:
        raise e;

    def prosesKnn(self, video_path):
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

                        object_id = self.next_object_id
                        self.next_object_id += 1


                        if self.check_line_crossing(y1, y2, line_y) and object_id not in self.tracked_objects:
                            self.tracked_objects.append(object_id)

                            if pred_label in self.label_counts:
                                if pred_label in self.label_groups:
                                    matched_group = None
                                    for group_id, group_info in self.label_groups[pred_label].items():
                                        group_center = group_info['center']

                                        current_center = ((x1 + x2) // 2, (y1 + y2) // 2)
                                        distance = np.linalg.norm(np.array(group_center) - np.array(current_center))

                                        if distance < self.max_distance:
                                            matched_group = group_id
                                            break

                                    if matched_group is not None:
                                        self.label_groups[pred_label][matched_group]['objects'].append({
                                            'id': object_id,
                                            'bbox': (x1, y1, x2, y2)
                                        })
                                        self.label_groups[pred_label][matched_group]['path'].append(current_center)
                                    else:
                                        new_group_id = len(self.label_groups[pred_label]) + 1
                                        self.label_groups[pred_label][new_group_id] = {
                                            'objects': [{
                                                'id': object_id,
                                                'bbox': (x1, y1, x2, y2)
                                            }],
                                            'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                                            'path': [((x1 + x2) // 2, (y1 + y2) // 2)]
                                        }
                                else:
                                    self.label_groups[pred_label] = {
                                        1: {
                                            'objects': [{
                                                'id': object_id,
                                                'bbox': (x1, y1, x2, y2)
                                            }],
                                            'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                                            'path': [((x1 + x2) // 2, (y1 + y2) // 2)]
                                        }
                                    }
                            else:
                                self.label_counts[pred_label] = 1

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label_text = f"Label: {pred_label}, Conf: {confidence:.2f}"
                        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                for label, groups in self.label_groups.items():
                    for group_info in groups.values():
                        path = group_info['path']
                        if len(path) > 1:
                            for i in range(1, len(path)):
                                cv2.line(frame, path[i-1], path[i], (0, 255, 0), 2)

                cv2.line(frame, line_points[0], line_points[1], (0, 0, 255), 2)
                out.write(frame)

            cap.release()
            out.release()

            output = [{"label": label, "total": len(group_info['objects'])} for label, groups in self.label_groups.items() for group_info in groups.values()]

            label_groups = defaultdict(list)
            for item in output:
                label = item['label']
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
                cursor.execute("""
                    INSERT INTO perhitungan_lele_knns (tanggal, grade, jumlah, file_path, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (timestamp, label, jumlah, video_path, timestamp, timestamp))
            
            conn.commit()
            close_connection()
            print("Data berhasil disimpan ke database.")

        except Exception as e:
            print(f"Error during video processing: {e}")

        
    def check_line_crossing(self, y1, y2, line_y):
        return (y1 < line_y and y2 >= line_y)