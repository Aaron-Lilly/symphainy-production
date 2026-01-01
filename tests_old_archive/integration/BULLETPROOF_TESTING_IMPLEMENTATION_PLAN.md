# Bulletproof Testing Implementation Plan

## 🎯 Executive Summary

This plan combines:
1. **Test Coverage Improvements** (from gap analysis)
2. **SSH Access Guardrails** (preventing VM lockout)
3. **Additional Best Practices** (making testing truly bulletproof)

**Goal**: Create a testing infrastructure that:
- ✅ Catches issues early (Layer 0-2)
- ✅ Never breaks SSH access
- ✅ Never hangs or loops infinitely
- ✅ Provides actionable diagnostics
- ✅ Is maintainable and scalable

---

## 📊 Implementation Phases

### **Phase 1: Foundation & Safety (Week 1)** 🔴 **CRITICAL**

**Goal**: Prevent catastrophic issues (SSH lockout, infinite loops)

#### **1.1: SSH Access Protection** 🔴 **DO FIRST**

**Files to Create/Update**:
- `tests/conftest.py` - Add global protection fixtures
- `tests/integration/layer_0_startup/test_infrastructure_preflight.py` - Already created ✅
- All test files - Add protection fixtures

**Implementation**:

```python
# tests/conftest.py

import pytest
import os
from typing import Dict

# Critical GCP environment variables that must NEVER be modified
CRITICAL_GCP_ENV_VARS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCLOUD_PROJECT",
    "GOOGLE_CLOUD_PROJECT",
    "GCLOUD_CONFIG",
    "CLOUDSDK_CONFIG"
]

@pytest.fixture(scope="session", autouse=True)
def protect_critical_env_vars():
    """
    Global fixture that protects critical GCP environment variables.
    Runs automatically for all tests.
    """
    # Capture original values
    original_values = {}
    for var in CRITICAL_GCP_ENV_VARS:
        original_values[var] = os.environ.get(var)
    
    yield
    
    # Verify they weren't modified
    violations = []
    for var in CRITICAL_GCP_ENV_VARS:
        original = original_values[var]
        current = os.environ.get(var)
        if current != original:
            violations.append({
                "variable": var,
                "original": original,
                "current": current
            })
    
    if violations:
        error_msg = "CRITICAL: Critical GCP environment variables were modified!\n"
        error_msg += "This breaks SSH access to GCP VMs.\n\n"
        for v in violations:
            error_msg += f"  {v['variable']}:\n"
            error_msg += f"    Original: {v['original']}\n"
            error_msg += f"    Current: {v['current']}\n"
        error_msg += "\nFix: Use test-specific credential variables instead."
        pytest.fail(error_msg)


@pytest.fixture(scope="session", autouse=True)
def check_vm_resources_before_tests():
    """
    Check VM resources before running tests.
    Alerts if resources are low (could cause SSH issues).
    """
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    alerts = []
    if cpu_percent > 85:
        alerts.append(f"CPU: {cpu_percent}% (threshold: 85%)")
    if memory.percent > 85:
        alerts.append(f"Memory: {memory.percent}% (threshold: 85%)")
    if disk.percent > 90:
        alerts.append(f"Disk: {disk.percent}% (threshold: 90%)")
    
    if alerts:
        pytest.fail(
            f"VM resources are low before tests:\n{chr(10).join(alerts)}\n"
            f"This may cause SSH access issues if resources are exhausted.\n"
            f"Free up resources before running tests."
        )


@pytest.fixture(scope="session", autouse=True)
def check_container_health_before_tests():
    """
    Check container health before running tests.
    Detects restart loops that could cause resource exhaustion.
    """
    import subprocess
    
    containers = [
        "symphainy-redis",
        "symphainy-arangodb",
        "symphainy-consul",
        "symphainy-celery-worker",
        "symphainy-celery-beat"
    ]
    
    unhealthy = []
    for container in containers:
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format",
                 "{{.State.Status}}|{{.RestartCount}}|{{.State.Health.FailingStreak}}",
                 container],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split("|")
                status = parts[0] if len(parts) > 0 else "unknown"
                restart_count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                failing_streak = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                
                if restart_count > 10:
                    unhealthy.append(f"{container}: restart_count={restart_count} (possible restart loop)")
                if failing_streak > 10:
                    unhealthy.append(f"{container}: failing_streak={failing_streak} (health check failing)")
        except Exception:
            # Container might not exist - that's OK for some tests
            pass
    
    if unhealthy:
        pytest.fail(
            f"Container health issues detected before tests:\n{chr(10).join(unhealthy)}\n"
            f"This may cause VM resource exhaustion and SSH access issues.\n"
            f"Fix container issues before running tests."
        )
```

