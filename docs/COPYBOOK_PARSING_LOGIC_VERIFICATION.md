# Copybook Parsing Logic Verification

**Date:** December 22, 2025  
**Status:** ✅ **ALL LOGIC PRESERVED**

---

## 🎯 Verification Summary

**Question:** Are all the copybook parsing logic features preserved after moving copybook loading to FileParserService?

**Answer:** ✅ **YES - All logic is preserved and intact**

---

## ✅ Copybook Parsing Features Verified

### **1. Column Position Handling (6-72 / 6-71)**

**Location:** `mainframe_processing_adapter.py` → `_clean_cobol()` method (lines 330-362)

**What it does:**
- ✅ Slices columns 6-72 from each COBOL line (COBOL standard)
  - Columns 1-5: Line numbers (ignored)
  - Columns 6-72: Actual COBOL code
  - Column 73+: Comments (ignored)
- ✅ Handles continuation lines (fields spanning multiple physical lines)
- ✅ Joins continuation lines until a period (`.`) is found
- ✅ Skips empty lines and comments (lines starting with `*` or `/`)
- ✅ Warns about unfinished lines

**Code:**
```python
def _clean_cobol(self, lines: List[str]) -> List[str]:
    for row in lines:
        # Legacy approach: directly slice columns 6-72 (COBOL standard)
        row = row[6:72].rstrip()
        # ... handles continuation lines, comments, etc.
```

**Status:** ✅ **PRESERVED** - Called by `_parse_copybook_from_string()` which receives the copybook content string

---

### **2. PIC Code Parsing**

**Location:** `mainframe_processing_adapter.py` → `_parse_pic_clause()` method (lines 655-706)

**What it does:**
- ✅ Expands repeating patterns: `9(5)` → `99999`
- ✅ Detects data types:
  - `float`: Patterns like `9V99`, `S9(5)V99`
  - `integer`: Patterns like `S9(5)`, `9(10)`
  - `string`: Everything else (X, A, etc.)
- ✅ Handles signed fields: Detects `S` prefix
- ✅ Calculates precision: Counts digits after `V` (decimal point)
- ✅ Calculates field length: Total length of expanded PIC string

**Code:**
```python
def _parse_pic_clause(self, pic_str: str) -> Dict[str, Any]:
    # Expand repeats: 9(5) → 99999
    pic_pattern_repeats = re.compile(r"(.)\((\d+)\)")
    expanded_pic = pic_pattern_repeats.sub(...)
    
    # Detect type: float, integer, string
    pic_pattern_float = re.compile(r"[+-S]?[9Z]*[.V][9Z]+")
    pic_pattern_integer = re.compile(r"S?[9Z]+")
    
    # Calculate precision (digits after V)
    if 'V' in expanded_pic:
        parts = expanded_pic.split('V')
        precision = len(parts[1])
```

**Status:** ✅ **PRESERVED** - Called by `_parse_field_definition()` during copybook parsing

---

### **3. OCCURS Clause Handling**

**Location:** `mainframe_processing_adapter.py` → `_handle_occurs()` and `_denormalize_cobol()` methods (lines 382-474)

**What it does:**
- ✅ Flattens OCCURS clauses into multiple field instances
- ✅ Handles nested OCCURS (recursive)
- ✅ Adds postfixes to field names: `FIELD-1`, `FIELD-2`, etc.
- ✅ Handles OCCURS with PIC (repeats the field)
- ✅ Handles OCCURS without PIC (recursively processes subgroup)
- ✅ Adjusts field levels during expansion

**Code:**
```python
def _handle_occurs(self, lines, occurs, level_diff=0, name_postfix=""):
    for i in range(1, occurs + 1):
        # Add postfix: "-1", "-2", etc.
        new_name_postfix = name_postfix + "-" + str(i)
        # ... recursively processes fields
```

**Status:** ✅ **PRESERVED** - Called by `_parse_copybook_from_string()` after parsing field definitions

---

### **4. REDEFINES Clause Handling**

**Location:** `mainframe_processing_adapter.py` → `_parse_copybook_from_string()` method (lines 551-580)

**What it does:**
- ✅ Removes the field being redefined
- ✅ Removes the subgroup (all fields with higher level)
- ✅ Replaces with the REDEFINES field
- ✅ Handles nested REDEFINES

**Code:**
```python
redefines = field_def.get("redefines")
if redefines:
    # Find the field being redefined
    # Get subgroup (all fields with higher level)
    # Remove redefined field and its subgroup
    # Replace with REDEFINES field
```

**Status:** ✅ **PRESERVED** - Handled during field definition parsing

---

### **5. FILLER Field Handling**

**Location:** `mainframe_processing_adapter.py` → `_rename_filler_fields()` method (lines 476-487)

**What it does:**
- ✅ Renames FILLER fields to `FILLER_1`, `FILLER_2`, etc.
- ✅ Prevents duplicate field names

**Code:**
```python
def _rename_filler_fields(self, field_definitions):
    filler_counter = 1
    for field_def in field_definitions:
        if field_def.get("name", "").upper() == "FILLER":
            field_def["name"] = f"FILLER_{filler_counter}"
            filler_counter += 1
```

**Status:** ✅ **PRESERVED** - Called by `_parse_copybook_from_string()` after OCCURS denormalization

---

### **6. COMP-3, COMP, BINARY Handling**

