#!/usr/bin/env python3
"""
Create a new ASCII test file that properly matches the copybook.
This file has 30-byte POLICYHOLDER-NAME fields (matching copybook) and no prefixes.
"""

from pathlib import Path

# Copybook structure:
# POLICY-NUMBER: PIC X(20) = 20 bytes
# POLICYHOLDER-NAME: PIC X(30) = 30 bytes
# POLICYHOLDER-AGE: PIC 9(3) = 3 bytes
# POLICY-TYPE: PIC X(10) = 10 bytes
# PREMIUM-AMOUNT: PIC 9(10) = 10 bytes
# ISSUE-DATE: PIC X(8) = 8 bytes
# Total: 81 bytes per record

# Helper function to create 30-byte name field
def make_name_field(name: str) -> bytes:
    """Create a 30-byte name field, padded with spaces."""
    name_bytes = name.encode('ascii')
    if len(name_bytes) > 30:
        name_bytes = name_bytes[:30]  # Truncate if too long
    # Pad to exactly 30 bytes with spaces
    return name_bytes + b" " * (30 - len(name_bytes))

# Helper function to create 10-byte policy type field
def make_policy_type_field(policy_type: str) -> bytes:
    """Create a 10-byte policy type field, padded with spaces."""
    type_bytes = policy_type.encode('ascii')
    if len(type_bytes) > 10:
        type_bytes = type_bytes[:10]  # Truncate if too long
    # Pad to exactly 10 bytes with spaces
    return type_bytes + b" " * (10 - len(type_bytes))

# Helper function to create 20-byte policy number field
def make_policy_number(prefix: str, number: int) -> bytes:
    """Create a 20-byte policy number field."""
    policy_str = f"{prefix}{number:03d}"  # e.g., "POL001" = 6 bytes
    # Pad to exactly 20 bytes with digits
    remaining = 20 - len(policy_str)
    if remaining > 0:
        policy_str += "0" * remaining  # Pad with zeros
    return policy_str.encode('ascii')[:20]  # Ensure exactly 20 bytes

# Create records with proper field lengths matching copybook
# Each record: POLICY-NUMBER (20) + POLICYHOLDER-NAME (30) + AGE (3) + TYPE (10) + PREMIUM (10) + DATE (8) = 81 bytes
records = [
    make_policy_number("POL", 1) + make_name_field("John Smith") + b"045" + make_policy_type_field("Term Life") + b"0000050000" + b"20240115",
    make_policy_number("POL", 2) + make_name_field("Mary Johnson") + b"032" + make_policy_type_field("Whole Life") + b"0000075000" + b"20240116",
    make_policy_number("POL", 3) + make_name_field("Robert Davis") + b"028" + make_policy_type_field("Universal") + b"0000100000" + b"20240117",
    make_policy_number("POL", 4) + make_name_field("Sarah Wilson") + b"025" + make_policy_type_field("Annuity") + b"0000020000" + b"20240118",
    make_policy_number("POL", 5) + make_name_field("Michael Brown") + b"055" + make_policy_type_field("Term Life") + b"0000030000" + b"20240119",
    make_policy_number("POL", 6) + make_name_field("Lisa Anderson") + b"042" + make_policy_type_field("Whole Life") + b"0000080000" + b"20240120",
    make_policy_number("POL", 7) + make_name_field("David Miller") + b"038" + make_policy_type_field("Universal") + b"0000120000" + b"20240121",
    make_policy_number("POL", 8) + make_name_field("Jennifer Taylor") + b"029" + make_policy_type_field("Annuity") + b"0000150000" + b"20240122",
    make_policy_number("POL", 9) + make_name_field("Christopher Lee") + b"035" + make_policy_type_field("Term Life") + b"0000040000" + b"20240123",
    make_policy_number("POL", 10) + make_name_field("Amanda White") + b"031" + make_policy_type_field("Whole Life") + b"0000090000" + b"20240124",
    make_policy_number("POL", 11) + make_name_field("Daniel Garcia") + b"027" + make_policy_type_field("Universal") + b"0000110000" + b"20240125",
    make_policy_number("POL", 12) + make_name_field("Stephanie Hall") + b"033" + make_policy_type_field("Annuity") + b"0000060000" + b"20240126",
    make_policy_number("POL", 13) + make_name_field("Kevin Martinez") + b"041" + make_policy_type_field("Term Life") + b"0000130000" + b"20240127",
    make_policy_number("POL", 14) + make_name_field("Rachel Thompson") + b"026" + make_policy_type_field("Whole Life") + b"0000140000" + b"20240128",
    make_policy_number("POL", 15) + make_name_field("Thomas Anderson") + b"039" + make_policy_type_field("Universal") + b"0000160000" + b"20240129",
]

# Verify each record is exactly 81 bytes
for i, record in enumerate(records):
    if len(record) != 81:
        print(f"ERROR: Record {i+1} is {len(record)} bytes, expected 81 bytes")
        print(f"  Record: {record[:50]}...")
        exit(1)

# Verify POLICYHOLDER-NAME fields are exactly 30 bytes
for i, record in enumerate(records):
    name_field = record[20:50]  # Bytes 20-49 (30 bytes)
    if len(name_field) != 30:
        print(f"ERROR: Record {i+1} POLICYHOLDER-NAME is {len(name_field)} bytes, expected 30 bytes")
        exit(1)
    # Verify it's padded with spaces (not truncated)
    name_text = name_field.decode('ascii', errors='ignore')
    if not name_text.rstrip():  # All spaces
        print(f"ERROR: Record {i+1} POLICYHOLDER-NAME is all spaces")
        exit(1)

# Combine all records
data_content = b"".join(records)

# Create copybook
copybook_content = """      01  POLICYHOLDER-RECORD.
          05  POLICY-NUMBER        PIC X(20).
          05  POLICYHOLDER-NAME    PIC X(30).
          05  POLICYHOLDER-AGE     PIC 9(3).
          05  POLICY-TYPE          PIC X(10).
          05  PREMIUM-AMOUNT       PIC 9(10).
          05  ISSUE-DATE           PIC X(8).
"""

# Write files
output_dir = Path(__file__).parent / "clean_test_files"
output_dir.mkdir(exist_ok=True)

data_file = output_dir / "valid_ascii_test_data.bin"
copybook_file = output_dir / "valid_ascii_test_copybook.cpy"

with open(data_file, 'wb') as f:
    f.write(data_content)

with open(copybook_file, 'w') as f:
    f.write(copybook_content)

print("=" * 60)
print("✅ Created Valid ASCII Test Files")
print("=" * 60)
print(f"\n📄 Data File: {data_file}")
print(f"   Size: {len(data_content)} bytes")
print(f"   Records: {len(records)}")
print(f"   Record size: 81 bytes (matches copybook)")
print(f"   POLICYHOLDER-NAME: 30 bytes per record (matches copybook)")

print(f"\n📄 Copybook File: {copybook_file}")
print(f"   Size: {len(copybook_content)} bytes")
print(f"   Record structure: POLICYHOLDER-RECORD (81 bytes)")

print(f"\n✅ Verification:")
print(f"   - All records are exactly 81 bytes")
print(f"   - All POLICYHOLDER-NAME fields are exactly 30 bytes")
print(f"   - File structure matches copybook specification")
print(f"\n🎯 This file should parse correctly with extensible validation!")
print("=" * 60)

