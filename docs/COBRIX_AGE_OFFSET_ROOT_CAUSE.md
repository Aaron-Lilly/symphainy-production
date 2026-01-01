# Cobrix AGE Field Offset Root Cause Analysis

**Date:** December 28, 2025  
**Status:** 🔍 **INVESTIGATION**

---

## 🎯 Problem

Cobrix is reading the AGE field from the wrong byte position:
- **Expected:** Bytes 50-52 = "045"
- **Actual:** Bytes 51-53 = "45T" (last 2 digits of AGE + first letter of POLICY_TYPE)

This is a **1-byte offset** that cascades through all subsequent fields.

---

## 🔍 Root Cause Investigation

### Hypothesis 1: Copybook Field Definition Issue

**Theory:** Cobrix might be interpreting the copybook field positions incorrectly.

**Copybook Structure:**
```
01  POLICYHOLDER-RECORD.
    05  POLICY-NUMBER      PIC X(20).
    05  POLICYHOLDER-NAME  PIC X(30).
    05  POLICYHOLDER-AGE   PIC X(3).    # Changed from PIC 9(3) to PIC X(3)
    05  POLICY_TYPE        PIC X(10).
    05  PREMIUM-AMOUNT      PIC 9(10).
    05  ISSUE-DATE          PIC X(8).
```

**Expected Byte Positions:**
- POLICY_NUMBER: bytes 0-19 (20 bytes)
- POLICYHOLDER_NAME: bytes 20-49 (30 bytes)
- AGE: bytes 50-52 (3 bytes)
- POLICY_TYPE: bytes 53-62 (10 bytes)

**Cobrix is reading:**
- AGE: bytes 51-53 = "45T"

**Possible Causes:**
1. Cobrix might be adding a 1-byte offset for some reason
2. The copybook preprocessing might be introducing an offset
3. Cobrix might be interpreting field positions differently

---

### Hypothesis 2: Copybook Preprocessing Issue

**Theory:** Our copybook cleaning might be introducing an offset.

**What we're doing:**
1. Changing `POLICYHOLDER-AGE` to `POLICYHOLDER_AGE`
2. Changing `PIC 9(3)` to `PIC X(3)`
3. Removing 88-level fields
4. Stripping identifiers

**Possible Issues:**
- Field name changes might affect Cobrix's internal field position calculations
- The underscore vs hyphen might cause Cobrix to recalculate positions

---

### Hypothesis 3: Cobrix Internal Field Position Calculation

**Theory:** Cobrix might be calculating field positions differently than expected.

**Possible Causes:**
1. Cobrix might be using 1-based indexing instead of 0-based
2. Cobrix might be adding padding/alignment bytes
3. Cobrix might be interpreting the copybook hierarchy differently

---

## 🔬 Investigation Steps

### Step 1: Check Copybook After Preprocessing

```bash
docker logs symphainy-cobrix-parser | grep "Full cleaned copybook"
```

**What to look for:**
- Is the AGE field definition correct?
- Are field positions correct?
- Is there any unexpected formatting?

---

### Step 2: Compare with Homegrown Solution

**Homegrown Solution Approach:**
- Reads fields sequentially from byte positions
- Uses explicit byte offsets: `field_start = previous_field_start + previous_field_length`
- No field position calculation - just direct byte reading

**Cobrix Approach:**
- Parses copybook and calculates field positions internally
- Uses Spark DataFrame schema
- Field positions are inferred from copybook structure

**Key Difference:**
- Homegrown: **Explicit byte positions** (we control exactly where to read)
- Cobrix: **Inferred positions** (Cobrix calculates from copybook)

---

### Step 3: Test with Minimal Copybook

**Test:** Create a minimal copybook with just AGE field to see if Cobrix reads it correctly.

```cobol
01  TEST-RECORD.
    05  POLICYHOLDER-AGE   PIC X(3).
```

**Expected:** Cobrix should read bytes 0-2 correctly.

**If this works:** The issue is with field position calculation in a multi-field record.

**If this fails:** The issue is with how Cobrix interprets `PIC X(3)`.

---

## 💡 Potential Solutions

### Solution 1: Fix Copybook Definition

**If the issue is with field positions:**
- Ensure copybook has correct field definitions
- Check for any hidden characters or formatting issues
- Verify field lengths match exactly

### Solution 2: Use Homegrown Solution

**If Cobrix's field position calculation is unreliable:**
- Switch to homegrown solution which uses explicit byte positions
- Homegrown solution already works for EBCDIC
- We've solved ASCII parsing issues (data start detection, prefix stripping)

**Pros:**
- ✅ Explicit control over byte positions
- ✅ Already working for EBCDIC
- ✅ Simpler, no Spark dependency
- ✅ Faster iteration

**Cons:**
- ⚠️ Not industry-standard
- ⚠️ We own maintenance

### Solution 3: Hybrid Approach

**Use homegrown for:**
- Files where field alignment is critical
- Files with complex preprocessing needs
- Small-medium files

**Use Cobrix for:**
- Very large files (if needed)
- Files with complex COBOL features (COMP-3, REDEFINES, etc.)
- When we need industry-standard solution

---

## 🎯 Recommendation

**For extensible patterns:** **Use Homegrown Solution**

**Reasons:**
1. ✅ **Explicit byte positions** - We control exactly where fields are read
2. ✅ **Already working** - EBCDIC parsing works, ASCII parsing issues solved
3. ✅ **Simpler** - No Spark, no complex preprocessing
4. ✅ **Faster iteration** - Pure Python, easier to debug
5. ✅ **Extensible** - Easy to add new features or handle edge cases

**The 1-byte offset in Cobrix suggests:**
- Cobrix's internal field position calculation is not matching our expectations
- This could be due to copybook format, field name changes, or Cobrix's internal logic
- Fixing this would require deep understanding of Cobrix's internals
- This is not extensible - it's a one-off fix for this specific case

**Homegrown solution:**
- We explicitly define byte positions
- We can easily adjust if needed
- We understand exactly what's happening
- This is extensible - we can handle any field layout

---

## 📋 Next Steps

1. **Test homegrown solution** with the ASCII file
2. **Verify field alignment** is correct
3. **If it works, switch to homegrown** for extensible, maintainable solution
4. **Keep Cobrix as fallback** for very large files or complex COBOL features

---

## 🔧 Quick Test

To test if homegrown solution works with ASCII:

```python
# Use MainframeProcessingAdapter
adapter = MainframeProcessingAdapter()
result = await adapter.parse_file(
    file_data=ascii_file_bytes,
    filename="test.txt",
    copybook_content=copybook_text
)
```

**Expected:** All fields correctly aligned, AGE reads as "045" not "45T".










