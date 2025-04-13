# tests/test_email_organizer/test_config_manager.py

import unittest
import os
import json
import tempfile
from modules.email_organizer.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.config_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        # Clean up temporary config file after each test
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_default_when_file_missing(self):
        # Test: If the config file is missing, defaults should load correctly
        os.remove(self.config_path)  # Explicitly remove the file to simulate missing config
        config = ConfigManager(config_path=self.config_path)
        # Should fall back to default 'INBOX' for email_folder
        self.assertEqual(config.get('email_folder'), 'INBOX')

    def test_save_and_load_config(self):
        # Test: Saving a modified config and then loading it should retain the changes
        config = ConfigManager(config_path=self.config_path)
        config.set('email_folder', 'TEST')  # Change a config value
        config.save_config()  # Save to file

        # Reload the config from file
        new_config = ConfigManager(config_path=self.config_path)
        self.assertEqual(new_config.get('email_folder'), 'TEST')  # Should reflect saved value

    def test_invalid_json_file_handling(self):
        # Test: If the config file contains invalid JSON, it should fallback to defaults
        with open(self.config_path, 'w') as f:
            f.write('INVALID_JSON')  # Write bad JSON content

        config = ConfigManager(config_path=self.config_path)
        # Should not crash, and should load defaults instead
        self.assertEqual(config.get('email_folder'), 'INBOX')

    def test_partial_config_file(self):
        # Test: If the config file has only some keys, missing keys should use default values
        partial_data = {
            "email_folder": "PARTIAL"  # Only setting one key
        }
        with open(self.config_path, 'w') as f:
            json.dump(partial_data, f)

        config = ConfigManager(config_path=self.config_path)
        # Existing key should take from file
        self.assertEqual(config.get('email_folder'), 'PARTIAL')
        # Missing key should fallback to default value
        self.assertEqual(config.get('processed_folder'), 'Processed')

    def test_large_max_email_size(self):
        # Test: Setting a very large max_email_size_mb should be saved and loaded correctly
        config = ConfigManager(config_path=self.config_path)
        large_value = 10**6  # 1 million MB
        config.set('max_email_size_mb', large_value)
        config.save_config()  # Save config with large value

        # Reload the config and validate the large value is retained
        new_config = ConfigManager(config_path=self.config_path)
        self.assertEqual(new_config.get('max_email_size_mb'), large_value)

if __name__ == '__main__':
    unittest.main()
