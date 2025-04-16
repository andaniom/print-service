import os
import time
from pathlib import Path

from fastapi import HTTPException, UploadFile

from api.config import Config
from api.logger import logger


def save_file(uploaded_file: UploadFile, filename: str):
    project_dir = Path(__file__).resolve().parent
    temp_dir = project_dir / "tmp/uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())
    logger.info(f"File saved at {file_path}")
    return str(file_path)

def save_file_from_text(text: str, filename: str):
    project_dir = Path(__file__).resolve().parent
    temp_dir = project_dir / "tmp/uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_path = temp_dir / filename
    with open(file_path, "w") as f:
        f.write(text)
    logger.info(f"File saved at {file_path}")
    return str(file_path)

def validate_file(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        logger.error("File must be a PDF")
        raise HTTPException(status_code=400, detail="File must be a PDF")

def clear_tmp():
    tmp_uploads = Path(__file__).resolve().parent / "tmp/uploads"
    for file in tmp_uploads.iterdir():
        file.unlink()