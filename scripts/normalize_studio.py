#!/usr/bin/env python3
"""
Studio Name Normalizer - Normalize studio names to folder names

Usage:
    python normalize_studio.py <studio_name>

Returns normalized folder name
"""

import sys
import re


# Studio name mappings (original -> normalized folder name)
STUDIO_MAPPINGS = {
    # S1 variations
    's1': 's1',
    's1 no.1 style': 's1',
    's1 no. 1 style': 's1',
    
    # IdeaPocket variations
    'ideapocket': 'ideapocket',
    'idea pocket': 'ideapocket',
    
    # MOODYZ variations
    'moodyz': 'moodyz',
    'moody\'s': 'moodyz',
    
    # Prestige variations
    'prestige': 'prestige',
    
    # E-Body variations
    'e-body': 'e-body',
    'ebody': 'e-body',
    
    # FALENO variations
    'faleno': 'faleno',
    'faleno star': 'faleno',
    
    # Attackers variations
    'attackers': 'attackers',
    
    # KM Produce variations
    'km produce': 'km-produce',
    'kmproduce': 'km-produce',
    
    # Madonna variations
    'madonna': 'madonna',
    
    # Premium variations
    'premium': 'premium',
    
    # kawaii variations
    'kawaii': 'kawaii',
    'kawaii*': 'kawaii',
    
    # Add more as needed
}


def normalize_studio(studio_name):
    """
    Normalize studio name to folder name
    
    Args:
        studio_name: Original studio name from javbus
    
    Returns:
        Normalized folder name (lowercase, hyphenated)
    """
    if not studio_name:
        return 'others'
    
    # Lowercase and clean
    cleaned = studio_name.lower().strip()
    
    # Check mappings
    if cleaned in STUDIO_MAPPINGS:
        return STUDIO_MAPPINGS[cleaned]
    
    # Default: lowercase, replace spaces with hyphens
    normalized = re.sub(r'[^\w\s-]', '', cleaned)  # Remove special chars
    normalized = re.sub(r'[\s]+', '-', normalized)  # Spaces to hyphens
    normalized = re.sub(r'-+', '-', normalized)     # Multiple hyphens to one
    
    return normalized or 'others'


def main():
    if len(sys.argv) != 2:
        print("Usage: python normalize_studio.py <studio_name>")
        sys.exit(1)
    
    studio_name = sys.argv[1]
    print(normalize_studio(studio_name))


if __name__ == "__main__":
    main()
