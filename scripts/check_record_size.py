#!/usr/bin/env python3
"""
Check if records are 81 or 86 bytes by analyzing file structure.
"""

import sys
import re

def check_record_size(file_path):
    """Check record size by analyzing file structure."""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Remove newlines for analysis
    content_no_newlines = content.replace(b'\n', b'').replace(b'\r', b'')
    
    print(f"File size: {len(content)} bytes")
    print(f"File size (no newlines): {len(content_no_newlines)} bytes")
    print()
    
    # Method 1: Check divisibility
    print("Method 1: Check divisibility")
    remainder_81 = len(content_no_newlines) % 81
    remainder_86 = len(content_no_newlines) % 86
    print(f"  Divisible by 81? Remainder: {remainder_81}")
    print(f"  Divisible by 86? Remainder: {remainder_86}")
    if remainder_81 == 0:
        record_count_81 = len(content_no_newlines) // 81
        print(f"  ✓ File is divisible by 81 → {record_count_81} records of 81 bytes")
    if remainder_86 == 0:
        record_count_86 = len(content_no_newlines) // 86
        print(f"  ✓ File is divisible by 86 → {record_count_86} records of 86 bytes")
    print()
    
    # Method 2: Check spacing between POL patterns
    print("Method 2: Check spacing between POL patterns")
    # Find all "POL001", "POL002", etc.
    pattern = rb'POL\d{3}'
    matches = list(re.finditer(pattern, content_no_newlines))
    print(f"  Found {len(matches)} POL patterns")
    
    if len(matches) >= 2:
        spacings = []
        for i in range(1, min(10, len(matches))):
            spacing = matches[i].start() - matches[i-1].start()
            spacings.append(spacing)
            print(f"  POL{i} at byte {matches[i].start()}, spacing from previous: {spacing} bytes")
        
        if len(set(spacings)) == 1:
            spacing = spacings[0]
            print(f"  ✓ Consistent spacing: {spacing} bytes")
            if spacing == 81:
                print(f"    → Records are 81 bytes (no prefix)")
            elif spacing == 86:
                print(f"    → Records are 86 bytes (5-byte prefix)")
            else:
                print(f"    → Records are {spacing} bytes (unexpected size)")
    print()
    
    # Method 3: Check first record structure
    print("Method 3: Check first record structure")
    if len(content_no_newlines) >= 86:
        first_86 = content_no_newlines[:86]
        first_81 = content_no_newlines[:81]
        
        first_86_text = first_86.decode('ascii', errors='ignore')
        first_81_text = first_81.decode('ascii', errors='ignore')
        
        print(f"  First 86 bytes: '{first_86_text[:50]}...'")
        print(f"  First 81 bytes: '{first_81_text[:50]}...'")
        
        if first_86_text.startswith('POL00'):
            print(f"  ✓ Starts with 'POL00' → Likely 86-byte records with 5-byte prefix")
        elif first_81_text.startswith('POL00'):
            print(f"  ✓ Starts with 'POL00' → Likely 81-byte records (POL00 is part of field)")
        elif first_86_text.startswith('POL001'):
            print(f"  ✓ Starts with 'POL001' → Likely 86-byte records")
        elif first_81_text.startswith('POL001'):
            print(f"  ✓ Starts with 'POL001' → Likely 81-byte records")
        else:
            print(f"  ⚠️ Doesn't start with POL pattern")
    
    print()
    print("Conclusion:")
    if remainder_81 == 0 and len(matches) >= 2 and spacings[0] == 81:
        print("  → Records are 81 bytes (no prefix to strip)")
    elif remainder_86 == 0 and len(matches) >= 2 and spacings[0] == 86:
        print("  → Records are 86 bytes (5-byte prefix to strip)")
    else:
        print("  → Unable to determine conclusively - check logs for spacing detection")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_record_size.py <file_path>")
        sys.exit(1)
    
    check_record_size(sys.argv[1])











