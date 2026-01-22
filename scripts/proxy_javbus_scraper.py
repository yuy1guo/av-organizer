#!/usr/bin/env python3
"""
增强版 JavBus 爬虫 - 支持代理和海报下载

Usage:
    python proxy_javbus_scraper.py <code> [--proxy http://127.0.0.1:7890]

Returns JSON with: studio, title, actresses, poster_url
"""

import sys
import re
import json
import urllib.request
import urllib.error
import ssl


def scrape_javbus_with_proxy(code, proxy='http://127.0.0.1:7890'):
    """
    Scrape metadata from javbus.com with proxy support
    
    Args:
        code: AV code (e.g., SSIS-001)
        proxy: Proxy URL
    
    Returns:
        dict with keys: studio, title, actresses, poster_url
        None if not found or error
    """
    try:
        # Normalize code
        code = code.upper().strip().replace(' ', '-')
        url = f"https://www.javbus.com/{code}"
        
        # Set up proxy
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy,
            'https': proxy
        })
        
        # Create SSL context that doesn't verify certificates (for proxy compatibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        
        # Build opener with proxy
        opener = urllib.request.build_opener(proxy_handler, https_handler)
        
        # Set headers
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Referer', 'https://www.javbus.com/'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8'),
        ]
        
        # Fetch page
        response = opener.open(url, timeout=20)
        html = response.read().decode('utf-8', errors='ignore')
        
        # Extract metadata using regex
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
            metadata['title'] = title_match.group(1).strip()
        
        # Extract studio
        studio_match = re.search(r'<a[^>]*href="[^"]*\/studio\/[^"]*"[^>]*>([^<]+)</a>', html)
        if studio_match:
            metadata['studio'] = studio_match.group(1).strip()
        
        # Extract actresses - improved pattern
        # Look for star name in the specific structure
        actress_pattern = r'<a[^>]*class="avatar-box"[^>]*title="([^"]+)"'
        actress_matches = re.findall(actress_pattern, html)
        if actress_matches:
            metadata['actresses'] = [a.strip() for a in actress_matches if a.strip()]
        
        # Alternative actress extraction from span tags in avatar section
        if not metadata['actresses']:
            actress_section = re.search(r'<div[^>]*id="avatar-waterfall"[^>]*>(.*?)</div[^>]*>', html, re.DOTALL)
            if actress_section:
                span_matches = re.findall(r'<span[^>]*>([^<]+)</span>', actress_section.group(1))
                metadata['actresses'] = [a.strip() for a in span_matches if a.strip() and len(a.strip()) > 1]
        
        # Extract poster URL
        # Pattern 1: bigImage link
        poster_match = re.search(r'<a[^>]*class="bigImage"[^>]*href="([^"]+)"', html)
        if poster_match:
            poster_url = poster_match.group(1)
            # Convert relative URL to absolute
            if poster_url.startswith('//'):
                metadata['poster_url'] = 'https:' + poster_url
            elif poster_url.startswith('/'):
                metadata['poster_url'] = 'https://www.javbus.com' + poster_url
            else:
                metadata['poster_url'] = poster_url
        else:
            # Pattern 2: Direct image from pics.dmm.co.jp
            poster_match = re.search(r'<img[^>]*src="(https://pics\.dmm\.co\.jp/[^"]+)"', html)
            if poster_match:
                metadata['poster_url'] = poster_match.group(1)
        
        # Validate
        if not metadata['studio'] and not metadata['title']:
            return None
        
        # Set defaults
        if not metadata['studio']:
            metadata['studio'] = 'Unknown'
        if not metadata['title']:
            metadata['title'] = code
        
        return metadata
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Code {code} not found on javbus", file=sys.stderr)
        else:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error scraping {code}: {e}", file=sys.stderr)
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape JavBus metadata with proxy')
    parser.add_argument('code', help='AV code (e.g., SSIS-001)')
    parser.add_argument('--proxy', default='http://127.0.0.1:7890', 
                       help='Proxy URL (default: http://127.0.0.1:7890)')
    args = parser.parse_args()
    
    result = scrape_javbus_with_proxy(args.code, args.proxy)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Not found"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
