import imaplib
import email
from email.header import decode_header

# Your credentials
from credentials import EMAIL_USER, EMAIL_PASS, IMAP_SERVER

# Connect to Gmail IMAP server
mail = imaplib.IMAP4_SSL("imap.gmail.com")

# Login
mail.login(EMAIL_USER, EMAIL_PASS)

# Select the mailbox you want to use ('inbox' here)
mail.select("inbox")

# Search for ALL emails
status, messages = mail.search(None, "ALL")

# Convert messages to a list of email IDs
mail_ids = messages[0].split()

# Get the latest email
latest_email_id = mail_ids[-1]

# Fetch the email by ID
status, data = mail.fetch(latest_email_id, "(RFC822)")

# Parse the email content
for response_part in data:
    if isinstance(response_part, tuple):
        msg = email.message_from_bytes(response_part[1])
        
        # Get email headers
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")
        
        from_ = msg.get("From")

        print(f"Subject: {subject}")
        print(f"From: {from_}")

# Logout
mail.logout()



def clean(text):
    # Clean text for creating folder names or filenames
    return "".join(c if c.isalnum() else "_" for c in text)

def read_emails():
    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)

    # Login to your account
    mail.login(EMAIL_USER, EMAIL_PASS)

    # Select the mailbox you want to use (INBOX)
    mail.select("inbox")

    # Search for specific emails (unread emails)
    status, messages = mail.search(None, 'UNSEEN')

    # Total number of unread emails
    email_ids = messages[0].split()

    print(f"Found {len(email_ids)} unread emails!")

    for email_id in email_ids:
        # Fetch the email by ID
        res, msg = mail.fetch(email_id, "(RFC822)")

        for response in msg:
            if isinstance(response, tuple):
                # Parse the bytes email into a message object
                msg = email.message_from_bytes(response[1])

                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # From
                from_ = msg.get("From")

                print("="*100)
                print(f"Subject: {subject}")
                print(f"From: {from_}")

                # If the email message is multipart
                if msg.is_multipart():
                    # Iterate over email parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            body = None

                        if body:
                            # Print only text emails
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                print(f"Body:\n{body}")
                else:
                    # Email not multipart
                    body = msg.get_payload(decode=True).decode()
                    print(f"Body:\n{body}")

    # Logout and close connection
    mail.logout()

# if __name__ == "__main__":
#     read_emails()


if __name__ == "__main__":
    try:
        read_emails()
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user. Exiting gracefully...")