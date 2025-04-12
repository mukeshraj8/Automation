import re
from bs4 import BeautifulSoup

class LinkExtractor:
    @staticmethod
    def extract_links_from_text(text):
        """Extract all URLs from plain text"""
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        return url_pattern.findall(text)

    @staticmethod
    def extract_links_from_html(html_content):
        """Extract all valid URLs from HTML content"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            links = [a['href'] for a in soup.find_all('a', href=True)]
            return [link for link in links if link.startswith('http')]
        except Exception:
            return []

    @staticmethod
    def extract_all_links(text, is_html=False):
        """Extract links from either plain text or HTML"""
        if is_html or ('<html' in text.lower() and '</html>' in text.lower()):
            return LinkExtractor.extract_links_from_html(text)
        else:
            return LinkExtractor.extract_links_from_text(text)