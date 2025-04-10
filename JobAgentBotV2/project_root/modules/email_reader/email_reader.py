import os
import imaplib
import email
from email.header import decode_header
import csv
import re
import signal
import sys
from datetime import datetime
from core.utils.logger_config import get_logger
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


# Load environment variables
load_dotenv()

# Setup logging
logger = get_logger(__name__)

# Global settings
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")  # Default if not in .env
MAILBOX = os.getenv("MAILBOX", "inbox")
CHECKPOINT_FILE = "checkpoint.txt"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# print(f"EMAIL_USER: {EMAIL_USER}")
# print(f"EMAIL_PASS: {EMAIL_PASS}")
# print(f"IMAP_SERVER: {IMAP_SERVER}")
# print(f"MAILBOX: {MAILBOX}")


# Global variables
should_exit = False

def signal_handler(sig, frame):
    global should_exit
    logger.warning("Ctrl+C detected. Will save progress and exit after current email...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

def connect_to_mailbox():
    try:
        logger.info(f"Connecting to IMAP server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        logger.info("Successfully connected to mailbox.")
        return mail
    except Exception as e:
        logger.error(f"Failed to connect to mailbox: {e}")
        return None

def save_checkpoint(uid):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(uid))
    logger.info(f"Saved checkpoint at UID {uid}.")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read())
    return 0

def extract_links_from_text(text):
    url_pattern = r'https?://\S+'
    return re.findall(url_pattern, text)

def fetch_emails(mail):
    mail.select(MAILBOX)
    _, message_numbers_raw = mail.search(None, "ALL")
    message_numbers = message_numbers_raw[0].split()
    logger.info(f"Total emails found: {len(message_numbers)}")
    return message_numbers

def process_email(mail, uid):
    try:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception as e:
                        logger.warning(f"Decoding error (multipart): {e}")
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception as e:
                logger.warning(f"Decoding error (singlepart): {e}")

        links = extract_links_from_text(body)
        return links
    except Exception as e:
        logger.error(f"Error processing email UID {uid}: {e}")
        return []

def main():
    mail = connect_to_mailbox()
    if not mail:
        logger.error("Unable to connect to mailbox. Exiting.")
        sys.exit(1)

    message_numbers = fetch_emails(mail)
    last_processed_uid = load_checkpoint()

    extracted_links = []
    start_processing = False if last_processed_uid else True

    for uid in message_numbers:
        uid_int = int(uid)
        if not start_processing:
            if uid_int > last_processed_uid:
                start_processing = True
            else:
                continue

        links = process_email(mail, uid)
        if links:
            for link in links:
                extracted_links.append((uid_int, link))

        save_checkpoint(uid_int)

        if should_exit:
            logger.info("Gracefully exiting after saving progress...")
            break

    # Save links to CSV
    if extracted_links:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(OUTPUT_DIR, f"extracted_links_{timestamp}.csv")
        with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["UID", "Link"])
            writer.writerows(extracted_links)

        logger.info(f"Saved {len(extracted_links)} links to {output_filename}.")

    mail.logout()

# # ----------------------------
# # Entry Point
# # ----------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt detected. Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
