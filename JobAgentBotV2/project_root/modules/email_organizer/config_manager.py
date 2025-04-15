import os
import json
from core.utils.logger_config import get_logger

logger = get_logger(__name__)

class ConfigManager:
    def __init__(self, config_path: str = "core/config/email_organizer_config.json"):
        """
        Initializes the ConfigManager.

        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "core/config/email_organizer_config.json".
        """
        self.config_path = config_path
        self.default_config = {
            "rules": [
                {
                    "name": "Example Rule",
                    "condition": "subject contains 'example'",
                    "actions": ["move to folder 'ExampleFolder'"]
                }
            ]
        }

    def get_config(self) -> dict:
        """
        Loads the configuration from the file. If the file does not exist,
        it creates a new one with default settings.

        Returns:
            dict: The configuration data.
        """
        if not os.path.exists(self.config_path):
            logger.warning(
                f"Config file '{self.config_path}' not found. Creating new one with defaults.")
            # Ensure the directory exists before creating the file
            config_dir = os.path.dirname(self.config_path)
            if not os.path.exists(config_dir):
                try:
                    os.makedirs(config_dir)  # Create the directory
                    logger.info(f"Created directory: {config_dir}")
                except OSError as e:
                    logger.error(f"Failed to create directory: {e}")
                    # If directory creation fails, return the default config and do not try to save.
                    return self.default_config

            try:
                with open(self.config_path, 'w') as f:
                    json.dump(self.default_config, f, indent=4)
                logger.info(f"Successfully saved default config to {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to save config: {e}")
                return self.default_config

        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            return config_data
        except Exception as e:
            logger.error(f"Error reading config file: {e}.  Returning default config.")
            return self.default_config  # Return default config on read error.