#### **1.2: Test Timeout Configuration** 🔴 **DO SECOND**

**File**: `pytest.ini`

```ini
[pytest]
# Global test timeout (5 minutes)
timeout = 300
timeout_method = thread

# Markers
markers =
    integration: Integration tests (require infrastructure)
    critical_infrastructure: Critical infrastructure tests (run first)
    slow: Slow tests (may take > 1 minute)
    real_infrastructure: Tests that require real infrastructure (Docker, etc.)

# Test discovery
testpaths = tests/integration
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --timeout=300
```

**File**: `tests/conftest.py` (add timeout helpers)

```python
import asyncio
from functools import wraps

def async_timeout(seconds: float = 5.0):
    """Decorator for async test functions with timeout."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                pytest.fail(
                    f"Test {func.__name__} timed out after {seconds} seconds. "
                    f"This may indicate a hanging operation or infrastructure issue."
                )
        return wrapper
    return decorator


def subprocess_timeout(seconds: int = 10):
    """Decorator for subprocess operations with timeout."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import subprocess
            # Ensure timeout is passed to subprocess.run
            if 'timeout' not in kwargs:
                kwargs['timeout'] = seconds
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

#### **1.3: Safe Docker Helper Functions** 🔴 **DO THIRD**

**File**: `tests/utils/safe_docker.py` (new file)

```python
#!/usr/bin/env python3
"""
Safe Docker Operations - All operations have timeouts and error handling.
"""

import subprocess
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds


