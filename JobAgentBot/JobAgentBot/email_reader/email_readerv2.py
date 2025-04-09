import imaplib
import email
from email.header import decode_header
import re
from credentials import EMAIL_USER, EMAIL_PASS, IMAP_SERVER


# --------------------------- #
# Utility Functions
# --------------------------- #

def connect_to_mailbox():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail

def decode_mime_words(s):
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
    mail.select("inbox")
    status, messages = mail.search(None, search_criteria)
    email_ids = messages[0].split()
    return email_ids

# --------------------------- #
# Core Functions
# --------------------------- #

def read_unread_emails():
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

def read_email_body_and_extract_links():
    print("\n🟢 Fetching email bodies and extracting links...")
    mail = connect_to_mailbox()
    email_ids = fetch_emails(mail)

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)") #it means "Give me the full raw email message (headers + body) as per standard RFC822 format"
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_mime_words(msg["subject"])
                from_ = msg.get("From")
                print(f"\n📬 Email - Subject: {subject}, From: {from_}")

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            print(f"📝 Body Preview:\n{body[:200]}...")  # Preview first 200 chars
                            links = re.findall(r'(https?://\S+)', body)
                            for link in links:
                                print(f"🔗 Link found: {link}")
                else:
                    content_type = msg.get_content_type()
                    if content_type == "text/plain":
                        body = msg.get_payload(decode=True).decode()
                        print(f"📝 Body Preview:\n{body[:200]}...")
                        links = re.findall(r'(https?://\S+)', body)
                        for link in links:
                            print(f"🔗 Link found: {link}")

    mail.logout()

# --------------------------- #
# Main Runner
# --------------------------- #

if __name__ == "__main__":
    try:
        #read_unread_emails()
        #read_emails_from_sender("jobalerts-noreply@linkedin.com")  # <-- Replace with actual sender
        read_email_body_and_extract_links()
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user. Exiting gracefully...")
