# CTO Demo Testing Guide - Production Platform

**Date:** December 2024  
**Status:** ✅ **READY FOR TESTING**

---

## 🎯 Overview

This guide explains how to run the CTO demo tests against the **actual production platform** (running in containers). These tests validate that the platform works end-to-end, technically, functionally, and in all ways that could trip us up during the actual demo.

---

## 📋 Prerequisites

1. **Docker & Docker Compose** installed and running
2. **Python 3.11+** with pytest installed
3. **Demo files** available at `/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/`
4. **Environment variables** configured (`.env.secrets` in `symphainy-platform/`)

---

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

```bash
cd /home/founders/demoversion/symphainy_source
./run_cto_demo_tests.sh
```

This script will:
1. ✅ Start all Docker containers
2. ✅ Wait for services to be healthy
3. ✅ Run all 3 CTO demo tests
4. ✅ Optionally stop containers after tests

### Option 2: Manual Steps

#### Step 1: Start Production Platform

```bash
cd /home/founders/demoversion/symphainy_source
docker-compose up -d
```

#### Step 2: Wait for Services to be Healthy

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check infrastructure services
curl http://localhost:8500/v1/status/leader  # Consul
docker exec symphainy-redis redis-cli ping   # Redis
curl http://localhost:8529/_api/version      # ArangoDB
```

#### Step 3: Run Tests

```bash
export TEST_BACKEND_URL="http://localhost:8000"
export TEST_FRONTEND_URL="http://localhost:3000"

cd /home/founders/demoversion/symphainy_source
pytest tests/e2e/production/cto_demos/ -v --tb=short -m "cto_demo" --timeout=600
```

---

## 🎬 The Three CTO Demo Scenarios

### Demo 1: Autonomous Vehicle Testing (Defense T&E)

**Test File:** `test_cto_demo_1_autonomous_vehicle.py`

**Journey:**
1. **Content Pillar:** Upload mission data → Parse COBOL binary → Extract incidents
2. **Insights Pillar:** Analyze mission patterns → Generate safety insights
3. **Operations Pillar:** Generate operational SOPs → Create workflow diagrams
4. **Business Outcomes Pillar:** Create strategic roadmap → Generate POC proposal

**Demo Files:**
- `mission_plan.csv`
- `telemetry_raw.bin`
- `telemetry_copybook.cpy`
- `test_incident_reports.docx`

**Expected Duration:** ~2-3 minutes

---

### Demo 2: Life Insurance Underwriting/Reserving Insights

**Test File:** `test_cto_demo_2_underwriting.py`

**Journey:**
1. **Content Pillar:** Upload claims, reinsurance, policy data
2. **Insights Pillar:** Analyze underwriting patterns → Generate insights
3. **Operations Pillar:** Create underwriting workflows → Generate SOPs
4. **Business Outcomes Pillar:** Create strategic roadmap → Generate POC proposal

**Demo Files:**
- `claims.csv`
- `reinsurance.xlsx`
- `underwriting_notes.pdf`
- `policy_master.dat`
- `copybook.cpy`

**Expected Duration:** ~2-3 minutes

---

### Demo 3: Data Mash Coexistence/Migration Enablement

**Test File:** `test_cto_demo_3_coexistence.py`

**Journey:**
1. **Content Pillar:** Upload legacy policies, target schema, alignment map
2. **Insights Pillar:** Analyze migration patterns
3. **Operations Pillar:** Create coexistence SOPs → Convert to workflows
4. **Business Outcomes Pillar:** Create strategic roadmap → Generate POC proposal

**Demo Files:**
- `legacy_policy_export.csv`
- `target_schema.json`
- `alignment_map.json`

**Expected Duration:** ~2-3 minutes

---

## ✅ What Gets Tested

### Technical Validation
- ✅ **API Endpoints:** All 4 pillar endpoints are accessible
- ✅ **Service Discovery:** Curator, Consul, and service registration work
- ✅ **Database Connectivity:** ArangoDB, Redis connections work
- ✅ **File Processing:** Upload, parse, and retrieval work
- ✅ **Session Management:** Session creation and tracking work

### Functional Validation
- ✅ **Content Pillar:** File upload, parsing, and preview
- ✅ **Insights Pillar:** Data analysis and visualization generation
- ✅ **Operations Pillar:** Workflow/SOP conversion and coexistence analysis
- ✅ **Business Outcomes Pillar:** Roadmap and POC proposal generation

### Integration Validation
- ✅ **Agentic-Forward Pattern:** Agents perform critical reasoning, services execute
- ✅ **Real LLM Calls:** Actual LLM integration works (if API key configured)
- ✅ **Artifact Creation:** Artifacts are created and stored correctly
- ✅ **Cross-Pillar Communication:** Pillars can access each other's outputs

---

## 🔧 Troubleshooting

### Issue: Backend Not Accessible

**Symptoms:**
```
❌ Backend is not accessible at http://localhost:8000
```

**Solutions:**
1. Check if containers are running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify port 8000 is not in use: `netstat -tuln | grep 8000`
4. Check Traefik routing: `curl http://localhost:8080/api/rawdata`

