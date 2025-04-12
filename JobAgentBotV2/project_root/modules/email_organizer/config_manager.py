import os
import json

class ConfigManager:
    def __init__(self, config_path=None):
        self.CONFIG_FILE = config_path or os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        self.CONFIG_FILE = os.path.abspath(self.CONFIG_FILE)
        self.DEFAULT_CONFIG = {
            "email_folder": "INBOX",
            "processed_folder": "Processed",
            "max_email_size_mb": 10
        }
        self.config_data = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as file:
                    self.config_data = json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding {self.CONFIG_FILE}. Loading defaults.")
                self.config_data = self.DEFAULT_CONFIG.copy()
        else:
            print(f"{self.CONFIG_FILE} not found. Creating new with defaults.")
            self.config_data = self.DEFAULT_CONFIG.copy()
            self.save_config()

        # Add missing keys from DEFAULT_CONFIG if they are missing
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config_data:
                self.config_data[key] = value
        self.save_config()

    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as file:
            json.dump(self.config_data, file, indent=4)

    def get_config(self):
        return self.config_data

    # ⭐ Add these two methods:
    def get(self, key):
        return self.config_data.get(key)

    def set(self, key, value):
        self.config_data[key] = value
        self.save_config()

    def update_config(self, key, value):
        self.config_data[key] = value
        self.save_config()