def run_docker_command(
    cmd: List[str],
    timeout: int = DEFAULT_TIMEOUT,
    capture_output: bool = True
) -> Tuple[bool, str, str]:
    """
    Run Docker command with timeout.
    
    Returns:
        (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["docker"] + cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Docker command timed out after {timeout} seconds: {' '.join(cmd)}")
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Docker command failed: {e}")
        return False, "", str(e)


def check_container_status(container_name: str) -> Dict[str, Any]:
    """Check Docker container status safely."""
    success, stdout, stderr = run_docker_command(
        ["inspect", "--format",
         "{{.State.Status}}|{{.State.Health.Status}}|{{.RestartCount}}|{{.State.Health.FailingStreak}}",
         container_name],
        timeout=5
    )
    
    if not success:
        return {
            "exists": False,
            "status": "not_found",
            "health": "unknown",
            "restart_count": 0,
            "failing_streak": 0,
            "error": stderr
        }
    
    parts = stdout.strip().split("|")
    return {
        "exists": True,
        "status": parts[0] if len(parts) > 0 else "unknown",
        "health": parts[1] if len(parts) > 1 else "unknown",
        "restart_count": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
        "failing_streak": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
        "error": None
    }


def check_container_health(container_name: str) -> bool:
    """Check if container is healthy (quick check)."""
    status = check_container_status(container_name)
    if not status["exists"]:
        return False
    
    # Alert on restart loops
    if status["restart_count"] > 10:
        logger.warning(
            f"⚠️ {container_name}: restart_count={status['restart_count']} "
            f"(possible restart loop)"
        )
    
    if status["failing_streak"] > 10:
        logger.warning(
            f"⚠️ {container_name}: failing_streak={status['failing_streak']} "
            f"(health check failing)"
        )
    
    return (
        status["status"] == "running" and
        status["health"] in ["healthy", "none", "unknown"] and
        status["restart_count"] <= 10 and
        status["failing_streak"] <= 10
    )


def get_container_logs(
    container_name: str,
    tail: int = 50,
    timeout: int = 5
) -> Tuple[bool, str]:
    """Get container logs safely (with limits)."""
    success, stdout, stderr = run_docker_command(
        ["logs", "--tail", str(tail), container_name],
        timeout=timeout
    )
    
    if not success:
        return False, stderr
    
    return True, stdout


def check_all_containers_healthy() -> Dict[str, bool]:
    """Check health of all required containers."""
    containers = [
        "symphainy-redis",
        "symphainy-arangodb",
        "symphainy-consul",
        "symphainy-celery-worker",
        "symphainy-celery-beat"
    ]
    
    results = {}
    for container in containers:
        results[container] = check_container_health(container)
    
    return results
```

---

### **Phase 2: Test Coverage Improvements (Week 2)** 🟠 **HIGH PRIORITY**

#### **2.1: Update Layer 0 Tests**

**File**: `tests/integration/layer_0_startup/test_platform_startup.py`

**Changes**:
1. Replace all `pytest.skip()` with `pytest.fail()` + diagnostics
2. Add infrastructure connectivity tests
3. Add configuration validation tests

**Pattern**:

```python
@pytest.mark.asyncio
async def test_foundations_initialize_in_order(self):
    """Test that all foundations initialize in correct order. FAILS with diagnostics if infrastructure unavailable."""
    from tests.utils.safe_docker import check_container_status, check_all_containers_healthy
    
    # Pre-flight check: Verify containers are healthy
    container_health = check_all_containers_healthy()
    unhealthy = [c for c, h in container_health.items() if not h]
    if unhealthy:
        pytest.fail(
            f"Infrastructure containers are unhealthy before test:\n"
            f"{chr(10).join([f'  - {c}' for c in unhealthy])}\n"
            f"Fix container issues before running tests."
        )
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            pwf_result = await asyncio.wait_for(
                pwf.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            # Check infrastructure status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Public Works Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n\n"
                f"Check: docker logs symphainy-consul\n"
                f"Check: docker logs symphainy-arangodb"
            )
        
        if not pwf_result:
            # Get detailed diagnostics
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        assert pwf_result is True, "Public Works Foundation should initialize"
        assert pwf.is_initialized, "Public Works Foundation should be marked as initialized"
        
    except ConnectionError as e:
        pytest.fail(
            f"Infrastructure connection failed: {e}\n\n"
            f"This indicates infrastructure is unavailable or misconfigured.\n"
            f"Check Docker containers: docker ps --filter name=symphainy-\n"
            f"Check configuration: Verify ports and environment variables match Docker containers"
        )
    except ImportError as e:
        pytest.fail(
            f"Foundation services not available: {e}\n\n"
            f"Check that foundations are installed and in Python path"
        )
    except Exception as e:
        error_str = str(e).lower()
        if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
            pytest.fail(
                f"Infrastructure error during initialization: {e}\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-\n"
                f"Check configuration: Verify ports and environment variables"
            )
        else:
            raise
```

#### **2.2: Add Connectivity Tests to All Layers**

**File**: `tests/integration/layer_0_startup/test_infrastructure_connectivity.py` (new file)

```python
#!/usr/bin/env python3
"""
Layer 0: Infrastructure Connectivity Tests

Tests that verify infrastructure is actually reachable (not just that containers exist).
"""

import pytest
import asyncio
from tests.utils.safe_docker import check_container_status

pytestmark = [pytest.mark.integration, pytest.mark.critical_infrastructure]


async def check_service_reachable(host: str, port: int, timeout: float = 5.0) -> Tuple[bool, str]:
    """Check if service is reachable with timeout."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True, ""
    except asyncio.TimeoutError:
        return False, f"Connection timeout after {timeout} seconds"
    except Exception as e:
        return False, str(e)


