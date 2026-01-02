#!/usr/bin/env python3
"""
Debug EBCDIC parsing to determine if issues are translation or alignment.
"""

import sys
sys.path.insert(0, '/app')

def analyze_ebcdic_bytes(byte_sequence: bytes, field_name: str = "unknown"):
    """Analyze EBCDIC bytes to see what they decode to."""
    print(f"\n{'='*60}")
    print(f"Field: {field_name}")
    print(f"Raw bytes (hex): {byte_sequence.hex()}")
    print(f"Raw bytes (decimal): {[b for b in byte_sequence]}")
    
    # Try different decodings
    try:
        cp037_decoded = byte_sequence.decode('cp037', errors='replace')
        print(f"cp037 (US/Canada): {repr(cp037_decoded)}")
    except Exception as e:
        print(f"cp037 decode failed: {e}")
    
    try:
        cp1047_decoded = byte_sequence.decode('cp1047', errors='replace')
        print(f"cp1047 (Western Europe): {repr(cp1047_decoded)}")
    except Exception as e:
        print(f"cp1047 decode failed: {e}")
    
    # Check for EBCDIC digit patterns
    ebcdic_digits = [b for b in byte_sequence if 0xF0 <= b <= 0xF9]
    ebcdic_space = [b for b in byte_sequence if b == 0x40]
    ebcdic_at = [b for b in byte_sequence if b == 0x7C]  # @ in some contexts
    
    print(f"EBCDIC digits (0xF0-0xF9): {len(ebcdic_digits)}/{len(byte_sequence)}")
    print(f"EBCDIC spaces (0x40): {len(ebcdic_space)}/{len(byte_sequence)}")
    print(f"Byte 0x7C (might be @ or |): {len(ebcdic_at)}/{len(byte_sequence)}")
    
    # Check if it looks like ASCII mis-decoded
    ascii_printable = [b for b in byte_sequence if 0x20 <= b <= 0x7E]
    print(f"ASCII printable (0x20-0x7E): {len(ascii_printable)}/{len(byte_sequence)}")
    
    # Check for common EBCDIC patterns
    if len(ebcdic_digits) > len(byte_sequence) * 0.5:
        print("✅ Looks like EBCDIC numeric field")
    elif len(ascii_printable) > len(byte_sequence) * 0.8:
        print("⚠️ Looks like ASCII (might be wrong encoding)")
    else:
        print("❓ Unclear encoding pattern")

if __name__ == "__main__":
    print("EBCDIC Parsing Debug Tool")
    print("="*60)
    
    # Test some common EBCDIC byte patterns
    print("\n1. EBCDIC digit '0' (should be 0xF0):")
    analyze_ebcdic_bytes(bytes([0xF0]), "EBCDIC_0")
    
    print("\n2. EBCDIC digit '5' (should be 0xF5):")
    analyze_ebcdic_bytes(bytes([0xF5]), "EBCDIC_5")
    
    print("\n3. EBCDIC space (should be 0x40):")
    analyze_ebcdic_bytes(bytes([0x40]), "EBCDIC_SPACE")
    
    print("\n4. Byte 0x7C (what does this decode to?):")
    analyze_ebcdic_bytes(bytes([0x7C]), "BYTE_0x7C")
    
    print("\n5. EBCDIC '123' (0xF1 0xF2 0xF3):")
    analyze_ebcdic_bytes(bytes([0xF1, 0xF2, 0xF3]), "EBCDIC_123")
    
    print("\n6. Mixed: space + digits (0x40 0xF1 0xF2 0xF3):")
    analyze_ebcdic_bytes(bytes([0x40, 0xF1, 0xF2, 0xF3]), "EBCDIC_SPACE_123")
    
    print("\n" + "="*60)
    print("\nTo debug a specific field from the balances file:")
    print("1. Get the raw bytes from the file")
    print("2. Call analyze_ebcdic_bytes(bytes, 'field_name')")
    print("3. Check which code page produces correct results")