**Location:** `mainframe_processing_adapter.py` → Multiple locations

**What it does:**
- ✅ Detects COMP-3 (packed decimal/BCD): `" COMP-3"` in line
- ✅ Detects COMP: `" COMP"` in line
- ✅ Detects BINARY: `" BINARY"` in line
- ✅ Adjusts field lengths for packed formats:
  - COMP-3: `ceil((field_length + 1) / 2)` bytes
  - COMP/BINARY: Uses `_get_len_for_comp_binary()` for byte length calculation
- ✅ Marks fields with `is_bcd`, `is_comp`, `is_binary` flags

**Code:**
```python
# Detect COMP-3 before pattern matching
is_comp3 = " COMP-3" in line or " COMP-3." in line

# Adjust length for COMP-3 (packed decimal)
if pic_info.get('is_bcd'):
    field_length = int(math.ceil((field_length + 1) / 2))
```

**Status:** ✅ **PRESERVED** - Handled during field definition parsing and binary record parsing

---

## 📋 Copybook Content Extraction Flow

### **New Flow (FileParserService handles loading):**

```
Frontend
  ↓ copybook_file_id
ContentJourneyOrchestrator
  ↓ copybook_file_id in parse_options
FileParserService.parse_file()
  ↓ detects copybook_file_id
  ↓ retrieves copybook document via file_retrieval_module
  ↓ extracts copybook content (file_content, data, or content field)
  ↓ decodes to string (UTF-8 or Latin-1)
  ↓ adds to parse_options as "copybook" (string)
  ↓ continues to parsing orchestrator
MainframeProcessingAbstraction.parse_file()
  ↓ receives "copybook" (string) in request.options
  ↓ calls adapter.parse_file(file_data, filename, copybook_data.encode())
MainframeProcessingAdapter.parse_file()
  ↓ decodes copybook_data to string
  ↓ calls _parse_copybook_from_string(copybook_content)
  ↓ calls _clean_cobol() → handles columns 6-72
  ↓ parses field definitions → handles PIC, OCCURS, REDEFINES
  ↓ calls _denormalize_cobol() → handles OCCURS expansion
  ↓ calls _rename_filler_fields() → handles FILLER
  ↓ returns field_definitions
  ↓ parses binary records using field definitions
```

### **Key Points:**

1. ✅ **Column 6-72 handling preserved**: `_clean_cobol()` is still called with the copybook content string
2. ✅ **PIC parsing preserved**: `_parse_pic_clause()` is still called during field definition parsing
3. ✅ **OCCURS handling preserved**: `_denormalize_cobol()` is still called after parsing
4. ✅ **REDEFINES preserved**: Handled during field definition parsing
5. ✅ **FILLER handling preserved**: `_rename_filler_fields()` is still called
6. ✅ **COMP-3/COMP/BINARY preserved**: Detected and handled during parsing

---

## ✅ Verification Checklist

- [x] Column 6-72 slicing (`_clean_cobol`)
- [x] Continuation line handling
- [x] Comment skipping (`*`, `/`)
- [x] PIC code parsing (`_parse_pic_clause`)
- [x] PIC expansion (`9(5)` → `99999`)
- [x] Data type detection (float, integer, string)
- [x] Signed field handling (`S` prefix)
- [x] Precision calculation (`V` decimal point)
- [x] OCCURS clause handling (`_handle_occurs`, `_denormalize_cobol`)
- [x] OCCURS expansion (field repetition)
- [x] Nested OCCURS (recursive)
- [x] REDEFINES clause handling
- [x] FILLER field renaming (`_rename_filler_fields`)
- [x] COMP-3 detection and length adjustment
- [x] COMP detection and length adjustment
- [x] BINARY detection and length adjustment

---

## 🔍 Code Locations

**All parsing logic is in:**
- `/home/founders/demoversion/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/mainframe_processing_adapter.py`

**Key methods:**
- `_clean_cobol()` - Lines 330-362 (column 6-72 handling)
- `_parse_copybook_from_string()` - Lines 489-603 (main parsing entry point)
- `_parse_pic_clause()` - Lines 655-706 (PIC code parsing)
- `_handle_occurs()` - Lines 382-462 (OCCURS expansion)
- `_denormalize_cobol()` - Lines 464-474 (OCCURS denormalization)
- `_rename_filler_fields()` - Lines 476-487 (FILLER renaming)
- `_parse_field_definition()` - Lines 605-653 (field definition parsing)

**Copybook loading (new location):**
- `/home/founders/demoversion/symphainy_source/symphainy-platform/backend/content/services/file_parser_service/modules/file_parsing.py` - Lines 117-144

---

## ✅ Conclusion

**All copybook parsing logic is preserved and intact.**

The move to FileParserService only changed **where** the copybook content is loaded (from orchestrator to service), but **all the parsing logic remains unchanged** in `MainframeProcessingAdapter`.

The copybook content is still passed as a string to `_parse_copybook_from_string()`, which then:
1. Calls `_clean_cobol()` → handles columns 6-72
2. Parses field definitions → handles PIC, OCCURS, REDEFINES, COMP-3, etc.
3. Calls `_denormalize_cobol()` → handles OCCURS expansion
4. Calls `_rename_filler_fields()` → handles FILLER

**No parsing logic was lost or modified.**

---

**Last Updated:** December 22, 2025  
**Status:** ✅ **ALL LOGIC VERIFIED AND PRESERVED**



