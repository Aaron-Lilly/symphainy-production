# Data Solution Orchestrator Integration - Test Guide

**Date:** January 16, 2025  
**Status:** 🧪 **READY FOR TESTING**

---

## 🎯 What We're Testing

The new flow routes file processing through Data Solution Orchestrator:

```
Frontend Request
  ↓
Data Solution Orchestrator (Solution realm)
  ↓ orchestrates platform correlation
Client Data Journey Orchestrator (Journey realm)
  ↓ routes to
Content Orchestrator (Content realm)
  ↓ calls
FileParserService (Content realm)
```

---

## ✅ Expected Benefits

1. **Data as First-Class Citizen:**
   - workflow_id propagation throughout entire flow
   - Lineage tracking (Data Steward)
   - Observability (Nurse)
   - Platform correlation (auth, session, events)

2. **Better Debugging:**
   - End-to-end correlation IDs
   - Workflow tracking
   - Better error messages with context

3. **No Timeout Issues:**
   - Proper request handling
   - No circular dependencies
   - Clean architectural layering

---

## 🧪 Test Steps

### 1. **Start Log Monitoring**

```bash
cd /home/founders/demoversion/symphainy_source
docker-compose logs backend --follow --tail=0 | grep -E "Data Solution|Client Data Journey|ContentOrchestrator|process_file|orchestrate_data_parse|workflow_id"
```

### 2. **Test Mainframe File Parsing**

1. Go to frontend
2. Upload a mainframe file (if not already uploaded)
3. Upload/select a copybook file
4. Click "Process File" or "Parse"

### 3. **What to Look For in Logs**

#### ✅ **Success Indicators:**

1. **Data Solution Orchestrator Called:**
   ```
   Data Solution Orchestrator: Orchestrating data parsing
   workflow_id: <uuid>
   ```

2. **Platform Correlation:**
   ```
   Orchestrating platform correlation: data_parse
   Auth validated, Session managed, Workflow tracked
   ```

3. **Client Data Journey Orchestrator:**
   ```
   Client Data Journey Orchestrator: Orchestrating client data parsing
   ```

4. **Content Orchestrator:**
   ```
   Content Orchestrator: Processing file: <file_id>
   FileParserService: Parsing file
   ```

5. **Workflow ID Propagation:**
   - Same workflow_id should appear in all log entries
   - End-to-end correlation

#### ❌ **Error Indicators:**

1. **Discovery Failures:**
   ```
   ContentOrchestrator not found
   Data Solution Orchestrator not available
   ```

2. **Circular Dependency:**
   ```
   ContentOrchestrator calling Data Solution Orchestrator (should NOT happen)
   ```

3. **Wrong Realm:**
   ```
   Found ContentOrchestrator but wrong realm: business_enablement (expected 'content')
   ```

4. **Timeout:**
   ```
   502 Bad Gateway
   Timeout after 90 seconds
   ```

---

## 📊 Log Patterns to Monitor

### **Expected Flow in Logs:**

```
1. FrontendGatewayService: handle_process_file_request
2. Data Solution Orchestrator: orchestrate_data_parse
3. Data Solution Orchestrator: _orchestrate_platform_correlation
4. Client Data Journey Orchestrator: orchestrate_client_data_parse
5. Client Data Journey Orchestrator: _discover_content_orchestrator (Content realm)
6. Content Orchestrator: process_file
7. FileParserService: parse_file
8. MainframeProcessingAdapter: _parse_binary_records
```

### **Workflow ID Should Appear In:**

- Data Solution Orchestrator logs
- Client Data Journey Orchestrator logs
- Content Orchestrator logs
- FileParserService logs
- Lineage tracking (Data Steward)
- Observability (Nurse)

---

## 🔍 Debugging Commands

### **Check Service Discovery:**
```bash
docker-compose exec backend python3 -c "
from backend.foundations.curator_foundation.services.curator_foundation_service import CuratorFoundationService
import asyncio

async def check():
    # Check if services are registered
    curator = CuratorFoundationService(...)
    services = await curator.get_registered_services()
    print('ContentOrchestratorService:', 'ContentOrchestratorService' in services)
    print('DataSolutionOrchestratorService:', 'DataSolutionOrchestratorService' in services)
    print('ClientDataJourneyOrchestratorService:', 'ClientDataJourneyOrchestratorService' in services)

asyncio.run(check())
"
```

### **Check Realm Names:**
```bash
docker-compose logs backend | grep -E "realm_name.*content|realm_name.*business"
```

### **Monitor Real-Time:**
```bash
docker-compose logs backend --follow | grep -E "process_file|orchestrate|workflow_id"
```

---

## ✅ Success Criteria

1. ✅ File parsing completes successfully
2. ✅ No 502 errors or timeouts
3. ✅ workflow_id appears in all log entries
4. ✅ Flow goes: Data Solution → Client Data Journey → Content → FileParser
5. ✅ Platform correlation works (lineage, observability)
6. ✅ No circular dependency errors
7. ✅ ContentOrchestrator discovered from Content realm (not Business Enablement)

---

## 🐛 Known Issues to Watch For

1. **Service Discovery:**
   - If ContentOrchestrator not found, check Curator registration
   - Verify realm_name="content" in ContentOrchestrator

2. **Circular Dependency:**
   - Should NOT see ContentOrchestrator calling Data Solution Orchestrator
   - If seen, check content_analysis_orchestrator.py

3. **Wrong Realm:**
   - If ContentOrchestrator found but wrong realm, check discovery logic
   - Verify ContentOrchestrator uses realm_name="content"

---

## 📝 Test Results Template

```
Test Date: ___________
File Type: ___________
File Size: ___________
Copybook: Yes/No

Results:
- [ ] File parsed successfully
- [ ] No 502 errors
- [ ] No timeouts
- [ ] workflow_id propagated
- [ ] Platform correlation worked
- [ ] Flow correct: Data Solution → Client Data Journey → Content → FileParser

Issues Found:
- 

Logs:
(paste relevant log entries)
```



