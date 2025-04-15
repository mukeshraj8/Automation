import imaplib
import email
from email.message import Message
from typing import List
from core.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class EmailReader:
    def __init__(self, server: str, email_user: str, email_pass: str):
        """
        Initialize the EmailReader with server details and credentials.
        """
        self.server = server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mail = None
        logger.info("EmailReader initialized.")

    def connect(self):
        """
        Connect to the IMAP server and log in with the provided credentials.
        """
        try:
            logger.info(f"Connecting to IMAP server: {self.server}")
            self.mail = imaplib.IMAP4_SSL(self.server)
            self.mail.login(self.email_user, self.email_pass)
            logger.info("Successfully connected and logged in.")
        except imaplib.IMAP4.error as e:
            logger.error(f"Failed to connect or log in to the server: {e}")
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
            logger.info(f"Selecting folder: {folder}")
            result, _ = self.mail.select(folder)
            if result != "OK":
                logger.error(f"Failed to select folder: {folder}")
                raise Exception(f"Failed to select folder: {folder}")

            logger.info(f"Searching emails with criteria: {criteria}")
            result, data = self.mail.search(None, criteria)
            if result != "OK":
                logger.error(f"Failed to search emails with criteria: {criteria}")
                raise Exception(f"Failed to search emails with criteria: {criteria}")

            email_ids = data[0].split()
            emails = []

            logger.info(f"Found {len(email_ids)} emails. Fetching emails...")
            for email_id in email_ids:
                result, message_parts = self.mail.fetch(email_id, "(RFC822)")
                if result != "OK":
                    logger.warning(f"Failed to fetch email with ID: {email_id}")
                    continue
                raw_email = message_parts[0][1]
                msg = email.message_from_bytes(raw_email)
                emails.append(msg)

            logger.info(f"Successfully fetched {len(emails)} emails.")
            return emails

        except Exception as e:
            logger.error(f"An error occurred while fetching emails: {e}")
            raise Exception(f"An error occurred while fetching emails: {e}")

    def disconnect(self):
        """
        Disconnect from the IMAP server.
        """
        if self.mail:
            try:
                logger.info("Disconnecting from the IMAP server.")
                self.mail.logout()
                logger.info("Successfully disconnected.")
            except Exception as e:
                logger.error(f"Failed to disconnect: {e}")

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