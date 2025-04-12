import sys
import os
import unittest

# Add the project_root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.email_link_extractor.link_extractor import LinkExtractor
from bs4 import BeautifulSoup

class TestLinkExtractor(unittest.TestCase):

    def test_extract_links_from_text(self):
        """
        Test extracting links from plain text.
        Ensures that valid URLs in plain text are correctly identified and returned.
        """
        text = "Visit https://example.com and also check http://test.org for more info."
        expected_links = ['https://example.com', 'http://test.org']
        self.assertEqual(LinkExtractor.extract_links_from_text(text), expected_links)

    def test_extract_links_from_html(self):
        """
        Test extracting links from HTML content.
        Ensures that valid URLs in anchor tags are correctly identified and returned.
        """
        html = """
        <html>
            <body>
                <a href="https://example.com">Example</a>
                <a href="http://test.org">Test</a>
                <a href="#">No link</a>
            </body>
        </html>
        """
        # Update expected_links to exclude '#'
        expected_links = ['https://example.com', 'http://test.org']
        self.assertEqual(LinkExtractor.extract_links_from_html(html), expected_links)

    def test_extract_all_links_plain_text(self):
        """
        Test extracting all links from plain text using the extract_all_links method.
        Ensures that the method works correctly when is_html=False.
        """
        text = "Go to https://example.com for details."
        expected = ['https://example.com']
        self.assertEqual(LinkExtractor.extract_all_links(text, is_html=False), expected)

    def test_extract_all_links_html(self):
        """
        Test extracting all links from HTML content using the extract_all_links method.
        Ensures that the method works correctly when is_html=True.
        """
        html = '<a href="https://example.com">Example</a>'
        expected = ['https://example.com']
        self.assertEqual(LinkExtractor.extract_all_links(html, is_html=True), expected)

    def test_extract_links_from_text_with_no_links(self):
        """
        Test extracting links from plain text with no URLs.
        Ensures that an empty list is returned when no links are present.
        """
        text = "No links here!"
        self.assertEqual(LinkExtractor.extract_links_from_text(text), [])

    def test_extract_links_from_html_with_no_links(self):
        """
        Test extracting links from HTML content with no anchor tags containing href attributes.
        Ensures that an empty list is returned when no links are present.
        """
        html = "<html><body><p>No links!</p></body></html>"
        self.assertEqual(LinkExtractor.extract_links_from_html(html), [])

if __name__ == '__main__':
    unittest.main(verbosity=2)