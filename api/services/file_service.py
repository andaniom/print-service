import os
from pathlib import Path

from fastapi import HTTPException, UploadFile

from api.config import Config
from api.logger import logger


def save_file(uploaded_file: UploadFile, filename: str):
    temp_dir = Path("/tmp/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())
    logger.info(f"File saved at {file_path}")
    return str(file_path)

def validate_file(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        logger.error("File must be a PDF")
        raise HTTPException(status_code=400, detail="File must be a PDF")
