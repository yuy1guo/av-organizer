---
name: av-organizer
description: Organize AV video collection by automatically extracting codes from filenames, fetching metadata from javbus.com, and reorganizing files into studio-based folder structure with standardized naming. Use when user needs to organize, rename, or categorize AV/JAV video files based on studio/code/title metadata.
---

# AV Organizer

Automatically organize AV video collections by extracting codes, fetching metadata from javbus.com, and reorganizing into a clean folder structure.

## Overview

This skill organizes AV videos by:
1. Scanning a directory for video files (both standalone and in folders)
2. Extracting AV codes from filenames (e.g., SSIS-001, IPX-123)
3. Fetching metadata from javbus.com (studio, title, actresses)
4. Creating studio-based folder structure
5. Renaming files to `[Code]-[Title]` format
6. Moving files to appropriate studio folders

## Workflow

### Step 1: Scan Directory

Identify all video files in the target directory:

```python
import os
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.wmv', '.flv', '.mov', '.m4v', '.rmvb'}

def scan_directory(directory):
    """
    Scan for video files (both standalone and in folders)
    
    Returns:
        List of tuples: (file_path, is_in_folder, folder_path_if_applicable)
    """
    results = []
    
    for item in Path(directory).iterdir():
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            # Standalone video file
            results.append((str(item), False, None))
        
        elif item.is_dir():
            # Check if folder contains video files
            video_files = [
                f for f in item.rglob('*') 
                if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
            ]
            if video_files:
                # Folder with videos
                results.append((str(item), True, str(item)))
    
    return results
```

### Step 2: Extract Code and Fetch Metadata

Use bundled scripts to extract code and fetch metadata:

```python
import subprocess
import json

def process_item(item_path, is_folder):
    """
    Extract code and fetch metadata
    
    Returns:
        dict: {
            'code': str,
            'studio': str,
            'title': str,
            'actresses': list,
            'success': bool
        }
    """
    # Determine filename to extract code from
    if is_folder:
        filename = os.path.basename(item_path)
    else:
        filename = os.path.basename(item_path)
    
    # Extract code using script
    result = subprocess.run(
        ['python', 'scripts/extract_code.py', filename],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {'success': False, 'reason': 'code_not_found'}
    
    code = result.stdout.strip()
    
    # Fetch metadata using script
    result = subprocess.run(
        ['python', 'scripts/javbus_scraper.py', code],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return {'success': False, 'reason': 'metadata_not_found', 'code': code}
    
    metadata = json.loads(result.stdout)
    
    return {
        'success': True,
        'code': code,
        'studio': metadata['studio'],
        'title': metadata['title'],
        'actresses': metadata['actresses']
    }
```

### Step 3: Normalize Studio Name

Use bundled script to normalize studio name to folder name:

```python
def get_studio_folder(studio_name):
    """Get normalized studio folder name"""
    result = subprocess.run(
        ['python', 'scripts/normalize_studio.py', studio_name],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

### Step 4: Rename and Move

```python
import shutil

def organize_item(item_path, is_folder, metadata, base_directory):
    """
    Rename and move item to studio folder
    
    Args:
        item_path: Original path
        is_folder: Whether item is a folder
        metadata: Metadata dict from Step 2
        base_directory: Root directory (e.g., E:\\迅雷下载)
    """
    # Get studio folder name
    studio_folder = get_studio_folder(metadata['studio'])
    
    # Create studio directory if needed
    studio_path = Path(base_directory) / studio_folder
    studio_path.mkdir(exist_ok=True)
    
    # Build new name: [Code]-[Title]
    # Sanitize title for filesystem
    safe_title = sanitize_filename(metadata['title'])
    new_name = f"[{metadata['code']}]-[{safe_title}]"
    
    if is_folder:
        # Move entire folder
        new_path = studio_path / new_name
        shutil.move(item_path, new_path)
    else:
        # Move single file, preserve extension
        ext = Path(item_path).suffix
        new_path = studio_path / f"{new_name}{ext}"
        shutil.move(item_path, new_path)
    
    return new_path


def sanitize_filename(filename):
    """Remove invalid filesystem characters"""
    import re
    # Remove invalid Windows filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    # Limit length
    return sanitized[:200]
