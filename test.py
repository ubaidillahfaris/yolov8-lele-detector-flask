import subprocess

# Definisikan variabel
home = '/path/to/home'  # Ganti dengan path ke direktori HOME
dataset_location = '/path/to/dataset'  # Ganti dengan path ke direktori dataset

# Perintah YOLO dalam bentuk string
command = f"yolo task=detect mode=val model=runs/detect/train/weights/best.pt data=data/dataLele.yaml"

# Jalankan perintah menggunakan subprocess
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# Cetak output dan error (jika ada)
print("Output:")
print(stdout.decode())

if stderr:
    print("Error:")
    print(stderr.decode())
