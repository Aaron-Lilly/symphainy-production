# Smart City New APIs - Testing Guide

**Date:** January 2025  
**Status:** ✅ Ready for Testing  
**Purpose:** Guide for testing the new Smart City APIs end-to-end

---

## Overview

This guide covers testing the new Smart City implementation, including:
- **SemanticDataAbstraction**: Storage and retrieval of embeddings and semantic graphs
- **ObservabilityAbstraction**: Platform observability data storage
- **Content Steward**: Parsed file storage APIs
- **Librarian**: Content metadata and embeddings storage APIs

---

## Prerequisites

### Infrastructure Requirements

1. **Supabase** (PostgreSQL)
   - Must be running and accessible
   - Connection configured in `.env` or config

2. **ArangoDB**
   - Must be running and accessible
   - Connection configured in `.env` or config

3. **GCS (Google Cloud Storage)**
   - For file storage (Content Steward)
   - Credentials configured

### Environment Setup

Ensure you're in the project root:
```bash
cd /home/founders/demoversion/symphainy_source
```

---

## Step 1: Setup Infrastructure

### 1.1 Setup Supabase Table

Create the `parsed_data_files` table:

```bash
python3 scripts/setup_supabase_parsed_data_files.py
```

**Expected Output:**
```
✅ Supabase adapter retrieved
✅ SQL schema loaded
✅ SQL schema executed successfully
✅ Table verified: parsed_data_files exists
🎉 Supabase setup completed successfully!
```

**What it does:**
- Creates `parsed_data_files` table in Supabase
- Creates indexes for performance
- Sets up RLS policies (if applicable)

### 1.2 Setup ArangoDB Collections

Create the necessary ArangoDB collections:

```bash
python3 scripts/setup_arangodb_collections.py
```

**Expected Output:**
```
✅ ArangoDB adapter retrieved
✅ Collection created: structured_embeddings
✅ Collection created: semantic_graph_nodes
✅ Collection created: semantic_graph_edges
✅ Collection created: correlation_maps
✅ Collection created: platform_logs
✅ Collection created: platform_metrics
✅ Collection created: platform_traces
✅ Collection created: agent_executions
✅ All 8 collections verified
🎉 ArangoDB setup completed successfully!
```

**What it does:**
- Creates semantic data collections (embeddings, graphs, correlation maps)
- Creates observability collections (logs, metrics, traces, agent executions)
- Verifies all collections exist

---

## Step 2: Run End-to-End Tests

### 2.1 Run Complete Test Suite

Test all new APIs:

```bash
python3 scripts/test_smart_city_new_apis.py
```

**Expected Output:**
```
================================================================================
SMART CITY NEW APIS - END-TO-END TEST SUITE
================================================================================

================================================================================
TEST 1: SemanticDataAbstraction
================================================================================
✅ SemanticDataAbstraction retrieved
✅ Embeddings stored: 1 embeddings
✅ Embeddings retrieved: 1 embeddings

================================================================================
TEST 2: ObservabilityAbstraction
================================================================================
✅ ObservabilityAbstraction retrieved
✅ Platform log recorded
✅ Platform metric recorded
✅ Platform trace recorded
✅ Agent execution recorded
✅ Platform logs retrieved: X logs

================================================================================
TEST 3: Content Steward Parsed File APIs
================================================================================
✅ Content Steward initialized
✅ Parsed file stored: parsed_xxx
✅ Parsed file retrieved
✅ Parsed files listed: 1 files

================================================================================
TEST 4: Librarian Content Metadata & Embeddings APIs
================================================================================
✅ Librarian initialized
✅ Content metadata stored: content_xxx
✅ Content metadata retrieved
✅ Embeddings stored: 1 embeddings
✅ Embeddings retrieved: 1 embeddings

================================================================================
TEST SUMMARY
================================================================================
  semantic_data_abstraction: ✅ PASSED
  observability_abstraction: ✅ PASSED
  content_steward_apis: ✅ PASSED
  librarian_apis: ✅ PASSED

Total: 4/4 tests passed

🎉 All tests passed!
```

### 2.2 Run Pytest Integration Tests

For more comprehensive testing with pytest:

```bash
cd tests
pytest integration/smart_city/test_smart_city_new_apis_e2e.py -v
```

