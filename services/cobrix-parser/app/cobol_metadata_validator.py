"""
COBOL Metadata Validator
Extracts validation rules from metadata 01-level records in copybooks.
Similar to legacy 88-field validation, but uses metadata records instead.

Architecture: Role=What (Validation), Service=How (Metadata Extraction + Rule Application)
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import codecs


class ValidationRuleType(Enum):
    """Types of validation rules extracted from metadata."""
    ALLOWED_VALUES = "allowed_values"  # POLICY-TYPES: list of valid values
    RANGE = "range"  # AGE-VALIDATION: min/max values
    FORMAT = "format"  # VALIDATION-RULES: format patterns
    THRESHOLD = "threshold"  # ANOMALY-THRESHOLDS: threshold values
    FLAG = "flag"  # ANOMALY-DETECTION, DATA-QUALITY-FLAGS: boolean flags


@dataclass
class ValidationRule:
    """A single validation rule extracted from metadata."""
    rule_type: ValidationRuleType
    field_name: str  # Field in data record this applies to
    rule_name: str  # Name of the rule (e.g., "MIN_AGE", "POLICY_TYPE_ALLOWED")
    value: Any  # Rule value (list, dict, number, string, etc.)
    metadata_record: str  # Source metadata record (e.g., "AGE-VALIDATION")


@dataclass
class ValidationResult:
    """Result of validating a record against rules."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    anomalies: List[str]
    quality_flags: Dict[str, bool]
    details: Dict[str, Any]


