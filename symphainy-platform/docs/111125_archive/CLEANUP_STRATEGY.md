# Platform Directory Cleanup Strategy
## Audit & Cleanup Recommendations

**Date:** November 6, 2025  
**Goal:** Remove orphaned/duplicate code, keep only active codebase

---

## 🚨 **CRITICAL FINDING**

**IMPORTANT DISCOVERY:** The current `main.py` imports from **TOP-LEVEL** realm directories, NOT from `backend/`:

- `main.py` imports from: `journey_solution/`, `solution/`, `experience/` (TOP LEVEL)
- NEW refactored code is in: `backend/journey/`, `backend/solution/`, `backend/experience/`

**This means:**
- ✅ TOP-LEVEL realm directories are **CURRENTLY ACTIVE** (used by main.py)
- ✅ `backend/` realm directories are the **NEW REFACTORED CODE** (not yet integrated)
- ⚠️ Migration required: Update `main.py` to import from `backend/` subdirectories
- ⚠️ After migration: Archive top-level directories

**Action Required:**
1. Update `main.py` to import from `backend/` subdirectories
2. Test thoroughly
3. Archive old top-level directories

---

## 📊 **DIRECTORY AUDIT RESULTS**

### **✅ KEEP - Active Production Code**

These directories contain actively used code:

1. **`backend/`** - ✅ **KEEP** (PRIMARY)
   - Contains all active Smart City services
   - Business Enablement realm
   - Experience realm
   - Journey realm
   - Solution realm
   - All actively used by `main.py`

2. **`foundations/`** - ✅ **KEEP**
   - `public_works_foundation/` - Active infrastructure abstractions
   - `agentic_foundation/` - Active agent SDK

3. **`bases/`** - ✅ **KEEP**
   - Base classes for services
   - Mixins
   - Protocols
   - Used throughout the platform

4. **`config/`** - ✅ **KEEP**
   - Platform configuration files
   - Environment settings

5. **`utilities/`** - ✅ **KEEP**
   - DI Container utilities
   - Helper functions
   - Used by all services

6. **`tests/`** - ✅ **KEEP**
   - All 243 comprehensive tests we just built
   - Critical for production readiness

7. **`docs/`** - ✅ **KEEP**
   - CTO feedback documents
   - Architecture documentation
   - Implementation guides

8. **`scripts/`** - ✅ **KEEP** (but needs cleanup)
   - `startup.sh` - Active startup script
   - `stop.sh` - Active stop script
   - Need to archive old/experimental scripts

9. **`archive/`** - ✅ **KEEP**
   - Explicitly marked for archival
   - Historical reference

---

### **🗑️ DELETE - Orphaned/Duplicate Code**

These directories/files are duplicates or no longer used:

#### **High-Priority Deletions:**

1. **`symphainy-platform/`** (nested directory) - 🗑️ **DELETE**
   - This is a DUPLICATE of the parent directory
   - Nested `backend/`, `platform/`, `archive/` are duplicates
   - **Action:** Delete entire nested `symphainy-platform/` directory

2. **`agentic/`** (top-level) - 🗑️ **DELETE**
   - Old agentic code (replaced by `foundations/agentic_foundation/`)
   - **Action:** Delete entire `agentic/` directory

3. **`platform/`** (top-level) - 🗑️ **DELETE** or **MERGE**
   - Appears to be old/duplicate platform code
   - Check if it has anything unique, otherwise delete
   - **Action:** Review, then likely delete

4. **`platform_infrastructure/`** - 🗑️ **DELETE** or **MERGE**
   - Old infrastructure code (replaced by `foundations/public_works_foundation/`)
   - **Action:** Review for any unique code, then delete

5. **`engines/`** - 🗑️ **DELETE** or **ARCHIVE**
   - Unclear what this contains
   - Likely old/experimental code
   - **Action:** Review and delete if unused

6. **`journey_solution/`** (top-level) - ⚠️ **CRITICAL - CURRENTLY ACTIVE**
   - **FINDING:** `main.py` imports from `journey_solution/`, NOT `backend/journey/`
   - `backend/journey/` is the NEW refactored code
   - **Action:** KEEP until migration is complete, then archive

