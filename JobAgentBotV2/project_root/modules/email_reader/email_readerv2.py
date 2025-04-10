import os
import imaplib
import email
import re
import csv
import signal
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Global settings
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
MAILBOX = os.getenv("MAILBOX", "inbox")
CHECKPOINT_FILE = "checkpoint.txt"
OUTPUT_DIR = "output"
BATCH_SIZE = 100  # Emails to fetch at once
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global variables
should_exit = False

def signal_handler(sig, frame):
    global should_exit
    logger.warning("Ctrl+C detected. Will save progress and exit after current batch...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

def connect_to_mailbox():
    try:
        logger.info(f"Connecting to IMAP server: {IMAP_SERVER}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select(MAILBOX)
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

def fetch_email_uids(mail):
    typ, data = mail.uid('search', None, "ALL")
    if typ != "OK":
        logger.error("Failed to fetch email UIDs")
        return []
    uids = data[0].split()
    logger.info(f"Total emails found: {len(uids)}")
    return uids

def process_email(mail, uid):
    try:
        typ, msg_data = mail.uid('fetch', uid, '(RFC822)')
        if typ != "OK":
            logger.error(f"Failed to fetch UID {uid}")
            return []
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
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

    all_uids = fetch_email_uids(mail)
    if not all_uids:
        logger.error("No emails found. Exiting.")
        sys.exit(1)

    last_processed_uid = load_checkpoint()
    logger.info(f"Resuming from UID {last_processed_uid}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"extracted_links_{timestamp}.csv")

    with open(output_file, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["UID", "Link"])

        batch = []
        for uid in all_uids:
            uid_int = int(uid)
            if uid_int <= last_processed_uid:
                continue  # Already processed

            batch.append(uid)

            if len(batch) >= BATCH_SIZE or should_exit:
                for batch_uid in batch:
                    links = process_email(mail, batch_uid)
                    if links:
                        for link in links:
                            writer.writerow([batch_uid.decode(), link])

                    save_checkpoint(int(batch_uid))

                csvfile.flush()
                batch.clear()

                if should_exit:
                    logger.info("Gracefully exiting after current batch...")
                    break

        # Process remaining emails if any
        if batch:
            for batch_uid in batch:
                links = process_email(mail, batch_uid)
                if links:
                    for link in links:
                        writer.writerow([batch_uid.decode(), link])

                save_checkpoint(int(batch_uid))
            csvfile.flush()

    mail.logout()
    logger.info("Finished processing all emails.")

if __name__ == "__main__":
    main()
