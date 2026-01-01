# Server Startup Guide for Testing

**Question**: Do we need to start servers before testing?

**Answer**: It depends on which layer you're testing!

---

## What Needs to Be Running

### Layer 1: Adapter Infrastructure Tests ✅ NO BACKEND NEEDED

**What to Start**:
```bash
# Only infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d
```

**What's NOT Needed**:
- ❌ Backend server (main.py)
- ❌ Frontend server
- ❌ Celery workers

**Why**: Layer 1 tests connect directly to infrastructure (Redis, ArangoDB, Meilisearch) - no backend needed.

---

### Layer 2: Abstraction Exposure Tests ⚠️ MAY NEED BACKEND

**What to Start**:
```bash
# Infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Backend server (for Smart City services)
cd symphainy-platform
python3 main.py --port 8000 &
```

**What's NOT Needed**:
- ❌ Frontend server

**Why**: Layer 2 tests Smart City services and Platform Gateway, which require backend initialization.

---

### Layers 7-9: Production Readiness Tests ⚠️ NEED BACKEND

**What to Start**:
```bash
# Infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Backend server
cd symphainy-platform
python3 main.py --port 8000 &
```

**What's NOT Needed**:
- ❌ Frontend server

**Why**: These tests validate orchestrators and enabling services, which require backend.

---

### Layer 4: Orchestrator Output Tests ⚠️ NEED BACKEND

**What to Start**:
```bash
# Infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Backend server
cd symphainy-platform
python3 main.py --port 8000 &
```

**Why**: Tests orchestrator methods that require full backend stack.

---

### Layer 5: CTO Demo Scenarios ⚠️ NEED BOTH FRONTEND & BACKEND

**What to Start**:
```bash
# Infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Backend server
cd symphainy-platform
python3 main.py --port 8000 &

# Frontend server (in separate terminal)
cd symphainy-frontend
npm run dev  # or npm start for production
```

**Why**: E2E tests require both frontend and backend.

---

## Quick Reference: Startup Commands by Layer

### For Layer 1 Only (Infrastructure Tests)
```bash
# Just infrastructure
docker-compose -f tests/docker-compose.test.yml up -d
pytest tests/integration/infrastructure_adapters/ -v
```

### For Layers 2-4, 7-9 (Backend Tests)
```bash
# Infrastructure + Backend
docker-compose -f tests/docker-compose.test.yml up -d
cd symphainy-platform && python3 main.py --port 8000 &
sleep 10  # Wait for backend to initialize
pytest tests/integration/... -v
```

### For Layer 5 (E2E Tests)
```bash
# Infrastructure + Backend + Frontend
docker-compose -f tests/docker-compose.test.yml up -d
cd symphainy-platform && python3 main.py --port 8000 &
cd symphainy-frontend && npm run dev &
sleep 15  # Wait for both to initialize
pytest tests/integration/demo_scenarios/ -v
```

---

## Recommended Testing Workflow

### Step 1: Start Infrastructure (Always First)
```bash
# Start infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Verify containers are healthy
docker-compose -f tests/docker-compose.test.yml ps
```

### Step 2: Run Layer 1 Tests (No Backend Needed)
```bash
# These tests work with just infrastructure
pytest tests/integration/infrastructure_adapters/ -v
```

### Step 3: Start Backend (For Layers 2+)
```bash
# Start backend server
cd symphainy-platform
python3 main.py --port 8000 &

# Wait for initialization (check logs)
sleep 10

# Verify backend is running
curl http://localhost:8000/health || echo "Backend not ready yet"
```

### Step 4: Run Layers 2-4, 7-9 Tests
```bash
# These tests need backend
pytest tests/integration/foundations/ -v  # Layer 2
pytest tests/integration/orchestrators/test_orchestrator_access_patterns.py -v  # Layer 7
pytest tests/integration/production_readiness/ -v  # Layers 8-9
pytest tests/integration/orchestrators/test_business_outcomes_*.py -v  # Layer 4
```

### Step 5: Start Frontend (For Layer 5 Only)
```bash
# Start frontend (only for E2E tests)
cd symphainy-frontend
npm run dev &

# Wait for frontend
sleep 5
```

### Step 6: Run Layer 5 Tests (E2E)
```bash
# E2E tests need both frontend and backend
pytest tests/integration/demo_scenarios/ -v
```

---

## Health Check Commands

### Check Infrastructure
```bash
# Check all containers
docker-compose -f tests/docker-compose.test.yml ps

# Check individual services
redis-cli ping  # Should return PONG
curl http://localhost:8529/_api/version  # ArangoDB
curl http://localhost:7700/health  # Meilisearch
curl http://localhost:8500/v1/status/leader  # Consul
```

### Check Backend
```bash
# Check backend health
curl http://localhost:8000/health

# Check backend is responding
curl http://localhost:8000/docs  # Should return Swagger UI
```

### Check Frontend
```bash
# Check frontend is running
curl http://localhost:3000  # Should return HTML
```

---

## Troubleshooting

### Backend Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Check backend logs
cd symphainy-platform
python3 main.py --port 8000  # Run in foreground to see errors
```

### Infrastructure Not Accessible
```bash
# Restart containers
docker-compose -f tests/docker-compose.test.yml restart

# Check container logs
docker-compose -f tests/docker-compose.test.yml logs
```

### Tests Fail with "Connection Refused"
- **Layer 1**: Check infrastructure containers are running
- **Layers 2-4, 7-9**: Check backend server is running
- **Layer 5**: Check both frontend and backend are running

---

## Summary

| Layer | Infrastructure | Backend | Frontend |
|-------|----------------|---------|----------|
| Layer 1 | ✅ Required | ❌ Not needed | ❌ Not needed |
| Layer 2 | ✅ Required | ⚠️ Recommended | ❌ Not needed |
| Layers 7-9 | ✅ Required | ✅ Required | ❌ Not needed |
| Layer 4 | ✅ Required | ✅ Required | ❌ Not needed |
| Layer 5 | ✅ Required | ✅ Required | ✅ Required |

**Start with Layer 1** - it only needs infrastructure containers!
