import sys
import os

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))  # Move one level up
sys.path.insert(0, project_root)

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils.logger import setup_logger   # ✅ Corrected import!

def test_setup_logger():
    # Arrange
    log_file = 'logs/test_logger.log'
    logger_name = 'testLogger'
    test_message = "This is a test log message."

    # Act
    logger = setup_logger(logger_name, log_file)
    logger.info(test_message)

    # Assert
    assert os.path.exists(log_file), "Log file was not created."

    with open(log_file, 'r') as f:
        log_contents = f.read()

    assert test_message in log_contents, "Test log message not found in log file."

    print("✅ Logger test passed!")

if __name__ == "__main__":
    test_setup_logger()