class CobolMetadataValidator:
    """
    Extracts and applies validation rules from COBOL copybook metadata records.
    
    Architecture:
    - Role: Data Validator (WHAT - validates data quality)
    - Service: Metadata Rule Extractor (HOW - extracts rules from copybook metadata)
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.field_mappings: Dict[str, str] = {}  # Maps metadata field names to data field names
        self.value_to_names: Dict[str, Dict[str, str]] = {}  # 88-field value->name mappings (legacy)
    
    def extract_metadata_rules(self, copybook_content: str, extract_88_fields: bool = True) -> List[ValidationRule]:
        """
        Extract validation rules from metadata 01-level records AND 88-level fields.
        
        Args:
            copybook_content: Full copybook content with all 01-level records
            extract_88_fields: Whether to also extract 88-level field rules (legacy pattern)
        
        Returns:
            List of validation rules
        """
        from copybook_analyzer import analyze_copybook
        
        records, _ = analyze_copybook(copybook_content)
        rules = []
        
        # Extract rules from metadata 01-level records
        for record in records:
            if record.is_metadata:
                # Extract rules from this metadata record
                record_rules = self._extract_rules_from_metadata_record(record)
                rules.extend(record_rules)
        
        # Extract rules from 88-level fields (legacy pattern)
        if extract_88_fields:
            try:
                from cobol_88_field_extractor import Level88Extractor
                extractor = Level88Extractor()
                level88_values, value_to_names = extractor.extract_88_fields(copybook_content)
                
                # Convert 88-level fields to ValidationRule objects
                for field_name, allowed_values in level88_values.items():
                    if allowed_values:
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.ALLOWED_VALUES,
                            field_name=field_name.upper().replace('_', '-'),
                            rule_name=f"{field_name.upper()}_88_ALLOWED",
                            value=sorted(list(allowed_values)),  # Sort for consistency
                            metadata_record="88-LEVEL-FIELDS"
                        ))
                
                # Store value_to_names for potential use in validation messages
                self.value_to_names = value_to_names
            except Exception as e:
                # Non-critical - 88-field extraction is optional
                import logging
                logging.getLogger(__name__).debug(f"88-field extraction failed (non-critical): {e}")
        
        self.rules = rules
        return rules
    
    def _extract_rules_from_metadata_record(self, record) -> List[ValidationRule]:
        """Extract validation rules from a single metadata record."""
        rules = []
        record_name = record.name.upper()
        
        # POLICY-TYPES: Allowed values for POLICY-TYPE field
        if record_name == "POLICY-TYPES" or "TYPES" in record_name:
            allowed_values = []
            for line in record.lines:
                # Extract field name and VALUE
                # Pattern: 05  TERM-LIFE  PIC X(10) VALUE 'Term Life  '.
                match = re.search(r'05\s+(\w+(?:-\w+)*)\s+PIC\s+\S+\s+VALUE\s+[\'"]([^\'"]+)[\'"]', line, re.IGNORECASE)
                if match:
                    field_name, value = match.groups()
                    allowed_values.append(value.strip())
            
            if allowed_values:
                rules.append(ValidationRule(
                    rule_type=ValidationRuleType.ALLOWED_VALUES,
                    field_name="POLICY-TYPE",  # Maps to POLICY-TYPE in data record
                    rule_name="POLICY_TYPE_ALLOWED",
                    value=allowed_values,
                    metadata_record=record.name
                ))
        
        # AGE-VALIDATION: Range validation for AGE field
        elif record_name == "AGE-VALIDATION" or "VALIDATION" in record_name:
            min_age = None
            max_age = None
            suspicious_flag = None
            
            for line in record.lines:
                # Extract MIN-AGE, MAX-AGE, SUSPICIOUS-AGE-FLAG
                if "MIN-AGE" in line.upper() or "MIN_AGE" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        min_age = int(match.group(1))
                elif "MAX-AGE" in line.upper() or "MAX_AGE" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        max_age = int(match.group(1))
                elif "SUSPICIOUS" in line.upper():
                    match = re.search(r"VALUE\s+['\"]([NY])['\"]", line, re.IGNORECASE)
                    if match:
                        suspicious_flag = match.group(1).upper() == 'Y'
            
            if min_age is not None:
                rules.append(ValidationRule(
                    rule_type=ValidationRuleType.RANGE,
                    field_name="POLICYHOLDER-AGE",
                    rule_name="AGE_MIN",
                    value=min_age,
                    metadata_record=record.name
                ))
            
            if max_age is not None:
                rules.append(ValidationRule(
                    rule_type=ValidationRuleType.RANGE,
                    field_name="POLICYHOLDER-AGE",
                    rule_name="AGE_MAX",
                    value=max_age,
                    metadata_record=record.name
                ))
        
        # VALIDATION-RULES: Format and length constraints
        elif record_name == "VALIDATION-RULES" or "RULES" in record_name:
            for line in record.lines:
                # Extract format rules
                if "POLICY-NUM-FORMAT" in line.upper() or "POLICY_NUM_FORMAT" in line.upper():
                    match = re.search(r"VALUE\s+['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
                    if match:
                        format_pattern = match.group(1)
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.FORMAT,
                            field_name="POLICY-NUMBER",
                            rule_name="POLICY_NUM_FORMAT",
                            value=format_pattern,
                            metadata_record=record.name
                        ))
                
                # Extract length constraints
                elif "NAME-MIN-LENGTH" in line.upper() or "NAME_MIN_LENGTH" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        min_length = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.RANGE,
                            field_name="POLICYHOLDER-NAME",
                            rule_name="NAME_MIN_LENGTH",
                            value=min_length,
                            metadata_record=record.name
                        ))
                
                elif "NAME-MAX-LENGTH" in line.upper() or "NAME_MAX_LENGTH" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        max_length = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.RANGE,
                            field_name="POLICYHOLDER-NAME",
                            rule_name="NAME_MAX_LENGTH",
                            value=max_length,
                            metadata_record=record.name
                        ))
                
                elif "PREMIUM-MIN-AMOUNT" in line.upper() or "PREMIUM_MIN_AMOUNT" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        min_amount = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.RANGE,
                            field_name="PREMIUM-AMOUNT",
                            rule_name="PREMIUM_MIN",
                            value=min_amount,
                            metadata_record=record.name
                        ))
                
                elif "DATE-FORMAT" in line.upper() or "DATE_FORMAT" in line.upper():
                    match = re.search(r"VALUE\s+['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
                    if match:
                        date_format = match.group(1)
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.FORMAT,
                            field_name="ISSUE-DATE",
                            rule_name="DATE_FORMAT",
                            value=date_format,
                            metadata_record=record.name
                        ))
        
        # ANOMALY-THRESHOLDS: Threshold values for anomaly detection
        elif record_name == "ANOMALY-THRESHOLDS" or "THRESHOLDS" in record_name:
            for line in record.lines:
                if "AGE-SUSPICIOUS-LOW" in line.upper() or "AGE_SUSPICIOUS_LOW" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        threshold = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.THRESHOLD,
                            field_name="POLICYHOLDER-AGE",
                            rule_name="AGE_SUSPICIOUS_LOW",
                            value=threshold,
                            metadata_record=record.name
                        ))
                
                elif "AGE-SUSPICIOUS-HIGH" in line.upper() or "AGE_SUSPICIOUS_HIGH" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        threshold = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.THRESHOLD,
                            field_name="POLICYHOLDER-AGE",
                            rule_name="AGE_SUSPICIOUS_HIGH",
                            value=threshold,
                            metadata_record=record.name
                        ))
                
                elif "PREMIUM-SUSPICIOUS" in line.upper() or "PREMIUM_SUSPICIOUS" in line.upper():
                    match = re.search(r'VALUE\s+(\d+)', line, re.IGNORECASE)
                    if match:
                        threshold = int(match.group(1))
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.THRESHOLD,
                            field_name="PREMIUM-AMOUNT",
                            rule_name="PREMIUM_SUSPICIOUS",
                            value=threshold,
                            metadata_record=record.name
                        ))
        
        # ANOMALY-DETECTION: Flags for anomaly detection
        elif record_name == "ANOMALY-DETECTION" or "DETECTION" in record_name:
            for line in record.lines:
                if "AGE-UNDER-5" in line.upper() or "AGE_UNDER_5" in line.upper():
                    match = re.search(r"VALUE\s+['\"]([NY])['\"]", line, re.IGNORECASE)
                    if match:
                        flag_value = match.group(1).upper() == 'Y'
                        rules.append(ValidationRule(
                            rule_type=ValidationRuleType.FLAG,
                            field_name="POLICYHOLDER-AGE",
                            rule_name="AGE_UNDER_5_FLAG",
                            value=flag_value,
                            metadata_record=record.name
                        ))
        
        # DATA-QUALITY-FLAGS: Missing data detection flags
        elif record_name == "DATA-QUALITY-FLAGS" or "QUALITY" in record_name:
            # These are flags indicating what to check for missing data
            # Not validation rules per se, but quality indicators
            pass  # Can be used for quality reporting
        
        return rules
    
    def validate_record(self, record: Dict[str, Any], encoding: str = "ascii") -> ValidationResult:
        """
        Validate a parsed record against extracted rules.
        
        Args:
            record: Parsed record (flattened dict with field names)
            encoding: Encoding used ("ascii", "ebcdic", "cp037", "cp1047")
        
        Returns:
            ValidationResult with validation status and issues
        """
        errors = []
        warnings = []
        anomalies = []
        quality_flags = {}
        details = {}
        
        # Normalize field names (handle both - and _)
        normalized_record = {}
        for key, value in record.items():
            normalized_key = key.replace('_', '-').upper()
            
            # Handle EBCDIC encoding - decode if needed
            if encoding.lower() in ("ebcdic", "cp037", "cp1047"):
                if isinstance(value, bytes):
                    try:
                        codepage = "cp037" if encoding.lower() == "ebcdic" or encoding.lower() == "cp037" else "cp1047"
                        value = codecs.decode(value, codepage)
                    except Exception:
                        pass  # Keep as bytes if decode fails
                elif isinstance(value, str):
                    # Value might already be decoded by Cobrix, but check for EBCDIC patterns
                    # If it contains non-printable or unusual characters, might need re-decoding
                    pass
            
            normalized_record[normalized_key] = value
        
        # Apply each rule
        for rule in self.rules:
            field_value = normalized_record.get(rule.field_name)
            
            if field_value is None:
                # Field missing - check if it's required
                if rule.rule_type in [ValidationRuleType.ALLOWED_VALUES, ValidationRuleType.FORMAT]:
                    errors.append(f"Required field '{rule.field_name}' is missing")
                continue
            
            # Apply rule based on type
            if rule.rule_type == ValidationRuleType.ALLOWED_VALUES:
                if isinstance(rule.value, list):
                    # Normalize value for comparison (strip whitespace)
                    normalized_value = str(field_value).strip() if field_value else ""
                    if normalized_value not in [v.strip() for v in rule.value]:
                        errors.append(
                            f"Field '{rule.field_name}' has invalid value '{field_value}'. "
                            f"Allowed values: {rule.value}"
                        )
            
            elif rule.rule_type == ValidationRuleType.RANGE:
                try:
                    numeric_value = int(field_value) if isinstance(field_value, str) else field_value
                    
                    if rule.rule_name.endswith("_MIN") or rule.rule_name.endswith("MIN"):
                        if numeric_value < rule.value:
                            errors.append(
                                f"Field '{rule.field_name}' value {numeric_value} is below minimum {rule.value}"
                            )
                    
                    elif rule.rule_name.endswith("_MAX") or rule.rule_name.endswith("MAX"):
                        if numeric_value > rule.value:
                            errors.append(
                                f"Field '{rule.field_name}' value {numeric_value} exceeds maximum {rule.value}"
                            )
                    
                    elif "MIN_LENGTH" in rule.rule_name:
                        if len(str(field_value)) < rule.value:
                            errors.append(
                                f"Field '{rule.field_name}' length {len(str(field_value))} is below minimum {rule.value}"
                            )
                    
                    elif "MAX_LENGTH" in rule.rule_name:
                        if len(str(field_value)) > rule.value:
                            warnings.append(
                                f"Field '{rule.field_name}' length {len(str(field_value))} exceeds maximum {rule.value}"
                            )
                
                except (ValueError, TypeError):
                    warnings.append(f"Field '{rule.field_name}' cannot be converted to number for range validation")
            
            elif rule.rule_type == ValidationRuleType.FORMAT:
                if rule.rule_name == "POLICY_NUM_FORMAT":
                    # Check if policy number matches expected format
                    # Format: 'POL###1234567890123456789' suggests POL + digits
                    if not str(field_value).upper().startswith("POL"):
                        errors.append(
                            f"Field '{rule.field_name}' does not match expected format (should start with 'POL')"
                        )
                
                elif rule.rule_name == "DATE_FORMAT":
                    # Check if date matches YYYYMMDD format
                    date_str = str(field_value).strip()
                    if len(date_str) != 8 or not date_str.isdigit():
                        errors.append(
                            f"Field '{rule.field_name}' does not match date format YYYYMMDD"
                        )
            
            elif rule.rule_type == ValidationRuleType.THRESHOLD:
                try:
                    numeric_value = int(field_value) if isinstance(field_value, str) else field_value
                    
                    if "SUSPICIOUS_LOW" in rule.rule_name:
                        if numeric_value < rule.value:
                            anomalies.append(
                                f"Field '{rule.field_name}' value {numeric_value} is suspiciously low (threshold: {rule.value})"
                            )
                    
                    elif "SUSPICIOUS_HIGH" in rule.rule_name:
                        if numeric_value > rule.value:
                            anomalies.append(
                                f"Field '{rule.field_name}' value {numeric_value} is suspiciously high (threshold: {rule.value})"
                            )
                    
                    elif "SUSPICIOUS" in rule.rule_name:
                        if numeric_value > rule.value:
                            anomalies.append(
                                f"Field '{rule.field_name}' value {numeric_value} exceeds suspicious threshold {rule.value}"
                            )
                
                except (ValueError, TypeError):
                    pass  # Skip threshold validation if not numeric
            
            elif rule.rule_type == ValidationRuleType.FLAG:
                # Flags indicate what to check, not validation rules
                quality_flags[rule.rule_name] = rule.value
        
        # Check for missing data (quality flags)
        for field_name in ["POLICY-NUMBER", "POLICYHOLDER-NAME", "POLICYHOLDER-AGE", 
                          "POLICY-TYPE", "PREMIUM-AMOUNT", "ISSUE-DATE"]:
            value = normalized_record.get(field_name)
            if not value or (isinstance(value, str) and value.strip() == ""):
                quality_flags[f"MISSING_{field_name.replace('-', '_')}"] = True
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            anomalies=anomalies,
            quality_flags=quality_flags,
            details={
                "rules_applied": len(self.rules),
                "encoding": encoding
            }
        )
    
    def validate_batch(self, records: List[Dict[str, Any]], encoding: str = "ascii") -> Dict[str, Any]:
        """
        Validate a batch of records and return summary statistics.
        
        Args:
            records: List of parsed records
            encoding: Encoding used
        
        Returns:
            Summary with validation statistics
        """
        results = []
        total_errors = 0
        total_warnings = 0
        total_anomalies = 0
        
        for i, record in enumerate(records):
            result = self.validate_record(record, encoding)
            results.append(result)
            total_errors += len(result.errors)
            total_warnings += len(result.warnings)
            total_anomalies += len(result.anomalies)
        
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count
        
        return {
            "total_records": len(records),
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "total_anomalies": total_anomalies,
            "validation_rate": valid_count / len(records) if records else 0.0,
            "results": results
        }