```

### Step 5: Handle Failures

Items that fail code extraction or metadata fetch go to `/others`:

```python
def handle_failed_item(item_path, is_folder, base_directory, reason):
    """Move failed items to /others folder"""
    others_path = Path(base_directory) / 'others'
    others_path.mkdir(exist_ok=True)
    
    # Keep original name
    item_name = os.path.basename(item_path)
    new_path = others_path / item_name
    
    shutil.move(item_path, new_path)
    
    print(f"Moved to /others: {item_name} (reason: {reason})")
```

## Complete Workflow Example

```python
def organize_av_directory(directory):
    """
    Complete workflow to organize AV directory
    
    Args:
        directory: Target directory (e.g., E:\\迅雷下载)
    """
    print(f"Scanning directory: {directory}")
    items = scan_directory(directory)
    print(f"Found {len(items)} items")
    
    for item_path, is_folder, _ in items:
        print(f"\nProcessing: {os.path.basename(item_path)}")
        
        # Extract and fetch metadata
        metadata = process_item(item_path, is_folder)
        
        if not metadata['success']:
            # Failed - move to /others
            handle_failed_item(
                item_path, 
                is_folder, 
                directory, 
                metadata.get('reason', 'unknown')
            )
            continue
        
        # Success - organize
        try:
            new_path = organize_item(item_path, is_folder, metadata, directory)
            print(f"✓ Moved to: {new_path}")
        except Exception as e:
            print(f"✗ Error: {e}")
            handle_failed_item(item_path, is_folder, directory, 'move_error')

# Usage
organize_av_directory('E:\\迅雷下载')
```

## Quick Start (Simplified Version)

For Python 2.7 compatibility, use the simplified all-in-one script:

```bash
python scripts/simple_organizer.py "E:\\迅雷下载" --dry-run --first-only
```

Options:
- `--dry-run`: Preview changes without modifying files
- `--first-only`: Test on first item only

Once verified, remove flags to process all items:

```bash
python scripts/simple_organizer.py "E:\\迅雷下载"
```

**Note**: The simplified version uses built-in studio mappings based on code prefixes (e.g., SSIS → S1, IPX → IdeaPocket). For real-time javbus.com scraping, use Python 3.6+ with the full workflow below.

## Bundled Scripts

### scripts/simple_organizer.py (Recommended)
All-in-one script compatible with Python 2.7+. Uses built-in studio mappings.

Usage: `python scripts/simple_organizer.py <directory> [--dry-run] [--first-only]`

### scripts/extract_code.py (Python 3)
Extracts AV code from filename. Handles formats like:
- `SSIS-001`
- `IPX 123` (with space)
- `MIDV456` (no separator)

Usage: `python scripts/extract_code.py <filename>`

### scripts/javbus_scraper.py (Python 3)
Fetches metadata from javbus.com given a code.

Usage: `python scripts/javbus_scraper.py <code>`

Returns JSON: `{"studio": "...", "title": "...", "actresses": [...]}`

### scripts/normalize_studio.py (Python 3)
Normalizes studio name to consistent folder name.

Usage: `python scripts/normalize_studio.py <studio_name>`

Handles common variations (e.g., "S1 No.1 Style" → "s1")

### scripts/organize.py (Python 3)
Full workflow with real-time javbus.com scraping. Requires Python 3.6+.

Usage: `python scripts/organize.py <directory> [--dry-run] [--first-only]`

## Edge Cases

- **Multiple codes in filename**: Extracts first match
- **No code found**: Move to `/others`
- **Javbus fetch fails**: Move to `/others`
- **Duplicate filenames**: Append suffix `_1`, `_2`, etc.
- **Very long titles**: Truncate to 200 characters

## Testing

Before processing entire directory, test on a single file:

```python
# Test code extraction
test_file = "SSIS-001.mp4"
result = subprocess.run(['python', 'scripts/extract_code.py', test_file], capture_output=True, text=True)
print(f"Extracted code: {result.stdout.strip()}")

# Test metadata fetch
result = subprocess.run(['python', 'scripts/javbus_scraper.py', 'SSIS-001'], capture_output=True, text=True)
print(f"Metadata: {result.stdout}")

# Test studio normalization
result = subprocess.run(['python', 'scripts/normalize_studio.py', 'S1 No.1 Style'], capture_output=True, text=True)
print(f"Studio folder: {result.stdout.strip()}")
```
