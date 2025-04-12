import imaplib
import email
from email.header import decode_header

class EmailClient:
    def __init__(self, imap_server, email_account, email_password, mailbox="INBOX"):
        self.imap_server = imap_server
        self.email_account = email_account
        self.email_password = email_password
        self.mailbox = mailbox
        self.connection = None

    def connect(self):
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server)
            self.connection.login(self.email_account, self.email_password)
            self.connection.select(self.mailbox)
            print("✅ Connected to email server successfully.")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            raise

    def fetch_emails(self, limit=50):
        result, data = self.connection.search(None, "ALL")
        email_ids = data[0].split()

        latest_email_ids = email_ids[-limit:]
        emails = []

        for eid in reversed(latest_email_ids):
            result, data = self.connection.fetch(eid, "(RFC822)")
            raw_email = data[0][1]
            message = email.message_from_bytes(raw_email)

            subject = self._decode_header(message.get("Subject"))
            from_ = self._decode_header(message.get("From"))

            body = ""
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            body = ""
                        break
            else:
                try:
                    body = message.get_payload(decode=True).decode()
                except:
                    body = ""

            emails.append((subject, from_, body))

        return emails

    def disconnect(self):
        if self.connection:
            self.connection.logout()
            print("🔌 Disconnected from email server.")

    def _decode_header(self, value):
        if value:
            parts = decode_header(value)
            decoded_string = ""
            for part, encoding in parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding if encoding else "utf-8", errors="ignore")
                else:
                    decoded_string += part
            return decoded_string
        return ""
