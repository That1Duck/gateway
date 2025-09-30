import sys
from loguru import logger

def setup_logging() -> None:
    """
    Configuring logs via loguru
    """
    logger.remove()
    logger.add(sys.stdout, enqueue=True, backtrace=True, diagnose=False,
               format=("{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message} "
                       "| {extra}"))