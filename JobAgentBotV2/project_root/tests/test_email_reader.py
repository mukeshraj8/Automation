import unittest
from unittest.mock import patch, MagicMock
from email.message import Message
from modules.email_reader.email_reader import EmailReader


class TestEmailReader(unittest.TestCase):
    def setUp(self):
        # Provide dummy credentials and server
        self.reader = EmailReader(
            server="imap.example.com",
            email_user="dummy@example.com",
            email_pass="password"
        )

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_connection_failure(self, mock_imap):
        """
        Test that the connect method raises an exception on connection failure.
        """
        mock_imap.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception):
            self.reader.connect()

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_connect_success(self, mock_imap):
        """
        Test successful connection to the IMAP server.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        self.reader.connect()
        mock_imap.assert_called_once_with("imap.example.com")
        mock_mail.login.assert_called_once_with("dummy@example.com", "password")

    def test_disconnect_without_connect(self):
        """
        Test that disconnect does not raise an exception if not connected.
        """
        try:
            self.reader.disconnect()
            self.assertTrue(True)
        except Exception:
            self.fail("Disconnect should not fail even if not connected.")

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_disconnect_after_connect(self, mock_imap):
        """
        Test that disconnect works correctly after a successful connection.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        self.reader.connect()
        self.reader.disconnect()
        mock_mail.logout.assert_called_once()

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_fetch_emails_success(self, mock_imap):
        """
        Test fetching emails successfully.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock the IMAP server responses
        mock_mail.select.return_value = ("OK", [b""])
        mock_mail.search.return_value = ("OK", [b"1 2"])
        mock_mail.fetch.side_effect = [
            ("OK", [(b"1", b"Subject: Test Email 1")]),
            ("OK", [(b"2", b"Subject: Test Email 2")]),
        ]

        self.reader.connect()
        emails = self.reader.fetch_emails()

        self.assertEqual(len(emails), 2)
        self.assertIsInstance(emails[0], Message)
        self.assertEqual(emails[0]["Subject"], "Test Email 1")
        self.assertEqual(emails[1]["Subject"], "Test Email 2")

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_fetch_emails_failure(self, mock_imap):
        """
        Test failure when fetching emails.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock the IMAP server responses
        mock_mail.select.return_value = ("NO", [b""])
        mock_mail.search.return_value = ("NO", [b""])

        self.reader.connect()
        with self.assertRaises(Exception):
            self.reader.fetch_emails()

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_fetch_emails_invalid_folder(self, mock_imap):
        """
        Test fetching emails from an invalid folder.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock the IMAP server responses
        mock_mail.select.return_value = ("NO", [b""])

        self.reader.connect()
        with self.assertRaises(Exception) as context:
            self.reader.fetch_emails(folder="invalid_folder")
        self.assertIn("Failed to select folder", str(context.exception))

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_fetch_emails_empty_folder(self, mock_imap):
        """
        Test fetching emails from an empty folder.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock the IMAP server responses
        mock_mail.select.return_value = ("OK", [b""])
        mock_mail.search.return_value = ("OK", [b""])

        self.reader.connect()
        emails = self.reader.fetch_emails()
        self.assertEqual(emails, [])

    @patch("modules.email_reader.email_reader.imaplib.IMAP4_SSL")
    def test_fetch_emails_partial_failure(self, mock_imap):
        """
        Test fetching emails where some fetch operations fail.
        """
        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        # Mock the IMAP server responses
        mock_mail.select.return_value = ("OK", [b""])
        mock_mail.search.return_value = ("OK", [b"1 2"])
        mock_mail.fetch.side_effect = [
            ("OK", [(b"1", b"Subject: Test Email 1")]),
            ("NO", None),  # Simulate a failure for the second email
        ]

        self.reader.connect()
        emails = self.reader.fetch_emails()

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["Subject"], "Test Email 1")


if __name__ == "__main__":
    unittest.main()