import json
import os
from fastapi import HTTPException, UploadFile

from api.config import Config
from api.logger import logger


def save_file(file: UploadFile, filename: str):
    temp_dir = Config.TEMP_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file = os.path.join(temp_dir, filename)
    with open(temp_file, "wb") as f:
        f.write(file.file.read())
    logger.info(f"File saved: {temp_file}")
    return temp_file

def validate_file(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        logger.error("File must be a PDF")
        raise HTTPException(status_code=400, detail="File must be a PDF")
