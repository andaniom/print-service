import json
import time

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from services.queue_service import print_queue
from services.file_service import save_file, validate_file
from services.printer_service import initialize_printer
from repo.mapping_printer_repo import get_mapping_printers_from_db, save_mapping_printers_to_db
from repo.printer_repo import get_printers_from_db
from utils.usb_util import list_usb_printers
from logger import logger
from models import Base
from database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/mapping-printer")
def get_mapping_printers(db: Session = Depends(get_db)):
    printers = get_mapping_printers_from_db(db)
    return JSONResponse(content={"printers": printers})

@app.post("/mapping-printer")
def save_mapping_printers(printer : MappingPrinter, db: Session = Depends(get_db)):
    try:
        save_mapping_printers_to_db(db, printer)
        return JSONResponse(content={"message": "Printers saved successfully"})
    except Exception as e:
        logger.error(f"Failed to save printers: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/printer-device")
def get_printer_device():
    printers = list_usb_printers()
    return JSONResponse(content={"printers": printers})

@app.get("/printers")
def get_printers(db: Session = Depends(get_db)):
    printers = get_printers_from_db(db)
    return JSONResponse(content={"printers": printers})

@app.post("/select-printer")
def select_printer(vendor_id: str, product_id: str):
    printer = initialize_printer(vendor_id, product_id)
    if printer:
        return JSONResponse(content={"message": "Printer selected successfully"})
    else:
        raise HTTPException(status_code=400, detail="Failed to select printer")


@app.post("/print_eticket")
async def add_to_queue(file: UploadFile = File(...), metadata: str = Form(...)):

    # validate_file(file)
    # if not printer_label:
    #     raise HTTPException(status_code=400, detail="No printer label")

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
    uvicorn.run(app, host="0.0.0.0", port=2212, reload=False, workers=1)