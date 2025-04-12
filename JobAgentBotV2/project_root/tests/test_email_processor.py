import unittest
from unittest.mock import patch, MagicMock
from modules.email_reader.email_processor import EmailProcessor


class TestEmailProcessor(unittest.TestCase):
    @patch("modules.email_reader.email_processor.EmailClient")
    def setUp(self, mock_email_client):
        """
        Set up the EmailProcessor instance with dummy credentials.
        """
        self.imap_server = "imap.example.com"
        self.email_user = "dummy@example.com"
        self.email_pass = "password"
        self.mailbox = "INBOX"
        self.mock_email_client = mock_email_client  # Store the mock

        # Mock EmailClient behavior
        mock_client_instance = MagicMock()
        mock_email_client.return_value = mock_client_instance
        mock_client_instance.fetch_emails.return_value = [
            {"uid": "1", "subject": "Invoice", "from": "boss@example.com", "body": "Here is the invoice link: https://example.com/invoice"},
            {"uid": "2", "subject": "Meeting", "from": "hr@example.com", "body": "Join the meeting at https://example.com/meeting"}
        ]

        self.processor = EmailProcessor(
            imap_server=self.imap_server,
            email_user=self.email_user,
            email_pass=self.email_pass,
            mailbox=self.mailbox
        )

    @patch("modules.email_reader.email_processor.EmailFilter")
    @patch("modules.email_reader.email_processor.LinkExtractor")
    def test_process_emails_success(self, mock_link_extractor, mock_email_filter):
        """
        Test successful processing of emails.
        """

        # Mock EmailFilter behavior
        mock_filter_instance = MagicMock()
        mock_email_filter.return_value = mock_filter_instance
        mock_filter_instance.filter_emails.return_value = [
            {"uid": "1", "subject": "Invoice", "from": "boss@example.com", "body": "Here is the invoice link: https://example.com/invoice"}
        ]

        # Mock LinkExtractor behavior
        mock_extractor_instance = MagicMock()
        mock_link_extractor.return_value = mock_extractor_instance
        mock_extractor_instance.extract_links_from_text.return_value = ["https://example.com/invoice"]

        # Mock CSV writing
        with patch("modules.email_reader.email_processor.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            # Call the process_emails method
            self.processor.process_emails(
                limit=100,
                keywords=["invoice", "urgent", "meeting"],
                senders=["boss@example.com", "hr@example.com"],
                output_dir="test_output"
            )

            # Assertions for EmailClient
            self.mock_email_client.assert_called_once_with(
                self.imap_server, self.email_user, self.email_pass, self.mailbox
            )
            self.mock_email_client.return_value.connect.assert_called_once()
            self.mock_email_client.return_value.fetch_emails.assert_called_once_with(limit=100)
            self.mock_email_client.return_value.disconnect.assert_called_once()

            # Assertions for EmailFilter
            mock_email_filter.assert_called_once_with(
                subject_keywords=["invoice", "urgent", "meeting"],
                sender_keywords=["boss@example.com", "hr@example.com"]
            )
            mock_filter_instance.filter_emails.assert_called_once_with(self.mock_email_client.return_value.fetch_emails.return_value)

            # Assertions for LinkExtractor
            mock_link_extractor.assert_called_once()
            mock_extractor_instance.extract_links_from_text.assert_called_once_with(
                mock_filter_instance.filter_emails.return_value[0]["body"]
            )

            # Assertions for CSV writing
            mock_open.assert_called_once()
            mock_file.write.assert_called()  # Ensure the file was written to


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""
What is Mocking?

In software testing, particularly unit testing, mocking is a technique used to isolate the code being tested from its dependencies. Dependencies are other parts of your system that the code under test relies on to function correctly. These dependencies could be:   

External services (like databases, APIs, email servers)
Other modules or classes within your own application
Hardware interfaces
When testing a specific unit of code (like your EmailProcessor class), you want to focus solely on its logic and behavior, without being affected by the complexities, potential unreliability, or slow performance of its dependencies. This is where mocking comes in.

The Core Idea of Mocking:

Mocking involves replacing real dependencies with controlled, simulated objects called mocks or mock objects. These mock objects are programmed to:   

Mimic the behavior of the real dependencies in ways that are relevant to the test.   
Allow you to make assertions about how the code under test interacts with these dependencies (e.g., which methods were called, how many times, with what arguments).   
Why Use Mocking?

Isolation: Ensures that test failures are due to issues in the unit being tested, not its dependencies.   
Speed: Mocking in-memory objects is much faster than interacting with real external systems.
Predictability: You can control the responses and behavior of mock objects, making tests more reliable and reproducible.   
Testing Edge Cases: You can easily simulate error conditions or unusual responses from dependencies that might be difficult to trigger in a real environment.   
Parallel Testing: Tests that rely on mocks can often be run in parallel without conflicts.
How Mocking Works in Your Test:

Let's focus on the mocking of the EmailClient in your test_process_emails_success method (using the corrected Option 1):

@patch("modules.email_reader.email_processor.EmailClient"):

This is a decorator provided by Python's unittest.mock module.
It targets the EmailClient class as it is used within the modules.email_reader.email_processor module (where your EmailProcessor class is defined).
When the test method (setUp in this case) is executed, patch temporarily replaces the EmailClient class with a special "mock object" (which is an instance of MagicMock).
This mock object is then passed as an argument to the decorated method (setUp). In your code, you named this argument mock_email_client.
mock_client_instance = MagicMock() and mock_email_client.return_value = mock_client_instance:

mock_email_client itself is a mock representing the EmailClient class. When your EmailProcessor tries to create an instance of EmailClient (i.e., EmailClient(...)), it's actually interacting with this mock_email_client.
mock_email_client.return_value = mock_client_instance tells the mock class that whenever it's "instantiated" (called as if it were a constructor), it should return the mock_client_instance. This mock_client_instance is a mock object that simulates an instance of the EmailClient.
mock_client_instance.fetch_emails.return_value = [...]:

Here, you are programming the behavior of the fetch_emails method of the mocked EmailClient instance. When the process_emails method in your EmailProcessor calls self.client.fetch_emails(), it will actually be calling the fetch_emails method of mock_client_instance.
You are setting its return_value to a list of dictionaries, simulating the data that a real EmailClient might return.
self.processor = EmailProcessor(...):

Because you've patched EmailClient before creating the EmailProcessor instance in setUp, the EmailProcessor's __init__ method now uses the mocked EmailClient class. When self.client = EmailClient(...) is executed within EmailProcessor, it's the mock_email_client that gets called, and self.processor.client becomes the mock_client_instance.
Assertions (self.mock_email_client.assert_called_once_with(...), self.mock_email_client.return_value.connect.assert_called_once(), etc.):

These are the crucial part where you verify how your EmailProcessor interacted with the mocked EmailClient.
self.mock_email_client.assert_called_once_with(...) checks that the EmailClient class (the mock itself) was "instantiated" exactly once with the specified arguments. This confirms that your EmailProcessor tried to create an EmailClient with the correct credentials.
self.mock_email_client.return_value.connect.assert_called_once() checks that the connect() method of the mocked instance of EmailClient was called exactly once.
Similarly, you assert that fetch_emails() and disconnect() were called with the expected arguments (or without arguments in some cases).
In essence, mocking allows you to control the external world as seen by your EmailProcessor. You define how its dependencies should behave during the test, and then you verify that your EmailProcessor interacts with those dependencies in the way you expect.

The same principles apply to the mocking of EmailFilter and LinkExtractor in your test. You are replacing their real implementations with mocks to isolate the testing of the EmailProcessor's core logic of orchestrating these components. The patching of open is to control the file system interaction during CSV writing.

"""