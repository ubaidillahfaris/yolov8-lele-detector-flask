from flask import Flask, jsonify, request
from datetime import datetime, timedelta
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2
import torch
import os
import math
import numpy as np 
from models.PerhitunganLele import PerhitunganLele
from models.harga import Harga
from database.connection import get_connection


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

    def show(self, id):
        # Code to fetch a single record by ID
        pass

    def store(self):
        # Code to store a new record
        pass

    def update(self, id):
        # Code to update a record by ID
        pass

    def delete(self, id):
        # Code to delete a record by ID
        pass
