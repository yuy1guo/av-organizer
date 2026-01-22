#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合版 AV 整理脚本 - 优先从 javbus 抓取，失败时使用内置规则

特性:
1. 尝试从 javbus.com 抓取真实片名和女优
2. 失败时使用内置规则（番号作为标题，Unknown 女优）
3. 支持女优二级文件夹
4. 支持海报下载（当可用时）
5. 支持 --retry-failed 重新处理 others/unknown

使用方法:
    python hybrid_organizer.py <directory> [--dry-run] [--retry-failed] [--first-only]
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path
import re
from urllib.request import urlopen, Request

# Video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb'}

# Get script directory
SCRIPT_DIR = Path(__file__).parent

# Studio mappings (fallback)
STUDIO_MAPPING = {
    'SSIS': 'S1', 'SSNI': 'S1', 'SONE': 'S1',
    'IPX': 'IdeaPocket', 'IPZZ': 'IdeaPocket',
    'MIDV': 'MOODYZ', 'MIAB': 'MOODYZ', 'MIDA': 'MOODYZ', 'MFYD': 'MOODYZ',
    'PRED': 'Premium',
    'JUR': 'Madonna', 'JUQ': 'Madonna', 'URE': 'Madonna',
    'EBWH': 'E-Body',
    'HMN': 'Hon Naka',
    'ADN': 'Attackers', 'ATID': 'Attackers',
    'MEYD': 'Tameike Goro',
    'ROYD': 'Royal',
    'DASS': 'DAS!',
    'DLDSS': 'DAHLIA',
    'SONE': 'S1',
    'START': 'SOD Create',
    'WAAA': 'Wanz Factory',
    'CAWD': 'kawaii',
    'ABF': 'Prestige',
    'FFT': 'Faleno', 'FNS': 'Faleno Star', 'FSDSS': 'FALENO',
    'NGOD': 'JET Eizou',
    'GVH': 'Glory Quest',
}


def extract_code(filename):
    """Extract AV code from filename"""
    name = filename.upper()
    
    patterns = [
        r'([A-Z]{2,6}[-\s]\d{3,5})',  # ABC-123 or ABC 123
        r'([A-Z]{2,6}\d{3,5})',       # ABC123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            code = match.group(1)
            # Normalize to hyphen format
            code = re.sub(r'([A-Z]+)\s+(\d+)', r'\1-\2', code)
            code = re.sub(r'([A-Z]+)(\d+)', r'\1-\2', code)
            return code
    
    return None


def fetch_metadata_from_javbus(code):
    """Try to fetch metadata from javbus.com"""
    try:
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'enhanced_javbus_scraper.py'), code],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=20
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'error' not in data:
                data['code'] = code
                data['source'] = 'javbus'
                return data
    except:
        pass
    
    return None


def get_fallback_metadata(code):
    """Generate fallback metadata using internal rules"""
    # Extract studio prefix
    prefix_match = re.match(r'([A-Z]+)', code.upper())
    if prefix_match:
        prefix = prefix_match.group(1)
        studio = STUDIO_MAPPING.get(prefix, 'Unknown')
    else:
        studio = 'Unknown'
    
    return {
        'code': code,
        'studio': studio,
        'title': code,  # Use code as title
        'actresses': [],  # No actress info
        'poster_url': None,
        'source': 'fallback'
    }


def fetch_metadata(code):
    """Fetch metadata with fallback"""
    print("  Trying javbus.com...")
    metadata = fetch_metadata_from_javbus(code)
    
    if metadata:
        print(f"  OK Got data from javbus.com")
        return metadata
    
    print("  ! javbus.com unavailable, using fallback rules")
    return get_fallback_metadata(code)


def normalize_studio(studio_name):
    """Normalize studio name to folder name"""
    if not studio_name:
        return 'others'
    
    cleaned = studio_name.lower().strip()
    
    # Remove special chars and convert spaces to hyphens
    normalized = re.sub(r'[^\w\s-]', '', cleaned)
    normalized = re.sub(r'[\s]+', '-', normalized)
    normalized = re.sub(r'-+', '-', normalized)
    
    return normalized if normalized else 'others'


def sanitize_filename(filename):
    """Remove invalid filesystem characters"""
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:200]


def download_poster(poster_url, target_path, code):
    """Download poster image"""
    if not poster_url:
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.javbus.com/'
        }
        req = Request(poster_url, headers=headers)
        
        with urlopen(req, timeout=15) as response:
            image_data = response.read()
        
        # Determine extension
        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        else:
            ext = '.jpg'
        
        # Save poster
        poster_filename = f"[{code}]-poster{ext}"
        poster_path = Path(target_path) / poster_filename
        
        with open(poster_path, 'wb') as f:
            f.write(image_data)
        
        return True
    except Exception as e:
        print(f"  ! Failed to download poster: {e}")
        return False


