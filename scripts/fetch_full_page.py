#!/usr/bin/env python3
import sys
import http.cookiejar
import urllib.request
import ssl

code = sys.argv[1] if len(sys.argv) > 1 else "SSNI-424"
proxy = 'http://127.0.0.1:7890'
url = f"https://www.javbus.com/{code}"

cookie_jar = http.cookiejar.CookieJar()
cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)

proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
https_handler = urllib.request.HTTPSHandler(context=ssl_context)

opener = urllib.request.build_opener(proxy_handler, https_handler, cookie_processor)

# Important: Set the right cookie to bypass age verification
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    ('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8'),
    ('Cookie', 'existmag=all'),
]

try:
    response = opener.open(url, timeout=20)
    html = response.read()
    
    # Save raw bytes
    with open(f'{code}_raw.html', 'wb') as f:
        f.write(html)
    
    print(f"Saved to {code}_raw.html ({len(html)} bytes)")
    
    # Try UTF-8 decode and save
    text = html.decode('utf-8', errors='ignore')
    with open(f'{code}_utf8.html', 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Check if we have actual content
    if '演員' in text:
        print("✓ Found 演員 section!")
        # Find actress section
        import re
        actress_section = re.search(r'演員:.*?<div[^>]*>(.*?)</div>', text, re.DOTALL)
        if actress_section:
            print("Actress section:")
            print(actress_section.group(0)[:500])
    else:
        print("✗ No 演員 section found - might be age verification page")
        if 'Age Verification' in text:
            print("  Confirmed: Got age verification page")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
