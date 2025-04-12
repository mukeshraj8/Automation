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
        # Clean up temporary config file
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_default_when_file_missing(self):
        os.remove(self.config_path)
        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get('email_folder'), 'INBOX')

    def test_save_and_load_config(self):
        config = ConfigManager(config_path=self.config_path)
        config.set('email_folder', 'TEST')
        config.save_config()

        # Reload and check
        new_config = ConfigManager(config_path=self.config_path)
        self.assertEqual(new_config.get('email_folder'), 'TEST')

    def test_invalid_json_file_handling(self):
        # Write invalid JSON
        with open(self.config_path, 'w') as f:
            f.write('INVALID_JSON')

        config = ConfigManager(config_path=self.config_path)
        # Should fall back to defaults
        self.assertEqual(config.get('email_folder'), 'INBOX')

    def test_partial_config_file(self):
        # Only write a part of the config
        partial_data = {
            "email_folder": "PARTIAL"
        }
        with open(self.config_path, 'w') as f:
            json.dump(partial_data, f)

        config = ConfigManager(config_path=self.config_path)
        self.assertEqual(config.get('email_folder'), 'PARTIAL')
        self.assertEqual(config.get('processed_folder'), 'Processed')  # default

    def test_large_max_email_size(self):
        config = ConfigManager(config_path=self.config_path)
        large_value = 10**6  # 1 million MB
        config.set('max_email_size_mb', large_value)
        config.save_config()

        new_config = ConfigManager(config_path=self.config_path)
        self.assertEqual(new_config.get('max_email_size_mb'), large_value)

if __name__ == '__main__':
    unittest.main()
