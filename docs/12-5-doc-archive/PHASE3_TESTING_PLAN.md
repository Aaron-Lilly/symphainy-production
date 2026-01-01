# Phase 3: CLI Integration - Testing Plan

**Date:** December 2024  
**Status:** 📋 **TESTING PLAN**  
**Goal:** Test Phase 3 CLI Integration with Client Config Foundation

---

## 🎯 Testing Objectives

1. ✅ Verify CLI can initialize Client Config Foundation
2. ✅ Verify CLI can load tenant configurations
3. ✅ Verify CLI config management commands work
4. ✅ Verify tenant-aware commands use tenant configs
5. ✅ Verify graceful fallback when Client Config Foundation unavailable

---

## 🧪 Test Cases

### **Test 1: CLI Help Commands**

**Objective:** Verify CLI commands are properly registered

**Commands:**
```bash
# Main help
python3 scripts/insurance_use_case/data_mash_cli.py --help

# Config help
python3 scripts/insurance_use_case/data_mash_cli.py config --help

# Individual command help
python3 scripts/insurance_use_case/data_mash_cli.py config load --help
python3 scripts/insurance_use_case/data_mash_cli.py config validate --help
python3 scripts/insurance_use_case/data_mash_cli.py config store --help
python3 scripts/insurance_use_case/data_mash_cli.py config version --help
```

**Expected:** All commands show help without errors

---

### **Test 2: Client Config Foundation Initialization**

**Objective:** Verify CLI can initialize Client Config Foundation

**Test:**
```bash
# This will attempt to initialize Client Config Foundation
python3 scripts/insurance_use_case/data_mash_cli.py config load test_tenant domain_models
```

**Expected:**
- CLI attempts to initialize Client Config Foundation
- If available: Loads configs successfully
- If unavailable: Shows graceful warning and continues

---

### **Test 3: Config Load Command**

**Objective:** Verify CLI can load tenant configurations

**Test:**
```bash
python3 scripts/insurance_use_case/data_mash_cli.py config load test_tenant_001 domain_models
python3 scripts/insurance_use_case/data_mash_cli.py config load test_tenant_001 workflows
python3 scripts/insurance_use_case/data_mash_cli.py config load test_tenant_001 ingestion_endpoints
```

**Expected:**
- CLI loads tenant configs successfully
- Displays config keys and structure
- Handles missing configs gracefully

---

### **Test 4: Config Validate Command**

**Objective:** Verify CLI can validate tenant configurations

**Prerequisites:**
- Create a test config file: `test_config.json`
```json
{
  "workflow_name": "PolicyApproval",
  "steps": ["underwriting", "review"]
}
```

**Test:**
```bash
python3 scripts/insurance_use_case/data_mash_cli.py config validate test_tenant_001 workflows test_config.json
```

**Expected:**
- CLI validates config successfully
- Reports validation result (pass/fail)
- Handles invalid configs gracefully

---

### **Test 5: Config Store Command**

**Objective:** Verify CLI can store tenant configurations

**Test:**
```bash
python3 scripts/insurance_use_case/data_mash_cli.py config store test_tenant_001 workflows test_config.json
```

**Expected:**
- CLI stores config successfully
- Returns config ID
- Handles storage errors gracefully

---

### **Test 6: Config Version Command**

**Objective:** Verify CLI can retrieve config versions

**Test:**
```bash
python3 scripts/insurance_use_case/data_mash_cli.py config version test_tenant_001 workflows
```

**Expected:**
- CLI retrieves versions successfully
- Displays version list
- Handles missing versions gracefully

---

### **Test 7: Tenant-Aware Ingest Command**

**Objective:** Verify ingest command uses tenant configs

**Test:**
```bash
# Create a test file
echo "test,data" > test_data.csv

# Ingest with tenant
python3 scripts/insurance_use_case/data_mash_cli.py ingest test_data.csv --format=csv --tenant=test_tenant_001
```

**Expected:**
- CLI loads tenant configs
- Applies tenant-specific ingestion endpoint if configured
- Falls back to default endpoint if no tenant config

---

### **Test 8: Tenant-Aware Map-to-Canonical Command**

**Objective:** Verify map-to-canonical command uses tenant configs

**Test:**
```bash
# Create a test schema file
echo '{"fields": ["id", "name"]}' > test_schema.json

python3 scripts/insurance_use_case/data_mash_cli.py map-to-canonical --source-schema=test_schema.json --canonical=policy_v1 --tenant=test_tenant_001
```

**Expected:**
- CLI loads tenant configs
- Uses tenant-specific canonical model if configured
- Falls back to provided canonical model

---

### **Test 9: Tenant-Aware Generate-Plan Command**

**Objective:** Verify generate-plan command uses tenant configs

**Test:**
```bash
python3 scripts/insurance_use_case/data_mash_cli.py generate-plan --source=legacy_system --target=new_platform --canonical=policy_v1 --tenant=test_tenant_001
```

**Expected:**
- CLI loads tenant configs
- Uses tenant-specific workflows if configured
- Falls back to default workflow

---

### **Test 10: Graceful Fallback**

**Objective:** Verify CLI works when Client Config Foundation is unavailable

**Test:**
```bash
# Run commands without Client Config Foundation available
python3 scripts/insurance_use_case/data_mash_cli.py ingest test_data.csv --format=csv
```

**Expected:**
- CLI shows warning about Client Config Foundation
- Commands still work using default behavior
- No crashes or errors

---

## 📊 Test Execution

### **Quick Test (5 minutes)**
```bash
# Test help commands
python3 scripts/insurance_use_case/data_mash_cli.py --help
python3 scripts/insurance_use_case/data_mash_cli.py config --help

# Test config load (will attempt initialization)
python3 scripts/insurance_use_case/data_mash_cli.py config load test_tenant domain_models
```

### **Full Test Suite (15-20 minutes)**
Run all 10 test cases above in sequence.

---

## ✅ Success Criteria

1. ✅ All help commands work
2. ✅ Client Config Foundation initializes (or graceful fallback)
3. ✅ Config management commands work
4. ✅ Tenant-aware commands use tenant configs
5. ✅ Graceful fallback when Client Config Foundation unavailable
6. ✅ No crashes or errors

---

## 🐛 Known Issues / Expected Behavior

### **Client Config Foundation Not Available**
- **Expected:** CLI shows warning and continues with default behavior
- **Not a bug:** This is graceful degradation

### **Tenant Configs Not Found**
- **Expected:** CLI shows warning and uses defaults
- **Not a bug:** This is expected for new tenants

### **Config Validation Fails**
- **Expected:** CLI reports validation failure with details
- **Not a bug:** This is the intended behavior

---

## 📋 Test Results Template

```
Test 1: CLI Help Commands
  Status: [PASS/FAIL]
  Notes: [Any issues or observations]

Test 2: Client Config Foundation Initialization
  Status: [PASS/FAIL]
  Notes: [Any issues or observations]

Test 3: Config Load Command
  Status: [PASS/FAIL]
  Notes: [Any issues or observations]

... (continue for all tests)
```

---

**Last Updated:** December 2024  
**Status:** Ready for Testing




