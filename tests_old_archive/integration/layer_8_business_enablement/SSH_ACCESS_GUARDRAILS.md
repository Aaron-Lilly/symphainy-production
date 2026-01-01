# SSH Access Guardrails - Preventing VM Lockout

## 🚨 Critical Issue: SSH Access Loss

**What Happened**: Changes in Layer 8 caused loss of SSH access to GCE VM, which would be catastrophic in production.

**Root Cause**: Global modification of `GOOGLE_APPLICATION_CREDENTIALS` environment variable broke GCP authentication, including SSH.

---

## 🔍 Root Cause Analysis

### **Primary Cause: GOOGLE_APPLICATION_CREDENTIALS Modification**

**Problem**: `GOOGLE_APPLICATION_CREDENTIALS` is used by **ALL** GCP tools:
- SSH access to GCP VMs
- `gcloud` CLI commands
- GCS client authentication
- Any GCP service authentication

**What Broke SSH**:
1. Test code modified `GOOGLE_APPLICATION_CREDENTIALS` globally
2. GCS adapter set `GOOGLE_APPLICATION_CREDENTIALS` during initialization
3. If set to invalid path or wrong credentials, **all GCP authentication fails**
4. SSH can't authenticate → VM becomes inaccessible

### **Secondary Causes: Infinite Loops**

**Docker Health Check Failures**:
- Containers in restart loops consume resources
- Can cause VM to become unresponsive
- Can prevent SSH from working if resources exhausted

**Test Hanging**:
- Tests without timeouts can hang indefinitely
- Block Python processes
- Can prevent new SSH sessions if resources exhausted

---

## ✅ Fixes Applied

### **1. GCS Adapter Fix** ✅
**File**: `gcs_file_adapter.py`

**Before** (Dangerous):
```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path  # ❌ BREAKS SSH
self._client = storage.Client(project=project_id)
```

**After** (Safe):
```python
# CRITICAL: We do NOT modify GOOGLE_APPLICATION_CREDENTIALS globally
# This would break SSH access and other GCP tools
# Instead, we pass credentials directly to the client
if credentials_path:
    self._client = storage.Client.from_service_account_json(credentials_path, project=project_id)
else:
    self._client = storage.Client(project=project_id)  # Uses ADC or existing env var
```

### **2. Test Code Fix** ✅
**File**: `test_file_parser_core.py`

**Before** (Dangerous):
```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path  # ❌ BREAKS SSH
```

**After** (Safe):
```python
# Only modify test-specific credential variables, NOT GOOGLE_APPLICATION_CREDENTIALS
for key in ['GCS_CREDENTIALS_PATH', 'TEST_GCS_CREDENTIALS']:
    os.environ[key] = abs_path  # ✅ Safe - doesn't affect SSH
```

### **3. Connection Timeout Fixes** ✅
- Consul connection: 5-second timeout
- ArangoDB connection: 5-second timeout
- Graceful failure instead of hanging

### **4. Docker Health Check Fixes** ✅
- Tempo: Changed from `curl` to `wget`
- OPA: Removed health check (distroless image)
- Celery: Fixed module path and env vars

---

## 🛡️ Guardrails to Prevent Future Issues

### **Guardrail 1: Never Modify Critical GCP Environment Variables**

**Rule**: **NEVER** modify these environment variables globally:
- `GOOGLE_APPLICATION_CREDENTIALS` ❌
- `GCLOUD_PROJECT` ❌
- `GOOGLE_CLOUD_PROJECT` ❌
- Any GCP authentication-related env vars ❌

**Implementation**:
```python
# ❌ FORBIDDEN - Add to code review checklist
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", path)
os.putenv("GOOGLE_APPLICATION_CREDENTIALS", path)

# ✅ ALLOWED - Use test-specific variables
os.environ["TEST_GCS_CREDENTIALS"] = path
os.environ["GCS_CREDENTIALS_PATH"] = path

# ✅ ALLOWED - Pass credentials directly to clients
storage.Client.from_service_account_json(credentials_path, project=project_id)
```

**Code Review Checklist**:
- [ ] No global modification of `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] No global modification of other GCP auth env vars
- [ ] Credentials passed directly to clients, not via env vars
- [ ] Test-specific credential variables used instead

---

### **Guardrail 2: Pre-Flight Checks Before Dangerous Operations**

**Rule**: Check critical environment variables before modifying anything.

**Implementation**:
```python
def check_critical_env_vars():
    """Check that critical GCP env vars are not being modified."""
    critical_vars = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GCLOUD_PROJECT",
        "GOOGLE_CLOUD_PROJECT"
    ]
    
    original_values = {}
    for var in critical_vars:
        original_values[var] = os.environ.get(var)
    
    # ... do work ...
    
    # Verify they weren't modified
    for var in critical_vars:
        if os.environ.get(var) != original_values[var]:
            raise RuntimeError(
                f"CRITICAL: {var} was modified! This breaks SSH access. "
                f"Original: {original_values[var]}, Current: {os.environ.get(var)}"
            )