7. **`solution/`** (top-level) - ⚠️ **CRITICAL - CURRENTLY ACTIVE**
   - **FINDING:** `main.py` imports from `solution/`, NOT `backend/solution/`
   - `backend/solution/` is the NEW refactored code
   - **Action:** KEEP until migration is complete, then archive

8. **`experience/`** (top-level) - ⚠️ **CRITICAL - CURRENTLY ACTIVE**
   - **FINDING:** `main.py` imports from `experience/`, NOT `backend/experience/`
   - `backend/experience/` is the NEW refactored code
   - **Action:** KEEP until migration is complete, then archive

9. **`contracts/`** - 🗑️ **DELETE** or **ARCHIVE**
   - Old contract/interface code (we use protocols now)
   - **Action:** Archive if historical value, otherwise delete

#### **Orphaned Files to Delete:**

10. **Main Files (keep only one):**
    - ✅ KEEP: `main.py` (primary entry point)
    - 🗑️ DELETE: `main_updated.py` (old version)
    - 🗑️ DELETE: `main_bottomsup.py` (experimental)

11. **Startup Scripts (keep only active ones):**
    - ✅ KEEP: `startup.sh` (primary)
    - ✅ KEEP: `stop.sh`
    - 🗑️ DELETE: `startup_bottomsup.sh` (experimental)
    - Move `logs.sh` to `scripts/`

12. **Test Files (orphaned at root):**
    - 🗑️ DELETE: All `test_*.py` files at root
    - These should be in `tests/` directory
    - List includes:
      - `test_architectural_patterns.py`
      - `test_both_services_infrastructure_mapping.py`
      - `test_business_enablement_architecture.py`
      - `test_cio_*.py` (all CIO test files)
      - `test_communication_foundation_*.py`
      - `test_conductor_clean_rebuild.py`
      - `test_content_steward_clean_rebuild.py`
      - `test_corrected_infrastructure_mapping.py`
      - `test_data_steward_*.py`
      - `test_foundation_enhancements.py`
      - `test_librarian_clean_rebuild.py`
      - `test_nurse_service_infrastructure_mapping.py`
      - `test_post_office_clean_rebuild_proper_infrastructure.py`
      - `test_remaining_realms_architecture.py`
      - `test_security_guard_*.py` (all security guard test files)
      - `test_smart_city_architecture.py`
      - `test_solution_*.py`
      - `test_startup_updated.py`
      - `test_traffic_cop_infrastructure_mapping.py`
      - `test_unified_communication_foundation.py`

13. **Python Service Files at Root:**
    - 🗑️ DELETE: All `*_service_*.py` files at root
    - These were likely test/experimental files
    - List includes:
      - `data_steward_service_corrected_infrastructure.py`
      - `data_steward_service_infrastructure_connected.py`
      - `post_office_service_clean_rebuild_proper_infrastructure.py`
      - `security_guard_service_*.py` (multiple files)

14. **Analysis Python Files at Root:**
    - 🗑️ DELETE: All `*_analysis.py` files at root
    - List includes:
      - `audit_all_adapters.py`
      - `security_capabilities_analysis.py`
      - `security_guard_service_analysis.py`

15. **Markdown Documentation Files:**
    - ⚠️ **REVIEW & CONSOLIDATE** (many duplicates)
    - **Action:** Move valuable docs to `docs/` directory
    - **Delete:** Outdated/duplicate analysis files
    - Candidates for consolidation/deletion:
      - All `*_ANALYSIS.md` files (many duplicates)
      - All `*_AUDIT.md` files (consolidate into one)
      - All `*_REFACTORING_*.md` files (outdated)
      - All `*_IMPLEMENTATION_*.md` files (consolidate)
      - All `SESSION_*.md` files (keep recent, archive old)

#### **Infrastructure Files:**

16. **Docker/Config Files:**
    - ✅ KEEP: `docker-compose.infrastructure.yml` (if active)
    - ✅ KEEP: `pyproject.toml`
    - ✅ KEEP: `requirements.txt`
    - ✅ KEEP: `tempo-config.yaml`
    - ✅ KEEP: `otel-collector-config.yaml`
    - 🗑️ DELETE: `test_config.env` (move to proper location or delete)

