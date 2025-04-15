import unittest
from unittest.mock import patch, MagicMock
from core.utils.config_loader import get_config
from core.utils.logger_config import get_logger

# Initialize logger for the test
logger = get_logger(__name__)

class TestConfigLoader(unittest.TestCase):
    """
    Unit tests for the config_loader module.
    """

    @patch("core.utils.config_loader.os.getenv")
    def test_get_config_existing_key(self, mock_getenv):
        """
        Test that get_config returns the correct value for an existing key.
        """
        mock_getenv.return_value = "test_user"
        result = get_config("EMAIL_USER")
        self.assertEqual(result, "test_user")
        logger.info(f"Test passed: Existing key 'EMAIL_USER' returned '{result}'")

    @patch("core.utils.config_loader.os.getenv")
    def test_get_config_missing_key_with_default(self, mock_getenv):
        """
        Test that get_config returns the default value for a missing key.
        """
        mock_getenv.return_value = None
        result = get_config("NOT_PRESENT_KEY", default="default_value")
        self.assertEqual(result, "default_value")
        logger.info(f"Test passed: Missing key 'NOT_PRESENT_KEY' returned default '{result}'")

    @patch("core.utils.config_loader.os.getenv")
    def test_get_config_missing_key_without_default(self, mock_getenv):
        """
        Test that get_config returns None for a missing key without a default value.
        """
        mock_getenv.return_value = None
        result = get_config("NOT_PRESENT_KEY")
        self.assertIsNone(result)
        logger.info(f"Test passed: Missing key 'NOT_PRESENT_KEY' returned None")

    @patch("core.utils.config_loader.os.path.exists", return_value=True)
    @patch("core.utils.config_loader.load_dotenv")
    def test_env_file_loading(self, mock_load_dotenv, mock_path_exists):
        """
        Test that the .env file is loaded if it exists.
        """
        from core.utils.config_loader import ENV_PATH
        with patch("core.utils.config_loader.logger") as mock_logger:
            mock_load_dotenv.return_value = None
            self.assertTrue(mock_path_exists(ENV_PATH))
            mock_load_dotenv.assert_called_once_with(ENV_PATH)
            mock_logger.info.assert_called_with(f"Loaded environment variables from {ENV_PATH}")

    @patch("core.utils.config_loader.os.path.exists", return_value=False)
    def test_env_file_missing(self, mock_path_exists):
        """
        Test that a warning is logged if the .env file is missing.
        """
        from core.utils.config_loader import ENV_PATH
        with patch("core.utils.config_loader.logger") as mock_logger:
            self.assertFalse(mock_path_exists(ENV_PATH))
            mock_logger.warning.assert_called_with(
                f"⚠️  Warning: config.env file not found at {ENV_PATH}. Defaults will be used where applicable."
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)