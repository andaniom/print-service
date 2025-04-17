import time
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError, Field

from api.logger import logger
from api.services.file_service import save_file, save_file_from_text, clear_tmp
from api.services.queue_service import enqueue_eticket_job, enqueue_print_job, get_queue_status, shutdown_workers, \
    initialize_workers, enqueue_print_pk_job

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
async def add_to_queue(
        file: Optional[UploadFile] = File(None),
        code: Optional[str] = Form(None),
        key: str = Form(..., min_length=1, max_length=50)):
    try:
        filename = f"{key}_{int(round(time.time() * 1000))}"
        if file is not None:
            filename = f"{filename}.pdf"
            temp_file = save_file(file, filename)
        elif code is not None:
            filename = f"{filename}.zpl"
            temp_file = save_file_from_text(code, filename)
        else:
            raise HTTPException(status_code=400, detail="file or code not found")

        enqueue_print_job(temp_file, key)
        return JSONResponse(content={"message": "PDF added to print queue"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PrintPKData(BaseModel):
    serial: bool
    type: str


class PrintPKRequest(BaseModel):
    code: List[str]
    data: PrintPKData
    key: Optional[str] = None


@app.post("/print-pk")
async def add_to_queue_lab(request: Request, print_request: Optional[PrintPKRequest] = None):
    try:
        if print_request is None:
            body = await request.body()
            logger.info(f"Raw request body: {body.decode()}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Log the received data
        logger.info(f"Received print request: {print_request}")

        # Validate the request
        if not print_request.code or not print_request.data:
            raise HTTPException(status_code=400, detail="Missing code or data in request")

        if print_request.data.type.lower() != "zpl":
            raise HTTPException(status_code=400, detail="Only ZPL type is supported")

        if print_request.key is None:
            print_request.key = print_request.data.type

        # Save the file
        for i, code in enumerate(print_request.code):
            timestamp = int(round(time.time() * 1000))
            filename = f"{print_request.key}_{timestamp}_{i}.{print_request.data.type}"
            file_path = save_file_from_text(code, filename)
            enqueue_print_pk_job(file_path, print_request.key)

        return JSONResponse(content={"message": "Success"})

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/print-radiology")
async def add_to_queue_radiology(request: Request, print_request: Optional[PrintPKRequest] = None):
    try:
        if print_request is None:
            body = await request.body()
            logger.info(f"Raw request body: {body.decode()}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Log the received data
        logger.info(f"Received print request: {print_request}")

        # Validate the request
        if not print_request.code or not print_request.data:
            raise HTTPException(status_code=400, detail="Missing code or data in request")

        if print_request.data.type.lower() != "zpl":
            raise HTTPException(status_code=400, detail="Only ZPL type is supported")

        if print_request.key is None:
            print_request.key = print_request.data.type

        # Save the file
        for i, code in enumerate(print_request.code):
            timestamp = int(round(time.time() * 1000))
            filename = f"{print_request.key}_{timestamp}_{i}.{print_request.data.type}"
            file_path = save_file_from_text(code, filename)
            enqueue_print_pk_job(file_path, print_request.key)

        return JSONResponse(content={"message": "Success"})

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/print-radiologi-multiple")
async def add_to_queue_radiology_multi(request: Request, print_request: Optional[PrintPKRequest] = None):
    try:
        if print_request is None:
            body = await request.body()
            logger.info(f"Raw request body: {body.decode()}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Log the received data
        logger.info(f"Received print request: {print_request}")

        # Validate the request
        if not print_request.code or not print_request.data:
            raise HTTPException(status_code=400, detail="Missing code or data in request")

        if print_request.data.type.lower() != "zpl":
            raise HTTPException(status_code=400, detail="Only ZPL type is supported")

        if print_request.key is None:
            print_request.key = print_request.data.type

        # Save the file
        for i, code in enumerate(print_request.code):
            timestamp = int(round(time.time() * 1000))
            filename = f"{print_request.key}_{timestamp}_{i}.{print_request.data.type}"
            file_path = save_file_from_text(code, filename)
            enqueue_print_pk_job(file_path, print_request.key)

        return JSONResponse(content={"message": "Success"})

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/print-micro")
async def add_to_queue_micro(request: Request, print_request: Optional[PrintPKRequest] = None):
    try:
        if print_request is None:
            body = await request.body()
            logger.info(f"Raw request body: {body.decode()}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Log the received data
        logger.info(f"Received print request: {print_request}")

        # Validate the request
        if not print_request.code or not print_request.data:
            raise HTTPException(status_code=400, detail="Missing code or data in request")

        if print_request.data.type.lower() != "zpl":
            raise HTTPException(status_code=400, detail="Only ZPL type is supported")

        if print_request.key is None:
            print_request.key = print_request.data.type

        # Save the file
        for i, code in enumerate(print_request.code):
            timestamp = int(round(time.time() * 1000))
            filename = f"{print_request.key}_{timestamp}_{i}.{print_request.data.type}"
            file_path = save_file_from_text(code, filename)
            enqueue_print_pk_job(file_path, print_request.key)

        return JSONResponse(content={"message": "Success"})

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def index():
    return {"message": "Print Queue API"}


@app.get("/queue_status")
def queue_status():
    return get_queue_status()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# @app.on_event("shutdown")
# def shutdown():
#     shutdown_workers()

# Initialize workers on startup
initialize_workers()

if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=2212, help="Port to listen to")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host to listen to")
    args = parser.parse_args()

    clear_tmp()
    logger.info(f"Starting API on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
