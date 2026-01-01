# Container Fixes Plan - Safe Implementation

## 🔍 Root Causes Identified

### 1. Tempo - Health Check Failure
- **Issue**: `curl` not available in container
- **Solution**: Use `wget` (available at `/busybox/wget`)
- **Risk**: Low - simple health check change

### 2. OPA - Health Check Failure  
- **Issue**: `curl` not available, `wget` not available
- **Solution**: Use OPA binary `/opa` to check health endpoint OR remove health check and use `depends_on`
- **Risk**: Low - OPA binary is available

### 3. Celery Worker/Beat - Restart Loops
- **Issue**: Missing `main.celery` module + missing env vars (`SECRET_KEY`, `JWT_SECRET`)
- **Solution**: 
  1. Create `main/celery.py` module OR fix command to use correct module path
  2. Add missing environment variables
- **Risk**: Medium - need to verify Celery module structure

---

## 🔧 Fixes to Apply

### Fix #1: Tempo Health Check
**File**: `docker-compose.infrastructure.yml` (line 120)

**Change**:
```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:3200/status"]
```

### Fix #2: OPA Health Check
**File**: `docker-compose.infrastructure.yml` (line 253)

**Option A** (Recommended): Use OPA binary to check health
```yaml
healthcheck:
  test: ["CMD", "/opa", "eval", "-i", "http://localhost:8181/health", "true"]
```

**Option B**: Remove health check, use `depends_on` only
```yaml
# Remove healthcheck section
# Rely on depends_on with service_started
```

**Option C**: Use a simple HTTP check if we can find a tool
- Need to verify if OPA image has any HTTP tools

### Fix #3: Celery Configuration
**File**: `docker-compose.infrastructure.yml` (lines 148-179, 182-213)

**Changes Needed**:
1. Add missing environment variables:
   ```yaml
   - SECRET_KEY=${SECRET_KEY:-}
   - JWT_SECRET=${JWT_SECRET:-}
   ```

2. Fix Celery module path:
   - Option A: Create `main/celery.py` with Celery app
   - Option B: Change command to use correct module path
   - Option C: Verify if `main.py` should export `celery` attribute

---

## ⚠️ Safety Measures

1. **All fixes are non-blocking** - health checks have timeouts
2. **No infinite loops** - health checks have retry limits
3. **VM session safe** - no blocking operations
4. **Test each fix individually** - apply one at a time

---

## 📋 Implementation Order

1. ✅ Fix Tempo (safest - simple health check change)
2. ✅ Fix OPA (safe - health check change or removal)
3. ⚠️ Fix Celery (requires investigation of module structure)

---

## 🧪 Testing Plan

After each fix:
1. Restart the affected container
2. Monitor health check status (use safe_docker_inspect.py)
3. Verify no restart loops
4. Check logs for errors

