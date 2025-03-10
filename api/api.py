import time

import argparse
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from api.logger import logger
from api.services.file_service import save_file
from api.services.queue_service import enqueue_eticket_job, enqueue_print_job, get_queue_status, shutdown_workers, \
    initialize_workers

# FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Metadata validation
class Metadata(BaseModel):
    name: str
    data: list

@app.post("/print_eticket")
async def add_to_queue_eticket(file: UploadFile = File(...), metadata: str = Form(...)):
    try:
        metadata_json = Metadata.parse_raw(metadata)
    except ValidationError as e:
        logger.error(f"Invalid metadata: {e}")
        return JSONResponse(content={"error": "Invalid metadata"}, status_code=400)

    filename = f"{metadata_json.name}.pdf"
    temp_file = save_file(file, filename)

    enqueue_eticket_job(temp_file, metadata_json.dict())
    return JSONResponse(content={"message": "PDF added to e-ticket print queue"})

@app.post("/print")
async def add_to_queue(file: UploadFile = File(...), key: str = Form(...)):
    filename = f"{key}_{int(round(time.time() * 1000))}.pdf"
    temp_file = save_file(file, filename)

    enqueue_print_job(temp_file, key)
    return JSONResponse(content={"message": "PDF added to print queue"})

@app.get("/")
def index():
    return {"message": "Print Queue API"}

@app.get("/queue_status")
def queue_status():
    return get_queue_status()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("shutdown")
def shutdown():
    shutdown_workers()

# Initialize workers on startup
initialize_workers()

if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=2212, help="Port to listen to")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host to listen to")
    parser.add_argument("-w", "--workers", type=int, default=1, help="Number of workers")
    args = parser.parse_args()

    logger.info(f"Starting API on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
