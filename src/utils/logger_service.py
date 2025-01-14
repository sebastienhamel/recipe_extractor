import sys
from loguru import logger

logger.remove()
format = "{time} - {level} | {file} - {function} | {message} | {exception}"
logger.add(
    sys.stdout,
    format = format,
    colorize = True,
    level = "INFO"
)

logger.add(
    "logs/{time:YYYY-MM_DD}.log", 
    rotation = "1 day", 
    retention = "7 days", 
    compression = "zip",
    format = format, 
    level="INFO"
)

logger.opt(exception = True)

def get_logger(name:str):
    return logger.bind(name = name)