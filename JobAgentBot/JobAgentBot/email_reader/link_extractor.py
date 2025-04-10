# link_extractor.py

import re
from bs4 import BeautifulSoup

def extract_links_from_text(text):
    """
    Extracts all HTTP/HTTPS links from plain text using regex.
    """
    # Regex to find links
    url_pattern = r'(https?://\S+)'
    links = re.findall(url_pattern, text)
    return links

def extract_links_from_html(html_content):
    """
    Extracts all links from HTML content using BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for a_tag in soup.find_all("a", href=True):
        links.append(a_tag['href'])
    return links

def extract_first_link(content, is_html=False):
    """
    Extracts the first link from given content.
    If content is HTML, it uses BeautifulSoup. Otherwise regex.
    """
    links = extract_links_from_html(content) if is_html else extract_links_from_text(content)
    return links[0] if links else None
