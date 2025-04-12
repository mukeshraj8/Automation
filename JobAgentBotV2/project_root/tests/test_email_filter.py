import unittest
from email.message import EmailMessage
from modules.email_reader.email_filter import EmailFilter
import sys
sys.path.append("d:/Automation/JobAgentBotV2/project_root/modules/email_reader/")

class TestEmailFilter(unittest.TestCase):

    def setUp(self):
        self.subject_keywords = ["urgent", "important", "action required"]
        self.sender_keywords = ["boss@example.com", "admin@example.com"]
        self.max_attachment_size = 1024 * 1024  # 1 MB
        self.importance_levels = ["high", "urgent"]
        self.filter = EmailFilter(
            subject_keywords=self.subject_keywords,
            sender_keywords=self.sender_keywords,
            max_attachment_size=self.max_attachment_size,
            importance_levels=self.importance_levels
        )

    def test_filter_by_subject_keyword(self):
        email = EmailMessage()
        email['Subject'] = "This is an urgent update"
        email['From'] = "someone@example.com"
        self.assertTrue(self.filter.filter_email(email))

    def test_filter_by_sender_keyword(self):
        email = EmailMessage()
        email['Subject'] = "Random subject"
        email['From'] = "boss@example.com"
        self.assertTrue(self.filter.filter_email(email))

    def test_filter_by_importance(self):
        email = EmailMessage()
        email['Subject'] = "Random subject"
        email['From'] = "someone@example.com"
        email['Importance'] = "high"
        self.assertTrue(self.filter.filter_email(email))

    def test_filter_by_priority(self):
        email = EmailMessage()
        email['Subject'] = "Random subject"
        email['From'] = "someone@example.com"
        email['X-Priority'] = "1 (Highest)"
        self.assertTrue(self.filter.filter_email(email))

    def test_filter_by_attachment_size(self):
        email = EmailMessage()
        email['Subject'] = "Important document attached"  # <-- matches 'important' keyword
        email['From'] = "someone@example.com"

        # Add a small attachment
        email.add_attachment(
            b"small attachment", 
            maintype="application", 
            subtype="octet-stream", 
            filename="file.txt"
        )
        self.assertTrue(self.filter.filter_email(email))  # Now this should pass

        # Add a large attachment exceeding the max size
        large_attachment = b"a" * (self.max_attachment_size + 1)
        email = EmailMessage()  # Reset email to avoid multiple attachments
        email['Subject'] = "Important document attached"  # maintain matching subject
        email['From'] = "someone@example.com"
        email.add_attachment(
            large_attachment, 
            maintype="application", 
            subtype="octet-stream", 
            filename="large_file.txt"
        )
        self.assertFalse(self.filter.filter_email(email))  # Now this should correctly fail


if __name__ == "__main__":
    unittest.main()