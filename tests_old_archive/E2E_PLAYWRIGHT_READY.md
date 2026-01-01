# E2E Playwright Testing - Ready! ✅

**Date:** December 2024  
**Status:** ✅ **ALL FIXTURES COMPLETE**

---

## 🎯 Summary

Successfully created automated test fixtures for both backend and frontend servers, enabling fully automated E2E testing with Playwright.

---

## ✅ Test Infrastructure Completed

### **1. Backend Server Fixture** ✅

**File:** `tests/e2e/conftest.py`

**Fixture:** `backend_server` (session scope)

**Features:**
- Automatically starts backend server in subprocess
- Waits for health check (`/health` endpoint)
- Captures server logs to `tests/e2e/backend_server.log`
- Reuses server if already running
- Gracefully shuts down after tests

**Usage:**
```python
@pytest.mark.asyncio
async def test_api_endpoint(backend_server):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        assert response.status_code == 200
```

---

### **2. Frontend Server Fixture** ✅

**File:** `tests/e2e/conftest.py`

**Fixture:** `frontend_server` (session scope)

**Features:**
- Automatically starts frontend server in subprocess
- Uses `npm run dev` (or `npm run start` if `TEST_FRONTEND_PRODUCTION=true`)
- Waits for HTTP response (accepts redirects)
- Captures server logs to `tests/e2e/frontend_server.log`
- Reuses server if already running
- Gracefully shuts down after tests

**Usage:**
```python
@pytest.mark.asyncio
async def test_frontend_page(frontend_server):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:3000")
        assert response.status_code == 200
```

---

### **3. Combined Servers Fixture** ✅

**File:** `tests/e2e/conftest.py`

**Fixture:** `both_servers` (session scope)

**Features:**
- Ensures both backend and frontend servers are running
- Perfect for Playwright E2E tests that need full stack

**Usage:**
```python
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_full_journey(both_servers):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        # ... test code ...
        await browser.close()
```

---

## 🚀 Quick Start

### **Option 1: Automated (Recommended)**

Just run your tests - fixtures handle everything:

```bash
# API endpoint tests (backend only)
pytest tests/e2e/test_api_endpoints_reality.py -v

# Semantic API tests (backend only)
pytest tests/e2e/test_semantic_apis_e2e.py -v

# Playwright E2E tests (both servers)
pytest tests/e2e/test_three_demo_scenarios_e2e.py -v
```

**Note:** Ensure infrastructure (Redis, ArangoDB) is running first:
```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

---

### **Option 2: Manual Server Control**

If you prefer to start servers manually:

```bash
# Terminal 1: Backend
cd symphainy-platform
python3 main.py

# Terminal 2: Frontend
cd symphainy-frontend
npm run dev

# Terminal 3: Run tests (fixtures will detect running servers)
pytest tests/e2e/ -v
```

The fixtures will detect running servers and reuse them instead of starting new ones.

---

## 📋 Configuration

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_BACKEND_URL` | `http://localhost:8000` | Backend server URL |
| `TEST_BACKEND_PORT` | `8000` | Backend server port |
| `TEST_BACKEND_STARTUP_TIMEOUT` | `120` | Seconds to wait for backend |
| `TEST_FRONTEND_URL` | `http://localhost:3000` | Frontend server URL |
| `TEST_FRONTEND_PORT` | `3000` | Frontend server port |
| `TEST_FRONTEND_STARTUP_TIMEOUT` | `60` | Seconds to wait for frontend |
| `TEST_FRONTEND_PRODUCTION` | `false` | Use `npm start` instead of `npm run dev` |
| `TEST_SKIP_IF_SERVER_DOWN` | `false` | Skip tests if server fails to start (instead of failing) |

---

## 🎯 Test Types Supported

### **1. API Endpoint Tests** ✅

**Files:**
- `tests/e2e/test_api_endpoints_reality.py`
- `tests/e2e/test_semantic_apis_e2e.py`

**Fixture:** `backend_server`

**Example:**
```python
@pytest.mark.asyncio
async def test_health_endpoint(backend_server):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        assert response.status_code == 200
```

---

### **2. Playwright E2E Tests** ✅

**Files:**
- `tests/e2e/test_three_demo_scenarios_e2e.py`
- Any test using `playwright` or `pytest-playwright`

**Fixture:** `both_servers`

**Example:**
```python
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_cto_demo(both_servers):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        # ... test interactions ...
        await browser.close()
```

---

### **3. Frontend TypeScript Playwright Tests** ✅

**Location:** `symphainy-frontend/tests/e2e/*.spec.ts`

**Setup:** These tests use Playwright's global setup (`global-setup.ts`) which expects servers to be running.

**To run:**
```bash
cd symphainy-frontend
npm test  # or npx playwright test
```

**Note:** Start servers manually or use the Python fixtures first, then run these tests.

---

## 🔍 Debugging

### **Server Logs**

Server output is captured to:
- `tests/e2e/backend_server.log` - Backend server logs
- `tests/e2e/frontend_server.log` - Frontend server logs

If a server fails to start, check these logs for errors.

### **Manual Verification**

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

### **Skip on Failure**

If you want tests to skip (instead of fail) when servers can't start:

```bash
TEST_SKIP_IF_SERVER_DOWN=true pytest tests/e2e/ -v
```

---

## ✅ Next Steps

1. **Run API Tests:**
   ```bash
   pytest tests/e2e/test_api_endpoints_reality.py -v
   pytest tests/e2e/test_semantic_apis_e2e.py -v
   ```

2. **Run Playwright E2E Tests:**
   ```bash
   pytest tests/e2e/test_three_demo_scenarios_e2e.py -v
   ```

3. **Run Frontend TypeScript Tests:**
   ```bash
   cd symphainy-frontend
   npm test
   ```

---

## 🎉 Ready to Test!

All fixtures are in place. Just run your tests and the servers will start automatically!

**Last Updated:** December 2024


