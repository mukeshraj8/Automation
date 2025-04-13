"""
Step	What Happens
1.	ConfigManager loads config from file.
2.	RuleEngine uses RuleFactory to create all Rule objects from config.
3.	For each incoming email (you'll pass a dictionary), RuleEngine checks all rules.
4.	First matching rule decides the target folder or action.
5.	If no rule matches, move to Processed folder by default.


Very Clean, Extensible and SOLID
✅ Add a new rule? ➔ Just add a new JSON block + one small class.
✅ No existing code breaks.
✅ Supports unit testing easily — test each Rule independently.
✅ Future enhancement (e.g., complex rules)? ➔ Use Composite Pattern or Chain of Responsibility if needed later.
"""

import os
import json
import logging


class ConfigManager:
    def __init__(self, config_path=None):
        if config_path:
            self.config_file = os.path.abspath(config_path)
        else:
            # Default: config file is next to this file
            current_dir = os.path.dirname(__file__)
            self.config_file = os.path.join(current_dir, 'email_organizer_config.json')

        self.default_config = {
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
                logging.warning(f"Error decoding JSON in '{self.CONFIG_FILE}'. Loading defaults.")
                self.config_data = self.DEFAULT_CONFIG.copy()
        else:
            logging.warning(f"Config file '{self.CONFIG_FILE}' not found. Creating new one with defaults.")
            self.config_data = self.DEFAULT_CONFIG.copy()
            self.save_config()

        # Ensure all default keys exist
        updated = False
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config_data:
                self.config_data[key] = value
                updated = True
        
        if updated:
            self.save_config()

    def save_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(self.config_data, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_config(self):
        return self.config_data.copy()

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value
        self.save_config()
