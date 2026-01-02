"""
COBOL 88-Level Field Extractor
Extracts validation rules from 88-level fields (legacy pattern).
Similar to legacy implementation's level88_values and value_to_names extraction.
"""

import re
from typing import Dict, List, Set, Tuple, Optional


class Level88Extractor:
    """
    Extracts 88-level field validation rules from COBOL copybook.
    
    Architecture:
    - Role: Validation Rule Extractor (WHAT - extracts validation rules)
    - Service: 88-Field Parser (HOW - parses 88-level fields from copybook)
    """
    
    def __init__(self):
        self.level88_values: Dict[str, Set[str]] = {}  # Maps field names to allowed values
        self.value_to_names: Dict[str, Dict[str, str]] = {}  # Maps field->value->name mappings
    
    def extract_88_fields(self, copybook_content: str) -> Tuple[Dict[str, Set[str]], Dict[str, Dict[str, str]]]:
        """
        Extract 88-level field validation rules from copybook.
        
        Returns:
            (level88_values, value_to_names) tuple
        """
        lines = copybook_content.split('\n')
        cleaned_lines = self._clean_cobol_lines(lines)
        
        # Track current parent field for 88-level fields
        current_parent = None
        temp_value_to_names = {}  # Temporary storage before finalizing
        fields_in_occurs = set()
        occurrence_mapping = {}
        
        # First pass: Identify OCCURS blocks
        current_occurs = None
        current_level = 0
        
        for line in cleaned_lines:
            if not line.strip().startswith("88"):
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        level = int(parts[0])
                        field_name = parts[1]
                        
                        # Check for OCCURS
                        if "OCCURS" in line and " TIMES" in line:
                            occurs_match = re.search(r'OCCURS\s+(\d+)\s+TIMES', line, re.IGNORECASE)
                            if occurs_match:
                                occurs_count = int(occurs_match.group(1))
                                current_occurs = occurs_count
                                current_level = level
                                occurrence_mapping[field_name] = occurs_count
                                fields_in_occurs.add(field_name)
                        elif current_occurs and level > current_level:
                            fields_in_occurs.add(field_name)
                            occurrence_mapping[field_name] = current_occurs
                        elif level <= current_level:
                            current_occurs = None
                            current_level = 0
                    except (ValueError, IndexError):
                        continue
        
        # Second pass: Extract 88-level fields
        for i, line in enumerate(cleaned_lines):
            if line.strip().startswith("88"):
                # This is a 88-level field
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                
                level88_name = parts[1]
                
                # Find parent field (look backwards for non-88 field)
                if not current_parent:
                    for prev_line in reversed(cleaned_lines[:i]):
                        if not prev_line.strip().startswith("88"):
                            prev_parts = prev_line.strip().split()
                            if len(prev_parts) >= 2:
                                try:
                                    prev_level = int(prev_parts[0])
                                    if prev_level < 88:  # Parent must be level < 88
                                        current_parent = prev_parts[1]
                                        break
                                except (ValueError, IndexError):
                                    continue
                
                if current_parent:
                    # Initialize if needed
                    if current_parent not in self.level88_values:
                        self.level88_values[current_parent] = set()
                        temp_value_to_names[current_parent] = {}
                    
                    # Extract VALUES or VALUE clause
                    values_str = None
                    if " VALUES " in line.upper():
                        values_str = line.split(" VALUES ", 1)[1] if " VALUES " in line else None
                    elif " VALUE " in line.upper():
                        values_str = line.split(" VALUE ", 1)[1] if " VALUE " in line else None
                    
                    if values_str:
                        # Remove trailing period and clean
                        values_str = values_str.strip().rstrip('.')
                        
                        # Parse values (can be multiple, separated by spaces or commas)
                        # Handle quoted values: 'VALUE1' 'VALUE2' or "VALUE1" "VALUE2"
                        value_pattern = r"['\"]([^'\"]+)['\"]"
                        values = re.findall(value_pattern, values_str)
                        
                        # Also handle unquoted values (numbers, etc.)
                        if not values:
                            # Try to extract unquoted values
                            unquoted = re.findall(r'\b(\d+|\w+)\b', values_str)
                            values = unquoted
                        
                        for value in values:
                            clean_value = value.strip()
                            if clean_value:
                                # Add to level88_values
                                self.level88_values[current_parent].add(clean_value)
                                
                                # Add to value_to_names mapping
                                if clean_value not in temp_value_to_names[current_parent]:
                                    temp_value_to_names[current_parent][clean_value] = []
                                temp_value_to_names[current_parent][clean_value].append(level88_name)
            else:
                # Not a 88-level field - finalize current parent if exists
                if current_parent and current_parent in temp_value_to_names:
                    # Create base entry if not in OCCURS
                    if current_parent not in fields_in_occurs:
                        if current_parent not in self.value_to_names:
                            self.value_to_names[current_parent] = {}
                        for value, names in temp_value_to_names[current_parent].items():
                            self.value_to_names[current_parent][value] = ','.join(names)
                    
                    # Handle OCCURS - create entries for each occurrence
                    if current_parent in occurrence_mapping:
                        base_name = current_parent
                        occurs_count = occurrence_mapping[current_parent]
                        for i in range(1, occurs_count + 1):
                            occurrence_name = f"{base_name}_{i}"
                            if occurrence_name not in self.value_to_names:
                                self.value_to_names[occurrence_name] = {}
                            for value, names in temp_value_to_names[current_parent].items():
                                self.value_to_names[occurrence_name][value] = ','.join(names)
                
                current_parent = None
        
        # Finalize any remaining mappings
        for parent, values in temp_value_to_names.items():
            if parent not in fields_in_occurs:
                if parent not in self.value_to_names:
                    self.value_to_names[parent] = {}
                for value, names in values.items():
                    self.value_to_names[parent][value] = ','.join(names)
            
            # Handle OCCURS for remaining fields
            if parent in occurrence_mapping:
                base_name = parent
                occurs_count = occurrence_mapping[parent]
                for i in range(1, occurs_count + 1):
                    occurrence_name = f"{base_name}_{i}"
                    if occurrence_name not in self.value_to_names:
                        self.value_to_names[occurrence_name] = {}
                    for value, names in values.items():
                        self.value_to_names[occurrence_name][value] = ','.join(names)
        
        return self.level88_values, self.value_to_names
    
    def _clean_cobol_lines(self, lines: List[str]) -> List[str]:
        """Clean COBOL lines (extract columns 6-72, handle continuation)."""
        cleaned = []
        continuation_buffer = []
        
        for line in lines:
            # Extract columns 6-72 (standard COBOL format)
            if len(line) > 6:
                cobol_code = line[6:72].rstrip() if len(line) > 72 else line[6:].rstrip()
            else:
                cobol_code = line.rstrip()
            
            # Skip comments
            if not cobol_code or cobol_code[0] in ('*', '/'):
                continue
            
            # Handle continuation (column 6 = '-')
            if len(line) > 6 and line[6] == '-':
                continuation_buffer.append(cobol_code)
                continue
            
            # Join continuation if exists
            if continuation_buffer:
                full_line = ' '.join(continuation_buffer) + ' ' + cobol_code
                continuation_buffer = []
                cleaned.append(full_line)
            else:
                cleaned.append(cobol_code)
        
        return cleaned












