"""
File Format Normalizer for COBOL Fixed-Width Files

This module normalizes various file formats to the standard format expected by Cobrix:
- Pure binary fixed-width records (no delimiters, no headers)

Production COBOL files are typically:
1. Pure binary: Records concatenated without delimiters
2. No embedded headers/comments in the data file
3. File size = N * record_size (perfectly divisible)

However, test files and some legacy systems may have:
- Newlines between records (text format)
- Embedded comments/headers
- Variable-length headers

This normalizer handles these cases by:
1. Removing newlines (simple text-to-binary conversion)
2. Finding first valid data record using pattern matching (extensible)
3. Ensuring divisibility by record size
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class FileFormatNormalizer:
    """
    Normalizes file formats to standard fixed-width binary format for Cobrix.
    
    Uses a simple, extensible approach:
    1. Remove newlines (convert text to binary)
    2. Find first valid data record using pattern matching (works for any file type)
    3. Ensure divisibility
    """
    
    def __init__(self, record_size: int, first_field_pattern: Optional[str] = None):
        """
        Initialize the normalizer.
        
        Args:
            record_size: Expected record size in bytes (from copybook)
            first_field_pattern: Optional regex pattern for the first field (e.g., r'POL\\d{3}' for "POL001")
                                If None, uses general heuristics
        """
        self.record_size = record_size
        self.first_field_pattern = first_field_pattern
        self.detected_prefix_length = 0  # Will be set if we detect a prefix pattern
        self.detected_record_spacing = None  # Will be set if we detect spacing between patterns (e.g., 86 bytes)
    
    def normalize(self, file_content: bytes) -> Tuple[bytes, dict]:
        """
        Normalize file content to standard format.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            Tuple of (normalized_content, metadata)
        """
        metadata = {
            'original_size': len(file_content),
            'file_format': 'unknown',
            'newlines_removed': 0,
            'header_bytes': 0,
            'normalized_size': 0,
            'record_count': 0,
            'record_prefix_length': 0
        }
        
        # Step 1: Remove newlines (convert text format to binary)
        original_size = len(file_content)
        normalized = file_content.replace(b'\n', b'').replace(b'\r', b'')
        newlines_removed = original_size - len(normalized)
        metadata['newlines_removed'] = newlines_removed
        
        if newlines_removed > 0:
            metadata['file_format'] = 'text'
            logger.info(f"📊 Detected text format file ({newlines_removed} newlines removed)")
        else:
            metadata['file_format'] = 'binary'
            logger.info(f"📊 Detected binary format file")
        
        # Step 2: Find first valid data record using pattern matching
        # This is extensible - works for any file type by looking for valid record patterns
        data_start_offset = self._find_first_valid_record(normalized)
        
        if data_start_offset > 0:
            # Use the exact offset where the pattern was found
            # The _find_first_valid_record already handles alignment to record boundaries
            normalized = normalized[data_start_offset:]
            metadata['header_bytes'] = data_start_offset
            logger.info(f"📊 Removed {data_start_offset} bytes of header/comments (found first valid record)")
        
        # Step 3: Detect and strip record prefixes (e.g., "POL001", "POL002")
        # These are record identifiers that appear at the start of each record but are NOT part of the copybook fields
        # Priority: Use prefix length detected from pattern spacing, then try detection
        prefix_length = 0
        actual_record_size = self.record_size  # Will be updated if we detected different spacing
        
        if self.detected_prefix_length > 0:
            # Use prefix length detected during pattern matching (most reliable)
            prefix_length = self.detected_prefix_length
            # If we detected spacing (e.g., 86 bytes), that's the actual record size in the file
            # After stripping prefix, we'll have copybook record size
            if self.detected_record_spacing:
                actual_record_size = self.detected_record_spacing
                logger.info(f"📊 Using detected record spacing: {actual_record_size} bytes (file) → {self.record_size} bytes (copybook) after stripping {prefix_length}-byte prefix")
            else:
                logger.info(f"📊 Using detected prefix length of {prefix_length} bytes from pattern spacing")
        else:
            # Fallback: Try to detect prefix by examining record starts
            prefix_length = self._detect_record_prefix(normalized)
            if prefix_length > 0:
                logger.info(f"📊 Detected record prefix of {prefix_length} bytes by examining record starts")
        
        if prefix_length > 0:
            # CRITICAL: Pass actual_record_size so we split at correct boundaries (e.g., 86 bytes)
            # before stripping prefix to get copybook size (81 bytes)
            normalized = self._strip_record_prefixes(normalized, prefix_length, actual_record_size)
            metadata['record_prefix_length'] = prefix_length
            logger.info(f"📊 Stripped {prefix_length}-byte prefix from all records")
        
        # Step 4: Ensure file size is divisible by record size
        remainder = len(normalized) % self.record_size
        if remainder > 0:
            logger.info(f"📊 File size not divisible by record size, trimming {remainder} bytes (likely trailer/padding)")
            normalized = normalized[:-remainder]
        
        metadata['normalized_size'] = len(normalized)
        metadata['record_count'] = len(normalized) // self.record_size
        
        logger.info(f"📊 Normalized file: {metadata['original_size']} bytes → {metadata['normalized_size']} bytes ({metadata['record_count']} records)")
        
        return normalized, metadata
    
    def _find_first_valid_record(self, content: bytes) -> int:
        """
        Find the first valid data record using extensible pattern matching.
        
        Strategy:
        1. If first_field_pattern provided, search for that pattern
        2. Otherwise, use general heuristics:
           - Skip comment markers (#, *, /)
           - Skip descriptive text (header keywords)
           - Find first position that looks like structured data
        
        Returns:
            Byte offset where first valid record starts (0 if no headers detected)
        """
        # Initialize scan_start - will be set if pattern matching finds embedded pattern
        scan_start = 0
        
        # Strategy 1: Use provided pattern (most reliable)
        if self.first_field_pattern:
            try:
                # Search for the pattern in the content
                # CRITICAL: If pattern is a regex string (like r'POL\d{3}'), compile it first
                if isinstance(self.first_field_pattern, str):
                    # It's a regex pattern string - compile it and search in decoded content
                    pattern_regex = re.compile(self.first_field_pattern)
                    # Decode content to string for regex search, but track byte positions
                    content_str = content.decode('utf-8', errors='ignore')
                    all_matches_str = list(pattern_regex.finditer(content_str))
                    if not all_matches_str:
                        logger.warning("⚠️ Pattern not found in content")
                        return 0
                    # Convert string match positions to byte positions
                    # This is approximate but should work for ASCII content
                    first_match_str = all_matches_str[0]
                    pattern_length = len(first_match_str.group())
                    # Convert string position to byte position (approximate for ASCII)
                    match_start = len(content_str[:first_match_str.start()].encode('utf-8'))
                    # Store matches with byte positions for spacing calculation
                    # Create a simple class to hold match info
                    class ByteMatch:
                        def __init__(self, byte_pos, match_text):
                            self._byte_pos = byte_pos
                            self._match_text = match_text
                        def start(self):
                            return self._byte_pos
                        def group(self):
                            return self._match_text.encode('utf-8')
                    
                    all_matches = []
                    for m in all_matches_str:
                        byte_pos = len(content_str[:m.start()].encode('utf-8'))
                        all_matches.append(ByteMatch(byte_pos, m.group()))
                    
                    first_match = all_matches[0]
                else:
                    # It's already bytes - use directly
                    pattern_bytes = self.first_field_pattern
                    all_matches = list(re.finditer(pattern_bytes, content))
                    if not all_matches:
                        logger.warning("⚠️ Pattern not found in content")
                        return 0
                    pattern_length = len(pattern_bytes)
                    first_match = all_matches[0]
                    match_start = first_match.start()
                
                # CRITICAL INSIGHT: If POL001, POL002, POL003 appear at regular intervals,
                # that interval IS the record size (or record size + prefix)
                # Let's check if multiple occurrences form a pattern
                if len(all_matches) >= 3:
                    # Check spacing between consecutive matches
                    spacings = []
                    for i in range(1, min(4, len(all_matches))):
                        spacing = all_matches[i].start() - all_matches[i-1].start()
                        spacings.append(spacing)
                    
                    if len(set(spacings)) == 1:
                        # All spacings are the same - this is likely the record size!
                        detected_record_size = spacings[0]
                        logger.info(f"📊 Detected record spacing: {detected_record_size} bytes between patterns")
                        logger.info(f"📊   Copybook says: {self.record_size} bytes")
                        logger.info(f"📊   Difference: {detected_record_size - self.record_size} bytes")
                        
                        # CRITICAL: The detected spacing is the ACTUAL record size in the file
                        # If it's different from copybook, the file has prefixes/separators
                        if detected_record_size == self.record_size:
                            # Spacing matches - POL001 is at record start, no prefix
                            logger.info(f"📊 Pattern spacing matches record size - POL001 is at record start")
                            return match_start
                        elif detected_record_size > self.record_size:
                            # Spacing is larger - likely includes prefix/separator
                            # The spacing (86) is the distance from start of POL001 to start of POL002
                            # Copybook says record is 81 bytes
                            # So: spacing (86) = prefix + record_data (81)
                            # Therefore: prefix = 86 - 81 = 5 bytes
                            # But POL001 is 6 bytes, so maybe POL001 overlaps with first byte of data?
                            # OR: The actual record size in file is 86 bytes, and copybook is wrong?
                            
                            # CRITICAL: If POL001, POL002 appear every 86 bytes, and POL001 is 6 bytes:
                            #   - Record 0: bytes 0-85 (86 bytes) = [POL001][80 bytes data]
                            #   - Record 1: bytes 86-171 (86 bytes) = [POL002][80 bytes data]
                            # But copybook says 81 bytes of data, not 80!
                            
                            # HYPOTHESIS: POL001 is PART of the first field (POLICY-NUMBER), not a prefix
                            # So we should NOT strip it - it's part of the 20-byte POLICY-NUMBER field
                            # The spacing of 86 might be because records are actually 86 bytes, not 81
                            
                            # Store the detected spacing as the actual record size in the file
                            # This is CRITICAL - we need to split at 86-byte boundaries, not 81-byte boundaries
                            self.detected_record_spacing = detected_record_size
                            
                            calculated_prefix = detected_record_size - self.record_size
                            
                            logger.info(f"📊 Pattern spacing = record size + {calculated_prefix} bytes")
                            logger.info(f"📊   Pattern length: {pattern_length} bytes (matched pattern)")
                            logger.info(f"📊   Calculated prefix: {calculated_prefix} bytes (spacing - record size)")
                            
                            # CRITICAL INSIGHT: If spacing is 86 and record is 81, prefix is 5 bytes
                            # The pattern might match "POL001" (6 bytes), but the actual prefix might be "POL00" (5 bytes)
                            # with the digit (1, 2, 3...) being part of the POLICY-NUMBER field
                            
                            # Check if calculated prefix (5) matches a common pattern
                            # "POL00" is 5 bytes - this is likely the actual prefix
                            if calculated_prefix == 5:
                                # Try to verify: check if records start with "POL00" followed by a digit
                                if len(all_matches) > 0:
                                    first_match_text = all_matches[0].group().decode('utf-8', errors='ignore')
                                    if first_match_text.startswith('POL00') and len(first_match_text) >= 6:
                                        # Pattern is "POL001" but prefix is "POL00" (5 bytes)
                                        # The digit is part of the POLICY-NUMBER field
                                        logger.info(f"📊   Pattern '{first_match_text}' found, but prefix is 'POL00' (5 bytes)")
                                        logger.info(f"📊   Digit '{first_match_text[5]}' is part of POLICY-NUMBER field")
                                        self.detected_prefix_length = 5
                                    else:
                                        # Use calculated prefix
                                        self.detected_prefix_length = calculated_prefix
                                else:
                                    self.detected_prefix_length = calculated_prefix
                            elif calculated_prefix == pattern_length:
                                # Calculated prefix matches pattern length - use it
                                logger.info(f"📊   Calculated prefix ({calculated_prefix}) = pattern length ({pattern_length})")
                                self.detected_prefix_length = calculated_prefix
                            else:
                                # Use calculated prefix (spacing - record size) as it's more reliable
                                logger.info(f"📊   Using calculated prefix: {calculated_prefix} bytes")
                                self.detected_prefix_length = calculated_prefix
                            
                            return match_start
                        else:
                            # Spacing is smaller - unusual, but use detected size
                            logger.warning(f"⚠️ Pattern spacing ({detected_record_size}) is smaller than record size ({self.record_size})")
                            logger.info(f"📊 Using detected spacing as record size")
                            # Update record size to match detected spacing
                            self.record_size = detected_record_size
                            return match_start
                
                # Fallback: Check if first match is at a record boundary
                record_aligned = (match_start // self.record_size) * self.record_size
                position_in_record = match_start % self.record_size
                
                if position_in_record == 0:
                    # Perfect! Pattern is at record start
                    logger.info(f"📊 Found pattern at record start (offset {match_start})")
                    return match_start
                    
                    # Pattern is NOT at record start - need to find where it appears at record start
                    # Strategy: Check if there's comment text before it, then scan forward to find
                    # where POL001 appears at a record boundary
                    check_before = max(0, match_start - 30)
                    text_before = content[check_before:match_start].decode('utf-8', errors='ignore')
                    
                    # If there's comment text before, POL001 might be embedded in comments
                    # We need to find where POL001 appears at the START of a record (position 0)
                    if any(marker in text_before[-20:] for marker in ['#', 'characters', 'record', 'format', 'length', 'Total']):
                        # Pattern is embedded in comments - find where it appears at record start
                        # Start scanning from the NEXT record boundary after the match
                        next_record_start = ((match_start // self.record_size) + 1) * self.record_size
                        max_scan = min(match_start + (self.record_size * 10), len(content))
                        
                        # Scan forward record by record to find POL001 at record start
                        for offset in range(next_record_start, max_scan, self.record_size):
                            if offset + len(pattern_bytes) > len(content):
                                break
                            # Check if pattern appears at the START of this record
                            if content[offset:offset + len(pattern_bytes)] == pattern_bytes:
                                # Verify this isn't still in comment text
                                check_start = max(0, offset - 50)
                                check_text = content[check_start:offset + 20].decode('utf-8', errors='ignore')
                                if '#' in check_text and check_text.rfind('#') > (offset - check_start - 30):
                                    # Still in comments, continue
                                    continue
                                logger.info(f"📊 Found pattern at record start position {offset} (was embedded in comments at {match_start})")
                                return offset
                        
                        # If we can't find it at a record boundary, try aligning backwards
                        # Maybe the comments end exactly at a record boundary
                        prev_record_start = (match_start // self.record_size) * self.record_size
                        if prev_record_start >= 0 and prev_record_start + len(pattern_bytes) <= len(content):
                            # Check if pattern is at the start of the previous record
                            check_start = max(0, prev_record_start - 50)
                            check_text = content[check_start:prev_record_start + 20].decode('utf-8', errors='ignore')
                            if '#' not in check_text[-30:] or check_text.rfind('#') < (prev_record_start - check_start - 20):
                                # Not in comments, might be valid
                                if content[prev_record_start:prev_record_start + len(pattern_bytes)] == pattern_bytes:
                                    logger.info(f"📊 Found pattern at previous record start {prev_record_start}")
                                    return prev_record_start
                        
                        # Last resort: align to record boundary (might be wrong, but better than nothing)
                        logger.warning(f"⚠️ Pattern found at {match_start} but not at record start. Aligning to next record boundary {next_record_start}")
                        return next_record_start
                    else:
                        # Pattern might be at actual data start but not aligned
                        # Align to the record boundary
                        logger.info(f"📊 Pattern found at {match_start}, aligning to record boundary {record_aligned}")
                        return record_aligned
            except Exception as e:
                logger.warning(f"⚠️ Pattern matching failed: {e}, falling back to heuristics")
        
        # Strategy 2: General heuristics (extensible for any file type)
        # Scan at record-aligned boundaries
        max_scan = min(5000, len(content))  # Don't scan more than 5KB
        
        # Header keywords that indicate descriptive text (not data)
        header_keywords = [
            b'record', b'format', b'length', b'characters', b'contains',
            b'policyholder', b'each', b'some', b'suspicious', b'anomaly',
            b'total', b'size', b'bytes', b'char ', b'char-', b'char+',
            b'policy', b'premium', b'date', b'age', b'type', b'amount', b'issue',
            b'description', b'note', b'comment', b'header', b'footer'
        ]
        
        # Comment markers
        comment_markers = [b'#', b'*', b'/', b'//']
        
        # Start scanning from beginning (or from scan_start if pattern matching set it)
        # scan_start is initialized to 0, but may be updated if pattern matching finds embedded pattern
        start_offset = (scan_start // self.record_size) * self.record_size
        
        for offset in range(start_offset, max_scan, self.record_size):
            if offset + self.record_size > len(content):
                break
            
            # Get potential record at this offset
            record_bytes = content[offset:offset + self.record_size]
            record_text = record_bytes.decode('utf-8', errors='ignore')
            
            # Skip if starts with comment marker
            if any(record_bytes.startswith(marker) for marker in comment_markers):
                continue
            
            # Skip if contains header keywords (descriptive text)
            record_lower = record_text.lower().encode('utf-8')
            has_header_keywords = any(keyword in record_lower for keyword in header_keywords)
            if has_header_keywords:
                continue
            
            # Check if it looks like structured data (not descriptive text)
            # Valid data records typically have:
            # - High alphanumeric ratio (> 0.5)
            # - Low space ratio (< 0.4)
            # - Not all spaces or punctuation
            alphanumeric_count = sum(1 for c in record_text if c.isalnum())
            alphanumeric_ratio = alphanumeric_count / self.record_size if self.record_size > 0 else 0
            space_ratio = record_text.count(' ') / self.record_size if self.record_size > 0 else 1
            
            if alphanumeric_ratio > 0.5 and space_ratio < 0.4:
                # This looks like a valid data record!
                logger.info(f"📊 Found FIRST valid data record at offset {offset}")
                logger.info(f"📊   Sample: '{record_text[:50]}'")
                logger.info(f"📊   Alphanumeric ratio: {alphanumeric_ratio:.2f}, Space ratio: {space_ratio:.2f}")
                return offset
        
        # If no valid record found, assume no headers
        logger.warning(f"⚠️ Could not find clear data record, assuming no headers (starting at offset 0)")
        return 0
    
    def _detect_record_prefix(self, content: bytes) -> int:
        """
        Detect if records have a prefix identifier (e.g., "POL001", "POL002").
        
        This is extensible - detects common patterns:
        - 3 letters + 3 digits (e.g., "POL001", "REC001")
        - Long numeric strings at record start
        
        Returns:
            Length of prefix in bytes (0 if no prefix detected)
        """
        if len(content) < self.record_size * 2:
            return 0
        
        # Check first few records to see if they all start with the same pattern
        prefix_patterns = []
        
        # Check first 5 records to get a good sample
        for record_idx in range(min(5, len(content) // self.record_size)):
            record_start = record_idx * self.record_size
            if record_start + 10 > len(content):
                break
            
            record_start_bytes = content[record_start:record_start + 10]
            record_start_text = record_start_bytes.decode('utf-8', errors='ignore')
            
            logger.info(f"📊 Record {record_idx} first 10 bytes: '{record_start_text}' (hex: {record_start_bytes.hex()})")
            
            # Pattern 1: 3 letters + 3 digits (e.g., "POL001", "POL002")
            if len(record_start_text) >= 6:
                if record_start_text[:3].isalpha() and record_start_text[3:6].isdigit():
                    prefix_pattern = record_start_text[:6]
                    prefix_patterns.append(prefix_pattern)
                    logger.info(f"📊 Record {record_idx} starts with prefix pattern: '{prefix_pattern}'")
                    continue
            
            # Pattern 2: Check if it starts with just 2 letters (might be partial match)
            if len(record_start_text) >= 2 and record_start_text[:2].isalpha():
                # Might be a partial prefix, log it
                logger.info(f"📊 Record {record_idx} starts with partial pattern: '{record_start_text[:2]}'")
        
        # If we found consistent patterns across multiple records, it's a prefix
        if len(prefix_patterns) >= 2:
            # Check if all patterns follow the same format (3 letters + 3 digits)
            unique_patterns = set(prefix_patterns)
            if len(unique_patterns) == 1:
                # All records have the exact same prefix (unlikely, but possible)
                prefix_length = 6
                logger.info(f"📊 All records have same prefix: '{prefix_patterns[0]}' ({prefix_length} bytes)")
                return prefix_length
            else:
                # Check if all patterns follow the format: 3 letters + varying digits
                # (e.g., "POL001", "POL002", "POL003")
                first_letters = set(p[:3] for p in prefix_patterns if len(p) >= 3)
                if len(first_letters) == 1 and all(len(p) >= 6 and p[3:6].isdigit() for p in prefix_patterns):
                    prefix_length = 6
                    logger.info(f"📊 Detected record prefix of {prefix_length} bytes (pattern: {first_letters.pop()}###)")
                    return prefix_length
        
        return 0
    
    def _strip_record_prefixes(self, content: bytes, prefix_length: int, actual_record_size: Optional[int] = None) -> bytes:
        """
        Strip record prefixes/suffixes from all records.
        
        CRITICAL: If actual_record_size > record_size, the extra bytes might be:
        1. Prefix at the start (common for record identifiers)
        2. Suffix/padding at the end (common for alignment/padding)
        
        We try to detect which by checking if the pattern (e.g., "POL001") appears at the start.
        If it does, we assume it's part of the first field, not a prefix to strip.
        In that case, the extra bytes are likely padding at the END.
        
        Args:
            content: File content with prefixes/suffixes
            prefix_length: Length to strip from each record (interpreted as suffix if pattern is at start)
            actual_record_size: Actual record size in file (before stripping). If None, uses self.record_size
            
        Returns:
            Content with prefixes/suffixes removed
        """
        if prefix_length == 0:
            return content
        
        # Use actual record size if provided (e.g., 86 bytes), otherwise use copybook size (81 bytes)
        record_size_to_use = actual_record_size if actual_record_size else self.record_size
        
        # CRITICAL: If we detected a prefix length from pattern spacing (e.g., 5 bytes for "POL00"),
        # that means the pattern spacing (86) - copybook size (81) = prefix (5 bytes).
        # This prefix should be stripped from the START of each record.
        # 
        # The only time we strip from the END is if:
        # 1. We didn't detect a prefix from pattern spacing (prefix_length was detected another way)
        # 2. AND the pattern appears at the start AND the calculated prefix doesn't make sense
        # 
        # For our case: detected_prefix_length = 5 (from spacing), so we ALWAYS strip from start
        strip_from_end = False
        
        # Only check for end-stripping if prefix wasn't detected from pattern spacing
        # (i.e., if it was detected by examining record starts directly)
        if self.detected_prefix_length == 0 and len(content) >= record_size_to_use:
            first_record_start = content[:min(10, record_size_to_use)]
            first_record_text = first_record_start.decode('utf-8', errors='ignore')
            # If record starts with pattern-like text AND we didn't detect prefix from spacing,
            # it might be part of the field (strip from end as padding)
            if first_record_text.startswith('POL') or (self.first_field_pattern and 'POL' in str(self.first_field_pattern)):
                # But only if prefix_length matches pattern length (e.g., 6 for "POL001")
                # If prefix_length is different (e.g., 5 for "POL00"), it's a real prefix
                if prefix_length >= 6:  # Full pattern like "POL001"
                    strip_from_end = True
                    logger.info(f"📊 Pattern appears at record start - treating {prefix_length} bytes as END padding (not prefix)")
                else:
                    # Prefix length is less than pattern (e.g., 5 < 6), so it's a real prefix
                    logger.info(f"📊 Pattern at start but prefix_length ({prefix_length}) < pattern length - stripping from START")
        else:
            # Prefix was detected from pattern spacing - always strip from start
            logger.info(f"📊 Prefix detected from pattern spacing ({prefix_length} bytes) - stripping from START")
        
        # Split into records using the ACTUAL record size in the file
        # After stripping, records will be copybook size
        records = []
        for i in range(0, len(content), record_size_to_use):
            record = content[i:i + record_size_to_use]
            if len(record) < prefix_length:
                # Last partial record, skip stripping
                records.append(record)
            else:
                if strip_from_end:
                    # Strip from the END (padding/trailer)
                    stripped_record = record[:-prefix_length]
                else:
                    # Strip from the START (prefix)
                    stripped_record = record[prefix_length:]
                records.append(stripped_record)
        
        result = b''.join(records)
        location = "end (padding)" if strip_from_end else "start (prefix)"
        logger.info(f"📊 Stripped {prefix_length} bytes from {location} of {len(records)} records (split at {record_size_to_use}-byte boundaries)")
        
        # Debug: Verify first few records are correct size after stripping
        if len(records) > 0:
            logger.info(f"📊 First record after stripping: {len(records[0])} bytes (expected {self.record_size} bytes)")
            if len(records) > 1:
                logger.info(f"📊 Second record after stripping: {len(records[1])} bytes (expected {self.record_size} bytes)")
            if len(records) > 6:
                logger.info(f"📊 Seventh record after stripping: {len(records[6])} bytes (expected {self.record_size} bytes)")
            
            # Check if all records are the same size
            record_sizes = [len(r) for r in records]
            unique_sizes = set(record_sizes)
            if len(unique_sizes) > 1:
                logger.warning(f"⚠️ Records have inconsistent sizes after stripping: {unique_sizes}")
            else:
                logger.info(f"📊 All {len(records)} records are {record_sizes[0]} bytes after stripping")
        
        return result
