#!/usr/bin/env python3
"""
增强版 JavBus 爬虫 - 支持海报下载

Usage:
    python enhanced_javbus_scraper.py <code>

Returns JSON with: studio, title, actresses, poster_url
"""

import sys
import re
import json
from urllib.request import urlopen, Request
from urllib.parse import quote
from html.parser import HTMLParser


class EnhancedJavBusParser(HTMLParser):
    """Parse JavBus HTML to extract metadata including poster"""
    
    def __init__(self):
        super().__init__()
        self.studio = None
        self.title = None
        self.actresses = []
        self.poster_url = None
        
        # State tracking
        self._in_info_section = False
        self._next_is_studio = False
        self._in_title = False
        self._in_actress_section = False
        self._next_is_actress = False
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Find title in h3 tag
        if tag == 'h3' and not self.title:
            self._in_title = True
        
        # Find poster image
        if tag == 'img' and not self.poster_url:
            src = attrs_dict.get('src')
            img_class = attrs_dict.get('class')
            # javbus poster pattern: usually in a specific class or large image
            if (img_class and 'bigImage' in img_class) or (src and 'pics.dmm.co.jp' in src):
                self.poster_url = src
        
        # Alternative: look for poster in a tag with specific pattern
        if tag == 'a' and attrs_dict.get('class') == 'bigImage':
            href = attrs_dict.get('href', '')
            if href:
                self.poster_url = href
        
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


def scrape_javbus_enhanced(code, proxy=None):
    """
    Scrape metadata from javbus.com including poster
    
    Args:
        code: AV code (e.g., SSIS-001)
        proxy: Proxy URL (e.g., 'http://127.0.0.1:7890')
    
    Returns:
        dict with keys: studio, title, actresses, poster_url
        None if not found or error
    """
    try:
        # Normalize code (uppercase, remove spaces)
        code = code.upper().strip().replace(' ', '-')
        
        # Build URL
        url = f"https://www.javbus.com/{quote(code)}"
        
        # Fetch page with user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.javbus.com/'
        }
        req = Request(url, headers=headers)
        
        # Set up proxy if provided
        if proxy:
            from urllib.request import ProxyHandler, build_opener
            proxy_handler = ProxyHandler({'http': proxy, 'https': proxy})
            opener = build_opener(proxy_handler)
            response = opener.open(req, timeout=15)
            html = response.read().decode('utf-8', errors='ignore')
        else:
            with urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
        
        # Parse HTML
        parser = EnhancedJavBusParser()
        parser.feed(html)
        
        # Extract poster URL using regex as fallback
        if not parser.poster_url:
            # Pattern: <a class="bigImage" href="...">
            poster_match = re.search(r'<a[^>]*class="bigImage"[^>]*href="([^"]+)"', html)
            if poster_match:
                parser.poster_url = poster_match.group(1)
            else:
                # Pattern: <img ... src="https://pics.dmm.co.jp/..."
                img_match = re.search(r'<img[^>]*src="(https://pics\.dmm\.co\.jp/[^"]+)"', html)
                if img_match:
                    parser.poster_url = img_match.group(1)
        
        # Validate results
        if not parser.studio and not parser.title:
            return None
        
        return {
            'studio': parser.studio or 'Unknown',
            'title': parser.title or code,
            'actresses': parser.actresses,
            'poster_url': parser.poster_url
        }
    
    except Exception as e:
        print(f"Error scraping {code}: {e}", file=sys.stderr)
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape JavBus metadata')
    parser.add_argument('code', help='AV code (e.g., SSIS-001)')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890', 
                       help='Proxy URL (default: http://127.0.0.1:7890)')
    args = parser.parse_args()
    
    result = scrape_javbus_enhanced(args.code, args.proxy)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Not found"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
