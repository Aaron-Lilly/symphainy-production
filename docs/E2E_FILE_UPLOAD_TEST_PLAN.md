# E2E File Upload & Parsing Test Plan

**Date:** December 11, 2025  
**Objective:** Test complete file upload → parse → save flow with real servers

---

## 🎯 Test Flow

1. **Start Infrastructure** (Docker Compose)
2. **Start Backend** (FastAPI)
3. **Start Frontend** (Next.js)
4. **Upload Test File** (via frontend or curl)
5. **Verify Upload** (file stored in GCS + Supabase)
6. **Trigger Parsing** (if automatic, or via API)
7. **Verify Parsing** (parsed file stored)
8. **Check Results** (Supabase records, GCS files)

---

## 🔍 Current Architecture Flow

### **Upload Flow (Current)**
```
Frontend → FrontendGatewayService.handle_upload_file_request()
  → ContentAnalysisOrchestrator.upload_file()
    → Content Steward.process_upload() (direct SOA API)
      → GCS + Supabase storage
```

### **Parsing Flow (Current)**
```
ContentAnalysisOrchestrator.process_file()
  → FileParserService.parse_file()
    → Parsing modules (structured/unstructured/hybrid)
      → Content Steward.store_parsed_file()
        → GCS + Supabase storage
```

### **New Architecture Flow (Target)**
```
Frontend → FrontendGatewayService.handle_upload_file_request()
  → ContentAnalysisOrchestrator.upload_file()
    → Data Solution Orchestrator.orchestrate_data_ingest()
      → Content Steward.process_upload()
        → Data Steward.track_lineage()
        → Nurse.record_platform_event()
      → Return file_id + workflow_id

ContentAnalysisOrchestrator.process_file()
  → Data Solution Orchestrator.orchestrate_data_parse()
    → FileParserService.parse_file()
      → Parsing modules
    → Content Steward.store_parsed_file()
    → Data Steward.track_lineage()
    → Nurse.record_platform_event()
```

---

## ⚠️ Known Gaps & Required Fixes

### **1. ContentAnalysisOrchestrator Not Updated** ❌
- **Current:** Calls Content Steward directly
- **Needed:** Should call Data Solution Orchestrator
- **Location:** `business_enablement_old/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/`
- **Fix:** Update `upload_file()` to use Data Solution Orchestrator

### **2. Data Solution Orchestrator Not Registered** ❌
- **Current:** Created but not registered in startup
- **Needed:** Register in DeliveryManagerService or BusinessEnablementRealmBridge
- **Location:** `business_enablement/delivery_manager/data_solution_orchestrator/`
- **Fix:** Add to orchestrator discovery/initialization

### **3. workflow_id Propagation** ⚠️
- **Current:** FrontendGatewayService generates workflow_id (Phase 0.5 ✅)
- **Needed:** Ensure ContentAnalysisOrchestrator receives and uses it
- **Fix:** Pass workflow_id in user_context

### **4. Parsing Integration** ⚠️
- **Current:** FileParserService exists but may not be registered
- **Needed:** Ensure FileParserService is discoverable
- **Location:** `business_enablement/enabling_services/file_parser_service/`
- **Fix:** Register in service discovery

### **5. ContentAnalysisOrchestrator.process_file()** ❌
- **Current:** May not exist or may not call Data Solution Orchestrator
- **Needed:** Should call `orchestrate_data_parse()`
- **Fix:** Implement or update process_file() method

---

## 🧪 Test Steps

### **Step 1: Start Infrastructure**
```bash
cd /home/founders/demoversion/symphainy_source
docker-compose up -d
```

### **Step 2: Start Backend**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
poetry run python main.py --host 0.0.0.0 --port 8000
```

### **Step 3: Start Frontend**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-frontend
npm run dev
```

### **Step 4: Upload Test File (curl)**
```bash
curl -X POST http://localhost:8000/api/v1/content-pillar/upload-file \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/test.xlsx" \
  -F "file_type=xlsx" \
  -F "user_id=test_user"
```

### **Step 5: Verify Upload**
- Check Supabase `files` table
- Check GCS bucket
- Check response for `file_id`

### **Step 6: Trigger Parsing**
```bash
curl -X POST http://localhost:8000/api/v1/content-pillar/process-file/{file_id} \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### **Step 7: Verify Parsing**
- Check Supabase `parsed_files` table
- Check GCS for parsed file
- Check response for `parsed_file_id`

---

## 🔧 Required Fixes (Priority Order)

### **Fix 1: Register Data Solution Orchestrator** (HIGH)
- Add to DeliveryManagerService initialization
- Or add to BusinessEnablementRealmBridge
- Ensure it's discoverable

### **Fix 2: Update ContentAnalysisOrchestrator.upload_file()** (HIGH)
- Replace direct Content Steward call with Data Solution Orchestrator
- Pass workflow_id in user_context
- Handle response format

### **Fix 3: Implement/Update process_file()** (HIGH)
- Call Data Solution Orchestrator.orchestrate_data_parse()
- Pass file_id and workflow_id
- Handle parsing result

### **Fix 4: Register FileParserService** (MEDIUM)
- Ensure service discovery can find it
- Or register explicitly in DeliveryManagerService

### **Fix 5: Test workflow_id Propagation** (MEDIUM)
- Verify FrontendGatewayService generates workflow_id
- Verify it's passed to ContentAnalysisOrchestrator
- Verify it's passed to Data Solution Orchestrator

---

## 📊 Expected Results

### **Upload Success:**
```json
{
  "success": true,
  "file_id": "uuid-here",
  "workflow_id": "workflow-uuid-here",
  "ui_name": "test.xlsx",
  "message": "File uploaded successfully"
}
```

### **Parsing Success:**
```json
{
  "success": true,
  "file_id": "uuid-here",
  "parsed_file_id": "parsed-uuid-here",
  "workflow_id": "workflow-uuid-here",
  "parsing_type": "structured",
  "data": {...}
}
```

---

## 🚨 Failure Scenarios

### **Scenario 1: ContentAnalysisOrchestrator Not Found**
- **Error:** "Content Analysis Orchestrator not available"
- **Fix:** Check orchestrator registration/discovery

### **Scenario 2: Data Solution Orchestrator Not Found**
- **Error:** "Data Solution Orchestrator not available"
- **Fix:** Register in startup sequence

### **Scenario 3: FileParserService Not Found**
- **Error:** "FileParserService not available"
- **Fix:** Register in service discovery

### **Scenario 4: Content Steward Not Available**
- **Error:** "Content Steward service not available"
- **Fix:** Check Smart City initialization

### **Scenario 5: Parsing Fails**
- **Error:** Various parsing errors
- **Fix:** Check FileParserService implementation, abstractions

---

## ✅ Success Criteria

1. ✅ File uploads successfully
2. ✅ File stored in GCS
3. ✅ Metadata stored in Supabase
4. ✅ workflow_id generated and propagated
5. ✅ Parsing triggered successfully
6. ✅ Parsed file stored in GCS
7. ✅ Parsed metadata stored in Supabase
8. ✅ Lineage tracked in Data Steward
9. ✅ Observability recorded in Nurse

---

**Next Action:** Implement required fixes, then run E2E test



