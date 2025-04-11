# link_extractor.py

import re
from bs4 import BeautifulSoup

class LinkExtractor:
    @staticmethod
    def extract_links_from_text(text):
        """Extract all URLs from plain text"""
        url_pattern = re.compile(r'https?://\S+')
        return url_pattern.findall(text)

    @staticmethod
    def extract_links_from_html(html_content):
        """Extract all URLs from HTML content"""
        soup = BeautifulSoup(html_content, "html.parser")
        return [a['href'] for a in soup.find_all('a', href=True)]

    @staticmethod
    def extract_all_links(text, is_html=False):
        """Extract links from either plain text or HTML"""
        if is_html:
            return LinkExtractor.extract_links_from_html(text)
        else:
            return LinkExtractor.extract_links_from_text(text)
