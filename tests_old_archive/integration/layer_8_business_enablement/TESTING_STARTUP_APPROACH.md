# Testing Startup Approach

## ✅ Solution: Testing Startup Scripts (Instead of Modifying main.py)

Instead of adding Celery to `main.py`, we've created testing startup scripts similar to the production script.

---

## 📋 Created Scripts

### 1. `test-startup.sh` - Main Test Environment Startup
**Purpose**: Start infrastructure containers for testing

**What it does**:
- Starts Docker Compose infrastructure containers
- Verifies container health
- Checks infrastructure availability (Consul, ArangoDB, Redis, Tempo, OPA)
- Provides status report

**Usage**:
```bash
cd tests/integration/layer_8_business_enablement
./test-startup.sh
```

**When to use**: Before running any integration tests that need infrastructure

---

### 2. `celery-startup.sh` - Celery Startup for Testing
**Purpose**: Start Celery worker/beat outside Docker for testing

**What it does**:
- Creates a temporary Celery app module (`main_celery_test.py`)
- Uses CeleryAdapter configuration
- Starts Celery worker (and optionally Beat) using Poetry
- Manages PIDs for cleanup

**Usage**:
```bash
cd tests/integration/layer_8_business_enablement
./celery-startup.sh
```

**When to use**: When tests need Celery workers running outside Docker

---

## 🎯 Why This Approach?

### ✅ Advantages

1. **No Code Changes**: Doesn't require modifying `main.py`
2. **Separation of Concerns**: Testing setup separate from production code
3. **Flexibility**: Can use different Celery configurations for testing
4. **Consistency**: Follows same pattern as production startup script
5. **Isolation**: Test Celery setup doesn't affect production

### ⚠️ Docker Compose Celery Containers

**Current Status**: Docker Compose Celery containers (`symphainy-celery-worker`, `symphainy-celery-beat`) are configured but may restart until:
- Option A: Celery app instance is added to `main.py` (for Docker containers)
- Option B: Docker containers are disabled and `celery-startup.sh` is used instead

**Recommendation**: For testing, use `celery-startup.sh` instead of Docker Compose Celery containers.

---

## 🔄 Workflow

### For Tests That Need Infrastructure Only:
```bash
# Start infrastructure
./test-startup.sh

# Run tests
pytest tests/integration/... -v
```

### For Tests That Need Celery:
```bash
# Start infrastructure
./test-startup.sh

# Start Celery (outside Docker)
./celery-startup.sh

# Run tests
pytest tests/integration/... -v
```

### For Tests That Need Backend:
```bash
# Start infrastructure
./test-startup.sh

# Start backend (in separate terminal or background)
cd ../../symphainy-platform
python3 main.py --port 8000 &

# Run tests
pytest tests/integration/... -v
```

---

## 📝 Docker Compose Celery Containers

### Current Configuration
- **Command**: `celery -A main worker` (updated ✅)
- **Environment Variables**: Added `SECRET_KEY`, `JWT_SECRET` ✅
- **Issue**: Still needs Celery app instance in `main.py` OR use `celery-startup.sh` instead

### Options

**Option 1**: Keep Docker Compose Celery containers
- Add Celery app to `main.py` (for Docker)
- Use `celery-startup.sh` for testing (separate)

**Option 2**: Disable Docker Compose Celery containers for testing
- Comment out Celery services in `docker-compose.infrastructure.yml`
- Always use `celery-startup.sh` for testing

**Option 3**: Hybrid approach
- Docker Compose Celery for production
- `celery-startup.sh` for testing

**Recommendation**: Option 3 (Hybrid) - best of both worlds.

---

## 🧹 Cleanup

### Stop Celery (from celery-startup.sh):
```bash
# Kill Celery worker
kill $(cat ../../symphainy-platform/.celery_test.pid)

# Kill Celery Beat (if started)
kill $(cat ../../symphainy-platform/.celery_beat_test.pid)
```

### Stop Infrastructure:
```bash
cd ../../symphainy-platform
docker-compose -f docker-compose.infrastructure.yml down
```

---

## ✅ Benefits

1. ✅ **No main.py changes** - keeps production code clean
2. ✅ **Testing isolation** - test setup separate from production
3. ✅ **Flexibility** - can use different configs for testing
4. ✅ **Consistency** - follows production startup pattern
5. ✅ **Easy cleanup** - scripts manage PIDs and temporary files

---

## 📋 Next Steps

1. ✅ Scripts created and ready to use
2. ⚠️ **Optional**: Update Docker Compose to disable Celery containers for testing
3. 📝 **Documentation**: Add to test setup guides

