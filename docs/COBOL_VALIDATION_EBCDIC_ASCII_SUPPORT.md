# COBOL Validation: EBCDIC and ASCII Support

## Overview

The Cobrix parsing solution now supports both EBCDIC and ASCII encodings with comprehensive validation:

1. **EBCDIC Support** - With 88-level field validation (legacy pattern)
2. **ASCII Support** - With metadata 01-level record validation (new pattern)
3. **Automatic Encoding Detection** - Detects encoding from file content
4. **Unified Validation** - Single validator handles both patterns

## Architecture

### Encoding Detection
**Component:** `server.py._detect_encoding()`
- Analyzes file byte patterns
- Detects EBCDIC (cp037, cp1047) vs ASCII
- Returns encoding string for Cobrix

### Validation Rule Extraction
**Components:**
- `cobol_88_field_extractor.py` - Extracts 88-level field rules (EBCDIC pattern)
- `cobol_metadata_validator.py` - Extracts metadata record rules (ASCII pattern) + 88-fields

### Rule Application
**Component:** `CobolMetadataValidator.validate_record()`
- Handles both ASCII and EBCDIC encodings
- Applies all extracted rules (88-fields + metadata records)
- Returns comprehensive validation results

## Validation Patterns

### Pattern 1: 88-Level Fields (EBCDIC/Legacy)
```cobol
05  STATUS-CODE    PIC X(1).
    88  ACTIVE      VALUE 'A'.
    88  INACTIVE    VALUE 'I'.
    88  PENDING     VALUE 'P'.
```

**Extraction:**
- Extracts allowed values: ['A', 'I', 'P']
- Creates value_to_names mapping: {'A': 'ACTIVE', 'I': 'INACTIVE', 'P': 'PENDING'}
- Creates ValidationRule with ALLOWED_VALUES type

### Pattern 2: Metadata Records (ASCII/New)
```cobol
01  POLICY-TYPES.
    05  TERM-LIFE    PIC X(10) VALUE 'Term Life  '.
    05  WHOLE-LIFE   PIC X(10) VALUE 'Whole Life '.
```

**Extraction:**
- Extracts allowed values: ['Term Life', 'Whole Life']
- Creates ValidationRule with ALLOWED_VALUES type
- Maps to POLICY-TYPE field in data record

## Encoding Handling

### EBCDIC (cp037, cp1047)
1. **Detection:** Analyzes byte patterns (0xF0-0xF9 for digits, 0xC1-0xE9 for letters)
2. **Parsing:** Cobrix decodes EBCDIC to Unicode automatically
3. **Validation:** Values are already decoded, validation works on Unicode strings
4. **88-Fields:** Extracted from copybook, applied to decoded values

### ASCII
1. **Detection:** Analyzes byte patterns (0x20-0x7E printable range)
2. **Parsing:** Cobrix reads ASCII directly
3. **Validation:** Values are strings, validation works directly
4. **Metadata Records:** Extracted from copybook, applied to string values

## Implementation Flow

```
1. File Upload
   ↓
2. Encoding Detection (_detect_encoding)
   ↓
3. Copybook Analysis
   ├─ Extract data record (copybook_analyzer)
   ├─ Extract 88-level fields (cobol_88_field_extractor) ← EBCDIC pattern
   └─ Extract metadata records (cobol_metadata_validator) ← ASCII pattern
   ↓
4. Cobrix Parsing (with detected encoding)
   ↓
5. Record Validation
   ├─ Apply 88-field rules (if extracted)
   └─ Apply metadata record rules (if extracted)
   ↓
6. Return Results (with validation)
```

## Example: EBCDIC File with 88-Fields

```python
# Copybook has 88-level fields
copybook = """
05  STATUS-CODE    PIC X(1).
    88  ACTIVE      VALUE 'A'.
    88  INACTIVE    VALUE 'I'.
"""

# File is EBCDIC encoded
# Encoding detected: "cp037"

# Validation extracts:
rules = [
    ValidationRule(
        rule_type=ALLOWED_VALUES,
        field_name="STATUS-CODE",
        rule_name="STATUS_CODE_88_ALLOWED",
        value=['A', 'I'],
        metadata_record="88-LEVEL-FIELDS"
    )
]

# Validates decoded records
result = validator.validate_record(record, encoding="cp037")
```

## Example: ASCII File with Metadata Records

```python
# Copybook has metadata records
copybook = """
01  POLICYHOLDER-RECORD.
    05  POLICY-TYPE    PIC X(10).

01  POLICY-TYPES.
    05  TERM-LIFE    PIC X(10) VALUE 'Term Life  '.
    05  WHOLE-LIFE   PIC X(10) VALUE 'Whole Life '.
"""

# File is ASCII encoded
# Encoding detected: "ascii"

# Validation extracts:
rules = [
    ValidationRule(
        rule_type=ALLOWED_VALUES,
        field_name="POLICY-TYPE",
        rule_name="POLICY_TYPE_ALLOWED",
        value=['Term Life', 'Whole Life'],
        metadata_record="POLICY-TYPES"
    )
]

# Validates records
result = validator.validate_record(record, encoding="ascii")
```

## Combined Support

The validator can handle **both patterns simultaneously**:

```python
# Copybook has both 88-fields AND metadata records
validator = CobolMetadataValidator()
rules = validator.extract_metadata_rules(copybook_content, extract_88_fields=True)

# Rules include:
# - 88-level field rules (from 88-fields)
# - Metadata record rules (from 01-level metadata records)

# Validation applies all rules
result = validator.validate_record(record, encoding=detected_encoding)
```

## API Response

```json
{
  "success": true,
  "records": [...],
  "validation": {
    "total_records": 10,
    "valid_records": 8,
    "invalid_records": 2,
    "total_errors": 3,
    "total_warnings": 1,
    "total_anomalies": 2,
    "validation_rate": 0.8
  },
  "metadata": {
    "record_count": 10,
    "encoding": "cp037",  // or "ascii"
    "parser": "cobrix",
    "parser_version": "2.9.0"
  }
}
```

## Testing

### Test EBCDIC with 88-Fields
1. Upload EBCDIC file (cp037 or cp1047)
2. Copybook with 88-level fields
3. Verify encoding detection = "cp037" or "cp1047"
4. Verify 88-field rules extracted
5. Verify validation applied

### Test ASCII with Metadata Records
1. Upload ASCII file
2. Copybook with metadata 01-level records
3. Verify encoding detection = "ascii"
4. Verify metadata rules extracted
5. Verify validation applied

### Test Combined
1. Copybook with both 88-fields and metadata records
2. Verify both rule types extracted
3. Verify all rules applied during validation












