import os
import csv
from datetime import datetime
from modules.email_reader.email_client import EmailClient
from modules.email_reader.email_filter import EmailFilter
from modules.email_link_extractor.link_extractor import LinkExtractor


class EmailProcessor:
    def __init__(self, imap_server: str, email_user: str, email_pass: str, mailbox: str = "INBOX"):
        """
        Initialize the EmailProcessor with email client credentials and mailbox.

        Args:
            imap_server (str): The IMAP server address.
            email_user (str): The email account username.
            email_pass (str): The email account password.
            mailbox (str): The mailbox to process (default is "INBOX").
        """
        self.imap_server = imap_server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mailbox = mailbox
        self.client = EmailClient(imap_server, email_user, email_pass, mailbox)

    def process_emails(self, limit: int = 100, keywords: list = None, senders: list = None, output_dir: str = "output"):
        """
        Process emails by filtering and extracting links, then save the results to a CSV file.

        Args:
            limit (int): The maximum number of emails to fetch (default is 100).
            keywords (list): Keywords to filter emails by subject or body.
            senders (list): List of sender email addresses to filter emails.
            output_dir (str): Directory to save the output CSV file (default is "output").
        """
        try:
            # Connect to the email server
            self.client.connect()

            # Fetch emails
            emails = self.client.fetch_emails(limit=limit)

            # Filter emails
            filter_obj = EmailFilter(
                subject_keywords=keywords or [],
                sender_keywords=senders or []
            )
            filtered_emails = filter_obj.filter_emails(emails)

            # Extract links from filtered emails
            extractor = LinkExtractor()
            extracted_links = []
            for email_data in filtered_emails:
                links = extractor.extract_links_from_text(email_data["body"])
                for link in links:
                    extracted_links.append((email_data.get("uid", "N/A"), link))

            # Save extracted links to a CSV file
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"extracted_links_{timestamp}.csv")
            self._save_to_csv(output_file, extracted_links)

            print(f"✅ Processed {len(filtered_emails)} filtered emails and saved {len(extracted_links)} links to {output_file}")

        except Exception as e:
            print(f"❌ An error occurred while processing emails: {e}")
        finally:
            # Disconnect from the email server
            self.client.disconnect()

    def _save_to_csv(self, file_path: str, data: list):
        """
        Save data to a CSV file.

        Args:
            file_path (str): The path to the CSV file.
            data (list): The data to save (list of tuples).
        """
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["UID", "Link"])  # Write header
                writer.writerows(data)  # Write rows
        except Exception as e:
            print(f"❌ Failed to save data to CSV: {e}")


if __name__ == "__main__":
    # Load credentials from environment variables
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    mailbox = os.getenv("MAILBOX", "INBOX")

    # Initialize the EmailProcessor
    processor = EmailProcessor(imap_server, email_user, email_pass, mailbox)

    # Define filtering criteria
    keywords = ["invoice", "urgent", "meeting"]
    senders = ["boss@example.com", "hr@example.com"]

    # Process emails
    processor.process_emails(limit=100, keywords=keywords, senders=senders)