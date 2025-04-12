# processor.py
'''
Note: In this processor, the EmailClient’s fetch_emails returns a list of dictionaries with keys "subject", "from", "body", 
and I suggest you modify the EmailClient accordingly to include a “uid” field if needed.
'''


import os
import csv
from datetime import datetime
from email_client import EmailClient
from email_filter import EmailFilter
from link_extractor import LinkExtractor

def process_emails():
    # Set up email client with credentials from config.env via os.getenv
    import os
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    mailbox = os.getenv("MAILBOX", "INBOX")

    client = EmailClient(imap_server, email_user, email_pass, mailbox)
    client.connect()
    emails = client.fetch_emails(limit=100)  # adjust limit as needed

    # Filtering: Create an EmailFilter (example keywords and senders)
    filter_obj = EmailFilter(
        keywords=["invoice", "urgent", "meeting"],
        senders=["boss@example.com", "hr@example.com"]
    )
    filtered = filter_obj.filter_emails(emails)

    # Link extraction: For each filtered email, extract links.
    extractor = LinkExtractor()
    extracted_links = []
    for email_data in filtered:
        links = extractor.extract_links(email_data)
        for link in links:
            extracted_links.append((email_data.get("uid", "N/A"), link))

    # Save extracted links to a CSV file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"extracted_links_{timestamp}.csv")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["UID", "Link"])
        writer.writerows(extracted_links)
    print(f"Processed {len(filtered)} filtered emails and saved {len(extracted_links)} links to {output_file}")

    client.disconnect()

if __name__ == "__main__":
    process_emails()
