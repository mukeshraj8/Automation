"""  
✅ 1. Save links periodically (after every email processed), not just at the end.
Even if you Ctrl+C, you won't lose links.

✅ 2. Catch KeyboardInterrupt (Ctrl+C) gracefully.
When you Ctrl+C, it saves all captured links and exits properly.

✅ 3. Allow configurable batch size (example: process only 100 emails at a time).
No need to process 6559 emails at once.

✅ 4. Maintain a checkpoint file (e.g., last_processed_email.txt) to resume next time.
Resume from where it left off automatically.

✅ 5. Make the output CSV file timestamped (e.g., extracted_links_2025-04-10_03-45.csv).

"""

import imaplib
import email
from email.header import decode_header
import logging
import re
import csv
import os
import sys
import signal
from datetime import datetime
from credentials import EMAIL_USER, EMAIL_PASS, IMAP_SERVER

# ----------------------------
# Configuration Section
# ----------------------------

# How many emails to process in one run
BATCH_SIZE = 100

# Directory to store output CSV files
OUTPUT_DIR = "output"

# File to track the last processed email UID
CHECKPOINT_FILE = "last_processed_email.txt"

# Create output directory if it does not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate a timestamped CSV filename for saving links
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_FILENAME = os.path.join(OUTPUT_DIR, f"extracted_links_{timestamp}.csv")

# ----------------------------
# Setup Logging
# ----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("email_reader.log"),   # Log to file
        logging.StreamHandler(sys.stdout)          # Log to console
    ]
)

# ----------------------------
# Global Variables
# ----------------------------

# Collected links will be stored here
all_links = []

# Flag to gracefully exit when Ctrl+C is pressed
should_exit = False

# ----------------------------
# Signal Handling (to capture Ctrl+C)
# ----------------------------

def signal_handler(sig, frame):
    """
    Handler for graceful shutdown on Ctrl+C.
    Sets a flag so that we finish the current email and then save everything.
    """
    global should_exit
    logging.warning("Ctrl+C detected. Will save progress and exit after current email...")
    should_exit = True

# Attach signal handler
signal.signal(signal.SIGINT, signal_handler)

# ----------------------------
# Utility Functions
# ----------------------------

def connect_to_mailbox():
    """
    Connects to the IMAP server and logs in.
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        logging.info("Successfully connected to mailbox.")
        return mail
    except Exception as e:
        logging.error(f"Failed to connect to mailbox: {e}")
        sys.exit(1)

def safe_decode(payload):
    """
    Safely decode email payloads.
    """
    try:
        return payload.decode()
    except UnicodeDecodeError:
        try:
            return payload.decode('utf-8')
        except Exception as e:
            logging.warning(f"Decoding error: {e}")
            return payload.decode('latin-1', errors='ignore')

def extract_links_from_body(body):
    """
    Extracts all URLs from the email body using regex.
    """
    url_pattern = r'https?://\S+'
    links = re.findall(url_pattern, body)
    return links

def save_links_to_csv(links, filename=CSV_FILENAME):
    """
    Appends captured links to a CSV file.
    """
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Link"])  # Write header if file is new
            for link in links:
                writer.writerow([link])
        logging.info(f"Saved {len(links)} links to {filename}.")
    except Exception as e:
        logging.error(f"Error saving links to CSV: {e}")

def save_checkpoint(last_email_uid):
    """
    Saves the UID of the last processed email into a checkpoint file.
    """
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(last_email_uid))
        logging.info(f"Saved checkpoint at UID {last_email_uid}.")
    except Exception as e:
        logging.error(f"Error saving checkpoint: {e}")

def load_checkpoint():
    """
    Loads the UID of the last processed email from checkpoint file.
    If no checkpoint exists, start from 0.
    """
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            last_uid = f.read().strip()
            if last_uid.isdigit():
                logging.info(f"Resuming from last processed UID {last_uid}.")
                return int(last_uid)
    return 0

# ----------------------------
# Main Email Processing Logic
# ----------------------------

def process_emails():
    """
    Connects to mailbox, fetches emails, extracts links, saves progress.
    """
    global all_links

    mail = connect_to_mailbox()

    # Select the INBOX
    mail.select("inbox")

    # Search for all emails
    status, messages = mail.search(None, "ALL")
    if status != "OK":
        logging.error("Failed to fetch emails.")
        return

    # Get list of email UIDs
    email_uids = messages[0].split()
    total_emails = len(email_uids)
    logging.info(f"Total emails found: {total_emails}")

    # Load where we left off last time
    last_processed_uid = load_checkpoint()

    processed_count = 0

    for uid in email_uids:
        uid_int = int(uid)

        # Skip emails we have already processed
        if uid_int <= last_processed_uid:
            continue

        # Fetch the email by UID
        res, data = mail.fetch(uid, "(RFC822)")
        if res != "OK":
            logging.warning(f"Failed to fetch email UID {uid_int}. Skipping...")
            continue

        for response_part in data:
            if isinstance(response_part, tuple):
                try:
                    # Parse the email content
                    msg = email.message_from_bytes(response_part[1])

                    # Get the email body (plain text or HTML)
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if "attachment" not in content_disposition:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = safe_decode(payload)
                                    links = extract_links_from_body(body)
                                    all_links.extend(links)
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = safe_decode(payload)
                            links = extract_links_from_body(body)
                            all_links.extend(links)

                    processed_count += 1
                    save_checkpoint(uid_int)  # Save after every email processed

                    # Save links periodically
                    if processed_count % 10 == 0 or should_exit:
                        save_links_to_csv(all_links)
                        all_links.clear()  # Clear already saved links

                    # If user pressed Ctrl+C, exit cleanly
                    if should_exit:
                        logging.info("Gracefully exiting after saving progress...")
                        return

                    # Stop if batch size is reached
                    if processed_count >= BATCH_SIZE:
                        logging.info(f"Processed {processed_count} emails. Batch limit reached.")
                        return

                except Exception as e:
                    logging.error(f"Error processing email UID {uid_int}: {e}")

    # Final save if anything remains
    if all_links:
        save_links_to_csv(all_links)

# ----------------------------
# Main Program Entry
# ----------------------------

if __name__ == "__main__":
    try:
        process_emails()
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        save_links_to_csv(all_links)  # Try to save whatever was collected
