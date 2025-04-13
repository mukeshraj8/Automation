import os
import csv
from datetime import datetime
from modules.email_reader.email_client import EmailClient
from modules.email_reader.email_filter import EmailFilter
from modules.email_link_extractor.link_extractor import LinkExtractor
from typing import Protocol, List, Tuple, Optional


# Define Protocol (Interface) for EmailClient
class EmailClientInterface(Protocol):
    """
    Defines the interface for an EmailClient, outlining the methods
    that any concrete email client implementation should provide.
    """
    def connect(self):
        """
        Connects to the email server.
        """
        ...
    def fetch_emails(self, limit: int = 100) -> List[dict]:
        """
        Fetches emails from the server.

        Args:
            limit (int): The maximum number of emails to fetch (default is 100).

        Returns:
            List[dict]: A list of dictionaries, where each dictionary represents an email
                        and contains relevant information like 'uid', 'subject', 'from', 'body'.
        """
        ...
    def disconnect(self):
        """
        Disconnects from the email server.
        """
        ...


# Define Protocol (Interface) for EmailFilter
class EmailFilterInterface(Protocol):
    """
    Defines the interface for an EmailFilter, outlining the methods
    that any concrete email filter implementation should provide.
    """
    def __init__(self, subject_keywords: List[str], sender_keywords: List[str]):
        """
        Initializes the EmailFilter with keywords for filtering.

        Args:
            subject_keywords (List[str]): Keywords to look for in the email subject.
            sender_keywords (List[str]): Keywords to look for in the sender's email address.
        """
        ...
    def filter_emails(self, emails: List[dict]) -> List[dict]:
        """
        Filters a list of emails based on the initialized keywords.

        Args:
            emails (List[dict]): A list of email dictionaries to filter.

        Returns:
            List[dict]: A list of email dictionaries that match the filter criteria.
        """
        ...


# Define Protocol (Interface) for LinkExtractor
class LinkExtractorInterface(Protocol):
    """
    Defines the interface for a LinkExtractor, outlining the methods
    that any concrete link extractor implementation should provide.
    """
    def extract_links_from_text(self, text: str) -> List[str]:
        """
        Extracts URLs (links) from a given text.

        Args:
            text (str): The text to extract links from (e.g., email body).

        Returns:
            List[str]: A list of URLs found in the text.
        """
        ...


class EmailProcessor:
    """
    A class responsible for processing emails, including fetching, filtering,
    extracting links, and saving the results to a CSV file.  It uses dependency
    injection to allow for flexible configuration and testing.
    """
    def __init__(
        self,
        imap_server: str,
        email_user: str,
        email_pass: str,
        mailbox: str = "INBOX",
        email_client: Optional[EmailClientInterface] = None,
        email_filter: Optional[EmailFilterInterface] = None,
        link_extractor: Optional[LinkExtractorInterface] = None,
    ):
        """
        Initializes the EmailProcessor with configurations and optional dependencies.

        Args:
            imap_server (str): The IMAP server address.
            email_user (str): The email account username.
            email_pass (str): The email account password.
            mailbox (str): The mailbox to process (default is "INBOX").
            email_client (Optional[EmailClientInterface]): An instance of an EmailClientInterface.
            email_filter (Optional[EmailFilterInterface]): An instance of an EmailFilterInterface.
            link_extractor (Optional[LinkExtractorInterface]): An instance of a LinkExtractorInterface.
        """
        self.imap_server = imap_server
        self.email_user = email_user
        self.email_pass = email_pass
        self.mailbox = mailbox
        # Use provided dependencies or create default instances.  This allows for
        # dependency injection, making the class more testable and flexible.
        self.client: EmailClientInterface = email_client or EmailClient(imap_server, email_user, email_pass, mailbox)
        self.filter: EmailFilterInterface = email_filter or EmailFilter(subject_keywords=[], sender_keywords=[])
        self.extractor: LinkExtractorInterface = link_extractor or LinkExtractor()

    def process_emails(self, limit: int = 100, keywords: Optional[List[str]] = None, senders: Optional[List[str]] = None, output_dir: str = "output"):
        """
        Processes emails by fetching, filtering, and extracting links, then saves
        the results to a CSV file.  Handles potential errors during the process.

        Args:
            limit (int): The maximum number of emails to fetch (default is 100).
            keywords (Optional[List[str]]): Keywords to filter emails by subject or body.
            senders (Optional[List[str]]): List of sender email addresses to filter emails.
            output_dir (str): Directory to save the output CSV file (default is "output").
        """
        try:
            # Connect to the email server using the injected or default EmailClient.
            self.client.connect()

            # Fetch emails from the server.
            emails = self.client.fetch_emails(limit=limit)

            # Update filter criteria based on the provided keywords and senders.
            # This allows the filter to be configured dynamically for each processing task.
            self.filter.subject_keywords = keywords or []
            self.filter.sender_keywords = senders or []

            # Filter the fetched emails using the injected or default EmailFilter.
            filtered_emails = self.filter.filter_emails(emails)

            # Extract links from the filtered emails.
            extracted_links: List[Tuple[str, str]] = []
            for email_data in filtered_emails:
                links = self.extractor.extract_links_from_text(email_data["body"])
                for link in links:
                    extracted_links.append((email_data.get("uid", "N/A"), link))  # "N/A" if uid is missing

            # Save the extracted links to a CSV file.
            os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a timestamp for the filename.
            output_file = os.path.join(output_dir, f"extracted_links_{timestamp}.csv")
            self._save_to_csv(output_file, extracted_links)

            print(f"✅ Processed {len(filtered_emails)} filtered emails and saved {len(extracted_links)} links to {output_file}")

        except Exception as e:
            # Handle any exceptions that occur during the email processing.
            print(f"❌ An error occurred while processing emails: {e}")
            raise  # Re-raise the exception for debugging and to signal failure.
        finally:
            # Ensure that the connection to the email server is closed, even if errors occur.
            self.client.disconnect()

    def _save_to_csv(self, file_path: str, data: List[Tuple[str, str]]):
        """
        Saves data (e.g., extracted links) to a CSV file.  Handles potential file I/O errors.

        Args:
            file_path (str): The path to the CSV file.
            data (List[Tuple[str, str]]): The data to save (list of tuples, e.g., (uid, link)).
        """
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["UID", "Link"])  # Write the header row.
                writer.writerows(data)  # Write the data rows.
        except Exception as e:
            # Handle any exceptions that occur during file operations.
            print(f"❌ Failed to save data to CSV: {e}")
            raise  # Re-raise the exception for debugging and to signal failure.


if __name__ == "__main__":
    # Example usage of the EmailProcessor class.  This code is typically used
    # when the script is run directly (not imported as a module).

    # Load credentials from environment variables.  This is a more secure
    # way to handle sensitive information than hardcoding them.
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")  # Default to Gmail if not set.
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    mailbox = os.getenv("MAILBOX", "INBOX")  # Default to INBOX if not set.

    # Validate that the required environment variables are set.
    if not email_user or not email_pass:
        raise ValueError("EMAIL_USER and EMAIL_PASS environment variables must be set.")

    # Initialize the EmailProcessor with the loaded credentials.
    processor = EmailProcessor(imap_server, email_user, email_pass, mailbox)

    # Define filtering criteria (keywords and senders).
    keywords = ["invoice", "urgent", "meeting"]
    senders = ["boss@example.com", "hr@example.com"]

    # Process emails using the defined criteria.
    processor.process_emails(limit=100, keywords=keywords, senders=senders)
