import os

class Config:
    DEBUG = os.getenv("DEBUG", False)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/print-service")
    DATABASE_URL = "sqlite:///./local.db"
