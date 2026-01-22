#!/usr/bin/env python3
"""
JavBus Scraper - Extract AV metadata from javbus.com

Usage:
    python javbus_scraper.py <code>

Returns JSON with: studio, title, actresses
"""

import sys
import re
import json
from urllib.request import urlopen, Request
from urllib.parse import quote
from html.parser import HTMLParser


class JavBusParser(HTMLParser):
    """Parse JavBus HTML to extract metadata"""
    
    def __init__(self):
        super().__init__()
        self.studio = None
        self.title = None
        self.actresses = []
        
        # State tracking
        self._in_info_section = False
        self._next_is_studio = False
        self._in_title = False
        self._in_actress_section = False
        self._next_is_actress = False
        self._current_tag = None
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Find title in h3 tag
        if tag == 'h3' and not self.title:
            self._in_title = True
        
        # Find info section
        if tag == 'p' and attrs_dict.get('class') == 'header':
            self._in_info_section = True
        
        # Find studio link
        if self._in_info_section and tag == 'a':
            href = attrs_dict.get('href')
            if href and '/studio/' in href:
                self._next_is_studio = True
        
        # Find actress section
        if tag == 'div' and attrs_dict.get('id') == 'avatar-waterfall':
            self._in_actress_section = True
        
        # Find actress name
        if self._in_actress_section and tag == 'span':
            self._next_is_actress = True
    
    def handle_endtag(self, tag):
        if tag == 'h3':
            self._in_title = False
        if tag == 'p':
            self._in_info_section = False
        if tag == 'div':
            self._in_actress_section = False
    
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        
        # Extract title
        if self._in_title and not self.title:
            self.title = data
        
        # Extract studio
        if self._next_is_studio:
            self.studio = data
            self._next_is_studio = False
        
        # Extract actress
        if self._next_is_actress and data:
            self.actresses.append(data)
            self._next_is_actress = False


def scrape_javbus(code):
    """
    Scrape metadata from javbus.com
    
    Args:
        code: AV code (e.g., SSIS-001)
    
    Returns:
        dict with keys: studio, title, actresses
        None if not found or error
    """
    try:
        # Normalize code (uppercase, remove spaces)
        code = code.upper().strip().replace(' ', '-')
        
        # Build URL
        url = f"https://www.javbus.com/{quote(code)}"
        
        # Fetch page with user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = Request(url, headers=headers)
        
        with urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Parse HTML
        parser = JavBusParser()
        parser.feed(html)
        
        # Validate results
        if not parser.studio and not parser.title:
            return None
        
        return {
            'studio': parser.studio or 'Unknown',
            'title': parser.title or code,
            'actresses': parser.actresses
        }
    
    except Exception as e:
        print(f"Error scraping {code}: {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python javbus_scraper.py <code>")
        sys.exit(1)
    
    code = sys.argv[1]
    result = scrape_javbus(code)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Not found"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
