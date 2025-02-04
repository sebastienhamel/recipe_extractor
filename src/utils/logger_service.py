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

# Function to capture unhandled exceptions
def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Let Ctrl+C work normally
        return
    logger.opt(exception=True).critical("Unhandled exception occurred")

sys.excepthook = exception_handler

def get_logger(name:str):
    return logger.bind(name = name)