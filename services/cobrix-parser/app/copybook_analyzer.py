"""
Smart Copybook Analyzer
Detects which 01-level records are actual data records vs metadata/lookup tables.
"""

import re
from typing import List, Dict, Tuple, Optional

class CopybookRecord:
    """Represents a single 01-level record in the copybook."""
    def __init__(self, name: str, start_line: int, lines: List[str]):
        self.name = name
        self.start_line = start_line
        self.lines = lines
        self.has_value_clauses = False
        self.field_count = 0
        self.total_length = 0
        self.is_metadata = False
        
    def analyze(self):
        """Analyze the record to determine if it's data or metadata."""
        # Check for VALUE clauses (metadata indicator)
        for line in self.lines:
            if re.search(r'\bVALUE\s+', line, re.IGNORECASE):
                self.has_value_clauses = True
                break
        
        # Count fields (05-level and below)
        for line in self.lines:
            # Match level numbers (05, 10, 15, etc.)
            match = re.match(r'^\s*(\d+)\s+', line)
            if match:
                level = int(match.group(1))
                if level >= 5:  # Field level (not 01)
                    self.field_count += 1
                    # Try to extract PIC clause to estimate length
                    pic_match = re.search(r'PIC\s+([X9]+)\((\d+)\)', line, re.IGNORECASE)
                    if pic_match:
                        length = int(pic_match.group(2))
                        self.total_length += length
        
        # Heuristics to identify metadata records
        metadata_keywords = [
            'TYPES', 'VALIDATION', 'RULES', 'THRESHOLDS', 
            'FLAGS', 'FIELDS', 'REPORT', 'CONFIG', 'CONSTANT'
        ]
        name_upper = self.name.upper()
        for keyword in metadata_keywords:
            if keyword in name_upper:
                self.is_metadata = True
                break
        
        # If it has VALUE clauses, it's definitely metadata
        if self.has_value_clauses:
            self.is_metadata = True

def analyze_copybook(copybook_content: str) -> Tuple[List[CopybookRecord], Optional[CopybookRecord]]:
    """
    Analyze copybook to find all 01-level records and identify the data record.
    
    Returns:
        (all_records, data_record) - List of all records and the identified data record
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not copybook_content or not copybook_content.strip():
        raise ValueError("Copybook content is empty")
    
    lines = copybook_content.split('\n')
    logger.info(f"📋 Analyzing copybook: {len(lines)} lines, {len(copybook_content)} characters")
    records: List[CopybookRecord] = []
    current_record: Optional[CopybookRecord] = None
    
    for i, line in enumerate(lines):
        # Match 01-level record definition
        # Pattern: optional asterisk (comment marker) + spaces + "01" + spaces + record-name + optional period
        # Some copybooks have *01 which is technically a comment but contains the record definition
        # Handle both "01" and "*01" patterns (with optional leading whitespace)
        # First strip leading whitespace, then check for optional asterisk
        line_stripped = line.lstrip()
        if line_stripped.startswith('*'):
            line_stripped = line_stripped[1:].lstrip()  # Remove asterisk and any following whitespace
        match = re.match(r'^\s*01\s+(\w+(?:-\w+)*)', line_stripped, re.IGNORECASE)
        if match:
            # Save previous record if exists
            if current_record:
                records.append(current_record)
            
            # Start new record
            record_name = match.group(1)
            current_record = CopybookRecord(record_name, i, [line])
        elif current_record:
            # Continue current record until next 01 or end
            # Check if this is the start of a new 01-level record
            line_stripped = line.lstrip()
            if line_stripped.startswith('*'):
                line_stripped = line_stripped[1:].lstrip()  # Remove asterisk and any following whitespace
            if re.match(r'^\s*01\s+', line_stripped, re.IGNORECASE):
                # This shouldn't happen, but handle it
                if current_record:
                    records.append(current_record)
                match = re.match(r'^\s*01\s+(\w+(?:-\w+)*)', line_stripped, re.IGNORECASE)
                if match:
                    current_record = CopybookRecord(match.group(1), i, [line])
            else:
                # Add line to current record
                current_record.lines.append(line)
    
    # Don't forget the last record
    if current_record:
        records.append(current_record)
    
    # Analyze each record
    for record in records:
        record.analyze()
    
    # Find the data record using heuristics
    data_record = None
    
    # Strategy 1: Find record without VALUE clauses and not marked as metadata
    candidates = [r for r in records if not r.has_value_clauses and not r.is_metadata]
    if candidates:
        # Prefer the first one (most common pattern)
        data_record = candidates[0]
        # Or prefer the one with most fields
        if len(candidates) > 1:
            data_record = max(candidates, key=lambda r: r.field_count)
    
    # Strategy 2: If all have VALUE clauses, find the one with most fields (likely data)
    if not data_record:
        if not records:
            # Log the first few lines of the copybook for debugging
            sample_lines = '\n'.join(lines[:20])
            logger.error(f"❌ No 01-level records found in copybook. First 20 lines:\n{sample_lines}")
            raise ValueError(f"No records found in copybook. Please check the copybook format. Copybook has {len(lines)} lines, {len(copybook_content)} characters.")
        data_record = max(records, key=lambda r: r.field_count)
    
    # Strategy 3: If still unclear, use the first record
    if not data_record and records:
        data_record = records[0]
    
    return records, data_record

def extract_data_record_copybook(copybook_content: str, record_name: Optional[str] = None) -> str:
    """
    Extract only the data record from a copybook with multiple 01-level records.
    
    Args:
        copybook_content: Full copybook content
        record_name: Optional specific record name to extract. If None, auto-detects.
    
    Returns:
        Cleaned copybook with only the data record
    """
    records, auto_detected_record = analyze_copybook(copybook_content)
    
    if not records:
        # No 01-level records found, return as-is
        return copybook_content
    
    # Use specified record or auto-detected
    target_record = None
    if record_name:
        for record in records:
            if record.name.upper() == record_name.upper():
                target_record = record
                break
        if not target_record:
            # Fallback to auto-detected
            target_record = auto_detected_record
    else:
        target_record = auto_detected_record
    
    if not target_record:
        # Fallback: return first record
        target_record = records[0]
    
    # Extract lines for the target record
    # Include the 01-level line and all subsequent lines until next 01 or end
    result_lines = []
    in_target_record = False
    
    for line in copybook_content.split('\n'):
        # Check if this is the start of our target record
        match = re.match(r'^\s*01\s+(\w+(?:-\w+)*)', line, re.IGNORECASE)
        if match:
            record_name_found = match.group(1)
            if record_name_found == target_record.name:
                in_target_record = True
                result_lines.append(line)
            else:
                in_target_record = False
        elif in_target_record:
            # Check if we hit another 01-level record (end of our record)
            if re.match(r'^\s*01\s+', line, re.IGNORECASE):
                in_target_record = False
            else:
                result_lines.append(line)
    
    return '\n'.join(result_lines)


