import unittest
from core.utils.logger_config import get_logger

class TestLoggerConfig(unittest.TestCase):
    def setUp(self):
        """Set up the logger once for all tests."""
        self.logger = get_logger("testLoggerLevels")

    def tearDown(self):
        """Tear down the logger and close file handlers."""
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def test_info_log(self):
        self.logger.info("This is an info log")

    def test_debug_log(self):
        self.logger.debug("This is a debug log")

    def test_error_log(self):
        self.logger.error("This is an error log")

    def test_critical_log(self):
        self.logger.critical("This is a critical log")
