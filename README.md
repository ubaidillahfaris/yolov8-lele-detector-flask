
# Yolov8 Lele detector (w/ Model)




## Installation

```bash
 -  git clone https://github.com/ubaidillahfaris/yolov8-lele-detector-flask.git <nama_project>
 -  cd <nama_project>
 -  python:
        python -m venv <target/folder/venv>
    python 3:
        python3 -m venv <target/folder/venv>
 -  source <target/folder/venv>/bin/activate
 -  pip install -r requirements.txt
 -  setting .env

```
    
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`APP_HOST`=ip_address

`APP_PORT`=port

`DB_HOST`=ip_database

`DB_PORT`=db_port

`DB_NAME`=db_name

`DB_USER`=db_username

`DB_PASSWORD`=db_password



## FAQ

#### Muncul error torch.lib

```bash
Traceback (most recent call last):
  File "/Users/faris/Python/lele_machine/main.py", line 3, in <module>
    from datetime import datetime, timedelta
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/faris/Python/lele_machine/controller/VideoProcessingController.py", line 2, in <module>
    from ultralytics import YOLO, solutions
  File "/Users/faris/Python/lele_machine/venv/lib/python3.12/site-packages/ultralytics/__init__.py", line 10, in <module>
    from ultralytics.data.explorer.explorer import Explorer
  File "/Users/faris/Python/lele_machine/venv/lib/python3.12/site-packages/ultralytics/data/__init__.py", line 3, in <module>
    from .base import BaseDataset
  File "/Users/faris/Python/lele_machine/venv/lib/python3.12/site-packages/ultralytics/data/base.py", line 15, in <module>
    from torch.utils.data import Dataset
  File "/Users/faris/Python/lele_machine/venv/lib/python3.12/site-packages/torch/__init__.py", line 237, in <module>
    from torch._C import *  # noqa: F403
```
Solusi:
-  pip install torch
- matikan service python. Jika anda menjalankan python main.py, matikan dengan cara ctrl+C

#### Penanda jika aplikasi berjalan

Tidak ada error muncul pada terminal


## 🔗 Links
https://github.com/ubaidillahfaris
