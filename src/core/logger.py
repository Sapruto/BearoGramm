import logging
import logging.handlers
import sys
from datetime import datetime
from src.core.paths import LOGS_ROOT

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str = "core", log_file: str = None, level: int = logging.DEBUG, console_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is None:
        log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

    file_path = LOGS_ROOT / log_file
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=10_485_760,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_ROOT / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=5_242_880,
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger

default_logger = setup_logger("core")

def get_logger(name: str = None) -> logging.Logger:
    if name is None:
        return default_logger
    return logging.getLogger(f"core.{name}")