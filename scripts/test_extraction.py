#!/usr/bin/env python3
import re

with open('SSNI-424_utf8.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("=== Title ===")
title_match = re.search(r'<h3>([^<]+)</h3>', html)
if title_match:
    full_title = title_match.group(1)
    print(f'Full: {full_title}')
    cleaned = re.sub(r'^SSNI-424\s+', '', full_title)
    print(f'Cleaned: {cleaned}')

print("\n=== Actress from avatar-waterfall ===")
avatar = re.search(r'<div[^>]*id="avatar-waterfall"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
if avatar:
    print(f"Avatar section length: {len(avatar.group(1))}")
    spans = re.findall(r'<span>([^<]+)</span>', avatar.group(1))
    print(f'From span tags: {spans}')
    
print("\n=== Actress from img title ===")
imgs = re.findall(r'<img[^>]*src="/pics/actress/[^"]*"[^>]*title="([^"]+)"', html)
print(f'From img titles: {imgs}')

print("\n=== Studio ===")
studio = re.search(r'<a[^>]*href="[^"]*\/studio\/[^"]*"[^>]*>([^<]+)</a>', html)
if studio:
    print(f'Studio: {studio.group(1)}')
