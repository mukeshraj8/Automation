# email_reader.py

import imaplib
import email
from typing import List
from link_extractor import extract_links_from_email

class EmailReader:
    def __init__(self, server: str, email_user: str, email_pass: str):
        self.server = server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mail = None

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.server)
        self.mail.login(self.email_user, self.email_pass)

    def fetch_emails(self, folder="inbox", criteria="ALL") -> List[str]:
        self.mail.select(folder)
        result, data = self.mail.search(None, criteria)
        if result != 'OK':
            raise Exception("Failed to fetch emails.")
        
        email_ids = data[0].split()
        emails = []
        
        for email_id in email_ids:
            result, message_parts = self.mail.fetch(email_id, "(RFC822)")
            if result != 'OK':
                continue
            raw_email = message_parts[0][1]
            msg = email.message_from_bytes(raw_email)
            emails.append(msg)
        
        return emails

    def disconnect(self):
        if self.mail:
            self.mail.logout()
