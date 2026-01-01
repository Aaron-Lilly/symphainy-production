# Dependency Analysis: Missing File Processing Libraries

**Date:** 2025-12-04  
**Status:** 🔍 **ANALYSIS COMPLETE**

---

## 📊 **Current Status**

### **Dependencies Found:**

1. **reportlab** ✅
   - ✅ In `pyproject.toml` (line 81): `reportlab = "^4.0.0"`
   - ✅ In `requirements.txt` (line 76): `reportlab>=4.0.0`
   - ✅ In `poetry.lock` (line 4953): `reportlab-4.4.5`
   - **Status:** Already included, should be installed

2. **python-docx** ⚠️
   - ❌ Commented out in `pyproject.toml` (line 67): `# python-docx = "^0.8.11"  # Already in platform`
   - ❌ Commented out in `requirements.txt` (line 62): `# python-docx==0.8.11  # Already in platform`
   - ⚠️ **Issue:** Comment says "Already in platform" but it's commented out!
   - **Status:** Needs to be uncommented and added

3. **openpyxl** ❌
   - ❌ Not in `pyproject.toml` at all
   - ❌ Not in `requirements.txt` at all
   - ✅ Found in `poetry.lock` as dependency of `pandas[excel]` (line 3483)
   - ⚠️ **Issue:** `pandas` is installed but `openpyxl` is only available via `pandas[excel]` extra
   - **Status:** Needs to be explicitly added

---

## 🔍 **Root Cause Analysis**

### **Why They're Missing:**

1. **python-docx:**
   - Commented out with note "Already in platform"
   - But it's not actually installed
   - Likely was removed during cleanup but comment left behind

2. **openpyxl:**
   - `pandas` is installed (line 55 in pyproject.toml)
   - But `pandas[excel]` extra is NOT specified
   - `openpyxl` is only installed if `pandas[excel]` is used
   - Need to either:
     - Add `pandas = {extras = ["excel"], version = "^2.0.0"}` OR
     - Add `openpyxl = "^3.1.0"` explicitly

3. **reportlab:**
   - Already included, should work
   - If not installed, may be a Poetry lock file issue

---

## ✅ **Solution**

### **1. Add python-docx**

**In `pyproject.toml`:**
```toml
# Document Processing Libraries
python-docx = "^0.8.11"  # Uncomment - required for DOCX parsing
```

**In `requirements.txt`:**
```txt
python-docx==0.8.11  # Required for DOCX parsing
```

### **2. Add openpyxl**

**Option A: Add as explicit dependency (Recommended)**
```toml
# Excel Processing
openpyxl = "^3.1.0"  # Required for Excel parsing
```

**Option B: Use pandas[excel] extra**
```toml
pandas = {extras = ["excel"], version = "^2.0.0"}
```

**Recommendation:** Use Option A (explicit) for clarity.

### **3. Verify reportlab**

Already included, but verify it's in poetry.lock and will be installed.

---

## 🔧 **Implementation Plan**

1. ✅ **Update pyproject.toml**
   - Uncomment `python-docx`
   - Add `openpyxl`

2. ✅ **Update requirements.txt**
   - Uncomment `python-docx`
   - Add `openpyxl`

3. ✅ **Update poetry.lock**
   - Run `poetry lock` to regenerate lock file

4. ✅ **Rebuild Docker containers**
   - Rebuild backend container
   - Verify dependencies installed

5. ✅ **Test**
   - Run file type tests
   - Verify all file types work

---

## 📝 **Files to Update**

1. `/home/founders/demoversion/symphainy_source/symphainy-platform/pyproject.toml`
   - Line 67: Uncomment `python-docx`
   - Add `openpyxl = "^3.1.0"` after line 81

2. `/home/founders/demoversion/symphainy_source/symphainy-platform/requirements.txt`
   - Line 62: Uncomment `python-docx`
   - Add `openpyxl>=3.1.0` after line 76

3. Regenerate `poetry.lock`:
   ```bash
   cd symphainy-platform
   poetry lock
   ```

---

**Status:** ✅ **Analysis Complete** | 🚧 **Ready to Implement**