### Issue: Tests Timeout

**Symptoms:**
```
TimeoutError: Test timed out after 600 seconds
```

**Solutions:**
1. Check LLM API key is configured in `.env.secrets`
2. Check service logs for errors: `docker-compose logs -f`
3. Increase timeout: `--timeout=1200` (20 minutes)
4. Check network connectivity between containers

### Issue: Demo Files Not Found

**Symptoms:**
```
pytest.skip: Demo file not found: /path/to/demo_files/...
```

**Solutions:**
1. Verify demo files exist: `ls -la /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/`
2. Check file permissions: `chmod -R 644 /path/to/demo_files/`
3. Tests will skip gracefully if files are missing

### Issue: Session Creation Fails

**Symptoms:**
```
Session creation failed: 500 - Internal Server Error
```

**Solutions:**
1. Check backend logs: `docker-compose logs backend | tail -50`
2. Verify database connectivity: `curl http://localhost:8529/_api/version`
3. Check Redis connectivity: `docker exec symphainy-redis redis-cli ping`
4. Verify Consul is healthy: `curl http://localhost:8500/v1/status/leader`

---

## 📊 Expected Test Results

### Success Case

```
tests/e2e/production/cto_demos/test_cto_demo_1_autonomous_vehicle.py::test_cto_demo_1_autonomous_vehicle_full_journey PASSED
tests/e2e/production/cto_demos/test_cto_demo_2_underwriting.py::test_cto_demo_2_underwriting_full_journey PASSED
tests/e2e/production/cto_demos/test_cto_demo_3_coexistence.py::test_cto_demo_3_coexistence_full_journey PASSED

======================== 3 passed in 180.45s ========================
```

### Partial Success (Some Tests Skip)

If demo files are missing, tests will skip gracefully:
```
tests/e2e/production/cto_demos/test_cto_demo_1_autonomous_vehicle.py::test_cto_demo_1_autonomous_vehicle_full_journey SKIPPED
tests/e2e/production/cto_demos/test_cto_demo_2_underwriting.py::test_cto_demo_2_underwriting_full_journey PASSED
tests/e2e/production/cto_demos/test_cto_demo_3_coexistence.py::test_cto_demo_3_coexistence_full_journey PASSED

==================== 2 passed, 1 skipped in 120.30s ====================
```

---

## 🎯 Next Steps

After running the tests:

1. **Review Test Output:** Check for any warnings or skipped tests
2. **Check Logs:** Review container logs for any errors
3. **Validate Artifacts:** Verify that artifacts were created correctly
4. **Performance Check:** Note test execution times (should be < 5 minutes total)

---

## 📝 Notes

- **Test Isolation:** Each test creates its own session to avoid conflicts
- **Rate Limiting:** Tests include rate limit handling (429 responses)
- **Timeout Protection:** All tests have 10-minute timeouts
- **Graceful Degradation:** Tests skip gracefully if demo files are missing
- **Production-Specific:** These tests are designed for production containers, not local development servers

---

**Last Updated:** December 2024  
**Status:** ✅ **READY FOR CTO DEMO**







