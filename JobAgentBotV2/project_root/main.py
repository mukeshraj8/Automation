import os
import sys
from modules.email_reader.email_client import EmailClient
from modules.email_reader.email_processor import EmailProcessor
from modules.email_organizer.config_manager import ConfigManager
from modules.email_organizer.organizer import Organizer
from core.utils.config_loader import get_config, load_env
from core.utils.logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

def main():
    # Set the standard output encoding to UTF-8.
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            print(f"Standard output encoding set to: {sys.stdout.encoding}")
        except AttributeError:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
            print(f"Standard output encoding set to: {sys.stdout.encoding}")
    load_env()

    config_manager = ConfigManager(config_path="config/email_organizer_config.json")
    rules_json = config_manager.get_config()

    imap_server = get_config("EMAIL_SERVER", "imap.gmail.com")
    email_user = get_config("EMAIL_USER")
    email_pass = get_config("EMAIL_PASS")
    mailbox = get_config("MAILBOX", "INBOX")

    if not email_pass:
        logger.error("Email password is not configured. Please set the EMAIL_PASS environment variable in core/config/config.env.")
        return

    email_client = EmailClient(imap_server, email_user, email_pass, mailbox)
    organizer = Organizer(rules_json)

    try:
        if not email_client.connect():
            logger.error("Failed to connect to the email server. Exiting.")
            return

        emails = email_client.fetch_emails(limit=100)
        logger.info(f"Fetched {len(emails)} emails from {mailbox}")

        for email_data in emails:
            try:
                subject = email_data.get('subject', '<No Subject>')
                if isinstance(subject, bytes):
                    subject = subject.decode('utf-8', errors='ignore')
                logger.info(f"Processing email: {subject}")
                actions = organizer.organize_email(email_data)
                logger.info(f"Actions applied: {actions}")
            except UnicodeEncodeError as e:
                logger.error(f"Error encoding subject for logging: {e}. Skipping logging of this subject.")
                logger.info(f"Processing email with problematic subject")
                actions = organizer.organize_email(email_data)
                logger.info(f"Actions applied: {actions}")

    except KeyboardInterrupt:  # Handle KeyboardInterrupt here
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        email_client.disconnect()
        logger.info("Main function finished")

if __name__ == "__main__":
    main()
