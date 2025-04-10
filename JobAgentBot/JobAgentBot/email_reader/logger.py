import logging
import os
from dotenv import load_dotenv

# Load config
load_dotenv()

# Get log configurations from .env
LOG_FOLDER = os.getenv('LOG_FOLDER', 'logs')
LOG_FILE_NAME = os.getenv('LOG_FILE_NAME', 'app.log')

# Create log folder if not exists
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

log_file_path = os.path.join(LOG_FOLDER, LOG_FILE_NAME)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

# Usage Example:
# logger = logging.getLogger(__name__)
# logger.info("Logging is ready!")