```

**Add to Test Fixtures**:
```python
@pytest.fixture(autouse=True)
def protect_critical_env_vars():
    """Protect critical GCP environment variables from modification."""
    critical_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        "GCLOUD_PROJECT": os.environ.get("GCLOUD_PROJECT"),
        "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT")
    }
    
    yield
    
    # Verify they weren't modified
    for var, original_value in critical_vars.items():
        current_value = os.environ.get(var)
        if current_value != original_value:
            pytest.fail(
                f"CRITICAL: {var} was modified during test! "
                f"Original: {original_value}, Current: {current_value}. "
                f"This breaks SSH access to GCP VMs."
            )
```

---

### **Guardrail 3: Always Use Timeouts**

**Rule**: **ALL** network operations, Docker commands, and async operations must have timeouts.

**Implementation**:
```python
# ✅ REQUIRED: All async operations with timeout
async def safe_operation():
    try:
        result = await asyncio.wait_for(
            some_async_operation(),
            timeout=5.0  # REQUIRED: Always specify timeout
        )
        return result
    except asyncio.TimeoutError:
        raise TimeoutError("Operation timed out after 5 seconds")

# ✅ REQUIRED: All subprocess calls with timeout
result = subprocess.run(
    ["docker", "logs", "container"],
    capture_output=True,
    timeout=10  # REQUIRED: Always specify timeout
)

# ✅ REQUIRED: All HTTP requests with timeout
async with aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=5)  # REQUIRED: Always specify timeout
) as session:
    async with session.get(url) as resp:
        ...
```

**Code Review Checklist**:
- [ ] All `asyncio` operations use `asyncio.wait_for` with timeout
- [ ] All `subprocess.run` calls have `timeout` parameter
- [ ] All HTTP requests have timeout configured
- [ ] All Docker commands use `timeout` wrapper

---

### **Guardrail 4: Prevent Infinite Loops**

**Rule**: Health checks, retries, and loops must have limits.

**Implementation**:
```python
# ✅ REQUIRED: Health checks with retry limits
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:8500/health"]
  interval: 30s
  timeout: 10s
  retries: 3  # REQUIRED: Limit retries
  start_period: 60s

# ✅ REQUIRED: Retry loops with max attempts
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await operation()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(1)

# ✅ REQUIRED: Connection timeouts
async def connect_with_timeout():
    try:
        await asyncio.wait_for(
            connect(),
            timeout=5.0  # REQUIRED: Fail fast, don't hang
        )
    except asyncio.TimeoutError:
        raise ConnectionError("Connection timeout - infrastructure unavailable")
```

**Code Review Checklist**:
- [ ] All health checks have `retries` limit
- [ ] All retry loops have `max_attempts` limit
- [ ] All connections have timeouts
- [ ] No infinite `while True` loops without breaks

---

### **Guardrail 5: Monitor Container Health**

**Rule**: Monitor container restart counts and health status.

**Implementation**:
```python
def check_container_health(container_name: str) -> Dict[str, Any]:
    """Check container health and detect restart loops."""
    result = subprocess.run(
        ["docker", "inspect", "--format",
         "{{.State.Status}}|{{.State.Health.Status}}|{{.RestartCount}}|{{.State.Health.FailingStreak}}",
         container_name],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode != 0:
        return {"error": "Container not found"}
    
    parts = result.stdout.strip().split("|")
    status = parts[0]
    health = parts[1] if len(parts) > 1 else "unknown"
    restart_count = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    failing_streak = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    
    # ALERT: Restart loop detected
    if restart_count > 10 or failing_streak > 10:
        logger.error(
            f"⚠️ RESTART LOOP DETECTED: {container_name}\n"
            f"   Restart count: {restart_count}\n"
            f"   Failing streak: {failing_streak}\n"
            f"   This may cause VM resource exhaustion!"
        )
    
    return {
        "status": status,
        "health": health,
        "restart_count": restart_count,
        "failing_streak": failing_streak,
        "is_healthy": status == "running" and health in ["healthy", "none"]
    }
```

**Add to Pre-Flight Checks**:
```python
@pytest.fixture(scope="session", autouse=True)
def check_container_health_before_tests():
    """Check container health before running tests."""
    containers = [
        "symphainy-redis",
        "symphainy-arangodb",
        "symphainy-consul",
        "symphainy-celery-worker",
        "symphainy-celery-beat"
    ]
    
    unhealthy_containers = []
    for container in containers:
        health = check_container_health(container)
        if health.get("restart_count", 0) > 10:
            unhealthy_containers.append(f"{container}: restart_count={health['restart_count']}")
        if health.get("failing_streak", 0) > 10:
            unhealthy_containers.append(f"{container}: failing_streak={health['failing_streak']}")
    
    if unhealthy_containers:
        pytest.fail(
            f"Container restart loops detected before tests:\n"
            f"{chr(10).join(unhealthy_containers)}\n"
            f"This may cause VM resource exhaustion and SSH access issues."
        )
```

---

### **Guardrail 6: Resource Monitoring**

**Rule**: Monitor VM resources and alert if approaching limits.

**Implementation**:
```python
def check_vm_resources() -> Dict[str, Any]:
    """Check VM resource usage and alert if approaching limits."""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    alerts = []
    
    # ALERT: High CPU usage
    if cpu_percent > 90:
        alerts.append(f"CPU usage: {cpu_percent}% (threshold: 90%)")
    
    # ALERT: Low memory
    if memory.percent > 90:
        alerts.append(f"Memory usage: {memory.percent}% (threshold: 90%)")
    
    # ALERT: Low disk space
    if disk.percent > 90:
        alerts.append(f"Disk usage: {disk.percent}% (threshold: 90%)")
    
    if alerts:
        logger.warning(
            f"⚠️ VM RESOURCE ALERTS:\n{chr(10).join(alerts)}\n"
            f"This may cause SSH access issues if resources are exhausted."
        )
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "alerts": alerts
    }
