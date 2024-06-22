from ultralytics import YOLO, solutions
import cv2
import torch

# Load the model
model = YOLO("model/Lele/best.pt")

# Ensure the model is using the GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")
model.to(device)

# Open the video file
video_path = "uploads/WhatsApp Video 2024-06-08 at 19.00.53.mp4"
cap = cv2.VideoCapture(video_path)
assert cap.isOpened(), f"Error reading video file {video_path}"

# Get video properties
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
print(f"Video properties - Width: {w}, Height: {h}, FPS: {fps}")

# Define line points
line_points = [(20, 600), (1080, 600)]

# Video writer
output_path = "object_counting_output.mp4"
video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
assert video_writer.isOpened(), f"Error opening video writer for {output_path}"

# Init Object Counter
counter = solutions.ObjectCounter(
    view_img=False,  # Change to True if you want to view the frames while processing
    reg_pts=line_points,
    classes_names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

while cap.isOpened():
    success, im0 = cap.read()
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break

    # Perform prediction with the model on the current frame
    tracks = model.track(im0, persist=True, show=False, conf=0.1, verbose=True, device=device)

    # Count objects and draw bounding boxes
    im0 = counter.start_counting(im0, tracks)
    
    # Write the frame to the output video
    video_writer.write(im0)

# Release video resources
cap.release()
video_writer.release()
cv2.destroyAllWindows()

print(f"Processed video saved to {output_path}")
