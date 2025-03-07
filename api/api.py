import json
import time

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.logger import logger
from api.services.file_service import save_file
from api.services.queue_service import e_ticket_print_queue, print_queue

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/print_eticket")
async def add_to_queue(file: UploadFile = File(...), metadata: str = Form(...)):

    metadata_json = None
    if metadata:
        try:
            metadata_json = json.loads(metadata)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid metadata: {e}")
    current_time_millis = int(round(time.time() * 1000))
    filename = metadata_json['name'] + "_" + str(current_time_millis) + ".pdf"

    temp_file = save_file(file, filename)
    e_ticket_print_queue.put((temp_file, metadata_json))
    return JSONResponse(content={"message": "PDF added to print queue"})

@app.post("/print")
def print_single(file: UploadFile = File(...), key: str = Form(...)):
    current_time_millis = int(round(time.time() * 1000))
    filename = key + "_" + str(current_time_millis) + ".pdf"
    temp_file = save_file(file, filename)
    print_queue.put((temp_file, key))
    return JSONResponse(content={"message": "PDF added to print queue"})

@app.get("/")
def index():
    logger.info("index")
    return {"message": "Print Queue API"}

@app.on_event("shutdown")
def shutdown():
    e_ticket_print_queue.put(None)
    print_queue.put(None)
    logger.info("Shutting down the application")

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    multiprocessing.freeze_support()  # For Windows support

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=2212)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, reload=False, workers=1)