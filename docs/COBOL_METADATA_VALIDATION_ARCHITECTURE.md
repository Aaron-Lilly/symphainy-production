# COBOL Metadata Validation Architecture

## Overview

This document describes the architecture for extracting and applying validation rules from COBOL copybook metadata records, similar to the legacy 88-field validation but adapted for the new architectural pattern.

## Problem Statement

COBOL copybooks often contain:
1. **Data records** (01-level) - The actual record structure
2. **Metadata records** (01-level) - Validation rules, thresholds, allowed values, flags

The legacy implementation used **level 88 fields** to define allowed values. Our copybook uses **metadata 01-level records** instead:
- `POLICY-TYPES` - Allowed policy type values
- `AGE-VALIDATION` - Min/max age, suspicious flags
- `VALIDATION-RULES` - Format patterns, length constraints
- `ANOMALY-THRESHOLDS` - Threshold values for anomaly detection
- `DATA-QUALITY-FLAGS` - Missing data indicators
- `ANOMALY-DETECTION` - Anomaly detection flags

## Architecture: Role=What, Service=How

### Role: Data Validator (WHAT)
**What:** Validates data quality, compliance, and business rules

### Service: Metadata Rule Extractor (HOW)
**How:** Extracts validation rules from copybook metadata and applies them to parsed records

## Implementation Layers

### 1. Metadata Extraction Layer
**Component:** `CobolMetadataValidator.extract_metadata_rules()`
- Analyzes copybook to identify metadata records
- Extracts VALUE clauses from metadata records
- Maps metadata fields to data record fields
- Creates `ValidationRule` objects

### 2. Rule Application Layer
**Component:** `CobolMetadataValidator.validate_record()`
- Applies rules to parsed records
- Handles both ASCII and EBCDIC encodings
- Returns `ValidationResult` with errors, warnings, anomalies

### 3. Integration Layer
**Component:** Integration with Content Steward / Validation Engine
- Extracts rules during copybook parsing
- Applies validation during/after parsing
- Stores validation results with parsed data

## Validation Rule Types

### 1. ALLOWED_VALUES
**Source:** `POLICY-TYPES` record
**Example:** Policy type must be one of: "Term Life", "Whole Life", "Universal", "Annuity"
**Application:** Check if `POLICY-TYPE` field value is in allowed list

### 2. RANGE
**Source:** `AGE-VALIDATION`, `VALIDATION-RULES` records
**Examples:**
- Age must be between MIN-AGE (5) and MAX-AGE (100)
- Name length must be between NAME-MIN-LENGTH (2) and NAME-MAX-LENGTH (30)
- Premium must be >= PREMIUM-MIN-AMOUNT (1000)
**Application:** Check numeric/length values against min/max constraints

### 3. FORMAT
**Source:** `VALIDATION-RULES` record
**Examples:**
- Policy number format: "POL###1234567890123456789" (must start with "POL")
- Date format: "YYYYMMDD" (8 digits)
**Application:** Check string patterns, formats

### 4. THRESHOLD
**Source:** `ANOMALY-THRESHOLDS` record
**Examples:**
- AGE-SUSPICIOUS-LOW: 5 (flag if age < 5)
- AGE-SUSPICIOUS-HIGH: 100 (flag if age > 100)
- PREMIUM-SUSPICIOUS: 100000 (flag if premium > 100000)
**Application:** Detect anomalies (warnings, not errors)

### 5. FLAG
**Source:** `ANOMALY-DETECTION`, `DATA-QUALITY-FLAGS` records
**Examples:**
- AGE-UNDER-5: 'Y' (check for ages under 5)
- MISSING-POLICY-NUM: 'N' (check for missing policy numbers)
**Application:** Quality indicators, not validation rules

## Integration Points

