#!/usr/bin/env python3
"""
AV Organizer - Complete workflow to organize AV directory

Usage:
    python organize.py <directory> [--dry-run] [--first-only]

Options:
    --dry-run: Show what would be done without making changes
    --first-only: Process only the first item (for testing)
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
import re

# Video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb'}

# Get script directory
SCRIPT_DIR = Path(__file__).parent


def scan_directory(directory):
    """
    Scan for video files (both standalone and in folders)
    
    Returns:
        List of tuples: (item_path, is_folder)
    """
    results = []
    
    for item in Path(directory).iterdir():
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            # Standalone video file
            results.append((str(item), False))
        
        elif item.is_dir():
            # Check if folder contains video files
            video_files = [
                f for f in item.rglob('*') 
                if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
            ]
            if video_files:
                # Folder with videos
                results.append((str(item), True))
    
    return results


def extract_code(filename):
    """Extract AV code from filename using script"""
    try:
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'extract_code.py'), filename],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"  Error extracting code: {e}")
        return None


def fetch_metadata(code):
    """Fetch metadata from javbus using script"""
    try:
        result = subprocess.run(
            ['python', str(SCRIPT_DIR / 'javbus_scraper.py'), code],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
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
            encoding='utf-8'
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


def organize_item(item_path, is_folder, metadata, base_directory, dry_run=False):
    """
    Rename and move item to studio folder
    
    Returns:
        (success, new_path_or_error)
    """
    # Get studio folder name
    studio_folder = normalize_studio(metadata['studio'])
    
    # Create studio directory path
    studio_path = Path(base_directory) / studio_folder
    
    # Build new name: [Code]-[Title]
    safe_title = sanitize_filename(metadata['title'])
    new_name = f"[{metadata['code']}]-[{safe_title}]"
    
    if is_folder:
        # Move entire folder
        new_path = studio_path / new_name
    else:
        # Move single file, preserve extension
        ext = Path(item_path).suffix
        new_path = studio_path / f"{new_name}{ext}"
    
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
        return (True, str(new_path))
    
    try:
        # Create studio directory
        studio_path.mkdir(exist_ok=True)
        
        # Move item
        shutil.move(str(item_path), str(new_path))
        
        return (True, str(new_path))
    except Exception as e:
        return (False, str(e))


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


def organize_av_directory(directory, dry_run=False, first_only=False):
    """
    Complete workflow to organize AV directory
    """
    print(f"Scanning directory: {directory}")
    items = scan_directory(directory)
    print(f"Found {len(items)} items\n")
    
    if first_only and items:
        items = items[:1]
        print("Processing first item only (test mode)\n")
    
    success_count = 0
    failed_count = 0
    
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
        metadata = fetch_metadata(code)
        
        if not metadata:
            print("  ✗ Metadata not found on javbus.com")
            failed_count += 1
            handle_failed_item(item_path, is_folder, directory, 'metadata_not_found', dry_run)
            continue
        
        print(f"  ✓ Studio: {metadata['studio']}")
        print(f"  ✓ Title: {metadata['title']}")
        if metadata['actresses']:
            print(f"  ✓ Actresses: {', '.join(metadata['actresses'][:3])}")
        
        # Organize
        print("Organizing...")
        success, result = organize_item(item_path, is_folder, metadata, directory, dry_run)
        
        if success:
            print(f"  ✓ Moved to: {result}")
            success_count += 1
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
    
    if dry_run:
        print("\n[DRY RUN] No actual changes were made")


def main():
    if len(sys.argv) < 2:
        print("Usage: python organize.py <directory> [--dry-run] [--first-only]")
        sys.exit(1)
    
    directory = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    first_only = '--first-only' in sys.argv
    
    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)
    
    organize_av_directory(directory, dry_run, first_only)


if __name__ == "__main__":
    main()
