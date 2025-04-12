import unittest
from unittest.mock import patch, MagicMock
from email.message import Message
from modules.email_reader.email_client import EmailClient


class TestEmailClient(unittest.TestCase):
    def setUp(self):
        """
        Set up the EmailClient instance with dummy credentials.
        """
        self.client = EmailClient(
            imap_server="imap.example.com",
            email_user="dummy@example.com",
            email_pass="password"
        )

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_connect_success(self, mock_imap):
        """
        Test successful connection to the IMAP server.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        self.client.connect()

        mock_imap.assert_called_once_with("imap.example.com")
        mock_connection.login.assert_called_once_with("dummy@example.com", "password")
        mock_connection.select.assert_called_once_with("INBOX")

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_connect_failure(self, mock_imap):
        """
        Test connection failure to the IMAP server.
        """
        mock_imap.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception) as context:
            self.client.connect()

        self.assertIn("Connection failed", str(context.exception))

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_disconnect_success(self, mock_imap):
        """
        Test successful disconnection from the IMAP server.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        self.client.connect()
        self.client.disconnect()

        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_fetch_emails_success(self, mock_imap):
        """
        Test fetching emails successfully.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        # Mock the IMAP server responses
        mock_connection.uid.return_value = ("OK", [b"1 2"])
        mock_connection.uid.side_effect = [
            ("OK", [b"1 2"]),
            ("OK", [(b"1", b"Subject: Test Email 1")]),
            ("OK", [(b"2", b"Subject: Test Email 2")]),
        ]

        self.client.connect()
        emails = self.client.fetch_emails(limit=2)

        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]["subject"], "Test Email 1")
        self.assertEqual(emails[1]["subject"], "Test Email 2")

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_fetch_emails_failure(self, mock_imap):
        """
        Test failure when fetching emails.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        # Simulate a failure in the UID search
        mock_connection.uid.return_value = ("NO", None)

        self.client.connect()
        with self.assertRaises(Exception) as context:
            self.client.fetch_emails()

        self.assertIn("Failed to search for emails", str(context.exception))

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_fetch_emails_empty_folder(self, mock_imap):
        """
        Test fetching emails from an empty folder.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        # Simulate an empty folder
        mock_connection.uid.return_value = ("OK", [b""])

        self.client.connect()
        emails = self.client.fetch_emails()

        self.assertEqual(emails, [])

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_decode_header(self, mock_imap):
        """
        Test decoding email headers.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        # Simulate a raw email with encoded headers
        raw_email = b"Subject: =?UTF-8?B?VGVzdCBFbWFpbA==?="
        msg = Message()
        msg.set_payload(raw_email)

        self.client.connect()
        decoded_subject = self.client._decode_header("=?UTF-8?B?VGVzdCBFbWFpbA==?=")

        self.assertEqual(decoded_subject, "Test Email")

    @patch("modules.email_reader.email_client.imaplib.IMAP4_SSL")
    def test_get_body(self, mock_imap):
        """
        Test extracting the plain text body from an email.
        """
        mock_connection = MagicMock()
        mock_imap.return_value = mock_connection

        # Simulate a raw email with a plain text body
        msg = Message()
        msg.set_payload("This is a test email body.")

        self.client.connect()
        body = self.client._get_body(msg)

        self.assertEqual(body, "This is a test email body.")


if __name__ == "__main__":
    unittest.main(verbosity=2)