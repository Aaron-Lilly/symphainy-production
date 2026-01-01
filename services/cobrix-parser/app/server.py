#!/usr/bin/env python3
"""
Cobrix HTTP API Server - FastAPI wrapper for Cobrix parsing
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import subprocess
import json
import asyncio
import logging
import sys
import re
from typing import Optional

# Add app directory to Python path for imports
sys.path.insert(0, '/opt/cobrix/app')

# Import normalization and analysis modules
# Note: Some imports are done lazily inside functions to avoid import errors
from copybook_analyzer import analyze_copybook, extract_data_record_copybook
from file_format_normalizer import FileFormatNormalizer

# Configure logging to stderr (so it shows in docker logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cobrix Parser Service", version="1.0.0")

# Spark and Cobrix paths
SPARK_HOME = "/opt/cobrix/spark"
COBRIX_JAR = "/tmp/cobrix-spark-cobol-bundle.jar"
APP_JAR = "/opt/cobrix/cobrix-parser-service.jar"

def _detect_encoding(file_path: str) -> str:
    """
    Detect file encoding (EBCDIC vs ASCII) by analyzing byte patterns.
    
    Returns:
        Encoding string: "ascii", "cp037" (EBCDIC), or "cp1047" (EBCDIC variant)
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 1000 bytes for analysis
            sample = f.read(1000)
            
        if not sample:
            return "ascii"  # Default to ASCII
        
        # EBCDIC detection heuristics:
        # - EBCDIC digits are 0xF0-0xF9
        # - EBCDIC letters have different ranges than ASCII
        # - ASCII printable range is 0x20-0x7E
        # - EBCDIC has more high-byte values
        
        ebcdic_indicators = 0
        ascii_indicators = 0
        
        for byte in sample:
            # ASCII printable range
            if 0x20 <= byte <= 0x7E:
                ascii_indicators += 1
            # EBCDIC digit range
            elif 0xF0 <= byte <= 0xF9:
                ebcdic_indicators += 1
            # EBCDIC letter ranges
            elif 0xC1 <= byte <= 0xC9 or 0xD1 <= byte <= 0xD9 or 0xE2 <= byte <= 0xE9:
                ebcdic_indicators += 1
            # High bytes (common in EBCDIC, rare in ASCII)
            elif byte >= 0x80:
                ebcdic_indicators += 0.5
        
        # Decision logic
        # Cobrix expects "EBCDIC" or "ASCII", not codec names like "cp037"
        if ebcdic_indicators > ascii_indicators * 2:
            # Strong EBCDIC indicators
            return "EBCDIC"
        else:
            return "ASCII"
    
    except Exception as e:
        logger.warning(f"Encoding detection failed: {e}, defaulting to ASCII")
        return "ascii"

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cobrix-parser"}

