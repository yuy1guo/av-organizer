#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试代理连接"""

import urllib.request
import urllib.error
import ssl
import sys

def test_proxy(proxy='http://127.0.0.1:7890'):
    try:
        print(f"Testing proxy: {proxy}")
        
        # Setup proxy
        proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
        
        # SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        
        # Build opener
        opener = urllib.request.build_opener(proxy_handler, https_handler)
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
        ]
        
        # Test connection
        print("Connecting to javbus.com...")
        url = "https://www.javbus.com/SONE-586"
        response = opener.open(url, timeout=20)
        html = response.read().decode('utf-8', errors='ignore')
        
        print(f"Success! Received {len(html)} bytes")
        print(f"HTML preview: {html[:200]}")
        
        return True
        
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        print(f"Reason: {e.reason if hasattr(e, 'reason') else 'Unknown'}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_proxy()
    sys.exit(0 if success else 1)
