import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any
from email.message import Message
from core.utils.logger_config import get_logger  # Import your logger

logger = get_logger(__name__)

class EmailClient:
    def __init__(self, imap_server: str, email_user: str, email_pass: str, mailbox: str = "INBOX"):
        """
        Initialize the EmailClient with server details and credentials.
        """
        self.imap_server = imap_server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mailbox = mailbox
        self.connection = None  # Will hold the IMAP connection object
        self.is_connected = False

    def connect(self) -> bool:
        """
        Connect to the IMAP server and log in with the provided credentials.
        Select the specified mailbox (default is "INBOX").
        Returns True on success, False on failure.
        """
        try:
            logger.info(
                f"Connecting to IMAP server: {self.imap_server}:{993 if self.imap_server == 'imap.gmail.com' else 143} and mailbox: {self.mailbox}")
            self.connection = imaplib.IMAP4_SSL(
                self.imap_server)  # Establish a secure connection
            self.connection.login(
                self.email_user, self.email_pass)  # Log in to the email account
            self.connection.select(
                self.mailbox)  # Select the mailbox (e.g., "INBOX")
            logger.info(f"Successfully connected to mailbox: {self.mailbox}")
            self.is_connected = True
            return True  # Indicate success
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error during connection or login: {e}")
            self.connection = None
            self.is_connected = False
            return False  # Indicate failure
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection: {e}")
            self.connection = None
            self.is_connected = False
            return False  # Indicate failure

    def disconnect(self):
        """
        Disconnect from the IMAP server.
        Close the selected mailbox and log out of the email account.
        """
        if self.connection:
            try:
                self.connection.close()  # Close the selected mailbox
                self.connection.logout()  # Log out of the IMAP server
                logger.info("Successfully disconnected from IMAP server.")
            except imaplib.IMAP4.error as e:
                logger.error(f"IMAP error during disconnection: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred during disconnection: {e}")
            finally:
                self.connection = None
                self.is_connected = False

    def fetch_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch the latest emails from the mailbox.

        Args:
            limit (int): The maximum number of emails to fetch (default is 50).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing email details (UID, subject, sender, body).
        """
        emails = []
        if not self.is_connected:
            logger.error("Not connected to IMAP server. Cannot fetch emails.")
            return emails  # Return empty list

        try:
            # Use UID-based search for reliability
            typ, data = self.connection.uid(
                'search', None, "ALL")  # Search for all emails in the mailbox
            if typ != "OK":
                logger.error("Failed to search for emails.")
                return emails

            uids = data[0].split()  # Get the list of email UIDs
            if not uids:
                logger.info("No emails found in the mailbox.")
                return emails

            latest_uids = uids[-limit:]  # Get the latest emails based on the limit

            for uid in latest_uids:
                try:
                    # Fetch the full email message using its UID
                    typ, msg_data = self.connection.uid('fetch', uid, "(RFC822)")
                    if typ != "OK":
                        logger.warning(
                            f"Failed to fetch email with UID {uid.decode()}. Skipping.")
                        continue  # Skip if fetching the email fails

                    raw_email = msg_data[0][1]  # Get the raw email content
                    msg = email.message_from_bytes(
                        raw_email)  # Parse the raw email into a Message object

                    # Create a dictionary with email details
                    email_dict = {
                        "uid": uid.decode(),  # Unique identifier for the email
                        "subject": self._decode_header(msg.get("Subject", "")),  # Decoded subject line
                        "from": self._decode_header(msg.get("From", "")),  # Decoded sender information
                        "body": self._get_body(msg)  # Extracted plain text body
                    }
                    emails.append(email_dict)  # Add the email details to the list
                except Exception as e:
                    logger.error(
                        f"Error processing email with UID {uid.decode()}: {e}")

            logger.info(f"Successfully fetched {len(emails)} emails.")
            return emails  # Return the list of emails

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error during email fetching: {e}")
            return emails  # Return empty list
        except Exception as e:
            logger.error(f"An unexpected error occurred during email fetching: {e}")
            return emails  # Return empty list

    def fetch_unread_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch the latest unread emails from the mailbox.

        Args:
            limit (int): The maximum number of emails to fetch (default is 50).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing email details (UID, subject, sender, body).
        """
        emails = []
        if not self.is_connected:
            logger.error("Not connected to IMAP server. Cannot fetch unread emails.")
            return emails  # Return empty list

        try:
            # Use UID-based search for reliability
            typ, data = self.connection.uid(
                'search', None, '(UNSEEN)')  # Search for unread emails
            if typ != "OK":
                logger.error("Failed to search for unread emails.")
                return emails

            uids = data[0].split()  # Get the list of email UIDs
            if not uids:
                logger.info("No unread emails found in the mailbox.")
                return emails

            latest_uids = uids[-limit:] if len(
                uids) > limit else uids  # Get the latest emails based on the limit

            for uid in latest_uids:
                try:
                    # Fetch the full email message using its UID
                    typ, msg_data = self.connection.uid('fetch', uid, "(RFC822)")
                    if typ != "OK":
                        logger.warning(
                            f"Failed to fetch email with UID {uid.decode()}. Skipping.")
                        continue  # Skip if fetching the email fails

                    raw_email = msg_data[0][1]  # Get the raw email content
                    msg = email.message_from_bytes(
                        raw_email)  # Parse the raw email into a Message object

                    # Create a dictionary with email details
                    email_dict = {
                        "uid": uid.decode(),  # Unique identifier for the email
                        "subject": self._decode_header(msg.get("Subject", "")),  # Decoded subject line
                        "from": self._decode_header(msg.get("From", "")),  # Decoded sender information
                        "body": self._get_body(msg)  # Extracted plain text body
                    }
                    emails.append(email_dict)  # Add the email details to the list
                except Exception as e:
                    logger.error(
                        f"Error processing unread email with UID {uid.decode()}: {e}")

            logger.info(f"Successfully fetched {len(emails)} unread emails.")
            return emails  # Return the list of emails

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error during unread email fetching: {e}")
            return emails
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during unread email fetching: {e}")
            return emails

    def _decode_header(self, value: str) -> str:
        """
        Decode email headers into a readable string.
        """
        if not value:
            return ""
        try:
            parts = decode_header(value)  # Decode the header into parts
            decoded = ""
            for part, encoding in parts:
                if isinstance(part, bytes):
                    # Decode bytes using the specified encoding
                    if encoding:
                        try:
                            decoded += part.decode(encoding, errors="ignore")
                        except LookupError:
                            # Handle unknown encoding
                            decoded += part.decode("latin-1", errors="ignore")
                    else:
                        decoded += part.decode("latin-1", errors="ignore")
                else:
                    decoded += part  # Append plain string parts
            return decoded  # Return the fully decoded header
        except Exception as e:
            logger.error(f"Error decoding header: {e}. Returning raw value.")
            return value
    def _get_body(self, msg: Message) -> str:
        """
        Extract the plain text body content from an email message.
        """
        body = ""
        try:
            if msg.is_multipart():  # Check if the email has multiple parts
                for part in msg.walk():  # Iterate through each part
                    content_type = part.get_content_type()
                    disposition = str(part.get("Content-Disposition"))

                    # Prefer plain text if available and not an attachment
                    if content_type == "text/plain" and "attachment" not in disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            try:
                                body += payload.decode("utf-8", errors="ignore")
                            except Exception as e:
                                logger.error(
                                    f"Error decoding text/plain payload: {e}. Skipping part.")
                                body += ""
            else:
                # If not multipart, decode the payload directly
                payload = msg.get_payload(decode=True)
                if payload:
                    try:
                        body += payload.decode("utf-8", errors="ignore")
                    except Exception as e:
                        logger.error(
                            f"Error decoding non-multipart payload: {e}.  Returning empty body")
                        body = ""
            return body  # Return the plain text body
        except Exception as e:
            logger.error(
                f"Error extracting email body: {e}.  Returning empty body")
            return ""