```

---

### **Guardrail 7: Safe Test Execution**

**Rule**: All tests must have timeouts and be killable.

**Implementation**:
```python
# Add to pytest.ini
[pytest]
timeout = 300  # 5 minute timeout for all tests
timeout_method = thread  # Use thread-based timeout (works with async)

# Or use decorator for specific tests
@pytest.mark.timeout(60)  # 60 second timeout
async def test_something():
    ...
```

**Test Execution Wrapper**:
```bash
#!/bin/bash
# safe_test_runner.sh

# Set maximum test execution time
MAX_TEST_TIME=600  # 10 minutes

# Run tests with timeout
timeout $MAX_TEST_TIME pytest "$@" || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Tests timed out after $MAX_TEST_TIME seconds"
        echo "This may indicate hanging tests or infrastructure issues"
    fi
    exit $exit_code
}
```

---

### **Guardrail 8: Emergency Recovery Procedures**

**Rule**: Document and automate emergency recovery procedures.

**Implementation**:
```bash
#!/bin/bash
# emergency_recovery.sh

echo "🚨 Emergency Recovery - Restoring SSH Access"

# 1. Unset problematic environment variables
unset GOOGLE_APPLICATION_CREDENTIALS
unset GCLOUD_PROJECT
unset GOOGLE_CLOUD_PROJECT

# 2. Stop problematic containers
docker stop $(docker ps -q --filter name=symphainy-) 2>/dev/null || true

# 3. Check for hanging processes
pkill -9 -f "pytest.*test_file_parser" || true

# 4. Check VM resources
df -h
free -h
top -bn1 | head -20

# 5. Restart Docker if needed
# sudo systemctl restart docker  # Uncomment if needed

echo "✅ Recovery procedures completed"
echo "Try SSH access again"
```

---

## 📋 Implementation Checklist

### **Immediate Actions** (Do Now)

- [ ] Add `protect_critical_env_vars` fixture to all test files
- [ ] Add pre-flight container health checks
- [ ] Add resource monitoring to test fixtures
- [ ] Update code review checklist with guardrails
- [ ] Create emergency recovery script

### **Code Changes** (Next PR)

- [ ] Add environment variable protection to all adapters
- [ ] Add timeouts to all async operations
- [ ] Add retry limits to all loops
- [ ] Add container health monitoring
- [ ] Add resource monitoring

### **Documentation** (Ongoing)

- [ ] Document all guardrails in README
- [ ] Add guardrails to onboarding docs
- [ ] Create runbook for SSH access issues
- [ ] Update architecture docs with safety patterns

---

## 🎯 Success Criteria

After implementing guardrails:

1. ✅ **No global modification** of `GOOGLE_APPLICATION_CREDENTIALS`
2. ✅ **All operations have timeouts** (no hanging operations)
3. ✅ **Container restart loops detected** before they cause issues
4. ✅ **Resource monitoring** alerts before VM becomes unresponsive
5. ✅ **Tests are killable** (timeout or signal)
6. ✅ **Emergency recovery procedures** documented and tested

---

## 📚 References

- **SSH Access Fix**: `SSH_ACCESS_FIX.md`
- **Test Safety**: `TEST_AUDIT_AND_SAFETY.md`
- **Safe Docker Commands**: `SAFE_DOCKER_COMMANDS.md`
- **Container Issues**: `CRITICAL_CONTAINER_ISSUES.md`

