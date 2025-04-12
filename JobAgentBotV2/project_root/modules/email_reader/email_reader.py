import imaplib
import email
from email.message import Message
from typing import List, Optional
import os
import sys
from core.utils.logger_config import get_logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

class EmailReader:
    def __init__(self, server: str, email_user: str, email_pass: str):
        """
        Initialize the EmailReader with server details and credentials.
        """
        self.server = server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mail = None

    def connect(self):
        """
        Connect to the IMAP server and log in with the provided credentials.
        """
        try:
            self.mail = imaplib.IMAP4_SSL(self.server)
            self.mail.login(self.email_user, self.email_pass)
        except imaplib.IMAP4.error as e:
            raise Exception(f"Failed to connect or log in to the server: {e}")

    def fetch_emails(self, folder: str = "inbox", criteria: str = "ALL") -> List[Message]:
        """
        Fetch emails from the specified folder based on the given criteria.

        Args:
            folder (str): The folder to fetch emails from (default is "inbox").
            criteria (str): The search criteria (default is "ALL").

        Returns:
            List[Message]: A list of email.message.Message objects.
        """
        try:
            # Select the folder
            result, _ = self.mail.select(folder)
            if result != "OK":
                raise Exception(f"Failed to select folder: {folder}")

            # Search for emails
            result, data = self.mail.search(None, criteria)
            if result != "OK":
                raise Exception(f"Failed to search emails with criteria: {criteria}")

            email_ids = data[0].split()
            emails = []

            # Fetch each email
            for email_id in email_ids:
                result, message_parts = self.mail.fetch(email_id, "(RFC822)")
                if result != "OK":
                    continue
                raw_email = message_parts[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append(msg)

            return emails

        except Exception as e:
            raise Exception(f"An error occurred while fetching emails: {e}")

    def disconnect(self):
        """
        Disconnect from the IMAP server.
        """
        if self.mail:
            try:
                self.mail.logout()
            except Exception as e:
                print(f"Failed to disconnect: {e}")

    def __enter__(self):
        """
        Context manager entry point.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point.
        """
        self.disconnect()