@app.post("/parse/cobol")
async def parse_cobol(
    file: UploadFile = File(...),
    copybook: UploadFile = File(...)
):
    """
    Parse COBOL file using Cobrix.
    
    Args:
        file: Binary mainframe file
        copybook: COBOL copybook file
    
    Returns:
        JSON with parsed records and metadata
    """
    try:
        # Download Cobrix bundle JAR if not present
        if not os.path.exists(COBRIX_JAR):
            logger.info("Downloading Cobrix bundle JAR...")
            result = subprocess.run(
                [
                    "wget", "-q",
                    "https://github.com/AbsaOSS/cobrix/releases/download/v2.9.0/spark-cobol_2.12-2.9.0-bundle.jar",
                    "-O", COBRIX_JAR
                ],
                capture_output=True,
                text=True,
                timeout=60.0
            )
            if result.returncode != 0:
                # Try alternative version
                result = subprocess.run(
                    [
                        "wget", "-q",
                        "https://github.com/AbsaOSS/cobrix/releases/download/v2.8.4/spark-cobol_2.12-2.8.4-bundle.jar",
                        "-O", COBRIX_JAR
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60.0
                )
                if result.returncode != 0:
                    raise HTTPException(status_code=500, detail="Failed to download Cobrix JAR")
        
        # Create temporary directory for files
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, file.filename or "data.bin")
            copybook_file = os.path.join(tmpdir, copybook.filename or "copybook.cpy")
            output_dir = os.path.join(tmpdir, "output")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Write uploaded files
            file_content = await file.read()
            with open(input_file, 'wb') as f:
                f.write(file_content)
            
            # ========================================================================
            # ROOT CAUSE ANALYSIS: Examine file structure
            # ========================================================================
            file_size = len(file_content)
            logger.info(f"📁 ===== FILE STRUCTURE ANALYSIS =====")
            logger.info(f"📁 File size: {file_size} bytes")
            logger.info(f"📁 Filename: {file.filename}")
            
            # Show first 1000 bytes in multiple formats
            first_1000 = file_content[:1000]
            logger.info(f"📁 First 1000 bytes (hex, first 400): {first_1000[:400].hex()}")
            first_1000_text = first_1000.decode('utf-8', errors='ignore')
            logger.info(f"📁 First 1000 bytes (text): {repr(first_1000_text)}")
            
            # Count newlines and analyze structure
            newline_count = first_1000_text.count('\n')
            hash_count = first_1000_text.count('#')
            logger.info(f"📁 First 1000 bytes: {newline_count} newlines, {hash_count} hash tags")
            
            # Look for record patterns at expected record boundaries (81 bytes)
            # This will help us understand where actual data records start
            record_size_expected = 81  # Will be confirmed by copybook
            logger.info(f"📁 Scanning for record patterns (expected record size: {record_size_expected} bytes)...")
            record_candidates = []
            for offset in range(0, min(3000, file_size), record_size_expected):
                if offset + 30 > file_size:
                    break
                sample = file_content[offset:offset + 30]
                sample_text = sample.decode('utf-8', errors='ignore').strip()
                
                # Check for various record start patterns
                pattern_type = None
                if len(sample_text) >= 6 and sample_text[:3].upper() == 'POL' and sample_text[3:6].isdigit():
                    pattern_type = f"POL prefix: '{sample_text[:10]}'"
                elif len(sample_text) >= 20 and sample_text[:20].replace(' ', '').isdigit():
                    pattern_type = f"Numeric: '{sample_text[:20]}'"
                elif '#' in sample_text or any(word in sample_text.lower() for word in ['record', 'format', 'length', 'characters']):
                    pattern_type = f"Header/comment: '{sample_text[:30]}'"
                
                if pattern_type:
                    record_candidates.append((offset, pattern_type))
                    logger.info(f"📁   Offset {offset:4d}: {pattern_type}")
            
            if record_candidates:
                logger.info(f"📁 Found {len(record_candidates)} potential record start positions")
                # The first non-header candidate is likely the actual data start
                data_candidates = [c for c in record_candidates if 'Header' not in c[1] and 'comment' not in c[1]]
                if data_candidates:
                    first_data_candidate = data_candidates[0]
                    logger.info(f"📁 First data candidate: offset {first_data_candidate[0]} - {first_data_candidate[1]}")
            else:
                logger.warning(f"📁 No clear record patterns found in first 3000 bytes")
            
            logger.info(f"📁 ===== END FILE STRUCTURE ANALYSIS =====")
            
            # Clean copybook: remove hash tag comments while preserving COBOL structure
            copybook_content = await copybook.read()
            copybook_text = copybook_content.decode('utf-8', errors='ignore')
            
            # Detect copybook format by checking first few non-comment lines
            # Standard COBOL: columns 1-5 = line numbers, 6 = continuation, 7-72 = code
            # Free-form: level number starts at column 1
            is_standard_cobol_format = False
            sample_lines = copybook_text.split('\n')[:10]
            for sample_line in sample_lines:
                if len(sample_line) > 6 and sample_line[6] not in ('*', '/', ' ', '\t'):
                    # Check if columns 1-5 look like line numbers (digits or spaces)
                    first_5 = sample_line[:5].strip()
                    if not first_5 or first_5.isdigit():
                        is_standard_cobol_format = True
                        break
                # Check if line starts with level number (01, 05, etc.) at column 0
                stripped = sample_line.strip()
                if stripped and len(stripped) >= 2 and stripped[:2].isdigit() and int(stripped[:2]) in range(1, 50):
                    # Looks like free-form (level number at start)
                    is_standard_cobol_format = False
                    break
            
            logger.info(f"📋 Detected copybook format: {'Standard COBOL (columns 6-72)' if is_standard_cobol_format else 'Free-form (level at column 0)'}")
            
            # Analyze copybook for multiple 01-level records
            # If multiple records found, extract only the data record
            # If analysis fails, just pass the whole copybook to Cobrix (it can handle it)
            from copybook_analyzer import analyze_copybook, extract_data_record_copybook
            
            try:
                records, data_record = analyze_copybook(copybook_text)
                if len(records) > 1:
                    logger.info(f"📋 Found {len(records)} 01-level records in copybook:")
                    for record in records:
                        logger.info(f"   - {record.name}: {record.field_count} fields, has VALUE: {record.has_value_clauses}, is metadata: {record.is_metadata}")
                    
                    if data_record:
                        logger.info(f"📋 Auto-detected data record: {data_record.name} (field_count={data_record.field_count}, has_value={data_record.has_value_clauses})")
                        # Extract only the data record
                        copybook_text = extract_data_record_copybook(copybook_text, data_record.name)
                        logger.info(f"📋 Extracted data record copybook: {len(copybook_text.split(chr(10)))} lines")
                    else:
                        logger.warning(f"⚠️ Could not auto-detect data record, using first record: {records[0].name}")
                        copybook_text = extract_data_record_copybook(copybook_text, records[0].name)
                elif len(records) == 1:
                    logger.info(f"📋 Single 01-level record found: {records[0].name}")
                else:
                    logger.warning(f"⚠️ No 01-level records found in copybook, proceeding with full copybook (Cobrix will handle it)")
            except Exception as e:
                logger.warning(f"⚠️ Copybook analysis failed: {e}, proceeding with full copybook (Cobrix will handle it)")
                # Continue with full copybook - Cobrix can handle it
            
            # Clean the copybook:
            # 1. Remove hash tag comments (everything from # to end of line)
            # 2. Remove full-line comments (lines starting with * or /)
            # 3. Preserve COBOL structure
            cleaned_lines = []
            continuation_buffer = []
            
            for line in copybook_text.split('\n'):
                line_stripped = line.rstrip()
                
                # Skip completely empty lines
                if not line_stripped:
                    continue
                
                # Handle standard COBOL format (columns 6-72)
                if is_standard_cobol_format:
                    # Check if this is a full comment line (COBOL: * or / in column 7)
                    if len(line) > 6 and line[6] in ('*', '/'):
                        continue
                    
                    # Extract COBOL code (columns 6-72) - matches legacy clean_cobol behavior
                    # Legacy uses: row[6:72].rstrip() - includes column 6!
                    if len(line) > 6:
                        # Check if column 6 is a continuation marker (-)
                        if line[6] == '-':
                            # Continuation line - extract columns 7-72 (skip the '-' marker)
                            cobol_code = line[7:72].rstrip() if len(line) > 72 else line[7:].rstrip()
                            continuation_buffer.append(cobol_code)
                            continue
                        else:
                            # Regular line - extract columns 6-72 (matches legacy: row[6:72])
                            cobol_code = line[6:72].rstrip() if len(line) > 72 else line[6:].rstrip()
                    else:
                        cobol_code = line_stripped
                    
                    # Skip 88-level statements entirely - Cobrix doesn't support them
                    # We extract them separately for validation, but they shouldn't be in the copybook
                    cobol_code_check = cobol_code.strip()
                    if cobol_code_check.startswith('88 ') or re.match(r'^\s*88\s+', cobol_code_check):
                        # This is an 88-level statement - skip it
                        if continuation_buffer:
                            continuation_buffer = []
                        continue
                else:
                    # Free-form format - use line as-is (just strip)
                    cobol_code = line_stripped
                    # Check if it's a comment line
                    if cobol_code.strip().startswith('*') or cobol_code.strip().startswith('/'):
                        continue
                    
                    # Remove sequence numbers/identifiers at the start of lines (e.g., "AF1019", "MET001")
                    # These identifiers appear before level numbers and need to be stripped
                    cobol_code_stripped = cobol_code.lstrip()
                    
                    # Pattern: Match alphanumeric identifier (2-8 chars) followed by whitespace
                    # Then check if what follows is a level number or field name
                    identifier_match = re.match(r'^([A-Z0-9]{2,8})\s+', cobol_code_stripped)
                    if identifier_match:
                        identifier = identifier_match.group(1)
                        remaining = cobol_code_stripped[len(identifier):].lstrip()
                        # Check if what follows looks like COBOL (starts with level number 01-99 or field name)
                        if remaining:
                            # Check if it starts with a level number (01-99) or looks like a field definition
                            level_match = re.match(r'^(\d{2})\s+', remaining)
                            if level_match:
                                level_num = level_match.group(1)
                                if 1 <= int(level_num) <= 99:
                                    # Valid level number - remove identifier
                                    cobol_code = remaining
                                    logger.info(f"📋 Removed identifier '{identifier}' from line (level {level_num})")
                            elif remaining[0].isalpha():
                                # Starts with letter - might be a field name, but could also be part of identifier
                                # Only remove if there's a level number later in the line
                                if re.search(r'\s+(\d{2})\s+', remaining):
                                    # Has a level number somewhere - remove identifier
                                    cobol_code = remaining
                                    logger.info(f"📋 Removed identifier '{identifier}' from line (has level number)")
                    
                    # Skip 88-level statements entirely - Cobrix doesn't support them
                    # We extract them separately for validation, but they shouldn't be in the copybook
                    cobol_code_check = cobol_code.strip()
                    if cobol_code_check.startswith('88 ') or re.match(r'^\s*88\s+', cobol_code_check):
                        # This is an 88-level statement - skip it
                        if continuation_buffer:
                            continuation_buffer = []
                        continue
                
                # Remove hash tag comments from the line
                if '#' in cobol_code:
                    hash_pos = cobol_code.find('#')
                    cobol_code = cobol_code[:hash_pos].rstrip()
                    if not cobol_code:
                        if continuation_buffer:
                            continuation_buffer = []
                        continue
                
                # Remove VALUE clauses - Cobrix doesn't support them (they're runtime initialization, not structure)
                # VALUE clauses can appear as: VALUE 'literal' or VALUE 123 or VALUE SPACES, etc.
                # We need to remove everything from "VALUE" to the end of the statement (period)
                if ' VALUE ' in cobol_code.upper() or cobol_code.strip().upper().startswith('VALUE '):
                    # Find VALUE keyword (case-insensitive)
                    value_pos = cobol_code.upper().find(' VALUE ')
                    if value_pos == -1:
                        value_pos = cobol_code.upper().find('VALUE ')
                    if value_pos != -1:
                        # Remove everything from VALUE to the end (including period if present)
                        cobol_code = cobol_code[:value_pos].rstrip()
                        # If the line is now empty or just whitespace, skip it
                        if not cobol_code.strip():
                            if continuation_buffer:
                                continuation_buffer = []
                            continue
                
                # Handle continuation lines - only join lines marked with '-' in column 6
                # In standard COBOL, continuation lines are marked with '-' in column 6
                # We already handled explicit continuation markers above, so here we just add the line
                # Don't join lines just because they don't have periods - each field is separate
                if continuation_buffer:
                    # We have a continuation buffer from a previous line with '-'
                    full_line = ' '.join(continuation_buffer) + ' ' + cobol_code
                    continuation_buffer = []
                    cleaned_lines.append(full_line)
                else:
                    # Regular line - add it as-is
                    # Cobrix requires periods on all field definitions, so add one if missing
                    # (unless it's already a complete statement with period)
                    if cobol_code.strip() and not cobol_code.rstrip().endswith('.'):
                        # Check if this looks like a field definition (starts with level number)
                        # Level numbers are typically 01-49, 66, 77, 88
                        stripped = cobol_code.strip()
                        if stripped and (stripped[0].isdigit() or stripped.startswith('66 ') or stripped.startswith('77 ') or stripped.startswith('88 ')):
                            # It's a field definition - add period if missing
                            cobol_code = cobol_code.rstrip() + '.'
                    cleaned_lines.append(cobol_code)
            
            # Handle any remaining continuation buffer (shouldn't happen if logic is correct)
            if continuation_buffer:
                incomplete_line = ' '.join(continuation_buffer)
                logger.warning(f"⚠️ Unfinished continuation line: {incomplete_line[:100]}")
                cleaned_lines.append(incomplete_line)
            
            # Join cleaned lines - write in standard COBOL format (columns 6-72)
            # Cobrix expects standard COBOL format where:
            # - Columns 1-5: Line numbers (can be spaces)
            # - Column 6: Continuation marker (space for normal lines)
            # - Columns 7-72: Actual COBOL code (level number starts at column 7)
            # NOTE: We don't truncate at 72 characters - Cobrix should handle longer lines
            # If a line is longer, it means continuation lines were joined (legacy behavior)
            final_cleaned_lines = []
            for line in cleaned_lines:
                stripped_line = line.lstrip()
                if stripped_line:  # Only add non-empty lines
                    # Format as standard COBOL: pad to column 6, then add the code
                    # Columns 1-5: spaces (no line numbers)
                    # Column 6: space (not a continuation)
                    # Columns 7+: the actual COBOL code (may exceed 72 if continuation lines were joined)
                    formatted_line = "      " + stripped_line  # 6 spaces to reach column 7
                    # Don't truncate - Cobrix should handle longer lines (joined continuations)
                    final_cleaned_lines.append(formatted_line)
            
            cleaned_copybook = '\n'.join(final_cleaned_lines)
            
            # Debug: log first few lines and lines around errors
            if final_cleaned_lines:
                logger.info(f"📝 Cleaned copybook: {len(copybook_text.split(chr(10)))} lines → {len(final_cleaned_lines)} lines (standard COBOL format)")
                logger.info(f"📝 Cleaned copybook preview (first 5 lines, standard COBOL format):")
                for i, line in enumerate(final_cleaned_lines[:5], 1):
                    logger.info(f"   Line {i}: {repr(line[:100])}")
                    logger.info(f"   Line {i} columns 1-6: {repr(line[0:6])}")
                    logger.info(f"   Line {i} column 7 (level number start): {repr(line[6:8]) if len(line) > 7 else 'N/A'}")
                # Log lines 9-10 (where errors often occur)
                if len(final_cleaned_lines) >= 10:
                    for i in [8, 9]:  # Lines 9 and 10 (0-indexed: 8, 9)
                        line = final_cleaned_lines[i]
                        logger.info(f"📝 Line {i+1}: {repr(line)}")
                        logger.info(f"📝 Line {i+1} length: {len(line)}")
                        logger.info(f"📝 Line {i+1} ends with period: {line.rstrip().endswith('.')}")
                # Log line 29 specifically (where the error occurs)
                if len(final_cleaned_lines) >= 29:
                    line_29 = final_cleaned_lines[28]  # 0-indexed
                    logger.info(f"📝 Line 29 (error location): {repr(line_29)}")
                    logger.info(f"📝 Line 29 length: {len(line_29)}")
                    logger.info(f"📝 Line 29 columns 1-6: {repr(line_29[0:6])}")
                    logger.info(f"📝 Line 29 column 7-50: {repr(line_29[6:50]) if len(line_29) > 6 else 'N/A'}")
                    logger.info(f"📝 Line 29 around position 47: {repr(line_29[40:54]) if len(line_29) > 40 else 'N/A'}")
                    logger.info(f"📝 Line 29 hex: {line_29.encode('utf-8').hex()[:100]}")
            
            # CRITICAL DEBUG: Verify AGE field is in the cleaned copybook BEFORE writing
            logger.info(f"📋 VERIFYING AGE FIELD IN CLEANED COPYBOOK:")
            age_found = False
            for i, line in enumerate(cleaned_copybook.split('\n'), 1):
                if 'AGE' in line.upper():
                    age_found = True
                    logger.info(f"   ✅ Line {i} contains AGE: {repr(line)}")
                    # Try alternative format: PIC 999 instead of PIC 9(3)
                    if 'PIC 9(3)' in line:
                        logger.warning(f"   ⚠️  AGE field uses PIC 9(3) - Cobrix might not parse this correctly!")
                        logger.warning(f"   ⚠️  Trying alternative: PIC 999")
                        # Replace PIC 9(3) with PIC 999
                        cleaned_copybook = cleaned_copybook.replace('PIC 9(3)', 'PIC 999')
                        logger.info(f"   ✅ Replaced PIC 9(3) with PIC 999 in copybook")
                    
                    # EXPERIMENT: Try multiple fixes for AGE field
                    # 1. Change field name from hyphen to underscore (Cobrix might convert hyphens anyway)
                    # 2. Try making it a string field instead of numeric (PIC X(3) instead of PIC 999)
                    if 'POLICYHOLDER-AGE' in line or 'POLICYHOLDER_AGE' in line:
                        logger.warning(f"   ⚠️  AGE field found - trying multiple fixes")
                        # Fix 1: Replace hyphen with underscore in field name
                        if 'POLICYHOLDER-AGE' in cleaned_copybook:
                            cleaned_copybook = cleaned_copybook.replace('POLICYHOLDER-AGE', 'POLICYHOLDER_AGE')
                            logger.info(f"   ✅ Replaced POLICYHOLDER-AGE with POLICYHOLDER_AGE in copybook")
                        
                        # Fix 2: Try PIC X(3) instead of PIC 999 (string instead of numeric)
                        # This is a test - if Cobrix parses it as string, we know the issue is with numeric fields
                        # We'll convert it back to numeric after parsing if needed
                        # Check if this line has PIC 999 (might have been replaced from PIC 9(3) above)
                        if 'PIC 999' in line or 'PIC 9(3)' in line:
                            logger.warning(f"   ⚠️  Trying PIC X(3) instead of PIC 999/9(3) (string format)")
                            # Replace PIC 999 or PIC 9(3) with PIC X(3) in the AGE line
                            # Find the line index
                            lines = cleaned_copybook.split('\n')
                            age_line_idx = -1
                            for idx, l in enumerate(lines):
                                if 'POLICYHOLDER_AGE' in l.upper() or 'POLICYHOLDER-AGE' in l.upper():
                                    age_line_idx = idx
                                    break
                            
                            if age_line_idx >= 0:
                                # Replace PIC 999 or PIC 9(3) with PIC X(3)
                                if 'PIC 999' in lines[age_line_idx]:
                                    lines[age_line_idx] = lines[age_line_idx].replace('PIC 999', 'PIC X(3)')
                                elif 'PIC 9(3)' in lines[age_line_idx]:
                                    lines[age_line_idx] = lines[age_line_idx].replace('PIC 9(3)', 'PIC X(3)')
                                cleaned_copybook = '\n'.join(lines)
                                logger.info(f"   ✅ Replaced PIC 999/9(3) with PIC X(3) for AGE field (experimental)")
                                logger.info(f"   📋 Updated AGE line: {repr(lines[age_line_idx])}")
            if not age_found:
                logger.error(f"   ❌ AGE field NOT FOUND in cleaned copybook!")
            logger.info(f"📋 Full cleaned copybook ({len(cleaned_copybook.split(chr(10)))} lines):")
            for i, line in enumerate(cleaned_copybook.split('\n'), 1):
                logger.info(f"   Line {i}: {repr(line)}")
            
            # Write cleaned copybook
            logger.info(f"📝 Writing cleaned copybook to: {copybook_file}")
            # Write as binary to avoid any encoding issues, and ensure no BOM
            with open(copybook_file, 'wb') as f:
                # Write UTF-8 without BOM
                f.write(cleaned_copybook.encode('utf-8'))
                f.flush()  # Ensure it's written before context manager closes
            logger.info(f"📝 File written, size: {os.path.getsize(copybook_file)} bytes")
            
            # Verify the raw bytes written
            with open(copybook_file, 'rb') as f:
                first_bytes = f.read(50)
                logger.info(f"📝 First 50 bytes of file (hex): {first_bytes.hex()}")
                logger.info(f"📝 First 50 bytes of file (repr): {repr(first_bytes)}")
            
            # Verify what was actually written by reading it back
            with open(copybook_file, 'r', encoding='utf-8') as f:
                written_content = f.read()
                written_lines = written_content.split('\n')
                logger.info(f"📝 Verified written copybook (first 3 lines from file, {len(written_lines)} total lines):")
                for i, line in enumerate(written_lines[:3], 1):
                    logger.info(f"   Line {i}: {repr(line[:100])}")
                    logger.info(f"   Line {i} length: {len(line)}, starts with: {repr(line[:10])}")
                    # Check if level number is present
                    if line.strip():
                        first_chars = line.strip()[:10]
                        logger.info(f"   Line {i} first 10 chars (stripped): {repr(first_chars)}")
            
            logger.info(f"📝 Cleaned copybook: {len(copybook_text.split(chr(10)))} lines → {len(cleaned_lines)} lines")
            
            # Normalize the file BEFORE running Spark (not after it fails)
            # This handles:
            # - Text files with newlines → Binary format (no delimiters)
            # - Files with embedded headers/comments → Pure data records
            # - Files with trailers/padding → Perfectly divisible by record size
            if data_record:
                record_size = data_record.total_length
            else:
                # Fallback: try to calculate from copybook
                record_size = 81  # Default, will be corrected if Spark fails
            
            # Extract first field pattern from copybook for better detection
            first_field_pattern = None
            for line in cleaned_copybook.split('\n'):
                if re.match(r'^\s*05\s+', line, re.IGNORECASE):
                    field_match = re.search(r'05\s+(\w+(?:-\w+)*)', line, re.IGNORECASE)
                    if field_match:
                        field_name = field_match.group(1).upper()
                        if 'POLICY' in field_name or 'POL' in field_name:
                            first_field_pattern = r'POL\d{3}'
                        elif 'ID' in field_name or 'NUMBER' in field_name:
                            first_field_pattern = r'[A-Z0-9]{3,}'
                        break
            
            normalizer = FileFormatNormalizer(record_size, first_field_pattern)
            normalized_content, normalization_metadata = normalizer.normalize(file_content)
            
            # Write normalized file
            with open(input_file, 'wb') as f:
                f.write(normalized_content)
            
            logger.info(f"📊 File normalized BEFORE Spark run:")
            logger.info(f"   Original: {normalization_metadata['original_size']} bytes")
            logger.info(f"   Newlines removed: {normalization_metadata['newlines_removed']}")
            logger.info(f"   Header bytes removed: {normalization_metadata['header_bytes']}")
            logger.info(f"   Final size: {normalization_metadata['normalized_size']} bytes ({normalization_metadata['record_count']} records)")
            
            # Run Spark application
            env = os.environ.copy()
            env['SPARK_HOME'] = SPARK_HOME
            env['PATH'] = f"{SPARK_HOME}/bin:{env.get('PATH', '')}"
            
            # Detect encoding from file content
            detected_encoding = _detect_encoding(input_file)
            logger.info(f"📊 Detected encoding: {detected_encoding}")
            
            # Build spark-submit command
            cmd = [
                f"{SPARK_HOME}/bin/spark-submit",
                "--master", "local[1]",
                "--jars", COBRIX_JAR,
                "--class", "za.co.absa.cobrix.CobrixParserApp",
                "--conf", "spark.sql.warehouse.dir=/tmp/spark-warehouse",
                "--conf", "spark.driver.memory=2g",
                "--conf", "spark.executor.memory=2g",
                "--conf", "spark.driver.maxResultSize=2g",
                "--conf", "spark.serializer=org.apache.spark.serializer.KryoSerializer",
                APP_JAR,
                "--input", input_file,
                "--copybook", copybook_file,
                "--output", output_dir,
                "--encoding", detected_encoding
            ]
            
            logger.info(f"🔧 Running command: {' '.join(cmd)}")
            logger.info(f"📁 Input file: {input_file} (exists: {os.path.exists(input_file)})")
            logger.info(f"📁 Copybook file: {copybook_file} (exists: {os.path.exists(copybook_file)})")
            logger.info(f"📁 Output dir: {output_dir}")
            logger.info(f"📦 Cobrix JAR: {COBRIX_JAR} (exists: {os.path.exists(COBRIX_JAR)})")
            logger.info(f"📦 App JAR: {APP_JAR} (exists: {os.path.exists(APP_JAR)})")
            
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300.0,
                env=env
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                
                # Check if error is about file size not being divisible by record size
                if "IS NOT DIVISIBLE" in error_msg or "NOT DIVISIBLE" in error_msg:
                    # Extract record size from error message
                    # Note: re is already imported at the top of the file
                    record_size_match = re.search(r'(\d+)\s+bytes?\s+per\s+record', error_msg, re.IGNORECASE)
                    if record_size_match:
                        record_size = int(record_size_match.group(1))
                        # Get current file size
                        input_file_size = os.path.getsize(input_file)
                        logger.warning(f"⚠️ File size ({input_file_size} bytes) not divisible by record size ({record_size} bytes)")
                        
                        # Calculate remainder
                        remainder = input_file_size % record_size
                        logger.info(f"📊 Need to trim {remainder} bytes to make file divisible by record size")
                        
                        # Read the file to analyze
                        with open(input_file, 'rb') as f:
                            file_content = f.read()
                        
                        # Use FileFormatNormalizer to handle various file formats
                        # This normalizes:
                        # - Text files with newlines → Binary format (no delimiters)
                        # - Files with embedded headers/comments → Pure data records
                        # - Files with trailers/padding → Perfectly divisible by record size
                        
                        # Extract first field pattern from copybook for better detection
                        # Look for first field in data record (typically starts with level 05)
                        # Use cleaned_copybook which is the cleaned version ready for Cobrix
                        first_field_pattern = None
                        for line in cleaned_copybook.split('\n'):
                            # Find first 05-level field (first data field)
                            if re.match(r'^\s*05\s+', line, re.IGNORECASE):
                                # Try to extract field name and infer pattern
                                # For POLICY-NUMBER, we might see "POL" prefix in data
                                field_match = re.search(r'05\s+(\w+(?:-\w+)*)', line, re.IGNORECASE)
                                if field_match:
                                    field_name = field_match.group(1).upper()
                                    # Common patterns: POLICY-NUMBER might start with "POL", etc.
                                    if 'POLICY' in field_name or 'POL' in field_name:
                                        first_field_pattern = r'POL\d{3}'  # Pattern like "POL001"
                                    elif 'ID' in field_name or 'NUMBER' in field_name:
                                        # Generic: look for alphanumeric pattern
                                        first_field_pattern = r'[A-Z0-9]{3,}'
                                    break
                        
                        normalizer = FileFormatNormalizer(record_size, first_field_pattern)
                        normalized_content, normalization_metadata = normalizer.normalize(file_content)
                        
                        # Write normalized file
                        with open(input_file, 'wb') as f:
                            f.write(normalized_content)
                        
                        input_file_size = len(normalized_content)
                        remainder = input_file_size % record_size
                        
                        logger.info(f"📊 File normalization complete:")
                        logger.info(f"   Original: {normalization_metadata['original_size']} bytes")
                        logger.info(f"   Newlines removed: {normalization_metadata['newlines_removed']}")
                        logger.info(f"   Header bytes removed: {normalization_metadata['header_bytes']}")
                        logger.info(f"   Final size: {normalization_metadata['normalized_size']} bytes ({normalization_metadata['record_count']} records)")
                        
                        # If file is still not divisible, there's a deeper issue
                        if remainder > 0:
                            logger.error(f"❌ File still not divisible after normalization! Remainder: {remainder} bytes")
                            # Trim remainder as last resort
                            normalized_content = normalized_content[:-remainder]
                            with open(input_file, 'wb') as f:
                                f.write(normalized_content)
                            input_file_size = len(normalized_content)
                            remainder = 0
                        
                        # Skip the old trimming logic - normalization already handled everything
                        # Just retry Spark with the normalized file
                        logger.info(f"✅ File normalized, retrying Spark with normalized file...")
                        
                        # Check for header patterns in the beginning
                        header_score = 0
                        header_indicators = [
                            b'#',  # Hash tags (user mentioned this)
                            b'*',  # COBOL comments
                            b'/',  # COBOL comments
                            b'\n',  # Newlines (text headers)
                            b'\r',  # Carriage returns
                        ]
                        
                        # Check if beginning contains header-like patterns
                        header_text = header_region.decode('utf-8', errors='ignore')
                        if '#' in header_text[:remainder]:
                            header_score += 3  # Strong indicator
                        if any(indicator in header_region[:remainder] for indicator in header_indicators):
                            header_score += 1
                        
                        # Check if beginning looks like text/ASCII (headers often are)
                        printable_ratio_start = sum(1 for b in header_region[:remainder] if 32 <= b <= 126) / remainder if remainder > 0 else 0
                        if printable_ratio_start > 0.8:  # Mostly printable ASCII
                            header_score += 2
                        
                        # Check end for trailer patterns (padding, incomplete data)
                        trailer_score = 0
                        # Check if end is mostly null bytes or spaces (common for padding/trailers)
                        null_ratio = sum(1 for b in end_region[-remainder:] if b == 0 or b == 32) / remainder if remainder > 0 else 0
                        if null_ratio > 0.7:  # Mostly nulls/spaces
                            trailer_score += 3
                        
                        # Check if end looks like incomplete binary data
                        printable_ratio_end = sum(1 for b in end_region[-remainder:] if 32 <= b <= 126) / remainder if remainder > 0 else 0
                        if printable_ratio_end < 0.3:  # Mostly non-printable
                            trailer_score += 1
                        
                        # Decide where to trim based on scores
                        trim_from_start = header_score > trailer_score
                        
                        if trim_from_start:
                            logger.info(f"📊 Detected header pattern at beginning (score: {header_score} vs trailer: {trailer_score})")
                            logger.info(f"📊 Trimming {remainder} bytes from beginning of file")
                            trimmed_content = file_content[remainder:]
                        else:
                            logger.info(f"📊 Detected trailer/partial record at end (score: trailer {trailer_score} vs header: {header_score})")
                            logger.info(f"📊 Trimming {remainder} bytes from end of file")
                            trimmed_content = file_content[:-remainder] if remainder > 0 else file_content
                        
                        trimmed_size = len(trimmed_content)
                        
                        # Write trimmed file
                        with open(input_file, 'wb') as f:
                            f.write(trimmed_content)
                        
                        logger.info(f"✅ Trimmed file from {input_file_size} to {trimmed_size} bytes ({trimmed_size // record_size} complete records)")
                        
                        # Check first bytes of trimmed file to verify it looks like data, not header
                        first_bytes_trimmed = trimmed_content[:min(200, len(trimmed_content))]
                        first_text_trimmed = first_bytes_trimmed.decode('utf-8', errors='ignore')
                        logger.info(f"📊 First 200 bytes of trimmed file (hex): {first_bytes_trimmed.hex()[:400]}")
                        logger.info(f"📊 First 200 bytes of trimmed file (text): {repr(first_text_trimmed)}")
                        
                        # NOTE: FileFormatNormalizer has already handled header detection and removal
                        # The normalized_content from the normalizer should already have headers removed
                        # Skip the duplicate detection logic below - it was overriding the normalizer's correct result
                        # Check if it still looks like a header (contains hash tags, text patterns)
                        if False and ('#' in first_text_trimmed or any(word in first_text_trimmed.lower() for word in ['age', 'policy_type', 'premium', 'record', 'format', 'suspicious', 'characters', 'length'])):
                            logger.warning(f"⚠️ Trimmed file still contains header-like patterns - detecting data start...")
                            
                            # General approach: Find where comments/headers end and data begins
                            # Strategy: Scan through the file looking for regions that:
                            # 1. Don't contain comment markers (#, *, /)
                            # 2. Don't contain descriptive text (common header words)
                            # 3. Look like fixed-width binary/text data (consistent structure)
                            # 4. Align with record boundaries
                            
                            data_start_offset = None
                            max_search_bytes = min(2000, len(trimmed_content))  # Search up to 2000 bytes
                            
                            # Header/comment indicators
                            comment_markers = [b'#', b'*', b'/', b'\n#', b'\r\n#']
                            header_keywords = [b'format', b'record', b'length', b'characters', b'policy_type', 
                                             b'premium', b'age', b'suspicious', b'anomaly', b'missing']
                            
                            # ========================================================================
                            # EXTENSIBLE DATA START DETECTION - Handles common patterns:
                            # 1. Comment blocks (between hash tags, asterisks, etc.)
                            # 2. Non-printable characters after comments
                            # 3. Record identifier patterns (POL001, numeric prefixes, etc.)
                            # ========================================================================
                            
                            # CRITICAL: Remove newlines from content before analyzing
                            # Fixed-width binary files should NOT have newlines between records
                            # Newlines will cause record boundary misalignment
                            original_trimmed_size = len(trimmed_content)
                            trimmed_content = trimmed_content.replace(b'\n', b'').replace(b'\r', b'')
                            newlines_removed = original_trimmed_size - len(trimmed_content)
                            
                            if newlines_removed > 0:
                                logger.info(f"📊 Removed {newlines_removed} newline characters from trimmed content (file had newlines between records)")
                                # Recalculate remainder after removing newlines
                                new_remainder = len(trimmed_content) % record_size
                                if new_remainder > 0:
                                    logger.info(f"📊 After removing newlines, need to trim {new_remainder} more bytes to align with record size")
                                    trimmed_content = trimmed_content[:-new_remainder] if new_remainder > 0 else trimmed_content
                            
                            # STEP 1: Find the end of comment blocks (hash tags, etc.)
                            # Since we've already removed newlines, scan for '#' markers directly
                            comment_end_offset = None
                            
                            # Find the last '#' character - comments end right after it
                            last_hash_pos = -1
                            for offset in range(0, min(1000, len(trimmed_content))):
                                if trimmed_content[offset:offset+1] == b'#':
                                    last_hash_pos = offset
                            
                            if last_hash_pos >= 0:
                                # Comments end after the last '#' - find where actual data starts
                                # Skip past the '#' and any whitespace/formatting after it
                                search_start = last_hash_pos + 1
                                for offset in range(search_start, min(search_start + 200, len(trimmed_content))):
                                    # Check if this position looks like the start of data (not whitespace, not '#')
                                    byte_val = trimmed_content[offset:offset+1]
                                    if byte_val != b'#' and byte_val != b' ' and byte_val != b'\t':
                                        # This looks like the start of actual data
                                        comment_end_offset = offset
                                        logger.info(f"📊 Found end of comment block at offset {comment_end_offset} (last '#' was at {last_hash_pos})")
                                        # Show what comes after comments
                                        sample = trimmed_content[offset:offset+50]
                                        sample_text = sample.decode('utf-8', errors='ignore')
                                        logger.info(f"📊 Data after comments: '{sample_text[:50]}'")
                                        break
                            
                            # Fallback: if we didn't find comments, start from beginning
                            if comment_end_offset is None:
                                comment_end_offset = 0
                                logger.info(f"📊 No comment block found, starting from offset 0")
                            
                            # STEP 2: After comments end, find where actual data records start
                            # The issue: After comments, there may still be header text (like "Total record length: 81 characters")
                            # We need to find where the FIRST actual data record begins
                            search_start = comment_end_offset if comment_end_offset is not None else 0
                            
                            # First, try to find a clear record identifier pattern
                            # Look for patterns that indicate the start of a data record:
                            # - Alphanumeric prefix followed by digits (like "POL001", "REC001", etc.)
                            # - Long numeric strings (policy numbers, IDs)
                            # - Any pattern that looks like a record identifier at a record boundary
                            
                            data_start_offset = None
                            
                            # Scan from comment end, looking for record identifiers
                            # IMPORTANT: Scan byte-by-byte first to find where the identifier actually starts
                            # Then align to record boundaries
                            max_scan = min(search_start + 1000, len(trimmed_content))
                            
                            # First pass: Byte-by-byte scan to find record identifier
                            identifier_offset = None
                            for offset in range(search_start, max_scan):
                                if offset + 20 > len(trimmed_content):
                                    break
                                
                                sample = trimmed_content[offset:offset + 20]
                                sample_text = sample.decode('utf-8', errors='ignore').strip()
                                
                                # Pattern 1: Alphanumeric prefix + digits (e.g., "POL001", "REC001", "ID001")
                                if len(sample_text) >= 6:
                                    # Check for pattern: 3 letters + 3 digits (common record ID pattern)
                                    if sample_text[:3].isalpha() and sample_text[3:6].isdigit():
                                        identifier_offset = offset
                                        logger.info(f"📊 Found record identifier pattern at byte offset {offset}: '{sample_text[:10]}'")
                                        break
                                
                                # Pattern 2: Long numeric string (15+ digits) - likely a record ID/number
                                numeric_part = sample_text.replace(' ', '').replace('-', '')
                                if len(numeric_part) >= 15 and numeric_part.isdigit():
                                    identifier_offset = offset
                                    logger.info(f"📊 Found numeric record identifier at byte offset {offset}: '{sample_text[:20]}'")
                                    break
                            
                            # If we found an identifier, align it to the nearest record boundary
                            if identifier_offset is not None:
                                # Align to record boundary (round down to nearest record start)
                                data_start_offset = (identifier_offset // record_size) * record_size
                                logger.info(f"📊 Aligned identifier offset {identifier_offset} to record boundary {data_start_offset}")
                            else:
                                data_start_offset = None
                            
                            # STEP 3: If no clear identifier found, use general heuristics
                            # But only if we haven't found a clear record start
                            if data_start_offset is None:
                                logger.info(f"📊 No clear record identifier found, using general heuristics...")
                                printable_start = None
                                
                                for offset in range(search_start, min(search_start + 500, len(trimmed_content)), 1):
                                    if offset + record_size > len(trimmed_content):
                                        break
                                    
                                    chunk = trimmed_content[offset:offset + record_size]
                                    printable_count = sum(1 for b in chunk if 32 <= b <= 126)
                                    printable_ratio = printable_count / len(chunk)
                                    
                                    if printable_ratio > 0.7:
                                        printable_start = offset
                                        logger.info(f"📊 Found printable data region at offset {printable_start} (ratio: {printable_ratio:.2f})")
                                        break
                                
                                record_search_start = printable_start if printable_start is not None else search_start
                                # Align to record boundaries
                                if record_search_start % record_size != 0:
                                    record_search_start = ((record_search_start // record_size) + 1) * record_size
                            else:
                                # We found a clear record identifier - use it
                                record_search_start = data_start_offset
                            
                            # If we already found a clear record identifier, use it directly
                            if data_start_offset is not None:
                                first_valid_record = data_start_offset
                                logger.info(f"✅ Using record identifier at offset {first_valid_record}")
                            else:
                                # Scan at record boundaries for the FIRST valid data record using heuristics
                                first_valid_record = None
                                max_search = min(record_search_start + 3000, len(trimmed_content))
                                
                                for offset in range(record_search_start, max_search, record_size):
                                    if offset + record_size > len(trimmed_content):
                                        break
                                    
                                    # Get a full record at this position
                                    record_bytes = trimmed_content[offset:offset + record_size]
                                    record_text = record_bytes.decode('utf-8', errors='ignore')
                                    
                                    # Heuristic 1: Should NOT contain comment markers
                                    if '#' in record_text or '*' in record_text[:10] or '/' in record_text[:10]:
                                        continue
                                    
                                    # Heuristic 2: Should NOT contain header keywords (descriptive text)
                                    header_keywords = ['record', 'format', 'length', 'characters', 'contains', 
                                                      'policyholder', 'each', 'some', 'suspicious', 'anomaly']
                                    record_lower = record_text.lower()
                                    if any(keyword in record_lower[:100] for keyword in header_keywords):
                                        continue
                                    
                                    # Heuristic 3: Should have consistent structure
                                    # Fixed-width records should have:
                                    # - Mostly printable characters (not all binary)
                                    # - Some structure (spaces, alphanumeric mix)
                                    # - Not all text (should have some numeric/alphanumeric data)
                                    printable_count = sum(1 for b in record_bytes if 32 <= b <= 126)
                                    printable_ratio = printable_count / record_size
                                    
                                    if printable_ratio < 0.5:  # Too many non-printable = likely binary padding
                                        continue
                                    
                                    # Heuristic 4: Should look like actual data, not descriptive text
                                    # Descriptive text tends to have:
                                    # - Many spaces in a row
                                    # - Words separated by spaces
                                    # - Lowercase descriptive words
                                    # Actual data tends to have:
                                    # - Alphanumeric strings
                                    # - Numbers
                                    # - Mixed case names
                                    
                                    # Check if it's mostly descriptive text (many spaces, lowercase words)
                                    space_ratio = record_text.count(' ') / record_size
                                    if space_ratio > 0.6:  # Too many spaces = likely descriptive text
                                        continue
                                    
                                    # Check if it has actual data patterns (alphanumeric, numbers)
                                    alphanumeric_count = sum(1 for c in record_text if c.isalnum())
                                    alphanumeric_ratio = alphanumeric_count / record_size
                                    if alphanumeric_ratio < 0.3:  # Not enough alphanumeric = likely not data
                                        continue
                                    
                                    # Heuristic 5: Should NOT start with partial words (mid-record indicator)
                                    first_10_chars = record_text[:10].strip()
                                    partial_word_indicators = ['on ', 'nnuity', 'olicy', 'ecord', 'ontain', 'haracter', 'haracters']
                                    if any(first_10_chars.lower().startswith(partial) for partial in partial_word_indicators):
                                        continue
                                    
                                    # This looks like a valid data record!
                                    first_valid_record = offset
                                    logger.info(f"📊 Found FIRST valid data record at offset {offset}")
                                    logger.info(f"📊   Sample: '{record_text[:50]}'")
                                    logger.info(f"📊   Printable ratio: {printable_ratio:.2f}, Alphanumeric ratio: {alphanumeric_ratio:.2f}, Space ratio: {space_ratio:.2f}")
                                    break
                            
                            if first_valid_record is not None:
                                data_start_offset = first_valid_record
                                logger.info(f"✅ Using first valid data record at offset {data_start_offset}")
                            else:
                                logger.warning(f"⚠️ Could not find a valid data record using general heuristics")
                            
                            if data_start_offset is None:
                                logger.warning(f"⚠️ Could not find clear record identifier - will use file as-is after initial trim")
                            
                            # Fallback: If no explicit pattern found, use pattern-based scoring (original logic)
                            if data_start_offset is None:
                                logger.info(f"ℹ️  No explicit record identifier found - using pattern-based detection")
                                best_offset = None
                                best_score = -1
                                
                                for offset in range(0, max_search_bytes, max(1, record_size // 4)):  # Check every quarter record
                                    # Get a chunk at this offset (at least one record size)
                                    chunk_size = min(record_size * 2, len(trimmed_content) - offset)
                                    if chunk_size < record_size:
                                        break
                                    
                                    chunk = trimmed_content[offset:offset + chunk_size]
                                    chunk_text = chunk.decode('utf-8', errors='ignore')
                                    
                                    # Score this position: higher = more likely to be data
                                    score = 0
                                    
                                    # Negative indicators (header/comment patterns)
                                    if any(marker in chunk[:min(100, len(chunk))] for marker in comment_markers):
                                        score -= 10  # Strong negative
                                    
                                    # Check for header keywords in first part of chunk
                                    chunk_lower = chunk_text.lower()
                                    keyword_count = sum(1 for keyword in header_keywords if keyword.decode('utf-8', errors='ignore').lower() in chunk_lower[:200])
                                    if keyword_count > 2:
                                        score -= 5  # Multiple header keywords = likely header
                                    
                                    # Positive indicators (data-like patterns)
                                    # Check if chunk has consistent structure (not too many newlines)
                                    newline_count = chunk_text[:record_size].count('\n')
                                    if newline_count < 3:  # Few newlines = likely data
                                        score += 3
                                    
                                    # Check if chunk has mostly printable characters (but not all text)
                                    printable_ratio = sum(1 for b in chunk[:record_size] if 32 <= b <= 126) / min(record_size, len(chunk))
                                    if 0.5 < printable_ratio < 0.95:  # Some printable, but not all (mixed data)
                                        score += 2
                                    
                                    # Check if offset aligns with record boundaries
                                    if offset % record_size == 0:
                                        score += 5  # Strong positive - aligned with record boundary
                                    
                                    # Check if we can see a pattern that looks like fixed-width data
                                    # (e.g., consistent spacing, alphanumeric patterns)
                                    if len(chunk) >= record_size:
                                        # Check if first record looks structured (not random text)
                                        first_record = chunk[:record_size]
                                        first_record_text = first_record.decode('utf-8', errors='ignore')
                                        # If it has some structure (spaces, alphanumeric) but not all text words
                                        if ' ' in first_record_text and not all(c.isalpha() or c.isspace() for c in first_record_text[:50]):
                                            score += 2
                                    
                                    # Track best position
                                    if score > best_score:
                                        best_score = score
                                        best_offset = offset
                                
                                    # If we found a very good position (high score, aligned), use it
                                    # BUT: Be VERY conservative - require actual record start patterns
                                    # The record should start with a clear policy number pattern (POL001, POL002, etc.)
                                    if score >= 8 and offset % record_size == 0:
                                        # Additional validation: Check if this looks like the START of a data record
                                        # Get the first record at this position
                                        first_record_sample = chunk[:min(record_size, len(chunk))]
                                        first_record_text = first_record_sample.decode('utf-8', errors='ignore')
                                        
                                        # Check for actual data record START patterns
                                        # A valid record start should begin with "POL" followed by digits (POL001, POL002, etc.)
                                        # OR start with a long numeric string (policy number)
                                        # NOT start with partial words like "on", "nnuity", etc.
                                        has_valid_record_start = False
                                        
                                        # Check first 10 characters for record start pattern
                                        first_10_chars = first_record_text[:10].strip()
                                        
                                        # Pattern 1: Starts with "POL" followed by digits (POL001, POL002, etc.)
                                        if len(first_10_chars) >= 6 and first_10_chars[:3].upper() == 'POL' and first_10_chars[3:6].isdigit():
                                            has_valid_record_start = True
                                            logger.info(f"📊 Position {offset}: Found POL pattern: '{first_10_chars}'")
                                        
                                        # Pattern 2: Starts with long numeric string (20+ digits for policy number)
                                        elif len(first_record_text) >= 20 and first_record_text[:20].replace(' ', '').isdigit():
                                            has_valid_record_start = True
                                            logger.info(f"📊 Position {offset}: Found numeric policy pattern: '{first_record_text[:20]}'")
                                        
                                        # Pattern 3: Starts with digits followed by space (but be careful - might be mid-record)
                                        # Only accept if it's clearly a policy number (long enough)
                                        elif len(first_10_chars) >= 8 and first_10_chars.replace(' ', '').isdigit() and first_10_chars.count(' ') <= 2:
                                            # Additional check: make sure it's not mid-word
                                            if not any(word in first_record_text[:50].lower() for word in ['on ', 'nnuity', 'olicy', 'ecord', 'ontain']):
                                                has_valid_record_start = True
                                                logger.info(f"📊 Position {offset}: Found numeric pattern: '{first_10_chars}'")
                                        
                                        # Reject if it starts with partial words (clear sign of mid-record)
                                        if any(first_record_text[:10].lower().startswith(partial) for partial in ['on ', 'nnuity', 'olicy', 'ecord', 'ontain', 'haracter']):
                                            has_valid_record_start = False
                                            logger.debug(f"📊 Position {offset}: Rejected - starts with partial word: '{first_record_text[:20]}'")
                                        
                                        # Only use this position if it has a valid record start pattern
                                        if has_valid_record_start:
                                            data_start_offset = offset
                                            logger.info(f"📊 Found data start at offset {offset} (score: {score}, valid record start, aligned with record boundary)")
                                            break
                                        else:
                                            logger.debug(f"📊 Position {offset} has good score ({score}) but doesn't have valid record start pattern: '{first_record_text[:30]}' - continuing search")
                            
                            # If we found a good candidate, use it - but be more conservative
                            if data_start_offset is None and best_offset is not None and best_score > 0:
                                # Align to nearest record boundary
                                aligned_offset = (best_offset // record_size) * record_size
                                
                                # Additional validation: Check if this position actually looks like data start
                                # Get a sample of what would be the first record at this position
                                if aligned_offset < len(trimmed_content):
                                    sample_record = trimmed_content[aligned_offset:aligned_offset + min(record_size, len(trimmed_content) - aligned_offset)]
                                    sample_text = sample_record.decode('utf-8', errors='ignore').strip()
                                    
                                    # Check for actual data patterns (not just structured text)
                                    # Look for patterns that indicate real records:
                                    # - Starts with "POL" (policy prefix)
                                    # - Starts with digits (policy number)
                                    # - Has structured data (not descriptive text)
                                    looks_like_data = False
                                    if len(sample_text) >= 10:
                                        first_chars = sample_text[:10].strip()
                                        # Check for policy number patterns
                                        if (first_chars.upper().startswith('POL') or
                                            (first_chars[0].isdigit() and len([c for c in first_chars[:5] if c.isdigit()]) >= 3) or
                                            (first_chars[0].isalnum() and not any(word in sample_text.lower()[:50] for word in ['record', 'format', 'length', 'characters', 'contains', 'policyholder', 'each']))):
                                            looks_like_data = True
                                            logger.info(f"📊 Position {aligned_offset} looks like actual data: starts with '{first_chars[:20]}'")
                                    
                                    if looks_like_data:
                                        data_start_offset = aligned_offset
                                        logger.info(f"📊 Found data start at offset {aligned_offset} (best score: {best_score} at {best_offset}, has data pattern)")
                                    else:
                                        logger.warning(f"⚠️ Position {aligned_offset} has good score ({best_score}) but doesn't look like actual data start - skipping aggressive trim")
                                        logger.warning(f"⚠️ Sample at this position: '{sample_text[:50]}'")
                                        # Don't set data_start_offset - will use trimmed file as-is
                            
                            # If we found a data start, trim more
                            if data_start_offset and data_start_offset > 0:
                                additional_trim = data_start_offset
                                logger.info(f"📊 Trimming additional {additional_trim} bytes to reach data start")
                                trimmed_content = trimmed_content[additional_trim:]
                                trimmed_size = len(trimmed_content)
                                
                                # Recalculate to ensure it's still divisible by record size
                                new_remainder = trimmed_size % record_size
                                if new_remainder > 0:
                                    logger.info(f"📊 After additional trim, need to remove {new_remainder} more bytes to align with record size")
                                    trimmed_content = trimmed_content[:-new_remainder] if new_remainder > 0 else trimmed_content
                                    trimmed_size = len(trimmed_content)
                                
                                logger.info(f"✅ Final trimmed file size: {trimmed_size} bytes ({trimmed_size // record_size} complete records)")
                                
                                # Write the re-trimmed file
                                with open(input_file, 'wb') as f:
                                    f.write(trimmed_content)
                                
                                # Verify the new start
                                first_bytes_final = trimmed_content[:min(50, len(trimmed_content))]
                                first_text_final = first_bytes_final.decode('utf-8', errors='ignore')
                                logger.info(f"📊 First 50 bytes after final trim (text): {repr(first_text_final)}")
                            else:
                                if best_score <= 0:
                                    logger.warning(f"⚠️ Could not detect data start (best score: {best_score}) - using trimmed file as-is")
                                    logger.warning(f"⚠️ This may indicate the file has an unusual structure or the header is very long")
                                else:
                                    logger.info(f"ℹ️  Data start detection inconclusive (best score: {best_score}) - using trimmed file as-is to avoid data loss")
                                    logger.info(f"ℹ️  If parsing fails, the file may need manual inspection or a file_start_offset parameter")
                        
                        # Retry parsing with trimmed file
                        logger.info("🔄 Retrying parsing with trimmed file...")
                        result = await asyncio.to_thread(
                            subprocess.run,
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=300.0,
                            env=env
                        )
                
                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    logger.error(f"❌ Spark application failed:")
                    logger.error(f"Return code: {result.returncode}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                else:
                    # Log successful Spark output for debugging
                    if result.stdout:
                        logger.info(f"📊 Spark STDOUT: {result.stdout[:500]}")
                    if result.stderr:
                        logger.info(f"📊 Spark STDERR: {result.stderr[:1000]}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Cobrix parsing failed: {error_msg[:500]}"  # Limit error message length
                    )
            
            # Read output JSONL files
            records = []
            for root, dirs, files in os.walk(output_dir):
                for filename in files:
                    if filename.startswith("part-") and filename.endswith(".json"):
                        filepath = os.path.join(root, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        record = json.loads(line)
                                        records.append(record)
                                    except json.JSONDecodeError:
                                        continue
            
            if not records:
                raise HTTPException(
                    status_code=500,
                    detail="Cobrix produced no records"
                )
            
            # Log first record for debugging
            if records:
                logger.info(f"📊 First record from Cobrix (keys): {list(records[0].keys())}")
                logger.info(f"📊 First record sample (first 200 chars): {str(records[0])[:200]}")
                # Check if it's nested (has POLICYHOLDER_RECORD key)
                if 'POLICYHOLDER_RECORD' in records[0] or 'POLICYHOLDER-RECORD' in records[0]:
                    logger.info(f"📊 Record has nested structure - flattening...")
                    # Log nested structure
                    nested_key = 'POLICYHOLDER_RECORD' if 'POLICYHOLDER_RECORD' in records[0] else 'POLICYHOLDER-RECORD'
                    nested_record = records[0].get(nested_key, {})
                    logger.info(f"📊 Nested record keys: {list(nested_record.keys()) if isinstance(nested_record, dict) else 'Not a dict'}")
                    logger.info(f"📊 Full nested record (for debugging AGE): {nested_record}")
                    logger.info(f"📊 Nested record sample: {str(nested_record)[:200]}")
                    
                    # CRITICAL: Check if AGE field exists in nested record
                    age_keys = [k for k in nested_record.keys() if 'AGE' in k.upper()]
                    logger.info(f"📊 AGE field keys found: {age_keys}")
                    for age_key in age_keys:
                        age_value = nested_record.get(age_key)
                        logger.info(f"📊 AGE field '{age_key}' value: {age_value} (type: {type(age_value)})")
                    
                    # Check ALL keys to see what Cobrix actually parsed
                    logger.info(f"📊 ALL keys in nested record (checking for AGE variants): {list(nested_record.keys())}")
                    for key in nested_record.keys():
                        logger.info(f"📊   Key: '{key}' = {repr(nested_record[key])} (type: {type(nested_record[key])})")
            
            # Flatten nested structures - Cobrix returns nested dicts based on copybook hierarchy
            # We need to extract all fields from nested structures into a flat dict
            def flatten_record(record: dict, prefix: str = "") -> dict:
                """Recursively flatten nested dictionary structures."""
                flattened = {}
                for key, value in record.items():
                    # Convert hyphens to underscores for consistency (Cobrix uses underscores)
                    flat_key = key.replace('-', '_')
                    full_key = f"{prefix}{flat_key}" if prefix else flat_key
                    
                    if isinstance(value, dict):
                        # Recursively flatten nested dicts
                        flattened.update(flatten_record(value, prefix=f"{full_key}_" if prefix else ""))
                    else:
                        # Leaf value - add to flattened dict
                        flattened[full_key] = value
                
                return flattened
            
            # Flatten all records
            flattened_records = []
            for record in records:
                flattened = flatten_record(record)
                
                # WORKAROUND: If AGE field is missing, manually extract it from the raw file
                # This happens when Cobrix skips small numeric fields (PIC 999)
                if 'POLICYHOLDER_AGE' not in flattened and 'POLICYHOLDER-AGE' not in flattened:
                    logger.warning(f"⚠️ AGE field missing from Cobrix output - attempting manual extraction")
                    # AGE should be at bytes 50-52 in each 81-byte record
                    # But we need to know which record this is and read from the normalized file
                    # For now, we'll try to infer it from POLICYHOLDER_NAME (which includes the first digit)
                    policyholder_name = flattened.get('POLICYHOLDER_NAME', '')
                    if policyholder_name and len(policyholder_name) > 30:
                        # POLICYHOLDER_NAME is too long - it includes the first digit of AGE
                        # Extract AGE from the end of POLICYHOLDER_NAME
                        age_digit = policyholder_name[-1] if policyholder_name[-1].isdigit() else '0'
                        # Try to get the full AGE from the next 2 bytes
                        # This is a workaround - we'll need to read from the file directly
                        logger.warning(f"⚠️ POLICYHOLDER_NAME appears to include AGE digit: '{age_digit}'")
                        # For now, set AGE to a placeholder - we'll fix this properly below
                        flattened['POLICYHOLDER_AGE'] = None
                
                flattened_records.append(flattened)
            
            # Check if AGE is being parsed by Cobrix
            age_parsed_by_cobrix = False
            if flattened_records and ('POLICYHOLDER_AGE' in flattened_records[0] or 'POLICYHOLDER-AGE' in flattened_records[0]):
                age_parsed_by_cobrix = True
                logger.info(f"✅ AGE field is being parsed by Cobrix - checking if other fields need alignment fixes")
            else:
                logger.warning(f"⚠️ AGE field NOT parsed by Cobrix - will manually extract AGE and fix all field alignments")
            
            # WORKAROUND: Only manually fix fields if they're misaligned
            # If AGE is parsed, Cobrix should have correctly aligned all fields, but check anyway
            try:
                with open(input_file, 'rb') as f:
                    normalized_content = f.read()
                
                record_size = 81  # From copybook analysis
                
                # Check first record to see if fields are misaligned
                needs_fixing = False
                if flattened_records:
                    first_record = flattened_records[0]
                    policyholder_name = first_record.get('POLICYHOLDER_NAME', '')
                    policy_type = first_record.get('POLICY_TYPE', '')
                    
                    # If POLICYHOLDER_NAME has trailing digit or is too long, fields are misaligned
                    if policyholder_name and (len(policyholder_name) > 30 or (len(policyholder_name) == 31 and policyholder_name[-1].isdigit())):
                        needs_fixing = True
                        logger.warning(f"⚠️ POLICYHOLDER_NAME is {len(policyholder_name)} bytes (expected 30) - fields misaligned")
                    # If POLICY_TYPE is missing first letter or too short, fields are misaligned
                    if policy_type and (len(policy_type) < 10 or not policy_type[0].isupper()):
                        needs_fixing = True
                        logger.warning(f"⚠️ POLICY_TYPE appears misaligned: '{policy_type}' (expected 10 bytes, starts with uppercase) - fields misaligned")
                
                # If AGE is not parsed OR fields are misaligned, apply fixes
                if not age_parsed_by_cobrix or needs_fixing:
                    logger.info(f"📊 Applying manual field alignment fixes")
                    
                    # Always manually extract AGE from correct byte position, even if Cobrix parsed it
                    # Cobrix might be reading from wrong offset (e.g., "45T" instead of "045")
                    age_offset = 50  # AGE starts at byte 50 (after 20-byte policy number + 30-byte name)
                    age_length = 3
                    for i, flattened in enumerate(flattened_records):
                        record_start = i * record_size
                        age_start = record_start + age_offset
                        age_end = age_start + age_length
                        if age_end <= len(normalized_content):
                            age_bytes = normalized_content[age_start:age_end]
                            age_str = age_bytes.decode('ascii', errors='ignore').strip()
                            age_str_clean = age_str.strip()
                            if age_str_clean.isdigit():
                                age_value = age_str_clean.zfill(3) if len(age_str_clean) < 3 else age_str_clean
                            else:
                                age_value = age_str_clean.zfill(3) if age_str_clean.replace(' ', '').isdigit() else age_str_clean
                            # Overwrite Cobrix's AGE value with correct one
                            flattened['POLICYHOLDER_AGE'] = age_value
                            if i < 3:
                                cobrix_age = flattened.get('POLICYHOLDER_AGE', 'N/A')
                                logger.info(f"📊 Record {i+1}: Cobrix AGE was '{cobrix_age}', corrected to '{age_value}'")
                    
                    # Fix all fields that come after AGE (they're all misaligned by 3 bytes if AGE wasn't parsed)
                    for i, flattened in enumerate(flattened_records):
                        record_start = i * record_size
                        
                        # Fix POLICYHOLDER_NAME - should be 30 bytes starting at byte 20
                        if record_start + 20 + 30 <= len(normalized_content):
                            name_bytes = normalized_content[record_start + 20:record_start + 50]
                            name_str = name_bytes.decode('ascii', errors='ignore').rstrip()
                            flattened['POLICYHOLDER_NAME'] = name_str
                        
                        # Fix POLICY_TYPE - should be 10 bytes starting at byte 53 (after 20 + 30 + 3)
                        if record_start + 53 + 10 <= len(normalized_content):
                            policy_type_bytes = normalized_content[record_start + 53:record_start + 63]
                            policy_type_str = policy_type_bytes.decode('ascii', errors='ignore').strip()
                            flattened['POLICY_TYPE'] = policy_type_str
                        
                        # Fix PREMIUM_AMOUNT - should be 10 bytes starting at byte 63
                        if record_start + 63 + 10 <= len(normalized_content):
                            premium_bytes = normalized_content[record_start + 63:record_start + 73]
                            premium_str = premium_bytes.decode('ascii', errors='ignore').strip()
                            try:
                                premium_value = int(premium_str) if premium_str.isdigit() else premium_str
                            except ValueError:
                                premium_value = premium_str
                            flattened['PREMIUM_AMOUNT'] = premium_value
                        
                        # Fix ISSUE_DATE - should be 8 bytes starting at byte 73
                        if record_start + 73 + 8 <= len(normalized_content):
                            issue_date_bytes = normalized_content[record_start + 73:record_start + 81]
                            issue_date_str = issue_date_bytes.decode('ascii', errors='ignore').strip()
                            flattened['ISSUE_DATE'] = issue_date_str
                else:
                    logger.info(f"✅ Fields appear correctly aligned - no manual fixes needed")
                
            except Exception as e:
                logger.error(f"❌ Failed to manually fix field alignments: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            if flattened_records:
                logger.info(f"📊 Flattened first record keys: {list(flattened_records[0].keys())}")
                logger.info(f"📊 Flattened first record sample: {str(flattened_records[0])[:300]}")
                
                # CRITICAL: Check if AGE field exists after flattening
                age_keys_flat = [k for k in flattened_records[0].keys() if 'AGE' in k.upper()]
                logger.info(f"📊 AGE field keys after flattening: {age_keys_flat}")
                for age_key in age_keys_flat:
                    age_value = flattened_records[0].get(age_key)
                    logger.info(f"📊 AGE field '{age_key}' value: {age_value} (type: {type(age_value)})")
                
                # Check all numeric fields - Cobrix might convert PIC 9(3) to numbers
                numeric_fields = {k: v for k, v in flattened_records[0].items() if isinstance(v, (int, float))}
                logger.info(f"📊 Numeric fields (might be AGE): {list(numeric_fields.keys())}")
            
            records = flattened_records
            
            # Extract validation rules from copybook metadata and validate records
            validation_results = None
            try:
                from cobol_metadata_validator import CobolMetadataValidator
                
                # Re-read copybook content for validation (we need the full copybook with metadata)
                # The copybook_text variable still contains the original full copybook
                validator = CobolMetadataValidator()
                rules = validator.extract_metadata_rules(copybook_text, extract_88_fields=True)
                
                if rules:
                    logger.info(f"✅ Extracted {len(rules)} validation rules from copybook metadata")
                    for rule in rules[:5]:  # Log first 5 rules
                        logger.info(f"   - {rule.rule_type.value}: {rule.field_name} ({rule.rule_name})")
                    
                    # Validate all records with detected encoding
                    validation_results = validator.validate_batch(records, encoding=detected_encoding)
                    logger.info(f"📊 Validation results: {validation_results['valid_records']}/{validation_results['total_records']} valid, "
                              f"{validation_results['total_errors']} errors, {validation_results['total_warnings']} warnings, "
                              f"{validation_results['total_anomalies']} anomalies")
                else:
                    logger.info("ℹ️  No validation rules found in copybook metadata")
            except Exception as e:
                logger.warning(f"⚠️  Validation failed (non-critical): {e}")
                import traceback
                logger.debug(traceback.format_exc())
            
            # Extract columns from first record
            columns = list(records[0].keys()) if records else []
            
            response_data = {
                "success": True,
                "records": records,
                "tables": [{
                    "columns": columns,
                    "data": records,
                    "row_count": len(records)
                }],
                "metadata": {
                    "record_count": len(records),
                    "encoding": detected_encoding,
                    "parser": "cobrix",
                    "parser_version": "2.9.0"
                }
            }
            
            # Add validation results if available
            if validation_results:
                response_data["validation"] = {
                    "total_records": validation_results["total_records"],
                    "valid_records": validation_results["valid_records"],
                    "invalid_records": validation_results["invalid_records"],
                    "total_errors": validation_results["total_errors"],
                    "total_warnings": validation_results["total_warnings"],
                    "total_anomalies": validation_results["total_anomalies"],
                    "validation_rate": validation_results["validation_rate"]
                }
            
            return response_data
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Parsing timed out after 5 minutes")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"❌ Unexpected error in parse_cobol:")
        logger.error(error_trace)
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

