import unittest
from unittest.mock import patch, MagicMock
from modules.email_reader.email_processor import EmailProcessor
from typing import List, Dict, Tuple


class TestEmailProcessorImproved(unittest.TestCase):
    """
    A test suite for the EmailProcessor class, focusing on different scenarios
    of email processing and error handling.
    """
    def setUp(self):
        """
        Set up method that is called before each test.
        It initializes the EmailProcessor instance with mocked dependencies
        to isolate the unit under test from external components.
        """
        # Create mock objects for the EmailClient, EmailFilter, and LinkExtractor dependencies.
        self.mock_email_client = MagicMock()
        self.mock_email_filter = MagicMock()
        self.mock_link_extractor = MagicMock()

        # Instantiate the EmailProcessor with the mocked dependencies.
        # This allows us to control the behavior of these dependencies during testing.
        self.processor = EmailProcessor(
            imap_server="dummy_imap",
            email_user="dummy_user",
            email_pass="dummy_pass",
            mailbox="INBOX",
        )
        self.processor.client = self.mock_email_client
        self.processor.filter = self.mock_email_filter
        self.processor.extractor = self.mock_link_extractor

        # Configure default return values for the mocked methods.
        # This ensures that if a specific behavior isn't set in a test,
        # these default values will be used.
        self.mock_email_client.connect.return_value = None
        self.mock_email_client.disconnect.return_value = None
        self.mock_email_client.fetch_emails.return_value = []
        self.mock_email_filter.filter_emails.return_value = []
        self.mock_link_extractor.extract_links_from_text.return_value = []

    @patch("modules.email_reader.email_processor.open", create=True)
    def test_process_emails_success_with_links(self, mock_open):
        """
        Test the successful processing of emails when filtered emails contain links.
        It verifies that the correct methods of the dependencies are called and
        that the extracted links are saved to a CSV file.
        """
        # Define a list of mock email dictionaries with sample data, including a link.
        mock_emails: List[Dict[str, str]] = [
            {"uid": "1", "subject": "Invoice", "from": "boss@example.com", "body": "Check this: https://example.com/invoice"},
            {"uid": "2", "subject": "Meeting", "from": "hr@example.com", "body": "Join here: http://meeting.com/now"},
        ]
        # Configure the mock_email_client to return the mock emails when fetch_emails is called.
        self.mock_email_client.fetch_emails.return_value = mock_emails
        # Configure the mock_email_filter to return the first email as a filtered result.
        self.mock_email_filter.filter_emails.return_value = [mock_emails[0]]
        # Configure the mock_link_extractor to return a list containing the link from the first email's body.
        self.mock_link_extractor.extract_links_from_text.return_value = ["https://example.com/invoice"]

        # Create a mock file object to simulate file operations.
        mock_file = MagicMock()
        # Configure the mock_open to return the mock file object when used in a 'with' statement.
        mock_open.return_value.__enter__.return_value = mock_file

        # Call the process_emails method of the EmailProcessor with specific parameters.
        self.processor.process_emails(
            limit=100,
            keywords=["invoice"],
            senders=["boss@example.com"],
            output_dir="test_output"
        )

        # Assertions to verify the interactions with the mocked dependencies.
        self.mock_email_client.connect.assert_called_once()
        self.mock_email_client.fetch_emails.assert_called_once_with(limit=100)
        self.mock_email_filter.filter_emails.assert_called_once_with(mock_emails)
        self.mock_link_extractor.extract_links_from_text.assert_called_once_with(mock_emails[0]["body"])

        # Assertions to verify that the file was opened and written to correctly.
        mock_open.assert_called_once()
        mock_file.write.assert_called()
        # Check if the header "UID,Link" was written to the file.
        args, _ = mock_file.write.call_args_list[0]
        self.assertIn("UID,Link", args)
        # Check if the extracted link along with the UID was written to the file.
        args, _ = mock_file.write.call_args_list[1]
        self.assertIn("1,https://example.com/invoice", args)

        self.mock_email_client.disconnect.assert_called_once()

    @patch("modules.email_reader.email_processor.open", create=True)
    def test_process_emails_no_filtered_emails(self, mock_open):
        """
        Test the scenario where no emails match the specified filter criteria.
        It verifies that the link extraction and file saving steps are skipped.
        """
        # Define a mock email that should not be filtered based on the process_emails arguments.
        self.mock_email_client.fetch_emails.return_value = [
            {"uid": "1", "subject": "Unrelated", "from": "spam@example.com", "body": "No links here"}
        ]
        # Configure the mock_email_filter to return an empty list, indicating no filtered emails.
        self.mock_email_filter.filter_emails.return_value = []

        # Call the process_emails method with filter criteria that should not match the mock email.
        self.processor.process_emails(
            limit=10,
            keywords=["important"],
            senders=["trusted@example.com"],
            output_dir="test_output"
        )

        # Assertions to verify the interactions with the mocked dependencies.
        self.mock_email_client.connect.assert_called_once()
        self.mock_email_client.fetch_emails.assert_called_once_with(limit=10)
        self.mock_email_filter.filter_emails.assert_called_once_with([])
        # Ensure that the link extractor was not called since there were no filtered emails.
        self.mock_link_extractor.extract_links_from_text.assert_not_called()
        # Ensure that the file was not opened for writing since no links were extracted.
        mock_open.assert_not_called()
        self.mock_email_client.disconnect.assert_called_once()

    @patch("modules.email_reader.email_processor.open", create=True)
    def test_process_emails_no_links_in_filtered_emails(self, mock_open):
        """
        Test the scenario where filtered emails do not contain any links.
        It verifies that a CSV file is still created with only the header.
        """
        # Define a mock email that matches the filter criteria but contains no links.
        mock_emails: List[Dict[str, str]] = [
            {"uid": "3", "subject": "Report", "from": "manager@example.com", "body": "Just text here"}
        ]
        # Configure the mock_email_client to return the mock emails.
        self.mock_email_client.fetch_emails.return_value = mock_emails
        # Configure the mock_email_filter to return the mock emails as filtered results.
        self.mock_email_filter.filter_emails.return_value = mock_emails
        # Configure the mock_link_extractor to return an empty list, indicating no links found.
        self.mock_link_extractor.extract_links_from_text.return_value = []

        # Get the mock file object.
        mock_file = mock_open.return_value.__enter__.return_value

        # Call the process_emails method.
        self.processor.process_emails(
            limit=5,
            keywords=["report"],
            senders=["manager@example.com"],
            output_dir="test_output"
        )

        # Assertions to verify the interactions with the mocked dependencies.
        self.mock_email_client.connect.assert_called_once()
        self.mock_email_client.fetch_emails.assert_called_once_with(limit=5)
        self.mock_email_filter.filter_emails.assert_called_once_with(mock_emails)
        self.mock_link_extractor.extract_links_from_text.assert_called_once_with(mock_emails[0]["body"])
        # Ensure that the file was opened for writing.
        mock_open.assert_called_once()
        # Ensure that the write method of the mock file was called (at least for the header).
        mock_file.write.assert_called()
        # Check if the header "UID,Link" was written.
        args, _ = mock_file.write.call_args_list[0]
        self.assertIn("UID,Link", args)
        # Ensure that only the header was written (no data rows).
        self.assertEqual(mock_file.write.call_count, 1)

        self.mock_email_client.disconnect.assert_called_once()

    def test_process_emails_error_during_fetching(self):
        """
        Test the handling of an error that occurs during the email fetching process.
        It verifies that the error is caught and potentially re-raised.
        """
        # Configure the mock_email_client's connect method to raise an exception.
        self.mock_email_client.connect.side_effect = Exception("Connection error")

        # Use a context manager to patch the 'open' function and another to assert that an exception is raised.
        with patch("modules.email_reader.email_processor.open", create=True) as mock_open:
            with self.assertRaises(Exception) as context:
                self.processor.process_emails(limit=10)

            # Assert that the raised exception contains the expected error message.
            self.assertIn("Connection error", str(context.exception))
            # Verify that the connect method was called.
            self.mock_email_client.connect.assert_called_once()
            # Ensure that the fetch_emails, filter_emails, and link extraction methods were not called
            # because the connection failed.
            self.mock_email_client.fetch_emails.assert_not_called()
            # Ensure that the file was not opened for writing.
            mock_open.assert_not_called()
            # Ensure that the disconnect method was called (in the finally block).
            self.mock_email_client.disconnect.assert_called_once()

    @patch("modules.email_reader.email_processor.os.makedirs")
    @patch("modules.email_reader.email_processor.open", create=True)
    def test_process_emails_output_directory_creation(self, mock_open, mock_makedirs):
        """
        Test that the output directory is created if it does not already exist.
        It verifies that the os.makedirs function is called with the correct parameters.
        """
        # Call the process_emails method with a specific output directory.
        self.processor.process_emails(output_dir="another_test_output")
        # Assert that os.makedirs was called with the specified directory and exist_ok=True
        # to prevent errors if the directory already exists.
        mock_makedirs.assert_called_once_with("another_test_output", exist_ok=True)

    @patch("modules.email_reader.email_processor.open", create=True)
    def test_save_to_csv_success(self, mock_open):
        """
        Test the successful saving of extracted links to a CSV file.
        It verifies that the file is opened in write mode and the data is written correctly.
        """
        # Define sample data to be saved to the CSV file.
        test_data: List[Tuple[str, str]] = [("a1", "http://link1.com"), ("b2", "http://link2.com")]
        # Define the expected file path.
        file_path = "test_output/test.csv"
        # Get the mock file object.
        mock_file = mock_open.return_value.__enter__.return_value

        # Call the _save_to_csv method with the sample data and file path.
        self.processor._save_to_csv(file_path, test_data)

        # Assert that the 'open' function was called with the correct file path, mode, newline, and encoding.
        mock_open.assert_called_once_with(file_path, "w", newline="", encoding="utf-8")
        # Assert that the header row was written to the file.
        mock_file.write.assert_any_call("UID,Link\r\n")
        # Assert that the data rows were written to the file.
        mock_file.write.assert_any_call("a1,http://link1.com\r\n")
        mock_file.write.assert_any_call("b2,http://link2.com\r\n")
        # Ensure that the write method was called three times (header + two data rows).
        self.assertEqual(mock_file.write.call_count, 3)

    @patch("modules.email_reader.email_processor.open", side_effect=IOError("Permission denied"))
    def test_save_to_csv_error(self, mock_open):
        """
        Test the handling of an IOError that occurs during the saving to a CSV file.
        It verifies that the exception is caught and re-raised.
        """
        # Define a file path that will cause an IOError due to the side_effect of the mocked 'open' function.
        file_path = "error_path.csv"
        # Assert that calling _save_to_csv with this file path raises an IOError.
        with self.assertRaises(OSError) as context:
            self.processor._save_to_csv(file_path, [("c3", "http://error.com")])

        # Assert that the raised IOError contains the expected error message.
        self.assertIn("Permission denied", str(context.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)