### Option 1: Content Steward Integration (Recommended)
**Location:** `content_steward/modules/content_validation.py`
**Approach:**
```python
# In Content Steward's parse_file method
async def parse_file(self, file_id: str, copybook_id: str, ...):
    # Parse file
    parsed_data = await self.parse_binary_file(file_id, copybook_id)
    
    # Extract validation rules from copybook
    validator = CobolMetadataValidator()
    rules = validator.extract_metadata_rules(copybook_content)
    
    # Validate parsed records
    validation_results = validator.validate_batch(parsed_data["records"])
    
    # Return parsed data with validation results
    return {
        "records": parsed_data["records"],
        "validation": validation_results
    }
```

### Option 2: Validation Engine Service Integration
**Location:** `validation_engine_service/`
**Approach:**
```python
# In Validation Engine Service
async def validate_cobol_data(self, file_id: str, copybook_id: str, ...):
    # Get parsed data
    parsed_data = await content_steward.get_parsed_file(file_id)
    
    # Get copybook
    copybook = await content_steward.get_file(copybook_id)
    
    # Extract and apply rules
    validator = CobolMetadataValidator()
    rules = validator.extract_metadata_rules(copybook["content"])
    results = validator.validate_batch(parsed_data["records"])
    
    return results
```

### Option 3: Cobrix Parser Integration (Current)
**Location:** `services/cobrix-parser/app/server.py`
**Approach:**
```python
# In parse_cobol endpoint
@app.post("/parse/cobol")
async def parse_cobol(file: UploadFile, copybook: UploadFile):
    # Parse with Cobrix
    records = await parse_with_cobrix(file, copybook)
    
    # Extract validation rules
    copybook_content = await copybook.read()
    validator = CobolMetadataValidator()
    rules = validator.extract_metadata_rules(copybook_content.decode())
    
    # Validate records
    validation_results = validator.validate_batch(records)
    
    return {
        "records": records,
        "validation": validation_results
    }
```

## Encoding Support

### ASCII
- Field values are already decoded as strings
- Direct string comparison for allowed values
- Numeric conversion for range/threshold validation

### EBCDIC
- Field values may need EBCDIC-to-ASCII conversion
- Use `codecs.decode(value, 'cp037')` or `'cp1047'` before validation
- Same validation logic applies after conversion

## Example Usage

```python
from cobol_metadata_validator import CobolMetadataValidator

# Initialize validator
validator = CobolMetadataValidator()

# Extract rules from copybook
with open("scenario3_copybook.txt", "r") as f:
    copybook_content = f.read()
rules = validator.extract_metadata_rules(copybook_content)

# Validate a record
record = {
    "POLICY_NUMBER": "POL001123456789012345",
    "POLICYHOLDER_NAME": "John Smith",
    "POLICYHOLDER_AGE": 45,
    "POLICY_TYPE": "Term Life",
    "PREMIUM_AMOUNT": 50000,
    "ISSUE_DATE": "20240115"
}

result = validator.validate_record(record, encoding="ascii")
print(f"Valid: {result.is_valid}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
print(f"Anomalies: {result.anomalies}")
```

## Comparison with Legacy 88-Field Validation

### Legacy Approach
- **88-level fields** define allowed values for a parent field
- **value_to_names mapping** maps values to descriptive names
- **mapper** lists all allowed values for a field

### New Approach
- **Metadata 01-level records** define validation rules
- **ValidationRule objects** represent different rule types
- **More flexible** - supports ranges, formats, thresholds, not just allowed values

### Advantages
1. **More expressive** - Can define ranges, formats, thresholds
2. **Better organized** - Rules grouped by purpose (validation, thresholds, flags)
3. **Easier to extend** - Add new rule types without changing structure
4. **Works with both** - Supports both 88-field and metadata-record patterns

## Future Enhancements

1. **88-Field Support** - Also extract rules from 88-level fields (backward compatibility)
2. **Custom Rule Definitions** - Allow users to define custom validation rules
3. **Rule Composition** - Combine multiple rules (AND/OR logic)
4. **Performance Optimization** - Cache extracted rules, batch validation
5. **Validation Reporting** - Generate detailed validation reports with statistics











