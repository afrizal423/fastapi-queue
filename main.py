from worker import create_task, frame_video, celery
from celery.result import AsyncResult
from fastapi import Body, FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
import json
from uuid_extensions import uuid7, uuid7str
import os
import cv2


app = FastAPI()
FACEPATH = "KnownFaces"


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/tasks", status_code=201)
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = celery.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


@app.post("/enrollV")
async def enroll_video(induk: str, file: UploadFile=File(...)):
    accepted_file_type = ['video/mp4']
    if(file.content_type in accepted_file_type):
        folder_root=os.getcwd()+"/"
        filename = uuid7str()+".mp4"
        folder = "tmp_video/"
        filenya = folder_root+folder+filename
        
        print(filenya)
        with open(filenya, "wb") as f:
            f.write(await file.read())

        # proses dibawah ini tanpa queue
        # # temp = NamedTemporaryFile(delete=False)
        # # contents = file.file.read()
        # # with temp as f:
        # #     f.write(contents)
        # # print(temp.name)
        # cam = cv2.VideoCapture(filenya)
        # frame_count = 0
        # while True:
        #     ret, frame = cam.read()

        #     if not ret:
        #         break
            
        #     frame_count += 1

        #     folder = FACEPATH+"/"+induk

        #     if os.path.isdir(folder):
        #         print("Exists")
        #     else:
        #         print("Doesn't exists")
        #         os.mkdir(folder)

        #     filename = uuid7str()
        #     location = folder+"/"+filename+".jpg"

        #     cv2.imwrite(location, frame) 

        # proses dibawah menggunakan queue
        task = frame_video.delay(filenya, induk, FACEPATH)
        return JSONResponse({"task_id": task.id})
    
    return False

