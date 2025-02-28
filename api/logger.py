import logging

from api.config import Config

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)
