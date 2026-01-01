# ASCII Parsing Root Cause Analysis

**Date:** December 28, 2025  
**Status:** 🔍 **ROOT CAUSE IDENTIFIED**

---

## 🎯 The Real Problem

**Neither solution works for ASCII files because we're fundamentally misunderstanding the file format.**

---

## 🔍 What We Discovered

### **The ASCII Test File Structure**

Looking at the test file creation script (`scripts/upload_clean_files_internal.py`):

```python
records = [
    b"POL001123456789012345" + b"John Smith                  " + b"045" + ...
]
```

**Key Insight:** `"POL001123456789012345"` is **20 bytes total** - this is the **entire POLICY-NUMBER field**, not a prefix!

The copybook says:
```cobol
05  POLICY-NUMBER        PIC X(20).
```

So:
- **POL001** (6 bytes) + **123456789012345** (14 bytes) = **20 bytes** = **POLICY-NUMBER field**

### **What We're Doing Wrong**

1. **We're trying to strip "POL001" as a record prefix**
   - But "POL001" is actually **part of the POLICY-NUMBER field data**
   - After stripping, we're misaligned by 6 bytes
   - This causes all subsequent fields to be misaligned

2. **We're overcomplicating the normalization**
   - The file format normalizer tries to:
     - Find data start (good)
     - Remove newlines (good)
     - Strip record prefixes (WRONG - "POL001" is part of the data)
   - This causes misalignment

3. **We're confusing record identifiers with field data**
   - "POL001" looks like a record identifier (POL + number)
   - But it's actually the first 6 bytes of the POLICY-NUMBER field
   - The pattern "POL001", "POL002", "POL003" is just how the test data was generated

---

## 💡 Why This Is So Difficult

### **The Fundamental Issue**

**ASCII files aren't pure binary fixed-width files** - they're **hybrid text/binary files** with:
1. **Headers/comments** (hash tags, descriptive text)
2. **Newlines** (text format, not binary)
3. **Embedded patterns** that look like record identifiers but are actually field data

### **Why EBCDIC Works But ASCII Doesn't**

**EBCDIC files:**
- ✅ Pure binary format (no newlines, no headers)
- ✅ Records are concatenated without delimiters
- ✅ File size = N * record_size (perfectly divisible)
- ✅ No embedded text patterns to confuse detection

**ASCII files:**
- ❌ Text format with newlines
- ❌ Headers/comments embedded in the file
- ❌ Patterns like "POL001" that look like record identifiers but are field data
- ❌ Not perfectly divisible (has headers/trailers)

---

## 🔧 What We're Missing

### **1. We Need to Understand the Actual File Format**

**Question:** Is "POL001" a record identifier or part of the field data?

**Answer:** It's **part of the field data** - the POLICY-NUMBER field is 20 bytes, and "POL001123456789012345" is exactly 20 bytes.

**Solution:** Don't strip "POL001" - it's part of the first field!

### **2. We Need Simpler Normalization**

**Current approach (too complex):**
1. Remove newlines ✅
2. Find data start ✅
3. Strip record prefixes ❌ (WRONG - "POL001" is field data)
4. Ensure divisibility ✅

**Correct approach (simpler):**
1. Remove newlines ✅
2. Find data start ✅
3. **Don't strip anything** - just parse from the data start
4. Ensure divisibility ✅

### **3. We Need to Trust the Copybook**

**The copybook tells us:**
- POLICY-NUMBER is 20 bytes
- The first field starts at byte 0 of each record

**We should:**
- Trust the copybook structure
- Parse fields according to the copybook
- Don't try to "fix" the data by stripping prefixes

---

## 🎯 The Real Solution

### **Option 1: Fix the Normalization Logic**

**Remove the prefix stripping logic** - "POL001" is part of the field data, not a prefix.

**Steps:**
1. Remove newlines
2. Find data start (skip headers/comments)
3. **Parse directly from data start** - don't strip prefixes
4. Ensure divisibility

### **Option 2: Use the Homegrown Solution (Simpler)**

**The homegrown solution already has:**
- ✅ ASCII data start detection (`_find_ascii_data_start`)
- ✅ Field-by-field parsing
- ✅ Encoding detection

**What it needs:**
- ❌ Remove the prefix stripping logic
- ❌ Trust the copybook structure
- ❌ Parse fields as defined in the copybook

### **Option 3: Fix Both Solutions**

**Both solutions have the same fundamental issue:**
- They're trying to strip "POL001" as a prefix
- But "POL001" is part of the POLICY-NUMBER field

**Fix:**
- Remove prefix stripping logic
- Parse fields according to copybook structure
- Trust that the data matches the copybook

---

## 📋 Next Steps

1. **Verify the file format** - Is "POL001" part of the field data or a record identifier?
2. **Remove prefix stripping** - If it's field data, don't strip it
3. **Simplify normalization** - Just remove newlines and find data start
4. **Test with actual file** - Verify the fix works

---

## 🔍 Key Insight

**The real issue isn't the parsing logic - it's that we're trying to "fix" the data by stripping prefixes that are actually part of the field data.**

**Solution:** Trust the copybook structure and parse fields as defined, without trying to strip prefixes that look like record identifiers.










