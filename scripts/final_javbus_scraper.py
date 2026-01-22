#!/usr/bin/env python3
"""
JavBus 爬虫 - 支持代理、Cookie和年龄验证

Usage:
    python final_javbus_scraper.py <code> [--proxy http://127.0.0.1:7890]
"""

import sys
import re
import json
import http.cookiejar
import urllib.request
import urllib.error
import ssl


def scrape_javbus_final(code, proxy='http://127.0.0.1:7890'):
    """
    Scrape javbus with age verification bypass
    """
    try:
        code = code.upper().strip().replace(' ', '-')
        url = f"https://www.javbus.com/{code}"
        
        # Set up cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
        
        # Set up proxy
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy,
            'https': proxy
        })
        
        # SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        
        # Build opener
        opener = urllib.request.build_opener(
            proxy_handler,
            https_handler,
            cookie_processor
        )
        
        # Headers
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7'),
            ('Cookie', 'existmag=all'),  # Bypass age verification
            ('Referer', 'https://www.javbus.com/'),
        ]
        
        # Fetch page
        response = opener.open(url, timeout=20)
        html = response.read().decode('utf-8', errors='ignore')
        
        # Check if we got age verification page
        if 'Age Verification' in html or 'driver-verify' in html:
            print("Warning: Got age verification page", file=sys.stderr)
            # Try to bypass by setting cookie and retry
            opener.addheaders.append(('Cookie', 'existmag=all; age_verified=1'))
            response = opener.open(url, timeout=20)
            html = response.read().decode('utf-8', errors='ignore')
        
        # Extract metadata
        metadata = {
            'code': code,
            'studio': None,
            'title': None,
            'actresses': [],
            'poster_url': None
        }
        
        # Extract title
        title_match = re.search(r'<h3>([^<]+)</h3>', html)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Extract studio
        studio_match = re.search(r'<a[^>]*href="[^"]*\/studio\/[^"]*"[^>]*>([^<]+)</a>', html)
        if studio_match:
            metadata['studio'] = studio_match.group(1).strip()
        
        # Extract actresses - multiple patterns
        # Pattern 1: avatar-box with title attribute
        actress_pattern1 = r'<a[^>]*class="avatar-box"[^>]*title="([^"]+)"'
        matches1 = re.findall(actress_pattern1, html)
        
        # Pattern 2: span inside avatar waterfall
        actress_pattern2 = r'<div[^>]*class="star-name"[^>]*>([^<]+)</div>'
        matches2 = re.findall(actress_pattern2, html)
        
        # Pattern 3: text after avatar image
        actress_pattern3 = r'<div[^>]*id="avatar-waterfall"[^>]*>.*?<span>([^<]+)</span>'
        matches3 = re.findall(actress_pattern3, html, re.DOTALL)
        
        # Combine all matches
        all_actresses = list(set(matches1 + matches2 + matches3))
        metadata['actresses'] = [a.strip() for a in all_actresses if a.strip() and len(a.strip()) > 1]
        
        # Extract poster
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
        if not metadata['studio'] and not metadata['title']:
            return None
        
        # Defaults
        if not metadata['studio']:
            metadata['studio'] = 'Unknown'
        if not metadata['title']:
            metadata['title'] = code
        
        return metadata
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Code {code} not found", file=sys.stderr)
        else:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('code', help='AV code')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890')
    args = parser.parse_args()
    
    result = scrape_javbus_final(args.code, args.proxy)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Not found"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
