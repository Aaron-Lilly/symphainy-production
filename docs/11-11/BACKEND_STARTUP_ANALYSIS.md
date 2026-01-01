# Backend Startup Process Analysis

## Current State

### ✅ Poetry Configuration
- **File:** `pyproject.toml`
- **Status:** Poetry is configured with uvicorn as a dependency
- **Uvicorn Version:** `^0.31.1` (with standard extras)

### ⚠️ Current Startup Method
- **File:** `start_backend.sh` (created today)
- **Method:** Direct `python3 main.py` with PYTHONPATH
- **Issue:** Not using Poetry, which may cause dependency issues

### 📋 Main.py Startup
- **File:** `main.py`
- **Method:** Uses `uvicorn.run()` internally (line 573-579)
- **Command:** `python3 main.py --port 8000`
- **Status:** Works, but may not use Poetry environment

---

## Archive Insights

### From `symphainy-mvp-final/startup.sh`:

**Key Finding:** FastAPI MUST start LAST in the sequence

```
Startup Order:
1. Celery worker (no ports)
2. Consul + Tempo (service discovery & telemetry)
3. MCP servers, databases, or other services
4. FastAPI backend LAST (let it take its time to initialize)
```

**Why:** FastAPI startup can be slow and complex. Starting it last prevents blocking other services and eliminates timing/port binding issues.

**Command Used:**
```bash
poetry run uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
```

### From `symphainy_source/symphainy-platform/scripts/production-startup.sh`:

**Startup Sequence:**
1. Phase 1: Infrastructure (Redis, Consul, etc.)
2. Phase 2: Celery Worker
3. Phase 3: FastAPI Backend (START LAST!)

**Command Used:**
```bash
poetry run python main.py --port $BACKEND_PORT
```

---

## Docker Considerations

### From `docker-compose.infrastructure.yml`:

**Infrastructure Services (must start first):**
1. **ArangoDB** - Graph Database (port 8529)
2. **Redis** - Cache and Message Broker (port 6379)
3. **Meilisearch** - Search Engine (port 7700)
4. **Consul** - Service Discovery (port 8500)
5. **Tempo** - Distributed Tracing (port 3200)
6. **OpenTelemetry Collector** - Telemetry (port 4317)
7. **Celery Worker** - Background Tasks
8. **Celery Beat** - Task Scheduler

**Dependencies:**
- Services have `depends_on` with `condition: service_healthy`
- Health checks ensure services are ready before dependent services start
- Docker handles startup order automatically

---

## Recommended Startup Process

### Option 1: Using Poetry (Recommended)

**For Development:**
```bash
# 1. Start infrastructure (if using Docker)
docker-compose -f docker-compose.infrastructure.yml up -d

# 2. Wait for infrastructure to be ready
sleep 10

# 3. Start FastAPI backend LAST using Poetry
cd /home/founders/demoversion/symphainy_source/symphainy-platform
poetry run python main.py --port 8000 --reload
```

**For Production:**
```bash
# 1. Start infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d

# 2. Wait for infrastructure
sleep 15

# 3. Start FastAPI backend LAST
poetry run python main.py --port 8000
```

### Option 2: Direct Python (Current - Works but not ideal)

**Current Method:**
```bash
export PYTHONPATH=/home/founders/demoversion/symphainy_source/symphainy-platform:$PYTHONPATH
python3 main.py --port 8000
```

**Issues:**
- Doesn't use Poetry environment
- May have dependency version mismatches
- Doesn't ensure all Poetry dependencies are installed

---

## Startup Sequence Best Practices

### 1. Infrastructure First
- Start Docker containers for infrastructure services
- Wait for health checks to pass
- Verify services are accessible

### 2. Background Services
- Start Celery workers (if needed)
- Start MCP servers (if needed)
- These don't block FastAPI startup

### 3. FastAPI Last
- Start FastAPI backend AFTER all infrastructure is ready
- This prevents:
  - Connection errors during startup
  - Port binding conflicts
  - Dependency initialization failures
  - Race conditions with service discovery

### 4. Port Binding Lag
- FastAPI/uvicorn takes time to bind to port
- Wait 5-10 seconds after starting before checking health
- Use health check endpoints to verify readiness

---

## Updated Startup Script Recommendation

Create a proper startup script that:

1. **Checks Poetry environment**
2. **Starts Docker infrastructure** (if available)
3. **Waits for infrastructure health**
4. **Starts FastAPI LAST using Poetry**
5. **Waits for port binding**
6. **Verifies health**

---

## Current Issues

1. ❌ **Not using Poetry** - Using direct Python instead of `poetry run`
2. ❌ **No infrastructure startup** - Assuming infrastructure is already running
3. ❌ **No startup sequence** - Starting FastAPI immediately without waiting
4. ❌ **No health checks** - Not verifying infrastructure readiness

---

## Next Steps

1. Update `start_backend.sh` to use Poetry
2. Add infrastructure startup checks
3. Implement proper startup sequence
4. Add health check verification
5. Consider using the existing `startup.sh` script (which has proper orchestration)

---

## Conclusion

**Current Status:** Backend starts but may have dependency/environment issues

**Recommended:** Use Poetry for dependency management and follow the startup sequence:
1. Infrastructure (Docker) → 2. Background Services → 3. FastAPI LAST

**Key Insight:** FastAPI startup is complex and should start LAST to avoid blocking and timing issues.





