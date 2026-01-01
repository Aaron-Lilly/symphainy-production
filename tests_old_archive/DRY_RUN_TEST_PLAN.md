# 🧪 Dry Run Test Plan - MVP with Real Demo Files

**Purpose:** Validate MVP functionality with realistic demo files before live CTO demo

**Strategy:** Run existing E2E tests + create new tests using actual demo files

---

## 📋 Test Phases

### **Phase 1: Platform Startup (2 min)**
Verify platform can start and all services initialize

```bash
cd /home/founders/demoversion/symphainy_source
python3 -m pytest tests/e2e/test_platform_startup_e2e.py -v
```

**Expected:** All services start, no critical errors

---

### **Phase 2: Content Pillar with Real Demo Files (5 min)**
Test file upload and parsing with actual demo files

```bash
# Run content pillar smoke test
python3 -m pytest tests/e2e/test_content_pillar_smoke.py -v

# Run with real demo files (new test to create)
python3 -m pytest tests/e2e/test_content_with_demo_files.py -v
```

**Expected:** 
- File upload succeeds
- Parsing handles CSV, Binary, DOCX, PDF, XLSX, JSON
- No crashes on real data

---

### **Phase 3: All 4 Pillars Smoke Tests (5 min)**
Verify each pillar is functional

```bash
# Run all pillar smoke tests
python3 -m pytest tests/e2e/test_content_pillar_smoke.py -v
python3 -m pytest tests/e2e/test_insights_pillar_smoke.py -v
python3 -m pytest tests/e2e/test_operations_pillar_smoke.py -v
python3 -m pytest tests/e2e/test_business_outcomes_pillar_smoke.py -v
```

**Expected:** All pillars respond to requests

---

### **Phase 4: Complete MVP Journey (10 min)**
Simulate full CTO demo journey

```bash
# Run complete journey test
python3 -m pytest tests/e2e/test_complete_cto_demo_journey.py -v

# Run MVP user journey
python3 -m pytest tests/e2e/test_mvp_user_journey_e2e.py -v
```

**Expected:** 
- User registration works
- Session management works
- Guide Agent provides recommendations
- Liaison Agents respond
- All 4 pillars accessible
- File upload → Parse → Analyze → Generate workflow

---

### **Phase 5: Agent System Tests (5 min)**
Verify Guide Agent and Liaison Agents

```bash
# Test agentic capabilities
python3 -m pytest tests/agentic/e2e/ -v
```

**Expected:**
- Guide Agent provides personalized recommendations
- Liaison Agents respond with domain expertise
- WebSocket connections work

---

## 🎯 Quick Run - All Tests

```bash
cd /home/founders/demoversion/symphainy_source

# Run all E2E tests
python3 -m pytest tests/e2e/ -v --tb=short

# If that passes, run agentic tests
python3 -m pytest tests/agentic/e2e/ -v --tb=short
```

---

## 📦 New Test: Demo Files Integration

Create a test that uses your actual demo files to validate the complete workflow.

**Test File:** `tests/e2e/test_demo_files_integration.py`

This test will:
1. Upload each demo ZIP file
2. Verify parsing succeeds
3. Test insights generation
4. Test operations (SOP/Workflow)
5. Test business outcomes (Roadmap/POC)

---

## 🚀 Recommended Approach

### **Option A: Quick Validation (10 min)**
Run critical path only:
```bash
cd /home/founders/demoversion/symphainy_source

# Platform starts
python3 -m pytest tests/e2e/test_platform_startup_e2e.py -v

# CTO demo journey works
python3 -m pytest tests/e2e/test_complete_cto_demo_journey.py -v
```

### **Option B: Comprehensive Dry Run (30 min)**
Run everything:
```bash
cd /home/founders/demoversion/symphainy_source

# All E2E tests
python3 -m pytest tests/e2e/ -v

# Agentic tests
python3 -m pytest tests/agentic/e2e/ -v
```

---

## 💡 What This Validates

✅ **Platform Stability:** Services start without crashing  
✅ **API Layer:** All endpoints respond correctly  
✅ **Manager Hierarchy:** City → Solution → Journey → Experience → Delivery  
✅ **Journey Orchestrator:** MVP journey tracking works  
✅ **Business Orchestrator:** Pillar logic executes  
✅ **Agent System:** Guide + 4 Liaison agents respond  
✅ **File Handling:** Upload, parse, analyze real files  
✅ **Session Management:** User sessions work  
✅ **Authentication:** Login/registration works  

---

## 🐛 If Tests Fail

1. **Check logs:** `tests/logs/` for detailed error traces
2. **Platform logs:** Backend terminal output
3. **Fix issues** before live demo
4. **Re-run tests** to verify fixes

---

## 📊 Success Criteria

Before running live demo, ensure:

- [ ] Platform startup test passes
- [ ] All 4 pillar smoke tests pass
- [ ] Complete CTO demo journey test passes
- [ ] Content upload works with real files
- [ ] No critical errors in logs

---

**Ready to start the dry run?** Let me know and I'll execute the tests for you! 🚀

