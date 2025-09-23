import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

def setup_logging():
    """Configurar sistema de logging con loguru"""
    logger.remove()
    
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler
    log_file = settings.logs_dir / "agent.log"
    logger.add(
        str(log_file),
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logging system initialized")
