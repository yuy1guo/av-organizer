#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试爬虫并显示结果"""

import sys
import json
import os

# 设置控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入爬虫
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from complete_javbus_scraper import scrape_javbus_complete

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "SONE-586"
    proxy = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:7890"
    
    print(f"正在爬取: {code}")
    print(f"使用代理: {proxy}")
    print("-" * 60)
    
    result = scrape_javbus_complete(code, proxy)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 60)
        print(f"✓ 厂商: {result['studio']}")
        print(f"✓ 标题: {result['title']}")
        print(f"✓ 女优: {', '.join(result['actresses'])}")
        print(f"✓ 海报: {result['poster_url']}")
    else:
        print("✗ 爬取失败")
        sys.exit(1)
