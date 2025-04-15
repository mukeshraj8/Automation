import os
from dotenv import load_dotenv
from core.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Log script start
logger.info("Script has started.")

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to config.env
ENV_PATH = os.path.join(BASE_DIR, 'config', 'config.env')

# Load environment variables
def load_env(): # Define load_env as a function
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
        logger.info(f"Loaded environment variables from {ENV_PATH}")
    else:
        logger.warning(f"⚠️  Warning: config.env file not found at {ENV_PATH}. Defaults will be used where applicable.")



def get_config(key: str, default=None):
    """
    Retrieve a configuration value from environment variables.

    Args:
        key (str): The name of the environment variable.
        default: The default value to return if the variable is not set.

    Returns:
        str: The value of the environment variable or the default value.
    """
    value = os.getenv(key, default)
    if value is None:
        logger.warning(f"Configuration key '{key}' is not set. Using default: {default}")
    return value
