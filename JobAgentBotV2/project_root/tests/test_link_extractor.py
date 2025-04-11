import sys
import os
import unittest

# Add the project_root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.email_link_extractor.link_extractor import LinkExtractor
from bs4 import BeautifulSoup

class TestLinkExtractor(unittest.TestCase):

    def test_extract_links_from_text(self):
        text = "Visit https://example.com and also check http://test.org for more info."
        expected_links = ['https://example.com', 'http://test.org']
        self.assertEqual(LinkExtractor.extract_links_from_text(text), expected_links)

    def test_extract_links_from_html(self):
        html = """
        <html>
            <body>
                <a href="https://example.com">Example</a>
                <a href="http://test.org">Test</a>
                <a href="#">No link</a>
            </body>
        </html>
        """
        expected_links = ['https://example.com', 'http://test.org', '#']
        self.assertEqual(LinkExtractor.extract_links_from_html(html), expected_links)

    def test_extract_all_links_plain_text(self):
        text = "Go to https://example.com for details."
        expected = ['https://example.com']
        self.assertEqual(LinkExtractor.extract_all_links(text, is_html=False), expected)

    def test_extract_all_links_html(self):
        html = '<a href="https://example.com">Example</a>'
        expected = ['https://example.com']
        self.assertEqual(LinkExtractor.extract_all_links(html, is_html=True), expected)

    def test_extract_links_from_text_with_no_links(self):
        text = "No links here!"
        self.assertEqual(LinkExtractor.extract_links_from_text(text), [])

    def test_extract_links_from_html_with_no_links(self):
        html = "<html><body><p>No links!</p></body></html>"
        self.assertEqual(LinkExtractor.extract_links_from_html(html), [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
