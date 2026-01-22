#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavBus 完整爬虫 - 支持代理、正确编码和女优抓取

Usage:
    python complete_javbus_scraper.py <code> [--proxy http://127.0.0.1:7890]
"""

import sys
import re
import json
import http.cookiejar
import urllib.request
import urllib.error
import ssl


def scrape_javbus_complete(code, proxy='http://127.0.0.1:7890'):
    """
    Complete JavBus scraper with proper encoding and actress extraction
    """
    try:
        code = code.upper().strip().replace(' ', '-')
        url = f"https://www.javbus.com/{code}"
        
        # Cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
        
        # Proxy
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        
        # SSL
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        
        # Opener
        opener = urllib.request.build_opener(proxy_handler, https_handler, cookie_processor)
        
        # Headers with age verification bypass
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7'),
            ('Cookie', 'existmag=all'),
            ('Referer', 'https://www.javbus.com/'),
        ]
        
        # Fetch
        response = opener.open(url, timeout=20)
        html = response.read().decode('utf-8', errors='ignore')
        
        # Check for age verification
        if 'Age Verification' in html or len(html) < 10000:
            raise Exception("Age verification page received")
        
        # Initialize metadata
        metadata = {
            'code': code,
            'studio': None,
            'title': None,
            'actresses': [],
            'poster_url': None
        }
        
        # Extract title from h3 tag
        title_match = re.search(r'<h3>([^<]+)</h3>', html)
        if title_match:
            full_title = title_match.group(1).strip()
            # Remove code prefix (e.g., "SSNI-424 " from the beginning)
            # Pattern: CODE followed by space
            title_cleaned = re.sub(rf'^{code}\s+', '', full_title)
            metadata['title'] = title_cleaned.strip()
        
        # Extract studio
        studio_match = re.search(r'<a[^>]*href="[^"]*\/studio\/[^"]*"[^>]*>([^<]+)</a>', html)
        if studio_match:
            metadata['studio'] = studio_match.group(1).strip()
        
        # Extract actresses - multiple methods
        actresses = []
        
        # Method 1: From avatar-waterfall section with span tags
        avatar_section = re.search(r'<div[^>]*id="avatar-waterfall"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        if avatar_section:
            # Find all span tags with actress names
            span_matches = re.findall(r'<span>([^<]+)</span>', avatar_section.group(1))
            actresses.extend([a.strip() for a in span_matches if a.strip()])
        
        # Method 2: From img title attributes
        img_matches = re.findall(r'<img[^>]*src="/pics/actress/[^"]*"[^>]*title="([^"]+)"', html)
        actresses.extend([a.strip() for a in img_matches if a.strip()])
        
        # Method 3: From star-name div
        star_name_matches = re.findall(r'<div[^>]*class="star-name"[^>]*><a[^>]*title="([^"]+)"', html)
        actresses.extend([a.strip() for a in star_name_matches if a.strip()])
        
        # Remove duplicates and filter
        metadata['actresses'] = list(dict.fromkeys([
            a for a in actresses 
            if a and len(a) > 1 and not a.isdigit()
        ]))
        
        # Extract poster URL
        poster_match = re.search(r'<a[^>]*class="bigImage"[^>]*href="([^"]+)"', html)
        if poster_match:
            poster_url = poster_match.group(1)
            if poster_url.startswith('//'):
                metadata['poster_url'] = 'https:' + poster_url
            elif poster_url.startswith('/'):
                metadata['poster_url'] = 'https://www.javbus.com' + poster_url
            else:
                metadata['poster_url'] = poster_url
        
        # Validate
        if not metadata['title']:
            return None
        
        # Defaults
        if not metadata['studio']:
            metadata['studio'] = 'Unknown'
        
        return metadata
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: {code} not found", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('code', help='AV code')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890')
    args = parser.parse_args()
    
    result = scrape_javbus_complete(args.code, args.proxy)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Not found"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
