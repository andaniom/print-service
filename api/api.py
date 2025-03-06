import json
import time

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse

from api.database import SessionLocal, engine, Base
from api.logger import logger
from api.services.file_service import save_file
from api.services.queue_service import print_queue

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    print_queue.put((temp_file, metadata_json))
    return JSONResponse(content={"message": "PDF added to print queue"})

@app.get("/queue")
def get_queue():
    queue_list = list(print_queue.queue)
    return JSONResponse(content={"queue": queue_list})

@app.get("/")
def index():
    return {"message": "Print Queue API"}

@app.on_event("shutdown")
def shutdown():
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