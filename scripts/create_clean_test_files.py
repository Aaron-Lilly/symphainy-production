#!/usr/bin/env python3
"""
Create clean test files for scenario3 (annuity data) without header comments.
This creates:
1. A clean binary data file (no header, just records)
2. A corrected copybook (only the data record structure, no metadata tables)
"""

import os
from pathlib import Path

# Output directory
OUTPUT_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/clean_test_files")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Record structure: 20 + 30 + 3 + 10 + 10 + 8 = 81 bytes
RECORD_SIZE = 81

# Sample records (clean data, no header)
SAMPLE_RECORDS = [
    {
        "policy_number": "POL001123456789012345",
        "name": "John Smith                  ",  # 30 chars
        "age": "045",
        "policy_type": "Term Life  ",
        "premium": "0000050000",
        "issue_date": "20240115"
    },
    {
        "policy_number": "POL002234567890123456",
        "name": "Mary Johnson                 ",  # 30 chars
        "age": "032",
        "policy_type": "Whole Life ",
        "premium": "0000075000",
        "issue_date": "20240116"
    },
    {
        "policy_number": "POL003345678901234567",
        "name": "Robert Davis                 ",  # 30 chars
        "age": "028",
        "policy_type": "Universal  ",
        "premium": "0000100000",
        "issue_date": "20240117"
    },
    {
        "policy_number": "POL004456789012345678",
        "name": "Sarah Wilson                 ",  # 30 chars
        "age": "025",
        "policy_type": "Annuity    ",
        "premium": "0000020000",
        "issue_date": "20240118"
    },
    {
        "policy_number": "POL005567890123456789",
        "name": "Michael Brown               ",  # 30 chars
        "age": "055",
        "policy_type": "Term Life  ",
        "premium": "0000030000",
        "issue_date": "20240119"
    },
    {
        "policy_number": "POL006678901234567890",
        "name": "Lisa Anderson               ",  # 30 chars
        "age": "042",
        "policy_type": "Whole Life ",
        "premium": "0000080000",
        "issue_date": "20240120"
    },
    {
        "policy_number": "POL007789012345678901",
        "name": "David Miller                ",  # 30 chars
        "age": "038",
        "policy_type": "Universal  ",
        "premium": "0000120000",
        "issue_date": "20240121"
    },
    {
        "policy_number": "POL008890123456789012",
        "name": "Jennifer Taylor             ",  # 30 chars
        "age": "029",
        "policy_type": "Annuity    ",
        "premium": "0000150000",
        "issue_date": "20240122"
    },
    {
        "policy_number": "POL009901234567890123",
        "name": "Christopher Lee             ",  # 30 chars
        "age": "035",
        "policy_type": "Term Life  ",
        "premium": "0000040000",
        "issue_date": "20240123"
    },
    {
        "policy_number": "POL010012345678901234",
        "name": "Amanda White                ",  # 30 chars
        "age": "031",
        "policy_type": "Whole Life ",
        "premium": "0000090000",
        "issue_date": "20240124"
    }
]

def create_clean_data_file():
    """Create a clean binary data file with just records, no header."""
    output_path = OUTPUT_DIR / "scenario3_annuity_data_clean.bin"
    
    with open(output_path, 'wb') as f:
        for record in SAMPLE_RECORDS:
            # Build record: 20 + 30 + 3 + 10 + 10 + 8 = 81 bytes
            record_bytes = (
                record["policy_number"][:20].ljust(20).encode('utf-8') +
                record["name"][:30].ljust(30).encode('utf-8') +
                record["age"][:3].ljust(3).encode('utf-8') +
                record["policy_type"][:10].ljust(10).encode('utf-8') +
                record["premium"][:10].ljust(10).encode('utf-8') +
                record["issue_date"][:8].ljust(8).encode('utf-8')
            )
            assert len(record_bytes) == RECORD_SIZE, f"Record size mismatch: {len(record_bytes)} != {RECORD_SIZE}"
            f.write(record_bytes)
    
    file_size = output_path.stat().st_size
    expected_size = len(SAMPLE_RECORDS) * RECORD_SIZE
    
    print(f"✅ Created clean data file: {output_path}")
    print(f"   Size: {file_size} bytes")
    print(f"   Records: {len(SAMPLE_RECORDS)}")
    print(f"   Record size: {RECORD_SIZE} bytes")
    print(f"   Expected size: {expected_size} bytes")
    assert file_size == expected_size, f"File size mismatch: {file_size} != {expected_size}"
    
    return output_path

def create_corrected_copybook():
    """Create a corrected copybook with only the data record structure."""
    copybook_content = """      01  POLICYHOLDER-RECORD.
          05  POLICY-NUMBER        PIC X(20).
          05  POLICYHOLDER-NAME    PIC X(30).
          05  POLICYHOLDER-AGE     PIC 9(3).
          05  POLICY-TYPE          PIC X(10).
          05  PREMIUM-AMOUNT       PIC 9(10).
          05  ISSUE-DATE           PIC X(8).
"""
    
    output_path = OUTPUT_DIR / "scenario3_copybook_clean.cpy"
    
    with open(output_path, 'w') as f:
        f.write(copybook_content)
    
    print(f"✅ Created corrected copybook: {output_path}")
    print(f"   Size: {output_path.stat().st_size} bytes")
    print(f"   Structure: Single 01-level record (POLICYHOLDER-RECORD)")
    print(f"   Record size: 81 bytes (20+30+3+10+10+8)")
    
    return output_path

def main():
    print("=" * 60)
    print("Creating Clean Test Files for Scenario 3")
    print("=" * 60)
    print()
    
    data_file = create_clean_data_file()
    copybook_file = create_corrected_copybook()
    
    print()
    print("=" * 60)
    print("✅ Clean test files created successfully!")
    print("=" * 60)
    print()
    print("Files created:")
    print(f"  1. Data file: {data_file}")
    print(f"  2. Copybook: {copybook_file}")
    print()
    print("Next steps:")
    print("  1. Upload these files through the UI")
    print("  2. Or use the upload script to add them to the test tenant")
    print()

if __name__ == "__main__":
    main()












