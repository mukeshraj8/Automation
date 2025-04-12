import os
from dotenv import load_dotenv
print("Script has started.")
# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 🔥 Corrected path to config.env
ENV_PATH = os.path.join(BASE_DIR, 'config', 'config.env')

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
else:
    print(f"⚠️  Warning: config.env file not found at {ENV_PATH}. Defaults will be used where applicable.")


def get_config(key: str, default=None):
    return os.getenv(key, default)