def scan_directory(directory, retry_failed=False, first_only=False):
    """Scan for video files"""
    results = []
    
    for item in Path(directory).iterdir():
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            results.append((str(item), False))
        
        elif item.is_dir():
            # Skip already organized studio folders unless retry_failed
            if retry_failed and item.name in ['others', 'unknown']:
                # Process contents
                for subitem in item.iterdir():
                    if subitem.is_file() and subitem.suffix.lower() in VIDEO_EXTENSIONS:
                        results.append((str(subitem), False))
                    elif subitem.is_dir():
                        video_files = [f for f in subitem.rglob('*') 
                                     if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
                        if video_files:
                            results.append((str(subitem), True))
            elif not retry_failed:
                # Check if folder contains videos
                video_files = [f for f in item.rglob('*') 
                             if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
                if video_files:
                    results.append((str(item), True))
    
    if first_only and results:
        results = results[:1]
    
    return results


def organize_item(item_path, is_folder, metadata, base_directory, dry_run=False):
    """Organize item with actress subfolder"""
    # Get studio folder
    studio_folder = normalize_studio(metadata['studio'])
    
    # Get actress name (first actress or "Unknown")
    actress_name = 'Unknown'
    if metadata.get('actresses') and len(metadata['actresses']) > 0:
        actress_name = sanitize_filename(metadata['actresses'][0])
    
    # Create studio/actress directory
    actress_path = Path(base_directory) / studio_folder / actress_name
    
    # Build new name: [Code]-[Title]
    safe_title = sanitize_filename(metadata['title'])
    new_name = f"[{metadata['code']}]-[{safe_title}]"
    
    if is_folder:
        new_path = actress_path / new_name
    else:
        ext = Path(item_path).suffix
        new_path = actress_path / f"{new_name}{ext}"
    
    # Handle duplicates
    if new_path.exists():
        counter = 1
        original_new_path = new_path
        while new_path.exists():
            if is_folder:
                new_path = original_new_path.parent / f"{original_new_path.name}_{counter}"
            else:
                stem = original_new_path.stem
                ext = original_new_path.suffix
                new_path = original_new_path.parent / f"{stem}_{counter}{ext}"
            counter += 1
    
    if dry_run:
        print(f"  [DRY RUN] Would move to: {new_path}")
        if metadata.get('poster_url'):
            print(f"  [DRY RUN] Would download poster")
        return (True, str(new_path), False)
    
    try:
        # Create directory
        actress_path.mkdir(parents=True, exist_ok=True)
        
        # Move item
        shutil.move(str(item_path), str(new_path))
        
        # Download poster
        poster_downloaded = False
        if metadata.get('poster_url'):
            time.sleep(0.5)  # Rate limiting
            poster_downloaded = download_poster(
                metadata['poster_url'],
                actress_path,
                metadata['code']
            )
            if poster_downloaded:
                print(f"  OK Downloaded poster")
        
        return (True, str(new_path), poster_downloaded)
    except Exception as e:
        return (False, str(e), False)


def handle_failed_item(item_path, base_directory, reason, dry_run=False):
    """Move failed items to /others"""
    others_path = Path(base_directory) / 'others'
    item_name = os.path.basename(item_path)
    new_path = others_path / item_name
    
    # Handle duplicates
    if new_path.exists():
        counter = 1
        base_name, ext = os.path.splitext(item_name)
        while new_path.exists():
            new_name = f"{base_name}_{counter}{ext if ext else ''}"
            new_path = others_path / new_name
            counter += 1
    
    if dry_run:
        print(f"  [DRY RUN] Would move to /others: {item_name}")
        return
    
    try:
        others_path.mkdir(exist_ok=True)
        shutil.move(str(item_path), str(new_path))
        print(f"  Moved to /others: {item_name} (reason: {reason})")
    except Exception as e:
        print(f"  Error: {e}")


def organize_av_directory(directory, dry_run=False, retry_failed=False, first_only=False):
    """Main organization workflow"""
    print(f"Scanning directory: {directory}")
    if retry_failed:
        print("Mode: Retry failed items")
    if first_only:
        print("Mode: First item only")
    
    items = scan_directory(directory, retry_failed, first_only)
    print(f"Found {len(items)} items\n")
    
    if not items:
        print("No items to process.")
        return
    
    success_count = 0
    failed_count = 0
    poster_count = 0
    javbus_count = 0
    
    for item_path, is_folder in items:
        item_name = os.path.basename(item_path)
        item_type = "Folder" if is_folder else "File"
        
        print(f"\n{'='*60}")
        print(f"{item_type}: {item_name}")
        print('='*60)
        
        # Extract code
        print("Extracting code...")
        code = extract_code(item_name)
        
        if not code:
            print("  X Code not found")
            failed_count += 1
            handle_failed_item(item_path, directory, 'code_not_found', dry_run)
            continue
        
        print(f"  OK Code: {code}")
        
        # Fetch metadata
        metadata = fetch_metadata(code)
        
        print(f"  OK Studio: {metadata['studio']}")
        print(f"  OK Title: {metadata['title']}")
        
        if metadata.get('actresses'):
            print(f"  OK Actress: {metadata['actresses'][0]}")
            if len(metadata['actresses']) > 1:
                print(f"    (+ {len(metadata['actresses'])-1} more)")
        else:
            print(f"  OK Actress: Unknown")
        
        if metadata.get('source') == 'javbus':
            javbus_count += 1
        
        # Organize
        print("Organizing...")
        success, result, poster_downloaded = organize_item(
            item_path, is_folder, metadata, directory, dry_run
        )
        
        if success:
            print(f"  OK Moved to: {result}")
            success_count += 1
            if poster_downloaded:
                poster_count += 1
        else:
            print(f"  X Error: {result}")
            failed_count += 1
            handle_failed_item(item_path, directory, 'move_error', dry_run)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Total items: {len(items)}")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Data from javbus: {javbus_count}")
    print(f"Posters downloaded: {poster_count}")
    
    if dry_run:
        print("\n[DRY RUN] No actual changes were made")


def main():
    if len(sys.argv) < 2:
        print("Usage: python hybrid_organizer.py <directory> [--dry-run] [--retry-failed] [--first-only]")
        sys.exit(1)
    
    directory = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    retry_failed = '--retry-failed' in sys.argv
    first_only = '--first-only' in sys.argv
    
    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    
    organize_av_directory(directory, dry_run, retry_failed, first_only)


if __name__ == "__main__":
    main()
