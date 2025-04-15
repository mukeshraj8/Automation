import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv, find_dotenv

# # Now safely read LOG_PATH
LOG_PATH = os.getenv('LOG_PATH', 'logs/default.log')

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

print(f"Logger will write to file: {os.path.abspath(LOG_PATH)}")
print(f"Log directory exists: {os.path.exists(os.path.dirname(LOG_PATH))}")
print(f"Log file exists already? {os.path.exists(LOG_PATH)}")


def get_logger(name: str) -> logging.Logger:
    """
    Central logger getter.
    
    :param name: Usually pass __name__ to identify module
    :return: Configured logger
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Rotating file handler (5 MB max, 5 backups)
    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=5*1024*1024, backupCount=5, delay=False
    )
    file_handler.flush = lambda: None  # force flush, optional
    file_handler.setFormatter(formatter)

    # Console output handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # or INFO based on your needs

    # Remove all existing handlers before adding ours
    if logger.hasHandlers():
        logger.handlers.clear()

    # Now safely add
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    print(f"Logger handlers attached to '{name}':")
    for handler in logger.handlers:
        print(f"  - {handler}")


    return logger

