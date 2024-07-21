import time
import os
import cv2
from uuid_extensions import uuid7, uuid7str
from celery import Celery
from datetime import datetime


celery = Celery(__name__, backend="redis://", broker="redis://")
# celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://103.175.219.61:6379")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://103.175.219.61:6379")

@celery.task(name="dummy_task")
def dummy_task():
    folder = os.getcwd()
    os.makedirs(folder, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%s")
    with open(f"{folder}/task-{now}.txt", "w") as f:
        f.write("hello!")
    return True

@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

@celery.task(name="frame_video")
def frame_video(temp, induk, FACEPATH):
    cam = cv2.VideoCapture(temp)
    frame_count = 0
    while True:
        ret, frame = cam.read()

        if not ret:
            break
        
        frame_count += 1

        folder = FACEPATH+"/"+induk

        if os.path.isdir(folder):
            print("Exists")
        else:
            print("Doesn't exists")
            os.mkdir(folder)

        filename = uuid7str()
        location = folder+"/"+filename+".jpg"

        cv2.imwrite(location, frame) 

    cam.release()
    os.remove(temp)
    return True