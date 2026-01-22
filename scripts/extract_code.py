#!/usr/bin/env python3
"""
AV Code Extractor - Extract AV codes from filenames

Usage:
    python extract_code.py <filename>

Returns the extracted code or empty string if not found
"""

import sys
import re


def extract_av_code(filename):
    """
    Extract AV code from filename
    
    Common patterns:
    - SSIS-001
    - IPX-123
    - MIDV-456
    - ABP-789
    - etc.
    
    Args:
        filename: Full filename or path
    
    Returns:
        Extracted code (uppercase) or None
    """
    # Remove file extension and path
    name = filename.upper()
    
    # Pattern: Letters + hyphen/space + numbers
    # Examples: SSIS-001, IPX 123, MIDV-456
    patterns = [
        r'([A-Z]{2,6}[-\s]\d{3,5})',  # Standard: ABC-123 or ABC 123
        r'([A-Z]{2,6}\d{3,5})',       # No separator: ABC123
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


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_code.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    code = extract_av_code(filename)
    
    if code:
        print(code)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
