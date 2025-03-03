import logging

from api.config import Config

logging.basicConfig(
    filename="backend.log",
    level=Config.LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
