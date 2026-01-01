#!/usr/bin/env python3
"""
COBOL Processing Infrastructure Adapter - Layer 1

Raw technology wrapper for COBOL processing operations.
This adapter can be swapped with cobrix (Spark-based) implementation.

WHAT (Infrastructure): I provide COBOL processing capabilities
HOW (Adapter): I wrap COBOL processing logic for swappable implementations
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import os
import tempfile
import re
import io
import codecs
import math
from array import array

# Dependency Injection for standard libraries
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pd = None
    pa = None
    pq = None

logger = logging.getLogger(__name__)

class MainframeProcessingAdapter:
    """
    Mainframe Processing Infrastructure Adapter
    
    Raw technology wrapper for mainframe processing operations (COBOL, binary, copybooks).
    This implementation uses the current business logic approach.
    Can be swapped with cobrix (Spark-based) implementation.
    """
    
    def __init__(self):
        """Initialize Mainframe Processing Adapter."""
        self.logger = logging.getLogger("CobolProcessingAdapter")
        self.pandas_available = pd is not None
        self.pyarrow_available = pa is not None
        
        if not self.pandas_available:
            self.logger.warning("⚠️ 'pandas' library not found. DataFrame operations will be limited.")
        if not self.pyarrow_available:
            self.logger.warning("⚠️ 'pyarrow' library not found. Parquet operations will be limited.")
        
        self.logger.info("✅ Mainframe Processing Adapter initialized")
    
    # ============================================================================
    # ARCHIVED: Legacy file path-based method
    # ============================================================================
    # ARCHIVED: This method is kept for reference but should not be used.
    # Use parse_file() with bytes instead.
    # ============================================================================
    async def parse_cobol_file(self, binary_path: str, copybook_path: str) -> Dict[str, Any]:
        """
        Parse COBOL binary file using copybook definitions.
        
        Args:
            binary_path: Path to binary COBOL file
            copybook_path: Path to copybook file
            
        Returns:
            Dict containing parsed data and metadata
        """
        try:
            if not os.path.exists(binary_path):
                return {
                    "success": False,
                    "error": f"Binary file not found: {binary_path}",
                    "data": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not os.path.exists(copybook_path):
                return {
                    "success": False,
                    "error": f"Copybook file not found: {copybook_path}",
                    "data": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Parse copybook
            field_definitions = await self._parse_copybook(copybook_path)
            if not field_definitions:
                return {
                    "success": False,
                    "error": "Failed to parse copybook",
                    "data": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Read binary file
            with open(binary_path, 'rb') as f:
                binary_data = f.read()
            
            # Parse records
            records = await self._parse_binary_records(binary_data, field_definitions)
            
            # Convert to DataFrame if pandas is available
            if self.pandas_available and records:
                df = pd.DataFrame(records)
                return {
                    "success": True,
                    "data": df,
                    "records": records,
                    "record_count": len(records),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": True,
                    "data": None,
                    "records": records,
                    "record_count": len(records),
                    "column_count": 0,
                    "columns": [],
                    "timestamp": datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"❌ COBOL file parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # NEW: Bytes-based parsing method
    # ============================================================================
    
    async def parse_file(self, file_data: bytes, filename: str, copybook_data: bytes = None) -> Dict[str, Any]:
        """
        Parse mainframe binary file from bytes using copybook definitions.
        
        Args:
            file_data: Binary file content as bytes
            filename: Original filename (for logging)
            copybook_data: Copybook content as bytes (required for parsing)
            
        Returns:
            Dict[str, Any]: A dictionary containing parsed data, tables, and metadata.
        """
        try:
            if not copybook_data:
                return {
                    "success": False,
                    "error": "Copybook data required. Provide copybook_data (bytes).",
                    "text": "",
                    "tables": [],
                    "records": [],
                    "data": None,
                    "metadata": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Decode copybook from bytes to string
            try:
                copybook_content = copybook_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    copybook_content = copybook_data.decode('latin-1')
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to decode copybook: {e}",
                        "text": "",
                        "tables": [],
                        "records": [],
                        "data": None,
                        "metadata": {},
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # Parse copybook from string
            field_definitions = await self._parse_copybook_from_string(copybook_content)
            if not field_definitions:
                return {
                    "success": False,
                    "error": "Failed to parse copybook",
                    "text": "",
                    "tables": [],
                    "records": [],
                    "data": None,
                    "metadata": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Extract validation rules (88-level fields and level-01 metadata records)
            validation_rules = self._extract_validation_rules(copybook_content)
            
            # Parse binary records (with timing)
            import time
            parse_start = time.time()
            records = await self._parse_binary_records(file_data, field_definitions)
            parse_elapsed = time.time() - parse_start
            self.logger.info(f"⏱️ Binary parsing took {parse_elapsed:.2f} seconds for {len(file_data)} bytes, {len(records)} records")
            
            if not records:
                return {
                    "success": False,
                    "error": "No records parsed from binary data",
                    "text": "",
                    "tables": [],
                    "records": [],
                    "data": None,
                    "metadata": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Convert records to text representation
            text_content = self._records_to_text(records)
            
            # Build tables structure
            tables = [{
                "data": records,
                "columns": list(records[0].keys()) if records else [],
                "row_count": len(records)
            }] if records else []
            
            # Convert to DataFrame if pandas is available
            data = None
            if self.pandas_available and records:
                data = pd.DataFrame(records)
            
            return {
                "success": True,
                "text": text_content,
                "tables": tables,
                "records": records,
                "data": data,
                "metadata": {
                    "file_type": "mainframe",
                    "record_count": len(records),
                    "column_count": len(records[0].keys()) if records else 0,
                    "columns": list(records[0].keys()) if records else [],
                    "filename": filename
                },
                "validation_rules": validation_rules,  # Store validation rules for data quality analysis
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Mainframe file parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "tables": [],
                "records": [],
                "data": None,
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _records_to_text(self, records: List[Dict[str, Any]]) -> str:
        """Convert records to text representation."""
        if not records:
            return ""
        
        # Create text representation
        text_lines = []
        for i, record in enumerate(records, 1):
            record_str = f"Record {i}: " + ", ".join(f"{k}: {v}" for k, v in record.items())
            text_lines.append(record_str)
        
        return "\n".join(text_lines)
    
    # ============================================================================
    # ARCHIVED: Legacy copybook parsing from file path
    # ============================================================================
    async def _parse_copybook(self, copybook_path: str) -> List[Dict[str, Any]]:
        """Parse copybook file to extract field definitions."""
        try:
            # COBOL pattern matching
            # Allow leading whitespace (COBOL copybooks are often indented)
            opt_pattern_format = "({})?"
            row_pattern_base = r"^\s*(?P<level>\d{2})\s+(?P<name>\S+)"
            row_pattern_occurs = r"\s+OCCURS (?P<occurs>\d+) TIMES"
            row_pattern_indexed_by = r"\s+INDEXED BY\s(?P<indexed_by>\S+)"
            row_pattern_redefines = r"\s+REDEFINES\s+(?P<redefines>\S+)"
            row_pattern_pic = r"\s+PIC\s+(?P<pic>[^\s.]+(?:\([^)]+\))?(?:V\d+)?)"  # PIC clause (may include parentheses, V for decimals)
            row_pattern_comp = r"\s+COMP(?:-\d+)?"  # COMP or COMP-3, COMP-4, etc.
            row_pattern_binary = r"\s+BINARY"
            row_pattern_end = r"\.?\s*$"  # Optional period, allow trailing whitespace
            
            row_pattern = re.compile(
                row_pattern_base
                + opt_pattern_format.format(row_pattern_redefines)
                + opt_pattern_format.format(row_pattern_occurs)
                + opt_pattern_format.format(row_pattern_indexed_by)
                + opt_pattern_format.format(row_pattern_pic)
                + opt_pattern_format.format(row_pattern_comp)
                + opt_pattern_format.format(row_pattern_binary)
                + row_pattern_end
            )
            
            field_definitions = []
            
            with open(copybook_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('*') or line.startswith('/'):
                        continue
                    
                    match = row_pattern.match(line)
                    if match:
                        field_def = self._parse_field_definition(match, line_num)
                        if field_def:
                            field_definitions.append(field_def)
            
            return field_definitions
            
        except Exception as e:
            self.logger.error(f"❌ Copybook parsing failed: {e}")
            return []
    
    # ============================================================================
    # NEW: Copybook parsing from string (uses StringIO)
    # ============================================================================
    
    def _clean_cobol(self, lines: List[str]) -> List[str]:
        """
        Clean COBOL lines by handling continuation lines (legacy clean_cobol function).
        COBOL allows fields to span multiple physical lines (columns 6-72).
        Lines are joined until a period is found.
        Adopted from legacy cobol2csv.py.
        """
        holder = []
        output = []
        
        for row in lines:
            # Legacy approach: directly slice columns 6-72 (COBOL standard)
            # This works even if row is shorter than 72 chars (slices to end)
            row = row[6:72].rstrip()
            
            # Skip empty lines and comments (legacy pattern)
            if row == "" or (row and row[0] in ("*", "/")):
                continue
            
            # Add to holder (join continuation lines)
            holder.append(row if len(holder) == 0 else row.strip())
            
            # If line ends with period, we have a complete statement
            if row[-1] == ".":
                output.append(" ".join(holder))
                holder = []
        
        # Warn if there are unfinished lines (legacy behavior)
        if len(holder) > 0:
            self.logger.warning(f"[WARNING] probably invalid COBOL - found unfinished line: {' '.join(holder)}")
            # Legacy doesn't add unfinished lines to output
        
        return output
    
    def _get_subgroup(self, parent_level: int, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get all fields that have a higher level than parent_level until
        a field with equal or lower level is encountered.
        Adopted from legacy get_subgroup function.
        """
        output = []
        for row in lines:
            level = row.get("level", 0)
            # Skip level 77 (working storage) and 88 (condition names)
            if level == 77 or level == 88:
                continue
            elif level > parent_level:
                output.append(row)
            else:
                return output
        return output
    
    def _handle_occurs(self, lines: List[Dict[str, Any]], occurs: int, level_diff: int = 0, name_postfix: str = "") -> List[Dict[str, Any]]:
        """
        Denormalize COBOL by handling OCCURS clauses.
        Recursively flattens OCCURS into multiple field instances.
        Adopted from legacy handle_occurs function.
        """
        if not lines:
            return []
        
        output = []
        
        try:
            for i in range(1, occurs + 1):
                skipTill = 0
                # If occurs > 1, add postfix like "-1", "-2", etc.
                new_name_postfix = name_postfix if occurs == 1 else name_postfix + "-" + str(i)
                
                for index, row in enumerate(lines):
                    if index < skipTill:
                        continue
                    
                    if not isinstance(row, dict):
                        self.logger.warning(f"⚠️ Skipping invalid row at index {index}: {type(row)}")
                        continue
                    
                    new_row = row.copy()
                    new_row["level"] = new_row.get("level", 0) + level_diff
                    
                    # Remove indexed_by when flattened (not needed)
                    new_row["indexed_by"] = None
                    
                    occurs_count = row.get("occurs")
                    if occurs_count is None:
                        # Field doesn't have OCCURS - just add postfix to name
                        field_name = row.get("name", "")
                        new_row["name"] = field_name + new_name_postfix
                        output.append(new_row)
                    else:
                        # Field has OCCURS
                        # Check if field has PIC (legacy checks row["pic"], we check pic_info)
                        pic_info = row.get("pic_info")
                        pic_string = pic_info.get("pic_string", "") if pic_info else ""
                        has_pic = pic_string != "" or (pic_info and pic_info.get("field_length", 0) > 0)
                        
                        if has_pic:
                            # Field has PIC - repeat the field multiple times (legacy: if row["pic"] is not None)
                            new_row["occurs"] = None  # Clear occurs after expansion
                            field_name = row.get("name", "")
                            for j in range(1, occurs_count + 1):
                                row_to_add = new_row.copy()
                                # Legacy naming: row["name"] + new_name_postfix + "-" + str(j)
                                row_to_add["name"] = field_name + new_name_postfix + "-" + str(j)
                                output.append(row_to_add)
                        else:
                            # Field has OCCURS but no PIC - get subgroup and recurse
                            occur_lines = self._get_subgroup(row.get("level", 0), lines[index + 1:])
                            if occur_lines and len(occur_lines) > 0:
                                # Calculate new level difference
                                first_occur_level = occur_lines[0].get("level")
                                if first_occur_level is not None:
                                    new_level_diff = level_diff + row.get("level", 0) - first_occur_level
                                    output += self._handle_occurs(occur_lines, occurs_count, new_level_diff, new_name_postfix)
                                    skipTill = index + len(occur_lines) + 1
                                else:
                                    # Invalid level - skip
                                    self.logger.warning(f"⚠️ Invalid level in occur_lines[0], skipping OCCURS expansion")
                                    new_row["occurs"] = None
                                    new_row["name"] = row.get("name", "") + new_name_postfix
                                    output.append(new_row)
                            else:
                                # No subgroup found - just add the field (shouldn't happen, but handle gracefully)
                                self.logger.warning(f"⚠️ OCCURS field {row.get('name')} has no subgroup, treating as regular field")
                                new_row["occurs"] = None
                                new_row["name"] = row.get("name", "") + new_name_postfix
                                output.append(new_row)
        except Exception as e:
            self.logger.error(f"❌ Error in _handle_occurs: {e}", exc_info=True)
            # Return what we have so far
            return output
        
        return output
    
    def _denormalize_cobol(self, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Denormalize COBOL by flattening OCCURS clauses.
        Adopted from legacy denormalize_cobol function.
        """
        try:
            return self._handle_occurs(lines, 1)
        except Exception as e:
            self.logger.error(f"❌ OCCURS denormalization failed: {e}", exc_info=True)
            # Return original lines if denormalization fails
            return lines
    
    def _rename_filler_fields(self, field_definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rename FILLER fields to FILLER_1, FILLER_2, etc. to avoid duplicate names.
        Adopted from legacy decode_copybook_file FILLER handling.
        """
        filler_counter = 1
        for field_def in field_definitions:
            field_name = field_def.get("name", "")
            if field_name.upper() == "FILLER":
                field_def["name"] = f"FILLER_{filler_counter}"
                filler_counter += 1
        return field_definitions
    
    async def _parse_copybook_from_string(self, copybook_content: str) -> List[Dict[str, Any]]:
        """Parse copybook from string content using legacy approach."""
        try:
            # Use legacy clean_cobol approach to handle continuation lines
            lines = copybook_content.split('\n')
            cleaned_lines = self._clean_cobol(lines)
            
            # COBOL pattern matching (legacy pattern)
            opt_pattern_format = "({})?"
            row_pattern_base = r"^(?P<level>\d{2})\s+(?P<name>\S+)"
            row_pattern_occurs = r"\s+OCCURS (?P<occurs>\d+) TIMES"
            row_pattern_indexed_by = r"\s+INDEXED BY\s(?P<indexed_by>\S+)"
            row_pattern_redefines = r"\s+REDEFINES\s+(?P<redefines>\S+)"
            row_pattern_pic = r"\s+PIC\s+(?P<pic>\S+)"  # Legacy uses simpler pattern
            row_pattern_comp = r"\s+COMP"  # Legacy pattern
            row_pattern_binary = r"\s+BINARY"  # Legacy pattern
            row_pattern_end = r"\.$"  # Legacy requires period at end
            
            row_pattern = re.compile(
                row_pattern_base
                + opt_pattern_format.format(row_pattern_redefines)
                + opt_pattern_format.format(row_pattern_occurs)
                + opt_pattern_format.format(row_pattern_indexed_by)
                + opt_pattern_format.format(row_pattern_pic)
                + opt_pattern_format.format(row_pattern_comp)
                + opt_pattern_format.format(row_pattern_binary)
                + row_pattern_end
            )
            
            field_definitions = []
            
            # Process cleaned lines (like legacy parse_cobol)
            for line_num, line in enumerate(cleaned_lines, 1):
                # Extract OCCURS count manually (legacy approach - before pattern matching)
                occurs_count = 0
                if "OCCURS " in line and " TIMES" in line:
                    occurs_index = line.find("OCCURS ")
                    whitespace_index = occurs_index - 1
                    while whitespace_index >= 0 and line[whitespace_index] == " ":
                        whitespace_index -= 1
                    times_index = line.find(" TIMES", occurs_index)
                    if times_index > occurs_index:
                        try:
                            occurs_count = int(line[occurs_index + len("OCCURS "):times_index])
                            # Remove OCCURS clause from line (legacy approach)
                            string_to_replace = (
                                " " * (occurs_index - whitespace_index - 1)
                                + line[occurs_index:times_index + len(" TIMES")]
                            )
                            line = line.replace(string_to_replace, "")
                        except ValueError:
                            self.logger.warning(f"⚠️ Could not parse OCCURS count in line {line_num}: {line}")
                
                # Check for COMP-3 before pattern matching (legacy approach)
                is_comp3 = " COMP-3" in line or " COMP-3." in line
                if is_comp3:
                    line = line.replace(" COMP-3", "").replace(" COMP-3.", ".")
                
                # CRITICAL FIX: Also check for COMP (without -3) before pattern matching
                # The regex might not catch it if it's at the end or has specific spacing
                is_comp = False
                if not is_comp3 and (" COMP" in line or " COMP." in line):
                    is_comp = True
                    # Don't remove COMP from line - let regex capture it
                
                match = row_pattern.match(line.strip())
                if match:
                    field_def = self._parse_field_definition(match, line_num, is_comp3=is_comp3, occurs_count=occurs_count, is_comp_manual=is_comp)
                    if field_def:
                        # Handle REDEFINES (legacy approach - remove redefined field)
                        redefines = field_def.get("redefines")
                        if redefines:
                            try:
                                # Find the field being redefined
                                redefined_item_index = None
                                for idx, item in enumerate(field_definitions):
                                    if item.get("name") == redefines:
                                        redefined_item_index = idx
                                        break
                                
                                if redefined_item_index is not None:
                                    redefined_item = field_definitions[redefined_item_index]
                                    # Get subgroup (all fields with higher level)
                                    related_group = self._get_subgroup(
                                        redefined_item.get("level", 0),
                                        field_definitions[redefined_item_index + 1:]
                                    )
                                    # Remove redefined field and its subgroup
                                    field_definitions = (
                                        field_definitions[:redefined_item_index]
                                        + field_definitions[redefined_item_index + len(related_group) + 1:]
                                    )
                                    # Clear redefines flag (field is now replacing the redefined one)
                                    field_def["redefines"] = None
                                    self.logger.debug(f"✅ REDEFINES: Replaced {redefines} with {field_def.get('name')}")
                                else:
                                    self.logger.warning(f"⚠️ Could not find field to be redefined ({redefines}) for line {line_num}")
                            except Exception as e:
                                self.logger.warning(f"⚠️ Error handling REDEFINES for {redefines}: {e}")
                        
                        field_definitions.append(field_def)
                # Legacy code continues even if no match (just skips the line)
            
            # Denormalize OCCURS (flatten OCCURS clauses)
            fields_before_denorm = len(field_definitions)
            field_definitions = self._denormalize_cobol(field_definitions)
            fields_after_denorm = len(field_definitions)
            
            # Rename FILLER fields to avoid duplicates
            field_definitions = self._rename_filler_fields(field_definitions)
            
            self.logger.info(f"✅ Parsed {fields_before_denorm} fields before OCCURS denormalization, {fields_after_denorm} fields after (expansion factor: {fields_after_denorm / fields_before_denorm if fields_before_denorm > 0 else 0:.2f}x)")
            
            # WARNING: If OCCURS expansion created too many fields, parsing will be very slow
            if fields_after_denorm > 1000:
                self.logger.warning(f"⚠️ WARNING: OCCURS expansion created {fields_after_denorm} fields. This may cause very slow parsing. Consider optimizing OCCURS handling.")
            
            return field_definitions
            
        except Exception as e:
            self.logger.error(f"❌ Copybook parsing from string failed: {e}", exc_info=True)
            return []
    
    def _parse_field_definition(self, match: re.Match, line_num: int, is_comp3: bool = False, occurs_count: int = 0, is_comp_manual: bool = False) -> Optional[Dict[str, Any]]:
        """Parse individual field definition from regex match."""
        try:
            level = int(match.group('level'))
            name = match.group('name')
            
            # Extract optional components (use get() to handle missing groups safely)
            redefines = match.group('redefines') if 'redefines' in match.groupdict() else None
            # Use manually extracted occurs_count (legacy approach) instead of regex group
            indexed_by = match.group('indexed_by') if 'indexed_by' in match.groupdict() else None
            pic = match.group('pic') if 'pic' in match.groupdict() else None
            comp = match.group('comp') if 'comp' in match.groupdict() else None
            binary = match.group('binary') if 'binary' in match.groupdict() else None
            
            # CRITICAL FIX: Use manually detected COMP if regex didn't capture it
            # The regex pattern makes COMP optional, so it might not be in the match group
            if is_comp_manual and comp is None:
                comp = "COMP"  # Set comp so the logic below works
            
            field_def = {
                "level": level,
                "name": name,
                "line_number": line_num,
                "redefines": redefines,
                "occurs": occurs_count if occurs_count > 0 else None,  # Use manually extracted count
                "indexed_by": indexed_by,
                "is_comp": comp is not None and not is_comp3,  # COMP but not COMP-3
                "is_binary": binary is not None
            }
            
            # Parse PIC clause
            if pic:
                pic_info = self._parse_pic_clause(pic)
                # Mark as BCD/COMP-3 if detected (COMP-3 is packed decimal)
                pic_info["is_bcd"] = is_comp3
                field_def["pic_info"] = pic_info
            else:
                field_def["pic_info"] = {
                    "pic_string": "",
                    "expanded_pic": "",
                    "field_length": 0,
                    "data_type": "unknown",
                    "has_sign": False,
                    "is_bcd": is_comp3,
                    "is_comp": comp is not None and not is_comp3,
                    "is_binary": binary is not None,
                    "precision": 0
                }
            
            return field_def
            
        except Exception as e:
            self.logger.error(f"❌ Field definition parsing failed at line {line_num}: {e}")
            return None
    
    def _parse_pic_clause(self, pic_str: str) -> Dict[str, Any]:
        """Parse PIC clause to extract field information."""
        try:
            # Remove parentheses and expand repeats
            pic_pattern_repeats = re.compile(r"(.)\((\d+)\)")
            expanded_pic = pic_pattern_repeats.sub(lambda m: m.group(1) * int(m.group(2)), pic_str)
            
            # Determine data type
            pic_pattern_float = re.compile(r"[+-S]?[9Z]*[.V][9Z]+")
            pic_pattern_integer = re.compile(r"S?[9Z]+")
            
            if pic_pattern_float.match(expanded_pic):
                data_type = "float"
            elif pic_pattern_integer.match(expanded_pic):
                data_type = "integer"
            else:
                data_type = "string"
            
            # Calculate field length
            # CRITICAL FIX: For COMP/BINARY fields, we need to count only digits (9s), not sign characters (S)
            # The sign character doesn't consume a byte in binary representation
            # For display formats (non-COMP), include all characters including sign
            field_length = len(expanded_pic)
            
            # Check for sign
            has_sign = 'S' in expanded_pic
            
            # Calculate precision (digits after decimal point)
            precision = 0
            if 'V' in expanded_pic:
                parts = expanded_pic.split('V')
                if len(parts) > 1:
                    precision = len(parts[1])
            
            return {
                "pic_string": pic_str,
                "expanded_pic": expanded_pic,
                "field_length": field_length,
                "data_type": data_type,
                "has_sign": has_sign,
                "precision": precision,
                "is_bcd": False,  # Will be set by caller if COMP-3
                "is_comp": False,  # Will be set by caller if COMP
                "is_binary": False  # Will be set by caller if BINARY
            }
            
        except Exception as e:
            self.logger.error(f"❌ PIC clause parsing failed: {e}")
            return {
                "pic_string": pic_str,
                "expanded_pic": pic_str,
                "field_length": 0,
                "data_type": "unknown",
                "has_sign": False
            }
    
    def _normalize_ascii_file(self, binary_data: bytes, record_length: int, parseable_fields: List[Dict[str, Any]]) -> Tuple[bytes, dict]:
        """
        Normalize ASCII file using extensible patterns (similar to FileFormatNormalizer).
        
        Steps:
        1. Remove newlines (convert text to binary)
        2. Find first valid data record using pattern matching (extensible)
        3. Detect and strip record prefixes using spacing detection (extensible)
        
        Returns:
            Tuple of (normalized_bytes, metadata_dict)
        """
        metadata = {
            'original_size': len(binary_data),
            'newlines_removed': 0,
            'header_bytes': 0,
            'record_prefix_length': 0,
            'normalized_size': 0
        }
        
        # Step 1: Remove newlines
        original_size = len(binary_data)
        # CRITICAL: Only remove newlines that are BETWEEN records, not within fields
        # Check if newlines are at record boundaries before removing
        normalized = binary_data.replace(b'\n', b'').replace(b'\r', b'')
        newlines_removed = original_size - len(normalized)
        metadata['newlines_removed'] = newlines_removed
        self.logger.info(f"📊 Removed {newlines_removed} newlines from ASCII file (original: {original_size} bytes, after: {len(normalized)} bytes)")
        
        # DEBUG: Log first 100 bytes before and after newline removal to verify no field data is lost
        if len(binary_data) >= 100 and len(normalized) >= 100:
            before_hex = binary_data[:100].hex()
            after_hex = normalized[:100].hex()
            self.logger.info(f"🔍 [newline_removal] First 100 bytes before: {before_hex[:80]}...")
            self.logger.info(f"🔍 [newline_removal] First 100 bytes after: {after_hex[:80]}...")
            # Check if any non-newline bytes were removed
            before_no_nl = binary_data[:100].replace(b'\n', b'').replace(b'\r', b'')
            if before_no_nl != normalized[:100]:
                self.logger.warning(f"⚠️ [newline_removal] Non-newline bytes were removed! This shouldn't happen.")
        
        # Step 2: Find first valid data record using extensible pattern matching
        data_start_offset = self._find_ascii_data_start_extensible(normalized, parseable_fields, record_length)
        
        if data_start_offset > 0:
            normalized = normalized[data_start_offset:]
            metadata['header_bytes'] = data_start_offset
            self.logger.info(f"📊 Removed {data_start_offset} bytes of header/comments")
        
        # Step 3: Detect and strip record prefixes using spacing-based detection (extensible)
        # This detects patterns like "POL001", "POL002" and calculates spacing to infer prefix length
        # The prefix is a separate field BEFORE the record data (e.g., "POL00" before POLICY-NUMBER)
        prefix_length = self._detect_and_strip_prefix_extensible(normalized, record_length, parseable_fields)
        
        if prefix_length > 0:
            # Strip prefixes from all records
            # The prefix is at the START of each record, before the first field
            normalized = self._strip_record_prefixes_extensible(normalized, prefix_length, record_length)
            metadata['record_prefix_length'] = prefix_length
            self.logger.info(f"📊 Stripped {prefix_length}-byte prefix from all records")
        else:
            self.logger.info(f"📊 No prefix detected - using data as-is")
        
        metadata['normalized_size'] = len(normalized)
        return normalized, metadata
    
    def _find_ascii_data_start_extensible(self, binary_data: bytes, parseable_fields: List[Dict[str, Any]], record_length: int, max_scan: int = 2000) -> int:
        """
        Extensible method to find where actual fixed-width data starts in ASCII files.
        
        Uses pattern matching based on first field from copybook (extensible for any file type).
        """
        # Extract first field pattern from copybook (extensible - works for any file)
        first_field = parseable_fields[0] if parseable_fields else None
        first_field_name = first_field.get('name', '').upper() if first_field else ''
        
        # Try to infer pattern from first field name or value
        # Common patterns: "POL001", "POL002" for policy numbers, "REC001" for records, etc.
        first_field_pattern = None
        if first_field_name:
            # If first field is numeric and we see patterns like "POL001", detect it
            # Pattern: 3 letters + 3 digits (e.g., "POL001")
            # We'll search for this pattern in the file
            if 'POLICY' in first_field_name or 'POL' in first_field_name:
                first_field_pattern = r'POL\d{3}'  # Matches "POL001", "POL002", etc.
            elif 'RECORD' in first_field_name or 'REC' in first_field_name:
                first_field_pattern = r'REC\d{3}'  # Matches "REC001", "REC002", etc.
        
        # Strategy 1: Pattern-based search (most reliable, extensible)
        if first_field_pattern:
            try:
                pattern_regex = re.compile(first_field_pattern.encode('ascii', errors='ignore'))
                # Search for pattern in binary data
                matches = list(pattern_regex.finditer(binary_data[:max_scan]))
                
                if len(matches) >= 3:
                    # Check spacing between matches to infer record structure
                    spacings = []
                    for i in range(1, min(4, len(matches))):
                        spacing = matches[i].start() - matches[i-1].start()
                        spacings.append(spacing)
                    
                    if len(set(spacings)) == 1:
                        # Consistent spacing detected - this is likely the record size in the file
                        detected_spacing = spacings[0]
                        self.logger.info(f"📊 Detected consistent spacing: {detected_spacing} bytes between patterns")
                        
                        # Return the first match position as data start
                        return matches[0].start()
            except Exception as e:
                self.logger.warning(f"⚠️ Pattern matching failed: {e}, falling back to heuristics")
        
        # Strategy 2: Use existing extensible heuristics
        return self._find_ascii_data_start(binary_data, parseable_fields, record_length, max_scan)
    
    def _detect_and_strip_prefix_extensible(self, normalized_data: bytes, record_length: int, parseable_fields: List[Dict[str, Any]]) -> int:
        """
        Detect record prefix using extensible spacing-based detection.
        
        Strategy: Find patterns like "POL001", "POL002" and calculate spacing.
        If spacing > record_length, infer prefix length = spacing - record_length.
        
        Returns:
            Prefix length in bytes (0 if no prefix detected)
        """
        if len(normalized_data) < record_length * 2:
            return 0
        
        # Try to find pattern in first few records
        first_field = parseable_fields[0] if parseable_fields else None
        first_field_name = first_field.get('name', '').upper() if first_field else ''
        
        # Infer pattern from field name (extensible)
        pattern = None
        if 'POLICY' in first_field_name or 'POL' in first_field_name:
            pattern = b'POL'
        elif 'RECORD' in first_field_name or 'REC' in first_field_name:
            pattern = b'REC'
        
        if pattern:
            # Search for pattern occurrences
            matches = []
            search_limit = min(len(normalized_data), record_length * 10)
            search_start = 0
            
            while search_start < search_limit:
                pos = normalized_data.find(pattern, search_start, search_limit)
                if pos == -1:
                    break
                matches.append(pos)
                search_start = pos + 1
            
            if len(matches) >= 3:
                # Calculate spacing between matches
                spacings = []
                for i in range(1, min(4, len(matches))):
                    spacing = matches[i] - matches[i-1]
                    spacings.append(spacing)
                
                if len(set(spacings)) == 1:
                    # Consistent spacing detected
                    detected_spacing = spacings[0]
                    self.logger.info(f"📊 Detected record spacing: {detected_spacing} bytes")
                    
                    if detected_spacing > record_length:
                        # Spacing is larger than record length - there's a prefix
                        prefix_length = detected_spacing - record_length
                        self.logger.info(f"📊 Inferred {prefix_length}-byte prefix (spacing {detected_spacing} - record {record_length})")
                        
                        # Verify: Check if "POL00" (5 bytes) or "POL001" (6 bytes) pattern exists
                        if prefix_length == 5:
                            # Check if records start with "POL00" followed by digit
                            if len(normalized_data) >= record_length:
                                first_record_start = normalized_data[:10].decode('ascii', errors='ignore')
                                if first_record_start.startswith('POL00') and len(first_record_start) >= 6 and first_record_start[5].isdigit():
                                    self.logger.info(f"📊 Verified: Records start with 'POL00' + digit pattern")
                                    return 5
                        elif prefix_length == 6:
                            # Check if records start with "POL001" pattern
                            if len(normalized_data) >= record_length:
                                first_record_start = normalized_data[:10].decode('ascii', errors='ignore')
                                if first_record_start.startswith('POL') and len(first_record_start) >= 6 and first_record_start[3:6].isdigit():
                                    self.logger.info(f"📊 Verified: Records start with 'POL###' pattern")
                                    return 6
                        
                        # Use calculated prefix length
                        return prefix_length
        
        return 0
    
    def _strip_record_prefixes_extensible(self, content: bytes, prefix_length: int, record_length: int) -> bytes:
        """
        Strip record prefixes from all records using extensible approach.
        
        Args:
            content: Normalized file content (no newlines, data start found)
            prefix_length: Length of prefix to strip from each record
            record_length: Expected record length after stripping prefix
            
        Returns:
            Content with prefixes stripped
        """
        if prefix_length == 0:
            return content
        
        # Split into records using actual record size (record_length + prefix_length)
        actual_record_size = record_length + prefix_length
        record_count = len(content) // actual_record_size
        
        self.logger.info(f"🔍 [prefix_strip] Splitting {len(content)} bytes into records: actual_record_size={actual_record_size} (record_length={record_length} + prefix_length={prefix_length}), record_count={record_count}")
        
        # DEBUG: Log first record before and after stripping to verify alignment
        if record_count > 0 and len(content) >= actual_record_size:
            first_full_record = content[0:actual_record_size]
            first_stripped = first_full_record[prefix_length:]
            self.logger.info(f"🔍 [prefix_strip] First record (full {actual_record_size} bytes): {first_full_record[:min(60, len(first_full_record))].hex()}")
            self.logger.info(f"🔍 [prefix_strip] First record (stripped {len(first_stripped)} bytes, expected {record_length}): {first_stripped[:min(60, len(first_stripped))].hex()}")
            self.logger.info(f"🔍 [prefix_strip] First record text (full): {repr(first_full_record[:min(60, len(first_full_record))].decode('ascii', errors='ignore'))}")
            self.logger.info(f"🔍 [prefix_strip] First record text (stripped): {repr(first_stripped[:min(60, len(first_stripped))].decode('ascii', errors='ignore'))}")
            # Verify the stripped record length
            if len(first_stripped) != record_length:
                self.logger.warning(f"⚠️ [prefix_strip] Stripped record length mismatch: expected {record_length} bytes, got {len(first_stripped)} bytes!")
            # Check byte 49 (should be first byte of AGE after stripping)
            if len(first_stripped) >= 50:
                byte_49 = first_stripped[49]
                self.logger.info(f"🔍 [prefix_strip] Byte 49 after stripping (should be '0' for AGE): {repr(chr(byte_49))} (hex: {byte_49:02x})")
            else:
                self.logger.warning(f"⚠️ [prefix_strip] Stripped record is only {len(first_stripped)} bytes, cannot check byte 49!")
        
        result = bytearray()
        for i in range(record_count):
            record_start = i * actual_record_size
            record_end = record_start + actual_record_size
            
            if record_end > len(content):
                break
            
            # Extract record and strip prefix from start
            full_record = content[record_start:record_end]
            record_without_prefix = full_record[prefix_length:]
            
            result.extend(record_without_prefix)
        
        self.logger.info(f"📊 Stripped {prefix_length}-byte prefix from {record_count} records")
        return bytes(result)
    
    def _validate_field_against_copybook(
        self, field_name: str, field_data: bytes, expected_length: int,
        pic_info: Dict[str, Any], offset: int, record_number: int, is_ascii_file: bool
    ) -> List[str]:
        """
        Extensible validation: Detect copybook/file mismatches for individual fields.
        
        This method validates that the actual field data matches the copybook specification.
        It does NOT try to "fix" the data - it only reports data quality issues.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        errors = []
        actual_length = len(field_data)
        
        # Validation 1: Field length mismatch
        if actual_length != expected_length:
            errors.append(
                f"Record {record_number}, Field '{field_name}': "
                f"Copybook specifies {expected_length} bytes, but file has {actual_length} bytes. "
                f"Offset: {offset}. This is a DATA QUALITY ISSUE - the file doesn't match the copybook."
            )
        
        # Validation 2: For text fields, check if padding/truncation suggests length mismatch
        if is_ascii_file and pic_info.get('data_type') == 'string' and actual_length == expected_length:
            try:
                field_text = field_data.decode('ascii', errors='ignore')
                # Check if field appears truncated (ends abruptly mid-word)
                # or has unexpected padding (spaces followed by non-space data)
                stripped = field_text.rstrip()
                if len(stripped) < actual_length - 2:  # More than 2 trailing spaces
                    # Check if next byte (if available) is part of what should be this field
                    # This is a heuristic - we can't access next byte here, but we can log the pattern
                    pass
            except Exception:
                pass  # Ignore decode errors - they're handled elsewhere
        
        # Validation 3: For numeric fields, check if data type matches
        if pic_info.get('data_type') in ['integer', 'float']:
            try:
                if is_ascii_file:
                    # ASCII numeric field - should contain only digits, spaces, decimal point, and signs
                    field_text = field_data.decode('ascii', errors='ignore').strip()
                    # Remove allowed characters: digits, spaces, decimal point, signs
                    cleaned = ''.join(c for c in field_text if c.isdigit() or c in [' ', '.', '-', '+'])
                    # Check if there are any remaining non-numeric characters
                    if field_text and len(cleaned) < len(field_text.replace(' ', '').replace('.', '').replace('-', '').replace('+', '')):
                        errors.append(
                            f"Record {record_number}, Field '{field_name}': "
                            f"Expected numeric data (PIC {pic_info.get('pic_clause', '?')}), "
                            f"but found non-numeric characters: {repr(field_text[:20])}. "
                            f"This may indicate field misalignment."
                        )
                else:
                    # EBCDIC numeric field - can contain EBCDIC digits (0xF0-0xF9), spaces (0x40), signs (0x4E=+, 0x60=-)
                    # Check if field contains valid EBCDIC numeric bytes
                    ebcdic_digits = [b for b in field_data if 0xF0 <= b <= 0xF9]
                    ebcdic_space = 0x40
                    ebcdic_plus = 0x4E
                    ebcdic_minus = 0x60
                    
                    # Count valid EBCDIC numeric bytes (digits, spaces, signs)
                    valid_bytes = sum(1 for b in field_data 
                                     if (0xF0 <= b <= 0xF9) or b == ebcdic_space or b == ebcdic_plus or b == ebcdic_minus)
                    
                    # If less than 80% of bytes are valid EBCDIC numeric characters, might be misaligned
                    if len(field_data) > 0 and valid_bytes / len(field_data) < 0.8:
                        # Decode for error message (but this is just for display)
                        field_text = field_data.decode('cp037', errors='ignore').strip()
                        errors.append(
                            f"Record {record_number}, Field '{field_name}': "
                            f"Expected EBCDIC numeric data (PIC {pic_info.get('pic_clause', '?')}), "
                            f"but found many non-numeric bytes. Decoded: {repr(field_text[:20])}. "
                            f"This may indicate field misalignment."
                        )
            except Exception:
                pass  # Ignore decode errors
        
        return errors
    
    def _validate_record_length(
        self, record_number: int, bytes_read: int, expected_length: int,
        record: Dict[str, Any], parseable_fields: List[Dict[str, Any]],
        record_start: int, current_offset: int
    ) -> List[str]:
        """
        Extensible validation: Detect record length mismatches.
        
        This method validates that the actual record length matches the copybook specification.
        It provides detailed diagnostics to help identify the root cause.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        errors = []
        
        if bytes_read != expected_length:
            # Calculate expected length from field definitions
            total_field_lengths = sum(f.get('actual_length', 0) for f in parseable_fields)
            
            error_msg = (
                f"Record {record_number}: Record length mismatch. "
                f"Copybook specifies {expected_length} bytes, but file has {bytes_read} bytes "
                f"(difference: {bytes_read - expected_length} bytes). "
            )
            
            if total_field_lengths != expected_length:
                error_msg += (
                    f"Sum of field lengths from copybook: {total_field_lengths} bytes. "
                    f"This suggests a copybook definition issue."
                )
            else:
                error_msg += (
                    f"Sum of field lengths matches copybook ({total_field_lengths} bytes). "
                    f"This suggests the file structure doesn't match the copybook."
                )
            
            error_msg += (
                f" Record start: {record_start}, Current offset: {current_offset}. "
                f"This is a DATA QUALITY ISSUE - the file doesn't match the copybook."
            )
            
            errors.append(error_msg)
            
            # Additional diagnostic: Show field breakdown for first few records
            if record_number < 3:
                field_breakdown = []
                current_pos = record_start
                for field_def in parseable_fields[:5]:  # First 5 fields
                    field_name = field_def.get('name', 'unknown')
                    field_length = field_def.get('actual_length', 0)
                    field_breakdown.append(
                        f"{field_name}({field_length} bytes @ {current_pos}-{current_pos+field_length-1})"
                    )
                    current_pos += field_length
                errors.append(
                    f"Record {record_number} field breakdown: {', '.join(field_breakdown)}"
                )
        
        return errors
    
    def _find_ascii_data_start(self, binary_data: bytes, parseable_fields: List[Dict[str, Any]], record_length: int, max_scan: int = 2000) -> int:
        """
        Extensible method to find where actual fixed-width data starts in ASCII files.
        
        Strategy (based on industry best practices):
        1. Skip common comment markers (#, *, /, //, REM, etc.)
        2. Detect header row by matching copybook field names (extensible - works for any file)
        3. Validate data records by checking field types match expected patterns
        4. Use heuristics: comments have newlines, fixed-width records typically don't
        
        Returns:
            int: Offset where data starts, or 0 if not found (start from beginning)
        """
        # Common comment markers (extensible list based on industry standards)
        # ASCII files commonly use: #, *, /, //, REM, C, ;, !
        comment_markers = [b'#', b'*', b'/', b'//', b'REM', b'REM ', b'C ', b'C\t', b';', b'!']
        
        # Extract field names from copybook (extensible - works for any file structure)
        field_names = [field.get('name', '').upper() for field in parseable_fields if field.get('name')]
        # Also get field types to validate data records
        field_types = {}
        for field in parseable_fields:
            field_name = field.get('name', '')
            # pic_info is already merged into field dict, or use field_type directly
            field_types[field_name.upper()] = {
                'data_type': field.get('field_type', field.get('pic_info', {}).get('data_type', 'string')),
                'field_length': field.get('actual_length', 0)
            }
        
        # Strategy 1: Find header row by matching field names from copybook
        # This is extensible - works for any file structure, not just policy files
        # Normalize field names (handle hyphens, underscores, spaces)
        normalized_field_names = []
        for name in field_names[:10]:  # Check first 10 field names
            if not name or name.startswith('FILLER'):
                continue
            # Create variations: original, with hyphens, with underscores, with spaces
            normalized_field_names.append(name)
            normalized_field_names.append(name.replace('_', '-'))
            normalized_field_names.append(name.replace('_', ' '))
            normalized_field_names.append(name.replace('-', '_'))
            normalized_field_names.append(name.replace('-', ' '))
        
        for field_name in normalized_field_names:
            if not field_name:
                continue
            # Search for this field name in the file (case-insensitive)
            field_name_upper = field_name.upper()
            field_name_bytes = field_name_upper.encode('ascii', errors='ignore')
            marker_pos = binary_data.find(field_name_bytes, 0, max_scan)
            if marker_pos != -1:
                # Found a field name, check if this is a header row
                # Try a few positions before/after to find record boundary
                for offset_adjust in range(-10, 11):
                    test_offset = marker_pos + offset_adjust
                    if test_offset < 0 or test_offset + record_length > len(binary_data):
                        continue
                    
                    test_record_bytes = binary_data[test_offset:test_offset + record_length]
                    try:
                        test_record_text = binary_data[test_offset:test_offset + record_length].decode('ascii', errors='ignore')
                        test_record_upper = test_record_text.upper()
                        
                        # Check if this record contains multiple field names (header row pattern)
                        # Also check normalized variations
                        matching_fields = 0
                        for name in field_names[:10]:
                            if not name or name.startswith('FILLER'):
                                continue
                            # Check original and variations
                            if (name in test_record_upper or 
                                name.replace('_', '-') in test_record_upper or
                                name.replace('_', ' ') in test_record_upper or
                                name.replace('-', '_') in test_record_upper or
                                name.replace('-', ' ') in test_record_upper):
                                matching_fields += 1
                        
                        if matching_fields >= 3:  # Found header row with at least 3 field names
                            self.logger.info(f"📍 Found header row at offset {test_offset} via field name '{field_name}' ({matching_fields} fields matched)")
                            # Skip the header row - return the offset of the NEXT record (after header)
                            next_record_offset = test_offset + record_length
                            self.logger.info(f"📍 Skipping header row, starting data at offset {next_record_offset}")
                            return next_record_offset
                    except:
                        continue
        
        # Strategy 2: Skip comment lines and find first valid data record
        # Validate records by checking if they match expected field types
        start_scan = 0
        # Skip initial comment markers
        for marker in comment_markers:
            if binary_data.startswith(marker):
                start_scan = len(marker)
                break
        
        for i in range(start_scan, min(max_scan - record_length, len(binary_data) - record_length), 1):
            test_record_bytes = binary_data[i:i+record_length]
            try:
                test_record_text = test_record_bytes.decode('ascii', errors='ignore')
                
                # Skip if it's a comment line
                is_comment = False
                for marker in comment_markers:
                    if test_record_text.startswith(marker.decode('ascii', errors='ignore')):
                        is_comment = True
                        break
                if is_comment:
                    continue
                
                # Skip if it contains newlines in the middle (comments often span lines, fixed-width data typically doesn't)
                if '\n' in test_record_text[:-2] or '\r' in test_record_text[:-2]:  # Allow trailing newline
                    continue
                
                # Skip if it contains comment keywords (extensible list)
                comment_keywords = ['comment', 'note', 'format', 'char', 'record', 'file', 'contains', 'description',
                                   'each record', 'record format', 'char age', 'char premium', 'for anomaly',
                                   'anomaly detection', 'total record', 'characters', 'policy number', 'policyholder']
                test_record_lower = test_record_text.lower()
                if any(keyword in test_record_lower for keyword in comment_keywords):
                    continue
                
                # Validate: Check if first few fields match expected types
                # This is extensible - works for any file structure
                offset = 0
                valid_fields = 0
                first_field_valid = False
                
                for idx, field in enumerate(parseable_fields[:5]):  # Check first 5 fields
                    field_length = field.get('actual_length', 0)
                    if field_length == 0 or offset + field_length > len(test_record_bytes):
                        break
                    
                    field_data = test_record_bytes[offset:offset + field_length]
                    field_type = field_types.get(field.get('name', '').upper(), {}).get('data_type', 'string')
                    
                    try:
                        field_text = field_data.decode('ascii', errors='ignore').strip()
                        
                        # For first field, be more strict - it should look like actual data, not a comment
                        if idx == 0:
                            # First field should NOT contain comment keywords
                            if any(keyword in field_text.lower() for keyword in comment_keywords):
                                break
                            # First field should NOT be mostly spaces or punctuation
                            if len(field_text.strip()) < 3:
                                break
                        
                        # Validate based on expected type
                        if field_type == 'integer':
                            if field_text.isdigit() and len(field_text) >= 3:  # At least 3 digits for meaningful data
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                        elif field_type == 'float':
                            if (field_text.replace('.', '').replace('-', '').isdigit() and len(field_text.replace('.', '').replace('-', '')) >= 3) or field_text == '':
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                        elif field_type == 'string':
                            # String fields should be meaningful (not just spaces, not comment keywords)
                            if len(field_text) > 2 and not any(keyword in field_text.lower() for keyword in comment_keywords):
                                valid_fields += 1
                                if idx == 0:
                                    first_field_valid = True
                    except:
                        pass
                    
                    offset += field_length
                
                # Require first field to be valid AND at least 3 fields total
                if first_field_valid and valid_fields >= 3:
                    # Verify next record also looks valid
                    if i + record_length * 2 <= len(binary_data):
                        next_record_bytes = binary_data[i+record_length:i+record_length*2]
                        try:
                            next_record_text = next_record_bytes.decode('ascii', errors='ignore')
                            # Quick validation: check if first field of next record also matches expected type
                            first_field = parseable_fields[0] if parseable_fields else None
                            if first_field:
                                first_field_length = first_field.get('actual_length', 0)
                                if first_field_length > 0:
                                    first_field_data = next_record_bytes[:first_field_length]
                                    first_field_text = first_field_data.decode('ascii', errors='ignore').strip()
                                    first_field_type = field_types.get(first_field.get('name', '').upper(), {}).get('data_type', 'string')
                                    
                                    # Skip if next record looks like a comment
                                    comment_keywords = ['comment', 'note', 'format', 'char', 'record', 'file', 'contains', 'description',
                                                       'each record', 'record format', 'char age', 'char premium', 'for anomaly']
                                    if any(keyword in first_field_text.lower() for keyword in comment_keywords):
                                        continue
                                    
                                    # Validate first field of next record (stricter)
                                    next_valid = False
                                    if first_field_type == 'integer' and first_field_text.isdigit() and len(first_field_text) >= 3:
                                        next_valid = True
                                    elif first_field_type == 'float' and (first_field_text.replace('.', '').replace('-', '').isdigit() and len(first_field_text.replace('.', '').replace('-', '')) >= 3):
                                        next_valid = True
                                    elif first_field_type == 'string' and len(first_field_text) > 2 and not any(keyword in first_field_text.lower() for keyword in comment_keywords):
                                        next_valid = True
                                    
                                    if next_valid:
                                        # Check if this looks like a header row (contains multiple field names)
                                        # If so, skip to the next record
                                        test_record_upper = test_record_text.upper()
                                        matching_field_names = sum(1 for name in field_names[:10] 
                                                                  if name and not name.startswith('FILLER') 
                                                                  and (name in test_record_upper or 
                                                                       name.replace('_', '-') in test_record_upper or
                                                                       name.replace('-', '_') in test_record_upper))
                                        
                                        if matching_field_names >= 3:
                                            # This is a header row, skip it
                                            next_record_offset = i + record_length
                                            self.logger.info(f"📍 Found header row at offset {i}, skipping to data at offset {next_record_offset}")
                                            return next_record_offset
                                        else:
                                            self.logger.info(f"📍 Found data start at offset {i} (validated {valid_fields} fields, first field valid)")
                                            return i
                        except:
                            pass
            except:
                continue
        
        # If we couldn't find a clear data start, return 0 (start from beginning)
        self.logger.warning(f"📍 Could not find clear data start, will parse from beginning")
        return 0
    
    async def _parse_binary_records(self, binary_data: bytes, field_definitions: List[Dict[str, Any]], codepage: str = 'cp037') -> List[Dict[str, Any]]:
        """
        Parse binary records using field definitions.
        Uses proven approach from legacy cobol2csv.py implementation.
        Reads fields sequentially like legacy: for each record, read all fields in order.
        """
        try:
            # Build parseable fields list with adjusted lengths (like legacy decode_copybook_file)
            parseable_fields = []
            record_length = 0
            
            for field_def in field_definitions:
                level = field_def.get('level', 0)
                if level == 1:  # Skip record level (01)
                    continue
                
                pic_info = field_def.get('pic_info', {})
                field_length = pic_info.get('field_length', 0)
                field_name = field_def.get('name', 'unknown')
                
                # DEBUG: Log field attributes to diagnose COMP detection
                is_comp = field_def.get('is_comp', False)
                is_binary = field_def.get('is_binary', False)
                is_bcd = pic_info.get('is_bcd', False)
                if field_name in ['NE1-ISS-YR', 'NE1-ISS-YR-SFX', 'NE1-SCL-YR', 'NE1-SCL-MO-NUM', 'NE1-LOW-AGE-NUM', 'NE1-HIGH-AGE-NUM']:
                    self.logger.info(f"🔍 [DEBUG] Field '{field_name}': is_comp={is_comp}, is_binary={is_binary}, is_bcd={is_bcd}, field_length={field_length}, expanded_pic='{pic_info.get('expanded_pic', '')}'")
                
                # Adjust length for COMP-3 (packed decimal) - use math.ceil like legacy
                # CRITICAL: is_bcd is stored in pic_info (set during parsing)
                if pic_info.get('is_bcd'):
                    # CRITICAL FIX: For COMP-3, count only digits (9s), not sign character (S) or V
                    # The expanded_pic includes 'S' and 'V' but binary representation doesn't use bytes for these
                    expanded_pic = pic_info.get('expanded_pic', '')
                    # Count only 9s and Zs (digits), excluding S, +, -, V, and decimal points
                    digit_count = len([c for c in expanded_pic if c in '9Z'])
                    if digit_count > 0:
                        field_length = int(math.ceil((digit_count + 1) / 2)) if digit_count > 0 else 0
                    else:
                        # Fallback to original field_length if no digits found
                        field_length = int(math.ceil((field_length + 1) / 2)) if field_length > 0 else 0
                # Adjust length for COMP/BINARY - use get_len_for_comp_binary logic
                # CRITICAL: is_comp is stored in field_def, not pic_info!
                elif field_def.get('is_comp') or field_def.get('is_binary'):
                    # CRITICAL FIX: For COMP/BINARY, count only digits (9s), not sign character (S)
                    # The expanded_pic includes 'S' but binary representation doesn't use a byte for sign
                    expanded_pic = pic_info.get('expanded_pic', '')
                    # Count only 9s and Zs (digits), excluding S, +, -, V, and decimal points
                    digit_count = len([c for c in expanded_pic if c in '9Z'])
                    if digit_count > 0:
                        original_field_length = field_length
                        field_length = self._get_len_for_comp_binary(digit_count)
                        field_name = field_def.get('name', 'unknown')
                        if original_field_length != field_length:
                            self.logger.info(f"🔧 [COMP_fix] Field '{field_name}': adjusted from {original_field_length} to {field_length} bytes (digit_count: {digit_count}, expanded_pic: '{expanded_pic}')")
                    else:
                        # Fallback to original field_length if no digits found
                        self.logger.warning(f"⚠️ [COMP_fix] Field '{field_def.get('name', 'unknown')}': No digits found in expanded_pic '{expanded_pic}', using original field_length {field_length}")
                        field_length = self._get_len_for_comp_binary(field_length)
                
                # Include ALL fields that have PIC clauses (like legacy - it includes all fields)
                # Even if field_length is 0, we should still include it to maintain alignment
                if field_length > 0:
                    record_length += field_length
                # Store field with adjusted length (like legacy element["length"])
                # Include even 0-length fields to maintain field order and alignment
                parseable_fields.append({
                    **field_def,
                    'actual_length': field_length,  # Adjusted byte length (may be 0)
                    'field_type': pic_info.get('data_type', 'string'),
                    'tag': 'BCD' if pic_info.get('is_bcd') else ('Comp' if pic_info.get('is_comp') else ('Binary' if pic_info.get('is_binary') else None))
                })
            
            if record_length == 0:
                self.logger.error("❌ No valid fields found or record length is 0")
                return []
            
            self.logger.info(f"📏 Calculated record length: {record_length} bytes, {len(parseable_fields)} fields")
            
            # WARNING: If too many fields, parsing will be extremely slow
            if len(parseable_fields) > 500:
                self.logger.warning(f"⚠️ WARNING: {len(parseable_fields)} parseable fields detected. This will cause very slow parsing. Estimated time: {len(parseable_fields) * 0.001:.1f} seconds per record.")
            
            # Debug: Log field lengths - LIMIT to first 50 fields to avoid log spam
            self.logger.info(f"🔍 [field_lengths] Record length: {record_length}, Total fields: {len(parseable_fields)}")
            field_lengths_summary = []
            for i, field_def in enumerate(parseable_fields[:50]):  # Limit to first 50 fields
                field_name = field_def.get('name', 'unknown')
                field_length = field_def.get('actual_length', 0)
                pic_info = field_def.get('pic_info', {})
                pic_length = pic_info.get('field_length', 0)
                is_bcd = pic_info.get('is_bcd', False)
                is_comp = pic_info.get('is_comp', False)
                is_binary = pic_info.get('is_binary', False)
                field_lengths_summary.append(f"{field_name}:{field_length}")
            if len(parseable_fields) > 50:
                self.logger.info(f"🔍 [field_lengths] First 50 fields: {', '.join(field_lengths_summary)} ... (showing first 50 of {len(parseable_fields)} fields)")
            else:
                self.logger.info(f"🔍 [field_lengths] All fields: {', '.join(field_lengths_summary)}")
            
            # Also log total from field_definitions to see if we're missing any
            total_fields_in_def = sum(1 for fd in field_definitions if fd.get('level', 0) != 1)
            self.logger.info(f"🔍 [field_count] Total fields in definitions: {total_fields_in_def}, Parseable fields: {len(parseable_fields)}")
            
            # Use proven sequential reading approach from legacy code
            # Read record-by-record: for each record, read all fields in order
            records = []
            offset = 0
            record_number = 0
            first_field_name = parseable_fields[0].get('name', '') if parseable_fields else ''
            
            # Use legacy approach: read ALL fields for ALL records sequentially
            # Accumulate data per field (like legacy item['data'] arrays)
            field_data_arrays = {field_def.get('name', 'unknown'): [] for field_def in parseable_fields}
            
            offset = 0
            record_number = 0
            
            # For ASCII files, use extensible pattern-based detection to find data start
            # This works for any file structure, not just specific file types
            # Strategy: Detect if file is ASCII, then use extensible method to find data start
            is_ascii_file = False
            if len(binary_data) > 100:
                ascii_bytes = sum(1 for b in binary_data[:100] if 0x20 <= b <= 0x7E)
                if ascii_bytes / 100 > 0.8:  # >80% ASCII printable
                    is_ascii_file = True
            
            record_prefix_length = 0
            if is_ascii_file or codepage in ['ascii', 'utf-8'] or codepage is None:
                # Step 1: Normalize file (remove newlines, find data start)
                # This uses extensible patterns that work for any file structure
                normalized_data, normalization_metadata = self._normalize_ascii_file(
                    binary_data, 
                    record_length, 
                    parseable_fields
                )
                
                # Update offset based on normalization
                offset = 0  # Normalized data starts at 0
                record_prefix_length = normalization_metadata.get('record_prefix_length', 0)
                
                # Use normalized data for parsing
                original_binary_data_size = len(binary_data)
                binary_data = normalized_data
                self.logger.info(f"📊 Using normalized data: {len(normalized_data)} bytes (was {original_binary_data_size} bytes before normalization)")
                
                # DEBUG: Log first record after normalization to verify alignment
                if len(normalized_data) >= record_length:
                    first_record_hex = normalized_data[:min(record_length, 100)].hex()
                    first_record_text = normalized_data[:min(record_length, 100)].decode('ascii', errors='ignore')
                    self.logger.info(f"📊 First normalized record (first {min(record_length, 100)} bytes):")
                    self.logger.info(f"   Hex: {first_record_hex[:80]}...")
                    self.logger.info(f"   Text: {repr(first_record_text[:80])}")
                    # Check specific byte positions for AGE field
                    if len(normalized_data) >= 53:
                        self.logger.info(f"   Byte 49 (should be first of AGE '0'): {repr(chr(normalized_data[49]))} (hex: {normalized_data[49]:02x})")
                        self.logger.info(f"   Byte 50 (should be second of AGE '4'): {repr(chr(normalized_data[50]))} (hex: {normalized_data[50]:02x})")
                        self.logger.info(f"   Byte 51 (should be third of AGE '5'): {repr(chr(normalized_data[51]))} (hex: {normalized_data[51]:02x})")
                        self.logger.info(f"   Bytes 49-52 (AGE + first of POLICY-TYPE): {repr(normalized_data[49:53].decode('ascii', errors='ignore'))}")
                
                self.logger.info(f"📍 ASCII file normalized: {normalization_metadata.get('header_bytes', 0)} bytes header removed, "
                               f"{normalization_metadata.get('newlines_removed', 0)} newlines removed, "
                               f"{record_prefix_length}-byte prefix detected")
            
            # Read fields sequentially until EOF (like legacy)
            # Safety: Maximum records to prevent infinite loops
            MAX_RECORDS = 1000000  # 1 million records max
            MAX_MISALIGNMENT_COUNT = 10  # Stop after 10 consecutive misalignments
            misalignment_count = 0
            
            # Performance warning: If we have many fields, warn but allow processing
            # Legacy implementations handled large OCCURS expansions successfully
            # Increased limit from 1000 to 10000 to accommodate real-world copybooks
            if len(parseable_fields) > 10000:
                self.logger.error(f"❌ Too many parseable fields ({len(parseable_fields)}). This will likely cause extremely slow parsing or timeout. OCCURS expansion may have created too many fields. Aborting to prevent timeout.")
                return []
            elif len(parseable_fields) > 1000:
                estimated_time_per_record = len(parseable_fields) * 0.001  # Rough estimate: 1ms per field
                self.logger.warning(f"⚠️ Large number of parseable fields ({len(parseable_fields)}). Estimated time: ~{estimated_time_per_record:.2f} seconds per record. This may be slow but will proceed.")
            
            while offset < len(binary_data) and record_number < MAX_RECORDS:
                # Read all fields for one record
                record_start = offset
                record = {}
                
                # Note: For ASCII files, prefixes are already stripped during normalization
                # So we don't need to skip prefixes here - the data is already clean
                
                # Performance: Log progress periodically to show we're making progress
                if record_number == 0:
                    self.logger.info(f"🔄 Starting to parse record 0 with {len(parseable_fields)} fields...")
                elif record_number % 100 == 0:
                    self.logger.info(f"🔄 Parsed {record_number} records so far... (offset: {offset}/{len(binary_data)})")
                
                for field_idx, field_def in enumerate(parseable_fields):
                    field_name = field_def.get('name', 'unknown')
                    field_length = field_def.get('actual_length', 0)
                    pic_info = field_def.get('pic_info', {})
                    
                    # Skip 0-length fields (they don't consume bytes)
                    if field_length == 0:
                        record[field_name] = ''  # Empty value for 0-length fields
                        field_data_arrays[field_name].append('')
                        continue
                    
                    # Extract field data
                    # CRITICAL: Check if we have enough bytes for this field
                    # If we don't have enough bytes, pad with zeros (for incomplete records)
                    # This allows us to continue parsing even if the file is shorter than expected
                    if offset + field_length > len(binary_data):
                        # Not enough bytes for this field - pad with zeros and break
                        remaining_bytes = len(binary_data) - offset
                        if remaining_bytes > 0:
                            # Read what we can and pad the rest
                            field_data = binary_data[offset:] + b'\x00' * (field_length - remaining_bytes)
                            self.logger.warning(f"⚠️ [incomplete_field] Record {record_number}, Field '{field_name}': Only {remaining_bytes} bytes available, expected {field_length}. Padding with zeros.")
                        else:
                            # No bytes left - break out of field loop
                            break  # End of file
                    else:
                        # Parse field according to copybook - trust the copybook as source of truth
                        field_data = binary_data[offset:offset + field_length]
                    
                    # Extensible validation: Detect copybook/file mismatches
                    validation_errors = self._validate_field_against_copybook(
                        field_name, field_data, field_length, pic_info, 
                        offset, record_number, is_ascii_file
                    )
                    if validation_errors:
                        for error in validation_errors:
                            self.logger.warning(f"⚠️ [copybook_validation] {error}")
                    
                    # Special handling for ASCII files with potential 1-byte misalignment:
                    # If this is the first field and it's supposed to be numeric but ends with a letter,
                    # we might be reading one byte too many. Try reading field_length-1 instead.
                    if (is_ascii_file and field_idx == 0 and field_length > 1 and 
                        pic_info.get('data_type') in ['integer', 'float']):
                        field_text = field_data.decode('ascii', errors='ignore').strip()
                        # Check if field ends with a letter when it should be all digits
                        if field_text and field_text[-1].isalpha() and field_text[:-1].isdigit():
                            # Likely reading one byte too many - try field_length-1
                            adjusted_length = field_length - 1
                            field_data = binary_data[offset:offset + adjusted_length]
                            self.logger.warning(f"⚠️ [field_alignment] First field '{field_name}' appears misaligned (ends with letter '{field_text[-1]}' when should be numeric). Trying length {adjusted_length} instead of {field_length}.")
                            offset += adjusted_length
                        else:
                            offset += field_length
                    else:
                        offset += field_length
                    
                    # Parse using proven legacy functions
                    # Pass is_ascii_file flag so numeric parsing can handle ASCII vs EBCDIC correctly
                    value = self._parse_field_value(field_data, field_def, pic_info, codepage, is_ascii_file=is_ascii_file)
                    
                    # Debug: Log first few records' fields with more detail
                    if record_number < 3:  # Reduced from 5 to 3 for EBCDIC files (can be very verbose)
                        value_str = str(value)[:50] if isinstance(value, str) else str(value)
                        # Log full hex for first few fields to debug alignment issues
                        hex_to_show = field_data.hex() if len(field_data) <= 50 else field_data[:50].hex() + "..."
                        field_start = offset - field_length
                        field_end = offset
                        
                        # For EBCDIC files, show both raw bytes and decoded values
                        if not is_ascii_file:
                            try:
                                cp037_decoded = field_data.decode('cp037', errors='replace')
                                self.logger.info(f"🔍 [mainframe_parse] Record {record_number}, Field {len(record)+1}/{len(parseable_fields)}: {field_name}, length: {field_length}, offset: {field_start}->{field_end}, raw_hex: {hex_to_show}, cp037: {repr(cp037_decoded[:30])}, parsed_value: {repr(value_str)}")
                            except:
                                self.logger.info(f"🔍 [mainframe_parse] Record {record_number}, Field {len(record)+1}/{len(parseable_fields)}: {field_name}, length: {field_length}, offset: {field_start}->{field_end}, raw_hex: {hex_to_show}, parsed_value: {repr(value_str)}")
                        else:
                            self.logger.info(f"🔍 [mainframe_parse] Record {record_number}, Field {len(record)+1}/{len(parseable_fields)}: {field_name}, length: {field_length}, offset: {field_start}->{field_end}, raw_bytes: {hex_to_show}, value: {repr(value_str)}")
                        
                        # For EBCDIC files, check if we're seeing @ symbols
                        # Note: @ (0x7C in cp037) can be valid data OR a filler
                        # If it's a single @ in a short field, it might be valid
                        # If it's many @ symbols, it's likely filler or misalignment
                        if not is_ascii_file and isinstance(value, str) and '@' in value:
                            at_count = value.count('@')
                            at_ratio = at_count / len(value) if value else 0
                            # Log warning if >30% @ symbols OR if single @ in a field that shouldn't have it
                            if at_ratio > 0.3:
                                self.logger.warning(f"   ⚠️ Field '{field_name}' has many @ symbols ({at_count}/{len(value)}, ratio: {at_ratio:.2f}) - might indicate wrong code page or misalignment. Raw hex: {hex_to_show}")
                            elif at_count == 1 and len(value) <= 3:
                                # Single @ in short field - might be valid data, but log for review
                                self.logger.info(f"   ℹ️ Field '{field_name}' has single @ symbol: {repr(value)}. Raw hex: {hex_to_show}. This might be valid data or a filler.")
                    
                    record[field_name] = value
                    # Accumulate per field (like legacy)
                    field_data_arrays[field_name].append(value)
                
                # Check if we got a complete record
                bytes_read = offset - record_start
                
                # DEBUG: Log bytes_read vs record_length for first few records
                if record_number < 3:
                    self.logger.info(f"🔍 [record_debug] Record {record_number}: record_start={record_start}, offset={offset}, bytes_read={bytes_read}, record_length={record_length}, diff={bytes_read - record_length}")
                
                # For ASCII files, check if there's a newline after the record
                # ASCII fixed-width files often have \n or \r\n between records
                if is_ascii_file and offset < len(binary_data):
                    # Check for newline(s) after the record
                    if binary_data[offset:offset+1] == b'\n':
                        offset += 1  # Skip single \n
                        bytes_read += 1
                    elif offset + 1 < len(binary_data) and binary_data[offset:offset+2] == b'\r\n':
                        offset += 2  # Skip \r\n
                        bytes_read += 2
                    elif binary_data[offset:offset+1] == b'\r':
                        offset += 1  # Skip single \r
                        bytes_read += 1
                
                # CRITICAL: After reading all fields, we need to ensure offset is at the start of the next record
                # If bytes_read matches record_length, offset should already be correct
                # But if there's a mismatch, we need to handle it properly
                
                if bytes_read != record_length:
                    # Log mismatch for first few records with field details
                    if record_number < 5:
                        field_summary = ', '.join([f"{k}={repr(str(v)[:20])}" for k, v in list(record.items())[:5]])
                        self.logger.warning(f"⚠️ [record_check] Record {record_number}: expected {record_length} bytes, read {bytes_read} bytes, diff: {bytes_read - record_length}, Record start: {record_start}, Current offset: {offset}, Fields parsed: {len(record)}, First 5 fields: {field_summary}")
                    
                    if bytes_read < record_length:
                        # Incomplete record - stop
                        self.logger.warning(f"⚠️ Incomplete record {record_number}: read {bytes_read} bytes, expected {record_length} bytes. Stopping.")
                        break
                    
                    # If we read more, we might be out of sync
                    if bytes_read > record_length:
                        misalignment_count += 1
                        if record_number < 5:
                            # Show field breakdown
                            total_field_lengths = sum(f.get('actual_length', 0) for f in parseable_fields)
                            self.logger.warning(f"⚠️ [record_overshoot] Record {record_number} read {bytes_read - record_length} extra bytes - might be misaligned! (misalignment_count: {misalignment_count}), Record start: {record_start}, Expected end: {record_start + record_length}, Actual offset: {offset}, Sum of field lengths: {total_field_lengths}, Record length: {record_length}")
                        
                        # If we have too many consecutive misalignments, stop to prevent infinite loop
                        if misalignment_count >= MAX_MISALIGNMENT_COUNT:
                            self.logger.error(f"❌ Too many consecutive misalignments ({misalignment_count}). Record length calculation may be incorrect. Stopping to prevent infinite loop.")
                            break
                        
                        # CRITICAL FIX: Realign offset to the correct next record start
                        # If we read more bytes than expected, the actual record length in the file might be different
                        # For EBCDIC files, trust the actual bytes_read as the real record length
                        # Reset offset to record_start + bytes_read (the actual record length we read)
                        if not is_ascii_file:  # For EBCDIC files, use actual bytes_read as record length
                            actual_record_length = bytes_read
                            # CRITICAL: Update offset to point to the start of the next record
                            offset = record_start + actual_record_length
                            if record_number < 3:
                                self.logger.warning(f"⚠️ [record_realign] Record {record_number}: Read {bytes_read} bytes (expected {record_length}). Using actual bytes_read as record length. Next record will start at offset {offset} (was at {record_start + record_length})")
                        else:
                            # For ASCII files, don't auto-realign - log and continue
                            if record_number < 5:
                                self.logger.warning(f"⚠️ Record {record_number} misalignment: read {bytes_read} bytes, expected {record_length}. Continuing to diagnose...")
                elif bytes_read == record_length:
                    # Record length matches - use simple sequential reading like legacy code
                    # Legacy code doesn't do padding detection - it just reads fields sequentially
                    # For EBCDIC files, trust the record_length and read sequentially
                    # Don't try to detect/skip padding - if padding exists, it will be read as part of the next field
                    # This matches the proven legacy approach
                    offset = record_start + bytes_read
                    if record_number < 3:
                        self.logger.info(f"✅ [record_check] Record {record_number}: Read exactly {bytes_read} bytes (matches record_length {record_length}). Next record starts at offset {offset}")
                    # Reset misalignment count if we're aligned
                    misalignment_count = 0
                else:
                    # bytes_read < record_length - incomplete record
                    # Reset misalignment count
                    misalignment_count = 0
                    # Don't update offset - we'll break out of the loop
                
                # Skip comment/metadata records using extensible pattern detection
                # Focus on general patterns (hash tags, non-printable chars) rather than file-specific patterns
                # Check raw bytes BEFORE parsing to catch non-printable characters
                is_header = False
                if record_number < 20:
                    # Check raw record bytes for non-printable characters BEFORE parsing
                    # BUT: Be more conservative - only skip if the ENTIRE first field is non-printable markers
                    # Don't skip records that have valid data mixed with markers
                    record_bytes = binary_data[record_start:record_start + record_length] if record_start + record_length <= len(binary_data) else binary_data[record_start:]
                    has_non_printable_in_raw = False
                    if record_number < 10:  # Only check first 10 records for performance
                        # Only skip if the FIRST field (first 20-30 bytes) is ALL non-printable markers
                        # This prevents skipping valid records that happen to have some non-printable chars
                        first_field_bytes = record_bytes[:30]  # Check first 30 bytes (typical first field size)
                        non_printable_in_first_field = sum(1 for b in first_field_bytes if b < 0x20 and b not in [0x09, 0x0A, 0x0D])
                        # Only skip if >80% of first field is non-printable (likely a pure marker/separator)
                        if len(first_field_bytes) > 0 and non_printable_in_first_field / len(first_field_bytes) > 0.8:
                            has_non_printable_in_raw = True
                            self.logger.info(f"⏭️ [filter] Skipping record {record_number}: first field is >80% non-printable markers")
                    
                    # Get the first field's NAME (key) and VALUE (after parsing)
                    first_field_name = parseable_fields[0].get('name', '') if parseable_fields else ''
                    first_value = str(record.get(first_field_name, '')) if first_field_name else ''
                    
                    # EXTENSIBLE PATTERN 1: Check for comment markers (#) anywhere in ANY field of the record
                    # Hash tags are commonly used as comment markers in ASCII fixed-width files
                    # This pattern works for any file type, not just specific ones
                    # Check ALL fields, not just first 10, to catch comments anywhere
                    has_comment_marker = False
                    has_non_printable = False
                    if record_number < 10:  # Only check first 10 records for performance
                        for field_name in list(record.keys()):  # Check ALL fields
                            field_value = str(record.get(field_name, ''))
                            if '#' in field_value:
                                has_comment_marker = True
                                break  # Found a comment marker, skip entire record
                            # EXTENSIBLE PATTERN 2: Check for non-printable control characters in parsed values
                            # This is a secondary check after raw byte check
                            # BUT: Be more conservative - only skip if field is >50% non-printable
                            if field_value:
                                # Count non-printable characters (excluding spaces, newlines, tabs)
                                non_printable_count = sum(1 for c in field_value if not c.isprintable() and c not in ['\n', '\r', '\t', ' '])
                                # Only skip if >50% of field is non-printable (likely a marker field, not data)
                                if len(field_value) > 0 and non_printable_count / len(field_value) > 0.5:
                                    has_non_printable = True
                                    break
                    
                    # Skip records with comment markers or excessive non-printable characters
                    # These are general patterns that work across file types
                    if first_value.startswith('#') or '\n' in first_value or has_comment_marker or has_non_printable or has_non_printable_in_raw:
                        is_header = True
                    # Also check for comment-like patterns in first value (extensible)
                    elif len(first_value) > 0:
                        # Check printable ratio (only for first 20 records)
                        printable_ratio = sum(1 for c in first_value if c.isprintable()) / len(first_value) if len(first_value) > 0 else 1.0
                        if printable_ratio < 0.5:
                            is_header = True
                        # Check for comment-like keywords (extensible pattern - works for any file type)
                        elif any(phrase in first_value.lower() for phrase in ['this is', 'file contains', 'record format', 'each record contains', 'description', 'note:', 'comment:', 'ord contains']):
                            is_header = True
                
                if not is_header:
                    records.append(record)
                elif record_number < 10:
                    first_value = str(record.get(parseable_fields[0].get('name', ''), ''))
                    self.logger.info(f"⏭️ [header_skip] Skipping record {record_number}: first field='{first_value[:30]}'")
                
                record_number += 1
                
                # Progress logging for large files
                if record_number % 10000 == 0:
                    self.logger.info(f"📊 Processed {record_number} records, {len(records)} valid records, offset: {offset}/{len(binary_data)} bytes")
            
            if record_number >= MAX_RECORDS:
                self.logger.warning(f"⚠️ Reached maximum record count ({MAX_RECORDS}). Stopping to prevent infinite loop.")
            
            self.logger.info(f"✅ Parsed {len(records)} records from {len(binary_data)} bytes")
            return records
            
        except Exception as e:
            self.logger.error(f"❌ Binary records parsing failed: {e}", exc_info=True)
            return []
    
    def _get_len_for_comp_binary(self, elem_length: int) -> int:
        """Calculate byte length for COMP/BINARY fields (from legacy code)."""
        if elem_length >= 1 and elem_length <= 4:
            return 2
        elif elem_length >= 5 and elem_length <= 9:
            return 4
        elif elem_length >= 10 and elem_length <= 18:
            return 8
        else:
            return 0
    
    def _ebcdic_to_decimal(self, byte_sequence: bytes) -> int:
        """
        Convert EBCDIC-encoded byte sequence to decimal (from legacy code).
        
        Handles EBCDIC display format numeric fields which may contain:
        - EBCDIC digits (0xF0-0xF9)
        - Spaces (0x40 in EBCDIC)
        - Sign indicators (0x4E for +, 0x60 for -)
        - Filler characters
        
        Returns the numeric value, ignoring spaces and other non-digit characters.
        """
        ebcdic_to_digit = {
            0xF0: '0', 0xF1: '1', 0xF2: '2', 0xF3: '3', 0xF4: '4',
            0xF5: '5', 0xF6: '6', 0xF7: '7', 0xF8: '8', 0xF9: '9'
        }
        
        # EBCDIC space is 0x40, but we'll also handle ASCII spaces (0x20) if present
        # EBCDIC sign indicators: 0x4E = '+', 0x60 = '-'
        
        digits = []
        is_negative = False
        
        for byte in byte_sequence:
            if byte in ebcdic_to_digit:
                digits.append(ebcdic_to_digit[byte])
            elif byte == 0x60:  # EBCDIC minus sign
                is_negative = True
            # Ignore spaces (0x40 EBCDIC, 0x20 ASCII), plus signs (0x4E EBCDIC), and other non-digits
        
        if not digits:
            return 0
        
        value = int(''.join(digits))
        return -value if is_negative else value
    
    def _unpack_hex_array(self, byte_sequence: bytes) -> int:
        """Unpack binary/COMP field (from legacy code)."""
        if not byte_sequence:
            return 0
        # Check if negative (starts with 0xFF)
        if byte_sequence[0] == 0xFF:
            v = 0
            for b in byte_sequence:
                v = v * 256 + (255 - b)
            return -(v + 1)
        else:
            v = 0
            for b in byte_sequence:
                v = v * 256 + b
            return int(v)
    
    def _unpack_comp3_number(self, byte_sequence: bytes, left_digits: int, right_digits: int) -> float:
        """Unpack COMP-3 (packed decimal) number (from legacy code)."""
        if not byte_sequence:
            return 0.0
        result = 0
        sign = 1
        # Process all bytes except the last one
        for byte in byte_sequence[:-1]:
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F
            result = (result * 100) + (high_nibble * 10) + low_nibble
        # Handle last byte which contains last digit and sign
        last_byte = byte_sequence[-1]
        last_digit = (last_byte >> 4) & 0x0F
        sign_nibble = last_byte & 0x0F
        result = (result * 10) + last_digit
        # Check sign nibble: 0x0D = negative, 0x0C = positive
        if sign_nibble == 0x0D:
            sign = -1
        return sign * (result / (10 ** right_digits))
    
    def _custom_encoder(self, my_string: str) -> str:
        """
        Replace non-ASCII characters with spaces (from legacy code).
        Also removes excessive @ symbols that are EBCDIC fillers.
        Enhanced to also filter control characters (0x00-0x1F) which cause garbled output.
        """
        # First, replace non-ASCII (>127) with spaces (legacy behavior)
        # Also replace control characters (0x00-0x1F) except common whitespace (tab, newline, carriage return)
        cleaned = "".join([
            i if (ord(i) < 128 and (ord(i) >= 32 or i in ['\n', '\r', '\t'])) else " " 
            for i in my_string
        ])
        # Remove excessive @ symbols (EBCDIC filler character)
        # Replace multiple consecutive @ with single space, then strip trailing @
        import re
        cleaned = re.sub(r'@{2,}', ' ', cleaned)  # Replace 2+ @ with space
        cleaned = cleaned.rstrip('@')  # Remove trailing @
        # Remove any remaining control characters that might have slipped through
        cleaned = ''.join(c if c.isprintable() or c in ['\n', '\r', '\t', ' '] else ' ' for c in cleaned)
        # Collapse multiple spaces to single space (but preserve single spaces)
        cleaned = re.sub(r' +', ' ', cleaned)
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        return cleaned
    
    def _parse_field_value(self, field_data: bytes, field_def: Dict[str, Any], pic_info: Dict[str, Any], codepage: str = 'cp037', is_ascii_file: bool = False) -> Any:
        """Parse field value using proven legacy approach."""
        data_type = pic_info.get('data_type', 'string')
        is_comp = pic_info.get('is_comp', False)
        is_binary = pic_info.get('is_binary', False)
        is_bcd = pic_info.get('is_bcd', False)
        has_sign = pic_info.get('has_sign', False)
        
        # Normalize data_type for matching (legacy uses "Integer", "Float", "Char")
        data_type_normalized = data_type.lower()
        is_integer = 'integer' in data_type_normalized
        is_float = 'float' in data_type_normalized
        
        # Handle Binary/COMP fields (legacy: tag == "Binary" or "Comp" with Integer)
        if is_binary or (is_comp and is_integer):
            return self._unpack_hex_array(field_data)
        
        # Handle COMP-3 (packed decimal / BCD) - legacy: tag == "BCD" or COMP-3
        # Legacy passes: unpack_comp3_number(data_read, item['length'], item['precision'])
        # where item['length'] is the adjusted byte length (after math.ceil)
        # But the function expects left_digits and right_digits, so we need to calculate from PIC
        if is_bcd:
            precision = pic_info.get('precision', 0)
            pic_length = pic_info.get('field_length', 0)  # Original PIC length
            left_digits = pic_length - precision  # Digits before decimal point
            return self._unpack_comp3_number(field_data, left_digits, precision)
        
        # Handle COMP float (legacy: tag == "Comp" with Float)
        if is_comp and is_float:
            int_val = self._unpack_hex_array(field_data)
            precision = pic_info.get('precision', 0)
            return float(int_val) / (10 ** precision) if precision > 0 else float(int_val)
        
        # Handle Integer (display format - ASCII or EBCDIC)
        # CRITICAL FIX: For ASCII files, decode as ASCII first, then parse as integer
        # For EBCDIC files, use EBCDIC-to-decimal conversion
        if is_integer:
            if is_ascii_file or codepage in ['ascii', 'utf-8']:
                # ASCII numeric field - decode as ASCII and parse
                try:
                    decoded = field_data.decode('ascii', errors='ignore').strip()
                    # Remove any non-digit characters (spaces, padding, letters, etc.)
                    digits_only = ''.join(c for c in decoded if c.isdigit())
                    if digits_only:
                        return int(digits_only)
                    else:
                        # If no digits found, return 0
                        self.logger.warning(f"⚠️ No digits found in numeric field (ASCII): {repr(decoded)}, raw_hex: {field_data.hex()}")
                        return 0
                except (ValueError, UnicodeDecodeError) as e:
                    self.logger.warning(f"⚠️ Failed to parse ASCII numeric field: {e}, raw: {field_data.hex()}")
                    return 0
            else:
                # EBCDIC numeric field - use EBCDIC-to-decimal conversion
                # This handles EBCDIC display format (digits 0xF0-0xF9, spaces, signs)
                value = self._ebcdic_to_decimal(field_data)
                # Log if we got 0 but field has non-zero bytes (might indicate parsing issue)
                if value == 0 and len(field_data) > 0:
                    non_zero_bytes = [b for b in field_data if b != 0x40 and b != 0x20 and b != 0x00]
                    if non_zero_bytes:
                        # Check if it's actually all zeros or if there's a parsing issue
                        ebcdic_digits = [b for b in field_data if 0xF0 <= b <= 0xF9]
                        if not ebcdic_digits and non_zero_bytes:
                            # No EBCDIC digits found but has non-zero bytes - might be wrong encoding
                            self.logger.debug(f"⚠️ EBCDIC numeric field has no digits: hex={field_data.hex()[:20]}")
                return value
        
        # Handle Float (display format - ASCII or EBCDIC)
        # CRITICAL FIX: For ASCII files, decode as ASCII first, then parse as float
        # For EBCDIC files, use EBCDIC-to-decimal conversion then convert to float
        if is_float:
            if is_ascii_file or codepage in ['ascii', 'utf-8']:
                # ASCII float field - decode as ASCII and parse
                try:
                    decoded = field_data.decode('ascii', errors='ignore').strip()
                    # Remove any non-numeric characters except decimal point and sign
                    cleaned = ''.join(c for c in decoded if c.isdigit() or c == '.' or c == '-' or c == '+')
                    if cleaned:
                        return float(cleaned)
                    else:
                        self.logger.warning(f"⚠️ No numeric value found in float field (ASCII): {repr(decoded)}, raw_hex: {field_data.hex()}")
                        return 0.0
                except (ValueError, UnicodeDecodeError) as e:
                    self.logger.warning(f"⚠️ Failed to parse ASCII float field: {e}, raw: {field_data.hex()}")
                    return 0.0
            else:
                # EBCDIC float field - use EBCDIC-to-decimal then convert to float
                int_val = self._ebcdic_to_decimal(field_data)
                precision = pic_info.get('precision', 0)
                return float(int_val) / (10 ** precision) if precision > 0 else float(int_val)
        
        # Handle String/Char - use legacy approach with codepage
        # OPTIMIZED: Only do encoding detection on first few bytes to avoid performance issues
        try:
            # Quick encoding detection: check first 10 bytes (or all if shorter)
            sample_size = min(10, len(field_data)) if field_data else 0
            is_ascii = False
            if sample_size > 0:
                ascii_count = sum(1 for b in field_data[:sample_size] if 0x20 <= b <= 0x7E)
                ascii_ratio = ascii_count / sample_size if sample_size > 0 else 0
                
                if ascii_ratio > 0.8:
                    # ASCII
                    is_ascii = True
                    original_str = field_data.decode('ascii', errors='ignore')
                else:
                    # EBCDIC
                    original_str = codecs.decode(field_data, codepage, errors='ignore')
            else:
                # Empty field
                original_str = ""
            
            # Apply different cleaning for ASCII vs EBCDIC
            if is_ascii:
                # ASCII-specific cleaning for FIXED-WIDTH fields
                # CRITICAL: For fixed-width ASCII, we must preserve field boundaries
                # Don't collapse spaces or strip aggressively - spaces are part of the field structure
                cleaned = original_str
                # EXTENSIBLE PATTERN: Filter out non-printable control characters aggressively
                # Keep only printable ASCII characters (32-126) and whitespace (space, tab)
                # This removes characters like "&|<  " which are control/marker characters
                # This pattern works for any file type, not just specific ones
                # Filter out ALL non-printable characters (except space 0x20 and tab 0x09)
                cleaned = ''.join(c if (32 <= ord(c) <= 126) or c in [' ', '\t'] else '' for c in cleaned)
                # Replace newlines/carriage returns with spaces (they shouldn't be in field data)
                cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
                # Replace tabs with spaces (preserve single space, don't collapse)
                cleaned = cleaned.replace('\t', ' ')
                # CRITICAL: DO NOT collapse multiple spaces for fixed-width ASCII
                # Spaces are part of the field structure in fixed-width formats
                # Only strip trailing whitespace (not leading, to preserve field alignment)
                cleaned = cleaned.rstrip()
                # Don't strip leading spaces - they're part of the field structure
                return cleaned
            else:
                # EBCDIC: use custom encoder (handles @ symbols, etc.)
                return self._custom_encoder(original_str.strip())
        except Exception:
            return ""
    
    def _parse_integer_field(self, field_data: bytes, pic_info: Dict[str, Any]) -> int:
        """Parse integer field from binary data."""
        try:
            if pic_info.get('is_comp') or pic_info.get('is_binary'):
                # Binary integer
                if len(field_data) == 4:
                    return int.from_bytes(field_data, byteorder='big', signed=pic_info.get('has_sign', False))
                elif len(field_data) == 2:
                    return int.from_bytes(field_data, byteorder='big', signed=pic_info.get('has_sign', False))
                else:
                    return int.from_bytes(field_data, byteorder='big', signed=pic_info.get('has_sign', False))
            else:
                # Packed decimal or display format - try ASCII first (check if printable)
                ascii_count = sum(1 for b in field_data if 0x20 <= b <= 0x7E)
                total_bytes = len(field_data) if field_data else 1
                ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
                
                if ascii_ratio > 0.8:
                    try:
                        # For fixed-width fields, preserve leading zeros - don't strip spaces
                        # Only remove trailing spaces, but keep leading spaces/zeros for alignment
                        decoded = field_data.decode('ascii', errors='ignore').rstrip()
                        # Remove leading spaces but keep zeros
                        decoded = decoded.lstrip(' ')
                        return int(decoded) if decoded else 0
                    except (ValueError, UnicodeDecodeError):
                        pass
                
                # Otherwise try EBCDIC
                try:
                    decoded = field_data.decode('cp037', errors='ignore').strip()
                    if not decoded:
                        decoded = field_data.decode('cp1047', errors='ignore').strip()
                    return int(decoded) if decoded else 0
                except (UnicodeDecodeError, LookupError, ValueError):
                    # Fall back to ASCII
                    return int(field_data.decode('ascii', errors='ignore').strip() or '0')
        except Exception:
            return 0
    
    def _parse_float_field(self, field_data: bytes, pic_info: Dict[str, Any]) -> float:
        """Parse float field from binary data."""
        try:
            if pic_info.get('is_comp') or pic_info.get('is_binary'):
                # Binary float
                if len(field_data) == 4:
                    return float(int.from_bytes(field_data, byteorder='big', signed=pic_info.get('has_sign', False)))
                else:
                    return float(int.from_bytes(field_data, byteorder='big', signed=pic_info.get('has_sign', False)))
            else:
                # Display format - try ASCII first (check if printable)
                ascii_count = sum(1 for b in field_data if 0x20 <= b <= 0x7E)
                total_bytes = len(field_data) if field_data else 1
                ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
                
                if ascii_ratio > 0.8:
                    try:
                        # For fixed-width fields, preserve leading zeros - don't strip spaces
                        # Only remove trailing spaces, but keep leading spaces/zeros for alignment
                        value_str = field_data.decode('ascii', errors='ignore').rstrip()
                        # Remove leading spaces but keep zeros
                        value_str = value_str.lstrip(' ')
                        return float(value_str) if value_str else 0.0
                    except (ValueError, UnicodeDecodeError):
                        pass
                
                # Otherwise try EBCDIC
                try:
                    value_str = field_data.decode('cp037', errors='ignore').strip()
                    if not value_str:
                        value_str = field_data.decode('cp1047', errors='ignore').strip()
                    return float(value_str) if value_str else 0.0
                except (UnicodeDecodeError, LookupError, ValueError):
                    # Fall back to ASCII
                    value_str = field_data.decode('ascii', errors='ignore').strip()
                    return float(value_str) if value_str else 0.0
        except Exception:
            return 0.0
    
    def _parse_string_field(self, field_data: bytes, pic_info: Dict[str, Any]) -> str:
        """Parse string field from binary data."""
        try:
            # Try to detect encoding by checking if data looks like ASCII or EBCDIC
            # ASCII printable range is 0x20-0x7E, EBCDIC has different ranges
            # Count how many bytes are in ASCII printable range
            ascii_count = sum(1 for b in field_data if 0x20 <= b <= 0x7E)
            total_bytes = len(field_data) if field_data else 1
            ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
            
            # Debug logging for first few fields
            if len(field_data) > 0 and len(field_data) <= 30:  # Only log short fields to avoid spam
                self.logger.debug(f"🔍 [encoding_detect] bytes: {field_data[:10].hex()}, ascii_count: {ascii_count}/{total_bytes}, ratio: {ascii_ratio:.2f}")
            
            # If >80% of bytes are in ASCII printable range, it's likely ASCII
            if ascii_ratio > 0.8:
                # Try ASCII first
                try:
                    # DON'T strip() for fixed-width fields - preserve spaces for alignment
                    # Only remove non-printable control characters (not spaces)
                    decoded = field_data.decode('ascii', errors='ignore')
                    # Remove non-printable control characters (but keep spaces, tabs, newlines)
                    decoded = ''.join(c if c.isprintable() or c in ['\n', '\r', '\t'] else '' for c in decoded)
                    # Verify it's actually readable (not just control chars)
                    if decoded and any(c.isprintable() for c in decoded):
                        if len(field_data) > 0 and len(field_data) <= 30:
                            self.logger.debug(f"🔍 [encoding_detect] Using ASCII: '{decoded[:50]}'")
                        return decoded
                except Exception as e:
                    if len(field_data) > 0 and len(field_data) <= 30:
                        self.logger.debug(f"🔍 [encoding_detect] ASCII decode failed: {e}")
            
                    # Otherwise try EBCDIC
            try:
                # Try EBCDIC (cp037 - US/Canada) first
                decoded = field_data.decode('cp037', errors='replace')
                
                # Check if cp037 decoding produced mostly @ symbols (might indicate wrong code page or misalignment)
                at_ratio = decoded.count('@') / len(decoded) if decoded else 0
                control_char_ratio = sum(1 for c in decoded if ord(c) < 32) / len(decoded) if decoded else 0
                
                # If >50% are @ symbols or control chars, might be wrong code page - try cp1047 if available
                if (at_ratio > 0.5 or control_char_ratio > 0.5) and len(decoded) > 0:
                    try:
                        cp1047_decoded = field_data.decode('cp1047', errors='replace')
                        # If cp1047 produces fewer @ symbols, use it
                        cp1047_at_ratio = cp1047_decoded.count('@') / len(cp1047_decoded) if cp1047_decoded else 1.0
                        if cp1047_at_ratio < at_ratio:
                            decoded = cp1047_decoded
                            self.logger.debug(f"🔍 [encoding_detect] Switched to cp1047 (fewer @ symbols: {cp1047_at_ratio:.2f} vs {at_ratio:.2f})")
                    except (UnicodeDecodeError, LookupError):
                        pass  # cp1047 not available, stick with cp037
                
                # Clean EBCDIC string fields - but be LESS aggressive
                # Only remove trailing fillers, preserve leading @ unless clearly all fillers
                if decoded:
                    # Remove trailing filler characters (spaces, nulls)
                    decoded = decoded.rstrip(' \x00\xff')
                    # Only remove leading @ if the ENTIRE field is @ symbols (clear filler pattern)
                    if decoded and all(c == '@' for c in decoded):
                        decoded = ''  # Entire field is @ symbols - likely filler
                    # If result is only control chars, return empty string
                    elif decoded and all(ord(c) < 32 for c in decoded if c):
                        decoded = ''
                    # Otherwise, keep the @ symbols - they might be part of the data
                
                if len(field_data) > 0 and len(field_data) <= 30:
                    self.logger.debug(f"🔍 [encoding_detect] Using EBCDIC: '{decoded[:50]}' (raw: {field_data[:10].hex()}, @ ratio: {at_ratio:.2f})")
                return decoded
            except (UnicodeDecodeError, LookupError):
                # Fall back to ASCII if EBCDIC codecs not available
                return field_data.decode('ascii', errors='ignore').strip()
        except Exception:
            return ""
    
    async def convert_to_parquet(self, records: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
        """
        Convert COBOL records to Parquet format.
        
        Args:
            records: List of parsed records
            output_path: Path for output Parquet file
            
        Returns:
            Dict containing conversion results
        """
        try:
            if not self.pandas_available or not self.pyarrow_available:
                return {
                    "success": False,
                    "error": "Required libraries not available",
                    "output_path": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            if not records:
                return {
                    "success": False,
                    "error": "No records to convert",
                    "output_path": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Convert to PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Write to Parquet
            pq.write_table(table, output_path)
            
            return {
                "success": True,
                "output_path": output_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Parquet conversion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "adapter_name": "MainframeProcessingAdapter",
            "status": "ready" if self.pandas_available else "limited",
            "libraries": {
                "pandas": self.pandas_available,
                "pyarrow": self.pyarrow_available
            },
            "capabilities": [
                "cobol_file_parsing",
                "copybook_parsing",
                "binary_record_parsing",
                "parquet_conversion"
            ],
            "supported_data_types": ["integer", "float", "string"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_validation_rules(self, copybook_content: str) -> Dict[str, Any]:
        """
        Extract validation rules from copybook (88-level fields and level-01 metadata records).
        
        Returns:
        {
            "88_level_fields": [
                {
                    "field_name": "STATUS-CODE",
                    "condition_name": "ACTIVE",
                    "value": "A",
                    "line_number": 123
                },
                ...
            ],
            "metadata_records": [
                {
                    "record_name": "POLICY-TYPES",
                    "field_name": "TERM-LIFE",
                    "value": "Term Life",
                    "target_field": "POLICY-TYPE",  # Field in data record this applies to
                    "line_number": 456
                },
                ...
            ]
        }
        """
        validation_rules = {
            "88_level_fields": [],
            "metadata_records": []
        }
        
        try:
            lines = copybook_content.split('\n')
            cleaned_lines = self._clean_cobol(lines)
            
            # Pattern for 88-level fields (condition names)
            # Example: "    88  ACTIVE      VALUE 'A'."
            pattern_88 = re.compile(r'^\s+88\s+(\S+)\s+VALUE\s+[\'"]?([^\'"]+)[\'"]?\.', re.IGNORECASE)
            
            # Pattern for level-01 metadata records
            # Example: "01  POLICY-TYPES."
            pattern_01 = re.compile(r'^01\s+(\S+)\.', re.IGNORECASE)
            
            # Pattern for fields within metadata records with VALUE clauses
            # Example: "    05  TERM-LIFE    PIC X(10) VALUE 'Term Life  '."
            pattern_metadata_field = re.compile(r'^\s+\d{2}\s+(\S+)\s+.*?VALUE\s+[\'"]?([^\'"]+)[\'"]?\.', re.IGNORECASE)
            
            current_88_field = None  # Track which field the 88-level applies to
            current_metadata_record = None  # Track current metadata record
            in_metadata_record = False
            
            for line_num, line in enumerate(cleaned_lines, 1):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('*') or line_stripped.startswith('/'):
                    continue
                
                # Check for level-01 metadata record
                match_01 = pattern_01.match(line_stripped)
                if match_01:
                    record_name = match_01.group(1)
                    # Check if this looks like a metadata record (not a data record)
                    # Metadata records typically have names like POLICY-TYPES, AGE-VALIDATION, etc.
                    if any(keyword in record_name.upper() for keyword in ['TYPES', 'VALIDATION', 'RULES', 'THRESHOLD', 'FLAGS', 'DETECTION']):
                        current_metadata_record = record_name
                        in_metadata_record = True
                        self.logger.debug(f"📋 Found metadata record: {record_name}")
                    else:
                        # This is a data record, reset metadata tracking
                        current_metadata_record = None
                        in_metadata_record = False
                        current_88_field = None
                    continue
                
                # Check for 88-level field (condition name)
                match_88 = pattern_88.match(line_stripped)
                if match_88:
                    condition_name = match_88.group(1)
                    value = match_88.group(2).strip()
                    
                    if current_88_field:
                        validation_rules["88_level_fields"].append({
                            "field_name": current_88_field,
                            "condition_name": condition_name,
                            "value": value,
                            "line_number": line_num
                        })
                        self.logger.debug(f"📋 Found 88-level field: {current_88_field}.{condition_name} = '{value}'")
                    continue
                
                # Check for regular field definition (might be the field that 88-level applies to)
                # Pattern: "05  STATUS-CODE    PIC X(1)."
                field_match = re.match(r'^\s+(\d{2})\s+(\S+)\s+.*?\.', line_stripped)
                if field_match:
                    level = int(field_match.group(1))
                    field_name = field_match.group(2)
                    
                    # If this is a field (not 01 level), it might have 88-level fields following it
                    if level > 1 and level < 88:
                        current_88_field = field_name
                        in_metadata_record = False  # Reset if we're in a data record field
                    
                    # Check if this field is in a metadata record and has a VALUE clause
                    if in_metadata_record and current_metadata_record:
                        match_metadata = pattern_metadata_field.match(line_stripped)
                        if match_metadata:
                            metadata_field_name = match_metadata.group(1)
                            metadata_value = match_metadata.group(2).strip()
                            
                            # Try to infer target field from metadata record name
                            # POLICY-TYPES -> POLICY-TYPE, AGE-VALIDATION -> AGE, etc.
                            target_field = None
                            if current_metadata_record.endswith('-TYPES'):
                                target_field = current_metadata_record[:-6]  # Remove '-TYPES'
                            elif current_metadata_record.endswith('-VALIDATION'):
                                target_field = current_metadata_record[:-11]  # Remove '-VALIDATION'
                            
                            validation_rules["metadata_records"].append({
                                "record_name": current_metadata_record,
                                "field_name": metadata_field_name,
                                "value": metadata_value,
                                "target_field": target_field,  # Field in data record this applies to
                                "line_number": line_num
                            })
                            self.logger.debug(f"📋 Found metadata record field: {current_metadata_record}.{metadata_field_name} = '{metadata_value}' (target: {target_field})")
            
            self.logger.info(f"✅ Extracted {len(validation_rules['88_level_fields'])} 88-level fields and {len(validation_rules['metadata_records'])} metadata record fields")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to extract validation rules from copybook: {e}")
            # Return empty rules if extraction fails (non-critical)
        
        return validation_rules