17. **Coverage/Logs:**
    - 🗑️ DELETE: `htmlcov/` (regenerated by tests)
    - 🗑️ DELETE: `coverage.xml` (regenerated by tests)
    - 🗑️ DELETE: `logs/` (regenerated at runtime)
    - 🗑️ DELETE: `__pycache__/` (all instances)

18. **External Dependencies:**
    - ⚠️ **REVIEW**: `arangodb-init/` (if still using ArangoDB, keep; otherwise archive)
    - ⚠️ **REVIEW**: `grafana/` (if monitoring setup is active, keep)

---

## 🎯 **RECOMMENDED CLEANUP STRATEGY**

### **Phase 1: Safe Deletions (High Confidence)**

1. Delete nested duplicate directory:
   ```bash
   rm -rf symphainy-platform/symphainy-platform/
   ```

2. Delete orphaned test files at root:
   ```bash
   rm test_*.py
   ```

3. Delete experimental service files at root:
   ```bash
   rm *_service_*.py
   rm *_analysis.py
   ```

4. Delete old main files:
   ```bash
   rm main_updated.py main_bottomsup.py
   ```

5. Delete old startup scripts:
   ```bash
   rm startup_bottomsup.sh
   ```

6. Delete generated artifacts:
   ```bash
   rm -rf htmlcov/ logs/ __pycache__/
   rm coverage.xml
   ```

### **Phase 2: Review & Consolidate**

7. Review top-level realm directories:
   ```bash
   # Check if these are duplicates of backend/ subdirectories
   diff -r journey_solution/ backend/journey/
   diff -r solution/ backend/solution/
   diff -r experience/ backend/experience/
   ```

8. Consolidate documentation:
   ```bash
   # Move valuable docs to docs/
   # Delete outdated/duplicate analysis files
   ```

9. Review and clean up old engines/platform directories:
   ```bash
   # Check for unique code
   # Archive if historical value, otherwise delete
   ```

### **Phase 3: Archive Strategy**

10. Move to archive instead of deleting (if uncertain):
    ```bash
    mv old_directory/ archive/old_directory_$(date +%Y%m%d)/
    ```

---

## 📁 **FINAL CLEAN DIRECTORY STRUCTURE**

After cleanup, the structure should be:

```
symphainy-platform/
├── archive/                    # Historical code (keep)
├── backend/                    # Active backend code (KEEP)
│   ├── business_enablement/
│   ├── experience/
│   ├── journey/
│   ├── smart_city/
│   └── solution/
├── bases/                      # Base classes (KEEP)
├── config/                     # Configuration (KEEP)
├── docs/                       # Documentation (KEEP, consolidate)
├── foundations/                # Foundation services (KEEP)
│   ├── agentic_foundation/
│   └── public_works_foundation/
├── scripts/                    # Startup/utility scripts (KEEP, clean up)
├── tests/                      # All 243 tests (KEEP)
├── utilities/                  # Helper utilities (KEEP)
├── docker-compose.infrastructure.yml
├── main.py                     # Primary entry point (KEEP)
├── pyproject.toml
├── requirements.txt
├── startup.sh
└── stop.sh
```

**Estimated cleanup:**
- **Delete:** ~100+ orphaned files
- **Archive:** ~20-30 directories
- **Space saved:** ~500+ MB (depending on logs/cache)

---

## ⚠️ **SAFETY RECOMMENDATIONS**

1. **Commit Current State First:**
   ```bash
   git add -A
   git commit -m "chore: Checkpoint before cleanup"
   git push
   ```

2. **Create Backup:**
   ```bash
   cp -r symphainy-platform symphainy-platform-backup-$(date +%Y%m%d)
   ```

3. **Test After Each Phase:**
   - Run tests after Phase 1
   - Run tests after Phase 2
   - Ensure platform still starts

4. **Incremental Approach:**
   - Do Phase 1 first (safe deletions)
   - Test thoroughly
   - Then proceed to Phase 2

---

## 🚀 **NEXT STEPS**

1. Review this strategy with the team
2. Commit current state
3. Execute Phase 1 (safe deletions)
4. Test platform
5. Execute Phase 2 (review & consolidate)
6. Test platform
7. Execute Phase 3 (archive uncertain code)
8. Final testing and validation

---

**Status:** ⏳ **Awaiting Approval to Execute**

Would you like me to proceed with Phase 1 (safe deletions) or would you prefer to review specific items first?