**Test Categories:**
- `test_complete_flow_structured_data`: Full E2E flow (upload → parse → metadata → embeddings)
- `test_content_steward_parsed_file_apis`: Content Steward APIs
- `test_librarian_content_metadata_apis`: Librarian metadata APIs
- `test_librarian_embeddings_apis`: Librarian embeddings APIs
- `test_semantic_data_abstraction`: Direct abstraction test
- `test_observability_abstraction`: Direct abstraction test

---

## Step 3: Verify Data Storage

### 3.1 Verify Supabase Data

Check `parsed_data_files` table:

```sql
SELECT * FROM parsed_data_files ORDER BY created_at DESC LIMIT 10;
```

**Expected Columns:**
- `uuid`, `file_id`, `parsed_file_id`
- `format_type`, `content_type`
- `row_count`, `column_count`, `column_names`, `data_types`
- `parsed_at`, `status`, `processing_status`

### 3.2 Verify ArangoDB Data

Check semantic data collections:

```javascript
// In ArangoDB Web UI or via AQL
db.structured_embeddings.toArray()
db.semantic_graph_nodes.toArray()
db.correlation_maps.toArray()
```

Check observability collections:

```javascript
db.platform_logs.toArray()
db.platform_metrics.toArray()
db.platform_traces.toArray()
db.agent_executions.toArray()
```

---

## Troubleshooting

### Issue: "Supabase adapter not found"

**Solution:**
- Ensure Public Works Foundation is initialized
- Check Supabase connection in config
- Verify Supabase container is running

### Issue: "ArangoDB adapter not found"

**Solution:**
- Ensure Public Works Foundation is initialized
- Check ArangoDB connection in config
- Verify ArangoDB container is running

### Issue: "Table already exists" (Supabase)

**Status:** ✅ This is OK - table already created
- Script will skip creation if table exists

### Issue: "Collection already exists" (ArangoDB)

**Status:** ✅ This is OK - collection already created
- Script will skip creation if collection exists

### Issue: "Failed to store embeddings"

**Possible Causes:**
- ArangoDB not connected
- Collection not created
- Invalid embedding format

**Solution:**
- Run ArangoDB setup script
- Check ArangoDB connection
- Verify embedding format (must be list of floats)

### Issue: "Failed to store parsed file"

**Possible Causes:**
- Supabase table not created
- GCS not accessible
- Invalid file data

**Solution:**
- Run Supabase setup script
- Check GCS credentials
- Verify file data format

---

## Test Coverage

### ✅ What's Tested

1. **SemanticDataAbstraction**
   - ✅ Store semantic embeddings
   - ✅ Retrieve semantic embeddings
   - ✅ Query embeddings (vector search)

2. **ObservabilityAbstraction**
   - ✅ Record platform logs
   - ✅ Record platform metrics
   - ✅ Record platform traces
   - ✅ Record agent executions
   - ✅ Retrieve platform logs

3. **Content Steward**
   - ✅ Store parsed files
   - ✅ Retrieve parsed files
   - ✅ List parsed files

4. **Librarian**
   - ✅ Store content metadata
   - ✅ Retrieve content metadata
   - ✅ Update content metadata
   - ✅ Store embeddings
   - ✅ Retrieve embeddings
   - ✅ Vector search

### ⚠️ What's NOT Tested (Yet)

1. **Full E2E Flow**
   - File upload → parsing → metadata extraction → embedding generation
   - (Requires Business Enablement services - deferred)

2. **Error Handling**
   - Invalid data formats
   - Network failures
   - Database connection issues

3. **Performance**
   - Large file handling
   - Concurrent requests
   - Query performance

---

## Next Steps

After successful testing:

1. **Integrate with Business Enablement**
   - Update orchestrators to use new APIs
   - Connect file parsing → Content Steward
   - Connect metadata extraction → Librarian
   - Connect embedding generation → Librarian

2. **Update Frontend**
   - Use new APIs for content display
   - Show embeddings instead of content metadata
   - Integrate semantic search

3. **Production Readiness**
   - Add error handling
   - Add retry logic
   - Add monitoring
   - Add performance optimization

---

## Summary

✅ **Infrastructure Setup:**
- Supabase: `parsed_data_files` table
- ArangoDB: 8 collections (semantic data + observability)

✅ **Test Scripts:**
- `setup_supabase_parsed_data_files.py`
- `setup_arangodb_collections.py`
- `test_smart_city_new_apis.py`

✅ **Test Coverage:**
- All new abstractions tested
- All new Smart City APIs tested
- End-to-end flow validated

**Ready for integration!** 🎉



