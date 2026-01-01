# AGE Field Missing - Debug Guide

**Date:** December 28, 2025  
**Status:** 🔍 **INVESTIGATING**

---

## 🐛 The Issue

**AGE field is missing from preview results**, which explains the 1-byte misalignment:
- AGE is 3 bytes (`PIC 9(3)`)
- If AGE is not being parsed/displayed, we're skipping those 3 bytes
- This causes POLICY_TYPE to start 3 bytes too early
- All subsequent fields are misaligned

---

## 🔍 How to Check Record Size

**Use the diagnostic script:**
```bash
python3 scripts/check_record_size.py <file_path>
```

**Or manually:**
1. **Check file size divisibility:**
   - If divisible by 81: records are 81 bytes
   - If divisible by 86: records are 86 bytes

2. **Check spacing between POL patterns:**
   - Find "POL001" and "POL002" in file
   - Calculate distance: if 86 bytes → 86-byte records (with prefix)
   - If 81 bytes → 81-byte records (no prefix)

3. **Check first record:**
   - Read first 86 bytes
   - If starts with "POL00" → 86-byte records with 5-byte prefix
   - If starts with "POL001" → 81-byte records (POL001 is part of field)

---

## 🔍 Why AGE Might Be Missing

### **Hypothesis 1: Cobrix Converts to Number and It's Null**
- `PIC 9(3)` is a numeric field
- Cobrix might convert it to an integer
- If the value is invalid or null, it might be filtered out

### **Hypothesis 2: Field Name Mismatch**
- Copybook says: `POLICYHOLDER-AGE`
- Cobrix might return: `POLICYHOLDER_AGE` (underscore)
- Flattening might not handle the conversion correctly

### **Hypothesis 3: AGE is in Nested Structure**
- Cobrix returns nested dicts
- AGE might be nested under `POLICYHOLDER_RECORD`
- Flattening might not be extracting it correctly

### **Hypothesis 4: AGE is Being Filtered Out**
- Some logic might be filtering out numeric fields
- Or filtering out null/empty values

---

## 🔧 Debug Steps Added

**New logging will show:**
1. ✅ All keys in nested record (before flattening)
2. ✅ AGE field keys found in nested record
3. ✅ AGE field value and type
4. ✅ All numeric fields (AGE might be converted to number)
5. ✅ Flattened record keys (after flattening)
6. ✅ AGE field keys after flattening

**Check logs for:**
- `📊 AGE field keys found: [...]`
- `📊 AGE field '...' value: ... (type: ...)`
- `📊 Numeric fields (might be AGE): [...]`

---

## 📋 Next Steps

1. **Run parsing again** with new debug logging
2. **Check logs** for AGE field information
3. **Verify record size** using diagnostic script
4. **Fix based on findings**










