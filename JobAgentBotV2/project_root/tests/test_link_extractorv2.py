# test/test_link_extractor.py

import unittest
from email.message import EmailMessage
from link_extractor import LinkExtractor

class TestLinkExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = LinkExtractor()

    def test_extract_links_from_text(self):
        text = "Visit https://example.com and http://test.com for more info."
        links = self.extractor.extract_links_from_text(text)
        self.assertIn("https://example.com", links)
        self.assertIn("http://test.com", links)

    def test_extract_links_from_email(self):
        msg = EmailMessage()
        msg.set_content("Hello, check out https://openai.com.")
        links = self.extractor.extract_links_from_email(msg)
        self.assertEqual(links, ["https://openai.com"])

    def test_extract_links_from_html_email(self):
        msg = EmailMessage()
        html_content = '<html><body><a href="https://openai.com">OpenAI</a></body></html>'
        msg.add_alternative(html_content, subtype='html')
        links = self.extractor.extract_links_from_email(msg)
        self.assertEqual(links, ["https://openai.com"])

if __name__ == "__main__":
    unittest.main()
