# One-Byte Misalignment Debug

**Date:** December 28, 2025  
**Status:** 🔍 **INVESTIGATING**

---

## 🐛 The Issue

**Symptoms:**
- ✅ Policy Number: Correct (20 bytes)
- ❌ Policyholder Name: Has extra "0" or "1" at end
- ❌ Policy Type: Missing first letter (e.g., "erm Life" instead of "Term Life")
- ❌ Starting at Record 7: Complete misalignment

**Pattern:**
- First field (Policy Number) is correct
- 1-byte misalignment starting from AGE field
- Misalignment accumulates, causing breakdown at record 7

---

## 🔍 Hypotheses

### **Hypothesis 1: AGE Field Length Issue**
- Copybook says: `POLICYHOLDER-AGE PIC 9(3)` = 3 bytes
- But we might be reading it as 2 bytes or 4 bytes
- This would cause all subsequent fields to shift

### **Hypothesis 2: Record Size Detection Issue**
- We detect 86-byte spacing between "POL001" patterns
- But after removing newlines, records might actually be 81 bytes
- We're incorrectly trying to strip a 5-byte prefix from 81-byte records

### **Hypothesis 3: Newline Handling Issue**
- File has newlines between records
- We remove newlines, but spacing detection was done before removal
- This causes incorrect record splitting

### **Hypothesis 4: Cumulative Offset**
- Each record is off by 1 byte
- After 7 records, we're off by 7 bytes
- This causes complete misalignment

---

## 🔧 Debug Steps

1. **Check record sizes after stripping:**
   - First record should be 81 bytes
   - All records should be 81 bytes
   - If not, we have a splitting issue

2. **Check if AGE field is correct:**
   - AGE should be 3 bytes (bytes 50-52)
   - If we're reading 2 bytes, we'd get misalignment

3. **Check spacing detection:**
   - Verify we're detecting 86-byte spacing correctly
   - Check if newlines are affecting detection

4. **Check file structure:**
   - Does file actually have 86-byte records?
   - Or does it have 81-byte records with newlines?

---

## 📋 Next Steps

1. Run parsing with debug logging enabled
2. Check logs for record sizes after stripping
3. Verify AGE field is being read as 3 bytes
4. Check if spacing detection is correct










