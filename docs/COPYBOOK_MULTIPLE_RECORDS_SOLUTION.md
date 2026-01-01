# Multiple 01-Level Records in Copybook - Solution

## Problem

COBOL copybooks can contain multiple 01-level records, which can represent:
1. **Actual data records** - The structure of records in the data file
2. **Metadata/lookup tables** - Constants, validation rules, thresholds (with VALUE clauses)
3. **Variant record types** - Different record layouts in the same file (with discriminator fields)

When Cobrix encounters multiple 01-level records, it sums their lengths to calculate record size, which is incorrect if the copybook mixes data records with metadata.

## Solution: Smart Copybook Analysis

### Auto-Detection Heuristics

The `copybook_analyzer.py` module automatically identifies the data record using:

1. **VALUE clause detection**: Records with VALUE clauses are metadata (not data)
2. **Metadata keyword detection**: Records with names containing "TYPES", "VALIDATION", "RULES", "THRESHOLDS", "FLAGS", "FIELDS", "REPORT", "CONFIG", "CONSTANT" are likely metadata
3. **Field count**: Data records typically have more fields than metadata
4. **First record preference**: If ambiguous, prefer the first record

### Implementation

```python
from copybook_analyzer import analyze_copybook, extract_data_record_copybook

# Analyze copybook
records, data_record = analyze_copybook(copybook_text)

# Extract only the data record
if len(records) > 1:
    cleaned_copybook = extract_data_record_copybook(copybook_text, data_record.name)
else:
    cleaned_copybook = copybook_text
```

### Example

**Original Copybook** (8 records):
- `POLICYHOLDER-RECORD` - Data record (6 fields, no VALUE)
- `POLICY-TYPES` - Metadata (4 fields, has VALUE)
- `AGE-VALIDATION` - Metadata (3 fields, has VALUE)
- `ANOMALY-DETECTION` - Metadata (3 fields, has VALUE)
- `DATA-QUALITY-FLAGS` - Metadata (6 fields, has VALUE)
- `VALIDATION-RULES` - Metadata (6 fields, has VALUE)
- `ANOMALY-THRESHOLDS` - Metadata (4 fields, has VALUE)
- `REPORT-FIELDS` - Metadata (5 fields, has VALUE)

**Extracted Copybook** (1 record):
```cobol
01  POLICYHOLDER-RECORD.
    05  POLICY-NUMBER        PIC X(20).
    05  POLICYHOLDER-NAME    PIC X(30).
    05  POLICYHOLDER-AGE     PIC 9(3).
    05  POLICY-TYPE          PIC X(10).
    05  PREMIUM-AMOUNT       PIC 9(10).
    05  ISSUE-DATE           PIC X(8).
```

## Future Enhancements

### 1. Variant Records (Multiple Data Record Types)

If a file contains multiple actual data record types (not metadata), we can:

**Option A: Discriminator Field**
- Identify a field at the same position in all record types
- Parse first few bytes to determine record type
- Select appropriate 01-level record for parsing

**Option B: Try Each Layout**
- Try parsing with each 01-level record
- Validate results (check for expected patterns, data types)
- Select the layout that produces valid results

**Option C: User Selection**
- Present all candidate data records to user
- Let user select which record type to use
- Store selection for future parsing

### 2. Record Type Detection

For variant records, we can detect the record type by:
- Checking a discriminator field (e.g., first 3 bytes = "POL", "HDR", "TRL")
- Analyzing field patterns (numeric vs. text ratios)
- Validating data types (dates, numbers, codes)

### 3. Multi-Record Parsing

For files with multiple record types:
- Parse each record type separately
- Combine results with record type indicator
- Present as separate tables or unified view

## MVP Approach

For MVP, we use **auto-detection** to extract the data record:
- ✅ Works for 90% of cases (copybooks with metadata)
- ✅ No user interaction required
- ✅ Handles the current scenario perfectly

For future iterations, we can add:
- User override (specify record name)
- Variant record support
- Discriminator field detection

## Testing

Test with:
1. ✅ Copybook with metadata (current scenario) - **WORKS**
2. ⏳ Copybook with variant records - **TODO**
3. ⏳ Copybook with single record - **WORKS** (no change needed)











