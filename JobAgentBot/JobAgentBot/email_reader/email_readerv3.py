"""
    Add Logging Info into the code
"""  

import os
import re
import csv
import email
import imaplib
import logging
from email.header import decode_header
from credentials import EMAIL_USER, EMAIL_PASS, IMAP_SERVER


# ------------------------------------- #
# Setup Logging
# ------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("email_reader.log"),
        logging.StreamHandler()
    ]
)

# ------------------------------------- #
# Utility Functions
# ------------------------------------- #

def connect_to_mailbox():
    """Connects and logs into the mailbox."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        logging.info("Successfully connected to mailbox.")
        return mail
    except Exception as e:
        logging.error(f"Failed to connect: {e}")
        raise

def safe_decode(payload):
    """Safely decodes email payload."""
    try:
        return payload.decode()
    except UnicodeDecodeError:
        try:
            return payload.decode('utf-8')
        except Exception as e:
            logging.warning(f"Decoding error: {e}")
            return payload.decode('latin-1', errors='ignore')
        

def extract_links_from_body(body):
    """Extracts all links from the email body."""
    url_pattern = r'https?://\S+'
    links = re.findall(url_pattern, body)
    return links


def save_links_to_csv(links, filename="extracted_links.csv"):
    """Saves extracted links into a CSV file."""
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Link"])
            for link in links:
                writer.writerow([link])
        logging.info(f"Saved {len(links)} links to {filename}.")
    except Exception as e:
        logging.error(f"Error saving links to CSV: {e}")

# ------------------------------------- #
# Core Functions
# ------------------------------------- #

def read_unread_emails():
    """Reads all unread emails."""
    mail = connect_to_mailbox()
    mail.select("inbox")

    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        logging.error("Failed to fetch emails.")
        return

    email_ids = messages[0].split()
    logging.info(f"Found {len(email_ids)} unread emails.")

    for email_id in email_ids:
        res, msg_data = mail.fetch(email_id, "(RFC822)")
        if res != "OK":
            logging.error(f"Failed to fetch email ID {email_id}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg.get("Subject"))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8')

        from_ = msg.get("From")
        logging.info(f"From: {from_} | Subject: {subject}")

    mail.logout()

def read_email_body_and_extract_links():
    """Reads emails, extracts links, and saves them."""
    mail = connect_to_mailbox()
    mail.select("inbox")

    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        logging.error("Failed to fetch emails.")
        return

    email_ids = messages[0].split()
    logging.info(f"Processing {len(email_ids)} unread emails.")

    all_links = []

    for email_id in email_ids:
        res, msg_data = mail.fetch(email_id, "(RFC822)")
        if res != "OK":
            logging.error(f"Failed to fetch email ID {email_id}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        body = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = safe_decode(payload)
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = safe_decode(payload)

        if body:
            links = extract_links_from_body(body)
            logging.info(f"Found {len(links)} links.")
            all_links.extend(links)
        else:
            logging.warning("No body content found.")

    # ❗ Save all collected links to CSV after processing all emails
    if all_links:
        save_links_to_csv(all_links)
    else:
        logging.info("No links found in unread emails.")

    mail.logout()

    mail.logout()

# ------------------------------------- #
# Main Execution Block
# ------------------------------------- #

if __name__ == "__main__":
    # Choose which function to run
    try:
        #read_unread_emails()
        #read_emails_from_sender("jobalerts-noreply@linkedin.com")  # <-- Replace with actual sender
        read_email_body_and_extract_links()
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user. Exiting gracefully...")