class TestInfrastructureConnectivity:
    """Test that infrastructure services are actually reachable."""
    
    @pytest.mark.asyncio
    async def test_consul_is_reachable_with_timeout(self):
        """Verify Consul is reachable with 5-second timeout."""
        import os
        consul_host = os.getenv("CONSUL_HOST", "localhost")
        consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        
        success, error = await check_service_reachable(consul_host, consul_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-consul")
            pytest.fail(
                f"Consul is not reachable at {consul_host}:{consul_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {container_status['status']} "
                f"(health: {container_status['health']}, "
                f"restarts: {container_status['restart_count']})\n\n"
                f"Check: docker logs symphainy-consul\n"
                f"Check: docker ps --filter name=symphainy-consul"
            )
    
    @pytest.mark.asyncio
    async def test_arangodb_is_reachable_with_timeout(self):
        """Verify ArangoDB is reachable with 5-second timeout."""
        import os
        arango_host = os.getenv("ARANGO_HOST", "localhost")
        arango_port = int(os.getenv("ARANGO_PORT", "8529"))
        
        success, error = await check_service_reachable(arango_host, arango_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-arangodb")
            pytest.fail(
                f"ArangoDB is not reachable at {arango_host}:{arango_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {container_status['status']} "
                f"(health: {container_status['health']}, "
                f"restarts: {container_status['restart_count']})\n\n"
                f"Check: docker logs symphainy-arangodb\n"
                f"Check: docker ps --filter name=symphainy-arangodb"
            )
    
    # Add similar tests for Redis, Celery, etc.
```

---

### **Phase 3: Automation & Tooling (Week 3)** 🟡 **MEDIUM PRIORITY**

#### **3.1: Pre-Test Validation Script**

**File**: `tests/scripts/pre_test_validation.sh` (new file)

```bash
#!/bin/bash
# Pre-Test Validation Script
# Runs before tests to ensure environment is safe

set -e

echo "🔍 Pre-Test Validation"
echo "===================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check critical environment variables
echo -e "\n${YELLOW}Checking critical environment variables...${NC}"
CRITICAL_VARS=(
    "GOOGLE_APPLICATION_CREDENTIALS"
    "GCLOUD_PROJECT"
    "GOOGLE_CLOUD_PROJECT"
)

for var in "${CRITICAL_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo -e "${GREEN}✓${NC} $var is set: ${!var}"
        # Verify file exists if it's a path
        if [[ "${!var}" == *.json ]] && [ ! -f "${!var}" ]; then
            echo -e "${RED}✗${NC} $var points to non-existent file: ${!var}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}⚠${NC} $var is not set (may use Application Default Credentials)"
    fi
done

# Check Docker containers
echo -e "\n${YELLOW}Checking Docker containers...${NC}"
CONTAINERS=(
    "symphainy-redis"
    "symphainy-arangodb"
    "symphainy-consul"
    "symphainy-celery-worker"
    "symphainy-celery-beat"
)

for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        STATUS=$(docker inspect --format '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        RESTART_COUNT=$(docker inspect --format '{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
        
        if [ "$STATUS" = "running" ]; then
            if [ "$RESTART_COUNT" -gt 10 ]; then
                echo -e "${RED}✗${NC} $container: running but restart_count=$RESTART_COUNT (possible restart loop)"
                ERRORS=$((ERRORS + 1))
            else
                echo -e "${GREEN}✓${NC} $container: running (restarts: $RESTART_COUNT)"
            fi
        else
            echo -e "${RED}✗${NC} $container: status=$STATUS"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${RED}✗${NC} $container: not found"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check VM resources
echo -e "\n${YELLOW}Checking VM resources...${NC}"
CPU_PERCENT=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEM_PERCENT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
DISK_PERCENT=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if (( $(echo "$CPU_PERCENT > 85" | bc -l) )); then
    echo -e "${RED}✗${NC} CPU usage: ${CPU_PERCENT}% (threshold: 85%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} CPU usage: ${CPU_PERCENT}%"
fi

if [ "$MEM_PERCENT" -gt 85 ]; then
    echo -e "${RED}✗${NC} Memory usage: ${MEM_PERCENT}% (threshold: 85%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} Memory usage: ${MEM_PERCENT}%"
fi

if [ "$DISK_PERCENT" -gt 90 ]; then
    echo -e "${RED}✗${NC} Disk usage: ${DISK_PERCENT}% (threshold: 90%)"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} Disk usage: ${DISK_PERCENT}%"
fi

# Summary
echo -e "\n${YELLOW}Validation Summary${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS issue(s)${NC}"
    echo -e "\nFix issues before running tests."
    exit 1
fi
```

#### **3.2: Test Runner Wrapper**

**File**: `tests/scripts/run_tests_safely.sh` (new file)

```bash
#!/bin/bash
# Safe Test Runner - Wraps pytest with safety checks and timeouts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run pre-test validation
echo "Running pre-test validation..."
"$SCRIPT_DIR/pre_test_validation.sh" || {
    echo "Pre-test validation failed. Fix issues before running tests."
    exit 1
}

# Set maximum test execution time (10 minutes)
MAX_TEST_TIME=600

# Run tests with timeout
echo "Running tests with ${MAX_TEST_TIME}s timeout..."
timeout $MAX_TEST_TIME pytest "$@" || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Tests timed out after $MAX_TEST_TIME seconds"
        echo "This may indicate hanging tests or infrastructure issues"
        echo "Check for hanging processes: ps aux | grep pytest"
    fi
    exit $exit_code
}
```

#### **3.3: Emergency Recovery Script**

**File**: `tests/scripts/emergency_recovery.sh` (new file)

```bash
#!/bin/bash
# Emergency Recovery Script - Restores SSH access and cleans up issues

set -e

echo "🚨 Emergency Recovery - Restoring SSH Access"
echo "============================================="

# 1. Unset problematic environment variables
echo "1. Unsetting problematic environment variables..."
unset GOOGLE_APPLICATION_CREDENTIALS
unset GCLOUD_PROJECT
unset GOOGLE_CLOUD_PROJECT
unset GCLOUD_CONFIG
unset CLOUDSDK_CONFIG

# 2. Stop problematic containers (if they're in restart loops)
echo "2. Checking for problematic containers..."
CONTAINERS=$(docker ps -q --filter name=symphainy- 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "   Found containers. Checking restart counts..."
    for container in $CONTAINERS; do
        RESTART_COUNT=$(docker inspect --format '{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
        if [ "$RESTART_COUNT" -gt 10 ]; then
            CONTAINER_NAME=$(docker inspect --format '{{.Name}}' "$container" | sed 's/\///')
            echo "   Stopping $CONTAINER_NAME (restart_count=$RESTART_COUNT)..."
            docker stop "$container" || true
        fi
    done
fi

# 3. Kill hanging test processes
echo "3. Checking for hanging test processes..."
pkill -9 -f "pytest.*test_file_parser" || true
pkill -9 -f "pytest.*layer_8" || true

# 4. Check VM resources
echo "4. Checking VM resources..."
df -h | head -2
free -h | head -2
echo "   CPU usage:"
top -bn1 | grep "Cpu(s)" | head -1

# 5. Summary
echo ""
echo "✅ Recovery procedures completed"
echo "Try SSH access again"
echo ""
echo "If SSH still doesn't work:"
echo "  1. Check GCP console for VM status"
echo "  2. Try resetting VM from GCP console"
echo "  3. Check firewall rules"
```

---

### **Phase 4: Additional Best Practices (Week 4)** 🟢 **ENHANCEMENTS**

#### **4.1: Test Result Reporting**

**File**: `tests/utils/test_reporting.py` (new file)

```python
#!/usr/bin/env python3
"""
Test Result Reporting - Generate actionable test reports.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


def generate_test_report(
    test_results: Dict[str, Any],
    output_file: str = "test_report.json"
) -> str:
    """
    Generate detailed test report with diagnostics.
    
    Args:
        test_results: Test results dictionary
        output_file: Output file path
    
    Returns:
        Report file path
    """
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total": test_results.get("total", 0),
            "passed": test_results.get("passed", 0),
            "failed": test_results.get("failed", 0),
            "skipped": test_results.get("skipped", 0),
            "errors": test_results.get("errors", 0)
        },
        "failures": test_results.get("failures", []),
        "infrastructure_status": test_results.get("infrastructure_status", {}),
        "recommendations": generate_recommendations(test_results)
    }
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return str(output_path)


def generate_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations from test results."""
    recommendations = []
    
    failures = test_results.get("failures", [])
    
    # Check for common failure patterns
    infrastructure_failures = [
        f for f in failures
        if any(keyword in f.get("message", "").lower()
               for keyword in ["connection", "timeout", "infrastructure", "container"])
    ]
    
    if infrastructure_failures:
        recommendations.append(
            "Infrastructure issues detected. Check Docker containers: "
            "docker ps --filter name=symphainy-"
        )
    
    ssh_failures = [
        f for f in failures
        if "GOOGLE_APPLICATION_CREDENTIALS" in f.get("message", "")
    ]
    
    if ssh_failures:
        recommendations.append(
            "SSH access protection triggered. Review code for global modification "
            "of GOOGLE_APPLICATION_CREDENTIALS. Use test-specific credential variables instead."
        )
    
    timeout_failures = [
        f for f in failures
        if "timeout" in f.get("message", "").lower()
    ]
    
    if timeout_failures:
        recommendations.append(
            "Timeout failures detected. Check for hanging operations or infrastructure issues."
        )
    
    return recommendations
```

#### **4.2: Continuous Monitoring**

**File**: `tests/utils/monitor_test_execution.py` (new file)

```python
#!/usr/bin/env python3
"""
Test Execution Monitor - Monitors test execution for issues.
"""

import time
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TestExecutionMonitor:
    """Monitor test execution for resource issues."""
    
    def __init__(self):
        self.start_time = time.time()
        self.checkpoints = []
    
    def checkpoint(self, name: str):
        """Record a checkpoint."""
        elapsed = time.time() - self.start_time
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        checkpoint = {
            "name": name,
            "elapsed": elapsed,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent
        }
        
        self.checkpoints.append(checkpoint)
        
        # Alert if resources are high
        if cpu_percent > 90:
            logger.warning(f"⚠️ High CPU usage at {name}: {cpu_percent}%")
        if memory.percent > 90:
            logger.warning(f"⚠️ High memory usage at {name}: {memory.percent}%")
        
        return checkpoint
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        total_time = time.time() - self.start_time
        return {
            "total_time": total_time,
            "checkpoints": self.checkpoints,
            "final_cpu": psutil.cpu_percent(interval=1),
            "final_memory": psutil.virtual_memory().percent
        }
```

---

## 📋 Implementation Checklist

### **Week 1: Foundation & Safety** 🔴

- [ ] Create `tests/conftest.py` with protection fixtures
- [ ] Create `tests/utils/safe_docker.py` helper functions
- [ ] Update `pytest.ini` with timeout configuration
- [ ] Test protection fixtures work correctly
- [ ] Verify SSH access is protected

### **Week 2: Test Coverage** 🟠

- [ ] Update Layer 0 tests (fail instead of skip)
- [ ] Add infrastructure connectivity tests
- [ ] Update Layer 1 tests
- [ ] Update Layer 2 tests
- [ ] Update Layers 3-7 tests

### **Week 3: Automation** 🟡

- [ ] Create pre-test validation script
- [ ] Create safe test runner wrapper
- [ ] Create emergency recovery script
- [ ] Test all scripts work correctly

### **Week 4: Enhancements** 🟢

- [ ] Add test result reporting
- [ ] Add test execution monitoring
- [ ] Create test documentation
- [ ] Review and refine

---

## 🎯 Success Criteria

After implementation:

1. ✅ **No SSH access issues** - Protection fixtures prevent env var modification
2. ✅ **No infinite loops** - All operations have timeouts and limits
3. ✅ **Early issue detection** - Pre-flight checks catch problems before tests
4. ✅ **Actionable diagnostics** - Test failures provide clear, fixable error messages
5. ✅ **Resource monitoring** - VM resources monitored and alerts provided
6. ✅ **Automated safety** - Pre-test validation and safe test runner
7. ✅ **Emergency recovery** - Documented recovery procedures

---

## 📚 Reference Documents

- **Gap Analysis**: `COMPREHENSIVE_LAYER_GAP_ANALYSIS.md`
- **SSH Guardrails**: `layer_8_business_enablement/SSH_ACCESS_GUARDRAILS.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **Test Safety**: `layer_8_business_enablement/TEST_AUDIT_AND_SAFETY.md`

