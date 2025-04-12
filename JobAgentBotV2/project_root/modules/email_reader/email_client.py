import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any
from email.message import Message


class EmailClient:
    def __init__(self, imap_server: str, email_user: str, email_pass: str, mailbox: str = "INBOX"):
        """
        Initialize the EmailClient with server details and credentials.

        Args:
            imap_server (str): The IMAP server address (e.g., "imap.gmail.com").
            email_user (str): The email account username.
            email_pass (str): The email account password.
            mailbox (str): The mailbox to select (default is "INBOX").
        """
        self.imap_server = imap_server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mailbox = mailbox
        self.connection = None  # Will hold the IMAP connection object

    def connect(self):
        """
        Connect to the IMAP server and log in with the provided credentials.
        Select the specified mailbox (default is "INBOX").
        """
        self.connection = imaplib.IMAP4_SSL(self.imap_server)  # Establish a secure connection
        self.connection.login(self.email_user, self.email_pass)  # Log in to the email account
        self.connection.select(self.mailbox)  # Select the mailbox (e.g., "INBOX")

    def disconnect(self):
        """
        Disconnect from the IMAP server.
        Close the selected mailbox and log out of the email account.
        """
        if self.connection:
            self.connection.close()  # Close the selected mailbox
            self.connection.logout()  # Log out of the IMAP server

    def fetch_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch the latest emails from the mailbox.

        Args:
            limit (int): The maximum number of emails to fetch (default is 50).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing email details (UID, subject, sender, body).
        """
        # Use UID-based search for reliability
        typ, data = self.connection.uid('search', None, "ALL")  # Search for all emails in the mailbox
        if typ != "OK":
            raise Exception("Failed to search for emails.")  # Raise an exception if the search fails

        uids = data[0].split()  # Get the list of email UIDs
        latest_uids = uids[-limit:]  # Get the latest emails based on the limit
        emails = []

        for uid in latest_uids:
            # Fetch the full email message using its UID
            typ, msg_data = self.connection.uid('fetch', uid, "(RFC822)")
            if typ != "OK":
                continue  # Skip if fetching the email fails

            raw_email = msg_data[0][1]  # Get the raw email content
            msg = email.message_from_bytes(raw_email)  # Parse the raw email into a Message object

            # Create a dictionary with email details
            email_dict = {
                "uid": uid.decode(),  # Unique identifier for the email
                "subject": self._decode_header(msg.get("Subject", "")),  # Decoded subject line
                "from": self._decode_header(msg.get("From", "")),  # Decoded sender information
                "body": self._get_body(msg)  # Extracted plain text body
            }
            emails.append(email_dict)  # Add the email details to the list

        return emails  # Return the list of emails

    def _decode_header(self, value: str) -> str:
        """
        Decode email headers into a readable string.

        Args:
            value (str): The header value to decode.

        Returns:
            str: The decoded header value.
        """
        parts = decode_header(value)  # Decode the header into parts
        decoded = ""
        for part, encoding in parts:
            if isinstance(part, bytes):
                # Decode bytes using the specified encoding or UTF-8 as a fallback
                decoded += part.decode(encoding if encoding else "utf-8", errors="ignore")
            else:
                decoded += part  # Append plain string parts
        return decoded  # Return the fully decoded header

    def _get_body(self, msg: Message) -> str:
        """
        Extract the plain text body content from an email message.

        Args:
            msg (Message): The email message object.

        Returns:
            str: The plain text body of the email.
        """
        body = ""
        if msg.is_multipart():  # Check if the email has multiple parts (e.g., plain text and HTML)
            for part in msg.walk():  # Iterate through each part of the email
                content_type = part.get_content_type()  # Get the content type (e.g., "text/plain")
                disposition = str(part.get("Content-Disposition"))  # Get the content disposition

                # Prefer plain text if available and not an attachment
                if content_type == "text/plain" and "attachment" not in disposition:
                    payload = part.get_payload(decode=True)  # Decode the payload
                    if payload:
                        body += payload.decode("utf-8", errors="ignore")  # Decode to a string
        else:
            # If the email is not multipart, decode the payload directly
            payload = msg.get_payload(decode=True)
            if payload:
                body += payload.decode("utf-8", errors="ignore")
        return body  # Return the plain text body