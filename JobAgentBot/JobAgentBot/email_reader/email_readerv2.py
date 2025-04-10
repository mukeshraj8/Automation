import imaplib
import email
from email.header import decode_header
import re
from credentials import EMAIL_USER, EMAIL_PASS, IMAP_SERVER


# ========================================================== #
# Email Utility Functions
# ========================================================== #

def connect_to_mailbox():
    """
    Connects to the IMAP email server using credentials
    and returns the mailbox object.
    """
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail

def decode_mime_words(s):
    """
    Decodes MIME-encoded email header strings (e.g., Subject).
    """
    decoded = decode_header(s)
    subject = ''
    for d, charset in decoded:
        if isinstance(d, bytes):
            charset = charset or 'utf-8'
            subject += d.decode(charset)
        else:
            subject += d
    return subject
    
def fetch_emails(mail, search_criteria='ALL'):
    """
    Fetches email IDs from the mailbox based on search criteria.
    Default is 'ALL' emails.
    """
    mail.select("inbox")
    status, messages = mail.search(None, search_criteria)
    email_ids = messages[0].split()
    return email_ids

def safe_decode(payload_bytes):
    """
    Safely decodes email payload bytes using UTF-8,
    falls back to Latin-1 or Windows-1252 if needed.
    """
    try:
        return payload_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return payload_bytes.decode('latin-1')
        except UnicodeDecodeError:
            return payload_bytes.decode('windows-1252', errors='replace')

def extract_links_from_body(body):
    """
    Extracts all hyperlinks from the given email body text.
    """
    return re.findall(r'(https?://\S+)', body)

# ========================================================== #
# Core Functions
# ========================================================== #

def read_unread_emails():
    """
    Connects to mailbox, fetches unread emails,
    and prints their subject and sender information.
    """
    print("\n🔵 Fetching unread emails...")
    mail = connect_to_mailbox()
    email_ids = fetch_emails(mail, search_criteria='UNSEEN')

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_mime_words(msg["subject"])
                from_ = msg.get("From")
                print(f"📬 Unread Email - Subject: {subject}, From: {from_}")

    mail.logout()

def read_emails_from_sender(sender_email):
    """
    Connects to mailbox, fetches all emails from a specific sender,
    and prints their subject lines.
    """
    print(f"\n🟡 Fetching emails from: {sender_email}")
    mail = connect_to_mailbox()
    search_criteria = f'(FROM "{sender_email}")'
    email_ids = fetch_emails(mail, search_criteria=search_criteria)

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_mime_words(msg["subject"])
                print(f"📬 Email from {sender_email} - Subject: {subject}")

    mail.logout()

# Fetches emails, decodes text bodies safely, extracts hyperlinks using regex, and prints them.
def read_email_body_and_extract_links():
    """
    Connects to mailbox, fetches all emails, decodes their text bodies,
    extracts and prints all hyperlinks found in each email.
    """
    print("\n🟢 Fetching email bodies and extracting links...")
    mail = connect_to_mailbox()
    email_ids = fetch_emails(mail)

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_mime_words(msg["subject"])
                from_ = msg.get("From")
                print(f"\n📬 Email - Subject: {subject}, From: {from_}")

                body = ""

                if msg.is_multipart():
                    # Walk through each part to find the plain text body
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = safe_decode(payload)
                                break  # Stop at first found text/plain body
                else:
                    # Single part email
                    content_type = msg.get_content_type()
                    if content_type == "text/plain":
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = safe_decode(payload)

                if body:
                    links = extract_links_from_body(body)
                    if links:
                        print("🔗 Links found:")
                        for link in links:
                            print(f" - {link}")
                    else:
                        print("🔗 No links found in this email.")

    mail.logout()
    
# --------------------------- #
# Main Runner
# --------------------------- #

if __name__ == "__main__":
    try:
        read_unread_emails()
        #read_emails_from_sender("jobalerts-noreply@linkedin.com")  # <-- Replace with actual sender
        #read_email_body_and_extract_links()
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user. Exiting gracefully...")
