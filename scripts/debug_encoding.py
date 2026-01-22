#!/usr/bin/env python3
import sys
import urllib.request
import ssl

code = sys.argv[1] if len(sys.argv) > 1 else "SSNI-424"
proxy = 'http://127.0.0.1:7890'
url = f"https://www.javbus.com/{code}"

proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
https_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(proxy_handler, https_handler)
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

response = opener.open(url, timeout=20)
html = response.read()

# Save to file for inspection
with open('javbus_debug.html', 'wb') as f:
    f.write(html)

print(f"Saved HTML to javbus_debug.html ({len(html)} bytes)")
print(f"Encoding: {response.headers.get('Content-Type')}")

# Try different decodings
for enc in ['utf-8', 'gbk', 'shift-jis', 'euc-jp']:
    try:
        text = html.decode(enc, errors='ignore')
        print(f"\n{enc}: First 500 chars of title area:")
        import re
        title_match = re.search(r'<h3>([^<]{0,100})</h3>', text)
        if title_match:
            print(f"  {title_match.group(1)[:100]}")
    except:
        pass
