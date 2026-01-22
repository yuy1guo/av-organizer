#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 AV 整理脚本 - 支持真实片名、女优文件夹、海报下载

新功能:
1. 从 javbus.com 抓取真实片名
2. 按女优名创建二级文件夹（取第一个女优）
3. 下载海报到对应文件夹
4. 重新处理 others/unknown 文件夹

使用方法:
    python enhanced_organizer.py <directory> [--dry-run] [--retry-failed]
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


def extract_code(filename):
    """Extract AV code from filename using script"""
    try:
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'extract_code.py'), filename],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"  Error extracting code: {e}")
        return None


def fetch_metadata_enhanced(code):
    """Fetch metadata from javbus using enhanced script"""
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
            # Add code to metadata
            data['code'] = code
            return data
        return None
    except Exception as e:
        print(f"  Error fetching metadata: {e}")
        return None


def normalize_studio(studio_name):
    """Normalize studio name using script"""
    try:
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'normalize_studio.py'), studio_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=5
        )
        
        return result.stdout.strip()
    except Exception as e:
        print(f"  Error normalizing studio: {e}")
        return 'others'


def sanitize_filename(filename):
    """Remove invalid filesystem characters"""
    # Remove invalid Windows filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    # Remove extra whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    # Limit length
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
        
        # Determine image extension
        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        else:
            ext = '.jpg'  # Default
        
        # Save poster
        poster_filename = f"[{code}]-poster{ext}"
        poster_path = Path(target_path) / poster_filename
        
        with open(poster_path, 'wb') as f:
            f.write(image_data)
        
        return True
    except Exception as e:
        print(f"  Warning: Failed to download poster: {e}")
        return False


def scan_directory(directory, retry_failed=False):
    """
    Scan for video files (both standalone and in folders)
    
    Args:
        directory: Target directory
        retry_failed: If True, only process others/ and unknown/ folders
    
    Returns:
        List of tuples: (item_path, is_folder)
    """
    results = []
    
    for item in Path(directory).iterdir():
        # Skip studio folders unless retry_failed
        if item.is_dir() and not retry_failed:
            # Check if it's a studio folder or special folder
            if item.name in ['others', 'unknown']:
                # Process contents of these folders
                for subitem in item.iterdir():
                    if subitem.is_file() and subitem.suffix.lower() in VIDEO_EXTENSIONS:
                        results.append((str(subitem), False))
                    elif subitem.is_dir():
                        # Check if folder contains videos
                        video_files = [f for f in subitem.rglob('*') 
                                     if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
                        if video_files:
                            results.append((str(subitem), True))
            else:
                # Check if folder contains video files (not already organized)
                video_files = [
                    f for f in item.rglob('*') 
                    if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
                ]
                if video_files:
                    results.append((str(item), True))
        
        elif item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            # Standalone video file
            results.append((str(item), False))
    
    # If retry_failed, only process items from others/unknown
    if retry_failed:
        results = [(path, is_folder) for path, is_folder in results 
                  if 'others' in path or 'unknown' in path]
    
    return results


def organize_item_enhanced(item_path, is_folder, metadata, base_directory, dry_run=False):
    """
    Rename and move item with actress subfolder and poster download
    
    Returns:
        (success, new_path_or_error, poster_downloaded)
    """
    # Get studio folder name
    studio_folder = normalize_studio(metadata['studio'])
    
    # Get actress name (first actress or "Unknown")
    actress_name = 'Unknown'
    if metadata.get('actresses') and len(metadata['actresses']) > 0:
        actress_name = sanitize_filename(metadata['actresses'][0])
    
    # Create studio/actress directory path
    actress_path = Path(base_directory) / studio_folder / actress_name
    
    # Build new name: [Code]-[Title]
    safe_title = sanitize_filename(metadata['title'])
    new_name = f"[{metadata['code']}]-[{safe_title}]"
    
    if is_folder:
        # Move entire folder
        new_path = actress_path / new_name
    else:
        # Move single file, preserve extension
        ext = Path(item_path).suffix
        new_path = actress_path / f"{new_name}{ext}"
    
    # Handle duplicate names
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
        print(f"  [DRY RUN] Would download poster for: {metadata['code']}")
        return (True, str(new_path), False)
    
    try:
        # Create actress directory
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
                print(f"  ✓ Downloaded poster")
        
        return (True, str(new_path), poster_downloaded)
    except Exception as e:
        return (False, str(e), False)


def handle_failed_item(item_path, is_folder, base_directory, reason, dry_run=False):
    """Move failed items to /others folder"""
    others_path = Path(base_directory) / 'others'
    
    # Keep original name
    item_name = os.path.basename(item_path)
    new_path = others_path / item_name
    
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
        print(f"  [DRY RUN] Would move to /others: {item_name} (reason: {reason})")
        return
    
    try:
        others_path.mkdir(exist_ok=True)
        shutil.move(str(item_path), str(new_path))
        print(f"  Moved to /others: {item_name} (reason: {reason})")
    except Exception as e:
        print(f"  Error moving to /others: {e}")


def organize_av_directory_enhanced(directory, dry_run=False, retry_failed=False):
    """
    Complete workflow to organize AV directory with enhancements
    """
    print(f"Scanning directory: {directory}")
    if retry_failed:
        print("Mode: Retry failed items from /others and /unknown")
    
    items = scan_directory(directory, retry_failed)
    print(f"Found {len(items)} items\n")
    
    if len(items) == 0:
        print("No items to process.")
        return
    
    success_count = 0
    failed_count = 0
    poster_count = 0
    
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
            print("  ✗ Code not found")
            failed_count += 1
            handle_failed_item(item_path, is_folder, directory, 'code_not_found', dry_run)
            continue
        
        print(f"  ✓ Code: {code}")
        
        # Fetch metadata
        print("Fetching metadata from javbus.com...")
        metadata = fetch_metadata_enhanced(code)
        
        if not metadata:
            print("  ✗ Metadata not found on javbus.com")
            failed_count += 1
            handle_failed_item(item_path, is_folder, directory, 'metadata_not_found', dry_run)
            continue
        
        print(f"  ✓ Studio: {metadata['studio']}")
        print(f"  ✓ Title: {metadata['title']}")
        if metadata.get('actresses'):
            print(f"  ✓ Actress: {metadata['actresses'][0]} (+ {len(metadata['actresses'])-1} more)")
        else:
            print(f"  ✓ Actress: Unknown")
        
        # Organize
        print("Organizing...")
        success, result, poster_downloaded = organize_item_enhanced(
            item_path, is_folder, metadata, directory, dry_run
        )
        
        if success:
            print(f"  ✓ Moved to: {result}")
            success_count += 1
            if poster_downloaded:
                poster_count += 1
        else:
            print(f"  ✗ Error: {result}")
            failed_count += 1
            handle_failed_item(item_path, is_folder, directory, 'move_error', dry_run)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"Total items: {len(items)}")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Posters downloaded: {poster_count}")
    
    if dry_run:
        print("\n[DRY RUN] No actual changes were made")


def main():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_organizer.py <directory> [--dry-run] [--retry-failed]")
        sys.exit(1)
    
    directory = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    retry_failed = '--retry-failed' in sys.argv
    
    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    
    organize_av_directory_enhanced(directory, dry_run, retry_failed)


if __name__ == "__main__":
    main()
