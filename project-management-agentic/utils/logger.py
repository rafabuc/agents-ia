import logging
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger as loguru_logger

from config.settings import settings


def setup_logging():
    """Setup logging configuration."""
    # Remove default handler
    loguru_logger.remove()
    
    # Add console handler
    loguru_logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    loguru_logger.add(
        str(log_file),
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return loguru_logger


# Initialize logger
logger = setup_logging()
