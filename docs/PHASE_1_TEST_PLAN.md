# Phase 1 Test Plan

**Date:** December 22, 2025  
**Status:** 🧪 **READY FOR TESTING**  
**Phase:** Phase 1 - Remove DataJourneyOrchestrator & Move ContentOrchestrator to Journey Realm

---

## 🎯 Test Objectives

Verify that the refactored architecture works correctly:
1. ✅ DataSolutionOrchestrator can discover ContentJourneyOrchestrator
2. ✅ ContentJourneyOrchestrator can be lazy-initialized if not found
3. ✅ File parsing flow works end-to-end
4. ✅ Platform correlation is properly orchestrated
5. ✅ No circular dependencies exist

---

## 📋 Test Cases

### **Test 1: Service Discovery**

**Objective:** Verify DataSolutionOrchestrator can discover ContentJourneyOrchestrator via Curator

**Steps:**
1. Start all containers
2. Verify ContentJourneyOrchestrator registers with Curator on initialization
3. Call `DataSolutionOrchestrator._discover_content_journey_orchestrator()`
4. Verify it finds ContentJourneyOrchestrator

**Expected Result:**
- ContentJourneyOrchestrator is discovered via Curator
- Log shows: `✅ Discovered ContentJourneyOrchestratorService via Curator`

**Test Command:**
```bash
# Check logs for Curator registration
docker-compose logs backend | grep -i "ContentJourneyOrchestrator"
```

---

### **Test 2: Lazy Initialization**

**Objective:** Verify ContentJourneyOrchestrator can be lazy-initialized if not found via Curator

**Steps:**
1. Temporarily prevent ContentJourneyOrchestrator from registering with Curator
2. Call `DataSolutionOrchestrator._discover_content_journey_orchestrator()`
3. Verify it lazy-initializes ContentJourneyOrchestrator

**Expected Result:**
- ContentJourneyOrchestrator is created and initialized
- Log shows: `✅ ContentJourneyOrchestratorService lazy-initialized successfully`

---

### **Test 3: End-to-End File Parsing Flow**

**Objective:** Verify the complete flow from Frontend to FileParserService

**Flow:**
```
Frontend Request
  ↓
FrontendGatewayService.handle_process_file_request()
  ↓
DataSolutionOrchestrator.orchestrate_data_parse()
  ↓ (platform correlation)
ContentJourneyOrchestrator.process_file()
  ↓
FileParserService.parse_file()
```

**Steps:**
1. Upload a mainframe file via frontend
2. Trigger file parsing via `/api/v1/content-pillar/process-file/{file_id}`
3. Monitor logs at each step
4. Verify parsing completes successfully

**Expected Result:**
- Request completes successfully
- All logs show proper flow through each service
- Parse result is returned to frontend
- Platform correlation (workflow_id, etc.) is tracked

**Test Command:**
```bash
# Monitor logs in real-time
docker-compose logs -f backend | grep -E "handle_process_file_request|orchestrate_data_parse|ContentJourneyOrchestrator|process_file|FileParserService"
```

---

### **Test 4: Platform Correlation**

**Objective:** Verify platform correlation is properly orchestrated

**Steps:**
1. Trigger file parsing with user context
2. Verify workflow_id is generated and propagated
3. Verify platform services are called (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)

**Expected Result:**
- workflow_id is generated and included in all requests
- Platform correlation services are called (if available)
- Correlation context is passed through the flow

**Test Command:**
```bash
# Check for workflow_id in logs
docker-compose logs backend | grep -i "workflow_id"
```

---

### **Test 5: No Circular Dependencies**

**Objective:** Verify no circular dependencies exist

**Steps:**
1. Check import statements
2. Verify ContentJourneyOrchestrator doesn't import DataSolutionOrchestrator
3. Verify DataSolutionOrchestrator doesn't create circular imports

**Expected Result:**
- No circular import errors
- Services can be imported independently

**Test Command:**
```bash
# Try importing both services
python3 -c "from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService; from backend.journey.orchestrators.content_journey_orchestrator.content_analysis_orchestrator import ContentJourneyOrchestrator; print('✅ No circular dependencies')"
```

---

### **Test 6: Error Handling**

**Objective:** Verify error handling works correctly

**Steps:**
1. Try parsing with invalid file_id
2. Try parsing when ContentJourneyOrchestrator is not available
3. Verify errors are properly handled and returned

**Expected Result:**
- Errors are caught and logged
- Error messages are returned to frontend
- No unhandled exceptions

---

## 🔍 Verification Checklist

### **Code Structure:**
- [x] ContentJourneyOrchestrator exists in Journey realm
- [x] DataSolutionOrchestrator routes to ContentJourneyOrchestrator
- [x] No references to ClientDataJourneyOrchestrator in DataSolutionOrchestrator
- [x] ContentJourneyOrchestrator is self-initializing
- [x] All imports are correct

### **Runtime Verification:**
- [ ] ContentJourneyOrchestrator registers with Curator
- [ ] DataSolutionOrchestrator discovers ContentJourneyOrchestrator
- [ ] File parsing completes successfully
- [ ] Platform correlation works
- [ ] No circular dependencies
- [ ] Error handling works

---

## 🐛 Known Issues to Watch For

1. **Import Path Issues:**
   - Verify `from backend.journey.orchestrators.content_journey_orchestrator.content_analysis_orchestrator import ContentJourneyOrchestrator` works

2. **Curator Registration:**
   - ContentJourneyOrchestrator must register with Curator during `initialize()`
   - Service name must be `"ContentJourneyOrchestratorService"`

3. **Realm Name:**
   - ContentJourneyOrchestrator must have `realm_name="journey"`

4. **Method Signatures:**
   - `ContentJourneyOrchestrator.process_file()` signature matches what DataSolutionOrchestrator calls

---

## 📊 Test Results

**Status:** ⏳ **PENDING TEST EXECUTION**

### Test Results:
- [ ] Test 1: Service Discovery
- [ ] Test 2: Lazy Initialization
- [ ] Test 3: End-to-End File Parsing Flow
- [ ] Test 4: Platform Correlation
- [ ] Test 5: No Circular Dependencies
- [ ] Test 6: Error Handling

---

## 🚀 Next Steps After Testing

1. **If Tests Pass:**
   - Proceed with Phase 2 (Bootstrap Pattern)
   - Continue with remaining phases

2. **If Tests Fail:**
   - Document failures
   - Fix issues
   - Re-test

---

## 📝 Test Execution Log

_To be filled during testing..._



