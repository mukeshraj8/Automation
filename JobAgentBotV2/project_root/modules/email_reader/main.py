""" 
project_root/
├── config.env
├── email_client.py
├── email_filter.py
├── link_extractor.py
├── main.py
├── requirements.txt
└── tests/
    ├── test_email_client.py
    ├── test_email_filter.py
    └── test_link_extractor.py
Note: You should place your config.env in the project root. (See below for a sample.)

Sample config.env
# config.env
EMAIL_USER=mukesh.rajendra@gmail.com
EMAIL_PASS=your_app_password_here
IMAP_SERVER=imap.gmail.com
MAILBOX=INBOX
LOG_PATH=logs/app.log

"""


from email_client import EmailClient
from email_filter import EmailFilter
import config

def main():
    # Initialize the email client
    client = EmailClient(
        imap_server=config.IMAP_SERVER,
        email_account=config.EMAIL_ACCOUNT,
        email_password=config.EMAIL_PASSWORD,
        mailbox=config.MAILBOX
    )

    # Connect and fetch emails
    client.connect()
    emails = client.fetch_emails(limit=100)  # Fetch latest 100 emails

    # Initialize the filter with criteria
    email_filter = EmailFilter(
        subject_keywords=["urgent", "important", "action required"],
        sender_addresses=["boss@example.com", "alerts@example.com"]
    )

    # Filter emails
    filtered_emails = email_filter.filter_emails(emails)

    # Display filtered emails
    print(f"\nTotal filtered emails: {len(filtered_emails)}\n")
    for idx, (subject, from_, body) in enumerate(filtered_emails, 1):
        print(f"Email {idx}:")
        print(f"Subject: {subject}")
        print(f"From: {from_}")
        print(f"Body Preview: {body[:100]}...")  # show first 100 chars
        print("-" * 50)

    client.disconnect()

if __name__ == "__main__":
    main()
